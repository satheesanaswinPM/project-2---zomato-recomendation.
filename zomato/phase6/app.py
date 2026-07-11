"""JSON-only REST API for restaurant recommendations (+ Phase 8 enhancements)."""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, request

from phase6.orchestrator import build_default_store, run_recommendation_search
from phase6.schemas import ErrorResponse, HealthResponse, SuccessResponse
from phase8.cache import SEARCH_CACHE
from phase8.pipeline import parse_nl_query, refine_and_search, run_cached_search

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8000
DEFAULT_CORS_ORIGIN = "http://localhost:3000"


def _cors_origin() -> str:
    return os.environ.get("CORS_ORIGIN", DEFAULT_CORS_ORIGIN)


def _api_port() -> int:
    return int(os.environ.get("API_PORT", DEFAULT_PORT))


def _apply_cors(response, origin: str):
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def create_app(*, cors_origin: str | None = None) -> Flask:
    app = Flask(__name__)
    origin = cors_origin or _cors_origin()

    @app.after_request
    def add_cors_headers(response):
        return _apply_cors(response, origin)

    @app.get("/api/health")
    def health():
        return jsonify(HealthResponse().to_dict())

    @app.get("/api/locations")
    def locations():
        """Return Bangalore locality names, optionally filtered by query prefix/substring."""
        city = (request.args.get("city") or "Bangalore").strip()
        query = (request.args.get("q") or "").strip().lower()

        store = build_default_store()
        names = store.localities(city)

        if query:
            names = [name for name in names if query in name.lower()]

        return jsonify({"ok": True, "city": city, "locations": names})

    @app.get("/api/history")
    def history():
        limit = int(request.args.get("limit") or 10)
        return jsonify({"ok": True, "history": SEARCH_CACHE.history(limit=limit)})

    @app.route("/api/parse-preferences", methods=["POST", "OPTIONS"])
    def parse_preferences_nl():
        if request.method == "OPTIONS":
            return _apply_cors(app.response_class(), origin)

        body = request.get_json(silent=True) or {}
        query = body.get("query") or body.get("q") or ""
        parsed = parse_nl_query(str(query))
        if not parsed.ok:
            return (
                jsonify(
                    {
                        "ok": False,
                        "errors": parsed.errors or {},
                        "message": parsed.message,
                    }
                ),
                400,
            )

        assert parsed.preferences is not None
        return jsonify(
            {
                "ok": True,
                "preferences": parsed.preferences.to_dict(),
                "raw": parsed.raw,
            }
        )

    @app.route("/api/recommendations", methods=["POST", "OPTIONS"])
    def recommendations():
        if request.method == "OPTIONS":
            return _apply_cors(app.response_class(), origin)

        body = request.get_json(silent=True)
        if body is None:
            body = request.form.to_dict() if request.form else {}

        use_cache = bool(body.pop("use_cache", True))
        session_id = body.pop("session_id", None)
        query_label = body.pop("query_label", None)

        # Prefer cached path from Phase 8; fall back to direct orchestrator.
        try:
            search, sid, cache_hit = run_cached_search(
                dict(body),
                use_cache=use_cache,
                session_id=session_id,
                query_label=query_label,
            )
        except Exception:
            logger.exception("Cached search failed; falling back")
            search = run_recommendation_search(body)
            sid = None
            cache_hit = False

        if not search.ok:
            payload = ErrorResponse(errors=search.errors)
            return jsonify(payload.to_dict()), search.status_code

        assert search.display is not None
        response = SuccessResponse(display=search.display.to_dict()).to_dict()
        response["session_id"] = sid
        response["cache_hit"] = cache_hit
        return jsonify(response), search.status_code

    @app.route("/api/refine", methods=["POST", "OPTIONS"])
    def refine():
        if request.method == "OPTIONS":
            return _apply_cors(app.response_class(), origin)

        body = request.get_json(silent=True) or {}
        session_id = str(body.get("session_id") or "").strip()
        follow_up = str(body.get("follow_up") or body.get("query") or "").strip()

        if not session_id:
            return (
                jsonify({"ok": False, "errors": {"session_id": "session_id is required."}}),
                400,
            )

        refined, search, state, cache_hit = refine_and_search(session_id, follow_up)
        if not refined.ok:
            return (
                jsonify(
                    {
                        "ok": False,
                        "errors": refined.errors or {},
                        "message": refined.message,
                    }
                ),
                400,
            )

        if search is None or not search.ok or search.display is None:
            return (
                jsonify(
                    {
                        "ok": False,
                        "errors": (search.errors if search else {})
                        or {"follow_up": "Refinement search failed."},
                    }
                ),
                400 if search and not search.ok else 500,
            )

        return jsonify(
            {
                "ok": True,
                "session_id": state.session_id if state else session_id,
                "preferences": refined.preferences.to_dict() if refined.preferences else None,
                "display": search.display.to_dict(),
                "cache_hit": cache_hit,
            }
        )

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = create_app()
    port = _api_port()
    logger.info("Phase 6 API listening on http://127.0.0.1:%s", port)
    app.run(debug=True, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
