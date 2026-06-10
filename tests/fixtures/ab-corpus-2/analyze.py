#!/usr/bin/env python3
"""Score the tier-diverse mini-experiment (task 078). Frozen BEFORE any run.

Arms: A (single opus), Dsame (3 opus critics), Dtier (sonnet/opus/fable critics).
Match = file + |Δline| <= 3 + class. Rules T1/T2/T3 mechanical.
"""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
GT = json.loads((ROOT / "ground_truth.json").read_text())
BUGS = GT["bugs"]
CONTROLS = set(GT["controls"])
FILES = sorted({b["file"] for b in BUGS}) + sorted(CONTROLS)
RUNS = [1, 2, 3]
LINE_TOL = 3
CRITICS = ("logic", "security", "performance")


def match_bug(f, fname):
    for b in BUGS:
        if b["file"] != fname:
            continue
        try:
            if abs(int(f.get("line", -999)) - b["line"]) <= LINE_TOL and f.get("class") == b["class"]:
                return b["id"]
        except (TypeError, ValueError):
            pass
    return None


def load_single(arm, fname, run):
    p = RESULTS / arm / f"{fname}__r{run}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("findings", [])
    except json.JSONDecodeError:
        return None


def load_committee(arm, fname, run):
    """Return (merged_findings, raw_per_critic) or (None, None) if absent."""
    raw = {}
    for c in CRITICS:
        p = RESULTS / arm / f"{fname}__r{run}" / f"{c}.json"
        if p.exists():
            try:
                raw[c] = json.loads(p.read_text()).get("findings", [])
            except json.JSONDecodeError:
                raw[c] = []
    if not raw:
        return None, None
    merged = []
    for c in CRITICS:
        for f in raw.get(c, []):
            dup = next((m for m in merged if m.get("class") == f.get("class")
                        and abs(int(m.get("line", -9)) - int(f.get("line", -99))) <= LINE_TOL), None)
            if dup is None:
                merged.append(dict(f))
    return merged, raw


def overlap_precision(raw):
    """Fraction of 2+critic same-location overlaps that land on a real bug."""
    flat = [(c, f) for c in CRITICS for f in raw.get(c, [])]
    events = correct = 0
    used = set()
    for i, (ci, fi) in enumerate(flat):
        for j, (cj, fj) in enumerate(flat):
            if j <= i or ci == cj or (i, j) in used:
                continue
            try:
                same = abs(int(fi.get("line", -9)) - int(fj.get("line", -99))) <= LINE_TOL
            except (TypeError, ValueError):
                same = False
            if same:
                used.add((i, j))
                events += 1
                # "correct" if either finding matches a seeded bug in any file
    return events  # raw count; precision computed per-file in score


def score(arm, committee):
    per_run, overlaps_total, overlaps_correct = [], 0, 0
    for run in RUNS:
        matched, fp_seed, fp_ctrl, total, bikeshed = set(), 0, 0, 0, 0
        for fname in FILES:
            if committee:
                findings, raw = load_committee(arm, fname, run)
            else:
                findings, raw = load_single(arm, fname, run), None
            if findings is None:
                continue
            for f in findings:
                total += 1
                if f.get("bikeshedding"):
                    bikeshed += 1
                    continue
                bug = match_bug(f, fname)
                if bug:
                    matched.add(bug)
                elif fname in CONTROLS:
                    fp_ctrl += 1
                else:
                    fp_seed += 1
            if committee and raw:
                flat = [f for c in CRITICS for f in raw.get(c, [])]
                seen_pairs = set()
                for i in range(len(flat)):
                    for j in range(i + 1, len(flat)):
                        try:
                            if abs(int(flat[i].get("line", -9)) - int(flat[j].get("line", -99))) <= LINE_TOL \
                               and flat[i].get("class") == flat[j].get("class"):
                                key = (min(i, j), max(i, j))
                                if key in seen_pairs:
                                    continue
                                seen_pairs.add(key)
                                overlaps_total += 1
                                if match_bug(flat[i], fname):
                                    overlaps_correct += 1
                        except (TypeError, ValueError):
                            pass
        per_run.append({"run": run, "recall": len(matched) / len(BUGS), "matched": sorted(matched),
                        "fp_per_file": (fp_seed + fp_ctrl) / len(FILES), "fp_control": fp_ctrl,
                        "findings": total, "bikeshed_ratio": bikeshed / total if total else 0.0})
    recalls = [r["recall"] for r in per_run]
    pooled = set().union(*(set(r["matched"]) for r in per_run)) if per_run else set()
    return {"arm": arm, "per_run": per_run,
            "recall_mean": statistics.mean(recalls) if recalls else 0.0,
            "recall_var": statistics.pvariance(recalls) if len(recalls) > 1 else 0.0,
            "pooled_recall": len(pooled) / len(BUGS),
            "fp_per_file_mean": statistics.mean(r["fp_per_file"] for r in per_run) if per_run else 0.0,
            "fp_control_total": sum(r["fp_control"] for r in per_run),
            "bikeshed_ratio_mean": statistics.mean(r["bikeshed_ratio"] for r in per_run) if per_run else 0.0,
            "pooled_by_class": {c: sum(1 for b in pooled if next(x for x in BUGS if x["id"] == b)["class"] == c) for c in CRITICS},
            "overlap_events": overlaps_total, "overlap_correct": overlaps_correct,
            "overlap_precision": (overlaps_correct / overlaps_total) if overlaps_total else None}


