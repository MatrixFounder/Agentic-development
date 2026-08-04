---
name: skill-archive-task
description: "Complete protocol for archiving TASK.md and PLAN.md (lockstep) with ID generation. Single source of truth for archiving."
tier: 1
version: 2.0
---
# Task Archiving Protocol

This skill encapsulates the complete protocol for archiving `docs/TASK.md` to `docs/tasks/`
and `docs/PLAN.md` to `docs/plans/` (in lockstep with TASK.md).

## When to Archive

Archive `docs/TASK.md` **ONLY** when:
1. Starting a **NEW** task AND `docs/TASK.md` exists with **DIFFERENT** content
2. **Completing** a task (Orchestrator Completion stage)

**DO NOT** archive when:
- Refining/clarifying the **CURRENT** task (overwrite instead)
- `docs/TASK.md` does not exist

> [!IMPORTANT]
> **PLAN.md rotates in lockstep with TASK.md.** Whenever TASK.md is archived for a
> NEW task, the old `docs/PLAN.md` (if present) is archived too — see
> **"PLAN.md Archiving (Lockstep)"** below. On task refinement, PLAN.md is overwritten
> in place, never archived. `docs/ARCHITECTURE.md` is a LIVING document and is **never**
> touched by this skill.

## Decision Logic: New vs Refinement

```
IF user request implies a NEW SEPARATE feature/refactor:
    → Archive existing TASK.md, then create new
    
IF user request is a clarification/refinement of CURRENT task:
    → Overwrite TASK.md, do NOT archive
```

**Indicators of NEW task:**
- Different feature/component mentioned
- "Create new task for...", "Start working on..."
- Completed previous task

**Indicators of REFINEMENT:**
- "Clarify requirement X", "Add detail to..."
- Same feature context as current TASK.md

## Protocol Steps

### Step 1: Check Condition
```
IF NOT exists("docs/TASK.md"):
    SKIP archiving → Create new TASK.md
```

### Step 2: Extract Metadata
Read from current `docs/TASK.md`:
- **Task ID** from "0. Meta Information" section
- **Slug** from "0. Meta Information" section

**If Meta Information is missing or malformed:**
- Use slug from task title (H1 header)
- Generate ID via tool if available, otherwise use `000` or increment last known ID manually.

### Step 3: Generate Filename

**The ID comes from the DOCUMENT, not from the directory.** Step 2 already read it from the Meta
block; Step 3 only confirms it is free and turns it into a filename.

**Option A: Use Tool (Preferred)**

```bash
python3 .agent/tools/task_id_tool.py "<slug-from-meta>" --proposed-id "<id-from-meta>" --no-correction
```

```python
result = generate_task_archive_filename(
    slug=slug_from_meta,
    proposed_id=task_id_from_meta,   # MANDATORY whenever Step 2 found an ID
    allow_correction=False,          # a cited ID is never renumbered silently
)
```

- **`proposed_id` is mandatory whenever Step 2 produced an ID.** Omit it and the tool
  auto-generates `max(existing)+1`, and that scan counts the task's **own** planner sub-task files
  (`task-NNN-SubID-slug.md`). A task with sub-tasks and no parent archive is then handed `NNN+1` —
  a number contradicting its Meta block, its `docs/plans/plan-NNN-*.md`, its sub-tasks and every
  commit citing it (**ARC-1**).
- Omit `proposed_id` **only** when Step 2 found no ID. That is the sole case where the tool may
  choose, and the sole case where Step 4 writes an ID back.
- Read `result["status"]`: `"generated"` → continue. `"conflict"` → **STOP**, report both paths,
  the operator decides. `"error"` → STOP.
- A populated **sub-task namespace is not a conflict** — with `--proposed-id` the tool checks
  parent archives only.

**Option B: Manual Generation (Fallback)**
1. Filename = `task-<ID-from-Meta>-<slug-from-Meta>.md`. The ID is **copied, never invented**.
2. Conflict check, parents only:
   `ls docs/tasks/task-<ID>-*.md` — hits shaped `task-<ID>-<digits>-*` are SUB-TASKS, expected, not
   conflicts. Any other hit, or any `docs/plans/plan-<ID>-*.md`, is a real conflict → STOP.
3. Only if Step 2 found no ID: `NNN = max(ID over docs/tasks/ and docs/plans/) + 1`, sub-tasks
   **included** in that maximum — a populated namespace reserves its parent's number.

