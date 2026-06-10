#!/usr/bin/env python3
"""Score A/B experiment runs against sealed ground truth (audit-067 Appendix A).

Frozen BEFORE any arm runs. Matching rule: same file, |line delta| <= 3,
class equal. Decision rules 1-3 evaluated mechanically; rule-1/3 variance
threshold = pooled per-run recall variance of the two compared arms.
"""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
GT = json.loads((ROOT / "ground_truth.json").read_text())
BUGS = GT["bugs"]
CONTROLS = set(GT["controls"])
SEEDED_FILES = sorted({b["file"] for b in BUGS})
ALL_FILES = SEEDED_FILES + sorted(CONTROLS)
ARMS_SINGLE = ["A", "B", "C", "E"]
RUNS = [1, 2, 3]
LINE_TOL = 3


def match_bug(finding: dict, fname: str):
    """Return bug id if the finding matches a seeded bug, else None."""
    for bug in BUGS:
        if bug["file"] != fname:
            continue
        try:
            delta = abs(int(finding.get("line", -999)) - bug["line"])
        except (TypeError, ValueError):
            continue
        if delta <= LINE_TOL and finding.get("class") == bug["class"]:
            return bug["id"]
    return None


def load_single(arm: str, fname: str, run: int) -> list[dict]:
    p = RESULTS / arm / f"{fname}__r{run}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("findings", [])
    except json.JSONDecodeError:
        return None


def load_d(fname: str, run: int) -> list[dict]:
    """Arm D: deterministic Phase-2 merge of the 3 critic reports.

    Rule 1 (dedup file/line±3/class, keep max severity), rule 4 (drop
    bikeshedding items from bikeshedding-only critics). Rule 3 corroborated
    tag irrelevant to scoring (no escalation); rule 2/5 N/A here.
    """
    merged: list[dict] = []
    found_any = False
    for critic in ("logic", "security", "performance"):
        p = RESULTS / "D" / f"{fname}__r{run}" / f"{critic}.json"
        if not p.exists():
            continue
        found_any = True
        data = json.loads(p.read_text())
        conv = data.get("convergence", "issues-found")
        for f in data.get("findings", []):
            if conv == "bikeshedding-only" and f.get("bikeshedding"):
                continue  # rule 4
            dup = next((m for m in merged
                        if m.get("class") == f.get("class")
                        and abs(int(m.get("line", -9)) - int(f.get("line", -99))) <= LINE_TOL), None)
            if dup is None:
                merged.append(dict(f))
    return merged if found_any else None


SEV_ORDER = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}


def score_arm(arm: str) -> dict:
    per_run = []
    missing = 0
    for run in RUNS:
        matched: set[str] = set()
        fp_seeded = fp_control = total_f = bikeshed = 0
        for fname in ALL_FILES:
            findings = load_d(fname, run) if arm == "D" else load_single(arm, fname, run)
            if findings is None:
                missing += 1
                continue
            for f in findings:
                total_f += 1
                if f.get("bikeshedding"):
                    bikeshed += 1
                bug = match_bug(f, fname)
                if bug:
                    matched.add(bug)
                elif not f.get("bikeshedding"):
                    if fname in CONTROLS:
                        fp_control += 1
                    else:
                        fp_seeded += 1
        per_run.append({
            "run": run, "matched": sorted(matched), "recall": len(matched) / len(BUGS),
            "fp_seeded": fp_seeded, "fp_control": fp_control,
            "fp_per_file": (fp_seeded + fp_control) / len(ALL_FILES),
            "findings": total_f, "bikeshed_ratio": (bikeshed / total_f) if total_f else 0.0,
        })
    recalls = [r["recall"] for r in per_run]
    pooled = set().union(*(set(r["matched"]) for r in per_run)) if per_run else set()
    by_class = {c: sum(1 for b in pooled if next(x for x in BUGS if x["id"] == b)["class"] == c)
                for c in ("logic", "security", "performance")}
    by_sev = {s: sum(1 for b in pooled if next(x for x in BUGS if x["id"] == b)["severity"] == s)
              for s in ("CRITICAL", "HIGH", "MEDIUM")}
    return {
        "arm": arm, "missing_result_files": missing, "per_run": per_run,
        "recall_mean": statistics.mean(recalls) if recalls else 0.0,
        "recall_var": statistics.pvariance(recalls) if len(recalls) > 1 else 0.0,
        "fp_per_file_mean": statistics.mean(r["fp_per_file"] for r in per_run) if per_run else 0.0,
        "fp_control_total": sum(r["fp_control"] for r in per_run),
        "bikeshed_ratio_mean": statistics.mean(r["bikeshed_ratio"] for r in per_run) if per_run else 0.0,
        "pooled_recall": len(pooled) / len(BUGS), "pooled_matched": sorted(pooled),
        "pooled_by_class": by_class, "pooled_by_severity": by_sev,
    }


