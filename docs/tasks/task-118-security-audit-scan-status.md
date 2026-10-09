# TASK 118 — The security-audit scan reports for each tool whether it ran, reports npm advisories at every severity, and scans the working tree for secrets

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 118 |
| Slug | security-audit-scan-status |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | [WI-42](../backlog/wi-42-security-audit-scans-hide-what-did-not-run.md); the operator's request of 2026-10-09; D1 to D4 |
| Base revision | `e1fb36200ff474957611497f1d0826c51499d31a` |
| Closes | WI-42 |
| Archive name | `task-118-security-audit-scan-status.md` |
| Revision | 7: stage-2 fix round 2 (D17 to D19); revision 6 per fix round 1 (D11 to D16) |

**Records.**

- [WI-42](../backlog/wi-42-security-audit-scans-hide-what-did-not-run.md), O-1 to O-4
- [WI-37](../backlog/wi-37-external-scanners-that-run-the-scanned-projects-code.md) (dropped), a
  different class: scanners that run the scanned project's code
- [TASK 111](task-111-checks-that-cover-what-they-claim.md), R5: the npm audit of each
  lockfile
- [TASK 116](task-116-archive-hardening-and-git-deny-rules.md), R6: the staging of modules
  that `tests/run_tests.py` imports
- [TASK 115 audit](../reviews/framework-audit-115.md), stage 2 and stage 4: the two `INCOMPLETE`
  audits

<!-- contract:problem -->

## 1. Problem

`security-audit` runs two layers: in-process regex scans and external tools. Its script
`run_audit.py` hides four states. Each was observed on 2026-10-08 (TASK 115).

1. **O-1.** `scan_dependencies` yields a finding only for critical and high npm advisories
   (`.agent/skills/security-audit/scripts/audit/scanners.py:89@e1fb362` `severity_count = {"critical": 0, "high": 0}`).
   `--scan-type deps --output json` reported 0 findings; `npm audit` reported 14 low entries.
   `tests/test_lockfile_audit.py:275@e1fb362` `test_l23_a_moderate_advisory_is_no_finding` pins this
   behaviour.
2. **O-2.** `run_external_tools` returns nothing
   (`.agent/skills/security-audit/scripts/audit/external.py:31@e1fb362` `def run_external_tools`).
   - A missing tool prints two lines to stderr; a non-zero exit prints one line to stderr.
   - `run_audit.py` exits 0 in both cases, also with `--fail-on`.
   - `--scan-type external` prints no report at all.
   - The tools write to stdout after the JSON document, so `--scan-type all --output json`
     prints no single JSON document.
3. **O-3.** gitleaks runs without `--no-git`
   (`.agent/skills/security-audit/scripts/audit/external.py:50@e1fb362` `["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]`).
   In git mode gitleaks reads the committed history; an uncommitted file is not scanned.
4. **O-4.** semgrep, gitleaks, trufflehog, bandit and pip-audit are not installed on the
   operator's machine. Both audits of TASK 115 ended `INCOMPLETE` for that cause (D11 of TASK 115).
   No document states which tools a complete run needs.

Six further facts bear on the design:

- `run_audit.py` starts no external tool when `detect_project_types` returns no type
  (`.agent/skills/security-audit/scripts/run_audit.py:187@e1fb362` `if types:`). A project of `.tsx`
  files or of documents only has no type.
- trufflehog exits 0 on a finding unless `--fail` is given; trivy exits 0 unless `--exit-code`
  is given.
- `npm audit` exits non-zero on an advisory of any severity unless `--audit-level` is given.
  This repository's 14 low advisories make the external `npm audit` exit non-zero.
- `run_audit.py` cuts each section to 30 findings before it counts the summary
  (`.agent/skills/security-audit/scripts/run_audit.py:73@e1fb362` `if len(result.get("findings", [])) > max_findings:`).
  The deps scan does not sort its findings, so the cut can drop a critical one.
- `run_audit.py` prints the `--fail-on` message `[GATE] …` to stdout, after the JSON document.
- The deps scan marks an unaudited lockfile with severity `info`
  (`.agent/skills/security-audit/scripts/audit/scanners.py:163@e1fb362` `sum(1 for f in found if f["severity"] == "info")`).
  npm also has an `info` advisory severity, so O-1's fix cannot count by that marker.

**Why.** A gate reads the exit code and the JSON. Today both show "complete, no finding" for a
scan in which no external tool ran.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The external layer reports one record per tool (O-2) | Y | R1.1–R1.10 | A1, A2, A3, A11, A14 |
| R2 | The exit code and the summary show a part not run and a tool's non-zero exit (O-2, D1, D2) | Y | R2.1–R2.10 | A1, A4, A5, A12 |
| R3 | The deps scan reports npm advisories at every severity (O-1, D3) | Y | R3.1–R3.7 | A6, A7 |
| R4 | The secret scan covers the working tree and the history (O-3) | Y | R4.1–R4.5 | A8 |
| R5 | `security-audit` and the auditor prompts state the toolset, the exit codes and their mapping (O-4, D4) | Y | R5.1–R5.8 | A9 |
| R6 | Version, documents and records | Y | R6.1–R6.6 | A10 |
| R7 | Staging (`framework-upgrade` §3 step 4) | Y | R7.1–R7.11 | A10, A13 |

## 3. Definitions

- **Scanned root** is the `project_path` argument of `run_audit.py`.
- **Tool record** is a JSON object that describes one external tool the scanner started or
  declined to start.
- **Slot** is the scan function that one tool fills: for example `sast` or `secrets-tree`. A
  fallback tool fills the slot of the tool it replaces.
