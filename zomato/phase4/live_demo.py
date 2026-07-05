"""Live Groq demo: full Phase 1 → 4 pipeline with real API call."""

from __future__ import annotations

import json
import logging

from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.pipeline import build_integration
from phase4.llm_client import GroqClient, GroqConfig
from phase4.pipeline import build_recommendations
from phase4.validate import DEFAULT_FIXTURE, _load_env_files

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    _load_env_files()

    preferences = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        additional_notes="family-friendly, good for groups",
    )

    print("=" * 60)
    print("LIVE GROQ DEMO — Zomato Recommendation Engine (Phase 4)")
    print("=" * 60)
    print("\nUser preferences:")
    print(json.dumps(preferences.to_dict(), indent=2))

    store = build_store(source_path=DEFAULT_FIXTURE)
    integration = build_integration(store, preferences)

    print(f"\nFiltered candidates: {len(integration.filter_result.candidates)}")
    for candidate in integration.filter_result.candidates:
        print(f"  - {candidate.name} | rating {candidate.rating} | ₹{candidate.cost_for_two}")

    if integration.filter_result.message:
        print(f"\nFilter note: {integration.filter_result.message}")

    print("\nCalling Groq API...")
    client = GroqClient()
    response = build_recommendations(integration, preferences, client=client)

    print(f"\nSource: {response.source}")
    if response.message:
        print(f"Message: {response.message}")
    if response.summary:
        print(f"Summary: {response.summary}")
    if response.warnings:
        print(f"Warnings: {response.warnings}")

    print("\nRecommendations:")
    print("-" * 60)
    for rec in response.recommendations:
        print(f"#{rec.rank}  {rec.name}")
        print(f"    Location: {rec.location}  |  Cuisine: {rec.cuisine}")
        print(f"    Cost: ₹{rec.cost_for_two}  |  Rating: {rec.rating}")
        print(f"    Why: {rec.explanation}")
        print()

    print("=" * 60)
    logger.info("Live demo complete.")


if __name__ == "__main__":
    main()