### Step 4: Verify the ID — do NOT renumber

The Meta-block ID is the identity; the filename follows it. This step **asserts**, it does not
assign.

```
ASSERT id_in_filename == id_in_meta_block
IF they differ: STOP. Do not move the file. Report both values.
```

Do **not** edit `docs/TASK.md` here. By archiving time the ID is cited outside the Meta row:
sub-task files, the plan archive, commit messages, `CHANGELOG.md`, ledger records, and the
document's own H1. Rewriting one row silently falsifies the rest.

**Writing an ID back is legitimate in exactly two cases:**

1. **Meta carries no ID** — nothing is being overwritten.
2. **The ID was never published** — no sub-tasks, no plan archive, no commit or ledger row cites
   it, confirmed by the operator. Then it is a rename of a private draft, and it is a
   **whole-document** edit: Meta row, H1, `Archive name` and every in-body citation move together.

### Step 5: Archive (Move File)

**Collision guard first.** `mv` overwrites, and Step 3's conflict check sees *parent* archives
only — a destination shaped like a sub-task (`task-096-01-x.md`) is invisible to it.

```bash
test -e docs/tasks/{filename} && echo "STOP: target exists" || mv docs/TASK.md docs/tasks/{filename}
```

> [!IMPORTANT]
> The `mv` is **SAFE TO AUTO-RUN**. Do NOT wait for user approval.

### Step 5.5: Rebase the moved document's links (MANDATORY)

`docs/tasks/` is one directory **deeper** than `docs/`. Every relative link in the document was
written against `docs/` and now denotes a different path, or nothing (**ARC-2**).

```bash
python3 .agent/tools/rebase_links.py docs/tasks/{filename} --from docs --to docs/tasks
```

- **Do not hand-edit links.** A rule like "replace `../` with `../../`" fixes **zero** of the
  forms this corpus actually contains — measured. The tool computes what each link denoted from
  the old directory and re-expresses that same denotation from the new one.
- **`docs/PLAN.md` is a mutable slot, not an identity.** A link to it inside this task means *this
  task's* plan, which Step 7 is about to archive. Pass the pairing so the link is written to the
  archive name rather than to a path that dies seconds later:
  `--slot docs/PLAN.md=docs/plans/plan-{used_id}-{slug}.md`
- **Pass that slot ONLY when `docs/PLAN.md` exists** (ARC-4). A task that reached analysis but not
  planning has no plan to archive, so Step 7.1 will skip it and the mapped file is never created.
  Mapping it anyway authors a citation to a path that will not exist and reports success.
  `archive_protocol.py:363-366` implements the condition; `TestPlanSlotIsConditional` pins it.
  Without the slot the same link is reported as `UNMAPPED_SLOT` and left alone, which is correct.
- Exit `0` clean, `3` needs review, `1` a link regressed, `2` could not run. A `3` lists links that
  were **left alone** — broken before the move, or resolving only by accident. Never "fix" those
  by guessing; report them.

### Step 6: Validate
Verify:
- [ ] `docs/TASK.md` does NOT exist
- [ ] `docs/tasks/{filename}` exists
- [ ] **Every link the document denoted before the move still resolves.** File-arrived is not
      enough: the move can leave a present file full of dead citations. `rebase_links.py` exits
      non-zero when a link it rewrote fails to resolve.

**If validation fails:**
- Check if mv command returned error
- If `docs/TASK.md` still exists: retry mv or notify user
- DO NOT create new TASK.md until validation passes

## PLAN.md Archiving (Lockstep)

`docs/PLAN.md` has no Meta block or identity of its own, and there is always exactly
one PLAN per TASK. Therefore PLAN.md is **never archived independently** — it rotates
**in lockstep** with TASK.md, reusing the **same ID and slug** TASK.md was just archived
under.

> Result: `docs/tasks/task-NNN-slug.md` ↔ `docs/plans/plan-NNN-slug.md` always pair up.

> [!IMPORTANT]
> `docs/tasks/` is shared — it also holds planner sub-task files
> (`task-NNN-SubID-slug.md`). PLAN.md therefore archives to a **separate** `docs/plans/`
> directory, **never** to `docs/tasks/`.

### Step 7: Archive PLAN.md (Lockstep)

Run this **only after Step 6 validation passed** (TASK.md successfully archived for a
NEW task). Execute sub-steps 7.1–7.7 in order.

**7.1 — Condition check.** No PLAN.md means the task never reached planning:

```
IF NOT exists("docs/PLAN.md"):
    SKIP plan archiving → DONE
```

**7.2 — Refinement guard.** Step 7 is normally only reached on the NEW-task path; this
guard is stated explicitly so re-planning the SAME task overwrites `docs/PLAN.md`:

```
IF Step 1 decision was REFINEMENT (not a NEW task):
    DO NOT archive PLAN.md — Planner overwrites it in place → DONE
```

**7.3 — Ensure destination** (idempotent, SAFE TO AUTO-RUN):

```bash
mkdir -p docs/plans
```

**7.4 — Derive filename** (NO new ID generation):

```
plan_filename = "plan-{used_id}-{slug}.md"
```

`{used_id}` and `{slug}` are REUSED VERBATIM from the TASK.md archive just completed — the
`used_id` returned by `generate_task_archive_filename` in Step 3, which Step 4 already asserted
equal to the Meta-block ID.

Under this protocol the two values cannot differ (**ARC-10**). Step 3 runs with correction OFF, so
`status: "corrected"` is unreachable and a collision returns `"conflict"` → STOP. Step 4 then
asserts `id_in_filename == id_in_meta_block` and stops on a mismatch, before Step 7 is ever
entered. The one path where a corrected ID survives is the automated mirror called as
`archive_protocol.archive_task(allow_renumber=True)`; there TASK and PLAN both take the corrected
ID and stay paired.

**7.5 — Collision guard:**

```
IF exists("docs/plans/{plan_filename}"):
    STOP. Do NOT overwrite. Report to user:
      "Plan archive collision: docs/plans/{plan_filename} already exists."
```

**7.6 — Archive (move):**

```bash
mv docs/PLAN.md docs/plans/{plan_filename}
```

**7.6.5 — Rebase the plan's links** (mirrors Step 5.5):

```bash
python3 .agent/tools/rebase_links.py docs/plans/{plan_filename} \
  --from docs --to docs/plans --slot-must-exist \
  --slot docs/TASK.md=docs/tasks/task-{used_id}-{slug}.md
```

The slot is **not optional here**. By this point `docs/TASK.md` is already gone — Step 5 moved it,
and Step 7 runs only after Step 6 passed. An existence-based rule would see the plan's
`[docs/TASK.md](TASK.md)` as broken both before and after, leave it dead forever, and report
nothing. The slot map carries the identity without touching the filesystem.

`--slot-must-exist` is **required here and forbidden at Step 5.5** (**ARC-6**). Here the TASK
archive was created in Step 5, so a mistyped `{slug}` names a file that is already absent and the
tool exits 1. At Step 5.5 the plan archive does not exist yet, so the same assertion would fail the
protocol's own happy path. Without the flag a one-character slug typo rewrote the citation and
returned exit 0 with `"ok": true`, and Step 7.7's assertion passed on a dead link.

**7.7 — Validate:**

```
ASSERT NOT exists("docs/PLAN.md")
ASSERT exists("docs/plans/{plan_filename}")
ASSERT every link denoted before the move still resolves   # rebase_links exit code
IF validation fails: retry mv once, else notify user.
```

### Edge Cases

| Case | Behavior |
|------|----------|
| `docs/PLAN.md` absent | Skip silently (7.1). Not an error — many tasks reach analysis but not planning. |
| Task refinement (same task) | Step 7.2 returns early. PLAN.md is overwritten in place by the Planner. |
| `docs/plans/` missing | `mkdir -p` in 7.3 creates it. |
| Corrected `used_id` | Unreachable under this protocol: Step 3 runs correction OFF and Step 4 stops on a mismatch. Only `archive_task(allow_renumber=True)` reaches it, and there 7.4 keeps TASK and PLAN paired. |
| **Orphan PLAN.md** (PLAN.md exists, no TASK.md) | Step 1 skipped archiving (no TASK.md) → Step 7 is never reached. The orphan PLAN.md is **left in place**. Warn the user it may be stale. PLAN.md has no independent ID, so it cannot be safely archived alone — this is a deliberate limitation. |

## Safe Commands (AUTO-RUN)

> See **`skill-safe-commands`** for the authoritative list of commands safe for auto-execution.

Key commands for this skill:
- `mv docs/TASK.md docs/tasks/...` — archiving TASK.md
- `mv docs/PLAN.md docs/plans/...` — archiving PLAN.md (lockstep)
- `mkdir -p docs/plans` — ensure PLAN archive destination exists
- `ls`, `cat` — validation


