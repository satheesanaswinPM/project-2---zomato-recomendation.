"""Phase 8 validation: NL parse, refine heuristics, cache."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase2.preferences import UserPreferences
from phase8.cache import SearchCache, cache_key_for_prefs
from phase8.nl_parser import parse_natural_language
from phase8.refinement import refine_preferences

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class _MockClient:
    def __init__(self, payload: dict):
        self.payload = payload

    def complete(self, system: str, user: str) -> str:
        return json.dumps(self.payload)


def run_validation() -> dict:
    client = _MockClient(
        {
            "location": "Indiranagar",
            "budget": "low",
            "max_budget": None,
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_notes": "family-friendly",
        }
    )
    nl = parse_natural_language(
        "Cheap Italian in Indiranagar, 4+ stars, family-friendly",
        client=client,
    )

    current = UserPreferences(location="Indiranagar", budget="high", cuisine="Italian")
    refined = refine_preferences(current, "Show me cheaper options", client=None)

    cache = SearchCache(history_path=None)
    key = cache_key_for_prefs({"location": "HSR", "budget": "medium"})
    cache.put(
        key,
        display={"title": "Your Recommendations", "recommendations": []},
        preferences={"location": "HSR", "budget": "medium"},
        label="HSR · medium",
    )
    hit = cache.get(key)

    report = {
        "nl_ok": nl.ok,
        "nl_location": nl.preferences.location if nl.preferences else None,
        "nl_budget": nl.preferences.budget if nl.preferences else None,
        "refine_ok": refined.ok,
        "refine_budget": refined.preferences.budget if refined.preferences else None,
        "cache_hit": hit is not None,
        "history_len": len(cache.history()),
    }
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    report = run_validation()
    if not all(
        [
            report["nl_ok"],
            report["nl_location"] == "Indiranagar",
            report["refine_ok"],
            report["refine_budget"] == "medium",
            report["cache_hit"],
        ]
    ):
        raise SystemExit("Phase 8 validation failed.")
    logger.info("Phase 8 validation passed.")


if __name__ == "__main__":
    main()
