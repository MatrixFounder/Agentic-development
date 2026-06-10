"""In-memory session store with TTL expiry and sliding renewal."""

import logging
import random
import string
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("sessions")

DEFAULT_TTL = 1800
TOKEN_LENGTH = 32


@dataclass
class Session:
    token: str
    user_id: int
    expires_at: float


class SessionStore:
    def __init__(self, ttl: int = DEFAULT_TTL):
        self.ttl = ttl
        self._sessions: dict[str, Session] = {}

    def _new_token(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(TOKEN_LENGTH))

    def create(self, user_id: int) -> Session:
        token = self._new_token()
        session = Session(token, user_id, time.time() + self.ttl)
        self._sessions[token] = session
        return session

    def _purge_expired(self) -> None:
        now = time.time()
        dead = [t for t, s in self._sessions.items() if s.expires_at <= now]
        for t in dead:
            del self._sessions[t]

    def get(self, token: str) -> Optional[Session]:
        """Return the session for a token, purging expired ones first."""
        self._purge_expired()
        return self._sessions.get(token)

    def touch(self, token: str) -> bool:
        """Slide the expiry forward by one TTL window."""
        session = self._sessions.get(token)
        if session is None:
            return False
        session.expires_at = time.time() + self.ttl
        return True

    def destroy(self, token: str) -> None:
        self._sessions.pop(token, None)

    def active_count(self) -> int:
        self._purge_expired()
        return len(self._sessions)

    def user_sessions(self, user_id: int) -> list[Session]:
        return [s for s in self._sessions.values() if s.user_id == user_id]
