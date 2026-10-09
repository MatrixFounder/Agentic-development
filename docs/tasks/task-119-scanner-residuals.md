# TASK 119 — The in-process scans skip a file that is not regular, the test helper's PATH holds system directories only, and printable escapes the backslash

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 119 |
| Slug | scanner-residuals |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | [WI-51](../backlog/wi-51-residual-routes-of-the-task-118-scanner-review.md); the operator's request of 2026-10-09 |
| Base revision | `5d0c83f0832a7960d98d6c1a00a5e94288250725` |
| Closes | WI-51 |
| Archive name | `task-119-scanner-residuals.md` |
| Revision | 6: the operator's D5 to D7 |

<!-- contract:problem -->

## 1. Problem

WI-51 holds seven routes that the review of TASK 118 left. This task takes five of them.

1. **A FIFO blocks an in-process scan.** Six sites call `open()` on a file of the scanned tree:
   - the `requirements.txt` check of the deps scan
     (`.agent/skills/security-audit/scripts/audit/scanners.py:165@5d0c83f` `with open(req, 'r', encoding='utf-8', errors='ignore') as f:`);
   - the secrets, patterns, configuration, IaC and MCP scans
     (`.agent/skills/security-audit/scripts/audit/scanners.py:250@5d0c83f` `with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:`,
     and lines 343, 403, 461 and 615 at the same revision).

   `open()` on a FIFO waits for a writer. The stage-2 code review of TASK 118 measured the
   secrets scan blocking until the process was killed.
2. **The test helper's `PATH`.** `AuditTestCase` puts the fake `npm` before the whole real `PATH`
   (`tests/test_lockfile_audit.py:134@5d0c83f` `env = {"PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",`).
   A tool installed on the machine, such as one under `/opt/homebrew/bin`, can start in a case
   that does not fake it.
3. **`printable` leaves the backslash.** A file name that holds the text `\x0a` prints as an
   escaped newline does.
4. **The module docstring** of `tests/test_lockfile_audit.py` lists TC-E19 but not TC-E19b.
5. **`security-audit` §2** lacks the routers' sentence that a run with no report is `NOT_RUN`.

**Why.** Items 1 and 3 reach the scanner's output from the scanned tree; item 2 lets a real tool
run inside a unit test.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Acceptance |
| :--- | :--- | :--- | :--- |
| R1 | Each in-process open of a scanned file refuses a file that is not regular | Y | A1, A2 |
| R2 | The test helper's `PATH` holds the fake tools and the system directories only | Y | A3 |
| R3 | `printable` escapes the backslash | Y | A4 |
| R4 | The test docstring lists TC-E19b | Y | A5 |
| R5 | §2 states that a run with no report is `NOT_RUN`, and that a non-regular file is skipped | Y | A5 |
| R6 | Records: changelogs and WI-51 | Y | A5 |
| R7 | Staging (`framework-upgrade` §3 step 4), as TASK 118 R7 | Y | A6 |

<!-- contract:requirements -->

## 3. Requirements

- **R1.1** `helpers.py` gains `open_regular_text(path, root)`. With `root` given, it resolves
  `path` with `os.path.realpath`, and a real path outside the real path of `root` raises
  `OSError("outside the scanned root")` before any open (D6). It opens the real path with
  `os.O_RDONLY`
  and, where the platform has them, `O_NONBLOCK` (a FIFO does not wait), `O_NOCTTY` (a terminal
  does not become the controlling one) and `O_BINARY` (Windows reads past a `0x1A` byte, as
  `open()` did). It then checks the opened descriptor with `os.fstat`:
  - a type other than a regular file → close, `OSError("not a regular file")`;
  - a size above `config.MAX_FILE_SIZE`, read at call time → close, `OSError("exceeds the size
    limit")`;
  - otherwise it clears `O_NONBLOCK` and returns a text stream, UTF-8 with `errors="ignore"`.
