"""
Test Archive Protocol

Tests for the 8 archiving scenarios from Task 033, plus VDD adversarial tests
and PLAN.md lockstep archiving (Step 7).

Core Scenarios (from skill-archive-task):
1. New task when TASK.md exists → archive
5. New task when TASK.md does NOT exist → skip
6. Refinement → skip (overwrite, no archive)
8. ID conflict → tool returns corrected ID

PLAN.md Lockstep (Step 7):
- PLAN.md archived to docs/plans/plan-NNN-slug.md, reusing the TASK id/slug
- Lockstep holds on a corrected ID
- PLAN.md absent → skip; collision → error; docs/plans/ auto-created
- Orphan guard: no lockstep id/slug → error

VDD Adversarial Tests:
- Missing Meta Information
- Malformed Task ID
- Permission denied simulation
- Concurrent access (race condition)
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from archive_protocol import (
    parse_task_meta,
    should_archive,
    archive_task,
    archive_plan
)


# ============================================================================
# FIXTURES
# ============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def clean_docs_dir(tmp_path):
    """Create isolated docs/ structure for each test."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "tasks").mkdir()
    return docs


@pytest.fixture
def existing_task(clean_docs_dir):
    """Create docs/TASK.md with valid Meta Information."""
    task_file = clean_docs_dir / "TASK.md"
    content = (FIXTURES_DIR / "task_with_meta.md").read_text()
    task_file.write_text(content)
    return task_file


@pytest.fixture
def task_without_meta(clean_docs_dir):
    """Create docs/TASK.md without Meta Information."""
    task_file = clean_docs_dir / "TASK.md"
    content = (FIXTURES_DIR / "task_without_meta.md").read_text()
    task_file.write_text(content)
    return task_file


@pytest.fixture
def task_malformed_id(clean_docs_dir):
    """Create docs/TASK.md with malformed Task ID."""
    task_file = clean_docs_dir / "TASK.md"
    content = (FIXTURES_DIR / "task_malformed_id.md").read_text()
    task_file.write_text(content)
    return task_file


@pytest.fixture
def existing_plan(clean_docs_dir):
    """Create docs/PLAN.md (a plan has no Meta block of its own)."""
    plan_file = clean_docs_dir / "PLAN.md"
    plan_file.write_text("# Development Plan\n\n- [ ] Phase 1: Stubs\n- [ ] Phase 2: Logic\n")
    return plan_file


# ============================================================================
# UNIT TESTS: parse_task_meta
# ============================================================================

class TestParseTaskMeta:
    """Tests for Meta Information extraction."""
    
    def test_valid_meta_extraction(self):
        """Extract Task ID and Slug from valid TASK.md."""
        content = (FIXTURES_DIR / "task_with_meta.md").read_text()
        meta = parse_task_meta(content)
        
        assert meta["has_meta"] is True
        assert meta["task_id"] == "042"
        assert meta["slug"] == "existing-feature"
    
    def test_missing_meta_fallback_to_title(self):
        """Fallback to H1 title when Meta section missing."""
        content = (FIXTURES_DIR / "task_without_meta.md").read_text()
        meta = parse_task_meta(content)
        
        assert meta["has_meta"] is False
        assert meta["task_id"] is None
        assert meta["slug"] is not None  # Should extract from title
        assert "legacy" in meta["slug"].lower() or "old" in meta["slug"].lower()
    
    def test_malformed_id_not_numeric(self):
        """Handle non-numeric Task ID in Meta."""
        content = (FIXTURES_DIR / "task_malformed_id.md").read_text()
        meta = parse_task_meta(content)
        
        # Our regex only matches \d+, so ABC won't match
        assert meta["has_meta"] is True
        assert meta["task_id"] is None  # ABC is not \d+


# ============================================================================
# UNIT TESTS: should_archive
# ============================================================================

class TestShouldArchive:
    """Tests for archiving decision logic."""
    
    def test_new_task_existing_file(self):
        """New task + existing file = archive."""
        assert should_archive(is_new_task=True, task_exists=True) is True
    
    def test_new_task_no_file(self):
        """New task + no file = skip."""
        assert should_archive(is_new_task=True, task_exists=False) is False
    
    def test_refinement_existing_file(self):
        """Refinement + existing file = skip."""
        assert should_archive(is_new_task=False, task_exists=True) is False
    
    def test_refinement_no_file(self):
        """Refinement + no file = skip."""
        assert should_archive(is_new_task=False, task_exists=False) is False


# ============================================================================
# CORE SCENARIOS
# ============================================================================

