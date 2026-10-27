# TASK 129 review — `task-reviewer` on TASK revision 1

- **Reviewer:** `task-reviewer` (read-only subagent), 2026-10-26.
- **Reviewed:** `docs/TASK.md` revision 1, sha256 prefix `309f618adb89`, at tree fingerprint
  `5b7baeaf7adc`, which the reviewer quoted.
- **Evidence in the brief:**
  - `scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md` → `0 warn / 0 info`;
  - `check_positional_refs.py --all docs/TASK.md` → `OK: 0 of 4 reference(s) in 1 document(s)
    resolve against the working tree (4 pinned, not checked)`;
  - the measurements of TASK §8.
- **Kept by:** the orchestrator, from the reviewer's hand-back, in the Architecture phase: the
  Analysis phase did not save it. Each finding keeps its claim; the last column names the answer
  of TASK revision 2.

---

**Verdict: APPROVED. 0 BLOCKING, 8 MAJOR (m1–m8, fixed before Architecture), 8 MINOR (N1–N8).**

## Technical answers

- **R1.** `System/` has no `__init__.py` and `System/scripts/` has one, so the repository root on
  `sys.path` fixes the import from any directory. CI already puts the root on the path
  (`.github/workflows/framework-gates.yml:67@2a7d11c`).
- **R3.** `dompurify` 3.4.17 is inside the `^3.2.4` of mermaid 10.9.8. mermaid-cli 11.17.0 accepts
  puppeteer `^23 || ^24 || ^25` as a peer, and 12.0.0 accepts `^25.0.0`. `chromium-bidi` 17.0.2
  requires `zod ^3.24.1`, which D3 answers.
- **R5.** `True` is the stated policy of `_pid_alive` for an unknown answer; the change removes
  only the event.
- **R4** matches `update_state.py:383@2a7d11c`. **R6.1** follows v3.48.0.

## MAJOR

| ID | Claim | Answer of revision 2 |
| :--- | :--- | :--- |
| m1 | R3.5 had no defined base: after R3.3 `render_check.py` refuses the base installs, whose lockfile stamp is stale | R3.5 renders the base first, in a temporary home; D8 compares statuses and metrics |
| m2 | UC-2 and R3.4 had no failure path; the setup prefers the build that puppeteer pins | UC-2 alternatives 2a, 3a and 3b; R3.4 keeps `browsers.json` and `BROWSER_MIN_BUILD` |
| m3 | The reason of D5 was false: the Windows jobs run the sweep of `tests/conftest.py` | D5 states that no CI run reaches a probe |
| m4 | D4 and §9 did not cite WI-41 | D4 takes option 1 of WI-41 under R3.5; R6.4 closes WI-41 |
| m5 | R6.2 met the disclosure rule of WI-30: TC-05 pins two paragraphs by sha256 | R6.2 names RF-22 and keeps RF-21 and WI-30; A8 runs `tests/test_disclosure_rule.py` |
| m6 | §10.7 of the architecture states the old audit result, outside every requirement | R4.2 names §10.7; R4.3 bounds the other lines |
| m7 | No security review was named, though the change adds dependencies to an auxiliary skill | R7 and A10 |
| m8 | R1.4, R5.2 and R6.2 had no criterion, and A9 mapped from no row | A11, A7 and A8; R2 and R3 map to A9 |

## MINOR

- **N1** — the global interpreter keeps pytest 9.0.2: §9 puts it out of scope.
- **N2** — A7 patches `os.name` around the call only, and records each call of `os.kill`.
- **N3** — D6 records the alternatives of R1; R1.2 registers the cleanup before the `chdir`.
- **N4** — UC-1 has a precondition, and UC-3 has alternative 1a.
- **N5** — §8 states that 3.4.17 fixes the three `dompurify` advisories, and the node floor of
  puppeteer 25.16.0 and `chromium-bidi` 157.
- **N6** — R6.1: the changelog tells the operator to run `setup_renderers.sh` again.
- **N7** — D1 records the move of the archive-chain port to TASK 130.
- **N8** — notes on the evidence: no DETECTORS block; the four references pinned; the referents
  matched by hand; no figure.

## Before the task

- `tests/_scratch.py:20-31@2a7d11c` says that the next sweep collects the directory of a killed
  run, which never held on Windows. R5.3 answers it.
- `docs/ARCHITECTURE.md:215@2a7d11c` repeats the claim of line 120. R4.1 answers it.

## Final recommendation

Proceed to Architecture with revision 2.
`{"review_file": "docs/reviews/task-129-review.md", "has_critical_issues": false}`
