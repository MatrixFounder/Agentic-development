# Known Issues & Tech Debt

**Purpose:** Track recurring bugs, architectural limitations, and sensitive areas to avoid
repeating mistakes.

This file is a **thin index**. Each issue lives in its own file under
[`docs/issues/`](issues/); the lines below are one-per-issue pointers grouped by category.
Read the linked file for the full symptom, workaround, and cross-links.

---

## Rules / Conventions

> Unlike the `obsidian-llm-wiki` vault this layout is borrowed from, **this repo has no
> `wiki-index-render` tooling** — the index below is **hand-maintained**. When you add,
> resolve, or re-categorize an issue you MUST edit both the per-issue file *and* the matching
> line here. These rules keep that hand-editing consistent.

**Per-issue file** — `docs/issues/<slug>.md`, YAML frontmatter then an H1 title and body:

```yaml
---
id: AT-6                 # <PREFIX>-<n>, unique
type: known-issue        # always this literal
status: open             # see vocab below
opened_at: 2026-04-17    # ISO date the issue was first recorded (git-truthful)
category: agent-teams    # see prefix→category table
severity: SEV-2          # OPTIONAL — omit when not meaningfully rankable
slug: at-6-teamdelete-does-not-clean-up-after-protocol-shutdown  # == filename stem
---
```

**ID prefix → category** (add a row here when introducing a new prefix):

| Prefix | Category      | Scope |
|--------|---------------|-------|
| `AT-N` | `agent-teams` | Native Claude Code Agent Teams (Layer B `TeamCreate`/`SendMessage`) limitations. |
| `ARC-N` | `archiving` | `skill-archive-task` / `task_id_tool.py` defects: ID generation, rotation, lockstep pairing. |
| `WR-N` | `wrappers`    | Thin-wrapper ↔ SOT synchronization hazards (`.claude/agents/` & scaffold dirs). |
| `HK-N` | `hooks`       | Claude Code hook-surface limitations affecting framework capture/automation. |
| `SS-N` | `session-state` | `skill-session-state` protocol/script defects (state resolution, locking, schema). |
| `VAL-N` | `validation` | `skill-creator` validation-gate blind spots (validate_skill.py, structural checks). |
| `RF-N` | `feedback` | `run-feedback` protocol/CLI defects (capture, triage, filing, doctor/init gates). |

**Status vocabulary:** `open` · `fixed` · `documented` (accepted; guidance written) ·
`by-design` (intended trade-off, not a defect) · `mitigated` · `wontfix`.
A `fixed` issue keeps its file and adds a `resolved_at` / `resolved_by` line + a resolution
blockquote; it is not deleted.

**Severity vocabulary (optional):** `SEV-2` (blocks a workflow / real impact) ·
`SEV-3` (degraded / annoying) · `SEV-4` (minor) · `LOW`. Omit for pure documented constraints.

**Index line format** (severity clause omitted when the file has no `severity`):

```
- **<ID>** [<title>](issues/<slug>.md) — severity `<SEV>`, status `<status>`, opened <YYYY-MM-DD>
```

**Adding a new issue:** ① pick the next `<PREFIX>-<n>`; ② create `docs/issues/<slug>.md` with
the frontmatter above (body preserved verbatim — never drop a clause); ③ add one line under
the matching `## <category>` heading here, in ID order.

---

## agent-teams

