"""Streamlit UI helpers for Culinary Compass (Phase 9)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from phase5.models import DisplayPayload

BUDGET_LABELS = {
    "low": "Rs. 0 - 500",
    "medium": "Rs. 500 - 1,500",
    "high": "Rs. 1,501+",
    "custom": "Enter custom amount",
}

RATING_OPTIONS = [
    ("Any rating", 0.0),
    ("2.5+", 2.5),
    ("3.0+", 3.0),
    ("3.5+", 3.5),
    ("4.0+", 4.0),
    ("4.5+", 4.5),
    ("5.0+", 5.0),
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .cc-card {
            background: #ffffff;
            border: 1px solid #eeeeee;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .cc-rank {
            display: inline-block;
            background: #E23744;
            color: #fff;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            margin-bottom: 0.35rem;
        }
        .cc-name {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1A1A2E;
            margin: 0.2rem 0 0.45rem;
        }
        .cc-meta {
            color: #555;
            font-size: 0.9rem;
            margin-bottom: 0.55rem;
        }
        .cc-chip {
            display: inline-block;
            background: #f4f6f8;
            color: #555;
            border-radius: 999px;
            padding: 0.15rem 0.55rem;
            margin: 0 0.35rem 0.35rem 0;
            font-size: 0.8rem;
        }
        .cc-rating {
            display: inline-block;
            background: #2E9E5B;
            color: #fff;
            border-radius: 6px;
            padding: 0.15rem 0.45rem;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .cc-ai {
            background: #f4f6f8;
            border-radius: 10px;
            padding: 0.7rem 0.85rem;
            font-size: 0.92rem;
            color: #1A1A2E;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.65rem;margin-bottom:0.25rem;">
          <div style="width:36px;height:36px;border-radius:50%;background:#E23744;
                      display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">
            ✦
          </div>
          <h1 style="margin:0;color:#E23744;font-size:1.85rem;">Culinary Compass</h1>
        </div>
        <p style="color:#555;margin:0 0 1.25rem;">
          AI restaurant recommendations for Bangalore — powered by the Zomato dataset + Groq.
        </p>
        """,
        unsafe_allow_html=True,
    )


def collect_preferences(localities: list[str]) -> dict[str, Any] | None:
    """Render the preference form. Returns a prefs dict on submit, else None."""
    with st.form("preferences_form", clear_on_submit=False):
        st.subheader("Your preferences")
        st.caption("Tell us what you're craving and we'll find the best spots.")

        col1, col2 = st.columns(2)
        with col1:
            location = st.selectbox(
                "Location",
                options=localities or ["Bangalore"],
                index=0,
                help="Bangalore localities from the dataset",
            )
        with col2:
            budget_key = st.selectbox(
                "Budget (per person)",
                options=list(BUDGET_LABELS.keys()),
                format_func=lambda key: BUDGET_LABELS[key],
                index=1,
            )

        max_budget = None
        if budget_key == "custom":
            max_budget = st.number_input(
                "Custom max budget (Rs. for two)",
                min_value=1,
                max_value=100_000,
                value=2000,
                step=50,
            )

        col3, col4 = st.columns(2)
        with col3:
            cuisine = st.text_input(
                "Cravings",
                placeholder="e.g. North Indian, Pizza",
            )
        with col4:
            rating_label = st.selectbox(
                "Minimum Rating",
                options=[label for label, _ in RATING_OPTIONS],
                index=0,
            )

        additional_notes = st.text_area(
            "Required service",
            placeholder="e.g. outdoor seating, quick service, parking",
            height=80,
        )

        submitted = st.form_submit_button(
            "Find restaurants",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    min_rating = dict(RATING_OPTIONS)[rating_label]
    payload: dict[str, Any] = {
        "location": location,
        "budget": budget_key,
        "cuisine": cuisine.strip() or None,
        "min_rating": min_rating,
        "additional_notes": additional_notes.strip(),
    }
    if budget_key == "custom" and max_budget is not None:
        payload["max_budget"] = float(max_budget)
    return payload


def render_display(display: DisplayPayload, *, location: str = "") -> None:
    st.subheader(display.title or "Your Recommendations")
    area = location or "your area"
    st.caption(f"Top matches based on your preferences in {area}.")

    if display.summary:
        st.write(display.summary)

    if display.message:
        if display.is_error:
            st.error(display.message)
        else:
            st.info(display.message)

    for warning in display.warnings:
        st.warning(warning)

    if display.is_empty or not display.recommendations:
        st.markdown(
            """
            <div class="cc-card" style="text-align:center;">
              <p><strong>No restaurants found</strong></p>
              <p style="color:#555;">Try lowering your minimum rating, changing cravings, or adjusting budget.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for item in display.recommendations:
        chips = "".join(
            f'<span class="cc-chip">{part.strip()}</span>'
            for part in (item.cuisine or "").split(",")
            if part.strip()
        )
        rating_html = (
            f'<span class="cc-rating">{item.rating_label} ★</span>'
            if item.rating_label and item.rating_label != "Unrated"
            else ""
        )
        cost = item.cost_label
        if cost and "for two" not in cost.lower() and cost != "Price not available":
            cost = f"{cost} for two"

        st.markdown(
            f"""
            <div class="cc-card">
              <div class="cc-rank">#{item.rank}</div>
              <div style="display:flex;justify-content:space-between;gap:0.75rem;align-items:flex-start;">
                <div class="cc-name">{item.name}</div>
                {rating_html}
              </div>
              <div class="cc-meta">📍 {item.location}</div>
              <div>{chips}<span class="cc-chip">💰 {cost}</span></div>
              <div class="cc-ai"><strong>AI Match:</strong> {item.explanation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_errors(errors: dict[str, str]) -> None:
    for field, message in errors.items():
        st.error(f"{field}: {message}")
