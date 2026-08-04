"""Tests for rebase_links (ARC-2).

One test per row of the decision table, one per markdown construct that can
carry a path, and regression pins for the two defects an adversarial review
found in the first design: the mutable-slot case and the indented-continuation
masking rule.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rebase_links import rebase_document_links, rebase_file  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    """A miniature repo: docs/{TASK.md,PLAN.md,ARCHITECTURE.md}, docs/tasks/, docs/plans/."""
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "docs" / "ARCHITECTURE.md").write_text("# arch")
    (tmp_path / "docs" / "TASK.md").write_text("# task")
    (tmp_path / "docs" / "PLAN.md").write_text("# plan")
    (tmp_path / "docs" / "tasks" / "task-063-01-x.md").write_text("# sub")
    (tmp_path / "README.md").write_text("# readme")
    return tmp_path


def rb(repo, text, from_dir="docs", to_dir="docs/plans", slot_map=None):
    return rebase_document_links(text, from_dir, to_dir, str(repo), slot_map)


def actions(records):
    return [r.action for r in records]


# ---------------------------------------------------------- decision table ---
class TestDecisionTable:
    def test_resolves_old_not_new_is_rewritten(self, repo):
        """The pure ARC-2 case."""
        new, rec = rb(repo, "[a](ARCHITECTURE.md)\n")
        assert actions(rec) == ["REWRITTEN"]
        assert "](../ARCHITECTURE.md)" in new

    def test_same_denotation_is_unchanged(self, repo):
        """A link whose meaning does not move is not touched."""
        new, rec = rb(repo, "[a](../README.md)\n", from_dir="docs", to_dir="docs")
        assert actions(rec) == ["UNCHANGED"]
        assert new == "[a](../README.md)\n"

    def test_broken_before_and_after_is_left_alone(self, repo):
        new, rec = rb(repo, "[a](nope.md)\n")
        assert actions(rec) == ["PRE_BROKEN"]
        assert new == "[a](nope.md)\n"

    def test_accidental_resolve_is_never_rewritten(self, repo):
        """Broken where authored, resolves by luck at the new home.

        Rewriting would turn an accidentally-working link into a definitely
        broken one. This row is also what makes a second run a no-op.
        """
        new, rec = rb(repo, "[a](../ARCHITECTURE.md)\n")
        assert actions(rec) == ["ACCIDENTAL_RESOLVE"]
        assert new == "[a](../ARCHITECTURE.md)\n"

    def test_escaping_repo_root_is_left_alone(self, repo):
        new, rec = rb(repo, "[a](../../../../etc/passwd)\n")
        assert actions(rec) == ["ESCAPES_ROOT"]
        assert new == "[a](../../../../etc/passwd)\n"

    def test_rerun_is_a_no_op(self, repo):
        once, _ = rb(repo, "[a](ARCHITECTURE.md)\n")
        twice, rec = rb(repo, once)
        assert twice == once
        assert actions(rec) == ["ACCIDENTAL_RESOLVE"]


# ------------------------------------------------------------ mutable slot ---
class TestMutableSlot:
    """`docs/TASK.md` is a slot, not an identity.

    A link to it meant *this* task's spec. Preserving the path re-points the
    citation at whatever task is current; preserving the referent means naming
    the archive the slot held.
    """

    def test_slot_resolves_to_archive_identity(self, repo):
        new, rec = rb(repo, "[spec](TASK.md)\n",
                      slot_map={"docs/TASK.md": "docs/tasks/task-063-fw.md"})
        assert actions(rec) == ["SLOT_RESOLVED"]
        assert "](../tasks/task-063-fw.md)" in new

    def test_slot_works_after_the_slot_file_is_gone(self, repo):
        """archive_plan runs after archive_task moved docs/TASK.md away."""
        os.remove(repo / "docs" / "TASK.md")
        new, rec = rb(repo, "[spec](TASK.md)\n",
                      slot_map={"docs/TASK.md": "docs/tasks/task-063-fw.md"})
        assert actions(rec) == ["SLOT_RESOLVED"]
        assert "](../tasks/task-063-fw.md)" in new

    def test_slot_link_keeps_its_fragment(self, repo):
        new, _ = rb(repo, "[s](TASK.md#4-acceptance-criteria)\n",
                    slot_map={"docs/TASK.md": "docs/tasks/task-063-fw.md"})
        assert "](../tasks/task-063-fw.md#4-acceptance-criteria)" in new

    def test_non_slot_link_is_unaffected_by_the_map(self, repo):
        new, rec = rb(repo, "[a](ARCHITECTURE.md)\n",
                      slot_map={"docs/TASK.md": "docs/tasks/task-063-fw.md"})
        assert actions(rec) == ["REWRITTEN"]
        assert "](../ARCHITECTURE.md)" in new


# --------------------------------------------------------------- constructs ---
class TestConstructs:
    def test_fenced_block_is_not_rewritten(self, repo):
        text = "```\n[a](ARCHITECTURE.md)\n```\n[b](ARCHITECTURE.md)\n"
        new, rec = rb(repo, text)
        assert actions(rec) == ["REWRITTEN"]
        assert "```\n[a](ARCHITECTURE.md)\n```" in new

    def test_tilde_fence_is_not_rewritten(self, repo):
        new, rec = rb(repo, "~~~\n[a](ARCHITECTURE.md)\n~~~\n")
        assert rec == []

    def test_inline_code_span_is_not_rewritten(self, repo):
        new, rec = rb(repo, "use `[a](ARCHITECTURE.md)` here\n")
        assert rec == []
        assert new == "use `[a](ARCHITECTURE.md)` here\n"

    def test_indented_list_continuation_IS_rewritten(self, repo):
        """Regression: masking 4-space indents as code swallowed 8 of 42 real
        links -- all lazy continuations of `- [ ]` items in a live plan."""
        text = ("- [ ] **T-095-01**\n"
                "      [s](tasks/task-063-01-x.md)\n")
        new, rec = rb(repo, text)
        assert actions(rec) == ["REWRITTEN"]
        assert "](../tasks/task-063-01-x.md)" in new

    def test_fragment_is_preserved(self, repo):
        new, _ = rb(repo, "[a](ARCHITECTURE.md#9-installer)\n")
        assert "](../ARCHITECTURE.md#9-installer)" in new

    def test_pure_anchor_is_ignored(self, repo):
        new, rec = rb(repo, "[a](#section)\n")
        assert rec == []

    def test_external_and_root_absolute_are_ignored(self, repo):
        text = "[a](https://x.dev/y) [b](/Attachments/i.png) [c](mailto:a@b.c)\n"
        new, rec = rb(repo, text)
        assert rec == []
        assert new == text

    def test_angle_bracket_target(self, repo):
        new, rec = rb(repo, "[a](<ARCHITECTURE.md>)\n")
        assert actions(rec) == ["REWRITTEN"]
        assert "](<../ARCHITECTURE.md>)" in new

    def test_image_is_rewritten(self, repo):
        (repo / "docs" / "d.png").write_bytes(b"x")
        new, rec = rb(repo, "![alt](d.png)\n")
        assert actions(rec) == ["REWRITTEN"]
        assert "](../d.png)" in new


# ------------------------------------------------------------------- files ---
class TestRebaseFile:
    def test_dry_run_does_not_write(self, repo):
        p = repo / "docs" / "plans" / "p.md"
        p.write_text("[a](ARCHITECTURE.md)\n")
        changed, rec = rebase_file(str(p), "docs", "docs/plans", str(repo),
                                   dry_run=True)
        assert changed is True
        assert p.read_text() == "[a](ARCHITECTURE.md)\n"

    def test_write_applies(self, repo):
        p = repo / "docs" / "plans" / "p.md"
        p.write_text("[a](ARCHITECTURE.md)\n")
        rebase_file(str(p), "docs", "docs/plans", str(repo))
        assert p.read_text() == "[a](../ARCHITECTURE.md)\n"

    def test_crlf_round_trips(self, repo):
        p = repo / "docs" / "plans" / "p.md"
        p.write_bytes(b"[a](ARCHITECTURE.md)\r\n")
        rebase_file(str(p), "docs", "docs/plans", str(repo))
        assert p.read_bytes() == b"[a](../ARCHITECTURE.md)\r\n"

    def test_cyrillic_content_round_trips(self, repo):
        p = repo / "docs" / "plans" / "p.md"
        p.write_text("Цель: [архитектура](ARCHITECTURE.md)\n", encoding="utf-8")
        rebase_file(str(p), "docs", "docs/plans", str(repo))
        assert p.read_text(encoding="utf-8") == \
            "Цель: [архитектура](../ARCHITECTURE.md)\n"


class TestReporting:
    def test_line_numbers_survive_masking(self, repo):
        text = "`x`\n\nfiller\n\n[a](ARCHITECTURE.md)\n"
        _, rec = rb(repo, text)
        assert rec[0].line == 5

    def test_record_carries_before_and_after(self, repo):
        _, rec = rb(repo, "[a](ARCHITECTURE.md)\n")
        assert rec[0].authored == "ARCHITECTURE.md"
        assert rec[0].new_target == "../ARCHITECTURE.md"
        assert rec[0].denotes_old == os.path.join("docs", "ARCHITECTURE.md")


class TestUnmappedSlot:
    """Regression: adversarial review found the fix run itself re-pointed an
    archived plan at the LIVE docs/TASK.md (TASK 096), converting a dead link
    into a silently wrong one that no link checker can detect.

    Slot awareness must be intrinsic, not opt-in.
    """

    def test_unmapped_slot_is_never_rewritten(self, repo):
        new, rec = rb(repo, "**Parent**: [docs/TASK.md](TASK.md)\n")
        assert actions(rec) == ["UNMAPPED_SLOT"]
        assert new == "**Parent**: [docs/TASK.md](TASK.md)\n"

    def test_unmapped_slot_is_reported_as_a_warning(self, repo):
        from rebase_links import ACTIONS_WARN
        assert "UNMAPPED_SLOT" in ACTIONS_WARN

    def test_unmapped_plan_slot_too(self, repo):
        new, rec = rb(repo, "[p](PLAN.md)\n")
        assert actions(rec) == ["UNMAPPED_SLOT"]
        assert new == "[p](PLAN.md)\n"

    def test_a_supplied_slot_still_resolves(self, repo):
        new, rec = rb(repo, "[spec](TASK.md)\n",
                      slot_map={"docs/TASK.md": "docs/tasks/task-063-fw.md"})
        assert actions(rec) == ["SLOT_RESOLVED"]
        assert "](../tasks/task-063-fw.md)" in new

    def test_non_slot_paths_are_unaffected(self, repo):
        """The guard must not swallow ordinary links."""
        new, rec = rb(repo, "[a](ARCHITECTURE.md)\n")
        assert actions(rec) == ["REWRITTEN"]


class TestCodeSpanBoundaries:
    """Regression: the code-span mask desynchronized and blanked real links.

    Two boundary rules, both violated by the naive `` (`+)(?:.|\\n)*?\\1 ``:
    a closing run must be the same LENGTH, and a span cannot cross a blank
    line. Measured cost of the old form on this corpus: 3 real links in
    docs/design/095_workflow_loop_contract.md were invisible to the tool,
    which would have reported success while leaving them broken.
    """

    def test_lone_backtick_does_not_close_against_a_longer_run(self, repo):
        """`` ` ``` ` `` is ONE span; closing on the run's first character
        left every later link mis-masked."""
        text = "| x ` ``` ` |\n\n[a](ARCHITECTURE.md)\n"
        new, rec = rb(repo, text)
        assert actions(rec) == ["REWRITTEN"]
        assert "](../ARCHITECTURE.md)" in new

    def test_unbalanced_backtick_does_not_swallow_later_links(self, repo):
        """A stray backtick must not pair across a blank line."""
        text = "an unclosed ` backtick\n\n[a](ARCHITECTURE.md)\n"
        new, rec = rb(repo, text)
        assert actions(rec) == ["REWRITTEN"]

    def test_double_backtick_span_containing_a_backtick(self, repo):
        text = "`` ` `` and then [a](ARCHITECTURE.md)\n"
        new, rec = rb(repo, text)
        assert actions(rec) == ["REWRITTEN"]

    def test_a_link_written_as_a_syntax_example_stays_masked(self, repo):
        """The 13 corpus links that are documentation of link syntax, not
        links. Recovering the real ones must not un-mask these."""
        new, rec = rb(repo, "use `[Ref](ARCHITECTURE.md)` in docs\n")
        assert rec == []
        assert new == "use `[Ref](ARCHITECTURE.md)` in docs\n"

    def test_bare_target_in_a_code_span_is_not_a_link(self, repo):
        """`](...)` has no `[`; it is prose about link syntax. It reached the
        link regex only because the mask had desynchronized."""
        new, rec = rb(repo, "| Link targets `](...)` | not prose |\n")
        assert rec == []

    def test_span_may_still_wrap_one_line(self, repo):
        """CommonMark allows a span across a newline -- just not a blank one."""
        new, rec = rb(repo, "`spanning\nnewline [a](ARCHITECTURE.md)`\n")
        assert rec == []


class TestSlotTargetIsAForwardReference:
    """Regression: the documented Step 5.5 command exited 1 on the happy path.

    The conservation law probed SLOT_RESOLVED targets on disk. But a slot map
    is the caller DECLARING what the slot becomes, and in the protocol's own
    order that file does not exist yet -- Step 5.5 names
    `docs/plans/plan-NNN-x.md`, which Step 7 creates afterwards. Exit 1 reads
    as "a link regressed", i.e. the protocol told the agent to stop on success.

    The first adversarial round recorded this finding as NOT REPRODUCING. It
    measured the command without `--slot`, which is not the documented one.
    """

    @staticmethod
    def _archive_fixture(tmp_path):
        (tmp_path / "docs" / "tasks").mkdir(parents=True)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        (tmp_path / "docs" / "ARCHITECTURE.md").write_text("# arch")
        moved = tmp_path / "docs" / "tasks" / "task-077-login.md"
        moved.write_text("[p](PLAN.md)\n[a](ARCHITECTURE.md)\n")
        return moved

    def test_step_5_5_exits_zero_before_the_plan_is_archived(self, tmp_path):
        from rebase_links import _main as main
        moved = self._archive_fixture(tmp_path)
        code = main([str(moved), "--from", "docs", "--to", "docs/tasks",
                     "--repo-root", str(tmp_path),
                     "--slot", "docs/PLAN.md=docs/plans/plan-077-login.md"])
        assert code == 0
        assert "](../plans/plan-077-login.md)" in moved.read_text()

    def test_a_link_broken_before_the_move_is_reported_as_review(self, tmp_path):
        """ARC-5. This fixture exits 3, not 1 — it never reaches the conservation
        branch.

        It was named `test_a_real_regression_still_exits_one` and asserted only
        `code != 0`. Deleting the target BEFORE `main` runs classifies the link
        PRE_BROKEN, so nothing is rewritten and the run exits 3. The name
        promised a guarantee the fixture did not exercise. The reachable exit 1
        is pinned in TestSlotTargetMustExist below.
        """
        from rebase_links import _main as main
        (tmp_path / "docs" / "tasks").mkdir(parents=True)
        (tmp_path / "docs" / "ARCHITECTURE.md").write_text("# a")
        moved = tmp_path / "docs" / "tasks" / "t.md"
        moved.write_text("[a](ARCHITECTURE.md)\n")
        os.remove(tmp_path / "docs" / "ARCHITECTURE.md")
        code = main([str(moved), "--from", "docs", "--to", "docs/tasks",
                     "--repo-root", str(tmp_path)])
        assert code == 3

    def test_a_wrong_slot_map_is_still_surfaced(self, tmp_path, capsys):
        """Exempting slots from the exit code must not make a typo invisible."""
        from rebase_links import _main as main
        moved = self._archive_fixture(tmp_path)
        main([str(moved), "--from", "docs", "--to", "docs/tasks",
              "--repo-root", str(tmp_path),
              "--slot", "docs/PLAN.md=docs/plans/TYPO.md"])
        assert "SLOT_PENDING" in capsys.readouterr().out

    def test_slot_target_that_exists_reports_no_pending(self, tmp_path, capsys):
        from rebase_links import _main as main
        moved = self._archive_fixture(tmp_path)
        (tmp_path / "docs" / "plans" / "plan-077-login.md").write_text("# p")
        code = main([str(moved), "--from", "docs", "--to", "docs/tasks",
                     "--repo-root", str(tmp_path),
                     "--slot", "docs/PLAN.md=docs/plans/plan-077-login.md"])
        assert code == 0
        assert "SLOT_PENDING" not in capsys.readouterr().out


class TestSlotTargetMustExist:
    """ARC-6. At Step 7.6.5 the slot target is already on disk, so a typo in it
    is detectable — and was reported as clean.

    `SLOT_RESOLVED` sits in neither ACTIONS_WARN nor _CONSERVED, so a slot map
    naming an absent file rewrote the link and exited 0 with `"ok": true`.
    Measured: `--slot docs/TASK.md=docs/tasks/task-077-logn.md` against an
    archive named `task-077-login.md` rewrote the citation and returned 0.

    The exemption is right at Step 5.5, where the plan archive does not exist
    yet. `--slot-must-exist` is how the caller states which of the two it is.
    """

    @staticmethod
    def _plan_fixture(tmp_path):
        (tmp_path / "docs" / "tasks").mkdir(parents=True)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        (tmp_path / "docs" / "tasks" / "task-077-login.md").write_text("# t")
        moved = tmp_path / "docs" / "plans" / "plan-077-login.md"
        moved.write_text("[t](TASK.md)\n")
        return moved

    def test_a_mistyped_slot_target_exits_one(self, tmp_path):
        """Red until `--slot-must-exist` sets the failure flag."""
        from rebase_links import _main as main
        moved = self._plan_fixture(tmp_path)
        code = main([str(moved), "--from", "docs", "--to", "docs/plans",
                     "--repo-root", str(tmp_path), "--slot-must-exist",
                     "--slot", "docs/TASK.md=docs/tasks/task-077-logn.md"])
        assert code == 1

    def test_the_correct_slot_target_exits_zero(self, tmp_path):
        from rebase_links import _main as main
        moved = self._plan_fixture(tmp_path)
        code = main([str(moved), "--from", "docs", "--to", "docs/plans",
                     "--repo-root", str(tmp_path), "--slot-must-exist",
                     "--slot", "docs/TASK.md=docs/tasks/task-077-login.md"])
        assert code == 0
        assert "](../tasks/task-077-login.md)" in moved.read_text()

    def test_a_forward_reference_stays_exempt_without_the_flag(self, tmp_path):
        """Step 5.5 must keep exiting 0 — the plan archive is created later."""
        from rebase_links import _main as main
        (tmp_path / "docs" / "tasks").mkdir(parents=True)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        moved = tmp_path / "docs" / "tasks" / "task-077-login.md"
        moved.write_text("[p](PLAN.md)\n")
        code = main([str(moved), "--from", "docs", "--to", "docs/tasks",
                     "--repo-root", str(tmp_path),
                     "--slot", "docs/PLAN.md=docs/plans/plan-077-login.md"])
        assert code == 0

    def test_json_reports_not_ok_when_the_assertion_fails(self, tmp_path,
                                                          capsys):
        """`"ok": true` on a dangling rewrite is what ARC-6 measured."""
        from rebase_links import _main as main
        moved = self._plan_fixture(tmp_path)
        main([str(moved), "--from", "docs", "--to", "docs/plans",
              "--repo-root", str(tmp_path), "--slot-must-exist", "--json",
              "--slot", "docs/TASK.md=docs/tasks/task-077-logn.md"])
        assert json.loads(capsys.readouterr().out)["ok"] is False
