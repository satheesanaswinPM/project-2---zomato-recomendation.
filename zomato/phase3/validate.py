"""Phase 3 validation: filter candidates and build LLM prompt."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.pipeline import build_integration

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[1] / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"
)


def run_validation(*, fixture: Path | None = None) -> dict:
    store = build_store(source_path=fixture or DEFAULT_FIXTURE)
    preferences = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_notes="family-friendly",
    )
    result = build_integration(store, preferences)

    prompt_preview = None
    if result.prompt:
        prompt_preview = {
            "version": result.prompt.version,
            "system_length": len(result.prompt.system),
            "user_length": len(result.prompt.user),
            "candidate_count": len(result.prompt.candidate_names),
            "candidate_names": result.prompt.candidate_names,
        }

    output = {
        "candidate_count": len(result.filter_result.candidates),
        "has_prompt": result.has_prompt,
        "relaxed_filters": result.filter_result.relaxed_filters,
        "message": result.filter_result.message,
        "prompt": prompt_preview,
    }
    print(json.dumps(output, indent=2))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 3 integration layer")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="Path to sample CSV fixture",
    )
    args = parser.parse_args()

    report = run_validation(fixture=args.fixture)

    if not report["has_prompt"]:
        raise SystemExit("Phase 3 validation failed: no prompt generated.")
    if report["candidate_count"] < 1 or report["candidate_count"] > 20:
        raise SystemExit("Phase 3 validation failed: candidate count out of range.")

    logger.info("Phase 3 validation passed.")


if __name__ == "__main__":
    main()