- **Selected slot** is a slot that holds at least one tool record.
- **Record status** is one of six values:
  - `ran` — the process ended on its own; `exit_code` holds its exit code;
  - `killed` — a signal ended the process; `exit_code` holds the negative code that Python
    reports (D13);
  - `not_installed` — the executable was not found;
  - `timed_out` — the process ran past its timeout and was stopped;
  - `not_run` — the scanner did not start the tool, for a stated `reason`, and the slot's input
    stays unscanned;
  - `not_applicable` — the scanned root holds no input for the slot, for a stated `reason`.
- **Part not run** is either of:
  - a selected slot with no `ran` record and no `not_applicable` record; a `killed` record does
    not complete its slot;
  - a dependency finding with `"audited": false`.
- **Requested part** is a part that `--scan-type` selects: every in-process scan for `all`, one
  for its own type, the external layer for `all` and `external`.
- **Staged name** is the name under which stage 1 of `framework-upgrade` §3 step 4 holds the new
  text of a file (R7.1).

<!-- contract:requirements -->

## 4. Requirements

### R1 — One record per external tool (O-2)

- **R1.1** `run_external_tools` returns a list of tool records. Each record holds the keys
  `slot`, `tool`, `command`, `where`, `status`, `exit_code` and `reason`.
  - `tool` is `command[0]`.
  - `command` is the argument list as started; for `not_run`, the list that would have started.
  - `where` is `.` for the scanned root, `yarn.lock` for yarn, and the lockfile's path relative
    to the scanned root, with `/` separators, for npm.
  - `exit_code` is an integer for `ran` and `killed`, and `null` otherwise.
  - `reason` is a string for `not_run` and `not_applicable`, and `null` otherwise.
- **R1.2** Every tool that the base starts gets one record. The slots:

  | Slot | Tools, first to fallback | Selected for |
  | :--- | :--- | :--- |
  | `sast` | semgrep | every scan (R1.4) |
  | `secrets-tree` | gitleaks, trufflehog | every scan (R1.4) |
  | `secrets-history` | gitleaks | every scan (R1.4, R4.2) |
  | `solidity` | slither | type solidity |
  | `python-sast` | bandit | type python |
  | `python-deps` | pip-audit | type python |
  | `npm-audit:<where>` | npm | each npm lockfile |
  | `yarn-audit` | yarn | type javascript, with a root `yarn.lock` |
  | `rust-deps`, `rust-lint` | cargo audit, cargo clippy | type rust |
  | `go-deps`, `go-sast` | govulncheck, gosec | type go |
  | `iac`, `iac-misconfig` | checkov, trivy | type iac |
  | `mcp` | snyk-agent-scan, mcp-scan | type mcp |

- **R1.3** The records follow the base's order of calls. A fallback record follows the record of
  the tool it replaces.
- **R1.4** `run_audit.py` calls `run_external_tools` for the scan types `all` and `external`, also
  when `detect_project_types` returns no type.
- **R1.5** A fallback tool starts only when the first tool's status is `not_installed` or
  `timed_out`, as in the base. A fallback that does not start gets no record.
- **R1.6** A lockfile or `yarn.lock` that the base skips gets a `not_run` record. Its `reason` is
  one of the texts the base prints:
  - `no package.json beside it` (npm);
  - `yarn.lock is a link or not a regular file`;
  - `no package.json beside yarn.lock`;
  - `package.json is not a JSON object`;
  - `the lockfile could not be copied`, for npm and yarn: a copy that raises `OSError`, such as
    a lockfile that is a FIFO (D16).
- **R1.7** The external section is the object `{"status": <value>, "tools": [<records>]}`. The
  first match sets `status`:
  1. `NOT_RUN` when no record has the status `ran`;
  2. `COMPLETE` when every selected slot has a `ran` record or a `not_applicable` record;
  3. `PARTIAL` otherwise.
- **R1.8** The report holds the external section under the key `external` for the scan types
  `all` and `external`. For `--scan-type external` the report holds an empty `scans` object.
  `--output summary` prints one line per record: slot, tool, status, and the exit code or the
  reason.
- **R1.9** A tool's stdout and stderr go to the scanner's file descriptor 2. With
  `--output json`, stdout holds exactly one JSON document. `run_audit.py` prints the report after
  the external tools have ended.

- **R1.10** The scanner's own lines print text from the scanned tree escaped, to stderr and in
  `--output summary`. Such text is, for example, a lockfile's path or an npm message. Each
  character of the Unicode categories Cc, Cf, Zl and Zp becomes `\xNN`, `\uNNNN` or
  `\UNNNNNNNN`. `--output json` keeps the escaping of `json.dumps` (D16). The external tools' own
  output reaches stderr unescaped.
### R2 — Exit code and summary (O-2, D1, D2)

- **R2.1** `summary.not_run` is a list with one string per part not run:
  - `external <slot>: <tool> <status>` for a slot, naming its last record;
    `, <reason>` follows for `not_run`;
  - `dependencies: <message>` for a dependency finding with `"audited": false`.
- **R2.2** `summary.scan_complete` is `true` when `summary.not_run` is empty, and `false`
  otherwise.
- **R2.3** `summary.tool_exits` is a list with one string `<tool> exited <N> (<slot>)` per `ran`
  record whose `exit_code` is not 0.
- **R2.4** `summary` holds the keys `total_findings`, `critical`, `high`, `medium`, `low`,
  `info`, `not_run`, `scan_complete`, `tool_exits` and `overall_status` for every scan type.
- **R2.5** The summary, `summary.not_run` and the `--fail-on` gate count every finding.
  Truncation to 30 findings per section applies to the printed and returned lists afterwards.
