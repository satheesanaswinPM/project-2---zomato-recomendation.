"""Phase 5 validation: parse and render recommendation output."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from unittest.mock import patch

from phase4.models import RecommendationResponse, RecommendationResult
from phase5.app import create_app
from phase5.parser import parse_response
from phase5.pipeline import present
from phase5.renderer import render_html, render_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_validation() -> dict:
    sample = RecommendationResponse(
        recommendations=[
            RecommendationResult(
                rank=1,
                name="Onesta",
                location="Bangalore",
                cuisine="Pizza, Cafe, Italian",
                cost_for_two=600.0,
                rating=4.6,
                explanation="Great Italian options within medium budget.",
            )
        ],
        summary="Top recommendations for you: Onesta.",
        source="llm",
    )

    payload = parse_response(sample)
    text_out = render_text(payload)
    html_out = render_html(payload)

    app = create_app()
    client = app.test_client()
    page = client.get("/")

    mock_response = RecommendationResponse(
        recommendations=[
            RecommendationResult(
                rank=1,
                name="Onesta",
                location="Bangalore",
                cuisine="Italian",
                cost_for_two=600,
                rating=4.6,
                explanation="Great pick.",
            )
        ],
        summary="Top recommendations for you: Onesta.",
    )
    with patch("phase5.app.build_recommendations", return_value=mock_response):
        api = client.post(
            "/api/search",
            json={"location": "Bangalore", "budget": "medium", "cuisine": "Italian"},
            content_type="application/json",
        )

    result = {
        "parsed_count": len(payload.recommendations),
        "has_summary": payload.summary is not None,
        "text_contains_name": "Onesta" in text_out,
        "html_contains_card": "result-card" in html_out,
        "index_status": page.status_code,
        "api_status": api.status_code,
    }

    empty = parse_response(RecommendationResponse(message="No restaurants found."))
    result["empty_state"] = empty.is_empty and empty.is_error

    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 5 output display")
    parser.add_argument("--serve", action="store_true", help="Start web UI on port 5000")
    args = parser.parse_args()

    if args.serve:
        from phase5.app import main as serve

        serve()
        return

    report = run_validation()
    if not all(
        [
            report["parsed_count"] >= 1,
            report["text_contains_name"],
            report["html_contains_card"],
            report["index_status"] == 200,
            report["empty_state"],
        ]
    ):
        raise SystemExit("Phase 5 validation failed.")
    logger.info("Phase 5 validation passed.")


if __name__ == "__main__":
    main()
