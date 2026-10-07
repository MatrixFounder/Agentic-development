"""
Task Archive ID Tool

Generates unique sequential IDs for archived tasks and validates proposed IDs.
Format: task-{XXX}-{slug}.md where XXX is a zero-padded 3-digit number.
"""

import os
import re
import stat
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

#: A PLANNER SUB-TASK by name: `task-<id>-<subid>-<slug>.md`, e.g. `task-005-1-usage-ddl.md`, with
#: a purely numeric segment right after the id. This is the FALLBACK rule of `classify_task_file()`,
#: used only when the file's H1 names no task of its id. It reads `task-033-05a-x.md` as a parent,
#: and it cannot be widened to `\d+[a-z]?`: that reads `task-012-3d-viewer.md` as sub-task `3d`.
SUBTASK_FILENAME_RE = re.compile(r'^task-(\d{3,})-(\d+)-.+\.md$')

#: The H1 of a task file: `# Task <id>` for a parent, `# Task <id>-<subid>` or `# Task <id>.<subid>`
#: for a sub-task, followed by `:`, `—`, `–`, `- ` or the line end. `<subid>` is `\d+[a-z]?`, the
#: grammar of `skill-planning-format` §3 (`05`, `05a`). Only `Task` matches in any case. TASK 114.
H1_TASK_RE = re.compile(
    r'^#[ \t]+(?i:task)[ \t]+(\d+)(?:[-.](\d+[a-z]?))?(?=[ \t]*(?:[:—–]|-[ \t]|$))')

#: Bytes read from the head of a task file to find its H1.
H1_SCAN_BYTES = 16384

#: An opening or closing code fence: up to three spaces, then three or more backticks or tildes.
_FENCE_RE = re.compile(r'[ ]{0,3}(`{3,}|~{3,})')


def _first_h1(path: str) -> Optional[str]:
    """The first H1 line of a regular file, or None.

    Reads at most `H1_SCAN_BYTES`. A UTF-8 BOM, HTML comments (an unclosed one to the end of the
    head), a leading YAML front matter and fenced code blocks are skipped: the sub-task template
    puts a comment block above its H1, and a YAML or shell comment line starts with `# `.
    The file is opened with `O_NONBLOCK | O_NOCTTY` and read only when `fstat` shows a regular
    file, so a FIFO or a device named `task-*.md` does not block the scan.
    """
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOCTTY', 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        head = os.read(fd, H1_SCAN_BYTES).decode('utf-8-sig', errors='replace')
    except OSError:
        return None
    finally:
        os.close(fd)
    head = re.sub(r'<!--(?:.*?-->|.*)', '', head, flags=re.DOTALL)
    lines = head.splitlines()
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() in ('---', '...'):
                lines = lines[i + 1:]
                break
    fence = None
    for line in lines:
        marker = _FENCE_RE.match(line)
        if marker:
            if fence is None:
                fence = marker.group(1)[0]
            elif marker.group(1)[0] == fence:
                fence = None
            continue
        if fence is None and re.match(r'#[ \t]+\S', line):
            return line
    return None


def classify_task_file(tasks_dir: str, filename: str) -> Optional[tuple[int, bool]]:
    """`(task id, is_subtask)` of a file in `tasks_dir`, or None when its name is not `task-<id>-*.md`.

    The order (TASK 114):

    1. The first H1 reads `# Task <id>-<subid>` or `# Task <id>.<subid>` -> a sub-task.
    2. The first H1 reads `# Task <id>` -> a parent archive.
    3. Otherwise -> `SUBTASK_FILENAME_RE` on the name decides, as before TASK 114.

    The H1 counts only when its id equals the filename's id as a number; `Task` matches in any case.
    The ids are compared as digit strings without leading zeros, so an H1 digit run past the
    int conversion limit cannot raise.
    """
    match = TASK_FILENAME_RE.match(filename)
    if not match:
        return None
    task_id = int(match.group(1))
    h1 = _first_h1(os.path.join(tasks_dir, filename))
    heading = H1_TASK_RE.match(h1) if h1 else None
    if heading and heading.group(1).lstrip('0') == match.group(1).lstrip('0'):
        return task_id, heading.group(2) is not None
    return task_id, bool(SUBTASK_FILENAME_RE.match(filename))


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

    A file is a parent archive when `classify_task_file()` says so: by its H1 first, by its name
    second. The name alone reads the letter-suffixed sub-task `task-033-05a-x.md` as a parent
    (KI-089 of n8n-lazy-loading-skills), and the parent `task-007-2024-migration.md` as sub-task
    2024. The H1 settles both: `# Task 033-05a: …` is a sub-task, `# Task 007: …` a parent, and
    `task-012-3d-viewer.md` with `# Task 012: …` stays a parent. A file whose H1 names no task of
    its id keeps the name rule, with its two misreadings.

    Args:
        tasks_dir: Path to the tasks directory

    Returns:
        List of task IDs that have a parent archive, as integers
    """
    parent_ids = []

    if not os.path.exists(tasks_dir):
        return parent_ids

    for filename in os.listdir(tasks_dir):
        kind = classify_task_file(tasks_dir, filename)
        if kind and not kind[1]:
            parent_ids.append(kind[0])

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