- **R2.6** With `--fail-on`, `run_audit.py` exits 1 when either holds:
  - an in-process finding has the threshold's severity or a higher one (the base's rule);
  - `summary.tool_exits` is not empty (D2).
- **R2.7** Otherwise `run_audit.py` exits 3 when `summary.scan_complete` is `false`, with or
  without `--fail-on` (D1). Otherwise it exits 0.
- **R2.8** Exit 1 prints `[GATE] --fail-on <level>:` on stderr, followed by each cause:
  `<N> <severity> finding(s)` and each entry of `summary.tool_exits`. A non-empty
  `summary.not_run` prints `[INCOMPLETE]` on stderr, followed by each entry: on exit 3, and on
  exit 1 after the `[GATE]` lines.
- **R2.9** `summary.overall_status`, first match wins:
  1. a critical finding → `[!!] CRITICAL ISSUES FOUND`;
  2. a high finding → `[!] HIGH RISK ISSUES`;
  3. `summary.scan_complete` is `false` → `[?] INCOMPLETE: <N> part(s) did not run`;
  4. a finding, or a non-empty `summary.tool_exits` → `[?] REVIEW RECOMMENDED`;
  5. otherwise `[OK] SECURE`.
- **R2.10** Tool options that make a finding exit non-zero:
  - trufflehog runs with `--fail`;
  - trivy runs with `--exit-code 1`;
  - with `--fail-on`, npm runs with `--audit-level=<level>`: `critical`, `high`, or `moderate`
    for `medium`. Without `--fail-on`, npm runs without it.

  yarn runs as in the base, and its non-zero exit counts under R2.6.

**Why.** R2.10: trufflehog and trivy exit 0 on a finding by default, so R2.6 would not see their
findings. npm's `--audit-level` sets the lowest severity that makes `npm audit` exit non-zero, so
npm's exit follows the gate's threshold.

**Unchanged.** A missing directory and a non-positive `--max-size` exit 1 with a JSON error, as in
the base. argparse exits 2 on a usage error. yarn's exit is used as it is.

### R3 — npm advisories at every severity (O-1, D3)

- **R3.1** A finished `npm audit` yields one finding per npm severity whose count is not 0. The
  npm severity maps to the scanner's severity:

  | npm | scanner |
  | :--- | :--- |
  | `critical` | `critical` |
  | `high` | `high` |
  | `moderate` | `medium` |
  | `low` | `low` |
  | `info` | `info` |

  The message stays `<lockfile>: <N> <npm severity> vulnerabilities in dependencies`.
- **R3.2** An entry that is not a map, or holds no `severity`, counts as `low`, as in the base. A
  `severity` string outside the five counts as `unknown`. A non-zero `unknown` count yields one
  finding of severity `low` with the message `<lockfile>: <N> vulnerabilities of unknown severity`.
- **R3.3** The dependency section holds `npm_audit_counts`: a map from the lockfile's relative
  path to its counts `critical`, `high`, `moderate`, `low`, `info` and `unknown`. Each finished
  audit has one entry, also with every count at 0.
- **R3.4** A not-audited finding keeps the severity `info` and carries `"audited": false`. The
  section counts unaudited lockfiles by that key, not by the severity. A lockfile whose copy
  raises `OSError` is not audited, reason `the lockfile could not be copied` (D16).
- **R3.5** The section status, first match wins:
  1. a critical finding → `[!!] Critical vulnerabilities`;
  2. a high finding → `[!] HIGH: Dependency issues`;
  3. an unaudited lockfile → `[?] Not audited: <N> npm lockfile(s)`;
  4. a medium or low finding → `[?] Dependency issues below high`;
  5. otherwise `[OK] Secure`.
- **R3.6** The deps scan sorts its findings by severity, critical first.
- **R3.7** `--output summary` prints the five severity counts.

`summary.info` counts the not-audited markers and npm `info` advisories together.

### R4 — Secret scan of the working tree and the history (O-3)

- **R4.1** Slot `secrets-tree` runs `gitleaks detect --no-banner --redact --no-git -s .`. Its
  fallback runs `trufflehog filesystem --no-update --fail .`.
- **R4.2** Slot `secrets-history` looks for `.git` with `os.lstat`, in `os.path.realpath` of the
  scanned root and then in each parent directory up to the filesystem root. The walk is a function
  with a stop directory; `run_external_tools` passes none, and a test passes its temporary
  directory. At each directory, a `.git` entry is checked first, then whether the directory is
  itself a bare repository: a regular `HEAD` file and the directories `objects` and `refs`, none
  of them a link. The first match decides:
  - a `.git` directory or regular file, or a bare repository → `gitleaks detect --no-banner
    --redact -s .`, started in the scanned root, as in the base (D11, D15);
  - a symbolic link → one `not_run` record, reason `.git is a symbolic link`;
  - any other file type → one `not_run` record, reason `.git is not a directory or a regular file`;
  - an `lstat` that raises an error other than "not found" → one `not_run` record, reason
    `.git could not be read`;
  - a directory whose `HEAD`, `objects` and `refs` exist, one of them a link → one `not_run`
    record, reason `the bare repository holds a symbolic link` (D19);
  - no match on the whole path → one `not_applicable` record, reason `no .git at or above the
    scanned root`.
- **R4.3** Slot `secrets-history` has no fallback. gitleaks missing or timed out leaves it a part
  not run.
- **R4.4** The `not_run` and `not_applicable` records of R4.2 name gitleaks and its git-mode
  command.
- **R4.5** `secrets-tree` runs before `secrets-history`.

**Why.**

- gitleaks documents `--no-git` as "treat git repo as a regular directory and scan those files"
  (`cmd/detect.go`, read 2026-10-09). `detect` is hidden since gitleaks 8.19.0 and still runs;
  `dir` and `git` exist only from 8.19.0.
