"""Phase 1 validation: load, preprocess, and query restaurants by city."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from phase1.pipeline import build_store
from phase1.preprocessor import normalize_city

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_FIXTURE = Path(__file__).parent / "tests" / "fixtures" / "sample_zomato.csv"


def run_validation(
    city: str = "Bangalore",
    sample_size: int = 3,
    source_path: Path | None = None,
) -> dict:
    store = build_store(source_path=source_path)
    report = store.validation_report()

    normalized_city = normalize_city(city) or city
    city_results = store.get_by_city(normalized_city)
    alias_results = store.get_by_city("Bengaluru")

    sample = [
        r.to_dict()
        for r in (city_results[:sample_size] if city_results else store.sample(sample_size))
    ]

    result = {
        **report,
        "query_city": normalized_city,
        "restaurants_in_city": len(city_results),
        "alias_bengaluru_count": len(alias_results),
        "alias_matches_canonical": len(alias_results) == len(city_results),
        "sample_restaurants": sample,
    }

    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase 1 data layer")
    parser.add_argument("--city", default="Bangalore", help="City to query")
    parser.add_argument("--refresh", action="store_true", help="Force re-download from Hugging Face")
    parser.add_argument(
        "--fixture",
        type=Path,
        nargs="?",
        const=DEFAULT_FIXTURE,
        help="Load from local CSV (defaults to bundled sample fixture)",
    )
    parser.add_argument("--sample", type=int, default=3, help="Sample rows to print")
    args = parser.parse_args()

    if args.refresh and args.fixture is not None:
        raise SystemExit("Use either --refresh or --fixture, not both.")

    if args.refresh:
        build_store(force_refresh=True)

    report = run_validation(
        city=args.city,
        sample_size=args.sample,
        source_path=args.fixture,
    )

    if report["total_restaurants"] == 0:
        raise SystemExit("Validation failed: no restaurants loaded")

    using_fixture = args.fixture is not None
    if (
        not using_fixture
        and report["restaurants_in_city"] == 0
        and args.city.lower() in {"bangalore", "bengaluru"}
    ):
        raise SystemExit(f"Validation failed: no restaurants found for {args.city}")

    if report["restaurants_in_city"] > 0 and not report["alias_matches_canonical"]:
        raise SystemExit("Validation failed: city alias normalization mismatch")

    logger.info("Phase 1 validation passed.")


if __name__ == "__main__":
    main()