## Safety Boundaries

This skill performs **file mutations** (`mv`, `mkdir`). The following boundaries apply:

- **Move, never delete.** Archiving uses `mv` only — `docs/TASK.md` / `docs/PLAN.md`
  content is relocated, never destroyed.
- **No overwrite.** Step 5 and Step 7.5 enforce collision guards: if the target archive
  filename already exists, **STOP** and report — never overwrite an existing archive.
- **Lockstep integrity.** PLAN.md is archived only after TASK.md archiving is validated
  (Step 6). A failed TASK archive aborts the PLAN archive.
- **Living documents untouched.** `docs/ARCHITECTURE.md` is never moved or archived.
- **Validate before proceeding.** Each `mv` is followed by an existence assertion
  (Steps 6, 7.7); on failure, retry once then notify the user — do not continue blindly.

## Integration

### Required by Agents
- **Analyst** (`02_analyst_prompt.md`): Before creating new TASK.md
- **Orchestrator** (`01_orchestrator.md`): At Completion stage

## Example Flow

**Trigger:** User says *"Create new task for implementing login feature."*

1. Agent loads `skill-archive-task`.
2. Checks `docs/TASK.md` exists? → YES (contains `Task {OLD_ID}: {Old Feature}`).
3. Decision: NEW task (different feature) → Archive.
4. **Step 2** — read the Meta block: Task ID = `{OLD_ID}`, Slug = `{old-slug}`.
   The ID comes from the **document**, never from the directory listing.
5. **Step 3** — confirm the ID is free and turn it into a filename. `--proposed-id` is
   mandatory here, because Step 2 produced an ID:
   ```bash
   python3 .agent/tools/task_id_tool.py "{old-slug}" --proposed-id "{OLD_ID}" --no-correction
   ```
   `status: "conflict"` → **STOP**; the operator decides. Sub-task files matching
   `task-{OLD_ID}-<digits>-*` are **not** a conflict.
6. **Step 4** — assert `id_in_filename == {OLD_ID}`. This step never assigns.
7. **Step 5** — collision guard, then move:
   ```bash
   test -e docs/tasks/task-{OLD_ID}-{old-slug}.md \
     && echo "STOP: target exists" \
     || mv docs/TASK.md docs/tasks/task-{OLD_ID}-{old-slug}.md
   ```
8. **Step 5.5** — rebase the moved document's links. `docs/tasks/` is one level deeper, so every
   relative link now denotes something else. `docs/PLAN.md` is a slot, so pass the pairing Step 7
   is about to create — **only because `docs/PLAN.md` exists in this example**:
   ```bash
   python3 .agent/tools/rebase_links.py docs/tasks/task-{OLD_ID}-{old-slug}.md \
     --from docs --to docs/tasks \
     --slot docs/PLAN.md=docs/plans/plan-{OLD_ID}-{old-slug}.md
   ```
   With no `docs/PLAN.md`, drop the `--slot` line entirely (ARC-4). Do NOT add `--slot-must-exist`
   here: the plan archive is created in step 10, so this slot is a forward reference.
   Exit `3` lists links left alone deliberately — report them, never guess a target.
9. **Step 6** — validate: `docs/TASK.md` gone ✓, archive present ✓, links still resolve ✓.
10. **Step 7** — PLAN lockstep. `docs/PLAN.md` exists? → YES.
    - `mkdir -p docs/plans`, reuse `{OLD_ID}` + `{old-slug}` from the TASK archive above.
    - Collision guard, then `mv docs/PLAN.md docs/plans/plan-{OLD_ID}-{old-slug}.md`.
    - **Step 7.6.5** — rebase, with `docs/TASK.md` mapped to the archive it just became:
      ```bash
      python3 .agent/tools/rebase_links.py docs/plans/plan-{OLD_ID}-{old-slug}.md \
        --from docs --to docs/plans --slot-must-exist \
        --slot docs/TASK.md=docs/tasks/task-{OLD_ID}-{old-slug}.md
      ```
      The slot map is resolved before any filesystem probe, which is why it still works here —
      `docs/TASK.md` was moved away in step 7 above. `--slot-must-exist` belongs here and not in
      step 8: the TASK archive already exists, so a mistyped `{old-slug}` exits 1 (ARC-6).
    - Validate: `docs/PLAN.md` does NOT exist ✓.
11. Create new `docs/TASK.md` for the login feature with ID `{NEW_ID}`.

