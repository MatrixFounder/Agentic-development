---
id: WI-1
type: work-item
status: done
opened_at: 2026-07-20
slug: wi-1-skill-spec-validator-unit-tests
effort: S
value: 'prevents silent matcher drift / dead gate'
source: TASK 090
resolved_at: 2026-07-30
resolved_by: TASK 092
---
# WI-1 — Add unit tests for skill-spec-validator

> **✅ DONE 2026-07-30 (TASK 092; hardened after the vdd-multi review).** 38 stdlib tests under
> `.agent/skills/skill-spec-validator/scripts/tests/`, run by
> `bash scripts/tests/run_tests.sh` with a **zero-test-discovery guard** (a run that executes
> nothing is a failure, not a green gate). `SKILL.md` v1.0 → 1.1 gained the four Execution-Policy
> sections; the skill is now warning-free in `validate_skills.py` (45/45).
>
> **Everything this WI asked for is covered**, with the heading fixtures copied **verbatim** from
> `docs/tasks/` rather than invented: all **8** shapes the corpus actually ships (h2/h3, `N.`/`N)`
> section numbers, trailing `(RTM)`, the bare `Requirements (RTM)`, and two
> `Acceptance Criteria (…)` forms the WI had not enumerated), negative shapes (h1, h5, prose,
> non-RTM headings), ID references in **both** `## Step N — … (R1)` headings and `- [ ] R1` bullets,
> the **`R1`-vs-`R10`** boundary plus hyphenated ids (`R-065-1`, `TF-X-7`) and markdown noise
> (`**R1**`, `` `R1` ``, `[R1]`), and the empty-table / wrong-columns / bypass paths.
>
> **The part that actually answers the WI's *why*.** Fixture tests alone would not have caught the
> original drift — the next author to re-tighten the regex would have updated the fixtures to match
> their new idea of the convention. So `tests/test_corpus.py` anchors to the **artifacts**: a probe
> keyed on the `trace*`/`rtm` stems — **wider** than the matcher's required phrase — finds the
> RTM-ish headings under `docs/tasks/` and asserts `RTM_HEADER` matches every one that is not a
> declared non-RTM mention, plus a regression pin on the 8 shapes that must never stop matching and
> liveness floors (≥15 tasks pass `--mode task`, ≥10 exact-slug pairs pass `--mode plan`; **20 and
> 14 of 27 today**). Finding **zero** headings is itself a failure. The floors are canaries set
> *below* today's counts, so artifact churn never reddens the suite while a dead matcher always
> does. Outside the framework repo these tests skip.
>
> **The first version of that probe was a tautology** and the vdd-multi logic critic caught it: it
> required `requirements traceability` or `(rtm)`, i.e. a **subset** of what `RTM_HEADER` accepts, so
> "every probed heading matches" was true by construction and could only fail if someone *narrowed*
> the matcher. It could not see the corpus drifting to a shape neither regex knew — the very drift
> its docstring claimed to catch. Widening the probe immediately surfaced a real corpus case
> (`task-050`'s prose heading `### 2.1 Analysis Phase: The "Traceability Matrix"`), now an explicit,
> staleness-checked exclusion rather than a silent one.
>
> **Proof the guard bites, not just that it is green:** re-injecting each historical regression
> turns the suite red — the pre-TASK-090 `^## Requirements Traceability$` matcher → **28 failures**
> (every corpus test among them), the literal `[**R-1**]` PLAN token → **7 failures**.
>
> **Deliberately NOT changed** (`developer-guidelines`: no unsolicited refactoring; a live gate
> loosened to fit a nonconforming artifact is this very defect running backwards):
> 1. `validate.py` still `sys.exit()`s from its entry points — tests assert on `SystemExit.code`
>    with stdout captured instead. A testability refactor of a live gate is a separate change.
> 2. The `ID`/`Requirement` column contract stays as-is, so
>    `docs/tasks/task-088-known-issues-vdd-fixes.md` (`| ID | Finding | Fix | Verify |`) remains the
>    one corpus artifact failing `--mode task`. Recorded, not papered over.
> 3. **The bypass is a bare substring anywhere in `TASK.md`** — writing the token into a spec
>    silently switches its own gate off and prints a line that reads like a pass. This bit TASK 092's
>    own first-draft spec. Pinned by a test and documented with a warning in `SKILL.md`; tightening
>    it is a behaviour change for the owner to decide.
>
> Dogfood: TASK 092's own `docs/TASK.md` carries a real RTM and both modes pass on it
> (`Found 12 requirements` / `All 12 requirements covered`).

> Migrated verbatim from the single inlined `docs/BACKLOG.md` bullet when this ledger became a thin
> index over record files (TASK 091). Text preserved; only the frontmatter and this note are new.

skill-spec-validator ships zero unit tests. Both matchers (RTM heading + PLAN ID coverage) drifted
from the real house convention and failed on 100% of artifacts across >=2 prior "fixes", undetected
until a manual corpus run in TASK 090. Add tests/ with fixtures covering: the 6 RTM heading forms
(h2-h4, section number, trailing (RTM), bare `Requirements (RTM)`), ID references in both
`## Step N (R1)` headings and `- [ ]` bullets, the R1-vs-R10 whole-token boundary, and the empty-table
/ bypass paths.