- R4.2 looks above the scanned root because the base's git mode, started in a subdirectory, read
  the history of the enclosing repository. `vdd-multi` scans a subdirectory scope.
- R4.3: `trufflehog git` executed a command that a scanned repository's `.git/config` names in
  `core.fsmonitor` (CVE-2025-41390, CVSS 7.8, TruffleHog 3.90.2; Talos TALOS-2025-2243). A
  history fallback through it would add that route to an audit of an untrusted tree (D7).

### R5 — Where the external layer runs, and how an auditor reads it (O-4, D4)

- **R5.1** `security-audit` §2 holds the slot table of R1.2, and the external-tools bullets name
  the options of R2.10 and R4.
- **R5.2** §2 states that a complete local run needs, per selected slot, one installed tool that
  finishes within 600 s; a `not_applicable` slot needs none.
- **R5.3** §2 names an install command for semgrep, gitleaks, trufflehog, bandit and pip-audit.
  It states that trufflehog runs in `filesystem` mode only, and cites CVE-2025-41390 as the reason
  that no slot runs `trufflehog git`.
- **R5.4** §2 states the exit codes 0, 1 and 3, exit 1 with a JSON `error` for a missing
  directory or a non-positive `--max-size`, and argparse's exit 2. It states `summary.not_run`,
  `summary.tool_exits`, the external section's status, and the severity mapping of R3.1.
- **R5.5** A new block, outside every block that `tests/test_run_safety_rules.py` pins, states in
  `.claude/agents/security-auditor.md`, `System/Agents/10_security_auditor.md` and step 2 of
  `.agent/workflows/security-audit.md`:
  - exit 3, or a `summary.not_run` that is not empty, sets `scan_status: "NOT_RUN"`;
  - a `summary.tool_exits` that is not empty sets at least `scan_status: "findings"`;
  - a non-zero tool exit is a finding or an error, and an error that the tool's output shows sets
    `scan_status: "NOT_RUN"` (D13);
  - a run that prints no report, such as exit 1 with a JSON `error` or exit 2, sets
    `scan_status: "NOT_RUN"`.
- **R5.6** `.agent/skills/security-audit/examples/usage_example.md` shows the summary output of
  R2.4 and R1.8.
- **R5.7** No CI job runs the external layer (D4).
- **R5.8** §2 states three exposures that this task keeps:
  - git mode runs git in the scanned tree's `.git`, whose configuration can name commands that git
    runs; an untrusted tree's history belongs in an isolated environment (D11);
  - `cargo clippy`, `slither` and `checkov` can execute the scanned project's code or
    configuration (D12, WI-37);
  - the scanned tree can hold configuration files that the tools read, such as `.gitleaks.toml`,
    `.gitleaksignore`, `.semgrepignore` and `.trivyignore`, and that can silence them (D14).

### R6 — Version, documents and records

- **R6.1** `security-audit` becomes 3.12 in `__init__.py` `__version__`, the `SKILL.md`
  frontmatter and title, the `run_audit.py` header, the `security-audit` row of
  `System/Docs/SKILLS.md` and `System/Docs/VDD.md`. `tests/test_disclosure_rule.py`
  `TestVersionMirrors` requires the four documents to carry one version, so they change in the
  stage-3 edit (R7.6).
- **R6.2** `CHANGELOG.md` and `CHANGELOG.ru.md` get the entry v3.40.0. For an installing
  repository it names each behaviour change:
  - exit 3 for a part not run, and the `[INCOMPLETE]` line;
  - exit 1 under `--fail-on` for a tool's non-zero exit, pip-audit's included;
  - npm's `--audit-level` under `--fail-on`;
  - yarn's exit, which is not ranked: under `--fail-on`, an advisory of any severity gives exit 1;
  - findings and statuses for medium, low and info npm advisories; `--fail-on medium` fails on a
    moderate advisory;
  - the `[GATE]` line and the tools' output on stderr;
  - the report of `--scan-type external`, and the new JSON keys;
  - the working-tree secret scan, which reads ignored files such as `.env`;
  - the history scan, which needs gitleaks, looks for `.git` or a bare repository at and above
    the scanned root, and has no trufflehog fallback;
  - a tool killed by a signal is a part not run;
  - the external layer for a project with no detected type.
- **R6.3** WI-42 gets `status: done`, `resolved_at: 2026-10-09`, `resolved_by: TASK 118` and a
  resolution blockquote; its line in `docs/BACKLOG.md` says `done`.
- **R6.4** `docs/reviews/framework-audit-118.md` holds the audit record of this run.
- **R6.5** The docstrings of the two edited test modules list the new test ids.
- **R6.6** Three work-items are filed in `docs/backlog/` with their index lines
  (`known-issues-format`):
  - WI-49, an isolated history scan of an untrusted tree (D11);
  - WI-50, scanner configuration files in the scanned tree (D14);
  - WI-51, the residual routes of stage 2: a FIFO in the other in-process scans, a wrapper's
    positive exit code, the `mcp-scan` target, a test helper's `PATH` (D18).

### R7 — Staging (`framework-upgrade` §3 step 4)

`tests/run_tests.py` is named by a committed allow rule. It imports `test_lockfile_audit` and
`test_run_safety_rules`, and the first loads the scanner package. These files are therefore
code of §3 step 4's list.

