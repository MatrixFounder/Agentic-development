# TASK 130 — A dependency audit names the copies that run, and a TASK that fixes an advisory lists them

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 130 |
| Slug | audit-the-copies-that-run |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-55, filed at the retro of TASK 129; the operator's choice of 2026-10-27 (D1) |
| Base revision | `e89753f706403a63026de3a66d7aee9999be598b` |
| Closes | WI-55 |
| Archive name | `task-130-audit-the-copies-that-run.md` |
| Revision | 7 |

**Revision 7** applies the findings of round 4 of stage 2, cited as CR4-x and SA4-x, and the
operator's choice of a fifth round that checks the fix only (D17).
**Revision 6** applies the findings of round 3 of stage 2, cited as CR3-x and SA3-x, and the
operator's choice of one more round without the case of an accepted exposure (D13, D16).
**Revision 5** applies the findings of round 2 of stage 2, cited as CR2-x and SA2-x, and adds the
decisions D13 to D15.
**Revision 4** applies the findings of round 1 of stage 2 (the audit record). It cites them as
CR-x, of the code review, and SA-x, of the security audit, and adds the decisions D10 to D12.
**Revision 3** applies m1, m2 and N1 to N5 of Mode A round 2, which passed, with no further round.
**Revision 2** applies M1, m1 to m10 and N1 to N8 of Mode A round 1. It adds the four stages of
`tests/test_run_safety_rules.py` (R6), the pointers of R1.8, the reviewer's item of R2.4, and the
decisions D6 to D9.

**Request.** At the retro of TASK 129 the operator chose one finding: the overrides of the renderer
lockfiles did not reach the copies that the render page runs. It was filed as WI-55. On 2026-10-27
the operator chose two tasks: WI-55 first, with its option 2, and the Windows port of the archive
chain next, as TASK 131.

A coordinate into a file that this task edits carries the pin `@e89753f`, the base revision.

<!-- contract:problem -->

## 1. Problem

1. **The dependency audit reads the declared tree only.**
   - `.agent/skills/security-audit/SKILL.md:50@e89753f` `Dependencies / Supply Chain (OWASP A03:2025, CWE-1104) — real lock files only`
   - `.agent/skills/security-audit/SKILL.md:219@e89753f` `2. **Software Supply Chain (A03)**: Lock files committed? Versions pinned? SCA + dependency audit clean?`
   - `.agent/skills/security-audit/references/checklists/owasp_top_10.md:35@e89753f` `**Dependency Audit:**`

   None of them names a copy of a library that another package builds into its own artifact.
2. **TASK 129 measured the gap.** The overrides of `dompurify` and `katex` made `npm audit` report
   no advisory. The render page runs the copies that mermaid, `@mermaid-js/layout-elk` and
   `@mermaid-js/mermaid-zenuml` embed: DOMPurify 3.4.2, 3.4.12 and 3.3.1, and KaTeX 0.16.45 and
   0.16.47. Advisories cover each of them (TASK 129 D9 and §8; WI-41).
3. **No step of the analysis measures what runs.** `requirements-analysis` asks for no such
   measurement. The Analysis and Architecture phases of TASK 129 audited the tree only, and the
   operator decided D9 twice, once per inventory.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | Copies outside the dependency tree in `security-audit` | yes | the subsection; its steps; the table; the pointers of §2, §3, §7 and the checklist | A1, A3 |
| R2 | The measurement of the analysis and its review | yes | the rule; its place in a TASK; the reviewer's item; the versions | A2, A3 |
| R3 | Versions and their mirrors | yes | `security-audit` 3.13; the scanner at 3.12; `SKILLS.md`; `VDD.md` | A4 |
| R4 | A contract test | yes | the module; the red run; the mutations; the CI step; the check of what runs | A3, A6 |
| R5 | Records | yes | the changelogs; WI-55; `docs/BACKLOG.md`; no migration | A5 |
| R6 | The four stages of `tests/test_run_safety_rules.py` | yes | the staged copy; stage 2; stage 3; stage 4; the allow rules | A4, A7 |

## 3. Requirements