class TestCoreScenarios:
    """Tests for the 8 archiving scenarios from Task 033."""
    
    def test_scenario_1_new_task_archives_existing(self, clean_docs_dir, existing_task):
        """
        Scenario 1: New task when TASK.md exists → archive
        
        Given: docs/TASK.md exists with Task 042
        When: Agent starts NEW task (different feature)
        Then:
          - Old TASK.md archived to docs/tasks/task-042-existing-feature.md
          - Original file removed
        """
        assert existing_task.exists()
        
        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042"
        )
        
        assert result["status"] == "archived"
        assert not existing_task.exists(), "Original TASK.md should be moved"
        
        archived_path = clean_docs_dir / "tasks" / "task-042-existing-feature.md"
        assert archived_path.exists(), "Archive file should exist"
    
    def test_scenario_5_new_task_no_existing_file(self, clean_docs_dir):
        """
        Scenario 5: New task when TASK.md does NOT exist → skip
        
        Given: docs/TASK.md does NOT exist
        When: Agent starts NEW task
        Then: Archiving skipped, no error
        """
        task_file = clean_docs_dir / "TASK.md"
        assert not task_file.exists()
        
        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug=None
        )
        
        assert result["status"] == "skipped"
        assert result["reason"] == "no_existing_task"
    
    def test_scenario_6_refinement_no_archive(self, clean_docs_dir, existing_task):
        """
        Scenario 6: Refinement → skip (overwrite, no archive)
        
        Given: docs/TASK.md exists with Task 042
        When: Agent refines CURRENT task (same feature)
        Then:
          - TASK.md still exists (not archived)
          - Status is "skipped" with reason "refinement"
        """
        assert existing_task.exists()
        
        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=False,  # Refinement!
            current_task_slug="existing-feature"
        )
        
        assert result["status"] == "skipped"
        assert result["reason"] == "refinement"
        assert existing_task.exists(), "TASK.md should NOT be moved"
    
    def test_scenario_8_id_conflict_stops(self, clean_docs_dir, existing_task):
        """
        Scenario 8 (ARC-1): ID conflict → STOP, never a silent renumber.

        Given: docs/TASK.md exists with Task 042
        And: docs/tasks/task-042-existing-feature.md already exists
        When: Agent tries to archive
        Then: the run stops with a conflict; TASK.md stays put; nothing renamed.

        The id in the meta block is cited by the task's sub-tasks, its plan
        archive, commits and ledger rows. Choosing a different number for it is
        a human decision, so archiving reports and refuses.
        """
        conflict_file = clean_docs_dir / "tasks" / "task-042-existing-feature.md"
        conflict_file.write_text("# Conflict file")

        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042"
        )

        assert result["status"] == "error"
        assert result["reason"] == "conflict"
        assert (clean_docs_dir / "TASK.md").exists(), "TASK.md must stay put"
        assert not (clean_docs_dir / "tasks" / "task-043-existing-feature.md").exists()
        assert conflict_file.read_text() == "# Conflict file"

    def test_scenario_8b_renumber_is_opt_in(self, clean_docs_dir, existing_task):
        """The old correcting behaviour survives, but only when asked for."""
        (clean_docs_dir / "tasks" / "task-042-existing-feature.md").write_text("x")

        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042",
            allow_renumber=True,
        )

        assert result["status"] == "archived"
        assert result["used_id"] == "043"
        assert (clean_docs_dir / "tasks" / "task-043-existing-feature.md").exists()

    def test_archive_refuses_to_overwrite_a_subtask_file(self, clean_docs_dir):
        """A destination shaped like a sub-task is invisible to the id tool's
        parent-only conflict check, and `shutil.move` overwrites. Step 5 guards it."""
        (clean_docs_dir / "TASK.md").write_text(
            "<!-- contract:meta -->\n\n| Task ID | 096 |\n| Slug | 01-x |\n")
        victim = clean_docs_dir / "tasks" / "task-096-01-x.md"
        victim.parent.mkdir(parents=True, exist_ok=True)
        victim.write_text("# planner sub-task, must survive")

        result = archive_task(docs_dir=str(clean_docs_dir), is_new_task=True)

        assert result["status"] == "error"
        assert result["reason"] == "conflict"
        assert victim.read_text() == "# planner sub-task, must survive"


# ============================================================================
# VDD ADVERSARIAL TESTS
# ============================================================================

