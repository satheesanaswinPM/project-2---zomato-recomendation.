"""Phase 6 validation: JSON REST API."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase4.models import RecommendationResponse, RecommendationResult
from phase6.app import create_app
from phase6.orchestrator import run_recommendation_search

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FIXTURE = ROOT / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"

MOCK_RESPONSE = RecommendationResponse(
    recommendations=[
        RecommendationResult(
            rank=1,
            name="Onesta",
            location="Bangalore",
            cuisine="Italian",
            cost_for_two=600,
            rating=4.6,
            explanation="Great Italian options within medium budget.",
        )
    ],
    summary="Top recommendations for you: Onesta.",
    source="llm",
)


def run_validation() -> dict:
    app = create_app()
    client = app.test_client()

    health = client.get("/api/health")
    health_data = health.get_json()

    with patch(
        "phase6.orchestrator.build_recommendations", return_value=MOCK_RESPONSE
    ):
        api_ok = client.post(
            "/api/recommendations",
            json={"location": "Bangalore", "budget": "medium", "cuisine": "Italian"},
            content_type="application/json",
        )

    api_bad = client.post(
        "/api/recommendations",
        json={"location": "", "budget": "invalid"},
        content_type="application/json",
    )

    with patch(
        "phase6.orchestrator.build_recommendations", return_value=MOCK_RESPONSE
    ):
        orchestrator = run_recommendation_search(
            {"location": "Bangalore", "budget": "medium"},
            source_path=FIXTURE,
        )

    result = {
        "health_status": health.status_code,
        "health_ok": health_data.get("status") == "ok",
        "api_status": api_ok.status_code,
        "api_ok": api_ok.get_json().get("ok"),
        "api_has_display": "display" in (api_ok.get_json() or {}),
        "api_restaurant": (api_ok.get_json() or {})
        .get("display", {})
        .get("recommendations", [{}])[0]
        .get("name"),
        "validation_status": api_bad.status_code,
        "validation_errors": api_bad.get_json().get("errors"),
        "orchestrator_ok": orchestrator.ok,
        "orchestrator_name": (
            orchestrator.display.recommendations[0].name
            if orchestrator.display
            else None
        ),
    }

    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 6 backend API")
    parser.add_argument("--serve", action="store_true", help="Start API on port 8000")
    args = parser.parse_args()

    if args.serve:
        from phase6.app import main as serve

        serve()
        return

    report = run_validation()
    checks = [
        report["health_status"] == 200,
        report["health_ok"],
        report["api_status"] == 200,
        report["api_ok"] is True,
        report["api_has_display"],
        report["api_restaurant"] == "Onesta",
        report["validation_status"] == 400,
        bool(report["validation_errors"]),
        report["orchestrator_ok"],
        report["orchestrator_name"] == "Onesta",
    ]
    if not all(checks):
        raise SystemExit("Phase 6 validation failed.")
    logger.info("Phase 6 validation passed.")


if __name__ == "__main__":
    main()
