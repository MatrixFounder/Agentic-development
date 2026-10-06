# TASK 111 — Checks that cover what they claim: a framework-only allow list, pinned actions, a full fingerprint, every lockfile

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 111 |
| Slug | checks-that-cover-what-they-claim |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-31; the operator's answers of 2026-10-05 (D1, D2) |
| Base revision | `3a6e07ed53a3e8c25ea0c64a44708ee1b251cfa5` |
| Closes | WI-31 (its SEC-17 hook handed to WI-34) |
| Archive name | `task-111-checks-that-cover-what-they-claim.md` |
| Revision | 14: R7 per review round 8; test runners keep their bare forms (R2.7, D14) |

**Records.**

- [WI-31](backlog/wi-31-anchored-allow-rules-sha-pinned-actions-a-full-fingerprint-and-a-nested-lockfile-audit.md)

<!-- contract:problem -->

## 1. Problem

WI-31 names four checks whose coverage is narrower than their claim. Every fact below was measured
on 2026-10-05 at the base revision.

**SEC-17, allow rules.** `.claude/settings.json` allows 80 Bash rules. Several name a framework
script by a path relative to the working directory, such as
`Bash(python3 .agent/tools/task_id_tool.py *)`.

- A Bash rule matches the command text only; the working directory takes no part
  (code.claude.com/docs/en/permissions).
- The working directory persists between Bash calls inside the project and inside each additional
  working directory (code.claude.com/docs/en/tools-reference).
- No rule syntax anchors a Bash rule to the project root. A PreToolUse hook receives `cwd` and may
  return `ask` or `deny` over a matching allow rule (code.claude.com/docs/en/hooks).

In a nested checkout, such a rule runs that checkout's script of the same relative path without a
prompt. The test runners allowed by `Bash(python3 -m pytest*)` and its siblings run that
checkout's `conftest.py` or `package.json` scripts the same way. A `cd` inside one command moves the
directory without changing the `cwd` the hook receives. The PostToolUse hook is registered by the
relative path `.claude/hooks/validate_skill_hook.sh`.

**Personal permissions.** 33 of the 80 rules are personal or one-off:

- 4 rules name paths under `/Users/sergey`;
- `Bash(python3 -)` runs any Python program from standard input;
- `Bash(git push *)`, `Bash(git add *)` and `Bash(git restore *)` write to git;
- 25 others are one-off commands: `sed -n` reads, `cp` and `md5` across repositories, `rm -rf` of
  test directories, single test runs, `gh run *`.

28 of them entered with commit `0b7b075` of 2026-05-25 and 5 with `c846b5e` of 2026-05-07.
`permissions.additionalDirectories` holds 2 more paths under `/Users/sergey`.

- `System/scripts/vendors.yaml` copies `.claude/settings.json` into every new consumer project
  (`if_missing: true`). It copies `.claude/hooks/` always.
- Its comment says `settings.local.json` left the copy list because it "shipped one operator's
  permission allow-list — absolute home paths included". The copied file now holds such rules.
- The repository's `.gitignore` does not list `.claude/settings.local.json`; only the operator's
  global git ignore does.

**SEC-18, CI actions.** `.github/workflows/framework-gates.yml` holds 13 `uses:` lines:
`actions/checkout@v4`, `actions/setup-python@v5` and `actions/setup-node@v4`. A version tag moves.
On 2026-10-05 the tags point at the commits of v4.4.0, v5.6.0 and v4.4.0.

**SEC-19, tree fingerprint.** `skill-parallel-orchestration` §2.4.1 gives the formula
`{ git rev-parse HEAD; git status --porcelain; git diff HEAD; } | shasum -a 256 | cut -c1-12`.
`vdd-multi.md` step 1.0 and `.claude/agents/security-auditor.md` repeat it.

- An edit inside an untracked file leaves the value unchanged. §2.4.1 says so in prose.
- A tracked binary file enters the value only through the 7-character blob hash of its `index`
  line: without `--binary`, `git diff` prints "Binary files differ" in place of the content.
  (Revision 5 said a second edit left the value unchanged; the test-first run of D1 measured
  otherwise.)