def main():
    A = score("A", False)
    Dsame = score("Dsame", True)
    Dtier = score("Dtier", True)

    var_t1 = (Dtier["recall_var"] + max(A["recall_var"], 1e-9)) / 2
    T1 = {"recall_Dtier": Dtier["recall_mean"], "recall_A": A["recall_mean"],
          "delta": Dtier["recall_mean"] - A["recall_mean"], "bar": 0.10,
          "fp_ok": Dtier["fp_per_file_mean"] <= A["fp_per_file_mean"],
          "tier_diversity_earns_committee": (Dtier["recall_mean"] - A["recall_mean"] >= 0.10)
                                            and Dtier["fp_per_file_mean"] <= A["fp_per_file_mean"]}
    var_t2 = (Dtier["recall_var"] + Dsame["recall_var"]) / 2
    T2 = {"recall_Dtier": Dtier["recall_mean"], "recall_Dsame": Dsame["recall_mean"],
          "delta": Dtier["recall_mean"] - Dsame["recall_mean"], "pooled_var": var_t2,
          "heterogeneity_adds": (Dtier["recall_mean"] - Dsame["recall_mean"]) > var_t2}
    T3 = {"Dsame_overlap_precision": Dsame["overlap_precision"], "Dtier_overlap_precision": Dtier["overlap_precision"],
          "Dsame_overlaps": Dsame["overlap_events"], "Dtier_overlaps": Dtier["overlap_events"],
          "tier_agreement_more_truthful": (Dtier["overlap_precision"] or 0) > (Dsame["overlap_precision"] or 0)}

    out = {"arms": {"A": A, "Dsame": Dsame, "Dtier": Dtier},
           "rules": {"T1_committee_vs_single": T1, "T2_hetero_vs_same": T2, "T3_overlap_quality": T3}}
    (ROOT / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'arm':<7}{'recall μ':>9}{'var':>8}{'pooled':>8}{'FP/file':>9}{'FPctrl':>7}{'bike%':>7}{'ovl_prec':>9}")
    for k, a in (("A", A), ("Dsame", Dsame), ("Dtier", Dtier)):
        op = f"{a['overlap_precision']:.2f}" if a["overlap_precision"] is not None else "—"
        print(f"{k:<7}{a['recall_mean']:>9.3f}{a['recall_var']:>8.4f}{a['pooled_recall']:>8.3f}"
              f"{a['fp_per_file_mean']:>9.2f}{a['fp_control_total']:>7}{a['bikeshed_ratio_mean']*100:>6.1f}%{op:>9}")
    print()
    print("T1 committee-vs-single:", "EARNS (+10pp)" if T1["tier_diversity_earns_committee"] else "FAILS bar", f"Δ={T1['delta']:+.3f} fp_ok={T1['fp_ok']}")
    print("T2 hetero-vs-same:     ", "ADDS" if T2["heterogeneity_adds"] else "no measurable gain", f"Δ={T2['delta']:+.3f} var={T2['pooled_var']:.4f}")
    print("T3 overlap quality:    ", "tier-agreement more truthful" if T3["tier_agreement_more_truthful"] else "not better",
          f"Dsame={T3['Dsame_overlap_precision']} Dtier={T3['Dtier_overlap_precision']}")


if __name__ == "__main__":
    main()
