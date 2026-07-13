#!/usr/bin/env python3
"""
Aggregate individual run results into benchmark summary statistics.

Reads grading.json files from run directories and produces:
- run_summary with mean, stddev, min, max for each metric
- delta between with_skill and without_skill configurations

Usage:
    python aggregate_benchmark.py <benchmark_dir>

Example:
    python aggregate_benchmark.py benchmarks/2026-01-15T10-30-00/

The script supports two directory layouts:

    Workspace layout (from skill-creator iterations):
    <benchmark_dir>/
    └── eval-N/
        ├── with_skill/
        │   ├── run-1/grading.json
        │   └── run-2/grading.json
        └── without_skill/
            ├── run-1/grading.json
            └── run-2/grading.json

    Legacy layout (with runs/ subdirectory):
    <benchmark_dir>/
    └── runs/
        └── eval-N/
            ├── with_skill/
            │   └── run-1/grading.json
            └── without_skill/
                └── run-1/grading.json
"""

import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# Recognized arm names so the delta is "treatment − baseline" (improvement is positive)
# regardless of how config dirs happen to sort alphabetically. Unrecognized names keep
# their incoming order, so this never silently re-signs an unknown pair.
_TREATMENT_CONFIGS = {"with_skill", "new_skill", "candidate", "enriched", "after"}
_BASELINE_CONFIGS = {"without_skill", "old_skill", "baseline", "control", "before"}


def order_configs(configs: list[str]) -> list[str]:
    """Stable-reorder configs so a recognized treatment arm comes first and a recognized
    baseline arm comes second; everything else keeps its incoming order. This fixes the
    sign of the pass_rate delta for the documented workflows (e.g. old_skill/with_skill),
    where plain alphabetical order would otherwise compute baseline − treatment."""
    def rank(name: str) -> int:
        if name in _TREATMENT_CONFIGS:
            return 0  # treatment first
        if name in _BASELINE_CONFIGS:
            return 1  # baseline second (must outrank unknown configs)
        return 2      # unknown configs last
    return sorted(configs, key=rank)


def _percentile(sorted_vals: list[float], q: float) -> float:
    """Linear-interpolation percentile (numpy-style) on an already-sorted list.
    q in [0, 1]. Symmetric and not biased by int() truncation."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = max(0.0, min(1.0, q)) * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def bootstrap_delta_ci(
    results: dict,
    config_a: str,
    config_b: str,
    metric: str = "pass_rate",
    n: int = 5000,
    seed: int = 0,
    level: float = 0.95,
) -> dict | None:
    """Bootstrap confidence interval on (mean(config_a) − mean(config_b)) for a per-run
    metric — the multi-rep + interval pattern (advanced-eval-patterns.md §8).

    Use when a metric jitters run-to-run and a single before/after draw can't resolve the
    effect: collect N runs per arm, then resample to estimate the CI of the delta. Pure
    stdlib and SEEDED, so the result is deterministic (and therefore pinnable). Returns
    None if either arm has no runs.
    """
    def _vals(config):
        # An explicit `None` metric (e.g. a grader that failed to compute) is coerced to
        # 0.0, matching load_run_results' default — `.get(metric, 0.0)` alone would let a
        # present-but-None value through and crash the sum.
        out = []
        for r in results.get(config, []):
            v = r.get(metric)
            out.append(float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0)
        return out

    a, b = _vals(config_a), _vals(config_b)
    if not a or not b:
        return None
    rng = random.Random(seed)
    deltas = []
    for _ in range(n):
        mean_a = sum(rng.choice(a) for _ in a) / len(a)
        mean_b = sum(rng.choice(b) for _ in b) / len(b)
        deltas.append(mean_a - mean_b)
    deltas.sort()
    return {
        "metric": metric,
        "config_a": config_a,
        "config_b": config_b,
        "delta_mean": round(sum(deltas) / n, 4),
        "ci_low": round(_percentile(deltas, (1 - level) / 2), 4),
        "ci_high": round(_percentile(deltas, (1 + level) / 2), 4),
        "level": level,
        "n_resamples": n,
        "seed": seed,
        "runs_a": len(a),
        "runs_b": len(b),
    }


def calculate_stats(values: list[float]) -> dict:
    """Calculate mean, stddev, min, max for a list of values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4)
    }