- A user's `diff.external` or textconv setting changes the `git diff` output.
- TASK 110 reviewed untracked files under a recipe that adds the hash of each untracked file. Its
  reviewers computed two values for one tree, one per recipe.

**Lockfile audit.** `security-audit/scripts/audit/` audits npm lockfiles at the project root only.

- `scan_dependencies` in `scanners.py` runs `npm audit --json` only when the root holds
  `package.json`. A failed or offline run yields no finding.
- `run_external_tools` in `external.py` runs `npm audit` at the root when the tree holds a `.js` or
  `.ts` file.
- This repository holds three npm lockfiles under
  `.agent/skills/mermaid-authoring-guidelines/assets/renderers/` and none at the root. Neither
  function audits any of them.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The anchor hook for SEC-17 — deferred to WI-34 (D11) | — | — | — |
| R2 | The committed settings hold framework permissions only | Y | R2.1–R2.7 | A1, A3 |
| R3 | CI actions are pinned to commits and kept current | Y | R3.1–R3.3 | A1, A4 |
| R4 | The tree fingerprint covers every file under review | Y | R4.1–R4.5 | A1, A5 |
| R5 | The dependency audit covers every npm lockfile | Y | R5.1–R5.7 | A1, A6 |
| R6 | Records, versions, migration and the work-item | Y | R6.1–R6.6 | A7, A8 |
| R7 | The retro items: a hook registered last, an unfinished review | Y | R7.1–R7.2 | A7, A9 |

### 2.1 Sub-features

**The settings (R2).**

- **R2.1** `.claude/settings.json` keeps an allow rule of the base file only when one holds:
  - `skill-safe-commands` lists its command, as a pattern or in its command list;
  - `framework-gates.yml` runs its script;
  - a test of `tests/` pins it: `plan_gantt.py --check` (TASK 108 D9).

  Of the 80 base rules, 33 leave for the operator's local settings (R2.3), and R2.6 drops
  `Bash(find *)`. The other 46 stay; R2.6 rewrites 18 of them into 31,
  and R2.7 drops 13, so Appendix A holds 46.
- **R2.2** `permissions.additionalDirectories` leaves the committed file.
- **R2.3** After the operator commits, the orchestrator appends the 33 rules and the 2
  directories to the operator's `.claude/settings.local.json`, on the operator's go-ahead and
  without duplicates (D1, D5). It reads them from `git show <base>:.claude/settings.json`. The run
  does not touch that file before the commit. The audit records both counts and the count added.
- **R2.4** The repository's `.gitignore` lists `.claude/settings.local.json`.
- **R2.6** Each allow rule names its command whole: `X` and `X *` replace `X*`, which also
  matches every command whose name starts with `X`, such as `git difftool` for `git diff*`. The
  `mkdir` rules name `docs/`, `.agent/` or `tests/`, and the `mv` rules their destination
  directory. `Bash(find *)` leaves: `-exec`, `-execdir`, `-ok` and `-delete` run a command or delete
  files.
- **R2.5** No string under `permissions` of `.claude/settings.json` holds an absolute or `~`
  path. No allow rule is `Bash(python3 -)`. No allow rule names the `git` subcommand `add`,
  `commit`, `push`, `reset` or `restore`.
- **R2.7** No committed rule holds a wildcard form of a command that also writes:
  - `git log`, `git diff` and `git show`, whose `--output` writes a file;
  - `git branch`, `git tag` and `git remote`, whose arguments create or delete a ref or change a
    remote;
  - `tree`, whose `-o` writes a file;
  - `python -m pytest`, `python3 -m pytest`, `npm test`, `npx jest` and `cargo test`, whose options
    can run a program, delete a directory or overwrite a file (D14).

  Their bare forms stay, except `npx jest`, which downloads jest when the project has none. Claude
  Code's built-in check approves the read forms of `git` with no rule (Claude Code docs, Configure
  permissions, § Read-only commands; D13). `skill-safe-commands` states the same limit for every
  vendor.

**The actions (R3).**

