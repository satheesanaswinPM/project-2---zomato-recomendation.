"""JSON-only REST API for restaurant recommendations."""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, request

from phase6.orchestrator import run_recommendation_search
from phase6.schemas import ErrorResponse, HealthResponse, SuccessResponse

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

    @app.route("/api/recommendations", methods=["POST", "OPTIONS"])
    def recommendations():
        if request.method == "OPTIONS":
            return _apply_cors(app.response_class(), origin)

        body = request.get_json(silent=True)
        if body is None:
            body = request.form.to_dict() if request.form else {}

        search = run_recommendation_search(body)

        if not search.ok:
            payload = ErrorResponse(errors=search.errors)
            return jsonify(payload.to_dict()), search.status_code

        assert search.display is not None
        payload = SuccessResponse(display=search.display.to_dict())
        return jsonify(payload.to_dict()), search.status_code

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = create_app()
    port = _api_port()
    logger.info("Phase 6 API listening on http://127.0.0.1:%s", port)
    app.run(debug=True, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
