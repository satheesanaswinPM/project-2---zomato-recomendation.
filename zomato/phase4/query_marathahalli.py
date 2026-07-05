"""Run a custom restaurant query: Marathahalli, rating 4+, budget <= 2000."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase1.models import Restaurant
from phase1.pipeline import build_store
from phase2.preferences import UserPreferences
from phase3.models import FilterResult, IntegrationResult
from phase3.prompts import build_prompt
from phase4.llm_client import GroqClient
from phase4.pipeline import build_recommendations
from phase4.validate import _load_env_files

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LOCALITY = "marathahalli"
MAX_BUDGET = 2000
MIN_RATING = 4.0
TOP_N = 5
LOCAL_CACHE = ROOT / "phase1" / "cache" / "zomato_raw.csv"


def filter_by_locality_and_budget(
    restaurants: list,
) -> list:
    filtered = []
    seen_names: set[str] = set()
    for r in restaurants:
        locality = (r.locality or "").lower()
        if LOCALITY not in locality:
            continue
        if r.rating is None or r.rating < MIN_RATING:
            continue
        if r.cost_for_two is None or r.cost_for_two > MAX_BUDGET:
            continue
        if r.name in seen_names:
            continue
        seen_names.add(r.name)
        filtered.append(r)
    return sorted(
        filtered,
        key=lambda r: (r.rating or 0, r.votes),
        reverse=True,
    )


def main() -> None:
    _load_env_files()

    print("Loading dataset from local cache...")
    if not LOCAL_CACHE.exists():
        logger.error("Dataset not found at %s", LOCAL_CACHE)
        sys.exit(1)

    store = build_store(source_path=LOCAL_CACHE)
    marathahalli_all = [
        r for r in store.get_by_city("Bangalore")
        if LOCALITY in (r.locality or "").lower()
    ]
    candidates = filter_by_locality_and_budget(marathahalli_all)[:20]

    print(f"\nFound {len(candidates)} candidates in Marathahalli (rating >= {MIN_RATING}, budget <= Rs.{MAX_BUDGET})")

    if not candidates:
        print("No matches for Marathahalli with rating >= 4 and budget <= Rs.2000.")
        print(f"Total Marathahalli restaurants in dataset: {len(marathahalli_all)}")
        if marathahalli_all:
            print("Sample (unfiltered):")
            for r in marathahalli_all[:5]:
                print(f"  - {r.name} | Rs.{r.cost_for_two} | rating {r.rating}")
        sys.exit(0)

    for r in candidates[:10]:
        print(f"  - {r.name} | Rs.{r.cost_for_two} | rating {r.rating} | {r.cuisine}")

    preferences = UserPreferences(
        location="Marathahalli, Bangalore",
        budget="high",
        min_rating=MIN_RATING,
        additional_notes=f"Budget up to Rs.{MAX_BUDGET} for two",
    )

    filter_result = FilterResult(candidates=candidates)
    prompt = build_prompt(preferences, candidates, top_n=TOP_N)

    integration = IntegrationResult(
        filter_result=filter_result,
        prompt=prompt,
        candidates_formatted=[r.to_dict() for r in candidates],
    )

    print(f"\nCalling Groq for top {TOP_N} recommendations...")
    try:
        client = GroqClient()
        response = build_recommendations(
            integration, preferences, top_n=TOP_N, client=client
        )
    except Exception as exc:
        logger.warning("Groq unavailable (%s), using rating fallback.", exc)
        from phase4.fallback import build_fallback_recommendations

        response = build_fallback_recommendations(
            candidates, preferences, top_n=TOP_N
        )

    print("\n" + "=" * 60)
    print(f"TOP {TOP_N} RESTAURANTS IN MARATHAHALLI")
    print("=" * 60)
    if response.summary:
        print(response.summary)
    if response.message:
        print(response.message)

    for rec in response.recommendations[:TOP_N]:
        print(f"\n#{rec.rank}  {rec.name}")
        print(f"    Location: {rec.location}  |  Cuisine: {rec.cuisine}")
        print(f"    Cost: Rs.{rec.cost_for_two}  |  Rating: {rec.rating}")
        print(f"    Why: {rec.explanation}")

    print("\n" + "=" * 60)
    print(json.dumps([r.to_dict() for r in response.recommendations[:TOP_N]], indent=2))


if __name__ == "__main__":
    main()
