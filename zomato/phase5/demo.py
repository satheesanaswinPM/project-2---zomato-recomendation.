"""CLI end-to-end demo: preferences -> recommendations -> formatted display."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences, parse_preferences
from phase3.pipeline import build_integration
from phase4.llm_client import GroqClient
from phase4.pipeline import build_recommendations
from phase4.validate import _load_env_files
from phase5.pipeline import present

MOCK_LLM_JSON = json.dumps(
    [{"rank": 1, "name": "Onesta", "explanation": "Great Italian options within medium budget."}]
)


class _MockGroqClient:
    def complete(self, system: str, user: str) -> str:
        return MOCK_LLM_JSON

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LOCAL_CACHE = ROOT / "phase1" / "cache" / "zomato_raw.csv"
FIXTURE = ROOT / "phase1" / "tests" / "fixtures" / "sample_zomato.csv"


def run_demo(
    *,
    location: str = "Bangalore",
    budget: str = "medium",
    cuisine: str | None = "Italian",
    min_rating: float = 4.0,
    notes: str = "",
    use_live_groq: bool = False,
    output_format: str = "text",
) -> str:
    prefs_result = parse_preferences(
        {
            "location": location,
            "budget": budget,
            "cuisine": cuisine or "",
            "min_rating": str(min_rating) if min_rating else "",
            "additional_notes": notes,
        }
    )
    if not prefs_result.is_valid:
        raise ValueError(str(prefs_result.errors))

    preferences = prefs_result.preferences
    assert preferences is not None

    source = LOCAL_CACHE if LOCAL_CACHE.exists() else FIXTURE
    store = build_store(source_path=source)
    integration = build_integration(store, preferences)

    if use_live_groq:
        _load_env_files()
        client = GroqClient()
    else:
        client = _MockGroqClient()

    response = build_recommendations(integration, preferences, top_n=5, client=client)
    output = present(response, output_format=output_format)  # type: ignore[arg-type]
    return str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 5 end-to-end demo")
    parser.add_argument("--location", default="Bangalore")
    parser.add_argument("--budget", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", default="Italian")
    parser.add_argument("--min-rating", type=float, default=4.0)
    parser.add_argument("--notes", default="family-friendly")
    parser.add_argument("--live", action="store_true", help="Use live Groq API")
    parser.add_argument("--format", default="text", choices=["text", "json", "html"])
    args = parser.parse_args()

    print(run_demo(
        location=args.location,
        budget=args.budget,
        cuisine=args.cuisine,
        min_rating=args.min_rating,
        notes=args.notes,
        use_live_groq=args.live,
        output_format=args.format,
    ))


if __name__ == "__main__":
    main()
