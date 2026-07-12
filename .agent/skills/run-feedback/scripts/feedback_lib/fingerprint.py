"""Dedup fingerprints for findings.

The preimage deliberately EXCLUDES the capture source: the same Bash
failure caught live by a hook and mined later from the session transcript
must collapse to one finding (source provenance is kept as a merged
``sources`` list on the finding instead).

Normalization makes the fingerprint stable across reruns of the same
failure: volatile fragments (timestamps, paths, hex ids, numbers) are
replaced with placeholders before hashing.
"""

from __future__ import annotations

import hashlib
import re

_TS_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?")
_PATH_RE = re.compile(r"(?:~|\.{1,2})?/(?:[\w.+@%\-]+/)*[\w.+@%\-]+/?")
_HEX_RE = re.compile(r"\b[0-9a-fA-F]{8,}\b")
_NUM_RE = re.compile(r"\d+")
_WS_RE = re.compile(r"\s+")


def normalize_message(text):
    """Scrub volatile fragments; order matters (ts -> path -> hex -> num)."""
    text = text or ""
    text = _TS_RE.sub("<ts>", text)
    text = _PATH_RE.sub("<path>", text)
    text = _HEX_RE.sub("<hex>", text)
    text = _NUM_RE.sub("<n>", text)
    text = _WS_RE.sub(" ", text).strip().lower()
    return text


def failure_kind(error_type=None, exit_code=None):
    """The middle preimage component: envelope type wins over exit code."""
    if error_type:
        return str(error_type)
    if exit_code is not None:
        return "exit:%s" % exit_code
    return "unknown"


def compute(component, error_type=None, exit_code=None, message=""):
    """Return the 16-hex-char fingerprint for a failure signature."""
    preimage = "\x00".join([
        (component or "").strip().lower(),
        failure_kind(error_type, exit_code),
        normalize_message(message),
    ])
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()[:16]
