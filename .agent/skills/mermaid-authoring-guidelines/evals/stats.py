#!/usr/bin/env python3
"""Statistics for the figure evals (TASK 108, R11.9; decision rule D8, revision 3).

The unit of generalisation is the case, not the run. The arms are paired by case:

  * a case's score is the MEDIAN over its repetitions (`case_score`); the mean is kept for
    information (`case_mean`);
  * the paired delta is the mean over cases of (case score `with_skill` minus case score
    `without_skill`), equal case weights (`paired_delta`);
  * a paired two-stage case-cluster bootstrap: resample cases with replacement, then, inside
    each arm of each drawn case, resample its runs with replacement; a case score in a
    resample is the median of its drawn runs; the statistic is the paired delta of the
    resample; percentile interval (`cluster_bootstrap`);
  * an exact sign test over the case deltas (information only): a case is ahead when its
    delta is above 0, as the README defines "ahead"; a noise floor gives a sensitivity reading;
  * Wilson intervals for pass rates; Cohen's kappa and per-class precision and recall for the
    detector calibration (TASK D8 V2).

Every mean is taken with `math.fsum`, because `sum` over floats differs between Python 3.11 and
3.12 in the last unit of precision, and a pinned report must re-derive on both. The bootstrap
is seeded and draws with `random.Random(seed).random()`, whose sequence is stable across
Python versions. Pure functions; standard library only.
"""

from __future__ import annotations

import math
import random
from typing import Optional

ARMS = ("with_skill", "without_skill")
B_DEFAULT = 10000
SEED_DEFAULT = 0
LEVEL_DEFAULT = 0.95
#: How a case's repetitions become its score (TASK D8 revision 3): the median.
CENTER_DEFAULT = "median"
#: z for a two-sided 95 % interval.
Z95 = 1.959963984540054


def fmean(values) -> Optional[float]:
    """Mean with `math.fsum`; None for no value. None items are skipped."""
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return None
    return math.fsum(vals) / len(vals)


