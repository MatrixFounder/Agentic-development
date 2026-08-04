---
id: ARC-11
type: known-issue
status: fixed
opened_at: 2026-08-04
resolved_at: 2026-08-04
resolved_by: TASK 098
category: archiving
severity: SEV-3
slug: arc-11-a-sixth-invocation-site-of-the-bare-task-id-tool-py-slug-form-that-the-commit-s-own-audit-did-not-enumerat
provenance: machine
component: '.claude/agents/planner.md'
fingerprint: c6dd30c4445abbed
finding_ref: fnd-20260804-152825-c6dd30c4
---

# ARC-11 — A sixth invocation site of the bare `task_id_tool.py <slug>` form that the commit's own audit did not enumerat…

> Filed by `run-feedback` from capture `fnd-20260804-152825-c6dd30c4`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.


> **Resolved 2026-08-04** (TASK 098). `.claude/agents/planner.md:12` now instructs the planner to read the Task ID from the `docs/TASK.md` Meta block and reuse it for every sub-task filename, per `06_planner_prompt.md` Step 1, and states why the bare call is wrong. `docs/ARCHITECTURE.md:169` no longer claims the planner uses `task_id_tool.py`. A sweep of every live markdown invocation site found no other card carrying the generate-an-ID form.
**Component:** `.claude/agents/planner.md:12`

## Symptom

A sixth invocation site of the bare `task_id_tool.py <slug>` form that the commit's own audit did not enumerate (it lists four bootstrap docs plus skill-archive-task). It instructs the planner subagent to generate IDs for per-task files, contradicting `06_planner_prompt.md:40` which forbids generating an ID at all.

## Reproduction

`System/Agents/06_planner_prompt.md:40` — "Extract: Task ID (e.g., `002`) and Slug. **Use this ID for ALL filenames.**" and :75 — `docs/tasks/task-{ID}-{SubID}-{slug}.md`. The subagent card says the opposite: run the tool to "generate unique IDs". Concrete: TASK.md Meta ID = 095, planner already wrote `task-095-01..03-*.md`, user re-runs `/plan` after a TASK revision. The bare call scans `docs/tasks/`, sees 095 occupied (sub-tasks count on the auto-generate path — this is exactly the ARC-1 shadowing measured in `TestBareInvocationShadowsTheParentId`), returns `used_id: "096"`, and the second sub-task batch lands as `task-096-01-*.md` while TASK.md, `plan-095-*` and every commit say 095. Sub-tasks are orphaned from their parent and 096 is poisoned for the next real task. CLAUDE.md:29-33 was amended in this commit to declare the bare form wrong; this file was not.

## Evidence

.claude/agents/planner.md:12 — "Use `python3 .agent/tools/task_id_tool.py <slug>` to generate unique IDs (returns JSON with `filename`/`used_id`)." vs System/Agents/06_planner_prompt.md:40 — "**Extract:** Task ID (e.g., `002`) and Slug. Use this ID for ALL filenames."

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Confirmed on all counts, and the harm is worse than stated. .claude/agents/planner.md:12 reads verbatim "Use `python3 .agent/tools/task_id_tool.py <slug>` to generate unique IDs (returns JSON with `filename`/`used_id`)"; 06_planner_prompt.md Step 1 says "Extract: Task ID (e.g., `002`) and Slug. Use this ID for ALL filenames" and Step 3 emits `docs/tasks/task-{ID}-{SubID}-{slug}.md`. `grep -rn task_id_tool.py --include=*.md` confirms planner.md is a live invocation site the ARC-1 record's enumeration (CLAUDE.md, AGENTS.md, GEMINI.md, ORCHESTRATOR.md + skill-archive-task) omits, and docs/ARCHITECTURE.md:169 propagates it ("uses `task_id_tool.py`"). Measured against the real repo, no re-run needed: `python3 .agent/tools/task_id_tool.py "structural-anchors"` → `{"used_id": "097", "status": "generated"}`, EXIT 0, while `docs/TASK.md:9` reads `| Task ID | 096 |`. A planner following its card on the FIRST /plan run therefore writes `task-097-01-*.md` for TASK 096 — orphaned from the parent and poisoning 097. Severity medium stands; the only mitigation is line 8's "read and follow strictly" pointer to the authoritative prompt, which the "Subagent adaptations" heading below it normally overrides.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `allow-correction-flip`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
