"""Search result cache and recent-search history for Phase 6."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def cache_key_for_prefs(prefs: dict[str, Any]) -> str:
    """Stable hash for preference payloads."""
    normalized = {
        "location": str(prefs.get("location", "")).strip().lower(),
        "budget": str(prefs.get("budget", "")).strip().lower(),
        "max_budget": prefs.get("max_budget"),
        "cuisine": (str(prefs.get("cuisine") or "").strip().lower() or None),
        "min_rating": float(prefs.get("min_rating") or 0),
        "additional_notes": str(prefs.get("additional_notes") or "").strip().lower(),
    }
    blob = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class CacheEntry:
    key: str
    display: dict[str, Any]
    preferences: dict[str, Any]
    created_at: float = field(default_factory=time.time)
    label: str = ""


class SearchCache:
    """In-memory LRU-ish cache with optional JSON persistence for history."""

    def __init__(
        self,
        *,
        ttl_seconds: int = 1800,
        max_entries: int = 100,
        history_path: Path | None = None,
        max_history: int = 30,
    ):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.history_path = history_path
        self.max_history = max_history
        self._lock = threading.Lock()
        self._entries: dict[str, CacheEntry] = {}
        self._history: list[dict[str, Any]] = []
        if history_path and history_path.exists():
            try:
                self._history = json.loads(history_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._history = []

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if time.time() - entry.created_at > self.ttl_seconds:
                del self._entries[key]
                return None
            return entry

    def put(
        self,
        key: str,
        *,
        display: dict[str, Any],
        preferences: dict[str, Any],
        label: str | None = None,
    ) -> CacheEntry:
        entry = CacheEntry(
            key=key,
            display=display,
            preferences=preferences,
            label=label
            or f"{preferences.get('location', '?')} · {preferences.get('budget', '?')}",
        )
        with self._lock:
            self._entries[key] = entry
            self._trim_locked()
            self._history.insert(
                0,
                {
                    "key": key,
                    "label": entry.label,
                    "preferences": preferences,
                    "created_at": entry.created_at,
                },
            )
            self._history = self._history[: self.max_history]
            self._persist_history_locked()
        return entry

    def history(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._history[:limit])

    def _trim_locked(self) -> None:
        if len(self._entries) <= self.max_entries:
            return
        ordered = sorted(self._entries.items(), key=lambda item: item[1].created_at)
        overflow = len(self._entries) - self.max_entries
        for key, _ in ordered[:overflow]:
            del self._entries[key]

    def _persist_history_locked(self) -> None:
        if not self.history_path:
            return
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_path.write_text(
                json.dumps(self._history, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass


DEFAULT_HISTORY_PATH = (
    Path(__file__).resolve().parents[1] / "phase8" / "cache" / "search_history.json"
)

SEARCH_CACHE = SearchCache(history_path=DEFAULT_HISTORY_PATH)
