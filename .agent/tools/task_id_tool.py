"""
Task Archive ID Tool

Generates unique sequential IDs for archived tasks and validates proposed IDs.
Format: task-{XXX}-{slug}.md where XXX is a zero-padded 3-digit number.
"""

import os
import re
from typing import Optional


#: Cyrillic -> latin, for filename stems only. Deliberately NOT a general
#: transliterator and never shown to a user: its whole job is to keep two
#: different titles apart in `docs/tasks/`. Digraphs come first so that `щ`
#: does not decompose into `ш`+`ч` by accident.
_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'і': 'i', 'ї': 'yi', 'є': 'ye', 'ґ': 'g',
}


def normalize_slug(slug: str) -> str:
    """
    Normalize slug to a latin, filename-safe stem.

    Non-latin input is transliterated (Cyrillic by table, everything else by
    Unicode decomposition) BEFORE the character strip. It used to be stripped
    directly, which deleted the whole title and fell through to the literal
    ``"untitled"`` — silently, and with the same value every time, so
    ``"реестр-инструментов"`` and ``"единый-реестр"`` both produced
    ``task-095-untitled.md`` and the second archive overwrote the first
    (TASK 095 / WI-30, the unfiled half of the defect).

    ``"untitled"`` is kept for input that genuinely carries no word characters
    (``""``, ``"!!!"``) — there the fallback is honest rather than lossy.

    Args:
        slug: Raw slug string (e.g., "New Feature", "my_task", "Единый реестр")

    Returns:
        Normalized slug (e.g., "new-feature", "my-task", "edinyy-reestr")
    """
    import unicodedata

    # Convert to lowercase
    slug = slug.lower()
    # Transliterate Cyrillic, then let NFKD handle the rest (accents, ligatures,
    # full-width forms). Anything still non-latin after both is dropped below,
    # exactly as before — this only ADDS survivors, it never changes a stem that
    # was already pure latin.
    slug = ''.join(_TRANSLIT.get(ch, ch) for ch in slug)
    slug = unicodedata.normalize('NFKD', slug)
    slug = slug.encode('ascii', 'ignore').decode('ascii')
    # Replace underscores and spaces with dashes
    slug = re.sub(r'[_\s]+', '-', slug)
    # Remove all non-alphanumeric characters except dashes
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove consecutive dashes
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing dashes
    slug = slug.strip('-')
    return slug or "untitled"


#: Any archived task file: `task-<id>-<rest>.md`. 3+ digits, future-proofed.
TASK_FILENAME_RE = re.compile(r'^task-(\d{3,})-.*\.md$')

#: A PLANNER SUB-TASK: `task-<id>-<subid>-<slug>.md`, e.g. `task-005-1-usage-ddl.md`. The segment
#: right after the id is purely numeric — that is what distinguishes it from a parent archive
#: (`task-005-m2-alpha-paid.md`), whose slug never starts with a bare number segment.
SUBTASK_FILENAME_RE = re.compile(r'^task-(\d{3,})-(\d+)-.+\.md$')


def get_existing_task_ids(tasks_dir: str = "docs/tasks") -> list[int]:
    """
    Scan the tasks directory and extract all task IDs in use — parents AND sub-tasks.

    Used for AUTO-GENERATION (`proposed_id=None`), where a sub-task must keep its parent's id
    reserved: handing a brand-new task an id whose sub-task namespace is already populated would
    interleave two unrelated tasks under one number.

    Args:
        tasks_dir: Path to the tasks directory

    Returns:
        List of existing task IDs as integers
    """
    existing_ids = []

    if not os.path.exists(tasks_dir):
        return existing_ids

    for filename in os.listdir(tasks_dir):
        match = TASK_FILENAME_RE.match(filename)
        if match:
            task_id = int(match.group(1))
            existing_ids.append(task_id)

    return existing_ids


def get_parent_archive_ids(tasks_dir: str = "docs/tasks") -> list[int]:
    """
    Scan for IDs that already have a PARENT archive (`task-<id>-<slug>.md`), ignoring sub-tasks.

    This is the set an explicit `--proposed-id` must be checked against. `get_existing_task_ids()`
    counts sub-tasks too, so archiving a finished parent under its own id was refused whenever the
    planner had written `task-<id>-1..N-*.md` for it — and `skill-archive-task` Step 4 then says
    "set Task ID to the id used in filename", i.e. following the protocol literally RENUMBERED a
    task that was already committed, breaking its pairing with its own sub-tasks, its
    `docs/plans/plan-<id>-*.md` and any commit referencing it. Nothing errored; the archive was
    simply wrong, in a hand-maintained ledger.

    Known limitation: a parent slug that itself begins with a bare number segment
    (`task-007-2024-migration.md`) is indistinguishable from sub-task 2024 by filename alone.
    Avoid leading numeric segments in slugs; `normalize_slug` does not forbid them because a
    project may legitimately want e.g. `task-012-3d-viewer` (segment `3d` is not purely numeric,
    so it is read as a parent correctly).

    Args:
        tasks_dir: Path to the tasks directory

    Returns:
        List of task IDs that have a parent archive, as integers
    """
    parent_ids = []

    if not os.path.exists(tasks_dir):
        return parent_ids

    for filename in os.listdir(tasks_dir):
        match = TASK_FILENAME_RE.match(filename)
        if match and not SUBTASK_FILENAME_RE.match(filename):
            parent_ids.append(int(match.group(1)))

    return parent_ids