- **R7.1** Stage 1 writes the new text of each file under a staged name:

  | Final path | Staged name |
  | :--- | :--- |
  | `.agent/skills/security-audit/scripts/audit/__init__.py` | `…/audit/init_next.py` |
  | `.agent/skills/security-audit/scripts/audit/helpers.py` | `…/audit/helpers_next.py` |
  | `.agent/skills/security-audit/scripts/audit/scanners.py` | `…/audit/scanners_next.py` |
  | `.agent/skills/security-audit/scripts/audit/external.py` | `…/audit/external_next.py` |
  | `.agent/skills/security-audit/scripts/run_audit.py` | `…/scripts/run_audit_next.py` |
  | `tests/test_lockfile_audit.py` | `tests/staged_lockfile_audit.py` |
  | `tests/test_run_safety_rules.py` | `tests/staged_run_safety_rules.py` |

  - No allow rule, hook or listed script names or imports a staged name.
  - pytest's default patterns `test_*.py` and `*_test.py` match no staged name, and the repository
    holds no pytest configuration that adds one.
  - `audit/config.py` and `audit/patterns.py` are not edited.
- **R7.2** The text under a staged name is the final text. Stage 3 renames it over its final
  path unchanged; the SHA-256 of each staged file equals that of its final file.
- **R7.3** A driver in the session's scratchpad runs the staged test modules. The command asks
  for approval; no rule names it. It has two modes:
  - `next` runs them against the staged code;
  - `base` runs them against the base code.
- **R7.4** The staged code reaches the tests through three routes:
  - **Package.** `_load()` of the lockfile test module keeps its rule: it uses the package that
    `sys.modules` holds under its name. Mode `next` registers that name, then `.helpers`,
    `.scanners` and `.external` from the staged files, then runs `init_next.py` as the package.
    This happens before the test module is imported.
  - **In-process `run_audit`.** A module attribute holds the path of `run_audit.py`. A test reads
    it at call time and loads that file while `sys.modules["audit"]` names the package under
    test, so its `from audit import` reaches that package. Mode `next` sets the path to
    `run_audit_next.py` after the import.
  - **Subprocess.** A module attribute holds the command that the subprocess tests start. Mode
    `next` sets it to a bootstrap that registers the staged package as `audit` and runs
    `run_audit_next.py` as `__main__`.

  Mode `next` asserts that each registered module's `__file__` is its staged file, and that the
  loaded `run_audit_next.py` holds the staged `run_external_tools` and `scan_dependencies`. It stops
  otherwise.
- **R7.5** The base-fail run is mode `base`. Each new test fails or errors on the base, or the
  audit record names why it passes.
- **R7.6** Stage 3, after §4.5, is one edit:
  - the seven renames of R7.1;
  - the version 3.12 in the `SKILL.md` frontmatter and title, the `security-audit` row of
    `System/Docs/SKILLS.md` and `System/Docs/VDD.md` (R6.1);
  - the per-tool scan status in that `SKILLS.md` row (`framework-upgrade` §4.2). The base test
    pins the row whole, so the row changes once, in this edit.

  The gates run again after it: `python3 tests/run_tests.py`, the pytest list of CI, the skill
  validators, and `check_positional_refs.py --all docs/*.md docs/issues docs/backlog`, the
  living-corpus step of CI. No registration exists, so no settings test is added.
- **R7.7** No final path of R7.1 and no version string of R7.6 changes before stage 3, so
  `tests/run_tests.py` runs base code against base pins until then. Every other edit lands before
  stage 3, the §2 text of `security-audit` included.
- **R7.8** The audit record holds the stage-3 diff, and the SHA-256 of each staged file. The
  Failure rule of §3 step 4 applies as written:
  1. failed gates of stage 3, or a focused review that does not pass → the run restores every
     file of R7.6 to its text before the edit, the staged files included;
  2. an `INCOMPLETE` security audit as the only failure → `security-audit` §6.2 governs the re-run,
     which reads the recorded diff; a passing re-run re-applies the same diff for stage 4;
  3. every other case → the operator decides.
- **R7.9** Stage 2 is one code review and one security audit of the staged code, the tests and
  this TASK, at one fingerprint. The bound is 3 rounds (`stage2-review-retry`). Stage 4 is a code
  review and a security audit of the stage-3 diff on the new fingerprint.
- **R7.10** A security audit that ends `INCOMPLETE` because the external tools are missing
  follows `security-audit` §6.2: one re-run of the unfinished part in the run, then the operator's
  decision, quoted in the audit record. The question to the operator at stage 2 also asks whether
  the decision covers stage 4 for the same part and the same cause. Covered means: after the
  restore of the Failure rule, the same patch, by SHA-256, is applied again, the stage-3 gates
  run, and stage 4 is not repeated.
- **R7.11** If stage 3 is restored, or the run stops before it, the audit record lists under
  `Pending after restore` each edit that landed before stage 3 and describes the new behaviour:
  - the §2 text of `security-audit` (R5.1 to R5.4);
  - the three blocks of R5.5;
  - `examples/usage_example.md` (R5.6);
  - the CHANGELOG entries (R6.2);
  - WI-42 and its `docs/BACKLOG.md` line (R6.3).

  The operator decides on each.

<!-- contract:use-cases -->

## 5. Use cases

### UC-1 — An audit without the external tools (modified)

**Actors:** the security auditor (an agent), `run_audit.py`.

**Preconditions:** semgrep, gitleaks, trufflehog, bandit and pip-audit are not installed.

**Main scenario:**

1. The auditor runs `run_audit.py . --scan-type all --output json`.
2. The in-process scans run, as in the base.
3. The external layer records `not_installed` for each missing tool.
4. The scanner prints one JSON document. `external.status` is `NOT_RUN` or `PARTIAL`, and
   `summary.not_run` names each slot.
