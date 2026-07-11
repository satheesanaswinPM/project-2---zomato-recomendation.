"""Wire phases 1–5 into a single recommendation search."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from phase1.pipeline import build_store
from phase2.preferences import parse_preferences
from phase3.pipeline import build_integration
from phase4.llm_client import GroqClient
from phase4.models import RecommendationResponse
from phase4.pipeline import build_recommendations
from phase4.validate import _load_env_files
from phase5.models import DisplayPayload
from phase5.pipeline import build_display_payload

logger = logging.getLogger(__name__)

LOCAL_CACHE = Path(__file__).resolve().parents[1] / "phase1" / "cache" / "zomato_raw.csv"
DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "phase1"
    / "tests"
    / "fixtures"
    / "sample_zomato.csv"
)


def get_store_source() -> Path | None:
    if LOCAL_CACHE.exists():
        return LOCAL_CACHE
    return None


_STORE_CACHE: dict[str, Any] = {}


def build_default_store(*, source_path: Path | None = None):
    if source_path is not None:
        return build_store(source_path=source_path)

    cached = get_store_source()
    cache_key = str(cached) if cached is not None else "__default__"
    if cache_key not in _STORE_CACHE:
        if cached is not None:
            _STORE_CACHE[cache_key] = build_store(source_path=cached)
        else:
            _STORE_CACHE[cache_key] = build_store()
    return _STORE_CACHE[cache_key]


@dataclass
class SearchResult:
    ok: bool
    display: DisplayPayload | None = None
    errors: dict[str, str] = field(default_factory=dict)
    status_code: int = 200


def run_recommendation_search(
    raw_input: Mapping[str, Any],
    *,
    top_n: int = 5,
    client: Any | None = None,
    store: Any | None = None,
    source_path: Path | None = None,
) -> SearchResult:
    """
    Validate preferences and run the full recommendation pipeline.

    Returns validation errors (400) or a display payload (200).
    """
    result = parse_preferences(raw_input)
    if not result.is_valid:
        return SearchResult(ok=False, errors=result.errors, status_code=400)

    preferences = result.preferences
    assert preferences is not None

    try:
        if store is None:
            store = build_default_store(source_path=source_path)
        integration = build_integration(store, preferences)

        if client is None:
            _load_env_files()
            client = GroqClient()

        response = build_recommendations(
            integration, preferences, top_n=top_n, client=client
        )
    except Exception as exc:
        logger.exception("Recommendation search failed")
        response = RecommendationResponse(message=f"Something went wrong: {exc}")

    display = build_display_payload(response)
    return SearchResult(ok=True, display=display, status_code=200)