def find_next_available_id(existing_ids: list[int], start_from: int = 1) -> int:
    """
    Find the next available ID (max + 1 strategy, not gap-filling).
    
    Args:
        existing_ids: List of existing task IDs
        start_from: Minimum ID to start from
    
    Returns:
        Next available ID
    """
    if not existing_ids:
        return max(1, start_from)
    
    max_id = max(existing_ids)
    return max(max_id + 1, start_from)


def generate_task_archive_filename(
    slug: str,
    proposed_id: Optional[str] = None,
    allow_correction: bool = False,
    tasks_dir: str = "docs/tasks"
) -> dict:
    """
    Generate a unique filename for task archival.

    Args:
        slug: Short task name in Latin with dashes
        proposed_id: Optional desired ID (e.g., "031" or "31")
        allow_correction: If True, auto-correct to next available on conflict.
            Defaults to False: an ID cited in sub-tasks, a plan archive, commits
            or ledger rows is never renumbered without an explicit instruction
            (ARC-1). ARC-7 flipped this default, which had disagreed with
            `schemas.py` and `System/scripts/tool_runner.py` since 992b3ef.
            Ignored when `proposed_id` is None — that path auto-generates.
        tasks_dir: Path to tasks directory (default: "docs/tasks")
    
    Returns:
        dict with keys:
            - filename: Full filename (e.g., "task-031-new-feature.md")
            - used_id: The ID that was used (e.g., "031")
            - status: "generated" | "corrected" | "conflict" | "error"
            - message: Optional explanation
    """
    # Normalize slug
    normalized_slug = normalize_slug(slug)
    
    # Ensure tasks directory exists BEFORE scanning (avoid race condition)
    if not os.path.exists(tasks_dir):
        try:
            os.makedirs(tasks_dir, exist_ok=True)
        except OSError as e:
            return {
                "filename": None,
                "used_id": None,
                "status": "error",
                "message": f"Failed to create tasks directory: {e}"
            }
    
    # Get existing IDs (must be after directory creation).
    # Two different sets on purpose — see get_parent_archive_ids() for why:
    #   existing_ids -> auto-generation (sub-tasks reserve their parent's id)
    #   parent_ids   -> the --proposed-id conflict check (only a real parent archive conflicts)
    existing_ids = get_existing_task_ids(tasks_dir)
    parent_ids = get_parent_archive_ids(tasks_dir)

    if proposed_id is None:
        # Auto-generate: max + 1
        next_id = find_next_available_id(existing_ids)
        formatted_id = f"{next_id:03d}"
        filename = f"task-{formatted_id}-{normalized_slug}.md"
        
        return {
            "filename": filename,
            "used_id": formatted_id,
            "status": "generated",
            "message": None
        }
    
    # Validate and parse proposed_id
    try:
        proposed_int = int(proposed_id)
        if proposed_int < 1:
            raise ValueError("ID must be positive")
    except ValueError:
        return {
            "filename": None,
            "used_id": None,
            "status": "error",
            "message": f"Invalid ID format: '{proposed_id}'. Must be a positive integer."
        }
    
    formatted_proposed = f"{proposed_int:03d}"
    
    # Check for conflict — against PARENT archives only. A populated sub-task namespace
    # (`task-<id>-1..N-*.md`) is not a conflict for the parent that owns it.
    if proposed_int in parent_ids:
        if allow_correction:
            # Find next available
            next_id = find_next_available_id(existing_ids, start_from=proposed_int + 1)
            formatted_id = f"{next_id:03d}"
            filename = f"task-{formatted_id}-{normalized_slug}.md"
            
            return {
                "filename": filename,
                "used_id": formatted_id,
                "status": "corrected",
                "message": f"ID {formatted_proposed} is occupied, used {formatted_id} instead."
            }
        else:
            # Return conflict
            next_id = find_next_available_id(existing_ids, start_from=proposed_int + 1)
            suggested = f"{next_id:03d}"
            
            return {
                "filename": None,
                "used_id": None,
                "status": "conflict",
                "message": f"ID {formatted_proposed} is occupied. Suggested alternative: {suggested}"
            }
    
    # Proposed ID is available
    filename = f"task-{formatted_proposed}-{normalized_slug}.md"
    
    return {
        "filename": filename,
        "used_id": formatted_proposed,
        "status": "generated",
        "message": None
    }


if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Generate a unique sequential filename for task archival."
    )
    parser.add_argument("slug", help="Short task name (e.g. 'new-feature')")
    parser.add_argument(
        "--proposed-id",
        default=None,
        help="Optional desired ID (e.g. '031' or '31'); auto-generated if omitted",
    )
    parser.add_argument(
        "--tasks-dir",
        default="docs/tasks",
        help="Tasks directory (default: docs/tasks)",
    )
    parser.add_argument(
        "--allow-correction",
        action="store_true",
        help="Opt in to auto-selecting the next available ID on conflict; "
             "without it a conflict is reported and the exit code is 1",
    )
    parser.add_argument(
        "--no-correction",
        action="store_true",
        help="Deprecated no-op: refusing to renumber is the default (ARC-8). "
             "Accepted so the six documented invocation sites keep working",
    )
    args = parser.parse_args()

    # ARC-8. The CLI offered only the opt-OUT `--no-correction`, so an agent
    # that forgot one flag got a renumbered task and exit 0 -- the polarity the
    # schema and the dispatcher had already been flipped away from. The two
    # flags are combined rather than made mutually exclusive because
    # `--no-correction` now states the default, so passing both is consistent.
    allow_correction = args.allow_correction and not args.no_correction

    result = generate_task_archive_filename(
        slug=args.slug,
        proposed_id=args.proposed_id,
        allow_correction=allow_correction,
        tasks_dir=args.tasks_dir,
    )
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] in ("generated", "corrected") else 1)
