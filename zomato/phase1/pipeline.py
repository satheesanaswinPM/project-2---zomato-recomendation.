"""Build a RestaurantStore from raw or cached data."""

from __future__ import annotations

from pathlib import Path

from phase1.loader import load_raw_dataset
from phase1.preprocessor import preprocess
from phase1.store import RestaurantStore


def build_store(
    *,
    force_refresh: bool = False,
    source_path: Path | str | None = None,
) -> RestaurantStore:
    raw_df = load_raw_dataset(force_refresh=force_refresh, source_path=source_path)
    restaurants = preprocess(raw_df)
    return RestaurantStore(restaurants)
