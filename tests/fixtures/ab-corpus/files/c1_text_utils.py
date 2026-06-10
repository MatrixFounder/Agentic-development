"""Text normalization and formatting helpers (pure functions)."""

import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")
_SLUG_INVALID_RE = re.compile(r"[^a-z0-9-]")


def collapse_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single spaces and strip the ends."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def slugify(text: str, max_length: int = 80) -> str:
    """Lowercase ASCII slug: spaces become hyphens, invalid chars dropped."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = collapse_whitespace(ascii_text).lower().replace(" ", "-")
    slug = _SLUG_INVALID_RE.sub("", lowered)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_length].rstrip("-")


def truncate(text: str, limit: int, suffix: str = "…") -> str:
    """Truncate to `limit` characters, appending `suffix` if cut.

    The suffix counts toward the limit, so the result never exceeds it.
    """
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    if len(suffix) >= limit:
        return suffix[:limit]
    return text[: limit - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return '<count> <noun>' with a naive English plural fallback."""
    if plural is None:
        plural = singular + "s"
    noun = singular if abs(count) == 1 else plural
    return f"{count} {noun}"


def mask_middle(value: str, visible: int = 4, mask_char: str = "*") -> str:
    """Keep the first and last `visible` chars, mask the middle.

    Short values are fully masked to avoid leaking most of the content.
    """
    if visible < 0:
        raise ValueError("visible must be non-negative")
    if len(value) <= visible * 2:
        return mask_char * len(value)
    middle = mask_char * (len(value) - visible * 2)
    return value[:visible] + middle + value[-visible:]


def indent_block(text: str, spaces: int = 2) -> str:
    """Indent every non-empty line by the given number of spaces."""
    pad = " " * spaces
    lines = text.splitlines()
    return "\n".join(pad + line if line.strip() else line for line in lines)


def levenshtein(a: str, b: str) -> int:
    """Edit distance via the standard two-row dynamic program, O(len(a)*len(b))."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (char_a != char_b)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]