class TestVDDAdversarial:
    """VDD Adversarial tests: challenge assumptions, simulate failures."""
    
    def test_adversarial_missing_meta_info(self, clean_docs_dir, task_without_meta):
        """
        VDD: What if TASK.md has no Meta Information?
        
        Expected: Fallback to slug from title, auto-generate ID.
        """
        assert task_without_meta.exists()
        
        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True
            # No slug/id provided - must extract from file
        )
        
        assert result["status"] == "archived"
        assert not task_without_meta.exists()
        
        # Check that some file was created in tasks/
        tasks_dir = clean_docs_dir / "tasks"
        archived_files = list(tasks_dir.glob("task-*.md"))
        assert len(archived_files) == 1, "Should archive with fallback slug"
    
    def test_adversarial_malformed_task_id(self, clean_docs_dir, task_malformed_id):
        """
        VDD: What if Task ID is "ABC" not "042"?
        
        Expected: Fall back to auto-generate ID.
        """
        assert task_malformed_id.exists()
        
        result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True
            # No explicit ID - will try to extract from file (which has "ABC")
        )
        
        # Should still work - auto-generate ID when extraction fails
        assert result["status"] == "archived"
    
    def test_adversarial_permission_denied(self, clean_docs_dir, existing_task):
        """
        VDD: What if we can't move the file (permission denied)?
        
        Expected: Return error with clear message.
        """
        with patch('archive_protocol.shutil.move') as mock_move:
            mock_move.side_effect = PermissionError("Permission denied")
            
            result = archive_task(
                docs_dir=str(clean_docs_dir),
                is_new_task=True,
                current_task_slug="existing-feature",
                current_task_id="042"
            )
        
        assert result["status"] == "error"
        assert result["reason"] == "permission_denied"
        assert "Permission denied" in result["message"]
    
    def test_adversarial_tool_returns_error(self, clean_docs_dir, existing_task):
        """
        VDD: What if generate_task_archive_filename returns error?
        
        Expected: Propagate error, don't crash.
        """
        with patch('archive_protocol.generate_task_archive_filename') as mock_tool:
            mock_tool.return_value = {
                "status": "error",
                "filename": None,
                "used_id": None,
                "message": "Internal tool error"
            }
            
            result = archive_task(
                docs_dir=str(clean_docs_dir),
                is_new_task=True,
                current_task_slug="test",
                current_task_id="001"
            )
        
        assert result["status"] == "error"
        assert result["reason"] == "tool_error"


# ============================================================================
# PLAN.md LOCKSTEP TESTS (Step 7)
# ============================================================================

