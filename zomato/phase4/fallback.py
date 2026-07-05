"""Rating-based fallback when the LLM is unavailable or returns invalid output."""

from __future__ import annotations

from phase1.models import Restaurant
from phase2.preferences import UserPreferences
from phase4.models import RecommendationResponse, RecommendationResult


def _template_explanation(restaurant: Restaurant, preferences: UserPreferences) -> str:
    cuisine = ", ".join(restaurant.cuisine)
    rating = restaurant.rating if restaurant.rating is not None else "unrated"
    cost = restaurant.cost_for_two if restaurant.cost_for_two is not None else "unknown"
    return (
        f"Rated {rating} with {cuisine} cuisine in {restaurant.location}, "
        f"approx. cost for two Rs.{cost}. Matches your {preferences.budget} budget search."
    )


def build_fallback_recommendations(
    candidates: list[Restaurant],
    preferences: UserPreferences,
    *,
    top_n: int = 5,
    reason: str | None = None,
) -> RecommendationResponse:
    sorted_candidates = sorted(
        candidates,
        key=lambda r: (r.rating if r.rating is not None else -1.0, r.votes),
        reverse=True,
    )[:top_n]

    recommendations = [
        RecommendationResult(
            rank=index,
            name=restaurant.name,
            location=restaurant.location,
            cuisine=", ".join(restaurant.cuisine),
            cost_for_two=restaurant.cost_for_two,
            rating=restaurant.rating,
            explanation=_template_explanation(restaurant, preferences),
            source="fallback",
        )
        for index, restaurant in enumerate(sorted_candidates, start=1)
    ]

    names = ", ".join(item.name for item in recommendations[:3])
    summary = f"Top picks based on ratings: {names}." if names else None
    message = reason or "Ranked by rating (AI explanations unavailable)."

    return RecommendationResponse(
        recommendations=recommendations,
        summary=summary,
        source="fallback",
        message=message,
    )
