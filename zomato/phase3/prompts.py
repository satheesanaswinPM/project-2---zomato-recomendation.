"""Prompt templates for the recommendation LLM."""

from __future__ import annotations

import json

from phase1.models import Restaurant
from phase2.preferences import UserPreferences
from phase3.formatter import format_candidates_json
from phase3.models import PromptBundle

PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """You are a restaurant recommendation assistant.
Only recommend restaurants from the provided candidate list.
Do not invent or mention restaurants that are not in the list.
Return valid JSON only."""


def _format_preferences(preferences: UserPreferences) -> str:
    lines = [
        f"location: {preferences.location}",
        f"budget: {preferences.budget}",
        f"cuisine: {preferences.cuisine or 'any'}",
        f"min_rating: {preferences.min_rating}",
        f"additional_notes: {preferences.additional_notes or 'none'}",
    ]
    return "\n".join(lines)


def build_prompt(
    preferences: UserPreferences,
    candidates: list[Restaurant],
    *,
    top_n: int = 5,
) -> PromptBundle:
    """Assemble system and user prompts with grounded candidate data."""
    candidate_json = format_candidates_json(candidates)
    user_prompt = f"""Preferences:
{_format_preferences(preferences)}

Candidates:
{candidate_json}

Task: Rank the top {min(top_n, len(candidates))} restaurants that best match the preferences.
Explain briefly why each recommendation fits.

Return JSON array with objects containing:
- rank (integer, starting at 1)
- name (must exactly match a candidate name)
- explanation (short string)

Example:
[
  {{"rank": 1, "name": "Example Restaurant", "explanation": "Matches budget and cuisine."}}
]"""

    return PromptBundle(
        version=PROMPT_VERSION,
        system=SYSTEM_PROMPT,
        user=user_prompt,
        candidate_names=[r.name for r in candidates],
    )
