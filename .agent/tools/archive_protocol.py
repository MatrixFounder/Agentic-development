"""
Archive Protocol Module

Testable Python implementation of the 6-step archiving protocol
from skill-archive-task. This module enables automated testing
of the archiving scenarios.

Note: This duplicates logic from skill-archive-task for testability.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional

from task_id_tool import generate_task_archive_filename


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
    """
    result = {
        "task_id": None,
        "slug": None,
        "has_meta": False
    }
    
    # Check if Meta Information section exists
    if "## 0. Meta Information" not in content and "Meta Information" not in content:
        # Fallback: try to extract slug from H1 header
        h1_match = re.search(r'^#\s+(?:Task\s+\d+:\s+)?(.+)$', content, re.MULTILINE)
        if h1_match:
            # Convert title to slug
            title = h1_match.group(1).strip()
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            result["slug"] = slug
        return result
    
    result["has_meta"] = True
    
    # Extract Task ID from table format: | Task ID  | 042 |
    id_match = re.search(r'\|\s*Task ID\s*\|\s*(\d+)\s*\|', content)
    if id_match:
        result["task_id"] = id_match.group(1)
    
    # Extract Slug from table format: | Slug | existing-feature |
    slug_match = re.search(r'\|\s*Slug\s*\|\s*([a-z0-9-]+)\s*\|', content)
    if slug_match:
        result["slug"] = slug_match.group(1)
    
    return result


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
    current_task_id: Optional[str] = None
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
    
    # Step 2: Extract Metadata (if not provided)
    if current_task_slug is None:
        content = task_file.read_text()
        meta = parse_task_meta(content)
        current_task_slug = meta.get("slug") or "untitled"
        current_task_id = meta.get("task_id")
    
    # Step 3: Generate filename via tool
    tool_result = generate_task_archive_filename(
        slug=current_task_slug,
        proposed_id=current_task_id,
        allow_correction=True,
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
    
    # Step 4: Update Task ID in file (if corrected)
    if tool_result["status"] == "corrected" and current_task_id:
        content = task_file.read_text()
        # Update Task ID in the table
        updated_content = re.sub(
            r'(\|\s*Task ID\s*\|\s*)\d+(\s*\|)',
            rf'\g<1>{tool_result["used_id"]}\2',
            content
        )
        task_file.write_text(updated_content)
    
    # Step 5: Archive (move file)
    archived_path = tasks_dir / tool_result["filename"]
    
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
    
    return {
        "status": "archived",
        "reason": "success",
        "archived_to": str(archived_path),
        "message": f"Archived with ID {tool_result['used_id']}"
    }
