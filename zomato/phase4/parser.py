"""Parse structured JSON recommendations from LLM output."""

from __future__ import annotations

import json
import re
from typing import Any


class ParseError(ValueError):
    pass


def _extract_json_text(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text.strip()


def _normalize_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("recommendations", "results", "items", "restaurants"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    raise ParseError("LLM response is not a JSON array of recommendation objects.")


def parse_recommendations(text: str) -> list[dict[str, Any]]:
    """Extract recommendation objects with rank, name, and explanation."""
    raw = _extract_json_text(text)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON in LLM response: {exc}") from exc

    items = _normalize_items(payload)
    if not items:
        raise ParseError("LLM response contained no recommendation items.")

    parsed: list[dict[str, Any]] = []
    for item in items:
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        rank_raw = item.get("rank", len(parsed) + 1)
        try:
            rank = int(rank_raw)
        except (TypeError, ValueError):
            rank = len(parsed) + 1
        explanation = str(item.get("explanation", "")).strip()
        parsed.append({"rank": rank, "name": name, "explanation": explanation})

    if not parsed:
        raise ParseError("No valid recommendation items after parsing.")

    parsed.sort(key=lambda item: item["rank"])
    for index, item in enumerate(parsed, start=1):
        item["rank"] = index
    return parsed
