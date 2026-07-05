"""Orchestrate filtering, formatting, and prompt building."""

from __future__ import annotations

from phase1.store import RestaurantStore
from phase2.preferences import UserPreferences
from phase3.filter import FilterConfig, filter_restaurants
from phase3.formatter import format_candidates
from phase3.models import IntegrationResult
from phase3.prompts import build_prompt


def build_integration(
    store: RestaurantStore,
    preferences: UserPreferences,
    config: FilterConfig | None = None,
    *,
    top_n: int = 5,
) -> IntegrationResult:
    """Run the full Phase 3 pipeline: filter → format → prompt."""
    filter_result = filter_restaurants(store, preferences, config)
    candidates_formatted = format_candidates(filter_result.candidates)

    prompt = None
    if filter_result.candidates:
        prompt = build_prompt(preferences, filter_result.candidates, top_n=top_n)

    return IntegrationResult(
        filter_result=filter_result,
        prompt=prompt,
        candidates_formatted=candidates_formatted,
    )
