#!/usr/bin/env python3
"""Build every (case × arm × rep) sandbox for a benchmark iteration, in parallel.

Layout matches what skill-creator's aggregate_benchmark.py expects:

    <workspace>/runs/eval-<id>/eval_metadata.json
    <workspace>/runs/eval-<id>/<arm>/run-<n>/sandbox/     <- the agent works here
    <workspace>/runs/eval-<id>/<arm>/run-<n>/grading.json <- grade_run.py writes here

Each rep gets its OWN sandbox: the runs mutate a ledger, so they cannot share one.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR))
from harness import build  # noqa: E402

ARMS = ("with_skill", "without_skill")


def one(args):
    case, arm, rep, workspace = args
    dest = Path(workspace) / "runs" / f"eval-{case['id']}" / arm / f"run-{rep}" / "sandbox"
    build(case, arm, dest)
    return f"eval-{case['id']}/{arm}/run-{rep}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--evals", type=Path, default=EVALS_DIR / "evals.json")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    suite = json.loads(args.evals.read_text())
    jobs = []
    for case in suite["evals"]:
        meta_dir = args.workspace / "runs" / f"eval-{case['id']}"
        meta_dir.mkdir(parents=True, exist_ok=True)
        (meta_dir / "eval_metadata.json").write_text(json.dumps({
            "eval_id": case["id"],
            "eval_name": case["name"],
            "construction": case.get("construction"),
            "prompt": case["prompt"],
            "expectations": case["expectations"],
            "forbidden_expectations": case.get("forbidden_expectations", []),
        }, indent=2))
        for arm in ARMS:
            for rep in range(1, args.reps + 1):
                jobs.append((case, arm, rep, str(args.workspace)))

    done = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        futures = [ex.submit(one, j) for j in jobs]
        for f in as_completed(futures):
            f.result()          # surface fixture-integrity failures loudly
            done += 1
    print(f"built {done} sandboxes under {args.workspace}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