5. The scanner prints `[INCOMPLETE]` and the parts on stderr, and exits 3.
6. The auditor sets `scan_status: "NOT_RUN"` and the verdict `INCOMPLETE`, or `FAIL` on a
   CRITICAL or HIGH finding of the manual review (`security-audit` §6.2).

**Alternative A — a `--fail-on` breach:** an in-process finding meets the threshold. The scanner
exits 1, and `summary.not_run` still names each slot.

**Postconditions:** the report names each part not run; the exit code is 1 or 3.

### UC-2 — A CI gate with every tool installed (modified)

**Actors:** a CI job, `run_audit.py`.

**Preconditions:** each selected slot's first tool is installed.

**Main scenario:**

1. CI runs `run_audit.py . --fail-on high`.
2. Every selected slot records `ran`.
3. bandit exits 1. `summary.tool_exits` holds `bandit exited 1 (python-sast)`.
4. The scanner prints the `[GATE]` line with that entry on stderr, and exits 1.

**Alternative A — no tool exits non-zero and no finding meets the threshold:** the scanner exits 0.

**Postconditions:** the job's result follows the exit code.

### UC-3 — A moderate npm advisory (modified)

**Actors:** an operator, `run_audit.py`.

**Preconditions:** `npm audit` reports one moderate entry for `sub/package-lock.json`.

**Main scenario:**

1. The operator runs `run_audit.py . --scan-type deps --fail-on medium`.
2. The deps scan yields a `medium` finding and `npm_audit_counts["sub/package-lock.json"]`.
3. The scanner exits 1. With `--fail-on high` it exits 0.

**Postconditions:** the finding is in the report at both thresholds.

### UC-4 — An uncommitted secret (modified)

**Actors:** an operator, `run_audit.py`, gitleaks.

**Preconditions:** a secret stands in a file that git does not track; gitleaks is installed.

**Main scenario:**

1. The operator runs `run_audit.py . --scan-type external`.
2. Slot `secrets-tree` runs gitleaks with `--no-git`, which reads the file.

**Postconditions:** gitleaks reports the secret and exits non-zero; `summary.tool_exits` names
it.

<!-- contract:acceptance -->

## 6. Acceptance criteria

- **A1** — `--scan-type external`, every tool missing, no `.git`: each record is
  `not_installed` or `not_applicable`, `external.status` is `NOT_RUN`, and the exit code is 3.
- **A2** — `--output json`, a fake tool that prints to stdout: stdout parses as one JSON
  document.
- **A3** — gitleaks missing and trufflehog present: slot `secrets-tree` is complete.
- **A4** — `--fail-on critical` and a tool that exits 1: the exit code is 1.
- **A5** — the overall status is never `[OK] SECURE` while `summary.scan_complete` is `false` or
  `summary.tool_exits` is not empty.
- **A6** — a low, a moderate and an info advisory: three findings, of severity `low`, `medium`
  and `info`, and `npm_audit_counts` holds the six counts.
- **A7** — `--scan-type deps`, npm missing: the exit code is 3, and `summary.not_run` names the
  lockfile.
- **A8** — the `secrets-tree` command holds `--no-git`; with no `.git` at or above the scanned
  root, `secrets-history` is `not_applicable`; with one in a parent, gitleaks runs in git mode.
- **A9** — `security-audit` §2 holds the slot table, the install commands and the exit codes; the
  three routers of R5.5 hold the mapping.
- **A10** — after stage 3, `python3 tests/run_tests.py`, the pytest list of CI and the skill
  validators pass.
- **A11** — a project with no detected type: the external section holds the three slots of every
  scan.
- **A12** — a section of 31 findings with the critical one last: the summary counts all 31, and
  `--fail-on critical` exits 1.
- **A13** — the base-fail run shows each new test failing on the base, or the audit names why it
  passes.
- **A14** — three properties hold:
  - in the dependency scan and the external layer, a FIFO lockfile gives a part not run, never a
    crash;
  - a killed tool never completes its slot;
  - tree text is escaped in the scanner's own printed lines.

<!-- contract:tests -->

## 7. Test obligations

The new tests go into the staged test modules of R7.1.

- **Fake tools.** A fake tool is a `/bin/sh` script in a temporary `bin` directory. A new test
  sets `PATH` to that directory only, so a tool installed on the runner does not start. A fake
  tool calls other programs by absolute path, and a sleeping one runs `exec /bin/sleep`.
- **Two kinds of test.** A test of `run_external_tools` runs in process. A test of stdout or
  stderr starts the command of R7.4 as a subprocess. A test of an exit code does either.

The cases:

- **TC-E1** — `--scan-type external`, no tool, no `.git` → every record `not_installed` or
  `not_applicable`, `external.status` `NOT_RUN`, exit 3; fails when the records are ignored.
- **TC-E2** — fake semgrep exits 0 → record `ran`, `exit_code` 0.
- **TC-E3** — every selected slot's tool exits 0 but bandit exits 1:
  - `--fail-on critical` → exit 1, the `[GATE]` line names `bandit exited 1 (python-sast)`;
  - no `--fail-on` → exit 0, `summary.tool_exits` lists bandit.
- **TC-E4** — fake gitleaks sleeps past a patched timeout. The timeout is a constant of the
  helpers module, read at each call:
  - slot `secrets-tree`: record `timed_out`, then trufflehog starts;
  - slot `secrets-history`: record `timed_out`, no fallback, a part not run.
- **TC-E5** — gitleaks missing, fake trufflehog exits 0, a `.git` directory → `secrets-tree`
  complete; `secrets-history` is a part not run; no trufflehog record has slot `secrets-history`.
