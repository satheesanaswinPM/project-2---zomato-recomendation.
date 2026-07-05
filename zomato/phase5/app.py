"""Full-stack web app: Phase 2 input + Phases 1-4 pipeline + Phase 5 display."""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from phase1.pipeline import build_store
from phase2.preferences import parse_preferences
from phase3.pipeline import build_integration
from phase4.llm_client import GroqClient
from phase4.pipeline import build_recommendations
from phase4.validate import _load_env_files
from phase5.pipeline import build_display_payload, present
from phase5.renderer import render_html

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
LOCAL_CACHE = Path(__file__).resolve().parents[1] / "phase1" / "cache" / "zomato_raw.csv"


def _get_store():
    if LOCAL_CACHE.exists():
        return build_store(source_path=LOCAL_CACHE)
    return build_store()


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

    @app.get("/")
    def index():
        return render_template(
            "search.html",
            form=None,
            errors={},
            display=None,
            results_html=None,
        )

    @app.post("/search")
    def search():
        result = parse_preferences(request.form)
        if not result.is_valid:
            return render_template(
                "search.html",
                form=request.form,
                errors=result.errors,
                display=None,
                results_html=None,
            )

        preferences = result.preferences
        assert preferences is not None

        try:
            store = _get_store()
            integration = build_integration(store, preferences)
            _load_env_files()
            client = GroqClient()
            response = build_recommendations(
                integration, preferences, top_n=5, client=client
            )
        except Exception as exc:
            logger.exception("Search failed")
            from phase4.models import RecommendationResponse

            response = RecommendationResponse(
                message=f"Something went wrong: {exc}",
            )

        display = build_display_payload(response)
        results_html = render_html(display)

        return render_template(
            "search.html",
            form=request.form,
            errors={},
            display=display,
            results_html=results_html,
        )

    @app.post("/api/search")
    def api_search():
        result = parse_preferences(request.get_json(silent=True) or request.form.to_dict())
        if not result.is_valid:
            return jsonify({"ok": False, "errors": result.errors}), 400

        preferences = result.preferences
        assert preferences is not None

        store = _get_store()
        integration = build_integration(store, preferences)
        _load_env_files()
        response = build_recommendations(
            integration, preferences, top_n=5, client=GroqClient()
        )
        display = build_display_payload(response)
        return jsonify({"ok": True, "display": display.to_dict()})

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
