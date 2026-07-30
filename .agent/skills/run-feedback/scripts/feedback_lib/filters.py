"""Shared noise policy + redaction for all capture surfaces.

One module on purpose: the PostToolUse hook and the transcript miner MUST
agree on what counts as signal, otherwise the same failure is kept by one
surface and dropped by the other and cross-source dedup never gets a
chance to collapse them.

Policy summary (VDD-tuned):
  * exit 0                          -> drop
  * read-only/query command classes -> drop (grep exit 1 = "no match")
  * test runners                    -> drop (RED phases belong to the
                                       workflow retro step, not auto-capture)
  * user-aborted / interrupted      -> drop
  * exit 1 from anything else       -> KEEP only with a JSON error envelope
                                       or non-empty stderr (python/node/git
                                       legitimately fail with 1)
  * exit >= 2                       -> keep
"""

from __future__ import annotations

import re
import shlex

IGNORE_COMMANDS = frozenset({
    "grep", "rg", "fd", "find", "diff", "cmp", "test", "[", "[[",
    "ls", "which", "type", "stat", "tree", "wc", "head", "tail", "cat",
    "file", "du", "df", "readlink",
})

GIT_READONLY_PREFIXES = (
    "git diff", "git grep", "git log", "git status", "git show",
    "git check-ignore", "git ls-files", "git rev-parse",
)

_TEST_RUNNER_RE = re.compile(
    r"(?:\bpytest\b|\bunittest\b|\bnpm test\b|\bnpx jest\b|\bjest\b"
    r"|\bvitest\b|\bmocha\b|\bcargo test\b|\bgo test\b|test_e2e\.sh)")


def first_token(command):
    try:
        tokens = shlex.split(command or "", posix=True)
    except ValueError:
        tokens = (command or "").split()
    if not tokens:
        return ""
    # skip common env-var assignments and leading wrappers
    for tok in tokens:
        if "=" in tok and not tok.startswith(("=", "/", ".")):
            continue
        return tok.rsplit("/", 1)[-1]
    return ""


def is_test_runner(command):
    return bool(_TEST_RUNNER_RE.search(command or ""))


def should_capture(command, exit_code, stderr_text="", has_envelope=False,
                   interrupted=False):
    """Decide whether a failed Bash command is worth queueing as a finding."""
    if interrupted:
        return False
    if has_envelope:
        # a producer-emitted {"v":1,...} envelope IS a failure signal even
        # when no exit code could be parsed from the surrounding output
        return True
    if exit_code in (None, 0):
        return False
    stripped = (command or "").strip()
    if first_token(stripped) in IGNORE_COMMANDS:
        return False
    if stripped.startswith(GIT_READONLY_PREFIXES):
        return False
    if is_test_runner(stripped):
        return False
    if exit_code == 1:
        return bool((stderr_text or "").strip())
    return True


# --- shared extraction helpers (hook + miner must agree) --------------------

import json as _json

_COMPONENT_RE = re.compile(r"(?:^|[\s/'\"])(?:\.agent/)?skills/([\w\-]+)/")


def component_of(command, fallback="session"):
    """Infer the component from a skills/<name>/ path in the command."""
    match = _COMPONENT_RE.search(command or "")
    if match:
        return match.group(1)
    return (fallback or "session").lower()


def find_envelope(text):
    """Sniff a `{"v": 1, "error": ...}` JSON envelope from output tail."""
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    for line in reversed(lines[-5:]):
        if line.startswith("{") and '"v"' in line:
            try:
                obj = _json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and obj.get("v") == 1 and "error" in obj:
                return obj
    return None


# --- redaction -------------------------------------------------------------

_REDACT_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{8,}"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{8,}"),
    # bounded repetition: the unbounded form backtracks O(n^2) over a long run with
    # no `@`, and this runs on tool output inside a SYNCHRONOUS hook — one minified
    # JSON or base64 line was seconds of stall (iteration 3, M-04 / perf-High)
    re.compile(r"[\w.+\-]{1,64}@[\w\-]{1,255}\.[\w.\-]{1,255}"),
]
_KV_SECRET_RE = re.compile(
    r"(?i)\b(token|secret|passw\w*|api[_-]?key|apikey|cookie|authorization)"
    r"(\s*[=:]\s*)(\S+)")


def redact(text):
    if not text:
        return text
    for pattern in _REDACT_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    text = _KV_SECRET_RE.sub(lambda m: m.group(1) + m.group(2) + "[REDACTED]",
                             text)
    return text


#: how much more than the final limit to keep before redacting — enough that a
#: redaction never has to look at the whole input, generous enough that no secret
#: near the tail boundary is missed
_PRE_SLICE_FACTOR = 4


def clip(text, limit):
    """Hard-cap an excerpt, then redact; the tail is what matters for errors.

    The order used to be redact-then-slice, so ``excerpt_max_chars`` bounded the
    OUTPUT but not the WORK: a 100 MB excerpt file cost seven regex passes over
    100 MB to produce 2 000 characters, and the same code runs on tool output
    inside a synchronous hook (iteration 3, M-04 / perf-High). Slicing first with
    a generous margin keeps the cost proportional to the limit.
    """
    text = text or ""
    if limit and len(text) > limit * _PRE_SLICE_FACTOR:
        text = text[-(limit * _PRE_SLICE_FACTOR):]
    text = redact(text)
    if limit and len(text) > limit:
        # `text[-(limit - 1):]` is `text[-0:]` — the WHOLE string — when limit is 1,
        # so a cap of 1 silently disabled itself (iteration 3, sec-L-02)
        return "…" + (text[-(limit - 1):] if limit > 1 else "")
    return text