- **R3.1** Each `uses:` of `.github/workflows/*.yml` names a 40-hex commit, followed by a comment
  with its release tag: `actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0`.

  **Why.** The pinned commits are those the base's tags point at, so CI runs unchanged code.
- **R3.2** `.github/dependabot.yml` updates the `github-actions` ecosystem monthly (D2).
- **R3.3** `System/Docs/RELEASE_CHECKLIST.md` states how a pin changes: through the Dependabot pull
  request, or by hand with the commit and tag of a release.

**The fingerprint (R4).**

- **R4.1** §2.4.1 gives one formula:

  ```sh
  { git rev-parse HEAD; git status --porcelain; git diff HEAD --binary --no-ext-diff --no-textconv; git ls-files --others --exclude-standard -z | xargs -0 -r shasum -a 256; } | shasum -a 256 | cut -c1-12
  ```

- **R4.2** §2.4.1 states that the formula runs at the top level of the work tree. It names what
  the value does not cover: ignored files and the content of a nested repository.
- **R4.3** §2.4.1's scope paragraph states that, while a round runs, the caller writes its own
  output outside the work tree or to an ignored path.
- **R4.4** `vdd-multi.md` step 1.0 and `.claude/agents/security-auditor.md` cite §2.4.1 and quote
  the formula of R4.1 verbatim.
- **R4.5** §2.4.1 drops the sentence that excuses edits inside untracked files.

**The lockfile audit (R5).**

- **R5.1** A helper lists one npm lockfile per directory under the project:
  `npm-shrinkwrap.json` when present, else `package-lock.json`. It skips the directories of
  `SKIP_DIRS` and follows no symbolic link.
- **R5.2** `scan_dependencies` runs `npm audit --json --package-lock-only` once per listed
  lockfile, with a timeout of 60 seconds. It runs in a temporary directory that holds copies of the
  lockfile and its `package.json` only, so a `.npmrc` beside the lockfile takes no part. Each
  finding names its lockfile by its path relative to the project.
- **R5.3** An audit that does not finish yields an `info` finding with its lockfile and the
  reason. The reasons are `npm` absent, the timeout, output that is not a JSON object, and an
  `error` object; for the last, the reason quotes its code or npm's `message`.
- **R5.4** `run_external_tools` runs `npm audit --package-lock-only` for each listed lockfile, in
  a temporary copy as R5.2 makes it. It
  runs when the helper lists a lockfile, regardless of the detected types. `yarn audit` at the root
  stays as at the base.
- **R5.5** A project with no npm lockfile runs no `npm audit`. The missing-lock finding still
  reports a root `package.json` without a lockfile.

  **Why.** The base ran `npm audit` there, and npm stops with `ENOLOCK` without a lockfile.
- **R5.6** A lockfile without a regular `package.json` beside it is not audited; it yields an
  `info` finding. npm would otherwise audit an ancestor's project under the lockfile's name.
- **R5.7** When an audit does not finish, the section status reads `[?] Not audited: <N> npm
  lockfile(s)`, unless a critical or high finding sets its own status.

**Records (R6).**

- **R6.1** Versions:
  - `skill-parallel-orchestration` 3.10 → 3.11;
  - `skill-safe-commands` 1.2 → 1.3;
  - `security-audit` 3.9 → 3.10.

  For `security-audit`, these quote 3.10: the front matter, the H1, `scripts/audit/__init__.py`
  `__version__`, the `run_audit.py` header, `System/Docs/SKILLS.md` and `System/Docs/VDD.md`.
- **R6.2** `security-audit` `SKILL.md` describes the npm audit of every lockfile where it describes
  the dependency scan.
- **R6.3** `CHANGELOG.md` and `CHANGELOG.ru.md` carry v3.36.0 with two migration items:
  - this repository's operator finds the moved permissions in `settings.local.json`;
  - a consumer project installed before v3.36.0 removes from its copied `settings.json` the
    personal permissions listed in §1.
- **R6.4** `docs/ARCHITECTURE.md` states, beside its tools note on `.claude/settings.json`, that
  the committed allow list holds framework permissions only and that an operator's own rules live
  in the ignored `.claude/settings.local.json`.
