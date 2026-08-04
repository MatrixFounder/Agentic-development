"""
Archive Protocol Module

Testable Python implementation of the archiving protocol from
skill-archive-task: TASK.md archiving (Steps 1-6) and PLAN.md
lockstep archiving (Step 7). This module enables automated testing
of the archiving scenarios.

Note: This duplicates logic from skill-archive-task for testability.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional

from task_id_tool import generate_task_archive_filename, normalize_slug


#: Structural address of the meta section, registered in
#: `documentation-standards` §4.4. Checked before the English prose probes so
#: that a TASK.md in any language is read correctly.
META_ANCHOR = "<!-- contract:meta -->"


def parse_task_meta(content: str) -> dict:
    """
    Extract Task ID and Slug from TASK.md content.
    
    Args:
        content: Full content of TASK.md file
    
    Returns:
        dict with keys:
            - task_id: str or None if not found
            - slug: str or None if not found
            - has_meta: bool indicating if Meta section exists
            - id_ambiguous: bool, True when the meta region carried more than
              one 3-digit value and the structural read refused to pick one
            - slug_unreadable: bool, True when a meta region is present and no
              slug could be read from it

    The last two are the REFUSAL REASONS (ARC-3). Before them the caller could
    not tell "this document has no ID" from "this document has an ID I refuse
    to guess at", and both arrived as `task_id=None` -- which archive_task()
    turned into an auto-generated number over a set that counts sub-task files.
    """
    result = {
        "task_id": None,
        "slug": None,
        "has_meta": False,
        "id_ambiguous": False,
        "slug_unreadable": False,
    }
    
    # Locate the meta section. The anchor is checked FIRST and in any language;
    # the two English prose probes stay as the fallback for every TASK.md
    # written before the anchor existed (`documentation-standards` §4.3/§4.4).
    # The prose probe alone was already too narrow for this framework's own
    # template, which heads the section `## 0. Meta` — so archiving quietly
    # took the H1 fallback path on documents that DO have a meta table.
    if (META_ANCHOR not in content
            and "## 0. Meta Information" not in content
            and "Meta Information" not in content):
        # Fallback: try to extract slug from H1 header
        h1_match = re.search(r'^#\s+(?:Task\s+\d+:\s+)?(.+)$', content, re.MULTILINE)
        if h1_match:
            # Convert title to slug. Delegated, never re-implemented: this used
            # its own `[^a-zA-Z0-9]+` class, which deleted a non-latin title
            # outright and let it fall through to the shared "untitled", so two
            # different tasks archived over one filename (TASK 095 / WI-30).
            result["slug"] = normalize_slug(h1_match.group(1).strip())
        return result

    result["has_meta"] = True

    # Extract Task ID from table format: | Task ID  | 042 |
    id_match = re.search(r'\|\s*Task ID\s*\|\s*(\d+)\s*\|', content)
    if id_match:
        result["task_id"] = id_match.group(1)

    # Extract Slug from table format: | Slug | existing-feature |
    # The VALUE is captured as "anything but a pipe" and then normalized, rather
    # than matched against `[a-z0-9-]+`: a charset that admits only latin cannot
    # tell "no slug row" from "a slug row I refuse to read", and both produced
    # the same silent "untitled".
    slug_match = re.search(r'\|\s*Slug\s*\|\s*([^|]+?)\s*\|', content)
    if slug_match:
        result["slug"] = normalize_slug(slug_match.group(1))

    # Language-agnostic fallback (ARC-1). Both probes above key on an English
    # LABEL, so a TASK.md whose meta reads `| ИД задачи | 095 |` yields
    # task_id=None and slug=None -- and the caller then auto-generates an ID
    # (reproducing ARC-1) and files the document as `untitled` (reproducing the
    # WI-30 collision that TASK 095 closed for the slug VALUE but not its LABEL).
    #
    # The fallback addresses the meta table STRUCTURALLY: the region runs from
    # `<!-- contract:meta -->` to the NEXT `<!-- contract:` anchor -- not to the
    # next heading, because the registered convention puts the anchor
    # immediately BEFORE the `## 0. Meta` heading, so an anchor-to-heading
    # region is empty on every document this framework writes.
    #
    # Inside that region rows are identified by the SHAPE of their value, never
    # by their label: an id is a run of digits, a slug is a lowercase kebab
    # token. Runs only when the English probes came back empty, so latin
    # behaviour is unchanged by construction.
    if result["task_id"] is None or result["slug"] is None:
        start = content.find(META_ANCHOR)
        if start != -1:
            rest = content[start + len(META_ANCHOR):]
            nxt = rest.find("<!-- contract:")
            region = rest if nxt == -1 else rest[:nxt]

            # EMPTY value cells are kept (ARC-3/ARC-12). Dropping them lost the
            # positional anchor the slug rule depends on: with `| ИД задачи |  |`
            # skipped, "the row after the id row" pointed at the wrong row, and a
            # document whose id is merely awaiting write-back could not have its
            # slug read at all -- it fell to the shared "untitled" stem (WI-30).
            # Only the `|:---|:---|` separator is discarded.
            rows = []
            for _, value in re.findall(r'^\s*\|([^|\n]+)\|([^|\n]*)\|\s*$',
                                       region, re.MULTILINE):
                value = value.strip()
                if value and set(value) <= set("-: "):
                    continue
                rows.append(value)

            # The id is a value in the framework's own zero-padded form: EXACTLY
            # three digits. A looser `\d{1,6}` matched a `| Дата | 2026 |` row
            # and archived the document as task-2026, which also poisons
            # find_next_available_id for every later auto-generation.
            #
            # AMBIGUITY IS REFUSED, NOT GUESSED. Two rows carrying a 3-digit
            # value mean the table cannot be read structurally, and picking the
            # first is how a wrong identity gets committed silently. Returning
            # None routes to the caller's STOP path instead.
            ids = [i for i, v in enumerate(rows) if re.fullmatch(r'\d{3}', v)]
            if result["task_id"] is None and len(ids) > 1:
                result["id_ambiguous"] = True
            if result["task_id"] is None and len(ids) == 1:
                result["task_id"] = rows[ids[0]]

            # The slug is the row IMMEDIATELY AFTER the id row — the order the
            # templates emit and every existing artifact follows. Matching any
            # kebab-shaped value anywhere in the block picked up
            # `| Статус | in-progress |` instead.
            # The value may be in any script -- `| Слаг | реестр |` is a slug
            # and normalize_slug transliterates it. Requiring `[a-z0-9-]` here
            # would drop it to the shared "untitled", reopening the WI-30
            # collision from the other side. The only shape check is "contains
            # a letter", which rejects a date or a version number sitting where
            # the slug should be.
            #
            # ARC-3: the id row is located whether or not it carries a value.
            # A document awaiting write-back has an EMPTY id row, and anchoring
            # only on a filled one made its slug unreadable — the same
            # "untitled" collision, reached from the other side. The empty-cell
            # anchor is the one `_write_id_into_meta` writes into, so the two
            # read the same row by construction.
            anchor = ids[0] if len(ids) == 1 else None
            if anchor is None:
                blanks = [i for i, v in enumerate(rows) if v == ""]
                if len(blanks) == 1:
                    anchor = blanks[0]

            if result["slug"] is None and anchor is not None \
                    and anchor + 1 < len(rows):
                nxt_value = rows[anchor + 1]
                if any(ch.isalpha() for ch in nxt_value):
                    normalized = normalize_slug(nxt_value)
                    if normalized != "untitled":
                        result["slug"] = normalized

    # ARC-3, the milder shape: an id was read but no slug was. Falling through
    # left the caller to substitute the literal "untitled", which is the shared
    # stem two different tasks collide on (WI-30). A meta region that is present
    # and yields no slug is a refusal, not an absence.
    if result["has_meta"] and result["slug"] is None:
        result["slug_unreadable"] = True

    return result


def _write_id_into_meta(content: str, used_id: str):
    """Write a generated ID into the meta table's empty value cell (ARC-12).

    The row is addressed by SHAPE, mirroring parse_task_meta: inside the meta
    region, the target is the single row whose value cell is empty. The label
    cell is preserved verbatim, so `| ИД задачи |  |` becomes
    `| ИД задачи | 042 |` and the English table behaves as before.

    Returns:
        (content, written) -- `written` is False when the region offers no
        single empty value cell. The caller reports that in its result dict:
        the old code hid the same case behind `if updated != content`.
    """
    start = content.find(META_ANCHOR)
    if start == -1:
        for probe in ("## 0. Meta Information", "Meta Information"):
            start = content.find(probe)
            if start != -1:
                break
    if start == -1:
        return content, False

    rest = content[start:]
    nxt = rest.find("<!-- contract:", len(META_ANCHOR))
    region = rest if nxt == -1 else rest[:nxt]

    empty_rows = [m for m in re.finditer(
        r'^(\s*\|[^|\n]+\|)(\s*)\|[ \t]*$', region, re.MULTILINE)]
    if len(empty_rows) != 1:
        return content, False

    m = empty_rows[0]
    new_region = region[:m.start()] + f"{m.group(1)} {used_id} |" + region[m.end():]
    return content[:start] + new_region + rest[len(region):], True


def _rebase_moved_document(archived_path, from_dir, to_dir, slot_map) -> list:
    """Re-express the moved document's relative links against its new home.

    ARC-2. Every relative link in the document was written against `from_dir`.
    Failure here never fails the archive: the file has already moved, and a
    link problem must not strand the protocol half-done. It is reported instead.
    """
    try:
        from rebase_links import rebase_file
    except ImportError:
        return []

    repo_root = Path(from_dir).parent
    try:
        _, records = rebase_file(
            str(archived_path),
            from_dir=str(Path(from_dir).relative_to(repo_root)),
            to_dir=str(Path(to_dir).relative_to(repo_root)),
            repo_root=str(repo_root),
            slot_map={
                str(Path(k).relative_to(repo_root)):
                    str(Path(v).relative_to(repo_root))
                for k, v in slot_map.items()
            },
        )
        return records
    except (OSError, ValueError):
        return []


def should_archive(is_new_task: bool, task_exists: bool) -> bool:
    """
    Decision logic: should we archive the existing TASK.md?
    
    Args:
        is_new_task: True if starting a NEW task, False if refining current
        task_exists: True if docs/TASK.md exists
    
    Returns:
        True if archiving should happen, False otherwise
    """
    # Only archive if:
    # 1. This is a NEW task (not refinement)
    # 2. TASK.md exists
    return is_new_task and task_exists


def archive_task(
    docs_dir: str,
    is_new_task: bool,
    current_task_slug: Optional[str] = None,
    current_task_id: Optional[str] = None,
    allow_renumber: bool = False
) -> dict:
    """
    Execute the 6-step archiving protocol.
    
    Args:
        docs_dir: Path to docs/ directory (e.g., "/path/to/docs")
        is_new_task: True if starting a NEW task
        current_task_slug: Slug extracted from current TASK.md (or None)
        current_task_id: Task ID extracted from current TASK.md (or None)
    
    Returns:
        dict with keys:
            - status: "archived" | "skipped" | "error"
            - reason: Explanation for the status
            - archived_to: Path to archived file (if archived)
            - message: Optional additional info
    """
    docs_path = Path(docs_dir)
    task_file = docs_path / "TASK.md"
    tasks_dir = docs_path / "tasks"
    
    # Step 1: Check condition
    if not task_file.exists():
        return {
            "status": "skipped",
            "reason": "no_existing_task",
            "archived_to": None,
            "message": "docs/TASK.md does not exist"
        }
    
    # Check if we should archive
    if not should_archive(is_new_task, task_file.exists()):
        return {
            "status": "skipped",
            "reason": "refinement",
            "archived_to": None,
            "message": "This is a refinement, not a new task"
        }
    
    # Step 2: Extract Metadata for whichever field the caller did not supply.
    #
    # This used to run only `if current_task_slug is None`, so a caller passing
    # a slug but no id -- the documented signature makes both optional -- left
    # `current_task_id` at None and Step 3 fell to the auto-generate branch,
    # which counts the task's own sub-task files. That IS ARC-1, reached
    # through the automated path (verified: sub-tasks task-095-01..09 present,
    # meta id 095, caller supplies slug only -> archived as task-096).
    meta_id_written = False
    if current_task_slug is None or current_task_id is None:
        meta = parse_task_meta(task_file.read_text())

        # Step 2.5: the STOP path parse_task_meta's comment promises (ARC-3).
        #
        # A refusal is not an absence. `id_ambiguous` means the meta table
        # carried two 3-digit values, `slug_unreadable` means a meta region is
        # present and no slug could be read from it. Falling through turned the
        # first into an auto-generated id over a set that counts the task's own
        # sub-task files, and the second into the shared "untitled" stem --
        # measured: a document reading 095 archived as task-096-untitled.md
        # with status "archived" and no warning.
        #
        # A document with NO meta region at all still archives: nothing was
        # refused there, and Step 4 below writes the generated id back.
        if meta.get("id_ambiguous") or meta.get("slug_unreadable"):
            refused = []
            if meta.get("id_ambiguous"):
                refused.append("task_id")
            if meta.get("slug_unreadable"):
                refused.append("slug")
            return {
                "status": "error",
                "reason": "meta_unreadable",
                "archived_to": None,
                "refused": refused,
                "message": (
                    "The meta table could not be read structurally: "
                    + ", ".join(refused)
                    + ". Repair the meta block or pass the value explicitly; "
                      "guessing here commits a wrong identity."
                ),
            }

        if current_task_slug is None:
            current_task_slug = meta.get("slug") or "untitled"
        if current_task_id is None:
            current_task_id = meta.get("task_id")

    # Step 3: Generate filename via tool.
    # The document's id is the identity; the filename follows it. Correction is
    # OFF, so a collision with a real PARENT archive returns "conflict" and
    # stops the run instead of silently renumbering a task whose id is already
    # cited in its sub-tasks, its plan archive, commits and ledgers (ARC-1).
    tool_result = generate_task_archive_filename(
        slug=current_task_slug,
        proposed_id=current_task_id,
        allow_correction=allow_renumber,
        tasks_dir=str(tasks_dir)
    )
    
    if tool_result["status"] == "error":
        return {
            "status": "error",
            "reason": "tool_error",
            "archived_to": None,
            "message": tool_result["message"]
        }
    
    if tool_result["status"] == "conflict":
        return {
            "status": "error",
            "reason": "conflict",
            "archived_to": None,
            "message": tool_result["message"]
        }
    
    # Step 4: Write the id back ONLY when the document had none.
    #
    # The old code rewrote the `| Task ID |` row whenever the tool corrected the
    # id. That is the renumber ARC-1 forbids, and it was a one-row edit: the H1,
    # the `Archive name` row and every in-body citation were left stating the
    # old number, so the document contradicted itself. Renumbering a published
    # id is a human decision, not a side effect of archiving.
    # ARC-12: the row is located by STRUCTURE, not by the English label.
    # `parse_task_meta` above is language-agnostic by construction, so keying
    # the write-back on the literal `Task ID` made it a no-op on every
    # non-English document -- and `if updated != content` swallowed the miss,
    # leaving the archived document's identity in its filename only.
    #
    # Inside the meta region the target is the ONE row whose value cell is
    # empty. Two such rows mean the table cannot be addressed structurally, so
    # nothing is written: the same refuse-rather-than-guess rule as above.
    if tool_result["status"] == "generated" and not current_task_id:
        content = task_file.read_text()
        updated, meta_id_written = _write_id_into_meta(
            content, tool_result["used_id"])
        if meta_id_written:
            task_file.write_text(updated)

    # Step 5: Archive (move file)
    archived_path = tasks_dir / tool_result["filename"]

    # Collision guard. `shutil.move` overwrites, and the tool's conflict check
    # looks at PARENT archives only -- a destination shaped like a sub-task
    # (`task-096-01-x.md`) is invisible to it. Without this, archiving a
    # document whose meta reads id 096 / slug `01-x` silently overwrote a
    # planner sub-task file. SKILL.md already promised this guard existed.
    if archived_path.exists():
        return {
            "status": "error",
            "reason": "conflict",
            "archived_to": None,
            "message": f"Archive target already exists: {archived_path}. "
                       f"Refusing to overwrite."
        }

    try:
        # Ensure tasks directory exists
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file
        shutil.move(str(task_file), str(archived_path))
    except PermissionError as e:
        return {
            "status": "error",
            "reason": "permission_denied",
            "archived_to": None,
            "message": f"Permission denied: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": "move_failed",
            "archived_to": None,
            "message": f"Failed to move file: {e}"
        }
    
    # Step 6: Validate
    if task_file.exists():
        return {
            "status": "error",
            "reason": "validation_failed",
            "archived_to": str(archived_path),
            "message": "Original file still exists after move"
        }
    
    if not archived_path.exists():
        return {
            "status": "error",
            "reason": "validation_failed",
            "archived_to": None,
            "message": "Archived file does not exist after move"
        }
    
    # Derive the normalized slug from the archived filename (task-{id}-{slug}.md)
    # so PLAN.md can reuse the EXACT same id/slug for lockstep archiving (Step 7).
    used_id = tool_result["used_id"]
    archived_slug = tool_result["filename"][len(f"task-{used_id}-"):-len(".md")]

    # Step 5.5: rebase the moved document's relative links (ARC-2).
    #
    # The slot map is the whole point. `docs/PLAN.md` is a mutable slot: a link
    # to it inside THIS task means this task's plan, which Step 7 is about to
    # archive under the paired id/slug. Rebasing the path instead would author a
    # link that dies seconds later, in the same protocol run.
    # The PLAN slot is mapped only when a PLAN.md actually exists to be
    # archived. Mapping it unconditionally would author a link to
    # `plan-{id}-{slug}.md` for a task that never reached planning -- a file
    # Step 7 will never create -- and report success.
    slot_map = {}
    if (docs_path / "PLAN.md").exists():
        slot_map[str(docs_path / "PLAN.md")] = str(
            docs_path / "plans" / f"plan-{used_id}-{archived_slug}.md")

    link_records = _rebase_moved_document(
        archived_path,
        from_dir=docs_path,
        to_dir=tasks_dir,
        slot_map=slot_map,
    )

    return {
        "status": "archived",
        "links": [r._asdict() for r in link_records],
        "reason": "success",
        "archived_to": str(archived_path),
        "message": f"Archived with ID {used_id}",
        # Lockstep handoff: present ONLY on status == "archived".
        # Pass these straight to archive_plan() to keep TASK and PLAN paired.
        "used_id": used_id,
        "slug": archived_slug,
        # ARC-12. False on every document that already carried its id (the
        # normal case, where Step 4 must NOT write) and on a meta table that
        # offered no single empty value cell. Reported rather than inferred:
        # the miss used to be indistinguishable from a successful write.
        "meta_id_written": meta_id_written,
    }


def archive_plan(docs_dir: str, used_id: str, slug: str) -> dict:
    """
    Execute Step 7 of skill-archive-task: archive docs/PLAN.md in lockstep
    with a TASK.md archive that has just completed.

    PLAN.md has no Meta block or identity of its own — it reuses the ID and
    slug that TASK.md was archived under. Call this ONLY after a successful
    new-task archive_task() (status == "archived"), passing that call's
    result["used_id"] and result["slug"]. The result is the pairing
    docs/tasks/task-NNN-slug.md <-> docs/plans/plan-NNN-slug.md.

    Args:
        docs_dir: Path to docs/ directory (e.g., "/path/to/docs").
        used_id: The post-correction ID from archive_task (result["used_id"]).
        slug: The normalized slug from archive_task (result["slug"]).

    Returns:
        dict with keys:
            - status: "archived" | "skipped" | "error"
            - reason: Explanation for the status
            - archived_to: Path to archived file (if archived)
            - message: Optional additional info
    """
    docs_path = Path(docs_dir)
    plan_file = docs_path / "PLAN.md"
    plans_dir = docs_path / "plans"

    # Step 7.1: Condition check — no PLAN.md means the task never reached
    # planning. Not an error.
    if not plan_file.exists():
        return {
            "status": "skipped",
            "reason": "no_plan",
            "archived_to": None,
            "message": "docs/PLAN.md does not exist — nothing to rotate",
        }

    # Step 7.4 (guard): PLAN.md has no independent ID. Without the TASK
    # archive's used_id/slug it cannot be safely archived (orphan case).
    if not used_id or not slug:
        return {
            "status": "error",
            "reason": "missing_lockstep_id",
            "archived_to": None,
            "message": "archive_plan requires used_id and slug from a completed TASK.md archive",
        }

    # Step 7.4: Derive filename — reuse the TASK archive's id/slug verbatim.
    filename = f"plan-{used_id}-{slug}.md"
    archived_path = plans_dir / filename

    # Step 7.5: Collision guard — never overwrite an existing plan archive.
    if archived_path.exists():
        return {
            "status": "error",
            "reason": "conflict",
            "archived_to": None,
            "message": f"Plan archive collision: {archived_path} already exists",
        }

    # Step 7.3 + 7.6: Ensure destination exists, then move.
    try:
        plans_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(plan_file), str(archived_path))
    except PermissionError as e:
        return {
            "status": "error",
            "reason": "permission_denied",
            "archived_to": None,
            "message": f"Permission denied: {e}",
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": "move_failed",
            "archived_to": None,
            "message": f"Failed to move file: {e}",
        }

    # Step 7.7: Validate.
    if plan_file.exists():
        return {
            "status": "error",
            "reason": "validation_failed",
            "archived_to": str(archived_path),
            "message": "Original PLAN.md still exists after move",
        }

    if not archived_path.exists():
        return {
            "status": "error",
            "reason": "validation_failed",
            "archived_to": None,
            "message": "Archived plan file does not exist after move",
        }

    # Step 7.6.5: rebase the moved plan's relative links (ARC-2).
    #
    # `docs/TASK.md` is already GONE by now -- archive_task moved it and Step 7
    # runs only after that succeeded. An existence-based rule would therefore
    # see the link as broken-before-and-after and leave it dead forever. The
    # slot map carries the identity the slot held, so it needs no filesystem.
    link_records = _rebase_moved_document(
        archived_path,
        from_dir=docs_path,
        to_dir=plans_dir,
        slot_map={
            str(docs_path / "TASK.md"):
                str(docs_path / "tasks" / f"task-{used_id}-{slug}.md"),
        },
    )

    return {
        "status": "archived",
        "reason": "success",
        "archived_to": str(archived_path),
        "message": f"Archived PLAN.md in lockstep with ID {used_id}",
        "links": [r._asdict() for r in link_records],
    }
