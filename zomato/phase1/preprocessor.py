"""Clean and normalize raw Zomato dataset rows."""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd

from phase1.models import Restaurant

logger = logging.getLogger(__name__)

CITY_ALIASES: dict[str, str] = {
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "blr": "Bangalore",
    "banglore": "Bangalore",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
}

COST_COLUMN = "approx_cost(for two people)"
MIN_RATING = 0.0
MAX_RATING = 5.0


def normalize_city(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    cleaned = str(value).strip()
    key = cleaned.lower()
    return CITY_ALIASES.get(key, cleaned.title())


def parse_cuisines(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ["Unknown"]
    text = str(value).strip()
    if not text:
        return ["Unknown"]
    parts = re.split(r"[,;/]", text)
    cuisines = [part.strip() for part in parts if part.strip()]
    return cuisines or ["Unknown"]


def parse_rating(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"new", "nan", "-", "none"}:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None

    rating = float(match.group(1))
    if rating < MIN_RATING or rating > MAX_RATING:
        logger.debug("Clamping out-of-range rating: %s", rating)
        rating = max(MIN_RATING, min(MAX_RATING, rating))
    return rating


def parse_cost(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None

    digits = re.sub(r"[^\d.]", "", text.replace(",", ""))
    if not digits:
        return None

    try:
        cost = float(digits)
    except ValueError:
        return None
    return cost if cost >= 0 else None


def extract_city_from_address(address: Any) -> str | None:
    if address is None or (isinstance(address, float) and pd.isna(address)):
        return None
    text = str(address).strip()
    if not text:
        return None

    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        return None

    for part in reversed(parts):
        normalized = normalize_city(part)
        if normalized:
            return normalized
    return None


def _clean_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _row_to_restaurant(row: pd.Series) -> Restaurant | None:
    name = _clean_text(row.get("name"))
    locality = _clean_text(row.get("location"))
    city = extract_city_from_address(row.get("address")) or "Bangalore"
    city = normalize_city(city) or "Bangalore"

    if not name:
        return None

    rating = parse_rating(row.get("rate"))
    votes_raw = row.get("votes", 0)
    try:
        votes = int(votes_raw) if pd.notna(votes_raw) else 0
    except (TypeError, ValueError):
        votes = 0
    votes = max(votes, 0)

    return Restaurant(
        name=name,
        location=city,
        cuisine=parse_cuisines(row.get("cuisines")),
        cost_for_two=parse_cost(row.get(COST_COLUMN)),
        rating=rating,
        votes=votes,
        restaurant_type=_clean_text(row.get("rest_type")),
        locality=locality,
    )


def preprocess(raw_df: pd.DataFrame) -> list[Restaurant]:
    """Transform raw dataset rows into cleaned Restaurant records."""
    restaurants: list[Restaurant] = []
    dropped_missing_name = 0
    dropped_missing_location = 0

    for _, row in raw_df.iterrows():
        restaurant = _row_to_restaurant(row)
        if restaurant is None:
            dropped_missing_name += 1
            continue
        if not restaurant.location:
            dropped_missing_location += 1
            continue
        restaurants.append(restaurant)

    logger.info(
        "Preprocessed %d restaurants (dropped %d without name, %d without location)",
        len(restaurants),
        dropped_missing_name,
        dropped_missing_location,
    )
    return restaurants