- **R6.5** WI-31 closes `done`, with its SEC-17 hook handed to WI-34; its index line moves to
  `## Closed`. WI-34 is filed `open`. WI-35 is filed `open` (D13).
- **R6.6** Each new test module joins `CURATED_UNITTEST_MODULES` of `tests/run_tests.py`.

**The retro items (R7).**

- **R7.1** `framework-upgrade` §3 step 4 states that a change altering what runs, or what runs
  without a prompt, takes effect in the running session at once. Its list of such changes is not
  exhaustive. A change that only narrows may land at once, after a check before the edit that
  each list only narrows and no code a hook runs changes; the audit records its output. The
  TASK states the exact registration. A hook is built on a temporary fixture root that its test
  creates and removes; §3.1 allows that fixture. The code review and the security audit check the
  code and the registration; an `INCOMPLETE` audit blocks it until the operator decides. After
  §4.5 the last edit of the change registers it verbatim with a pinning settings test, and a code
  reviewer and a security auditor check that diff. A failed gate or review restores the text
  before that edit. After a failed gate, a rejected review or a `FAIL` the operator decides, and a
  changed registration or hook code returns to stage 1.
- **R7.2** `security-audit` §6.2 defines `PASS`, `FAIL` and `INCOMPLETE`. An audit whose scan or
  adversarial review does not run to completion is never `PASS`: it is `INCOMPLETE`, or `FAIL` when
  a part found a CRITICAL or HIGH issue, and it names that part. With no report, the orchestrator
  records it. Each part gets one re-run in a run; then the operator decides in their own message.
  A control whose bypass hunt never finished ships as no protection. Tests and a mutation run do
  not stand in for the hunt. The auditor wrapper, `10_security_auditor.md`, `security-audit.md`,
  `full-robust.md`, `SKILLS.md` and `WORKFLOWS.md` point to §6.2; `full-robust` §3 gates on `audit_status: PASS`.

<!-- contract:use-cases -->

## 3. Use Cases

| UC | Actor | Precondition | Main scenario | Alternative | Postcondition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-3 consumer install | installer | a new project | the copied settings hold framework rules only | an existing settings file: not copied | no personal rule ships |
| UC-4 CI | GitHub | a workflow run | each action runs the pinned commit | a moved tag: no effect | a pin changes by pull request |
| UC-5 review round | orchestrator | an untracked file under review | its edit changes the fingerprint | an ignored file: not covered | the round detects the edit |
| UC-6 audit | auditor | lockfiles in subdirectories only | each is audited in its directory | `npm` offline: an `info` finding | each finding names its lockfile |

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | Each case marked **base-fail** fails on the base tree and passes after the change |
| A2 | *(deferred to WI-34 with the hook, D11)* |
| A3 | The settings cases TC-S1 and TC-S3 to TC-S8 hold |
| A4 | The pin cases TC-P1 to TC-P3 hold |
| A5 | The fingerprint cases TC-F1 to TC-F5 hold |
| A6 | The lockfile cases TC-L1 to TC-L23 hold |
| A7 | `PYTHONPATH=. python3 tests/run_tests.py` reports OK; every gate of `framework-gates.yml` passes locally |
| A8 | `scan_register.py` reports no new `warn` on edited markdown; `git status` lists declared paths only |
| A9 | `tests/test_run_safety_rules.py` pins the rule sentences of R7.1 and R7.2 and the pointers, and runs in the curated suite |

The other cases are regression guards: they may pass on the base tree. Each case feeds its input
to the code the TASK names and asserts one outcome.

**Settings.**

- TC-S1 **base-fail** — the allow list of `.claude/settings.json` equals Appendix A.
- TC-S3 — R2.5 holds for every string under `permissions`; no rule of a command R2.7 lists holds
  a `*`, and the only `git` rule with a `*` is `Bash(git status *)`. A `python` rule runs a bare
  `-m pytest` or a named script.
