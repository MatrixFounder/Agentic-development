# PLAN 138 — update_state.py names the keys it drops, and a restored session names the date of its state (WI-60, WI-61)

**TASK:** [docs/TASK.md](TASK.md) (revision 2) · **Covers:** R1–R5 · **Acceptance:** TC-K1–TC-K4, TC-B1, TC-B2.

**Process:** reduced (TASK D1). Edits are in place; the tests come first and run red.

## Steps

- [x] P1 **Tests first.** TC-K1 to TC-K4 in `test_update_state.py`; TC-B1 in
      `tests/test_session_state_contract.py`. On the base TC-K1, TC-K3 and TC-B1 fail.
- [x] P2 **Script** (R1, R2): the dropped keys read from the state, the stderr line after the write.
- [x] P3 **Documents** (R3, R4): the three system prompts, `SKILL.md` §1 and §2, the guide's §1.
- [x] P4 **Green.** The tests of the skill and the contract tests pass, and each step of
      `framework-gates.yml` that runs here passes. One mutation per requirement fails a test.
- [x] P5 **Records** (R5): WI-60, WI-61, `docs/BACKLOG.md`, both changelogs, v3.55.0.
- [x] P6 **Reviews.** One code reviewer with the exhaustive prompt and one security auditor, in
      parallel; then one fix pass and the gates again.
- [x] P7 **Commit** on the operator's word.
