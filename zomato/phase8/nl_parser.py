"""Parse natural-language queries into UserPreferences using an LLM."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from phase2.preferences import UserPreferences, parse_preferences

logger = logging.getLogger(__name__)

NL_SYSTEM_PROMPT = """You convert restaurant search requests into JSON preferences.
Return ONLY valid JSON with these keys:
{
  "location": string (Bangalore locality or city, required),
  "budget": "low" | "medium" | "high" | "custom",
  "max_budget": number or null (set when budget is custom or a rupee amount is given),
  "cuisine": string or null,
  "min_rating": number 0-5 (default 0),
  "additional_notes": string (service needs, vibe, etc.)
}

Budget guide for cost for two:
- low: up to about Rs.500
- medium: about Rs.501-1500
- high: Rs.1501+
- custom: when a specific max amount is stated (put amount in max_budget)

If location is missing, use "Bangalore".
Do not wrap the JSON in markdown."""

NL_USER_TEMPLATE = """Parse this restaurant search request into preferences JSON:

{query}
"""


@dataclass
class NLParseResult:
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


def parse_natural_language(
    query: str,
    *,
    client: Any,
) -> NLParseResult:
    """Use an LLM client to map free text into validated UserPreferences."""
    text = (query or "").strip()
    if not text:
        return NLParseResult(
            ok=False,
            errors={"query": "Enter a search phrase, e.g. Cheap Italian in Indiranagar."},
        )

    try:
        raw_text = client.complete(
            NL_SYSTEM_PROMPT,
            NL_USER_TEMPLATE.format(query=text),
        )
        payload = _extract_json(raw_text)
    except Exception as exc:
        logger.exception("NL parse failed")
        return NLParseResult(
            ok=False,
            message=f"Could not parse natural language query: {exc}",
            errors={"query": "Unable to understand that request. Try again."},
        )

    validated = parse_preferences(payload)
    if not validated.is_valid:
        return NLParseResult(
            ok=False,
            raw=payload,
            errors=validated.errors or {"query": "Parsed preferences were invalid."},
        )

    return NLParseResult(
        ok=True,
        preferences=validated.preferences,
        raw=payload,
    )