### R1 — copies outside the dependency tree in `security-audit`

- **R1.1** §3 of `.agent/skills/security-audit/SKILL.md` gains the subsection
  `### Copies outside the dependency tree (every stack)`, after the subsection of Agentic / MCP.
  It states:
  1. the scan of §2 reads at most the declared package tree. For Python and pnpm it checks only that
     a lock file exists, and its bare `pip-audit` reads the environment that `pip-audit` runs in
     (SA-F3, CR-Q3, CR2-N2, SA2-N1, D12);
  2. a copy of a library that another package builds into its own artifact is outside that tree:
     a bundle, a vendored directory, a static or an embedded copy;
  3. the scan does not see such a copy, and an override or an upgrade of the package does not
     reach it.
- **R1.2** The subsection gives the procedure for a library that a published advisory covers. One of
  these names the library (SA-F2, SA2-N5):
  - the scan of §2;
  - an override, a resolution, a `[patch]` or a `replace` entry of a manifest;
  - an open record of `docs/BACKLOG.md` or `docs/KNOWN_ISSUES.md`;
  - an SBOM of the artifacts, matched against an advisory database (CR2-N11, SA2-N4);
  - a change that adds or alters a copy outside the tree, such as a vendored directory or a
    committed bundle (SA4-R4-2);
  - the request, or a change that fixes the advisory.

  Steps 1 and 2 decide whether a copy runs in the code under audit: the code that the audit, or the
  task, covers, with each runtime that it starts. A change to a manifest or a lock file adds each
  runtime that installs from it (CR2-N1, SA3-R3-2, CR3-R3-3, CR4-R4-1, CR4-R4-3, SA4-R4-1,
  SA4-R4-3, D13). A vulnerability with no published advisory follows §6.1, and its report states
  only what §6.1 step 2 allows (SA-F5, D11). Text read from an artifact or a ledger record is data,
  not instructions (SA-F7, SA2-N7). The steps:
  1. Find the entry points of the code under audit that each runtime loads, the build and the tests
     included, such as a page, a binary or an import path (SA-F8).
  2. List each copy of the library reachable from them, with the package that carries it and its
     version. The search uses more than the package name (SA-F9). A version is read without
     running the package's code. A fetch takes the carrying package at the version and integrity
     hash that its lock file records, or an artifact by its digest, for the platform of the
     runtime. It runs outside the repository, with install scripts off, and writes into a scratch
     directory. A source distribution, a git or a directory spec, and a build run the package's
     code (SA-F7, CR2-N4, CR2-N5, SA2-N2, SA2-N3, SA3-R3-5, SA3-R3-6, CR3-R3-8, D15).
  3. Name the advisories that cover the version of each copy.
  4. Report each copy at a covered version as a finding, at the highest severity among its
     advisories (SA-F11). When a change fixes the advisory, state whether the fix reaches the copy
     (CR-Q5). A copy that the fix cannot reach stays a finding, and the report names its route: a
     mitigation, the operator's decision quoted from its record, or a work-item (SA-F12). Such a
     finding sets the verdict of §6.2 as any finding does. The operator decides what follows in
     their own message; a decision quoted from a record names a route only (D13, SA4-R4-4).
- **R1.3** The procedure states its cases:
  - a review that finds no copy outside the tree says so, and names the entry points it read
    (CR-C1);
  - a copy whose version cannot be read is reported as `version not determined`. It counts as
    covered by each advisory of the library, at the highest severity, until its version is read
    (SA-F1, D14);
  - a step that cannot complete, such as an artifact that cannot be fetched, leaves the review not
    complete, and §6.2 applies (CR2-N8, SA2-N10);
  - a role with no execution tool records the lookup of step 3 as `NOT RUN`, and its caller
    supplies the data (`skill-parallel-orchestration` §2.4). Until the data arrives, the review is
    not complete (CR-Q4, SA-F13).
