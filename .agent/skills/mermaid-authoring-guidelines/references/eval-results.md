# Evaluation results

Campaign `2026-10-opus55-xhigh-r1`, graded on 2026-10-03. The design, the decision rule and the
checks are in `evals/README.md` (registered; its sha256 is in `evals/PROVENANCE.txt`). The full
report is `evals/corpus/2026-10-opus55-xhigh-r1/report.json`. Every change made after
registration, with its effect on grading, is in `evals/AMENDMENTS.md`.

## 1. Verdict

**Under the pre-registered rule D8 the campaign is invalid.** Validity criterion V2 is not met, so
the effect criteria decide nothing. The claim that the model without the skill does much worse is
not established. The effect numbers in §3 are reported for information.

- **Validity:** V1, V3 and C1 are met. V2 is not met on two defect types, and neither failure
  comes from the detector (§4).
- **Effect, for information:** H1, H2 and H3 would not be met either; V4 would be.
- **No revision round ran.** The baseline sits near the ceiling, so no revision could reach H1 or
  H2. The operator decided this on 2026-10-03 (TASK D28).

## 2. Setup

- **Model:** `claude-opus-5-5`, effort `xhigh`, one answer per run, no tools.
- **Runs:** 11 cases × 2 arms × 3 repetitions = 66 runs, all graded. Spend: 28.56 USD of the 60 USD
  cap.
- **Arms:** they differ by one input, the skill bundle. `with_skill` received `SKILL.md` and the
  references of the case's routed kind.
- **Measured bundle:** the run records hold its sha256. Example: `SKILL.md`, 2,741 words, sha256
  `852c6ba5…`. The shipped text changed after the campaign (§6).

## 3. Results, for information

Populations differ by score. H and H-core are means over the ten cases C1–C8, F1 and F2 of each
case's median run. Strict and contract pool all 33 runs of an arm, the control C0 included.

| Score | `with_skill` | `without_skill` |
| :--- | ---: | ---: |
| H, headline checks passed | 0.967 | 0.883 |
| H-core, without budget, caption and legend | 0.968 | 0.892 |
| strict, runs that pass every headline check | 0.61 | 0.33 |
| contract, the skill's own conventions | 0.93 | 0.48 |

- **Δ_H:** 0.084, 95 % case-cluster interval [0.035, 0.129]. H1 would need 0.25.
- **Δ_H-core:** 0.076 [0.027, 0.126]. H2 would need 0.15.
- **H3:** `with_skill` leads on 7 of 10 cases, ties on 3, trails on none of them. It would need 8,
  and it trails by more than 0.10 on the control C0 (§5).
- **Sign test, information only:** 7 ahead, 0 behind, 3 ties; one-sided p 0.008.
- **Detector fixes:** before the three fixes of §4, Δ_H was 0.077 [0.032, 0.124]. One fix
  changed a threshold after the results were read and lowered one baseline case.
  `evals/AMENDMENTS.md` states it.

Per check, runs passed of applicable, pooled over the cases:

| Check | `with_skill` | `without_skill` |
| :--- | ---: | ---: |
| Q03 no edge through a node | 17/17 | 15/21 |
| Q04 crossings within 2 | 17/17 | 16/21 |
| Q05 no label overlap, clip or edge through a label | 20/20 | 13/24 |
| Q06 contrast in the dark render | 23/23 | 23/27 |
| Q14 legend where two encodings need one | 20/22 | 7/17 |
| Q09 arrows the way the text states | 29/33 | 30/33 |
| Q10 required relations drawn | 27/33 | 29/33 |
| Q12 no invented element | 29/33 | 28/33 |

- With the skill, no figure failed Q03, Q04, Q05 or Q06. The legend was missing in 2 of 22
  figures, against 10 of 17.
- The geometry family carries the difference: leaving it out drops Δ_H to 0.025 (V4).
- The fidelity checks Q09–Q12 show no difference. The calibration found them noisy (§4), so
  this is no finding about fidelity either way.

**Why D8 cannot be met here.** The baseline scores 0.883, so Δ_H cannot exceed about 0.12, below
H1's 0.25. Three cases end at 1.0 in both arms, so at most 7 of 10 cases can lead, below H3's 8.
The thresholds assumed a weaker baseline.