- TC-S4 — `.gitignore` lists `.claude/settings.local.json`.
- TC-S5 — no allow rule ends in a `*` joined to a word, and none starts with `Bash(find`.
- TC-S6 — the settings hold `env`, `permissions` with `allow` only, and `hooks`. `env` is the
  base's, and `hooks` holds one entry: PostToolUse, matcher `Write|Edit`, command
  `.claude/hooks/validate_skill_hook.sh`.
- TC-S7 — every part of every shell block of `skill-archive-task` matches a committed rule, except
  the `test -e` guard of Step 5, which WI-35's script absorbs (D13).
- TC-S8 — the patterns of `skill-safe-commands` accept the read and bare forms of R2.7 and reject
  its writing forms. Its Antigravity list, the lists of both READMEs, `GEMINI.md` and `AGENTS.md`
  state the same.

**Pins.**

- TC-P1 **base-fail** — every `uses:` of `.github/workflows/*.yml` matches
  `<owner>/<repo>@<40 hex> # v<version>`; fails when one line names `@v4`.
- TC-P2 — `.github/dependabot.yml` names the `github-actions` ecosystem, monthly.
- TC-P3 — `RELEASE_CHECKLIST.md` names `dependabot.yml`.

**Fingerprint.** The test reads the formula from the fenced `sh` block of §2.4.1 and runs it with
`bash` in a temporary repository.

- TC-F1 **base-fail** — an edit inside an untracked file changes the value.
- TC-F2 — a second edit of a tracked binary file changes the value.
- TC-F3 — a repository with no untracked file yields one value on two runs.
- TC-F4 — `vdd-multi.md` and the auditor wrapper hold the §2.4.1 block's formula verbatim.
- TC-F5 — §2.4.1 holds the run-location, coverage and caller-output statements of R4.2 and R4.3,
  and not the sentence R4.5 drops.

**Lockfiles.** A fake `npm` on `PATH` records its directory and arguments and prints a set reply.

- TC-L1 **base-fail** — the only lockfile is `sub/package-lock.json` → `npm audit --json
  --package-lock-only` runs once, in a copy outside the project.
- TC-L2 — its reply holds one high advisory → a `high` finding names `sub/package-lock.json`.
- TC-L3 — a lockfile under `node_modules/` → not audited.
- TC-L4 — no lockfile → no `npm audit`.
- TC-L5 — `npm` absent, a reply that is not JSON, a reply with an `error` object, or the timeout →
  an `info` finding names the lockfile and the reason.
- TC-L6 — `package-lock.json` and `npm-shrinkwrap.json` in one directory → one audit.
- TC-L7 to TC-L10 — the PLAN's cases for R5.4 and R5.5.
- TC-L11 — a linked lockfile and a linked directory → not audited.
- TC-L12 — a critical and a high advisory → one finding each, naming the lockfile.
- TC-L13 — a `.npmrc` beside the lockfile → the copy holds only the lockfile and `package.json`.
- TC-L14 — no `package.json` beside the lockfile → an `info` finding, no `npm`.
- TC-L15 — `npm` absent → the section status of R5.7; each audit has a 60-second timeout.
- TC-L16 — the copy holds the original `package.json`. TC-L17 — a linked `package.json` → not
  audited.
- TC-L18 — a critical finding in one lockfile and an unfinished audit in another → the status
  names the critical finding.
- TC-L19 — `vulnerabilities` as `null`, a list, or a map of strings → no crash; a list is an
  `info` finding. TC-L20 — the timeout reason names 60 s.
- TC-L21 — an `error` code reaches the reason. TC-L22 — the status counts every unaudited
  lockfile. TC-L23 — a moderate advisory is no finding.

<!-- contract:open-questions -->

## 5. Open Questions

None open. D1 and D2 record the operator's answers.

## 6. Decisions

**D1, 2026-10-05, operator: the personal permissions move to the operator's local settings.**
Rejected: removing them, which makes those commands ask again; keeping them, which ships them to
consumers.

**D2, 2026-10-05, operator: Dependabot updates the action pins monthly.** Rejected: manual
updates, which leave a pin on an old release until someone looks.