- **TC-E6** — the history slot by `.git` and a bare repository, each case on a temporary root:
  - no `.git` between the root and the test's stop directory → `not_applicable`;
  - the scanned root given through a symbolic link to a directory below a `.git` → git mode;
  - a `.git` directory at the root, a `.git` file at the root, a `.git` directory in the parent →
    gitleaks runs in git mode, started in the scanned root;
  - a `.git` link → `not_run`; a `.git` FIFO → `not_run`;
  - a bare repository at the root → git mode; one whose `objects` is a link → `bare-link`;
  - at the record level, each declined kind (`link`, `other`, `unreadable`, `bare-link`, none)
    gives its status, its reason and the git-mode command;
  - at the record level, a `.git` file at the root gives a `ran` record of the git-mode command,
    started in the scanned root. So does a `.git` directory in the parent. The case fails when
    only a directory starts git mode.
- **TC-E7** — the `secrets-tree` command is
  `gitleaks detect --no-banner --redact --no-git -s .`.
- **TC-E8** — fake tools print to stdout, `--output json --fail-on critical` → stdout parses as
  one JSON document; the `[GATE]` line is on stderr.
- **TC-E9** — the trufflehog command holds `--fail`; the trivy command holds `--exit-code 1`; npm
  holds `--audit-level=moderate` under `--fail-on medium` and no `--audit-level` without it.
- **TC-E10** — a `--fail-on` breach and a part not run → exit 1, `summary.not_run` names the
  part, and stderr holds the `[GATE]` line.
- **TC-E11** — `--scan-type deps`, npm missing → exit 3; `summary.not_run` names the lockfile;
  stderr holds `[INCOMPLETE]`.
- **TC-E12** — a part not run, no critical or high finding → `overall_status` starts with
  `[?] INCOMPLETE`; a tool exit and nothing else → `[?] REVIEW RECOMMENDED`.
- **TC-E13** — external layer, one case per reason of R1.6 → record `not_run` with that reason;
  the scan is not complete:
  - a lockfile without `package.json`;
  - a `yarn.lock` link;
  - a `yarn.lock` without `package.json`;
  - a `package.json` that is not a JSON object.
- **TC-E14** — `--output summary` prints one line per record.
- **TC-E15** — no detected type → the slots `sast`, `secrets-tree`, `secrets-history` hold
  records.
- **TC-E16** — the external section's status: every slot `ran` → `COMPLETE`; one slot
  `not_installed` and one `ran` → `PARTIAL`.
- **TC-E17** — in process, a stub scanner returns 31 unsorted findings, one critical last:
  - `total_findings` is 31 and `critical` is 1;
  - the exit code under `--fail-on critical` is 1;
  - the returned list holds 30 entries.

  It fails when the summary is counted after the cut.
- **TC-D1** (replaces TC-L23) — moderate, low and info advisories → findings `medium`, `low`,
  `info`; fails when the critical-and-high filter returns.
- **TC-D2** — a moderate advisory, `--scan-type deps`: `--fail-on medium` → exit 1;
  `--fail-on high` → exit 0.
- **TC-D3** — an npm `info` advisory → the status is not `Not audited`; an unaudited lockfile →
  severity `info` and `"audited": false`.
- **TC-D4** — a severity outside the five → count `unknown` and one `low` finding; an entry that
  is not a map → count `low`.
- **TC-D5** — `npm_audit_counts` holds an entry with all six counts for a finished audit, also
  when every count is 0.
- **TC-D6** — the section status follows R3.5, one case per row, and an info-only advisory gives
  `[OK] Secure`.
- **TC-D7** — `summary` counts `low` and `info`; with two lockfiles that each report a low and a
  critical advisory, the deps findings are sorted, critical first; fails when the sort is removed.
- **TC-D8** — a lockfile that is a FIFO, `--scan-type deps` → a not-audited finding with reason
  `the lockfile could not be copied`, one JSON document, exit 3.
- **TC-E18** — a fake tool that kills itself with a signal → record `killed` with a negative
  `exit_code`; the slot is a part not run.
- **TC-E19** — a lockfile directory whose name holds an escape character → stderr and the summary
  output hold `\x1b`, never the raw character; the JSON holds the JSON escape.
- **TC-E19b** — `printable` escapes a newline, U+202E, U+2028, U+2029 and U+E0001 as R1.10
  states.
- **TC-3b** — the three new blocks of R5.5 stand whole in their files; the `security-audit` row
  of `System/Docs/SKILLS.md` names v3.12.

The tests of the base that patch `external.run_command` move to the function that replaces it.
TC-L1 to TC-L22, TC-L7 to TC-L9c and TC-Y1 to TC-Y3 keep their assertions. New tests filter
not-audited findings on `audited`, not on the severity.

<!-- contract:constraints -->

## 8. Constraints and assumptions

- **No tool installs.** The run installs no tool and changes no file outside the repository. A
  real gitleaks, trufflehog or semgrep run is not part of the gates; fake tools stand in for them.
- **This run's own audits.** The external tools are still missing, so the security audits of
  stages 2 and 4 are expected to end `INCOMPLETE` for the external layer (`security-audit` §6.2).
- **Unverified exit behaviour.** This task does not verify how slither, snyk-agent-scan, mcp-scan
  and cargo clippy exit on a finding. R2.3 records their exit code as it is.
- **pip-audit without arguments** audits the interpreter's environment, not the scanned project,
  and under D2 its non-zero exit now fails a gate. This task does not change its target; the
  retro files it as a work-item candidate.
- **gitleaks `--no-git`** reads every file under the scanned root, ignored files included, such
  as `.env` and `node_modules`. A large tree can make the run slow; the 600 s timeout of the base
  applies.
