"""Per-client sliding-window rate limiter for the public API gateway."""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("ratelimit")

WINDOW_SECONDS = 60
DEFAULT_LIMIT = 100


@dataclass
class Decision:
    allowed: bool
    remaining: int
    retry_after: Optional[float]


class RateLimiter:
    def __init__(self, limit: int = DEFAULT_LIMIT, window: int = WINDOW_SECONDS):
        self.limit = limit
        self.window = window
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, headers: dict[str, str]) -> str:
        """Identify the client. Honors the proxy's forwarded-for chain."""
        forwarded = headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return headers.get("Remote-Addr", "unknown")

    def check(self, headers: dict[str, str]) -> Decision:
        key = self._client_key(headers)
        now = time.time()
        cutoff = now - self.window
        hits = self._hits[key]
        # Prune timestamps older than the window.
        while hits and hits[0] < cutoff:
            hits.pop(0)
        if len(hits) <= self.limit:
            hits.append(now)
            return Decision(True, self.limit - len(hits), None)
        retry_after = hits[0] + self.window - now
        logger.warning("rate limit hit for %s", key)
        return Decision(False, 0, retry_after)

    def reset(self, headers: dict[str, str]) -> None:
        self._hits.pop(self._client_key(headers), None)

    def current_usage(self, headers: dict[str, str]) -> int:
        key = self._client_key(headers)
        now = time.time()
        cutoff = now - self.window
        return sum(1 for t in self._hits[key] if t >= cutoff)

    def sweep(self) -> int:
        """Drop empty buckets to bound memory; returns buckets removed."""
        now = time.time()
        cutoff = now - self.window
        empty = []
        for key, hits in self._hits.items():
            if not any(t >= cutoff for t in hits):
                empty.append(key)
        for key in empty:
            del self._hits[key]
        return len(empty)
