"""Rank restaurants and generate explanations using Groq."""

from __future__ import annotations

import logging

from phase1.models import Restaurant
from phase2.preferences import UserPreferences
from phase3.models import PromptBundle
from phase4.fallback import build_fallback_recommendations
from phase4.guard import guard_recommendations
from phase4.llm_client import GroqClient, LLMClient
from phase4.models import RecommendationResponse, RecommendationResult
from phase4.parser import ParseError, parse_recommendations

logger = logging.getLogger(__name__)

STRICT_JSON_SUFFIX = """

Return ONLY a valid JSON array. Do not include markdown fences or extra text.
Each item must contain rank, name, and explanation fields.
"""


def _candidate_lookup(candidates: list[Restaurant]) -> dict[str, Restaurant]:
    return {restaurant.name: restaurant for restaurant in candidates}


def _attach_metadata(
    items: list[dict],
    candidates: list[Restaurant],
) -> list[RecommendationResult]:
    lookup = _candidate_lookup(candidates)
    results: list[RecommendationResult] = []

    for item in items:
        restaurant = lookup.get(item["name"])
        if restaurant is None:
            continue
        explanation = item.get("explanation") or (
            f"Recommended based on your preferences in {restaurant.location}."
        )
        results.append(
            RecommendationResult(
                rank=item["rank"],
                name=restaurant.name,
                location=restaurant.location,
                cuisine=", ".join(restaurant.cuisine),
                cost_for_two=restaurant.cost_for_two,
                rating=restaurant.rating,
                explanation=explanation,
                source="llm",
            )
        )
    return results


def _build_summary(recommendations: list[RecommendationResult]) -> str | None:
    if not recommendations:
        return None
    top = recommendations[:3]
    names = ", ".join(item.name for item in top)
    return f"Top recommendations for you: {names}."


def recommend(
    prompt: PromptBundle,
    candidates: list[Restaurant],
    preferences: UserPreferences,
    *,
    top_n: int = 5,
    client: LLMClient | None = None,
    use_fallback_on_error: bool = True,
) -> RecommendationResponse:
    """Send prompt to Groq, parse response, validate, and attach metadata."""
    if not candidates:
        return RecommendationResponse(
            message="No candidates to recommend. Try broadening your search filters.",
        )

    llm_client = client or GroqClient()
    warnings: list[str] = []

    try:
        raw = llm_client.complete(prompt.system, prompt.user)
    except Exception as exc:
        logger.warning("Groq call failed: %s", exc)
        if use_fallback_on_error:
            return build_fallback_recommendations(
                candidates,
                preferences,
                top_n=top_n,
                reason="AI unavailable; ranked by rating instead.",
            )
        raise

    try:
        parsed = parse_recommendations(raw)
    except ParseError:
        logger.warning("Initial LLM JSON parse failed; retrying with stricter instructions.")
        try:
            raw = llm_client.complete(prompt.system, prompt.user + STRICT_JSON_SUFFIX)
            parsed = parse_recommendations(raw)
        except (ParseError, Exception) as exc:
            logger.warning("LLM parse retry failed: %s", exc)
            if use_fallback_on_error:
                return build_fallback_recommendations(
                    candidates,
                    preferences,
                    top_n=top_n,
                    reason="Could not parse AI response; ranked by rating instead.",
                )
            raise

    sanitized, guard_warnings = guard_recommendations(parsed, prompt.candidate_names)
    warnings.extend(guard_warnings)

    recommendations = _attach_metadata(sanitized, candidates)[:top_n]

    if not recommendations and use_fallback_on_error:
        fallback = build_fallback_recommendations(
            candidates,
            preferences,
            top_n=top_n,
            reason="AI results were invalid; ranked by rating instead.",
        )
        fallback.warnings.extend(warnings)
        return fallback

    return RecommendationResponse(
        recommendations=recommendations,
        summary=_build_summary(recommendations),
        source="llm",
        warnings=warnings,
    )
