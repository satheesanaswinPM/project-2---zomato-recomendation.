"""Stream-filter locality restaurants from the Zomato CSV on Hugging Face."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from phase1.models import Restaurant
from phase1.preprocessor import (
    extract_city_from_address,
    normalize_city,
    parse_cost,
    parse_cuisines,
    parse_rating,
)

logger = logging.getLogger(__name__)

CSV_URL = (
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/5738e9eda2fad49ad51c6e0ed26e761d9b947133/zomato.csv"
)
COST_COLUMN = "approx_cost(for two people)"
COLUMNS = [
    "name",
    "location",
    "cuisines",
    COST_COLUMN,
    "rate",
    "votes",
    "rest_type",
    "address",
]
CHUNK_SIZE = 3000


def _row_to_restaurant(row: Any) -> Restaurant | None:
    name = str(row.get("name") or "").strip()
    if not name:
        return None

    locality = str(row.get("location") or "").strip() or None
    city = extract_city_from_address(row.get("address")) or "Bangalore"
    city = normalize_city(city) or "Bangalore"

    votes_raw = row.get("votes", 0)
    try:
        votes = int(votes_raw) if pd.notna(votes_raw) else 0
    except (TypeError, ValueError):
        votes = 0

    rest_type = row.get("rest_type")
    restaurant_type = str(rest_type).strip() if pd.notna(rest_type) and rest_type else None

    return Restaurant(
        name=name,
        location=city,
        cuisine=parse_cuisines(row.get("cuisines")),
        cost_for_two=parse_cost(row.get(COST_COLUMN)),
        rating=parse_rating(row.get("rate")),
        votes=max(votes, 0),
        restaurant_type=restaurant_type,
        locality=locality,
    )


def stream_locality_restaurants(locality_query: str = "marathahalli") -> list[Restaurant]:
    """Stream CSV in chunks and collect restaurants matching the locality."""
    needle = locality_query.lower()
    results: list[Restaurant] = []
    logger.info("Streaming CSV chunks from Hugging Face for '%s'", locality_query)

    try:
        reader = pd.read_csv(
            CSV_URL,
            usecols=COLUMNS,
            chunksize=CHUNK_SIZE,
            on_bad_lines="skip",
        )
    except Exception as exc:
        raise RuntimeError(f"Could not open dataset CSV stream: {exc}") from exc

    for chunk in reader:
        location_mask = chunk["location"].astype(str).str.lower().str.contains(
            needle, na=False
        )
        address_mask = chunk["address"].astype(str).str.lower().str.contains(
            needle, na=False
        )
        matched = chunk[location_mask | address_mask]
        for _, row in matched.iterrows():
            restaurant = _row_to_restaurant(row)
            if restaurant:
                results.append(restaurant)

    logger.info("Found %d restaurants matching '%s'", len(results), locality_query)
    return results


def stream_marathahalli_restaurants() -> list[Restaurant]:
    return stream_locality_restaurants("marathahalli")