## 4. Validity

- **V1:** every run graded, with the pinned model served in each.
- **V3:** control C0, `without_skill` H-core 1.0.
- **C1:** contract rate 0.93 with the skill; 0.48 without it, for information.
- **V2:** the sample held 39 items: 30 drawn at random, 9 topped up. Two raters labelled each
  item, blind to the arm and to the detector; a third rater decided the 5 disagreements. All
  raters ran the same model, so V2 is `corroborated`.
- **Labelled items: 34 of the 39.** The 5 top-ups taken from the negative paired examples had no
  renders, and both raters left them unlabelled. The planned top-ups for title crossing and
  illegible text therefore did not happen; those types rest on 2 positives each.

The first grading disagreed with the labels on three types. The cause of each disagreement:

| Cause | Items | Fix |
| :--- | :--- | :--- |
| a milestone label measured against the box around its diamond | 1 | measured in the diamond's frame |
| a 2 px clip allowance applied to drawn note outlines | 1 | 0.5 px for drawn outlines |
| an edge through an edge label counted as a label overlap | 3 | its own check, `edges_through_labels`, still a gate (R7.6) |
| the rubric counted theme-coloured gantt bars as figure-set colour; D26 does not | 1 | none: the detector follows D26 |
| the C0 key accepts only `flowchart` (EI-02) | 1 | amendment `a1` |

After the three detector fixes, V2 per type on the random sample:

| Type | Precision | Recall | κ |
| :--- | ---: | ---: | ---: |
| crossings over allowance | 1.0 | 1.0 | 1.0 |
| edge through node | 1.0 | 1.0 | 1.0 |
| title crossing | 1.0 | 1.0 | 1.0 |
| label overlap or clip | 1.0 | 1.0 | 1.0 |
| illegible at the column | 1.0 | 1.0 | 1.0 |
| dark contrast | — | 0.0 | 0.0 |
| form unfit | 0.0 | — | 0.0 |

The two failing types hold one positive each. The dark-contrast positive follows a rubric wording
that D26 overrules; the form positive is the C0 key defect. No instrument change removes either,
so the campaign stays invalid (TASK D28).

**Fidelity is not calibrated, and it is noisy.** The information-only labels agree poorly with
Q09–Q13:

- "invented element": the detector flagged 4 items, and the raters flagged none.
- "untrue caption": the detector missed both captions the raters flagged.

## 5. Key defects, graded apart

Review round 1 found four key defects after the runs:

- **EI-02:** C0 accepts only `flowchart`, although its request names no kind and Step 0 picks
  ASCII.
- **EI-08:** the keys miss the parts of two containers.
- **EI-09:** the keys miss the documents' own wording.
- **EI-27:** C8 requires the admin console's relations.

Amendment `a1` corrects them. The reviewers had already seen per-case scores, so its report is a
POST-HOC sensitivity analysis.

| Under `a1` | `with_skill` | `without_skill` |
| :--- | ---: | ---: |
| H | 0.979 | 0.910 |
| strict | 0.79 | 0.33 |

Δ_H is 0.070 [0.024, 0.118]. V2 is still not met, so this analysis is invalid under D8 as well.

## 6. What this does and does not show

It suggests, for one strong model on small and medium figures:

- A run passes every headline check about twice as often: 0.61 against 0.33.
- With the skill, no figure exceeds the crossing allowance, cuts through a node, clashes labels
  or loses dark contrast, and legends are missing far less often.

It does not show:

- **A validated effect.** The campaign is invalid under its own rule.
- **Large figures.** No case went past the budgets, where the operator's real figures fail.
- **The fix loop.** Runs were single answers without the lint or the render check.
- **Weaker models and natural requests.**
- **Arm order.** The `without_skill` arm ran first, so API conditions may differ between the arms.
- **The shipped text.** `SKILL.md` and several references changed after the campaign, in the
  review rounds. The Δ refers to the bundle recorded in the runs.
- **The normalisation rule and the grader.** Their sha256 was recorded at grading time, not
  registered (R11.2).

The design of the next campaign is work-item WI-26. It adds large cases, a tool-loop arm and the
operator's own figures.
