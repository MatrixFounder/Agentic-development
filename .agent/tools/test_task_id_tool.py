"""
Unit tests for task_id_tool.py

Tests cover:
- Auto-generation of IDs (proposed_id=None)
- Proposed ID validation (free/occupied)
- Conflict handling (allow_correction=True/False)
- Slug normalization
- Edge cases
"""

import os
import tempfile
import pytest

from task_id_tool import (
    normalize_slug,
    get_existing_task_ids,
    get_parent_archive_ids,
    find_next_available_id,
    generate_task_archive_filename
)


class TestNormalizeSlug:
    """Tests for slug normalization."""
    
    def test_lowercase_conversion(self):
        assert normalize_slug("NewFeature") == "newfeature"
    
    def test_spaces_to_dashes(self):
        assert normalize_slug("new feature") == "new-feature"
    
    def test_underscores_to_dashes(self):
        assert normalize_slug("new_feature") == "new-feature"
    
    def test_remove_special_chars(self):
        assert normalize_slug("new!@#$%feature") == "newfeature"
    
    def test_consecutive_dashes(self):
        assert normalize_slug("new---feature") == "new-feature"
    
    def test_leading_trailing_dashes(self):
        assert normalize_slug("-new-feature-") == "new-feature"
    
    def test_mixed_case_spaces_underscores(self):
        assert normalize_slug("My New_Feature Test") == "my-new-feature-test"
    
    def test_empty_slug(self):
        assert normalize_slug("") == "untitled"
    
    def test_only_special_chars(self):
        assert normalize_slug("!@#$%") == "untitled"