- **History scan.** gitleaks in git mode runs `git log` in the scanned root, as in the base. A
  `.git` file can name a git directory elsewhere; that repository's configuration then applies, as
  in the base. R4.2 declines a `.git` link and a special file only. The walk of R4.2 ignores
  `GIT_DIR` and `GIT_CEILING_DIRECTORIES`; git honours them.
- **Python.** The code runs on 3.11 and 3.14, the two versions of CI.
- **Mirrors.** `Universal-skills` links this skill; no mirror is edited during the run.
- **The operator's local rules.** The ignored `.claude/settings.local.json` names `run_audit.py`
  with the scan types `config`, `patterns` and `sbom`. Those types start no external tool, in the
  base and after this change. The run edits nothing there.

<!-- contract:decisions -->

## 9. Decisions

- **D1**, 2026-10-09, operator: exit 3 whenever a requested part did not run, with or without
  `--fail-on`; exit 1 takes precedence. Rejected: exit 3 only when no external tool ran — a partial
  layer would exit 0; exit 3 only under `--fail-on` — misses the WI-42 acceptance.
- **D2**, 2026-10-09, operator: under `--fail-on`, a non-zero tool exit gives exit 1; trufflehog
  gets `--fail` and trivy `--exit-code 1`. Rejected: list only — the gate would still not cover
  the external layer.
- **D3**, 2026-10-09, operator: npm advisories become findings at every severity, with a count map
  per lockfile. Rejected: counts only — a finding below the gate would stay out of the findings.
- **D4**, 2026-10-09, operator: the external layer runs locally; `security-audit` states the
  toolset; no CI job. Rejected: an advisory or blocking CI job — stage-2 audits run before a
  commit, where CI does not run.
- **D5**, 2026-10-09, orchestrator, revised in revision 2: the edited code and test modules run
  through the four stages of `framework-upgrade` §3 step 4 (R7). Rejected: in-place edits — the
  spec audit of round 1 showed that `tests/run_tests.py`, a listed script, imports both test
  modules and the scanner package.
- **D6**, 2026-10-09, orchestrator: npm gets `--audit-level` under `--fail-on` (R2.10). Rejected:
  npm's default exit under D2 — this repository's 14 low advisories would fail every `--fail-on`
  of `--scan-type all`. D6 sets the threshold of npm's exit; a non-zero exit still fails the gate,
  as D2 states.
- **D7**, 2026-10-09, orchestrator: slot `secrets-history` has no trufflehog fallback (R4.3).
  Rejected: `trufflehog git file://.` — CVE-2025-41390 executed the scanned repository's
  `core.fsmonitor` command.
- **D8**, 2026-10-09, orchestrator: the history slot looks for `.git` above the scanned root
  (R4.2). Rejected: the scanned root only — a subdirectory scan would drop the history that the
  base read, and report the scan complete.
- **D9**, 2026-10-09, operator, on the spec-audit bound: "Apply rev 4, continue (Recommended)".
  Revision 4 applies P1 to P7 of round 3, and the run enters §2 with no fourth spec round.
- **D10**, 2026-10-09, orchestrator: revision 5 amends R7.6 and R7.10 after D9, per plan-audit
  round 1. R7.6 places the row text where the base pin allows it. R7.10 defines "covered"; it
  takes effect only through the operator's answer at stage 2, which quotes that definition.
- **D11**, 2026-10-09, operator, on H1 of stage-2 round 1: "Keep, state it, file WI
  (Recommended)". Rejected: an opt-in flag — every default run would exit 3; a `--log-opts`
  hardening — untestable without gitleaks.
- **D12**, 2026-10-09, operator, on H2: "Covered by WI-37 drop (Recommended)". Rejected: reopening
  WI-37 — the operator dropped it on 2026-10-06.
- **D13**, 2026-10-09, operator, on M1: "Signal + doc rule (Recommended)". Rejected: a per-tool
  exit-code table — each code needs a tool this machine does not hold.
- **D14**, 2026-10-09, operator, on M2: "File a work-item (Recommended)". Rejected: findings for
  the configuration files in this round.
- **D15**, 2026-10-09, orchestrator: a bare repository at or above the scanned root starts git
  mode, as the base's git mode did (L2). Rejected: `not_applicable` — the slot read complete with
  the history unread.
- **D16**, 2026-10-09, orchestrator: an `OSError` of the lockfile copy is a not-audited lockfile
  (L1), and text from the scanned tree is escaped in printed output (L3). Rejected: leaving L1 —
  the scanner exited 1 with no report.
- **D17**, 2026-10-09, operator, on the `INCOMPLETE` scan part of stage-2 round 2 (`security-audit`
  §6.2 rule 2): "Отгрузить с записанным пробелом (Recommended)". The decision covers stage 4 for
  the same part and the same cause (R7.10). Rejected: installing the tools for a second re-run;
  asking again at stage 4.
- **D18**, 2026-10-09, operator, on the LOW and MINOR findings of round 2: "Fix cheap ones, round 3
  (Recommended)". Rejected: TASK residuals and one record with no fix.
- **D19**, 2026-10-09, orchestrator: a bare repository that holds a link is `not_run`, as a `.git`
  link is. Rejected: `not_applicable` — the slot read complete with the history unread.

<!-- contract:out-of-scope -->

## 10. Out of scope

- pip-audit's target (§8) — retro work-item candidate.
- Parsing the findings of an external tool into the report.
- Installing the tools on the operator's machine (D4).
- A CI job for the external layer (D4).
- The `skipped_files` count of the in-process scans.
- yarn's exit bitmask.

<!-- contract:open-questions -->

## 11. Open questions

None. D1 to D4 answer the four questions of the analysis; D5 to D8 follow from the spec audit;
D9 closes it; D10 records the amendments of the plan audit.
