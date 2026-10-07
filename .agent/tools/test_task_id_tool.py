"""
Unit tests for task_id_tool.py

Tests cover:
- Auto-generation of IDs (proposed_id=None)
- Proposed ID validation (free/occupied)
- Conflict handling (allow_correction=True/False)
- Slug normalization
- Edge cases
"""

import json
import os
import subprocess
import sys
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
        """The guard must not be loosened into "never conflict".

        `allow_correction=True` is passed explicitly: this test exercises the
        correction path, and after ARC-7 the default no longer supplies it.
        """
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-005-m2-alpha-paid.md").touch()

        result = generate_task_archive_filename(
            "other", proposed_id="005", allow_correction=True,
            tasks_dir=str(tasks_dir)
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


class TestSubTaskByH1:
    """TASK 114: a file in `docs/tasks/` is classified by its H1 first, by its name second.

    The planner splits a sub-task further with a letter suffix (`task-033-05a-sqltest-db.md`).
    The filename rule reads `05a` as a parent slug, so `--proposed-id 033` returned `conflict`
    with no parent archive present (KI-089 of n8n-lazy-loading-skills). A filename rule of
    `\\d+[a-z]?` would read `task-012-3d-viewer.md` as sub-task `3d`, so the H1 decides.
    """

    @staticmethod
    def _write(tasks_dir, name, h1):
        tasks_dir.mkdir(exist_ok=True)
        (tasks_dir / name).write_text(f"{h1}\n\nBody.\n" if h1 else "No heading.\n")

    def test_tc1_letter_suffixed_subtasks_are_not_a_parent(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-033-05-acceptance-monitor.md", "# Task 033-05: Monitor")
        self._write(tasks_dir, "task-033-05a-sqltest-db.md", "# Task 033-05a: Test database")
        self._write(tasks_dir, "task-033-08b-sql-tests.md", "# Task 033.08b — SQL tests")

        result = generate_task_archive_filename(
            "admission-core-v1", proposed_id="033", tasks_dir=str(tasks_dir))

        assert result["status"] == "generated"
        assert result["filename"] == "task-033-admission-core-v1.md"
        assert get_parent_archive_ids(str(tasks_dir)) == []

    def test_tc2_a_parent_h1_still_conflicts(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-033-admission-core-v1.md", "# Task 033: Admission core V1")
        self._write(tasks_dir, "task-033-05a-sqltest-db.md", "# Task 033-05a: Test database")

        result = generate_task_archive_filename(
            "other", proposed_id="033", tasks_dir=str(tasks_dir))

        assert result["status"] == "conflict"
        assert get_parent_archive_ids(str(tasks_dir)) == [33]

    def test_tc3_a_parent_h1_overrides_a_numeric_first_segment(self, tmp_path):
        """The H1 resolves the old known limitation: `2024-migration` is a slug, not sub-task 2024."""
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-007-2024-migration.md", "# TASK 007 — Migration of 2024")

        result = generate_task_archive_filename(
            "other", proposed_id="007", tasks_dir=str(tasks_dir))

        assert result["status"] == "conflict"

    def test_tc4_3d_viewer_with_a_parent_h1_stays_a_parent(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-012-3d-viewer.md", "# Task 012: 3D viewer")
        assert get_parent_archive_ids(str(tasks_dir)) == [12]

    @pytest.mark.parametrize("name, h1, parents", [
        ("task-012-3d-viewer.md", None, [12]),
        ("task-005-1-usage-ddl.md", None, []),
        ("task-005-1-usage-ddl.md", "# Technical Specification: Usage DDL", []),
        ("task-005-m2-alpha.md", "# Task 006-01: an H1 of another task", [5]),
        ("task-005-1-usage-ddl.md", "# Task 006: an H1 of another task", []),
        ("task-005-05a-x.md", None, [5]),
    ])
    def test_tc5_without_a_matching_h1_the_name_decides(self, tmp_path, name, h1, parents):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, name, h1)
        assert get_parent_archive_ids(str(tasks_dir)) == parents

    # The name of each case reads the OPPOSITE way to its H1, so a pass shows the H1 decided:
    # `task-033-2024-x.md` is a sub-task by name, `task-033-05a-x.md` a parent by name.
    @pytest.mark.parametrize("h1, parents", [
        ("# Task 033: colon", [33]),
        ("# Task 033 — em dash", [33]),
        ("# Task 033 – en dash", [33]),
        ("# Task 033 - spaced hyphen", [33]),
        ("# Task 033", [33]),
        ("# TASK 033 — upper case", [33]),
        ("# Task 33: no zero padding", [33]),
    ])
    def test_h1_grammar_of_a_parent(self, tmp_path, h1, parents):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-033-2024-x.md", h1)
        assert get_parent_archive_ids(str(tasks_dir)) == parents

    @pytest.mark.parametrize("h1, parents", [
        ("# Task 033-05a: hyphen", []),
        ("# task 033-05a: lower case", []),
        ("# Task 33.1: dot, no zero padding", []),
        ("# Task 033-05 — em dash", []),
        ("# Task 033-05a-b: a subid of another grammar", [33]),
        ("# Task 033-05A: an upper-case letter is outside the grammar", [33]),
    ])
    def test_h1_grammar_of_a_subtask(self, tmp_path, h1, parents):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-033-05a-x.md", h1)
        assert get_parent_archive_ids(str(tasks_dir)) == parents

    def test_comments_and_front_matter_before_the_h1_are_skipped(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-033-05a-x.md").write_text(
            "---\n# Task 033: a YAML comment, not the H1\n---\n"
            "<!--\n# Task 033: inside a comment\n-->\n\n"
            "```markdown\n# Task 033: inside a fence\n```\n\n"
            "# Task 033-05a: the H1\n")
        assert get_parent_archive_ids(str(tasks_dir)) == []

    @pytest.mark.parametrize("body, parents", [
        ("﻿# Task 033-05a: after a BOM\n", []),
        ("<!--\n# Task 033-05a: inside an unclosed comment\n", [33]),
        ("~~~\n# Task 033-05a: inside an unclosed fence\n", [33]),
        ("# Task " + "0" * 5000 + "33-05a: a digit run past the int limit\n", []),
    ])
    def test_odd_heads(self, tmp_path, body, parents):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-033-05a-x.md").write_text(body, encoding="utf-8")
        assert get_parent_archive_ids(str(tasks_dir)) == parents

    @pytest.mark.parametrize("filler, parents", [(16384 - 40, [33]), (16384, [])])
    def test_the_h1_is_searched_in_the_first_16_kib(self, tmp_path, filler, parents):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-033-2024-x.md").write_text(
            "x" * filler + "\n# Task 033: late H1\n", encoding="ascii")
        assert get_parent_archive_ids(str(tasks_dir)) == parents

    @staticmethod
    def _scan_with_timeout(tasks_dir):
        """`get_parent_archive_ids` in a thread; a scan that blocks fails instead of stalling."""
        import threading
        result = []
        worker = threading.Thread(
            target=lambda: result.append(get_parent_archive_ids(str(tasks_dir))), daemon=True)
        worker.start()
        worker.join(timeout=10)
        assert not worker.is_alive(), "the scan blocked on a special file"
        return result[0]

    def test_a_fifo_is_not_read(self, tmp_path):
        """A FIFO named like a task file does not block the scan; its name decides."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        os.mkfifo(tasks_dir / "task-033-05a-x.md")
        assert self._scan_with_timeout(tasks_dir) == [33]

    def test_a_fifo_with_data_is_not_read(self, tmp_path):
        """Only a regular file is read: a FIFO holding a sub-task H1 is classified by its name."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        fifo = tasks_dir / "task-033-05a-x.md"
        os.mkfifo(fifo)
        reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
        writer = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
        try:
            os.write(writer, b"# Task 033-05a: x\n")
            assert self._scan_with_timeout(tasks_dir) == [33]
        finally:
            os.close(writer)
            os.close(reader)

    def test_tc6_auto_generation_reserves_an_id_held_by_letter_subtasks(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        self._write(tasks_dir, "task-033-05a-sqltest-db.md", "# Task 033-05a: Test database")
        self._write(tasks_dir, "task-033-08b-sql-tests.md", "# Task 033-08b: SQL tests")

        result = generate_task_archive_filename("brand-new", tasks_dir=str(tasks_dir))

        assert result["status"] == "generated"
        assert result["used_id"] == "034"


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


class TestAllowCorrectionPolarity:
    """ARC-7/8/9. One policy, four call surfaces, measured on each.

    ARC-1 decided that an ID already cited elsewhere is reported as a conflict,
    never renumbered without an explicit instruction. Commit 992b3ef applied
    that to `schemas.py` and `System/scripts/tool_runner.py` only, so the Python
    signature and the CLI kept renumbering.

    The class this replaces asserted one schema literal and nothing else:
    reverting `tool_runner.py` to `args.get("allow_correction", True)` left all
    39 tests green (measured, ARC-9). Each test below names the revert that
    turns it red.
    """

    @staticmethod
    def _tasks_dir_with_a_real_parent(tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "task-095-real-parent.md").touch()
        return tasks_dir

    def test_surface_1_schema_literal_is_false(self):
        """Red when `schemas.py` sets `"default": True`."""
        import schemas
        spec = next(t for t in schemas.TOOLS_SCHEMAS
                    if t["function"]["name"] == "generate_task_archive_filename")
        prop = spec["function"]["parameters"]["properties"]["allow_correction"]
        assert prop["default"] is False

    def test_surface_2_dispatcher_omitting_the_argument_refuses(self, tmp_path,
                                                               monkeypatch):
        """Red when `tool_runner.py` reads `args.get("allow_correction", True)`.

        The dispatcher hard-codes `tasks_dir` to the repo's own `docs/tasks`,
        so the effective argument is observed at the boundary instead of by
        archiving a real file.
        """
        import sys
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))), "System", "scripts"))
        import task_id_tool
        import tool_runner

        seen = {}

        def _recorder(slug, proposed_id=None, allow_correction=None,
                      tasks_dir=None):
            seen["allow_correction"] = allow_correction
            return {"filename": None, "used_id": None,
                    "status": "conflict", "message": "recorded"}

        # The dispatcher binds the name at call time via `from task_id_tool
        # import ...`, so patching the module attribute is what it will see.
        monkeypatch.setattr(task_id_tool, "generate_task_archive_filename",
                            _recorder)

        tool_runner.execute_tool({
            "name": "generate_task_archive_filename",
            "arguments": {"slug": "my-feature", "proposed_id": "095"},
        })

        assert seen["allow_correction"] is False

    def test_surface_3_python_default_refuses(self, tmp_path):
        """Red when `task_id_tool.py` declares `allow_correction: bool = True`."""
        tasks_dir = self._tasks_dir_with_a_real_parent(tmp_path)

        result = generate_task_archive_filename(
            slug="my-feature", proposed_id="095", tasks_dir=str(tasks_dir)
        )

        assert result["status"] == "conflict"
        assert result["used_id"] != "096"

    def test_surface_4_cli_without_a_flag_refuses(self, tmp_path):
        """Red when the CLI computes `allow_correction=not args.no_correction`."""
        tasks_dir = self._tasks_dir_with_a_real_parent(tmp_path)
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "task_id_tool.py")

        proc = subprocess.run(
            [sys.executable, tool, "my-feature", "--proposed-id", "095",
             "--tasks-dir", str(tasks_dir)],
            capture_output=True, text=True,
        )

        assert json.loads(proc.stdout)["status"] == "conflict"
        assert proc.returncode == 1

    def test_surface_4_cli_opts_in_explicitly(self, tmp_path):
        """The opt-in exists, so the CLI can still express both values."""
        tasks_dir = self._tasks_dir_with_a_real_parent(tmp_path)
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "task_id_tool.py")

        proc = subprocess.run(
            [sys.executable, tool, "my-feature", "--proposed-id", "095",
             "--tasks-dir", str(tasks_dir), "--allow-correction"],
            capture_output=True, text=True,
        )

        assert json.loads(proc.stdout)["status"] == "corrected"
        assert proc.returncode == 0

    def test_the_bare_new_id_form_is_untouched(self, tmp_path):
        """D2. Without `--proposed-id` the flag is never read.

        `02_analyst_prompt.md:48` and the planner card use the bare form for a
        task that has no ID yet. That path returns from the auto-generate branch
        before `allow_correction` is consulted, so flipping the default must not
        change it.
        """
        tasks_dir = self._tasks_dir_with_a_real_parent(tmp_path)
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "task_id_tool.py")

        proc = subprocess.run(
            [sys.executable, tool, "brand-new", "--tasks-dir", str(tasks_dir)],
            capture_output=True, text=True,
        )

        payload = json.loads(proc.stdout)
        assert payload["status"] == "generated"
        assert payload["used_id"] == "096"
        assert proc.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
