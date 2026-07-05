"""Normalize Phase 4 recommendation response for display."""

from __future__ import annotations

from phase4.models import RecommendationResponse
from phase5.models import DisplayPayload, DisplayRecommendation


def _format_cost(cost: float | None) -> str:
    if cost is None:
        return "Price not available"
    if cost == int(cost):
        return f"Rs.{int(cost)}"
    return f"Rs.{cost:.0f}"


def _format_rating(rating: float | None) -> str:
    if rating is None:
        return "Unrated"
    return f"{rating:.1f}"


def _default_explanation(name: str, location: str) -> str:
    return f"Recommended based on your preferences in {location}."


def parse_response(response: RecommendationResponse) -> DisplayPayload:
    """Convert a RecommendationResponse into a display-ready payload."""
    if response.is_empty:
        is_error = bool(response.message)
        return DisplayPayload(
            recommendations=[],
            summary=response.summary,
            message=response.message or "No recommendations found. Try broadening your search.",
            warnings=list(response.warnings),
            source=response.source,
            is_empty=True,
            is_error=is_error,
            title="No Results" if is_error else "No Matches",
        )

    items = [
        DisplayRecommendation(
            rank=rec.rank,
            name=rec.name,
            location=rec.location,
            cuisine=rec.cuisine or "Cuisine not listed",
            cost_label=_format_cost(rec.cost_for_two),
            rating_label=_format_rating(rec.rating),
            explanation=rec.explanation or _default_explanation(rec.name, rec.location),
            source=rec.source,
        )
        for rec in response.recommendations
    ]

    summary = response.summary
    message = response.message
    if response.source == "fallback" and not message:
        message = "Ranked by rating (AI explanations unavailable)."

    return DisplayPayload(
        recommendations=items,
        summary=summary,
        message=message,
        warnings=list(response.warnings),
        source=response.source,
        is_empty=False,
        is_error=False,
    )
