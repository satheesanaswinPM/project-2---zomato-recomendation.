"""Phase 8 pipelines: NL parse and follow-up refine + search."""

from __future__ import annotations

from typing import Any

from phase4.llm_client import GroqClient
from phase4.validate import _load_env_files
from phase6.orchestrator import SearchResult, run_recommendation_search
from phase8.cache import SEARCH_CACHE, cache_key_for_prefs
from phase8.nl_parser import NLParseResult, parse_natural_language
from phase8.refinement import RefineResult, refine_preferences
from phase8.session import SESSION_STORE, SessionState


def _client_or_default(client: Any | None) -> Any:
    if client is not None:
        return client
    _load_env_files()
    return GroqClient()


def parse_nl_query(query: str, *, client: Any | None = None) -> NLParseResult:
    return parse_natural_language(query, client=_client_or_default(client))


def run_cached_search(
    raw_input: dict[str, Any],
    *,
    client: Any | None = None,
    use_cache: bool = True,
    session_id: str | None = None,
    query_label: str | None = None,
) -> tuple[SearchResult, str | None, bool]:
    """
    Run recommendation search with cache + session.

    Returns (search_result, session_id, cache_hit).
    """
    key = cache_key_for_prefs(raw_input)
    if use_cache:
        hit = SEARCH_CACHE.get(key)
        if hit is not None:
            from phase5.models import DisplayPayload
            from phase5.parser import parse_response
            from phase4.models import RecommendationResponse

            # Rebuild DisplayPayload from cached dict via lightweight wrap
            display = _display_from_dict(hit.display)
            result = SearchResult(ok=True, display=display, status_code=200)
            sid = session_id
            if sid is None:
                from phase2.preferences import parse_preferences

                prefs = parse_preferences(raw_input).preferences
                if prefs is not None:
                    state = SESSION_STORE.create(
                        prefs, display=hit.display, query_label=query_label or hit.label
                    )
                    sid = state.session_id
            return result, sid, True

    search = run_recommendation_search(raw_input, client=client)
    sid = session_id
    if search.ok and search.display is not None:
        display_dict = search.display.to_dict()
        from phase2.preferences import parse_preferences

        prefs_result = parse_preferences(raw_input)
        prefs = prefs_result.preferences
        label = query_label or (
            f"{raw_input.get('location', '?')} · {raw_input.get('budget', '?')}"
        )
        SEARCH_CACHE.put(
            key,
            display=display_dict,
            preferences=dict(raw_input),
            label=label,
        )
        if prefs is not None:
            if sid:
                SESSION_STORE.update(
                    sid, preferences=prefs, display=display_dict, follow_up=None
                )
            else:
                state = SESSION_STORE.create(
                    prefs, display=display_dict, query_label=label
                )
                sid = state.session_id

    return search, sid, False


def refine_and_search(
    session_id: str,
    follow_up: str,
    *,
    client: Any | None = None,
) -> tuple[RefineResult, SearchResult | None, SessionState | None, bool]:
    state = SESSION_STORE.get(session_id)
    if state is None:
        return (
            RefineResult(
                ok=False,
                errors={"session_id": "Session expired or not found. Run a new search."},
            ),
            None,
            None,
            False,
        )

    llm = _client_or_default(client)
    refined = refine_preferences(state.preferences, follow_up, client=llm)
    if not refined.ok or refined.preferences is None:
        return refined, None, state, False

    raw = refined.preferences.to_dict()
    # Drop nulls for cache key stability
    body = {k: v for k, v in raw.items() if v is not None and v != ""}
    search, sid, cache_hit = run_cached_search(
        body,
        client=llm,
        session_id=session_id,
        query_label=follow_up,
    )
    if search.ok and search.display is not None:
        SESSION_STORE.update(
            session_id,
            preferences=refined.preferences,
            display=search.display.to_dict(),
            follow_up=follow_up,
        )
    return refined, search, SESSION_STORE.get(session_id), cache_hit


def _display_from_dict(data: dict[str, Any]):
    from phase5.models import DisplayPayload, DisplayRecommendation

    recs = [
        DisplayRecommendation(
            rank=int(item.get("rank", 0)),
            name=str(item.get("name", "")),
            location=str(item.get("location", "")),
            cuisine=str(item.get("cuisine", "")),
            cost_label=str(item.get("cost_label", "")),
            rating_label=str(item.get("rating_label", "")),
            explanation=str(item.get("explanation", "")),
            source=str(item.get("source", "llm")),
        )
        for item in data.get("recommendations", [])
    ]
    return DisplayPayload(
        recommendations=recs,
        summary=data.get("summary"),
        title=data.get("title") or "Your Recommendations",
        message=data.get("message"),
        warnings=list(data.get("warnings") or []),
        source=str(data.get("source") or "llm"),
        is_empty=bool(data.get("is_empty")),
        is_error=bool(data.get("is_error")),
    )