- **R1.4** The subsection holds a table of where such copies lie and how to read the version that
  runs. Each row has a cell on the version. Its rows:
  - npm: a browser bundle, or a Node package published pre-bundled;
  - Python: vendored modules, and native libraries that a wheel carries or links into its
    extension modules. The version is read as the source states it, or statically from the
    library, with no import (SA-F10, CR3-R3-7, SA3-R3-8, SA4-R4-5);
  - Go: binaries built elsewhere that a runtime runs, and library source copied into the module.
    `go.mod` fills `vendor/`, which is inside the tree (CR-Q2);
  - Rust: crates that build bundled C sources;
  - C and C++;
  - JVM: shaded or fat JARs. The version comes from `pom.properties` when present, else from the
    classes compared with released builds (CR-Q7, SA-F10, CR2-N6);
  - container images: the OS packages and runtimes of a base image. The version of a runtime
    installed from a tarball comes from its binary (SA-F10, CR2-N7).

  A sentence states that the table is not exhaustive. Another states that the procedure starts from
  an advisory, so a library that only an artifact carries stays unseen until an SBOM of the
  artifacts names it (SA-F4). Such an SBOM is made from the artifacts as they lie, with no install
  and no build (SA3-R3-7).
- **R1.5** The subsection names its origin: TASK 129, D9. It states that the render page runs the
  copies, which WI-41 tracks (SA-F15).
- **R1.6** The bullet of §2 at `.agent/skills/security-audit/SKILL.md:50@e89753f` gains a sentence
  that names the subsection. It states that the scan reads at most the declared package tree
  (SA-F3).
- **R1.7** Check 2 of "Web/API" at `.agent/skills/security-audit/SKILL.md:219@e89753f` and the
  question at `.agent/skills/security-audit/references/checklists/owasp_top_10.md:35@e89753f`
  `**Dependency Audit:**` each gain a pointer to the subsection.
- **R1.8** The table of §7 gains a row: the excuse "the dependency audit is clean, so the advisory
  is fixed", and the answer that names the subsection. The answer is one sentence: the audit reads
  at most the declared tree, and a bundled or vendored copy still runs (SA-F3).
- **R1.9** No file under `.agent/skills/security-audit/scripts/` or `examples/` changes (D2, D6).

### R2 — the measurement of the analysis and its review

- **R2.1** §3 of `.agent/skills/requirements-analysis/SKILL.md`, under "DO", gains a rule:
  - a task that fixes a published advisory in a dependency states, in its problem section, each
    copy of the library that a runtime loads, with its package, its version and its advisories
    (CR-Q6);
  - a library that no runtime of the project loads is stated as such (CR-C2);
  - the requirements name the copies that the fix reaches and those it does not (CR-C2);
  - a vulnerability with no published advisory follows `security-audit` §6.1 (SA-F5, D11);
  - the problem section is the one under `<!-- contract:problem -->`, which
    `System/Agents/02_analyst_prompt.md` defines; the task template calls it §1, General
    Description (CR-Q1).
- **R2.2** The rule names the subsection of R1.1, whose steps 1 to 3 give the measurement.
- **R2.3** The task template of the skill stays as it is (D3).
- **R2.4** §5 "Non-Functional" of `.agent/skills/task-review-checklist/SKILL.md` gains an item
  (D7). A TASK that fixes a published advisory in a dependency names each copy that a runtime
  loads, with its package, version and advisories, or states that none runs (SA-F14). Its
  requirements name the copies that the fix reaches and those it does not (CR2-N10, SA2-N9).
- **R2.5** `requirements-analysis` goes to version 1.5, and `task-review-checklist` to 1.2.

### R3 — versions and their mirrors

- **R3.1** `security-audit` goes to version 3.13 in four places: its front matter, its H1, the row
  of `System/Docs/SKILLS.md` and the quote of `System/Docs/VDD.md`. TC-04 of
  `tests/test_disclosure_rule.py` reads all four. They change in the edit of stage 3 (R6.3).
- **R3.2** The row of `System/Docs/SKILLS.md` names the rule of R1, in the same edit. Its clause
  stands before the clause of §6.1, in the order of the sections (CR-D2).
- **R3.3** The scanner keeps version 3.12: `scripts/run_audit.py`, `scripts/audit/__init__.py` and
  `examples/usage_example.md` stay as they are (D6).

