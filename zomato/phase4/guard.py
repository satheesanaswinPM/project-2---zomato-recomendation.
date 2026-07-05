"""Validate LLM recommendations against the candidate restaurant list."""

from __future__ import annotations

import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)

FUZZY_CUTOFF = 0.85


def _match_name(name: str, candidate_names: list[str]) -> str | None:
    if name in candidate_names:
        return name

    matches = get_close_matches(name, candidate_names, n=1, cutoff=FUZZY_CUTOFF)
    if matches:
        logger.warning("Fuzzy matched hallucinated name '%s' to '%s'", name, matches[0])
        return matches[0]
    return None


def guard_recommendations(
    items: list[dict],
    candidate_names: list[str],
) -> tuple[list[dict], list[str]]:
    """
    Keep only recommendations that map to real candidates.

    Returns sanitized items and warning messages for stripped hallucinations.
    """
    warnings: list[str] = []
    seen: set[str] = set()
    sanitized: list[dict] = []

    for item in items:
        matched = _match_name(item["name"], candidate_names)
        if matched is None:
            warnings.append(f"Removed hallucinated restaurant: {item['name']}")
            continue
        if matched in seen:
            continue
        seen.add(matched)
        sanitized.append({**item, "name": matched})

    for index, item in enumerate(sanitized, start=1):
        item["rank"] = index

    return sanitized, warnings
