"""Phase 4 validation: Groq recommendation engine."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.pipeline import build_integration
from phase4.llm_client import GroqClient, GroqConfig
from phase4.pipeline import build_recommendations

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[1] / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"
)


def _load_env_files() -> None:
    """Load GROQ_API_KEY from local .env files if not already set."""
    if os.environ.get("GROQ_API_KEY"):
        return

    project_root = Path(__file__).resolve().parents[1]
    for env_path in (project_root / "phase4" / ".env", project_root / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
        if os.environ.get("GROQ_API_KEY"):
            return

MOCK_LLM_JSON = json.dumps(
    [
        {
            "rank": 1,
            "name": "Onesta",
            "explanation": "Great Italian options within medium budget.",
        }
    ]
)


class _MockGroqClient:
    def complete(self, system: str, user: str) -> str:
        return MOCK_LLM_JSON


def run_validation(*, fixture: Path | None = None, use_live_groq: bool = False) -> dict:
    store = build_store(source_path=fixture or DEFAULT_FIXTURE)
    preferences = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_notes="family-friendly",
    )
    integration = build_integration(store, preferences)

    client = None
    if use_live_groq:
        _load_env_files()
        if not os.environ.get("GROQ_API_KEY"):
            raise SystemExit("GROQ_API_KEY is required for live validation.")
        client = GroqClient(GroqConfig(api_key=os.environ["GROQ_API_KEY"]))
    else:
        client = _MockGroqClient()

    response = build_recommendations(integration, preferences, client=client)

    result = {
        "recommendation_count": len(response.recommendations),
        "source": response.source,
        "summary": response.summary,
        "message": response.message,
        "warnings": response.warnings,
        "recommendations": [item.to_dict() for item in response.recommendations[:3]],
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 4 Groq recommendation engine")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call live Groq API (requires GROQ_API_KEY)",
    )
    args = parser.parse_args()

    report = run_validation(fixture=args.fixture, use_live_groq=args.live)

    if report["recommendation_count"] < 1:
        raise SystemExit("Phase 4 validation failed: no recommendations returned.")

    logger.info("Phase 4 validation passed (%s).", report["source"])


if __name__ == "__main__":
    main()