### R4 — a contract test

- **R4.1** A new module `tests/test_dependency_copies_rule.py` pins, by a quoted phrase of each, in
  the place where this TASK puts it (CR-T1):
  - TC-01: the subsection of R1.1 inside §3. Its statements are read before the procedure, and the
    trigger with its sources and rules inside the procedure. Each part of a step is read inside
    that step, and each case of R1.3 inside the cases (CR-T2, CR-T4, CR-T5, CR2-T-a to CR2-T-d,
    CR3-R3-5);
  - TC-02: each row of R1.4, with the places that R1.4 names and a cell on the version, and the two
    sentences after the table (CR-T3);
  - TC-03: the pointer of R1.6 in its bullet of §2, and the row of R1.8 in §7. The pointers of R1.7
    stand in check 2 of "Web/API" and in the item of A03 of the checklist;
  - TC-04: each part of the rule of R2.1 inside rule 6 of the list "DO", its reference of R2.2 with
    the steps it names, and the item of R2.4.

  The module holds its pinned phrases as constants, so a harness can remove each one.
- **R4.2** The module is written before the skill text. Its red run at the base is recorded, and
  each test fails there.
- **R4.3** Each test fails when the element it pins is removed, or moved out of its place, on a
  copy of its file. The module reads its files through module constants, which a harness points at
  a copy. The audit record lists each mutation with its result (CR-T6).
- **R4.4** The pytest step "Run tooling regression tests" of `.github/workflows/framework-gates.yml`
  lists the module (D5).
- **R4.5** The check of `framework-upgrade` §3 step 4, "What the change runs", runs each allowed
  command that reaches the module: a listing of the tree, the command, a second listing. The audit
  record holds each command, by the SHA-256 prefix of its rule, and its result.

### R5 — records

- **R5.1** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.49.0. It states:
  - no migration is needed: no skill is new, and no state changes its format;
  - the skill goes to 3.13 and the scanner stays at 3.12 (D6).
- **R5.2** The record of WI-55 takes `status: done`, `resolved_at` and `resolved_by: TASK 130`, with
  a resolution blockquote at the top of its body. The blockquote names the place of the rule: §3,
  where the options of the record named §6.2 (D2).
- **R5.3** The index line of WI-55 moves to `## Closed` of `docs/BACKLOG.md`.

### R6 — the four stages of `tests/test_run_safety_rules.py`

TC-3 of the module pins the row of `security-audit` in `System/Docs/SKILLS.md` whole, version
included (`tests/test_run_safety_rules.py:248@e89753f` `"System/Docs/SKILLS.md": (`).
`tests/run_tests.py` runs the module, and an allow rule runs that script, so the module takes the
four stages of `framework-upgrade` §3 step 4.

- **R6.1** Stage 1 writes `tests/staged_run_safety_rules.py`: the module with the row of R3.1 and
  R3.2. The copy fails against the row of the base. It passes in a throwaway worktree that holds the
  edit of R6.3, as TASK 128 R8.7 built one. No allow rule, hook or listed script names or imports
  the copy, and no collection pattern matches its name.
- **R6.2** Stage 2: the code review and the security audit check the whole change at one
  fingerprint. Both pass; at most 3 rounds.
- **R6.3** Stage 3, after §4.5: the last edit of the change copies the staged module over
  `tests/test_run_safety_rules.py`, removes the copy, and moves the four mirrors of R3.1 with the
  row of R3.2. Every other edit, R5 included, lands before it. The gates run again, with the check
  of what the change runs for each allowed command that reaches the edited module. The change holds
  no registration, so no settings test is added.
- **R6.4** Stage 4: a code reviewer and a security auditor check the diff of stage 3 on the new
  fingerprint.
- **R6.5** The run reads the allow rules of `.claude/settings.json`, `.claude/settings.local.json`
  and `~/.claude/settings.json` at §2.2, at §4.5 and after the gates of stage 3. A rule added since
  the first reading that runs a file of the change stops the run. The audit record names each file
  of the change that a rule runs, and quotes no rule.
