#!/usr/bin/env python3
"""Grade every run in a benchmark iteration. Deterministic, parallel, zero LLM tokens.

Writes <run-dir>/grading.json for each sandbox, which is what
skill-creator's aggregate_benchmark.py then reads.

    python3 grade_all.py --workspace <ws>/iteration-1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent


def one(run_dir_str: str):
    run_dir = Path(run_dir_str)
    case_id = int(run_dir.parents[1].name.split("-")[1])
    out = run_dir / "grading.json"
    proc = subprocess.run(
        [sys.executable, str(EVALS_DIR / "grade_run.py"),
         "--sandbox", str(run_dir / "sandbox"),
         "--case", str(case_id),
         "--out", str(out)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return {"run": run_dir_str, "error": (proc.stderr or proc.stdout)[-400:]}
    g = json.loads(out.read_text())
    return {
        "run": f"eval-{case_id}/{run_dir.parents[0].name}/{run_dir.name}",
        "case": case_id,
        "arm": run_dir.parents[0].name,
        "pass_rate": g["summary"]["pass_rate"],
        "passed": g["summary"]["passed"],
        "total": g["summary"]["total"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    run_dirs = sorted(
        str(p.parent) for p in args.workspace.glob("runs/eval-*/*/run-*/sandbox")
    )
    if not run_dirs:
        raise SystemExit(f"grade_all: no runs found under {args.workspace}")

    results, errors = [], []
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for f in as_completed([ex.submit(one, d) for d in run_dirs]):
            r = f.result()
            (errors if "error" in r else results).append(r)

    results.sort(key=lambda r: (r["case"], r["arm"], r["run"]))
    print(f"{'run':<34} {'passed':>8} {'rate':>6}")
    print("-" * 52)
    for r in results:
        print(f"{r['run']:<34} {r['passed']:>3}/{r['total']:<4} {r['pass_rate']:>6.2f}")

    for arm in ("with_skill", "without_skill"):
        rows = [r for r in results if r["arm"] == arm]
        if rows:
            mean = sum(r["pass_rate"] for r in rows) / len(rows)
            print(f"\n{arm:<15} mean pass_rate = {mean:.3f}  (n={len(rows)})")

    if errors:
        print(f"\n{len(errors)} GRADER ERROR(S):")
        for e in errors:
            print(f"  {e['run']}\n    {e['error']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
