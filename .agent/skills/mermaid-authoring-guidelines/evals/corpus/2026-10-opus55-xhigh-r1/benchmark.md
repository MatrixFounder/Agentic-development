# Skill Benchmark: mermaid-authoring-guidelines

**Model**: claude-opus-5-5
**Date**: 2026-10-03T14:08:40Z
**Evals**: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (3 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 95% ± 7% | 90% ± 10% | +0.05 |
| Time | 256.4s ± 258.0s | 45.0s ± 28.5s | +211.5s |
| Tokens | 64355 ± 49195 | 7070 ± 2523 | +57285 |

## Calibration scope

V2 calibrates the detector on the seven defect types of TASK D16 only: crossings_over_allowance, edge_through_node, title_crossing, label_overlap_or_clip, illegible_at_column, dark_contrast, form_unfit. Those are the geometry and form checks; the fidelity checks Q09-Q12, the caption and legend checks Q13-Q14, the concern check Q08, the budget Q07, the ASCII lint Q16 and the colour check Q17 are not calibrated by it.

## Grader provenance

the normalisation rule, grade_figures.py, fidelity.py: not registered before the runs of 2026-10-opus55-xhigh-r1. The sha256 is recorded at grading time; a change after the runs shows in it, and nothing refuses it (TASK R11.2; EI-13).