- **R1.2** The six sites of §1 item 1 call `open_regular_text` in place of `open`.
  - Each site already catches the error. The five scans count the file in `skipped_files` and print
    `[WARN] Skipped <path>: <reason>`; the reason is `not a regular file`, or the error that
    `os.open` raises for a socket or a device it cannot open.
  - The `requirements.txt` check returns "not hash-pinned".
- **R1.3** A link to a regular file inside the scanned root is still read, as in the base. A link
  whose real path leaves the root is skipped and counted, as R1.2 states (D6). Each site passes its
  scanned root: `project_path` in the five scans, `base` in the `requirements.txt` check.
- **R2.1** `AuditTestCase` sets `PATH` to the fake `bin` directory, then `/usr/bin` and `/bin`.
  The fake `npm` calls `ls`, `tr`, `cat` and `grep` from those two directories.
- **R3.1** `printable` escapes a backslash as `\\`. The escapes it writes for other characters
  stay as they are.
- **R4.1** The docstring of `tests/test_lockfile_audit.py` names TC-E19b and the cases of this task.
- **R5.1** The auditor bullet of §2, **Exit codes and summary**, gains: "A run that prints no
  report, such as exit 1 with a JSON `error` or exit 2, is `NOT_RUN`."
- **R5.2** §2's **Text from the tree** bullet states the backslash escape. A new bullet states that
  a file that is not regular is skipped and counted in `skipped_files`.
- **R6.1** `CHANGELOG.md` and `CHANGELOG.ru.md` get v3.40.1, with R1 to R3.
- **R6.2** WI-51 gets `status: done`, `resolved_at`, `resolved_by: 'TASK 119'` and a resolution
  blockquote. Its index line moves under `## Closed`. The blockquote states the other two routes:
  - the wrapper's positive exit code is covered by D13 of TASK 118 and is closed;
  - the target of the `mcp-scan` fallback is not verified, and §2 states it (D7).
- **R6.3** §2 states that the target of the `mcp-scan` fallback is not verified (D7).
- **R6.4** `System/Docs` does not change: D2 keeps the version in `SKILLS.md` and `VDD.md`.

- **R7.1** Staged names: `audit/helpers_next.py`, `audit/scanners_next.py`,
  `tests/staged_lockfile_audit.py`. `run_audit.py`, `__init__.py`, `external.py` and the other
  tests do not change.
- **R7.2** The staging differs from TASK 118 R7 as follows:
  - the driver's mode `next` registers the staged `.helpers` and `.scanners`, and loads
    `__init__.py` and `.external` from their final paths; it asserts each module's `__file__`;
  - the bootstrap of the subprocess cases registers that package as `audit` and runs the final
    `run_audit.py`;
  - stage 3 is one patch: three renames, no version change;
  - `Pending after restore` lists §2 of `security-audit`, the two changelogs and WI-51.
- **R7.3** The mutation runs, each in a fresh subprocess of the driver:
  - a scan site keeps `open()` → TC-F1 fails;
  - the `requirements.txt` check keeps `open()` → TC-F2 fails;
  - `open_regular_text` returns the stream without the type check → TC-F1 fails;
  - `PATH` holds the real `PATH` again → TC-F4 fails;
  - `printable` leaves the backslash → TC-F5 fails;
  - the root check refuses every file → TC-F3 fails;
  - `open_regular_text` drops `O_BINARY` → TC-F6 fails;
  - `open_regular_text` does not close the descriptor on a refusal → TC-F7 fails;
  - `open_regular_text` drops the size check → TC-F8 fails;
  - `open_regular_text` drops the root check → TC-F9 fails.
- **R7.4** The staging follows TASK 118 R7.2 to R7.11, with the differences of R7.2.

<!-- contract:tests -->

## 4. Test obligations

In `tests/staged_lockfile_audit.py`:

