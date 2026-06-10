"""Date/time helpers used across services (timezone-aware, pure functions)."""

from datetime import date, datetime, timedelta, timezone

ISO_DATE_FMT = "%Y-%m-%d"


def utc_now() -> datetime:
    """Timezone-aware current time in UTC."""
    return datetime.now(timezone.utc)


def parse_iso_date(value: str) -> date:
    """Parse YYYY-MM-DD strictly; raises ValueError on malformed input."""
    return datetime.strptime(value, ISO_DATE_FMT).date()


def start_of_day(d: date) -> datetime:
    """Midnight UTC at the start of the given date."""
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def end_of_day_exclusive(d: date) -> datetime:
    """Midnight UTC at the start of the NEXT day (half-open interval end).

    Using a half-open [start, end) interval avoids the classic
    boundary-day ambiguity when filtering timestamp columns.
    """
    return start_of_day(d) + timedelta(days=1)


def day_range(start: date, end: date) -> list[date]:
    """All dates from start to end inclusive; empty if end precedes start."""
    if end < start:
        return []
    span = (end - start).days
    return [start + timedelta(days=offset) for offset in range(span + 1)]


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def business_days_between(start: date, end: date) -> int:
    """Count weekdays in [start, end] inclusive, order-insensitive."""
    if end < start:
        start, end = end, start
    return sum(1 for d in day_range(start, end) if not is_weekend(d))


def humanize_delta(moment: datetime, reference: datetime | None = None) -> str:
    """Coarse human description of how long ago `moment` was."""
    ref = reference if reference is not None else utc_now()
    if moment.tzinfo is None or ref.tzinfo is None:
        raise ValueError("both datetimes must be timezone-aware")
    seconds = int((ref - moment).total_seconds())
    if seconds < 0:
        return "in the future"
    if seconds < 60:
        return "just now"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min ago"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours} h ago"
    days, hours = divmod(hours, 24)
    if days < 7:
        return f"{days} d ago"
    weeks, days = divmod(days, 7)
    return f"{weeks} w ago"


def clamp_to_range(value: datetime, lower: datetime, upper: datetime) -> datetime:
    """Clamp a datetime into [lower, upper]; raises if bounds are inverted."""
    if upper < lower:
        raise ValueError("upper bound precedes lower bound")
    return max(lower, min(value, upper))