def main() -> None:
    arms = {a: score_arm(a) for a in ARMS_SINGLE + ["D"]}
    A, B, C, D, E = (arms[k] for k in "ABCDE")

    pooled_var_bc = (B["recall_var"] + C["recall_var"]) / 2
    rule1 = {"delta_recall_C_minus_B": C["recall_mean"] - B["recall_mean"],
             "pooled_run_variance": pooled_var_bc,
             "fp_ok": C["fp_per_file_mean"] <= B["fp_per_file_mean"],
             "sarcasm_survives": (C["recall_mean"] - B["recall_mean"] > pooled_var_bc)
                                  and C["fp_per_file_mean"] <= B["fp_per_file_mean"]}
    best_single = max((A, E), key=lambda x: x["recall_mean"])
    rule2 = {"best_single_arm": best_single["arm"],
             "delta_recall_D_minus_best": D["recall_mean"] - best_single["recall_mean"],
             "fp_ok": D["fp_per_file_mean"] <= best_single["fp_per_file_mean"],
             "multi_survives": (D["recall_mean"] - best_single["recall_mean"] >= 0.10)
                                and D["fp_per_file_mean"] <= best_single["fp_per_file_mean"]}
    pooled_var_ab = (A["recall_var"] + B["recall_var"]) / 2
    rule3 = {"delta_recall_B_minus_A": B["recall_mean"] - A["recall_mean"],
             "pooled_run_variance": pooled_var_ab,
             "fp_ok": B["fp_per_file_mean"] <= A["fp_per_file_mean"],
             "forced_negativity_survives": (B["recall_mean"] - A["recall_mean"] > pooled_var_ab)
                                            and B["fp_per_file_mean"] <= A["fp_per_file_mean"]}

    out = {"arms": arms, "decision_rules": {"rule1_sarcasm": rule1,
                                            "rule2_multicritic": rule2,
                                            "rule3_forced_negativity": rule3}}
    (ROOT / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'arm':<4}{'recall μ':>9}{'var':>8}{'pooled':>8}{'FP/file':>9}{'FPctrl':>7}{'bike%':>7}{'miss':>6}")
    for k in "ABCDE":
        a = arms[k]
        print(f"{k:<4}{a['recall_mean']:>9.3f}{a['recall_var']:>8.4f}{a['pooled_recall']:>8.3f}"
              f"{a['fp_per_file_mean']:>9.2f}{a['fp_control_total']:>7}"
              f"{a['bikeshed_ratio_mean']*100:>6.1f}%{a['missing_result_files']:>6}")
    print("\nRule 1 (sarcasm):", "SURVIVES" if rule1["sarcasm_survives"] else "FAILS -> deprecate K2", rule1)
    print("Rule 2 (multi):  ", "SURVIVES" if rule2["multi_survives"] else "FAILS -> single strong reviewer", rule2)
    print("Rule 3 (neg.):   ", "SURVIVES" if rule3["forced_negativity_survives"] else "FAILS", rule3)


if __name__ == "__main__":
    main()