**D3, 2026-10-05, orchestrator: the hook asks, never denies.** A nested checkout may be the
operator's own work. Under `claude -p` no one answers the prompt, so an `ask` there stops the call.
Rejected: `deny`, which blocks a legitimate interactive run with no way through.

**D4, 2026-10-05, orchestrator: the pins keep the current major versions.** The pinned commits
equal the base's tags, so CI behaviour does not change. A major upgrade arrives as a Dependabot
pull request. Rejected: upgrading to `checkout` v7 now, which changes CI in a security task.

**D5, 2026-10-05, orchestrator: the local settings change after the commit.** `framework-upgrade`
§3.1 requires every edited path to be tracked, and `settings.local.json` is ignored. R2.3 therefore
runs after the operator's commit, as a mirror sync does. The base revision holds every moved
permission. The audit records counts, not the rules, because the rules hold home paths. Rejected:
editing the file during the run, which §3.1 stops.

**D6, 2026-10-05, operator: a fourth specification audit round.** Round 3 failed on 4 MAJOR
findings, all in R1, with a fix stated for each. The operator chose to fix them and audit once
more. Rejected: splitting the hook into a new work-item, which leaves SEC-17 open; stopping the
run.

**D7, 2026-10-05, operator: revision 5 proceeds to planning.** Round 4 failed on 3 MAJOR
findings, each a shell edge case of R1 with a one-clause fix that revision 5 applies. The audit
records `[OVERRIDE_VERIFICATION]`. The hook is checked where it runs: a test per case, and the
final code review and security audit, whose roles execute it. Rejected: a fifth round, which
finds the next edge case; splitting the hook off, which leaves SEC-17 open.

**D8, 2026-10-05, orchestrator: review round 1 narrows the settings and the scanner.** The code
review and the security audit found that `X*` rules admit `X`-prefixed commands, that `find *`
runs commands, and that `npm` read a vendored `.npmrc`. R2.6, R5.2, R5.6 and R5.7 answer them. The
hook's own fixes are deferred with it (D11). Rejected: listing the settings gaps in §7, which
keeps an allow rule that runs any program.

**D9, 2026-10-05, operator: the hook recognises safe shapes.** Review round 2 found that a `cd`
the shell never runs moved the modelled directory back to the root (SEC2-1). R1 no longer models
the shell: it lists the shapes it can check and asks on the rest. Rejected: patching the model,
which each audit and review round had found another way around.

**D10, 2026-10-05, operator: the hook stays strict.** It asks on a guarded command in Auto mode
too, even when no allow rule would approve it. A narrower hook, guarding only what an allow rule
approves, goes to a new work-item. Rejected for this run: an approximation of Claude Code's
matcher, which needs another review round.

**D11, 2026-10-06, operator: the hook is deferred to WI-34.** Three review rounds each found a new
way the hook's model parted from the shell (SEC2-1, CR3-3, CR3-4), and further adversarial analysis
could not run to a conclusion in this session. The hook is removed from this change; its design,
test suite and the review history move to WI-34. This supersedes D3, D6, D7, D9 and D10 for the
shipped change. R2 still narrows the committed allow list, which stands on its own as the
recorded reviews confirmed. Rejected: shipping the hook as a partial mitigation, which would claim
more protection than it gives.

**D12, 2026-10-06, operator: the retro items are fixed in this run.** The retro offered three
items; the operator chose two and asked to fix them now (R7). Rejected: filing them as
work-items.

**D13, 2026-10-06, operator: seven wildcard `git` and `tree` rules leave; archiving stays automatic.**
The R7 security audit found that `Bash(git diff *)`, `Bash(git log *)` and `Bash(git show *)`
approve `--output`, which writes a file (SECI-8). `git branch *`, `git tag *` and `git remote *`
approve writes to refs and remotes, and `tree *` approves `-o`. Claude Code's built-in check
approves the read forms of `git` with no rule (Claude Code docs, Configure permissions, § Read-only
commands), so the seven rules leave and the bare forms stay (R2.7). The wildcard of the two `mv`
rules also matches a destination outside their directories. The operator keeps archiving automatic; an archive script that checks its destination goes to
WI-35. Rejected: deny rules on `--output`, which the Claude Code documentation calls fragile.

