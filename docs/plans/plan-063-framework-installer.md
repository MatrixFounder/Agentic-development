# Development Plan — Framework Installer Script (Task 063)

**Parent**: [docs/TASK.md](TASK.md) — Technical Specification: Framework Installer Script
**Architecture**: [docs/ARCHITECTURE.md §9](ARCHITECTURE.md#9-framework-installer-subsystem) — Framework Installer Subsystem
**Mode**: VDD (Verification-Driven Development)
**Source plan**: `/Users/sergey/.claude/plans/snug-foraging-wind.md` (approved)

## Goal

Decompose the TASK (10 Epics E1–E10, ~35 Issues) into **11 atomic, verifiable tasks** under Stub-First discipline. Stage 1 builds the full module skeleton + config + test scaffold (`[STUB CREATION]`); Stage 2 implements logic layer-by-layer with per-module unit tests (`[LOGIC IMPLEMENTATION]`); Stage 3 wires integration tests.

**Already done (uncommitted stubs)**: [install.sh](../install.sh) (Issue I1.1 ✅) and [System/scripts/install.py](../System/scripts/install.py) argparse skeleton (Issue I1.2 ✅). `install.py` already imports `installer.cli.main` — Task 063-01 must create that package or the entry-point is broken.

## Stub-First strategy

Per [planning-decision-tree](../.agent/skills/planning-decision-tree/SKILL.md) §1: every functional module is split into structure (signatures + `NotImplementedError` stubs + docstrings) and logic. The installer is a 12-module Python package, so Stage 1 is one structural task covering **all** skeletons + `vendors.yaml` (pure config — single task per decision-tree rule) + the E2E test harness that goes Red→Green on stubs. Stage 2 then replaces stubs one layer at a time, bottom-up (no module implemented before its dependencies).

## Task Execution Sequence

### Stage 1 — Structure & Stubs `[STUB CREATION]`

- **Task 063-01** — Installer package skeleton + `vendors.yaml` + test scaffold
  - Epics/Issues: E1 (I1.3 vendors.yaml), all-module skeletons for E2–E9, E10/I10 scaffold
  - RTM: NFR-3 (stub-first), NFR-5 (minimal deps)
  - Description: [docs/tasks/task-063-01-installer-skeleton.md](tasks/task-063-01-installer-skeleton.md)
  - Priority: Critical
  - Dependencies: none (consumes existing `install.py`/`install.sh`)

### Stage 2 — Core Logic `[LOGIC IMPLEMENTATION]`

- **Task 063-02** — Errors + vendor profile loader & validator
  - Epics/Issues: E1 — I1.4 (`vendors.py`), I1.5 (`errors.py`)
  - RTM: FR-2 (vendor profile system), FR-14 (codex `git_root_required` profile field)
  - Description: [docs/tasks/task-063-02-vendors-errors.md](tasks/task-063-02-vendors-errors.md)
  - Priority: Critical · Dependencies: 063-01

- **Task 063-03** — State management + backup engine
  - Epics/Issues: E7 — I7.1 (`state.py`), I7.2 (heuristic mode), I7.3 (`backup.py` + retention)
  - RTM: FR-9 (state management), FR-10 (backup part)
  - Description: [docs/tasks/task-063-03-state-backup.md](tasks/task-063-03-state-backup.md)
  - Priority: Critical · Dependencies: 063-01, 063-02

- **Task 063-04** — `.agentic-development/` root management + platform
  - Epics/Issues: E2 — I2.1 (symlink mode), I2.2 (copy mode), I2.3 (target guards); `platform.py`, `copy.py`
  - RTM: FR-3 (root management), FR-13 (platform fallback)
  - Description: [docs/tasks/task-063-04-framework-root.md](tasks/task-063-04-framework-root.md)
  - Priority: Critical · Dependencies: 063-01, 063-02

- **Task 063-05** — Symlink engine
  - Epics/Issues: E3 — I3.1 (`link_one`), I3.2 (`link_per_item`), I3.3 (`link_folder`), I3.4 (`mkdir`)
  - RTM: FR-4 (per-item symlinks + reachability)
  - Description: [docs/tasks/task-063-05-symlink-engine.md](tasks/task-063-05-symlink-engine.md)
  - Priority: Critical · Dependencies: 063-01, 063-02

- **Task 063-06** — Managed-block engine
  - Epics/Issues: E4 — I4.1 (`inject_block`), I4.2 (marker formats), I4.3 (atomic write + force backup)
  - RTM: FR-5 (managed-block engine), NFR-2 (no silent clobber)
  - Description: [docs/tasks/task-063-06-managed-block.md](tasks/task-063-06-managed-block.md)
  - Priority: Critical · Dependencies: 063-01, 063-02, 063-03 (backup)

- **Task 063-07** — Vendor-aware bootstrap
  - Epics/Issues: E5 — I5.1 (`at_import`), I5.2 (`marker_block`), I5.3 (`none`), I5.4 (don't-overwrite list)
  - RTM: FR-6 (vendor-aware bootstrap), FR-15 (Antigravity dual bootstrap)
  - Description: [docs/tasks/task-063-07-bootstrap.md](tasks/task-063-07-bootstrap.md)
  - Priority: High · Dependencies: 063-06 (managed-block), 063-05 (symlinks)

- **Task 063-08** — `.gitignore` patch + `!`-exception scanner
  - Epics/Issues: E9 — I9.1 (`update_gitignore`), I9.2 (`!`-scanner)
  - RTM: FR-7 (`.gitignore` block)
  - Description: [docs/tasks/task-063-08-gitignore.md](tasks/task-063-08-gitignore.md)
  - Priority: High · Dependencies: 063-06 (managed-block)

- **Task 063-09** — Conflict prevention + `install` end-to-end
  - Epics/Issues: E6 — I6.1 (classifier), I6.2 (`System/` case), I6.3 (`--dry-run`), I6.4 (`--skip`); `install` algorithm in `cli.py`
  - RTM: FR-1 (`install` subcommand), FR-8 (conflict prevention), FR-14 (codex git-root check), NFR-1 (idempotency)
  - Description: [docs/tasks/task-063-09-conflict-install.md](tasks/task-063-09-conflict-install.md)
  - Priority: Critical · Dependencies: 063-02…063-08 (all layers)

- **Task 063-10** — Subcommands `switch` / `uninstall` / `update` / `doctor`
  - Epics/Issues: E8 — I8.1 (`switch`), I8.2 (`uninstall`), I8.3 (`update`), I8.4 (`doctor`)
  - RTM: FR-1 (remaining subcommands), FR-10 (`switch`), FR-11 (`uninstall`), FR-12 (`doctor`)
  - Description: [docs/tasks/task-063-10-subcommands.md](tasks/task-063-10-subcommands.md)
  - Priority: High · Dependencies: 063-09

### Stage 3 — Integration & Verification

- **Task 063-11** — Integration E2E suite + bash wrapper smoke test
  - Epics/Issues: E10 — I10.2 (integration tests), I10.3 (wrapper smoke test)
  - RTM: NFR-1 (idempotency), NFR-4 (testability)
  - Description: [docs/tasks/task-063-11-integration-tests.md](tasks/task-063-11-integration-tests.md)
  - Priority: High · Dependencies: 063-10

> **Issue I10.1 (per-module unit tests)** is intentionally *not* a separate task — under Stub-First, unit tests ship in Phase 2 alongside the logic they cover. Each Stage-2 task (063-02 … 063-10) delivers its own `tests/installer/test_<module>.py` as an acceptance criterion. Task 063-11 covers only the cross-module integration recipe (I10.2) and the bash smoke test (I10.3).

## Dependency Graph

```
063-01 (skeleton + vendors.yaml + test scaffold)
   │
   ├─► 063-02 (errors, vendors)
   │       ├─► 063-03 (state, backup)
   │       ├─► 063-04 (framework_root, platform, copy)
   │       └─► 063-05 (symlinks)
   │
   ├─► 063-06 (managed_block)  ◄── needs 063-03 (backup)
   │       ├─► 063-07 (bootstrap)  ◄── also needs 063-05
   │       └─► 063-08 (gitignore)
   │
   └─► 063-09 (conflict + install)  ◄── needs 063-02…063-08 (ALL layers)
           └─► 063-10 (switch/uninstall/update/doctor)
                   └─► 063-11 (integration tests)
```

**Serial VDD execution order**: `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11`. This order satisfies every edge above (063-06 lands before 063-07/063-08; all layers before 063-09). Tasks 063-03/04/05 are mutually independent and *could* run in parallel after 063-02, but VDD runs them serially so each gets its own verification gate.

## RTM Coverage Matrix

One requirement → at least one task; every task carries an RTM ID per [06_planner_prompt](../System/Agents/06_planner_prompt.md) §2.

| RTM      | Requirement                              | Covered by task(s)        |
|----------|------------------------------------------|---------------------------|
| `[FR-1]`  | CLI subcommands + flags + exit codes     | 063-01 (skeleton), 063-09 (`install`), 063-10 (`switch`/`update`/`uninstall`/`doctor`) |
| `[FR-2]`  | Vendor profile system (`vendors.yaml`)   | 063-01 (yaml), 063-02 (loader+validator) |
| `[FR-3]`  | `.agentic-development/` root management  | 063-04 |
| `[FR-4]`  | Per-item symlinks + reachability         | 063-05 |
| `[FR-5]`  | Managed-block engine                     | 063-06 |
| `[FR-6]`  | Vendor-aware bootstrap                   | 063-07 |
| `[FR-7]`  | `.gitignore` block + hash protection     | 063-08 |
| `[FR-8]`  | Pre-flight conflict prevention           | 063-09 |
| `[FR-9]`  | State management                         | 063-03 |
| `[FR-10]` | `switch` with backup                     | 063-03 (backup), 063-10 (`switch`) |
| `[FR-11]` | `uninstall` with `--purge`               | 063-10 |
| `[FR-12]` | `doctor` read-only verifier              | 063-10 |
| `[FR-13]` | Platform fallback (Windows)              | 063-04 |
| `[FR-14]` | Codex git-root requirement               | 063-02 (profile field), 063-09 (check) |
| `[FR-15]` | Antigravity dual bootstrap               | 063-07 |
| `[NFR-1]` | Idempotency                              | 063-09, 063-11 |
| `[NFR-2]` | No silent clobber                        | 063-06, 063-11 |
| `[NFR-3]` | Stub-First implementation                | 063-01 |
| `[NFR-4]` | Testability                              | 063-02…063-10 (unit), 063-11 (integration) |
| `[NFR-5]` | Minimal dependencies                     | 063-01 |

## Verification (chain-end)

After Task 063-11 merges, run the full installer test suite:

```bash
python3 -m pytest tests/installer/ -v          # all unit + integration tests pass
bash tests/installer/test_wrapper.sh           # wrapper smoke test (bash/sh/zsh)
python3 -m pytest tests/ -q                    # full regression — no pre-existing tests broken
```

End-to-end the installer must satisfy the recipe in `/Users/sergey/.claude/plans/snug-foraging-wind.md` §Verification (fresh install, conflict prevention, idempotency, switch, copy mode, anti-clobber, uninstall).

## Out of Scope (post-MVP — see [TASK §5](TASK.md))

- Git clone / submodule population strategies.
- Migration to plural `.agents/`.
- MD→MDC transformer for Cursor `.cursor/rules/`.
- `System/` rename in framework.
