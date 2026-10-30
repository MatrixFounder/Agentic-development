# PLAN 137 — The Mermaid renderers run on native Windows (MR-1)

**TASK:** [docs/TASK.md](TASK.md) (revision 2) · **Covers:** R1–R13 · **Acceptance:** TC-W1–TC-W8.

**Process:** reduced (TASK D3). Edits are in place; the tests come first and run red.

## Steps

- [x] P1 **Tests first.** `scripts/tests/test_renderers_windows.py` holds TC-W1 to TC-W6. The
      setup tests reuse the stand-ins of `test_setup_renderers.py` and preload a module through
      `NODE_OPTIONS` that sets `process.platform` to `win32` and removes `process.getuid`. On the
      base each of TC-W1 to TC-W6 fails; the run records why.
- [x] P2 **Setup** (R1 to R5, R12): the `.exe` candidate, the Windows branch of the Node check,
      `private_problem` and the stat rows on Windows, `build_of` on `\` paths.
- [x] P3 **Render check** (R6 to R9, R12): the platform flag, `install_problem`,
      `browser_stat_digest`, `mmdc_command` and `_run` on Windows.
- [x] P4 **Green on POSIX.** TC-W1 to TC-W6 pass; TC-W8: the skill's test suites pass unchanged,
      and each step of `framework-gates.yml` that runs here passes. One mutation per script
      reverts one Windows branch, and its test fails.
- [x] P5 **Windows job** (R11, D2, D8): a job on `windows-latest` that installs the pinned build,
      prints its tree hash with `--dry-run`, and runs the setup, `render_check.py` on one reference
      figure and the new tests. The first push measures the hash with the override set from the
      dry run; `browsers.json` then records it (R10), and the next push runs with no override
      (TC-W7). Each push waits for the operator's yes; a failure on Windows goes back to P2 or P3.
- [x] P6 **Records** (R13): `SKILL.md`, MR-1 and `docs/KNOWN_ISSUES.md`, both changelogs.
- [x] P7 **Reviews.** One code reviewer with the exhaustive prompt and one security auditor, in
      parallel, on the same fingerprint; then one fix pass, the gates again and the Windows job.
- [x] P8 **Commit** on the operator's word: the work branch merges into `main`.
