# Code Review: Task 129.3 — the renderer lockfiles

- **Reviewer:** `code-reviewer` (subagent), `03-develop-single-task` step 4. A security auditor
  reviewed the lockfile diff in parallel (TASK R7): `docs/reviews/security-129-review.md`.
- **Kept by:** the orchestrator, from the reviewer's hand-backs.

## Round 1 — 2026-10-26, at tree fingerprint `0a8d25c3fc5a`

**Status: REJECTED. 0 BLOCKING, 2 MAJOR, 5 MINOR.** The reviewer quoted the fingerprint, and the
orchestrator recomputed the same value at the return. The reviewer wrote nothing in the repository.

**Verified in the round:**

- each lockfile is byte-identical to its probe lockfile, and written again from the lockfile of
  HEAD with the committed manifest it comes out the same (R3.3);
- `npm audit` reports 0 advisories for each tag (A3); the manifests are in npm format, with the
  overrides sorted;
- only `node_modules/puppeteer` has an install script, so the claim at
  `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:13@2a7d11c` holds;
- 7 plantings on copies of the lockfiles each turn TC-L1 or the v10 test red.

### MAJOR

| ID | Finding | Answer |
| :--- | :--- | :--- |
| 1 | The statements of the bundled copies left out DOMPurify 3.3.1 of `@mermaid-js/mermaid-zenuml` (v11, v12) and the copies of `@mermaid-js/layout-elk` 0.2.3 (v11); the closing condition of WI-41 named mermaid releases only | measured again by the orchestrator; the operator confirmed D9 with every copy (2026-10-27); TASK revision 5 D9 and §8, R6.4 per copy, the setup header |
| 2 | `katex` 0.18.11 is deprecated by its publisher: "Accidentally published with breaking changes. Use 0.19.0 instead." | the operator chose 0.18.10 (2026-10-27); TASK D4; the manifests, `KATEX`, the lockfiles, the audit, the setup and the comparison done again |

### MINOR

| ID | Finding | Answer |
| :--- | :--- | :--- |
| 3 | The setup header stated the measurement under 19.11.1 in the present tense | both render sentences carry their dates |
| 4 | TASK D9 said that the advisories of §1 cover each copy; the critical one does not cover 3.4.2 | TASK §8 names the advisories of each copy |
| 5 | PLAN gave R6 as `129.3 (R6.3)` | `129.3 (R6.3, R6.5)` |
| 6 | D9's first rejected option gave no reason; the note of revision 4 was incomplete | reasons stated; the revision notes complete |
| 7 | `compare_renders.py` skipped `fonts`, `font_family`, `findings` and `pass` | it compares every field of a figure and of a render but the paths of the render files |

**Before the task:** `.agent/skills/mermaid-authoring-guidelines/scripts/mermaid_model/kinds.py:27@2a7d11c`
says that no pinned renderer loads the zenuml plugin; each of the three renders a `zenuml` fence.

## Round 2 — 2026-10-27, at tree fingerprint `dbdcf6571d95`

**Status: APPROVED, MERGE. 0 BLOCKING, 0 MAJOR, 4 new MINOR.** The reviewer quoted the fingerprint,
and the orchestrator recomputed the same value at the return. Each finding of round 1 is closed.

**Verified in the round:**

- the reviewer wrote each lockfile from the lockfile of `2a7d11c` with the final manifest: each came
  out byte-identical to the committed file, and a second run left it unchanged;
- against the lockfiles of round 1 only `node_modules/katex` differs; each lockfile holds one
  `katex`, at the top, with no `deprecated` field;
- the six copies of the tables match the reviewer's own measurement; the advisory counts of TASK §8
  recounted from the ranges: 13, 5 and 21;
- the widened `compare_renders.py` and the reviewer's own comparison of every field: 0 differences
  over 52 figures and 208 renders; 5 plantings in copies of the render output each gave 1
  difference;
- 4 plantings on copies of the lockfiles each turned TC-L1 red, among them `katex` 0.18.11 left in
  v12 and `katex` nested under mermaid;
- A9 with the new installs: `743 passed, 1 skipped`.

### MINOR

| ID | Finding | Answer |
| :--- | :--- | :--- |
| 1 | `docs/ARCHITECTURE.md` §10.7 still named `katex` 0.18.11 and the audit of 2026-10-26 | Task 129.4 names 0.18.10 and the audit of 2026-10-27 |
| 2 | The closing condition of R6.4 asked each package for KaTeX, which the zenuml plugin does not carry | TASK revision 6: each DOMPurify copy 3.4.17 or newer, each KaTeX copy 0.18.2 or newer |
| 3 | The note of revision 5 left out R3.1, A4, R6.4 and R6.5 | the note names them |
| 4 | D9 said "default options", where mermaid also passes `FORBID_TAGS` | D9 takes the wording of the audit |
