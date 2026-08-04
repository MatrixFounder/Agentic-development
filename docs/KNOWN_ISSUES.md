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

## feedback

- **RF-1** [doctor reports ready:true on built-in defaults, contradicting its own remediation](issues/rf-1-doctor-reports-ready-true-on-built-in-defaults-contradicting-its-own-remediation.md) — severity `SEV-4`, status `fixed`, opened 2026-07-13 · **fixed 2026-07-30** (TASK 095): `configured` is now a check and part of `ready`; E2E, cli_reference and SKILL.md §7 updated in lockstep
- **RF-2** [file accepts an unvalidated issue body and dry-run never previews it](issues/rf-2-file-accepts-an-unvalidated-issue-body-and-dry-run-never-previews-it.md) — severity `SEV-3`, status `fixed`, opened 2026-07-14 · **fixed 2026-07-30** (TASK 095): unbalanced fence + missing Reproduction refused at exit 4, and `--dry-run` echoes the rendered record


## hooks

- **HK-1** [PostToolUse fires only on successful tool calls — cannot capture Bash failures](issues/hk-1-posttooluse-fires-only-on-successful-tool-calls-cannot-capture-bash-failures.md) — status `documented`, opened 2026-07-13

## session-state

- **SS-1** [update_state.py resolves .agent/sessions relative to CWD — stray state when run from a subdir](issues/ss-1-update-state-py-resolves-agent-sessions-relative-to-cwd-stray-state-when-run-from-a-subdir.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13
- **SS-2** [Session state latest.yaml is git-tracked — every protocol run dirties the tree](issues/ss-2-session-state-latest-yaml-is-git-tracked-every-protocol-run-dirties-the-tree.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13

## validation

- **FW-1** [Spec-validator bypass token matches anywhere in content](issues/validator-bypass-substring.md) — severity `SEV-4`, status `open`, opened 2026-07-20
- **VAL-1** [validate_skill.py passes frontmatter that strict YAML parsers reject (unquoted colon in description)](issues/val-1-validate-skill-py-passes-frontmatter-that-strict-yaml-parsers-reject-unquoted-colon-in-description.md) — severity `SEV-4`, status `fixed`, opened 2026-07-13
- **VAL-2** [run_eval.py trigger probe false-negatives: name competition with installed skill and first-call strictness](issues/val-2-run-eval-py-trigger-probe-false-negatives-name-competition-with-installed-skill-and-first-call-strictness.md) — severity `SEV-3`, status `fixed`, opened 2026-07-13 · **fixed 2026-07-30** (v3.21.10, `31db854`): both names counted, exact matching, an 8-call budget across message boundaries; instrument failure now distinguishable from a real non-trigger


## wrappers

- **WR-1** [Wrapper/SOT drift risk](issues/wr-1-wrapper-sot-drift-risk.md) — severity `SEV-3`, status `documented`, opened 2026-06-10