class TestArchivePlanLockstep:
    """Tests for PLAN.md lockstep archiving (skill-archive-task Step 7)."""

    def test_plan_archived_in_lockstep(self, clean_docs_dir, existing_task, existing_plan):
        """
        PLAN.md is archived to docs/plans/plan-NNN-slug.md, reusing the
        id/slug returned by the TASK.md archive.
        """
        task_result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042",
        )
        assert task_result["status"] == "archived"

        plan_result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id=task_result["used_id"],
            slug=task_result["slug"],
        )

        assert plan_result["status"] == "archived"
        assert not existing_plan.exists(), "Original PLAN.md should be moved"

        archived = clean_docs_dir / "plans" / "plan-042-existing-feature.md"
        assert archived.exists(), "Plan archive should exist"

    def test_lockstep_pairing(self, clean_docs_dir, existing_task, existing_plan):
        """The archived TASK and PLAN filenames share the same ID and slug."""
        task_result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042",
        )
        plan_result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id=task_result["used_id"],
            slug=task_result["slug"],
        )

        task_name = Path(task_result["archived_to"]).name   # task-042-existing-feature.md
        plan_name = Path(plan_result["archived_to"]).name   # plan-042-existing-feature.md
        assert task_name == plan_name.replace("plan-", "task-", 1)

    def test_plan_lockstep_on_corrected_id(self, clean_docs_dir, existing_task, existing_plan):
        """
        When the TASK ID is corrected (042 -> 043) due to a conflict, PLAN.md
        archives under the SAME corrected ID — not the originally proposed one.
        """
        # Force a conflict so the tool corrects 042 -> 043.
        conflict = clean_docs_dir / "tasks" / "task-042-existing-feature.md"
        conflict.write_text("# Conflict file")

        task_result = archive_task(
            docs_dir=str(clean_docs_dir),
            is_new_task=True,
            current_task_slug="existing-feature",
            current_task_id="042",
            allow_renumber=True,   # ARC-1: renumbering is now opt-in
        )
        assert task_result["status"] == "archived"
        assert task_result["used_id"] == "043", "TASK ID should be corrected"

        plan_result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id=task_result["used_id"],
            slug=task_result["slug"],
        )
        assert plan_result["status"] == "archived"
        assert (clean_docs_dir / "plans" / "plan-043-existing-feature.md").exists()

    def test_plan_absent_skips(self, clean_docs_dir):
        """No docs/PLAN.md → skip, no error."""
        result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id="042",
            slug="existing-feature",
        )
        assert result["status"] == "skipped"
        assert result["reason"] == "no_plan"

    def test_plan_collision_guard(self, clean_docs_dir, existing_plan):
        """An existing plan archive is never overwritten."""
        plans_dir = clean_docs_dir / "plans"
        plans_dir.mkdir()
        (plans_dir / "plan-042-existing-feature.md").write_text("# Existing archive")

        result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id="042",
            slug="existing-feature",
        )
        assert result["status"] == "error"
        assert result["reason"] == "conflict"
        assert existing_plan.exists(), "PLAN.md must NOT be moved on collision"

    def test_plans_dir_auto_created(self, clean_docs_dir, existing_plan):
        """docs/plans/ is created on demand (mkdir -p)."""
        assert not (clean_docs_dir / "plans").exists()

        result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id="007",
            slug="feature",
        )
        assert result["status"] == "archived"
        assert (clean_docs_dir / "plans").is_dir()

    def test_plan_missing_lockstep_id(self, clean_docs_dir, existing_plan):
        """
        Orphan guard: a PLAN.md with no TASK identity (no used_id) cannot be
        archived — it has no defensible ID of its own.
        """
        result = archive_plan(
            docs_dir=str(clean_docs_dir),
            used_id=None,
            slug="feature",
        )
        assert result["status"] == "error"
        assert result["reason"] == "missing_lockstep_id"
        assert existing_plan.exists(), "PLAN.md must be left in place"

    def test_plan_archive_permission_denied(self, clean_docs_dir, existing_plan):
        """VDD: a failed move returns a clear error, not a crash."""
        with patch('archive_protocol.shutil.move') as mock_move:
            mock_move.side_effect = PermissionError("Permission denied")

            result = archive_plan(
                docs_dir=str(clean_docs_dir),
                used_id="042",
                slug="existing-feature",
            )

        assert result["status"] == "error"
        assert result["reason"] == "permission_denied"
        assert "Permission denied" in result["message"]


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestMetaFallbackStructural:
    """Regression pins for the language-agnostic meta fallback.

    Adversarial review reproduced two identity-corruption defects in the first
    version: a `| Дата | 2026 |` row became the Task ID, and a `| Статус |`
    row became the slug.
    """

    @staticmethod
    def _meta(body):
        return parse_task_meta("<!-- contract:meta -->\n" + body +
                               "\n<!-- contract:rtm -->")

    def test_date_row_does_not_become_the_id(self):
        m = self._meta("| Дата | 2026 |\n| Статус | in-progress |\n"
                       "| ИД задачи | 095 |\n| Слаг | my-task |")
        assert m["task_id"] == "095"
        assert m["slug"] == "my-task"

    def test_ambiguous_id_is_refused_not_guessed(self):
        """Two 3-digit rows -> the table cannot be read structurally."""
        m = self._meta("| Приоритет | 001 |\n| ИД | 095 |\n| Слаг | x-y |")
        assert m["task_id"] is None
        assert m["slug"] is None

    def test_single_word_non_latin_slug_is_transliterated(self):
        """Requiring a hyphen dropped it to 'untitled' — the WI-30 collision."""
        m = self._meta("| ИД | 042 |\n| Слаг | реестр |")
        assert m["task_id"] == "042"
        assert m["slug"] == "reestr"

    def test_a_date_sitting_where_the_slug_should_be_is_rejected(self):
        m = self._meta("| ИД | 042 |\n| Дата | 2026-08-04 |")
        assert m["task_id"] == "042"
        assert m["slug"] is None

    def test_latin_documents_are_byte_identical(self):
        """The fallback runs only when the English probes came back empty."""
        m = parse_task_meta("# Task 042: Existing Feature\n\n"
                            "## 0. Meta Information\n\n"
                            "| Task ID | 042 |\n| Slug | existing-feature |")
        assert m == {"task_id": "042", "slug": "existing-feature",
                     "has_meta": True}


class TestPlanSlotIsConditional:
    def test_no_plan_means_no_plan_slot_citation(self, clean_docs_dir):
        """Mapping the PLAN slot unconditionally authors a link to a file
        Step 7 will never create, and reports success."""
        (clean_docs_dir / "TASK.md").write_text(
            "<!-- contract:meta -->\n\n| Task ID | 077 |\n| Slug | no-plan |\n\n"
            "See [the plan](PLAN.md).\n")
        result = archive_task(docs_dir=str(clean_docs_dir), is_new_task=True)
        assert result["status"] == "archived"
        archived = (clean_docs_dir / "tasks" / "task-077-no-plan.md").read_text()
        assert "plan-077-no-plan.md" not in archived, \
            "authored a citation to a plan archive that will never exist"
