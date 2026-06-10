"""Numeric aggregation helpers for dashboards (pure functions, clean control)."""

from bisect import insort
from typing import Iterable, Optional


def safe_mean(values: Iterable[float]) -> Optional[float]:
    """Arithmetic mean, or None for an empty input."""
    items = list(values)
    if not items:
        return None
    return sum(items) / len(items)


def running_total(values: Iterable[float]) -> list[float]:
    """Cumulative sums; the i-th element is the sum of the first i+1 inputs."""
    out: list[float] = []
    acc = 0.0
    for value in values:
        acc += value
        out.append(acc)
    return out


def percentile(values: Iterable[float], pct: float) -> Optional[float]:
    """Linear-interpolation percentile for pct in [0, 100]."""
    if not 0 <= pct <= 100:
        raise ValueError("pct must be within [0, 100]")
    ordered = sorted(values)
    if not ordered:
        return None
    if len(ordered) == 1:
        return ordered[0]
    rank = (pct / 100) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] * (1 - frac) + ordered[high] * frac


def moving_average(values: list[float], window: int) -> list[float]:
    """Trailing moving average; result length = max(0, len-window+1)."""
    if window <= 0:
        raise ValueError("window must be positive")
    if len(values) < window:
        return []
    out = []
    current = sum(values[:window])
    out.append(current / window)
    for i in range(window, len(values)):
        current += values[i] - values[i - window]
        out.append(current / window)
    return out


def clamp(value: float, low: float, high: float) -> float:
    """Constrain value to [low, high]; raises if the bounds are inverted."""
    if high < low:
        raise ValueError("high must be >= low")
    return max(low, min(value, high))


class StreamingMedian:
    """Exact running median via a sorted list (insort keeps it ordered)."""

    def __init__(self) -> None:
        self._data: list[float] = []

    def add(self, value: float) -> None:
        insort(self._data, value)

    def median(self) -> Optional[float]:
        n = len(self._data)
        if n == 0:
            return None
        mid = n // 2
        if n % 2 == 1:
            return self._data[mid]
        return (self._data[mid - 1] + self._data[mid]) / 2

    def count(self) -> int:
        return len(self._data)