class TestGetExistingTaskIds:
    """Tests for extracting task IDs from directory."""
    
    def test_empty_directory(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        assert get_existing_task_ids(str(tasks_dir)) == []
    
    def test_nonexistent_directory(self, tmp_path):
        tasks_dir = tmp_path / "nonexistent"
        assert get_existing_task_ids(str(tasks_dir)) == []
    
    def test_single_task(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-001-test.md").touch()
        assert get_existing_task_ids(str(tasks_dir)) == [1]
    
    def test_multiple_tasks(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-001-first.md").touch()
        (tasks_dir / "task-005-second.md").touch()
        (tasks_dir / "task-010-third.md").touch()
        result = sorted(get_existing_task_ids(str(tasks_dir)))
        assert result == [1, 5, 10]
    
    def test_ignores_non_matching_files(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-001-valid.md").touch()
        (tasks_dir / "README.md").touch()
        (tasks_dir / "task-abc-invalid.md").touch()
        (tasks_dir / "not-a-task.md").touch()
        assert get_existing_task_ids(str(tasks_dir)) == [1]
    
    def test_supports_four_digit_ids(self, tmp_path):
        """Test that IDs beyond 999 are properly handled."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-999-old.md").touch()
        (tasks_dir / "task-1000-newer.md").touch()
        (tasks_dir / "task-1001-newest.md").touch()
        result = sorted(get_existing_task_ids(str(tasks_dir)))
        assert result == [999, 1000, 1001]


class TestParentArchiveVsSubTask:
    """
    Regression: a populated SUB-TASK namespace must not block archiving its own parent.

    Before this, `get_existing_task_ids()` was the only scan, and it matched
    `task-005-1-slug.md` as "id 005 in use". Archiving the finished parent TASK-005 under 005 was
    therefore refused and silently renumbered to 006 — and `skill-archive-task` Step 4 says to set
    the task's ID to the one in the filename, so following the protocol literally renumbered a
    task that was already committed, breaking its pairing with its nine sub-tasks, with
    `docs/plans/plan-005-*.md` and with every commit referencing TASK-005. Nothing raised; the
    hand-maintained ledger just became wrong.
    """

    def test_subtasks_alone_do_not_create_a_parent_archive(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-1-canonical-types.md").touch()
        (tasks_dir / "task-005-9-carryover.md").touch()
        assert get_parent_archive_ids(str(tasks_dir)) == []
        # ...while the auto-generate scan still sees the id as in use:
        assert get_existing_task_ids(str(tasks_dir)) == [5, 5]

    def test_parent_archive_is_detected(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-003-m1-read-layer.md").touch()
        (tasks_dir / "task-003-1-sub.md").touch()
        assert get_parent_archive_ids(str(tasks_dir)) == [3]

    def test_proposed_id_accepted_when_only_subtasks_exist(self, tmp_path):
        """The exact scenario that produced the wrong archive (TASK-006 retro, RF ledger)."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        for n in range(1, 10):
            (tasks_dir / f"task-005-{n}-sub.md").touch()

        result = generate_task_archive_filename(
            "m2-alpha-paid", proposed_id="005", tasks_dir=str(tasks_dir)
        )
        assert result["used_id"] == "005"
        assert result["status"] == "generated"
        assert result["filename"] == "task-005-m2-alpha-paid.md"

    def test_proposed_id_still_conflicts_with_a_real_parent(self, tmp_path):
        """The guard must not be loosened into "never conflict"."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-m2-alpha-paid.md").touch()

        result = generate_task_archive_filename(
            "other", proposed_id="005", tasks_dir=str(tasks_dir)
        )
        assert result["status"] == "corrected"
        assert result["used_id"] != "005"

    def test_no_correction_mode_still_reports_conflict_on_a_real_parent(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-parent.md").touch()

        result = generate_task_archive_filename(
            "other", proposed_id="005", allow_correction=False, tasks_dir=str(tasks_dir)
        )
        assert result["status"] == "conflict"

    def test_auto_generation_still_reserves_ids_held_only_by_subtasks(self, tmp_path):
        """A brand-new task must NOT land on an id whose sub-task namespace is populated."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-1-sub.md").touch()

        result = generate_task_archive_filename("brand-new", tasks_dir=str(tasks_dir))
        assert result["used_id"] == "006"
        assert result["status"] == "generated"

    def test_slug_starting_with_a_letter_digit_segment_reads_as_a_parent(self, tmp_path):
        """`m2`/`3d` are not purely numeric, so they are parents — only a bare number is a sub-id."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-m2-alpha-paid.md").touch()
        (tasks_dir / "task-012-3d-viewer.md").touch()
        assert sorted(get_parent_archive_ids(str(tasks_dir))) == [5, 12]


class TestFindNextAvailableId:
    """Tests for finding next available ID."""
    
    def test_empty_list(self):
        assert find_next_available_id([]) == 1
    
    def test_single_id(self):
        assert find_next_available_id([1]) == 2
    
    def test_gap_in_ids(self):
        # Should return max + 1, NOT fill gaps
        assert find_next_available_id([1, 5, 10]) == 11
    
    def test_start_from_higher(self):
        assert find_next_available_id([1, 2, 3], start_from=10) == 10
    
    def test_start_from_lower_than_max(self):
        assert find_next_available_id([1, 5, 10], start_from=3) == 11


class TestGenerateTaskArchiveFilename:
    """Integration tests for the main function."""
    
    def test_auto_generate_empty_dir(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        # Don't create dir - function should create it
        
        result = generate_task_archive_filename(
            slug="new-feature",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "generated"
        assert result["filename"] == "task-001-new-feature.md"
        assert result["used_id"] == "001"
        assert result["message"] is None
        assert tasks_dir.exists()
    
    def test_auto_generate_with_existing_tasks(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-old.md").touch()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "generated"
        assert result["filename"] == "task-006-new-feature.md"
        assert result["used_id"] == "006"
    
    def test_proposed_id_available(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-001-old.md").touch()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            proposed_id="050",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "generated"
        assert result["filename"] == "task-050-new-feature.md"
        assert result["used_id"] == "050"
    
    def test_proposed_id_occupied_with_correction(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-031-old.md").touch()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            proposed_id="31",
            allow_correction=True,
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "corrected"
        assert result["filename"] == "task-032-new-feature.md"
        assert result["used_id"] == "032"
        assert "031" in result["message"]
        assert "032" in result["message"]
    
    def test_proposed_id_occupied_without_correction(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-031-old.md").touch()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            proposed_id="31",
            allow_correction=False,
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "conflict"
        assert result["filename"] is None
        assert result["used_id"] is None
        assert "031" in result["message"]
        assert "032" in result["message"]
    
    def test_invalid_proposed_id(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            proposed_id="abc",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "error"
        assert result["filename"] is None
        assert "Invalid ID format" in result["message"]
    
    def test_negative_proposed_id(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        result = generate_task_archive_filename(
            slug="new-feature",
            proposed_id="-5",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["status"] == "error"
        assert "Invalid ID format" in result["message"]
    
    def test_slug_normalization_in_output(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        result = generate_task_archive_filename(
            slug="My New Feature!!!",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["filename"] == "task-001-my-new-feature.md"
    
    def test_proposed_id_short_format(self, tmp_path):
        """Test that '31' is correctly formatted as '031'."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        result = generate_task_archive_filename(
            slug="feature",
            proposed_id="31",
            tasks_dir=str(tasks_dir)
        )
        
        assert result["used_id"] == "031"
        assert result["filename"] == "task-031-feature.md"


class TestBareInvocationShadowsTheParentId:
    """ARC-1 is a *documentation* contract, not only a code one.

    `get_parent_archive_ids()` distinguishes sub-tasks from parents, but that
    machinery is reachable only on the `--proposed-id` path. On the bare
    auto-generate path sub-task files still occupy their parent's number --
    which is correct for inventing a *new* id and wrong for archiving a
    document that already has one.

    These two tests pin the difference that the wording in CLAUDE.md,
    AGENTS.md, GEMINI.md and ORCHESTRATOR.md exists to prevent. A later
    edit that "simplifies" those lines back to the bare form turns this red.
    """

    @staticmethod
    def _subtasks_without_a_parent(tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        for n in ("01", "02", "03"):
            (tasks_dir / f"task-095-{n}-x.md").write_text("# sub")
        return tasks_dir

    def test_bare_form_shadows_the_parent_id(self, tmp_path):
        """The form the bootstrap files used to document. Returns 096."""
        tasks_dir = self._subtasks_without_a_parent(tmp_path)
        result = generate_task_archive_filename(
            slug="structural-anchors", tasks_dir=str(tasks_dir)
        )
        assert result["used_id"] == "096"

    def test_protocol_form_keeps_the_authored_id(self, tmp_path):
        """The form skill-archive-task Step 3 documents. Returns 095."""
        tasks_dir = self._subtasks_without_a_parent(tmp_path)
        result = generate_task_archive_filename(
            slug="structural-anchors",
            proposed_id="095",
            allow_correction=False,
            tasks_dir=str(tasks_dir),
        )
        assert result["used_id"] == "095"
        assert result["status"] != "conflict"


class TestSchemaMatchesTheDispatcher:
    """The LLM-facing schema is a contract an agent reads and reasons from.

    It advertised `allow_correction: default true` while the dispatcher
    defaulted it False -- so a model could omit the argument believing it had
    enabled the renumbering ARC-1 forbids.
    """

    def test_schema_default_matches_tool_runner_default(self):
        import schemas
        spec = next(t for t in schemas.TOOLS_SCHEMAS
                    if t["function"]["name"] == "generate_task_archive_filename")
        prop = spec["function"]["parameters"]["properties"]["allow_correction"]
        assert prop["default"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