def load_run_results(benchmark_dir: Path) -> dict:
    """
    Load all run results from a benchmark directory.

    Returns dict keyed by config name (e.g. "with_skill"/"without_skill",
    or "new_skill"/"old_skill"), each containing a list of run results.
    """
    # Support both layouts: eval dirs directly under benchmark_dir, or under runs/
    runs_dir = benchmark_dir / "runs"
    if runs_dir.exists():
        search_dir = runs_dir
    elif list(benchmark_dir.glob("eval-*")):
        search_dir = benchmark_dir
    else:
        print(f"No eval directories found in {benchmark_dir} or {benchmark_dir / 'runs'}")
        return {}

    results: dict[str, list] = {}

    for eval_idx, eval_dir in enumerate(sorted(search_dir.glob("eval-*"))):
        metadata_path = eval_dir / "eval_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path) as mf:
                    eval_id = json.load(mf).get("eval_id", eval_idx)
            except (json.JSONDecodeError, OSError):
                eval_id = eval_idx
        else:
            try:
                eval_id = int(eval_dir.name.split("-")[1])
            except ValueError:
                eval_id = eval_idx

        # Discover config directories dynamically rather than hardcoding names
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            # Skip non-config directories (inputs, outputs, etc.)
            if not list(config_dir.glob("run-*")):
                continue
            config = config_dir.name
            if config not in results:
                results[config] = []

            for run_idx, run_dir in enumerate(sorted(config_dir.glob("run-*"))):
                # Mirror the eval_id guard: a stray dir like `run-final` must not crash
                # the whole aggregation (and therefore verify_pin). Fall back to position.
                parts = run_dir.name.split("-")
                try:
                    run_number = int(parts[1]) if len(parts) > 1 else run_idx
                except ValueError:
                    print(f"Warning: non-numeric run dir {run_dir.name}; using position {run_idx}")
                    run_number = run_idx
                grading_file = run_dir / "grading.json"

                if not grading_file.exists():
                    print(f"Warning: grading.json not found in {run_dir}")
                    continue

                try:
                    with open(grading_file) as f:
                        grading = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in {grading_file}: {e}")
                    continue

                # Extract metrics
                summary = grading.get("summary") or {}
                result = {
                    "eval_id": eval_id,
                    "run_number": run_number,
                    "pass_rate": summary.get("pass_rate", 0.0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "total": summary.get("total", 0),
                }

                # Extract timing — check grading.json first, then sibling timing.json
                timing = grading.get("timing") or {}
                result["time_seconds"] = timing.get("total_duration_seconds", 0.0)
                timing_file = run_dir / "timing.json"
                if result["time_seconds"] == 0.0 and timing_file.exists():
                    try:
                        with open(timing_file) as tf:
                            timing_data = json.load(tf) or {}
                        result["time_seconds"] = timing_data.get("total_duration_seconds", 0.0)
                        result["tokens"] = timing_data.get("total_tokens", 0)
                    except json.JSONDecodeError:
                        pass

                # Extract metrics if available
                metrics = grading.get("execution_metrics") or {}
                result["tool_calls"] = metrics.get("total_tool_calls", 0)
                if not result.get("tokens"):
                    result["tokens"] = metrics.get("output_chars", 0)
                result["errors"] = metrics.get("errors_encountered", 0)

                # Extract expectations — viewer requires fields: text, passed, evidence
                raw_expectations = grading.get("expectations") or []
                for exp in raw_expectations:
                    if "text" not in exp or "passed" not in exp:
                        print(f"Warning: expectation in {grading_file} missing required fields (text, passed, evidence): {exp}")
                result["expectations"] = raw_expectations

                # Extract notes from user_notes_summary
                notes_summary = grading.get("user_notes_summary") or {}
                notes = []
                notes.extend(notes_summary.get("uncertainties") or [])
                notes.extend(notes_summary.get("needs_review") or [])
                notes.extend(notes_summary.get("workarounds") or [])
                result["notes"] = notes

                results[config].append(result)

    return results


def aggregate_results(results: dict) -> dict:
    """
    Aggregate run results into summary statistics.

    Returns run_summary with stats for each configuration and delta.
    """
    run_summary = {}
    # Reorder so a recognized treatment arm is first → delta = treatment − baseline
    # (improvement positive). Unknown names keep their order, so this is a no-op for them.
    configs = order_configs(list(results.keys()))

    for config in configs:
        runs = results.get(config, [])

        if not runs:
            run_summary[config] = {
                "pass_rate": {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0},
                "time_seconds": {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0},
                "tokens": {"mean": 0, "stddev": 0, "min": 0, "max": 0}
            }
            continue

        pass_rates = [r["pass_rate"] for r in runs]
        times = [r["time_seconds"] for r in runs]
        tokens = [r.get("tokens", 0) for r in runs]

        run_summary[config] = {
            "pass_rate": calculate_stats(pass_rates),
            "time_seconds": calculate_stats(times),
            "tokens": calculate_stats(tokens)
        }

    # Calculate delta between the first two configs (if two exist)
    if len(configs) >= 2:
        primary = run_summary.get(configs[0], {})
        baseline = run_summary.get(configs[1], {})
    else:
        primary = run_summary.get(configs[0], {}) if configs else {}
        baseline = {}

    delta_pass_rate = primary.get("pass_rate", {}).get("mean", 0) - baseline.get("pass_rate", {}).get("mean", 0)
    delta_time = primary.get("time_seconds", {}).get("mean", 0) - baseline.get("time_seconds", {}).get("mean", 0)
    delta_tokens = primary.get("tokens", {}).get("mean", 0) - baseline.get("tokens", {}).get("mean", 0)

    run_summary["delta"] = {
        "pass_rate": f"{delta_pass_rate:+.2f}",
        "time_seconds": f"{delta_time:+.1f}",
        "tokens": f"{delta_tokens:+.0f}"
    }

    return run_summary


def generate_benchmark(
    benchmark_dir: Path,
    skill_name: str = "",
    skill_path: str = "",
    bootstrap: bool = False,
    bootstrap_n: int = 5000,
    bootstrap_seed: int = 0,
) -> dict:
    """
    Generate complete benchmark.json from run results.

    With bootstrap=False (the default) the output is a pure function of the committed
    grading.json files — which is what `verify_pin.py` relies on. Pass bootstrap=True to
    attach a seeded (deterministic) CI on the first-two-configs pass_rate delta.
    """
    results = load_run_results(benchmark_dir)
    run_summary = aggregate_results(results)

    if bootstrap:
        # run_summary is already treatment-first (aggregate_results applied order_configs),
        # so configs[0]/configs[1] match the sign of delta.pass_rate.
        configs = [k for k in run_summary if k != "delta"]
        if len(configs) > 2:
            print(f"Warning: {len(configs)} configs present; bootstrap CI compares only "
                  f"'{configs[0]}' vs '{configs[1]}' (the rest are ignored).", file=sys.stderr)
        if len(configs) >= 2:
            ci = bootstrap_delta_ci(
                results, configs[0], configs[1], "pass_rate", bootstrap_n, bootstrap_seed
            )
            if ci:
                run_summary.setdefault("delta", {})["pass_rate_ci"] = ci

    # Build runs array for benchmark.json
    runs = []
    for config in results:
        for result in results[config]:
            runs.append({
                "eval_id": result["eval_id"],
                "configuration": config,
                "run_number": result["run_number"],
                "result": {
                    "pass_rate": result["pass_rate"],
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "total": result["total"],
                    "time_seconds": result["time_seconds"],
                    "tokens": result.get("tokens", 0),
                    "tool_calls": result.get("tool_calls", 0),
                    "errors": result.get("errors", 0)
                },
                "expectations": result["expectations"],
                "notes": result["notes"]
            })

    # Determine eval IDs from results
    eval_ids = sorted(set(
        r["eval_id"]
        for config in results.values()
        for r in config
    ))

    benchmark = {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "skill_path": skill_path or "<path/to/skill>",
            "executor_model": "<model-name>",
            "analyzer_model": "<model-name>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": eval_ids,
            "runs_per_configuration": 3
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": []  # To be filled by analyzer
    }

    return benchmark


def generate_markdown(benchmark: dict) -> str:
    """Generate human-readable benchmark.md from benchmark data."""
    metadata = benchmark["metadata"]
    run_summary = benchmark["run_summary"]

    # Determine config names (excluding "delta")
    configs = [k for k in run_summary if k != "delta"]
    config_a = configs[0] if len(configs) >= 1 else "config_a"
    config_b = configs[1] if len(configs) >= 2 else "config_b"
    label_a = config_a.replace("_", " ").title()
    label_b = config_b.replace("_", " ").title()

    lines = [
        f"# Skill Benchmark: {metadata['skill_name']}",
        "",
        f"**Model**: {metadata['executor_model']}",
        f"**Date**: {metadata['timestamp']}",
        f"**Evals**: {', '.join(map(str, metadata['evals_run']))} ({metadata['runs_per_configuration']} runs each per configuration)",
        "",
        "## Summary",
        "",
        f"| Metric | {label_a} | {label_b} | Delta |",
        "|--------|------------|---------------|-------|",
    ]

    a_summary = run_summary.get(config_a, {})
    b_summary = run_summary.get(config_b, {})
    delta = run_summary.get("delta", {})

    # Format pass rate
    a_pr = a_summary.get("pass_rate", {})
    b_pr = b_summary.get("pass_rate", {})
    lines.append(f"| Pass Rate | {a_pr.get('mean', 0)*100:.0f}% ± {a_pr.get('stddev', 0)*100:.0f}% | {b_pr.get('mean', 0)*100:.0f}% ± {b_pr.get('stddev', 0)*100:.0f}% | {delta.get('pass_rate', '—')} |")

    # Format time
    a_time = a_summary.get("time_seconds", {})
    b_time = b_summary.get("time_seconds", {})
    lines.append(f"| Time | {a_time.get('mean', 0):.1f}s ± {a_time.get('stddev', 0):.1f}s | {b_time.get('mean', 0):.1f}s ± {b_time.get('stddev', 0):.1f}s | {delta.get('time_seconds', '—')}s |")

    # Format tokens
    a_tokens = a_summary.get("tokens", {})
    b_tokens = b_summary.get("tokens", {})
    lines.append(f"| Tokens | {a_tokens.get('mean', 0):.0f} ± {a_tokens.get('stddev', 0):.0f} | {b_tokens.get('mean', 0):.0f} ± {b_tokens.get('stddev', 0):.0f} | {delta.get('tokens', '—')} |")

    # Notes section
    if benchmark.get("notes"):
        lines.extend([
            "",
            "## Notes",
            ""
        ])
        for note in benchmark["notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate benchmark run results into summary statistics"
    )
    parser.add_argument(
        "benchmark_dir",
        type=Path,
        help="Path to the benchmark directory"
    )
    parser.add_argument(
        "--skill-name",
        default="",
        help="Name of the skill being benchmarked"
    )
    parser.add_argument(
        "--skill-path",
        default="",
        help="Path to the skill being benchmarked"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output path for benchmark.json (default: <benchmark_dir>/benchmark.json)"
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Attach a seeded bootstrap CI on the first-two-configs pass_rate delta "
             "(multi-rep + interval; use when the metric jitters across runs)."
    )
    parser.add_argument("--bootstrap-n", type=int, default=5000, help="Bootstrap resamples (default 5000)")
    parser.add_argument("--bootstrap-seed", type=int, default=0, help="Bootstrap seed (default 0; keeps it deterministic/pinnable)")

    args = parser.parse_args()

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}")
        sys.exit(1)

    # Generate benchmark
    benchmark = generate_benchmark(
        args.benchmark_dir, args.skill_name, args.skill_path,
        bootstrap=args.bootstrap, bootstrap_n=args.bootstrap_n, bootstrap_seed=args.bootstrap_seed,
    )

    # Determine output paths
    output_json = args.output or (args.benchmark_dir / "benchmark.json")
    output_md = output_json.with_suffix(".md")

    # Write benchmark.json
    with open(output_json, "w") as f:
        json.dump(benchmark, f, indent=2)
    print(f"Generated: {output_json}")

    # Write benchmark.md
    markdown = generate_markdown(benchmark)
    with open(output_md, "w") as f:
        f.write(markdown)
    print(f"Generated: {output_md}")

    # Print summary
    run_summary = benchmark["run_summary"]
    configs = [k for k in run_summary if k != "delta"]
    delta = run_summary.get("delta", {})

    print(f"\nSummary:")
    for config in configs:
        pr = run_summary[config]["pass_rate"]["mean"]
        label = config.replace("_", " ").title()
        print(f"  {label}: {pr*100:.1f}% pass rate")
    print(f"  Delta:         {delta.get('pass_rate', '—')}")
    ci = delta.get("pass_rate_ci")
    if ci:
        print(f"  95% CI (Δ pass_rate): [{ci['ci_low']:+.3f}, {ci['ci_high']:+.3f}] "
              f"(mean {ci['delta_mean']:+.3f}, {ci['runs_a']}v{ci['runs_b']} runs, n={ci['n_resamples']})")


if __name__ == "__main__":
    main()
