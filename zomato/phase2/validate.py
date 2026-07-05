"""Phase 2 validation: preference parsing and web app smoke test."""

from __future__ import annotations

import argparse
import json
import logging

from phase2.app import create_app
from phase2.preferences import parse_preferences

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_validation() -> dict:
    sample = parse_preferences(
        {
            "location": "Bengaluru",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": "4.0",
        }
    )

    app = create_app()
    client = app.test_client()
    page = client.get("/")
    api = client.post(
        "/api/preferences",
        json={"location": "Delhi", "budget": "low"},
        content_type="application/json",
    )

    result = {
        "preferences_valid": sample.is_valid,
        "sample_preferences": sample.preferences.to_dict() if sample.preferences else None,
        "index_status": page.status_code,
        "api_status": api.status_code,
        "api_ok": json.loads(api.data)["ok"],
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 2 user input layer")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the web UI on http://127.0.0.1:5000",
    )
    args = parser.parse_args()

    if args.serve:
        from phase2.app import main as serve

        serve()
        return

    report = run_validation()
    if not report["preferences_valid"] or report["index_status"] != 200 or not report["api_ok"]:
        raise SystemExit("Phase 2 validation failed.")
    logger.info("Phase 2 validation passed.")


if __name__ == "__main__":
    main()
