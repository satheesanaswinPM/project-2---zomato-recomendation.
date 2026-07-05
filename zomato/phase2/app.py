"""Flask backend serving the Phase 2 preference input web UI."""

from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from phase2.preferences import parse_preferences

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            form=None,
            errors={},
            warnings={},
            success=False,
            preferences=None,
        )

    @app.post("/api/preferences")
    def api_preferences():
        payload = request.get_json(silent=True) or request.form.to_dict()
        result = parse_preferences(payload)

        if not result.is_valid:
            response = {"ok": False, "errors": result.errors, "warnings": result.warnings}
            return jsonify(response), 400

        return jsonify(
            {
                "ok": True,
                "preferences": result.preferences.to_dict(),  # type: ignore[union-attr]
                "warnings": result.warnings,
            }
        )

    @app.post("/submit")
    def submit_form():
        result = parse_preferences(request.form)

        if not result.is_valid:
            return render_template(
                "index.html",
                form=request.form,
                errors=result.errors,
                warnings=result.warnings,
                success=False,
                preferences=None,
            )

        return render_template(
            "index.html",
            form=request.form,
            preferences=result.preferences,
            warnings=result.warnings,
            success=True,
            errors={},
        )

    return app


def main() -> None:
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
