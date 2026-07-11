"""Apply follow-up refinements to existing preferences."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from phase2.preferences import UserPreferences, parse_preferences

logger = logging.getLogger(__name__)

REFINE_SYSTEM_PROMPT = """You update restaurant search preferences based on a follow-up instruction.
Return ONLY valid JSON with the full updated preferences:
{
  "location": string,
  "budget": "low" | "medium" | "high" | "custom",
  "max_budget": number or null,
  "cuisine": string or null,
  "min_rating": number 0-5,
  "additional_notes": string
}

Rules:
- Start from the current preferences and apply the follow-up.
- "cheaper" / "lower budget" → move budget down one level (high→medium→low) or lower max_budget by ~30%.
- "more expensive" / "premium" → raise budget one level or raise max_budget.
- "only outdoor seating" / service requests → put into additional_notes (merge, don't erase useful notes).
- Cuisine changes replace cuisine when a new cuisine is named.
- Keep location unless the user asks to change area/city.
Do not wrap JSON in markdown."""

REFINE_USER_TEMPLATE = """Current preferences:
{current}

Follow-up:
{follow_up}

Return the updated preferences JSON.
"""


@dataclass
class RefineResult:
    ok: bool
    preferences: UserPreferences | None = None
    raw: dict[str, Any] | None = None
    errors: dict[str, str] | None = None
    message: str | None = None


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(cleaned[start : end + 1])


def _heuristic_refine(
    current: UserPreferences, follow_up: str
) -> UserPreferences | None:
    """Lightweight offline refinement for common phrases (tests / fallback)."""
    text = follow_up.lower()
    data = current.to_dict()

    if "cheaper" in text or "lower budget" in text or "less expensive" in text:
        if data.get("max_budget"):
            data["budget"] = "custom"
            data["max_budget"] = max(100, int(float(data["max_budget"]) * 0.7))
        else:
            ladder = {"high": "medium", "medium": "low", "low": "low"}
            data["budget"] = ladder.get(data.get("budget", "medium"), "low")
        return parse_preferences(data).preferences

    if "expensive" in text or "premium" in text or "higher budget" in text:
        if data.get("max_budget"):
            data["budget"] = "custom"
            data["max_budget"] = int(float(data["max_budget"]) * 1.3)
        else:
            ladder = {"low": "medium", "medium": "high", "high": "high"}
            data["budget"] = ladder.get(data.get("budget", "medium"), "high")
        return parse_preferences(data).preferences

    service_bits = []
    for phrase in (
        "outdoor seating",
        "family-friendly",
        "family friendly",
        "quick service",
        "parking",
        "rooftop",
        "live music",
    ):
        if phrase in text:
            service_bits.append(phrase)
    if service_bits:
        existing = (data.get("additional_notes") or "").strip()
        merged = ", ".join(filter(None, [existing, *service_bits]))
        data["additional_notes"] = merged
        return parse_preferences(data).preferences

    return None


def refine_preferences(
    current: UserPreferences,
    follow_up: str,
    *,
    client: Any | None = None,
) -> RefineResult:
    text = (follow_up or "").strip()
    if not text:
        return RefineResult(
            ok=False,
            errors={"follow_up": "Enter a follow-up, e.g. Show me cheaper options."},
        )

    heuristic = _heuristic_refine(current, text)
    if heuristic is not None and client is None:
        return RefineResult(ok=True, preferences=heuristic, raw=heuristic.to_dict())

    if client is None:
        if heuristic is not None:
            return RefineResult(ok=True, preferences=heuristic, raw=heuristic.to_dict())
        return RefineResult(
            ok=False,
            errors={"follow_up": "Could not apply that follow-up without the LLM."},
        )

    try:
        raw_text = client.complete(
            REFINE_SYSTEM_PROMPT,
            REFINE_USER_TEMPLATE.format(
                current=json.dumps(current.to_dict(), indent=2),
                follow_up=text,
            ),
        )
        payload = _extract_json(raw_text)
    except Exception as exc:
        logger.exception("Refine failed")
        if heuristic is not None:
            return RefineResult(ok=True, preferences=heuristic, raw=heuristic.to_dict())
        return RefineResult(
            ok=False,
            message=str(exc),
            errors={"follow_up": "Unable to refine preferences. Try again."},
        )

    validated = parse_preferences(payload)
    if not validated.is_valid:
        if heuristic is not None:
            return RefineResult(ok=True, preferences=heuristic, raw=heuristic.to_dict())
        return RefineResult(ok=False, raw=payload, errors=validated.errors)

    return RefineResult(ok=True, preferences=validated.preferences, raw=payload)
