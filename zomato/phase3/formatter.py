"""Format restaurant candidates for LLM consumption."""

from __future__ import annotations

import json

from phase1.models import Restaurant


def restaurant_to_candidate(restaurant: Restaurant) -> dict:
    return {
        "name": restaurant.name,
        "location": restaurant.location,
        "cuisine": restaurant.cuisine,
        "cost_for_two": restaurant.cost_for_two,
        "rating": restaurant.rating,
        "votes": restaurant.votes,
    }


def format_candidates(candidates: list[Restaurant]) -> list[dict]:
    """Return compact candidate summaries for prompts."""
    return [restaurant_to_candidate(r) for r in candidates]


def format_candidates_json(candidates: list[Restaurant], *, indent: int | None = None) -> str:
    return json.dumps(format_candidates(candidates), indent=indent)


def format_candidates_markdown(candidates: list[Restaurant]) -> str:
    if not candidates:
        return "_No candidates._"

    lines = ["| Name | Location | Cuisine | Cost | Rating |", "|---|---|---|---:|---:|"]
    for restaurant in candidates:
        cuisine = ", ".join(restaurant.cuisine)
        cost = restaurant.cost_for_two if restaurant.cost_for_two is not None else "N/A"
        rating = restaurant.rating if restaurant.rating is not None else "N/A"
        lines.append(
            f"| {restaurant.name} | {restaurant.location} | {cuisine} | {cost} | {rating} |"
        )
    return "\n".join(lines)