**D14, 2026-10-06, operator: test runners keep their bare forms; older classes go to WI-35.** The
round-5 security audit found that the wildcard rules of `python -m pytest`, `python3 -m pytest`,
`npm test`, `npx jest` and `cargo test` approve options that run a program, delete a directory or
overwrite a file (SECI5-1). These rules leave, and `npx jest` leaves whole (R2.7). In Manual mode
a test run with arguments now asks. The same reviews found older classes in `skill-safe-commands`,
the framework scripts and the dependency scan; the operator moved them to WI-35. Rejected: fixing
every vendor's patterns in this run.

## 7. Out of scope

- `.gemini/settings.json` and the other vendors' settings: they hold no allow list. The Gemini
  hook already prefixes `${GEMINI_PROJECT_DIR:-.}`.
- Lockfiles of `yarn`, `pnpm` and other ecosystems below the root.
- Rules in `.claude/settings.local.json` that were there before this task.
- Dependabot for the npm lockfiles of the renderers. Their overrides are deliberate (TASK 110).
- A command allowed by a read-only rule, such as `cat` or `git status`, in a foreign directory.
- A destination outside `docs/tasks/` or `docs/plans/` in the two `mv` rules: archiving stays
  automatic (D13). WI-35 holds the checked archive script.
- The older classes of review round 5 (D14): `rg`, `fd` and `file` options, open-ended patterns of
  `skill-safe-commands`, framework-script arguments, `yarn audit` and the `full-robust` scan gate.
  WI-35 holds them.
- The anchor hook for SEC-17, and every command shape it would have guarded — deferred to WI-34
  (D11). Without it, a committed relative-path allow rule still matches in a nested checkout.
- `Bash(python3 -)` and `Bash(git push *)` in the operator's local settings after R2.3 (D1).

## Appendix A — the allow rules that stay

1. `Bash(ls *)`
2. `Bash(cat *)`
3. `Bash(head *)`
4. `Bash(tail *)`
5. `Bash(grep *)`
6. `Bash(wc *)`
7. `Bash(stat *)`
8. `Bash(file *)`
9. `Bash(du *)`
10. `Bash(df *)`
11. `Bash(echo *)`
12. `Bash(git status)`
13. `Bash(git status *)`
14. `Bash(git log)`
15. `Bash(git diff)`
16. `Bash(git show)`
17. `Bash(git branch)`
18. `Bash(git remote)`
19. `Bash(git tag)`
20. `Bash(mv docs/TASK.md docs/tasks/*)`
21. `Bash(mv docs/PLAN.md docs/plans/*)`
22. `Bash(mkdir -p docs/*)`
23. `Bash(mkdir -p .agent/*)`
24. `Bash(mkdir -p tests/*)`
25. `Bash(python -m pytest)`
26. `Bash(python3 -m pytest)`
27. `Bash(npm test)`
28. `Bash(cargo test)`
29. `Bash(python3 .agent/skills/skill-session-state/scripts/update_state.py *)`
30. `Bash(python3 .agent/tools/task_id_tool.py *)`
31. `Bash(python3 .agent/skills/skill-creator/scripts/validate_skill.py *)`
32. `Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)`
33. `Bash(python3 .agent/tools/rebase_links.py *)`
34. `Bash(python3 .agent/skills/artifact-formalizer/scripts/scan_register.py *)`
35. `Bash(python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py *)`
36. `Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py *)`
37. `Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py --check *)`
38. `Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py docs/PLAN.md --check *)`
39. `Bash(python3 System/scripts/doctor.py)`
40. `Bash(python3 System/scripts/doctor.py *)`
41. `Bash(python3 tests/run_tests.py)`
42. `Bash(python System/scripts/validate_skills.py --root .)`
43. `Bash(python System/scripts/validate_skills.py --root . --quiet)`
44. `Bash(python System/scripts/check_prompt_references.py --root .)`
45. `Bash(python System/scripts/security_lint.py --root .)`
46. `Bash(python System/scripts/smoke_workflows.py --root .)`
