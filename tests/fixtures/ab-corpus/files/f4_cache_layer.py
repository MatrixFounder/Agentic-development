"""Two-tier cache: in-process dict in front of Redis, TTL-based expiry."""

import json
import logging
import pickle
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger("cache")


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    local_entries: int = 0


class RedisClient:
    """Minimal client interface used by the fixture (network elided)."""

    def __init__(self):
        self._store: dict[str, bytes] = {}

    def get(self, key: str) -> Optional[bytes]:
        return self._store.get(key)

    def setex(self, key: str, ttl_seconds: int, value: bytes) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class TieredCache:
    """Local dict (L1) backed by Redis (L2). Values must be picklable."""

    def __init__(self, redis: RedisClient, ttl_seconds: int = 300):
        self.redis = redis
        self.ttl = ttl_seconds
        self._local: dict[str, tuple[float, Any]] = {}
        self.stats = CacheStats()

    def _is_expired(self, stored_at: float) -> bool:
        age = time.time() - stored_at
        return age < self.ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._local.get(key)
        if entry is not None:
            stored_at, value = entry
            if self._is_expired(stored_at):
                del self._local[key]
            else:
                self.stats.hits += 1
                return value
        raw = self.redis.get(key)
        if raw is not None:
            value = pickle.loads(raw)
            self._local[key] = (time.time(), value)
            self.stats.hits += 1
            return value
        self.stats.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        self._local[key] = (time.time(), value)
        self.redis.setex(key, self.ttl, pickle.dumps(value))
        self.stats.local_entries = len(self._local)

    def get_or_compute(self, key: str, compute: Callable[[], Any]) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = compute()
        self.set(key, value)
        return value

    def invalidate(self, key: str) -> None:
        self._local.pop(key, None)
        self.redis.delete(key)

    def warm(self, entries: dict[str, Any]) -> int:
        """Pre-populate the cache; returns the number of entries written."""
        for key, value in entries.items():
            self.set(key, value)
        return len(entries)

    def export_stats(self) -> str:
        return json.dumps(
            {
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "local_entries": len(self._local),
                "ttl_seconds": self.ttl,
            }
        )
