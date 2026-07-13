#!/usr/bin/env python3
"""Verify that a benchmark report is "pinned": re-aggregate the committed run results
and assert the deterministic metrics still match a committed benchmark.json.

This is skill-creator's generic version of the `grade(raw) == committed grading.json`
invariant (see references/advanced-eval-patterns.md §3). Because aggregation is a pure
function of the committed grading.json files, re-running it must reproduce the committed
benchmark byte-for-byte on the metrics that matter. If the aggregation math changes, or a
committed grading.json is edited, the pin breaks — catching silent metric drift in CI.

Volatile metadata (timestamp, model names, paths) and any optional bootstrap CI are
ignored; only the computed `runs` and `run_summary` are compared.

Usage:
    python verify_pin.py <benchmark_dir> <committed_benchmark.json>

Exit 0 = pin holds. Exit 1 = drift detected (the differing keys are printed).
No LLM, no network, no shell — pure recomputation.
"""

import argparse
import json
import sys
from pathlib import Path

# Support both `python scripts/verify_pin.py` and `python -m scripts.verify_pin`.
try:
    from scripts.aggregate_benchmark import generate_benchmark
except ImportError:
    from aggregate_benchmark import generate_benchmark

# delta sub-keys that aggregation always produces; anything else (e.g. a bootstrap CI
# added with --bootstrap) is optional and excluded from the pin comparison.
_CANONICAL_DELTA_KEYS = ("pass_rate", "time_seconds", "tokens")

# metadata fields that legitimately vary between a committed pin and a fresh re-aggregation
# (timestamp, the caller-supplied skill name/path, placeholder model names). Everything
# else — including deterministic metadata like `evals_run` — is compared (fail-closed:
# a new top-level field is pinned by default rather than silently ignored).
_VOLATILE_META = {"timestamp", "skill_name", "skill_path", "executor_model", "analyzer_model"}


def _comparable(benchmark: dict) -> dict:
    """Deep-copy and strip only known-volatile fields, so the comparison covers every
    deterministic field (fail-closed) except environment noise and the optional CI."""
    out = json.loads(json.dumps(benchmark))  # deep copy
    meta = out.get("metadata")
    if isinstance(meta, dict):
        for key in _VOLATILE_META:
            meta.pop(key, None)
    delta = out.get("run_summary", {}).get("delta") if isinstance(out.get("run_summary"), dict) else None
    if isinstance(delta, dict):
        for key in list(delta):
            if key not in _CANONICAL_DELTA_KEYS:
                delta.pop(key)
    return out


def _diffs(recomputed, committed, path="") -> list[str]:
    """Recursively list human-readable differences between two comparable structures."""
    out: list[str] = []
    # int/float are interchangeable (JSON 1 vs 1.0); but bool is NOT — `type() in` rejects
    # bool (a subclass of int), so a true/1 regression is still reported as a type mismatch.
    both_numeric = type(recomputed) in (int, float) and type(committed) in (int, float)
    if type(recomputed) is not type(committed) and not both_numeric:
        return [f"{path or '<root>'}: type {type(recomputed).__name__} != {type(committed).__name__}"]
    if isinstance(recomputed, dict):
        for key in sorted(set(recomputed) | set(committed)):
            if key not in recomputed:
                out.append(f"{path}.{key}: missing in recomputed (committed={committed[key]!r})")
            elif key not in committed:
                out.append(f"{path}.{key}: extra in recomputed (={recomputed[key]!r})")
            else:
                out.extend(_diffs(recomputed[key], committed[key], f"{path}.{key}"))
    elif isinstance(recomputed, list):
        if len(recomputed) != len(committed):
            out.append(f"{path}: length {len(recomputed)} != {len(committed)}")
        for i, (a, b) in enumerate(zip(recomputed, committed)):
            out.extend(_diffs(a, b, f"{path}[{i}]"))
    else:
        if recomputed != committed:
            out.append(f"{path or '<root>'}: {recomputed!r} != {committed!r} (recomputed != committed)")
    return out


def pin_holds(benchmark_dir: Path, committed_path: Path) -> tuple[bool, list[str]]:
    """Return (holds, diffs). `holds` is True iff re-aggregation reproduces the committed
    benchmark's deterministic metrics."""
    recomputed = generate_benchmark(benchmark_dir)
    committed = json.loads(Path(committed_path).read_text())
    diffs = _diffs(_comparable(recomputed), _comparable(committed))
    return (not diffs), diffs


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a benchmark.json pin (no drift).")
    parser.add_argument("benchmark_dir", type=Path, help="Dir with eval-*/<config>/run-*/grading.json")
    parser.add_argument("committed_benchmark", type=Path, help="Committed benchmark.json to compare against")
    args = parser.parse_args()

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}", file=sys.stderr)
        return 2
    if not args.committed_benchmark.exists():
        print(f"Committed benchmark not found: {args.committed_benchmark}", file=sys.stderr)
        return 2

    holds, diffs = pin_holds(args.benchmark_dir, args.committed_benchmark)
    if holds:
        print(f"✅ Pin holds: re-aggregation matches {args.committed_benchmark}")
        return 0
    print(f"❌ Pin BROKEN: re-aggregation differs from {args.committed_benchmark}", file=sys.stderr)
    for d in diffs[:40]:
        print(f"  {d}", file=sys.stderr)
    if len(diffs) > 40:
        print(f"  … and {len(diffs) - 40} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
