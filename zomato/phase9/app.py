"""
Phase 9 — Culinary Compass Streamlit app.

Run locally:
  streamlit run phase9/app.py

Deploy: Streamlit Community Cloud → main file zomato/phase9/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase4.validate import _load_env_files
from phase6.orchestrator import build_default_store, run_recommendation_search
from phase9.ui import (
    collect_preferences,
    inject_styles,
    render_display,
    render_errors,
    render_header,
)


def _apply_secrets() -> None:
    """Load GROQ_API_KEY from Streamlit secrets or local .env files."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = str(st.secrets["GROQ_API_KEY"])
    except Exception:
        pass
    _load_env_files()


@st.cache_resource(show_spinner="Loading restaurant data…")
def get_store():
    return build_default_store()


@st.cache_data(show_spinner=False)
def get_localities(_store_id: int) -> list[str]:
    store = get_store()
    names = store.localities("Bangalore")
    return names or ["Bangalore"]


def main() -> None:
    st.set_page_config(
        page_title="Culinary Compass",
        page_icon="🍽️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _apply_secrets()
    inject_styles()
    render_header()

    if not os.environ.get("GROQ_API_KEY"):
        st.warning(
            "GROQ_API_KEY is not set. Add it under Streamlit Secrets "
            "(or phase4/.env / project .env) to enable live AI recommendations."
        )

    try:
        store = get_store()
        localities = get_localities(id(store))
    except Exception as exc:
        st.error(f"Failed to load restaurant data: {exc}")
        st.stop()

    with st.expander("Natural language (optional)", expanded=False):
        nl_query = st.text_input(
            "Describe what you want",
            placeholder="Cheap Italian in Indiranagar, 4+ stars",
            key="nl_query",
        )
        if st.button("Parse into form fields", key="nl_parse"):
            if not nl_query.strip():
                st.warning("Enter a phrase first.")
            else:
                try:
                    from phase8.pipeline import parse_nl_query

                    parsed = parse_nl_query(nl_query.strip())
                    if not parsed.ok or parsed.preferences is None:
                        render_errors(parsed.errors or {"query": "Could not parse."})
                    else:
                        prefs = parsed.preferences.to_dict()
                        st.session_state["nl_prefs"] = prefs
                        st.success(
                            f"Parsed: {prefs.get('location')} · "
                            f"{prefs.get('budget')} · {prefs.get('cuisine') or 'any cuisine'}"
                        )
                        st.info(
                            "Use the form below (or click Find restaurants after "
                            "adjusting fields). Parsed values are shown here for review."
                        )
                        st.json(prefs)
                except Exception as exc:
                    st.error(f"NL parse failed: {exc}")

    prefs = collect_preferences(localities)

    # If user just parsed NL and wants one-click search from session
    if st.session_state.get("nl_prefs") and st.button(
        "Search using last parsed NL preferences"
    ):
        prefs = dict(st.session_state["nl_prefs"])

    if prefs is None:
        st.caption("Tip: pick a locality like Indiranagar, HSR, or Whitefield.")
        return

    with st.spinner("Finding restaurants with AI…"):
        # Drop None cuisine for cleaner validation
        body = {k: v for k, v in prefs.items() if v is not None}
        result = run_recommendation_search(body)

    if not result.ok:
        render_errors(result.errors)
        return

    assert result.display is not None
    render_display(result.display, location=str(prefs.get("location") or ""))

    st.divider()
    st.caption("Phase 9 · Streamlit deploy path · Data from Zomato dataset · Groq LLM")


if __name__ == "__main__":
    main()