- **TC-F1** — FIFOs named `app.js`, `config.json`, `main.tf` and `.mcp.json` under the scanned
  root. For each of `secrets`, `patterns`, `config`, `iac` and `mcp`, `run_audit.py --scan-type
  <type> --output json` runs as a subprocess, with `PATH` the fake `bin` only and a 20 s timeout.
  - The run ends, and stderr names each FIFO the section reads with `not a regular file`.
  - The section's `skipped_files` equals the number of FIFOs its extension set selects.
  - The case fails when a site keeps `open()`: the run blocks, and the timeout fails it.
- **TC-F2** — `pyproject.toml` and a FIFO named `requirements.txt`; `--scan-type deps` as a
  subprocess, same `PATH` and timeout → the run ends and reports the Python lock file as missing.
  No new case opens a FIFO in process.
- **TC-F3** — a link `link.js` to a regular file inside the scanned root, holding a secret
  pattern → the secrets scan reports it, as in the base.
- **TC-F9** — a link `out.js` to a file outside the scanned root, holding a secret pattern → the
  secrets scan skips and counts it, stderr names `outside the scanned root`, and no finding holds
  the pattern.
- **TC-F4** — `AuditTestCase`'s `PATH` holds exactly the fake `bin`, `/usr/bin` and `/bin`.
- **TC-F5** — `printable` of a backslash, and of the text `\x0a`, doubles the backslash; an escape
  character still becomes `\x1b`.
- **TC-F6** — with `os.O_BINARY` and `os.O_NOCTTY` patched in, `os.open` receives both flags.
- **TC-F7** — 1,000 calls on a link to `/dev/null` each raise `not a regular file`, and the
  count of open descriptors is the same before and after.
- **TC-F8** — a file above a patched `MAX_FILE_SIZE` raises `exceeds the size limit`; the stream
  of a regular file has `O_NONBLOCK` cleared.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — TC-F1 and TC-F2 pass; the base fails both by their timeout.
- **A2** — TC-F3 passes on the base and after the change; TC-F9 passes after it.
- **A3** — TC-F4 passes.
- **A4** — TC-F5 passes.
- **A5** — the documents and records of R4 to R6 hold the stated text.
- **A6** — after stage 3, `python3 tests/run_tests.py`, the CI steps and the skill's tests pass.

<!-- contract:decisions -->

## 6. Decisions

- **D1**, 2026-10-09, orchestrator: `/framework-upgrade`, not `/light`. Rejected: `/light` — its
  `light-mode` criteria exclude edits to files that match `security*`.
- **D2**, 2026-10-09, orchestrator: no version bump of `security-audit`; v3.40.1 records the fix.
  Rejected: 3.12.1 — the bump changes the `SKILLS.md` row that `tests/test_run_safety_rules.py`
  pins whole, and a fourth staged file for a patch release.
- **D4**, 2026-10-09, orchestrator, on stage-2 round 1:
  - fixed in this task: the code review's MAJOR and MINOR items, LOW-1, `O_NOCTTY`, `O_NONBLOCK`;
  - MEDIUM-1: D6 fixes it in this task;
  - `printable`'s Zs and Mn characters and the unescaped `{e}` stay, as INFO.
- **D5**, 2026-10-09, operator: the task holds WI-51 and the review findings in the lines it
  changes; every other finding is one line in the audit record; a new backlog record needs the
  operator's decision. Rejected: fixing every finding in this task.
- **D6**, 2026-10-09, operator: a file whose real path leaves the scanned root is skipped (R1.1,
  R1.3). Rejected: a stated limitation.
- **D7**, 2026-10-09, operator: no record for the `mcp-scan` target; §2 states it (R6.3).
  Rejected: removing the fallback — `external.py` is outside the boundary of D5.
- **D3**, 2026-10-09, orchestrator, per the operator's "старайся не раздувать задач": two routes
  of WI-51 leave this task, the wrapper's positive exit code and the `mcp-scan` target (R6.2).

<!-- contract:out-of-scope -->

## 7. Out of scope

- The wrapper's positive exit code (D13 of TASK 118).
- The `mcp-scan` target (D7).
- WI-49 and WI-50.