def median(values) -> Optional[float]:
    """Median; None for no value. None items are skipped. An even count takes the mean of the
    two middle values."""
    vals = sorted(float(v) for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def center(values, how: str = CENTER_DEFAULT) -> Optional[float]:
    """`median` or `fmean` of *values*, by name."""
    if how == "median":
        return median(values)
    if how == "mean":
        return fmean(values)
    raise ValueError(f"unknown centre {how!r}: median or mean")


def percentile(sorted_vals: list, q: float) -> float:
    """Linear-interpolation percentile on a sorted list (`aggregate_benchmark._percentile`)."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = max(0.0, min(1.0, q)) * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def case_mean(runs: list, metric: str) -> Optional[float]:
    """Mean of *metric* over the runs of one arm of one case; None when no run has it.
    Information only: the decision rule scores a case by `case_score`."""
    return fmean(r.get(metric) for r in runs)


def case_score(runs: list, metric: str, how: str = CENTER_DEFAULT) -> Optional[float]:
    """The score of one arm of one case: the median of *metric* over its repetitions (TASK D8
    revision 3); None when no run has a value."""
    return center((r.get(metric) for r in runs), how)


def case_deltas(data: dict, metric: str, arms: tuple = ARMS,
                how: str = CENTER_DEFAULT) -> dict:
    """`{case: score(arm 0) - score(arm 1)}` over cases where both arms have a value."""
    out = {}
    for case in sorted(data, key=str):
        a = case_score(data[case].get(arms[0], []), metric, how)
        b = case_score(data[case].get(arms[1], []), metric, how)
        if a is not None and b is not None:
            out[case] = a - b
    return out


def paired_delta(data: dict, metric: str, arms: tuple = ARMS,
                 how: str = CENTER_DEFAULT) -> Optional[float]:
    """Mean over cases of the case delta, equal case weights; None with no paired case."""
    d = case_deltas(data, metric, arms, how)
    return fmean(d.values())


def _draw(rng: random.Random, n: int) -> int:
    return min(int(rng.random() * n), n - 1)


def cluster_bootstrap(data: dict, metrics: list, arms: tuple = ARMS, b: int = B_DEFAULT,
                      seed: int = SEED_DEFAULT, level: float = LEVEL_DEFAULT,
                      how: str = CENTER_DEFAULT) -> dict:
    """Paired two-stage case-cluster bootstrap of the delta of every metric in *metrics*.

    *data*: `{case: {arm: [ {metric: value or None} ]}}`. All metrics share the resampled
    cases and runs of one iteration. A case score in a resample is the *how* (median) of its
    drawn runs. In an iteration a drawn case enters a metric's delta only when both of its arms
    have a value for that metric among the drawn runs.

    Returns `{metric: {"delta", "ci_low", "ci_high", "cases", "b", "seed", "level",
    "case_score"}}`; the point estimate is the unresampled paired delta, the interval is the
    percentile interval.
    """
    cases = [c for c in sorted(data, key=str)
             if data[c].get(arms[0]) and data[c].get(arms[1])]
    out = {}
    for m in metrics:
        out[m] = {"delta": _round(paired_delta({c: data[c] for c in cases}, m, arms, how)),
                  "ci_low": None, "ci_high": None,
                  "cases": len(case_deltas({c: data[c] for c in cases}, m, arms, how)),
                  "b": b, "seed": seed, "level": level, "case_score": how}
    if not cases:
        return out
    rng = random.Random(seed)
    cache = {}

    def means(case, arm, idx):
        key = (case, arm, idx)
        if key not in cache:
            runs = data[case][arm]
            cache[key] = {m: center((runs[i].get(m) for i in idx), how) for m in metrics}
        return cache[key]

    samples = {m: [] for m in metrics}
    n = len(cases)
    for _ in range(b):
        drawn = [cases[_draw(rng, n)] for _ in range(n)]
        per_case = []
        for case in drawn:
            pair = []
            for arm in arms:
                k = len(data[case][arm])
                idx = tuple(sorted(_draw(rng, k) for _ in range(k)))
                pair.append(means(case, arm, idx))
            per_case.append(pair)
        for m in metrics:
            vals = [a[m] - w[m] for a, w in per_case if a[m] is not None and w[m] is not None]
            if vals:
                samples[m].append(math.fsum(vals) / len(vals))
    lo_q, hi_q = (1 - level) / 2, (1 + level) / 2
    for m in metrics:
        s = sorted(samples[m])
        if s:
            out[m]["ci_low"] = _round(percentile(s, lo_q))
            out[m]["ci_high"] = _round(percentile(s, hi_q))
    return out


def binom_tail_ge(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p), exact."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return math.fsum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def sign_test(deltas, floor: float = 0.0) -> dict:
    """Exact sign test over case deltas. A delta above *floor* is ahead, one below -*floor* is
    behind, and the rest are ties and leave. The default floor 0 is the README's "ahead": a case
    difference above 0 (R2-14).

    Returns counts and the one-sided (`with_skill` ahead) and two-sided p-values.
    """
    vals = [float(d) for d in deltas]
    pos = sum(1 for d in vals if d > floor)
    neg = sum(1 for d in vals if d < -floor)
    ties = len(vals) - pos - neg
    n = pos + neg
    one = binom_tail_ge(pos, n) if n else 1.0
    two = min(1.0, 2 * min(binom_tail_ge(pos, n), binom_tail_ge(neg, n))) if n else 1.0
    return {"floor": floor, "ahead": pos, "behind": neg, "ties": ties, "n": n,
            "p_one_sided": _round(one), "p_two_sided": _round(two)}


def wilson(k: int, n: int, z: float = Z95) -> tuple:
    """Wilson score interval for k successes of n; `(None, None)` for n = 0."""
    if n <= 0:
        return (None, None)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (_round(max(0.0, centre - half)), _round(min(1.0, centre + half)))


def confusion(pairs) -> dict:
    """Counts over `(truth, predicted)` booleans; positive means the defect is present."""
    tp = fp = fn = tn = 0
    for truth, pred in pairs:
        if truth and pred:
            tp += 1
        elif pred and not truth:
            fp += 1
        elif truth and not pred:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(pairs) -> dict:
    """Precision and recall of the predicted positives; None where the denominator is 0."""
    c = confusion(pairs)
    prec = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else None
    rec = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else None
    return dict(c, precision=_round(prec), recall=_round(rec))


def cohen_kappa(pairs) -> Optional[float]:
    """Cohen's kappa of two binary raters over `(a, b)` pairs; None for no pair."""
    c = confusion(pairs)
    n = c["tp"] + c["fp"] + c["fn"] + c["tn"]
    if n == 0:
        return None
    po = (c["tp"] + c["tn"]) / n
    pe = ((c["tp"] + c["fp"]) * (c["tp"] + c["fn"]) + (c["fn"] + c["tn"]) * (c["fp"] + c["tn"])) / (n * n)
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return _round((po - pe) / (1 - pe))


def sd(values) -> Optional[float]:
    """Sample standard deviation with `fsum`; None for fewer than two values."""
    vals = [float(v) for v in values if v is not None]
    if len(vals) < 2:
        return None
    m = math.fsum(vals) / len(vals)
    return _round(math.sqrt(math.fsum((v - m) ** 2 for v in vals) / (len(vals) - 1)))


def _round(v, nd: int = 6):
    return None if v is None else round(float(v), nd)