- **R6.6** The rule "Failure" of `framework-upgrade` §3 step 4 applies as written. The audit record
  holds the diff of stage 3.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An auditor checks the copies of an advised library

- **Actors.** The security auditor; the scan of §2; the orchestrator.
- **Precondition.** A published advisory names a library, and one of the sources of R1.2 names it.
1. The auditor finds the entry points that each runtime loads, the build and the tests included.
2. The auditor lists each copy of the library reachable from them, with its package and version.
3. The auditor names the advisories of each copy.
4. The auditor reports each copy at a covered version, and whether the fix reaches it or the route
   of a copy that it cannot reach.
- **Alternative 1a.** An artifact cannot be fetched: the step does not complete, and the review is
  not complete (§6.2) (CR4-R4-4).
- **Alternative 2a.** No copy lies outside the tree: the report says so and names the entry points
  read.
- **Alternative 2b.** The version of a copy cannot be read: the report names the copy as
  `version not determined`, and the copy counts as covered until its version is read.
- **Alternative 3a.** The role has no execution tool: it records the lookup as `NOT RUN`, and the
  orchestrator supplies the advisories of each version. Until then the review is not complete.
- **Postcondition.** The report names each copy that runs, its advisories, and whether the fix
  reaches it.

### UC-2 — An analyst writes a TASK that fixes an advisory

- **Actors.** The analyst; the task reviewer.
- **Precondition.** The request names a published advisory in a dependency.
1. The analyst reads the audit of the declared tree.
2. The analyst measures the copies that the runtime loads, by steps 1 to 3 of UC-1.
3. The problem section of the TASK lists them.
4. The task reviewer checks the list by the item of R2.4.
- **Alternative 2a.** The library runs in no runtime that the project loads, such as a package of
  type declarations only: the problem section says so.
- **Postcondition.** The requirements of the TASK name the copies that the fix reaches and those it
  does not.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — `.agent/skills/security-audit/SKILL.md` and `references/checklists/owasp_top_10.md` hold
  R1.1 to R1.8. For each of `.agent/skills/security-audit/scripts` and
  `.agent/skills/security-audit/examples`, `git diff e89753f -- <dir>` and
  `git status --porcelain --untracked-files=all -- <dir>` print nothing (R1.9).
- **A2** — `requirements-analysis` holds R2.1 and R2.2, and `task-review-checklist` holds R2.4, with
  the versions of R2.5. For `.agent/skills/requirements-analysis/assets`, both commands of A1 print
  nothing (R2.3).
- **A3** — `tests/test_dependency_copies_rule.py` passes. Each test fails at the base, and fails
  under the removal of its element on a copy (R4.2, R4.3).
- **A4** — after stage 3: the versions of R3; `tests/test_disclosure_rule.py` and
  `tests/test_run_safety_rules.py` pass; `System/scripts/validate_skills.py` passes every skill.
- **A5** — the records of R5. `scan_register.py` finds no warning on an added line of an edited
  document.
- **A6** — every `run:` step of `.github/workflows/framework-gates.yml` passes locally, the new
  module among the tests of the step "Run tooling regression tests". The checks of R4.5 and R6.3
  find no difference that code of the change writes.
- **A7** — stage 2 and stage 4 pass: each round of the code review and of the security audit
  passes on its fingerprint (R6.2, R6.4).

<!-- contract:open-questions -->

## 6. Open questions

None. The operator chose the order and the option (D1).

## 7. Decisions

- **D1**, 2026-10-27, operator: two tasks. WI-55 comes first, as TASK 130, with its option 2; the
  Windows port of the archive chain follows as TASK 131. Rejected: one task for both; the port
  first.
- **D2**, 2026-10-27, orchestrator: the rule goes into §3 of `security-audit`, the semantic layer
  of §0. Rejected:
  - §6.2, which the options of WI-55 named: §6.2 is "A review that cannot finish";
  - a detector in `run_audit.py`: a copy in an artifact needs a reader per ecosystem, and §0 puts
    such judgement in the semantic layer.
- **D3**, 2026-10-27, orchestrator: `requirements-analysis` gains one rule in §3, and the problem
  section of a TASK holds the measurement. Rejected: a section of the task template, which every
  TASK would carry, with or without an advisory.
