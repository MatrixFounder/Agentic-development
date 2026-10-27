# Task 129-04: The records and the check of the architecture

## Use Case Connection

- UC-2: The operator installs the renderers

<!-- contract:goal -->

## Task Goal

Write the records of TASK R6.1, R6.2, R6.4 and R6.5, and check §10.7 of the architecture, so that
each document states the overrides, the audit result of Task 129.3 and the bundled copies.

<!-- contract:changes -->

## Changes Description

`M/` stands for `.agent/skills/mermaid-authoring-guidelines/`.

### Changes in Existing Files

#### Files: `CHANGELOG.md` and `CHANGELOG.ru.md`

- Each gains a v3.48.1 entry above v3.48.0, in the form of v3.48.0 (R6.1). The entry lists:
  - the tests that run from any working directory (R1);
  - pytest 9.1.1 (R2);
  - the overrides of the renderer lockfiles, puppeteer 25.16.0 and the audit result (R3);
  - the answer of `_pid_alive` on Windows (R5);
  - the lock file that the architecture names (R4).
- The entry tells the operator to run `setup_renderers.sh` again: `render_check.py` refuses an
  install whose lockfile stamp is stale.
- The entry names each copy of DOMPurify and KaTeX that the render page runs, by tag and package,
  with its version, and states that WI-41 stays open for them (R6.5, TASK D9).

#### File: `M/references/renderer-facts.md`

- RF-22 states the overrides of `dompurify` and `katex`, and puppeteer 25.16.0 in each lockfile
  (R6.2). Its heading at the base:
  `.agent/skills/mermaid-authoring-guidelines/references/renderer-facts.md:818@2a7d11c` `### RF-22 — the floor renderer runs on the puppeteer of v11`
- RF-22 states the entry count of each lockfile, every key of `packages` counted, as RF-22 counts
  them.
- RF-22 states the result of `npm audit` of Task 129.3, with its date.
- RF-22 names each copy of DOMPurify and KaTeX that the render page runs, by tag and package, with
  its version (R6.5).
- RF-21 and the record of WI-30 stay as they are: TC-05 of `tests/test_disclosure_rule.py` pins a
  paragraph of each.

#### Files: `docs/backlog/wi-41-katex-advisory-ghsa-238p-pmpm-9mq7-in-the-renderer-lockfiles.md` and `docs/BACKLOG.md`

WI-41 stays open (R6.4, TASK D9):

1. The front matter keeps `status: open`.
2. A progress blockquote goes to the top of the body. The rest of the body stays as it is
   (`provenance: machine`). Precedent: PLAN 128 C6. The blockquote names:
   - the overrides and the audit result of Task 129.3;
   - each copy that the page runs, by tag and package, with its version and its advisories;
   - the condition of the closing, per copy (TASK R6.4).
3. The index line stays in its group and names the progress.

#### File: `docs/ARCHITECTURE.md`

- §10.7 is checked against the audit of Task 129.3 (R4.2). Its date follows that run.
- §10.7 names `katex` 0.18.10 (TASK D4) and the audit of 2026-10-27 (code review of Task 129.3,
  round 2).
- §10.7 names each copy of DOMPurify and KaTeX that the render page runs, by tag and package, with
  its version (R6.5).
- On the katex branch of R3.7, step 5 of that branch changes two sentences of §10.7.
- No other line changes (R4.3).

#### File: `tests/test_session_state_contract.py`

- **Method `test_c7_the_architecture_names_both_locks`:** each of the two lines also holds
  `` `.agent/sessions/latest.yaml.lock` `` (architecture review, MINOR 5).

<!-- contract:tests -->

## Test Cases

### Unit Tests

1. **TC-C7** — the two lines of `docs/ARCHITECTURE.md` → each holds `` `fcntl` ``, `` `msvcrt` `` and
   `` `.agent/sessions/latest.yaml.lock` ``; fails when either line names `latest.yaml` as the lock.
   The mutation runs on a copy of the document (A6).
2. **TC-D1** — `scan_register.py` on each edited document, against its base text → no `warn` on an
   added line (A8).
3. **TC-D2** — `tests/test_disclosure_rule.py` → passes (A8).

### Regression Tests

- `check_positional_refs.py` over the living corpus → no new `REFERENT_ABSENT`.
- Every `run:` step of `.github/workflows/framework-gates.yml`, run locally → each passes.

<!-- contract:acceptance -->

## Acceptance Criteria

- [ ] A6 and A8 hold.
- [ ] The code review approves.

## Notes

- The date of §10.7 and RF-22 is the date of the `npm audit` run of Task 129.3 on the committed
  lockfiles. The probe of the Architecture phase ran on copies (architecture review, MINOR 3).
- On the katex branch of R3.7, the changelog entry and RF-22 name the override of `dompurify` only,
  and GHSA-238p-pmpm-9mq7 as the low advisory that stays (PLAN 129, Failure paths, step 4).