> These apply to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent`
> tool-uses in one message) is **not** affected.

- **AT-1** [No session resumption](issues/at-1-no-session-resumption.md) — status `documented`, opened 2026-04-17
- **AT-2** [Task status lag](issues/at-2-task-status-lag.md) — severity `SEV-3`, status `documented`, opened 2026-04-17
- **AT-3** [One team per session](issues/at-3-one-team-per-session.md) — status `documented`, opened 2026-04-17
- **AT-4** [No leadership transfer](issues/at-4-no-leadership-transfer.md) — status `documented`, opened 2026-04-17
- **AT-5** [Higher token costs](issues/at-5-higher-token-costs.md) — status `by-design`, opened 2026-04-17
- **AT-6** [`TeamDelete` does NOT clean up after protocol shutdown](issues/at-6-teamdelete-does-not-clean-up-after-protocol-shutdown.md) — severity `SEV-2`, status `open`, opened 2026-04-17
- **AT-7** [Async spawn ≠ sync return](issues/at-7-async-spawn-not-sync-return.md) — status `documented`, opened 2026-04-17
- **AT-8** [Model inheritance inconsistent across agent types](issues/at-8-model-inheritance-inconsistent-across-agent-types.md) — status `documented`, opened 2026-04-17
- **AT-9** [Runtime sends structured JSON despite docs](issues/at-9-runtime-sends-structured-json-despite-docs.md) — status `documented`, opened 2026-04-17

## archiving

- **ARC-1** [task_id_tool counts sub-task files as occupying the parent ID](issues/arc-1-task-id-tool-counts-sub-task-files-as-occupying-the-parent-id.md) — severity `SEV-3`, status `fixed`, opened 2026-08-03 · **fixed 2026-08-04**: the id machinery was already correct; every documented invocation omitted `--proposed-id`. Protocol Steps 3/4 inverted, renumbering opt-in, meta parsing made language-agnostic, Step 5 collision guard added, 86 archive tests wired into CI
- **ARC-2** [Archiving moves an artifact one level deeper and breaks every relative link](issues/arc-2-archiving-moves-an-artifact-one-level-deeper-and-breaks-every-relative-link.md) — severity `SEV-3`, status `fixed`, opened 2026-08-03 · **fixed 2026-08-04**: `rebase_links.py` re-expresses each link's denotation and resolves mutable slots to archive identities; corpus 45 broken → 4 pre-broken, 19 mis-resolutions re-pointed
- **ARC-3** [parse_task_meta's documented "STOP path" for an unreadable/ambiguous meta table does not exist in archive_task…](issues/arc-3-parse-task-meta-s-documented-stop-path-for-an-unreadable-ambiguous-meta-table-does-not-exist-in-archive-task.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **ARC-4** [Step 5.5 tells the agent to pass `--slot docs/PLAN.md=...` unconditionally, while archive_protocol.py delibera…](issues/arc-4-step-5-5-tells-the-agent-to-pass-slot-docs-plan-md-unconditionally-while-archive-protocol-py-delibera.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **ARC-5** [The "conservation law" gate is unreachable: `failed` can never become True, so exit code 1 is dead](issues/arc-5-the-conservation-law-gate-is-unreachable-failed-can-never-become-true-so-exit-code-1-is-dead.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **ARC-6** [A `--slot` map whose target does not exist rewrites the link and exits 0 (`"ok": true`) because SLOT_RESOLVED …](issues/arc-6-a-slot-map-whose-target-does-not-exist-rewrites-the-link-and-exits-0-ok-true-because-slot-resolved.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **ARC-7** [The Python function default for `allow_correction` was NOT flipped and still defaults to True, directly contra…](issues/arc-7-the-python-function-default-for-allow-correction-was-not-flipped-and-still-defaults-to-true-directly-contra.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **ARC-8** [The CLI](issues/arc-8-the-cli.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **ARC-9** [`TestSchemaMatchesTheDispatcher.test_schema_default_matches_tool_runner_default` never imports or inspects `to…](issues/arc-9-testschemamatchesthedispatcher-test-schema-default-matches-tool-runner-default-never-imports-or-inspects-to.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **ARC-10** [Step 7.4 still mandates the pre-flip contract](issues/arc-10-step-7-4-still-mandates-the-pre-flip-contract.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **ARC-11** [A sixth invocation site of the bare `task_id_tool.py <slug>` form that the commit's own audit did not enumerat…](issues/arc-11-a-sixth-invocation-site-of-the-bare-task-id-tool-py-slug-form-that-the-commit-s-own-audit-did-not-enumerat.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **ARC-12** [The new Step 4 ID write-back keys on the English literal `Task ID`, while `parse_task_meta` was deliberately m…](issues/arc-12-the-new-step-4-id-write-back-keys-on-the-english-literal-task-id-while-parse-task-meta-was-deliberately-m.md) — severity `SEV-4`, status `open`, opened 2026-08-04

## feedback

- **RF-1** [doctor reports ready:true on built-in defaults, contradicting its own remediation](issues/rf-1-doctor-reports-ready-true-on-built-in-defaults-contradicting-its-own-remediation.md) — severity `SEV-4`, status `fixed`, opened 2026-07-13 · **fixed 2026-07-30** (TASK 095): `configured` is now a check and part of `ready`; E2E, cli_reference and SKILL.md §7 updated in lockstep
- **RF-2** [file accepts an unvalidated issue body and dry-run never previews it](issues/rf-2-file-accepts-an-unvalidated-issue-body-and-dry-run-never-previews-it.md) — severity `SEV-3`, status `fixed`, opened 2026-07-14 · **fixed 2026-07-30** (TASK 095): unbalanced fence + missing Reproduction refused at exit 4, and `--dry-run` echoes the rendered record


## hooks

- **HK-1** [PostToolUse fires only on successful tool calls — cannot capture Bash failures](issues/hk-1-posttooluse-fires-only-on-successful-tool-calls-cannot-capture-bash-failures.md) — status `documented`, opened 2026-07-13

## register

- **REG-1** [The rule-3 (reasoning) detector probes only the ONE modal/causal pair that happens to appear in the declared p…](issues/reg-1-the-rule-3-reasoning-detector-probes-only-the-one-modal-causal-pair-that-happens-to-appear-in-the-declared-p.md) — severity `SEV-2`, status `fixed`, opened 2026-08-04 · **fixed 2026-08-04** (TASK 097): every rule-3 pattern carries a declared example and is exercised against a known-good partner — 11 en and 13 ru patterns, against 1 before. Editing a pattern without its example is refused at load
- **REG-2** [TC-PROBE-02 derives its `expected` detector count from the very rule files under test, so it cannot fail for t…](issues/reg-2-tc-probe-02-derives-its-expected-detector-count-from-the-very-rule-files-under-test-so-it-cannot-fail-for-t.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **REG-3** [The `reasoning` probe row can never report DEAD: rule loading already makes "the declared probe fires" a preco…](issues/reg-3-the-reasoning-probe-row-can-never-report-dead-rule-loading-already-makes-the-declared-probe-fires-a-preco.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **REG-4** [`--probe` enumerates only the detector classes that exist in the data, so removing a whole detector class shri…](issues/reg-4-probe-enumerates-only-the-detector-classes-that-exist-in-the-data-so-removing-a-whole-detector-class-shri.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-5** [`dequote()` has no regression pin for the defect its own docstring says it exists to fix (a table inside a `> …](issues/reg-5-dequote-has-no-regression-pin-for-the-defect-its-own-docstring-says-it-exists-to-fix-a-table-inside-a.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **REG-6** [Only the `e.g.` abbreviation lookbehind in SENT_SPLIT is pinned by a test](issues/reg-6-only-the-e-g-abbreviation-lookbehind-in-sent-split-is-pinned-by-a-test.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-7** [Two of the three cross-key threshold invariants in `check_thresholds` are unexercised by any selftest case](issues/reg-7-two-of-the-three-cross-key-threshold-invariants-in-check-thresholds-are-unexercised-by-any-selftest-case.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-8** [The battery's case count is documented as a contract in four places but is never asserted](issues/reg-8-the-battery-s-case-count-is-documented-as-a-contract-in-four-places-but-is-never-asserted.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-9** [measurement-baseline.md records negative parallelism as an ADOPTED rule (`info`, RU only), but no such entry e…](issues/reg-9-measurement-baseline-md-records-negative-parallelism-as-an-adopted-rule-info-ru-only-but-no-such-entry-e.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-10** [The baseline states `✓`/`✗` are excluded from rule 5 unconditionally](issues/reg-10-the-baseline-states-are-excluded-from-rule-5-unconditionally.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **REG-11** [The EN rule-4 category has no counterpart to the RU red/green verb personification entry, although authoring-c…](issues/reg-11-the-en-rule-4-category-has-no-counterpart-to-the-ru-red-green-verb-personification-entry-although-authoring-c.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-12** [The EN rule-2 lexicon has no counterpart to the RU "главная опасность / главная проблема" ranking entry, altho…](issues/reg-12-the-en-rule-2-lexicon-has-no-counterpart-to-the-ru-ranking-entry-altho.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **REG-13** [SKILL.md states two different, both wrong, counts for the licensed statement forms in authoring-contract.md](issues/reg-13-skill-md-states-two-different-both-wrong-counts-for-the-licensed-statement-forms-in-authoring-contract-md.md) — severity `SEV-4`, status `open`, opened 2026-08-04


## session-state

- **SS-1** [update_state.py resolves .agent/sessions relative to CWD — stray state when run from a subdir](issues/ss-1-update-state-py-resolves-agent-sessions-relative-to-cwd-stray-state-when-run-from-a-subdir.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13
- **SS-2** [Session state latest.yaml is git-tracked — every protocol run dirties the tree](issues/ss-2-session-state-latest-yaml-is-git-tracked-every-protocol-run-dirties-the-tree.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13

## validation

- **FW-1** [Spec-validator bypass token matches anywhere in content](issues/validator-bypass-substring.md) — severity `SEV-4`, status `open`, opened 2026-07-20
- **VAL-1** [validate_skill.py passes frontmatter that strict YAML parsers reject (unquoted colon in description)](issues/val-1-validate-skill-py-passes-frontmatter-that-strict-yaml-parsers-reject-unquoted-colon-in-description.md) — severity `SEV-4`, status `fixed`, opened 2026-07-13
- **VAL-2** [run_eval.py trigger probe false-negatives: name competition with installed skill and first-call strictness](issues/val-2-run-eval-py-trigger-probe-false-negatives-name-competition-with-installed-skill-and-first-call-strictness.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13 · **fixed 2026-07-30** (v3.21.10, `31db854`): both names counted, exact matching, an 8-call budget across message boundaries; instrument failure now distinguishable from a real non-trigger

## wiring

- **WIR-1** [The commit added `rebase_links.py` to the safe-command list but not `scan_register.py`, even though six instru…](issues/wir-1-the-commit-added-rebase-links-py-to-the-safe-command-list-but-not-scan-register-py-even-though-six-instru.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **WIR-2** [The commit removed glyph severities from the four review checklists and declared "Severity is a named value, n…](issues/wir-2-the-commit-removed-glyph-severities-from-the-four-review-checklists-and-declared-severity-is-a-named-value-n.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **WIR-3** [The TASK template the Analyst is required to follow](issues/wir-3-the-task-template-the-analyst-is-required-to-follow.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **WIR-4** [The canonical "good" TASK exemplar that `skill-task-model` (TIER 1, Analysis) points the Analyst at demonstrat…](issues/wir-4-the-canonical-good-task-exemplar-that-skill-task-model-tier-1-analysis-points-the-analyst-at-demonstrat.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **WIR-5** [The Primary Command hard-codes the glob `docs/architectures/*.md`, which does not exist in the normal (single-…](issues/wir-5-the-primary-command-hard-codes-the-glob-docs-architectures-md-which-does-not-exist-in-the-normal-single.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **WIR-6** [The Primary Command scopes the register scan over `docs/tasks/*.md`, which is the framework's permanent archiv…](issues/wir-6-the-primary-command-scopes-the-register-scan-over-docs-tasks-md-which-is-the-framework-s-permanent-archiv.md) — severity `SEV-3`, status `open`, opened 2026-08-04
- **WIR-7** [The commit replaced the Analyst's manual Task-ID procedure with a mandatory shell command and explicitly forba…](issues/wir-7-the-commit-replaced-the-analyst-s-manual-task-id-procedure-with-a-mandatory-shell-command-and-explicitly-forba.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **WIR-8** [`rebase_links.py` was added to skill-safe-commands but not to the Claude Code permission allow-list that mirro…](issues/wir-8-rebase-links-py-was-added-to-skill-safe-commands-but-not-to-the-claude-code-permission-allow-list-that-mirro.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **WIR-9** [The "advisory" register-scan step exits 2](issues/wir-9-the-advisory-register-scan-step-exits-2.md) — severity `SEV-2`, status `fixed`, opened 2026-08-04 · **fixed 2026-08-04** (TASK 097): an unreadable path exits 3, not 2; `--allow-missing` names and skips the artifacts this framework archives, and the CI step passes in the archived state
- **WIR-10** [The ARC-1 default flip was applied to schemas.py and tool_runner.py but not to the CLI/library entry point the…](issues/wir-10-the-arc-1-default-flip-was-applied-to-schemas-py-and-tool-runner-py-but-not-to-the-cli-library-entry-point-the.md) — severity `SEV-4`, status `open`, opened 2026-08-04
- **WIR-11** [Four review checklists were rewritten to forbid glyph severities as a normative rule, but the reviewer prompts…](issues/wir-11-four-review-checklists-were-rewritten-to-forbid-glyph-severities-as-a-normative-rule-but-the-reviewer-prompts.md) — severity `SEV-4`, status `open`, opened 2026-08-04



## wrappers

- **WR-1** [Wrapper/SOT drift risk](issues/wr-1-wrapper-sot-drift-risk.md) — severity `SEV-3`, status `documented`, opened 2026-06-10