- **D4**, 2026-10-27, orchestrator: a contract test pins the rules where the agents read them, as
  `tests/test_disclosure_rule.py` pins §6.1. Rejected: no test; Mode B of
  `skill-self-improvement-verificator` asks for tests of a new framework feature.
- **D5**, 2026-10-27, orchestrator: the module runs in CI through the pytest step of the tooling
  job. Rejected: `CURATED_UNITTEST_MODULES` of `tests/run_tests.py`. The allow rule `a8ddacaa1aa9`
  of `.claude/settings.json` runs that script, so its edit takes the four stages.
- **D6**, 2026-10-27, orchestrator: the scanner keeps version 3.12, and the skill goes to 3.13. The
  scanner does not change. Rejected: moving the scanner's strings with the skill, as TASK 111, 112
  and 118 did, for a version that names no change of the scanner. That edit takes the four stages:
  - five local allow rules run `run_audit.py`;
  - `tests/run_tests.py`, which the rule `a8ddacaa1aa9` runs, runs `test_lockfile_audit`, which
    loads the package of the scanner.
- **D7**, 2026-10-27, orchestrator: the task reviewer checks the rule of R2.1 through an item of its
  checklist. Rejected: no item, which leaves UC-2 step 4 to memory.
- **D8**, 2026-10-27, orchestrator: `System/Agents/10_security_auditor.md` does not change; the role
  loads the skill. Rejected: a pointer there, which adds a second place to keep.
- **D9**, 2026-10-27, orchestrator: `docs/ARCHITECTURE.md` does not change. Its §10.7 already names
  the copies that the render page runs (TASK 129). Rejected: a section on the audit, which is a
  skill and not a component of the system.
- **D10**, 2026-10-27, orchestrator: the list of R2.1 stands in a TASK that the repository
  publishes, the copies that still run at a covered version among them (SA-F16). It names
  published advisories of public packages, at the versions that the lock files and the artifacts
  already show. The operator accepted the same exposure for WI-41 (TASK 129 D9). Rejected: keeping
  the list out of the TASK, which leaves the item of R2.4 nothing to check.
- **D11**, 2026-10-27, orchestrator: §6.1 of `security-audit` does not change; the subsection and
  rule 6 defer to it (SA-F5). Rejected: a sixth duty in the list of §6.1 that gives way. That list
  is pinned by `tests/test_disclosure_rule.py`, so the edit takes the four stages for that module
  too.
- **D12**, 2026-10-27, orchestrator: the subsection states what the scan of §2 reads, Python
  included, and the scanner does not change (D6). Its bare `pip-audit` at
  `.agent/skills/security-audit/scripts/audit/external.py:189@e89753f` is a finding before the
  task (SA-F3, the audit record).
- **D13**, 2026-10-27, operator and orchestrator: the code under audit bounds the procedure. Steps 1
  and 2 decide whether a copy runs in it, and a change to a manifest or a lock file adds each
  runtime that installs from it (CR2-N1, SA3-R3-2, CR3-R3-3, CR4-R4-1). A copy that the fix
  cannot reach stays a finding at its severity, and the operator decides what follows a `FAIL`.
  The operator removed the case of an accepted exposure after round 3 (SA3-R3-1). Rejected:
  - the trigger of revision 4 with no scope: every audit of this repository fails while WI-41 is
    open;
  - the case of an accepted exposure of revision 5: read strictly, it covered no record; read
    loosely, any record that mentions a decision cleared a copy;
  - an edit of §6.2, which `tests/test_run_safety_rules.py` pins whole.
- **D14**, 2026-10-27, orchestrator: a copy at `version not determined` counts as covered by each
  advisory of the library (CR2-N9). The default fails closed, as SA-F1 asked; the rows of the table
  name where a version is read. Rejected: a narrower default, which clears a copy on evidence that
  the review did not read.
- **D15**, 2026-10-27, orchestrator: step 2 states what a fetch for a version must not do, and
  names no command (CR2-N3, CR2-N4, SA2-N1, SA2-N2). Rejected: the commands of revision 4, whose
  options differ by tool, by version and by spec.
