"""In-memory session context for multi-turn refinement."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from phase2.preferences import UserPreferences


@dataclass
class SessionState:
    session_id: str
    preferences: UserPreferences
    last_display: dict[str, Any] | None = None
    history: list[str] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)


class SessionStore:
    """Process-local session store (good enough for single-instance demos)."""

    def __init__(self, *, ttl_seconds: int = 3600, max_sessions: int = 200):
        self.ttl_seconds = ttl_seconds
        self.max_sessions = max_sessions
        self._lock = threading.Lock()
        self._sessions: dict[str, SessionState] = {}

    def create(
        self,
        preferences: UserPreferences,
        *,
        display: dict[str, Any] | None = None,
        query_label: str | None = None,
    ) -> SessionState:
        self._purge()
        session_id = uuid.uuid4().hex
        state = SessionState(
            session_id=session_id,
            preferences=preferences,
            last_display=display,
            history=[query_label] if query_label else [],
        )
        with self._lock:
            self._sessions[session_id] = state
            self._trim_locked()
        return state

    def get(self, session_id: str) -> SessionState | None:
        self._purge()
        with self._lock:
            return self._sessions.get(session_id)

    def update(
        self,
        session_id: str,
        *,
        preferences: UserPreferences | None = None,
        display: dict[str, Any] | None = None,
        follow_up: str | None = None,
    ) -> SessionState | None:
        with self._lock:
            state = self._sessions.get(session_id)
            if state is None:
                return None
            if preferences is not None:
                state.preferences = preferences
            if display is not None:
                state.last_display = display
            if follow_up:
                state.history.append(follow_up)
            state.updated_at = time.time()
            return state

    def _purge(self) -> None:
        cutoff = time.time() - self.ttl_seconds
        with self._lock:
            expired = [sid for sid, s in self._sessions.items() if s.updated_at < cutoff]
            for sid in expired:
                del self._sessions[sid]

    def _trim_locked(self) -> None:
        if len(self._sessions) <= self.max_sessions:
            return
        ordered = sorted(self._sessions.items(), key=lambda item: item[1].updated_at)
        overflow = len(self._sessions) - self.max_sessions
        for sid, _ in ordered[:overflow]:
            del self._sessions[sid]


# Shared singleton used by the Phase 6 API process.
SESSION_STORE = SessionStore()
