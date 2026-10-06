---
id: WI-37
type: work-item
status: dropped
opened_at: 2026-10-06
slug: wi-37-external-scanners-that-run-the-scanned-projects-code
effort: M
value: 'a security audit runs no code of the project it scans'
source: 'TASK 112 (WI-35 follow-up)'
component: '.agent/skills/security-audit/scripts/audit/external.py'
resolved_at: 2026-10-06
resolved_by: 'operator, TASK 112 retro'
---

# WI-37 — External scanners that run the scanned project's code

> **Dropped 2026-10-06 (operator, TASK 112 retro).** The operator does not need it. The `yarn audit`
> copy of TASK 112 R5.1 stays; the other scanners keep running in the scanned root.

**Signal.** `run_external_tools` runs tools in the scanned root, and some of them execute that
project's code or configuration:

- `cargo clippy` builds the crate and runs its `build.rs`;
- `slither .` compiles through the project's build framework; a Hardhat configuration is
  JavaScript;
- `pip-audit` in a project directory can build a source distribution.

TASK 112 R5.1 moved `yarn audit` into a copy of `yarn.lock` and `package.json`; the copied
`package.json` keeps the dependency fields only, so a corepack `yarn` shim fetches no version that
`packageManager` or `devEngines` names. The others still run in the scanned root. The behaviour of each tool is not measured.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Measure each tool; run it in a copy or with the option that skips a build | M | per-tool work |
| 2 | Run the code-executing tools only with an operator flag | S | an audit without the flag covers less |
| 3 | do nothing, document the constraint | — | an audit of an untrusted project runs its code |

**Recommendation.** Option 1, with option 2 for a tool that has no safe form.

**Acceptance.** Each external tool runs no code of the scanned project, or runs only with a flag
the operator passes.
