"""End-to-end Phase 4 pipeline from integration result to recommendations."""

from __future__ import annotations

from phase2.preferences import UserPreferences
from phase3.models import IntegrationResult
from phase4.llm_client import LLMClient
from phase4.models import RecommendationResponse
from phase4.recommender import recommend


def build_recommendations(
    integration: IntegrationResult,
    preferences: UserPreferences,
    *,
    top_n: int = 5,
    client: LLMClient | None = None,
) -> RecommendationResponse:
    """Run Phase 4 on a Phase 3 integration result."""
    if not integration.has_prompt or integration.prompt is None:
        message = integration.filter_result.message or (
            "No restaurants matched your preferences."
        )
        return RecommendationResponse(message=message)

    return recommend(
        integration.prompt,
        integration.filter_result.candidates,
        preferences,
        top_n=top_n,
        client=client,
    )