- **D16**, 2026-10-27, orchestrator: the module pins phrases in their places, not whole blocks, and
  step 4 keeps the highest severity among the advisories (CR3-R3-6, CR3-R3-9). Rejected:
  - whole-block pins of a subsection that three rounds rewrote;
  - a rating in context, which lets a review rate a covered copy below its advisory.
- **D17**, 2026-10-27, operator: after round 4, the fix of its findings and a fifth round whose
  reviewers check that fix and what it touches. Rejected: a full fifth round; closing with the
  finding CR4-R4-1 as a residual, which leaves the case of WI-55 open.
- **D18**, 2026-10-27, orchestrator, under the operator's standing rule: stage 2 closes at round 5,
  where both reviews pass. The narrow LOW routes that stay are residuals:
  - the removal of a copy is not a source of the trigger (SA5-R5-1);
  - a runtime that the code under audit hands work to, and does not start, is outside its scope
    (SA5-R5-2);
  - a pin outside a manifest or a lock file, such as a `FROM` line, adds no runtime (CR5-F5-3);
  - a runtime that an added runtime starts is reached through the example of step 1 only
    (CR5-F5-4);
  - TC-02 does not pin "or the version string of the library" (CR5-F5-5);
  - a committed bundle names its libraries only after the search of step 2 (CR5-F5-7);
  - a lock change of a renderer fails its audit while WI-41 is open (SA5-R5-3). That fails closed.

  Rejected: a sixth round, which the rule keeps for a finding that breaks something real.
  A5 holds with one exception, a finding before the task. The cell of `security-audit` at
  `System/Docs/SKILLS.md:142` is wider than 120 characters: 761 at the base, 873 with the clause of
  R3.2. Nineteen rows of the file hold such a cell (CR4-S4-1).

## 8. Measurements of this run

- TASK 129 D9 and §8: the copies that the render page runs, and the advisories of each.
- No rule of `.agent/skills/*/SKILL.md` or `System/Agents/*.md` at the base names a copy outside
  the dependency tree. §6.1 of `security-audit` names a vendored copy for disclosure, and §5.1 of
  `developer-guidelines` names vendored code for bulk rewrites.
- The mirrors of the version of `security-audit` at the base, which TC-04 of
  `tests/test_disclosure_rule.py` reads:
  - `.agent/skills/security-audit/SKILL.md:8@e89753f` `# Security Audit v3.12`
  - `System/Docs/SKILLS.md:142@e89753f` `Vulnerability assessment v3.12`
  - `System/Docs/VDD.md:24@e89753f` `skill (v3.12)`
- TC-3 of `tests/test_run_safety_rules.py` pins the row of `System/Docs/SKILLS.md` whole.
  `tests/run_tests.py` runs the module, and the allow rule `a8ddacaa1aa9` runs that script.
- The scanner states its version in `scripts/run_audit.py`, `scripts/audit/__init__.py` and
  `examples/usage_example.md`. One test reads it for its form only,
  `.agent/skills/security-audit/tests/test_smoke.py`; none compares it with the skill's version.
- The pytest step of the tooling job lists its modules one by one; `tests/run_tests.py` runs the
  modules of `CURATED_UNITTEST_MODULES`.
- CI run 40458599632 of `e89753f`, the commit of TASK 129, passed each of its nine jobs.

<!-- contract:out-of-scope -->

## 9. Out of scope

- A detector of copies in `run_audit.py` (D2).
- An inventory of embedded libraries that no advisory names. No record carries it; R1.4 points to
  an SBOM of the artifacts.
- The bare `pip-audit` of the scanner, a finding before the task (D12).
- The copies that WI-41 tracks: they wait for releases of mermaid and its plugins.
- The task template of `requirements-analysis` (D3).
- The Windows port of the archive chain: TASK 131.
- The claim at `.agent/skills/mermaid-authoring-guidelines/scripts/mermaid_model/kinds.py:27` on
  the zenuml plugin, a finding before TASK 129 that `docs/reviews/code-129-3-review.md` records.
