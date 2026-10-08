"""Tests for slot_links.py: `rebase_links.py --inbound` re-targets own slot links (TASK 115).

`skill-archive-task` Steps 5.5 and 7.6.5 rebase the links inside the moved documents only. A link in
another document that resolves to `docs/TASK.md` or `docs/PLAN.md` kept naming the slot, and the
next task's TASK and PLAN filled it (WI-38). This module pins TC-0 to TC-46 of TASK 115 §8:

* the task's sub-task files and, with `--since`, its added lines are re-targeted; every other slot
  link is listed as `INBOUND` and left as written (TC-1 to TC-5, TC-15, TC-16, TC-24);
* fences and code spans, link text, fragments and reference definitions (TC-6 to TC-8);
* operands, `--since`, links, hard links, dry run, CRLF, undecodable files, the postcondition, the
  walk mode and the JSON output (TC-9 to TC-14, TC-17 to TC-20);
* no diff driver, textconv driver, clean filter or fsmonitor hook runs, inherited `GIT_DIR` and
  `GIT_INDEX_FILE` change nothing, and a root below the top level attributes lines (TC-21 to TC-23).

Git fixtures run with `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` and a fixed identity,
set for the test process so that the module's own git calls read no operator configuration.
"""

import errno
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import slot_links
from slot_links import InboundError, retarget_inbound

TOOLS = Path(__file__).resolve().parent
#: The script an allow rule names. Stage 3 of TASK 115 points this at `rebase_links.py`.
REBASE = TOOLS / "rebase_links.py"

TASK = "docs/tasks/task-033-admission-core-v1.md"
PLAN = "docs/plans/plan-033-admission-core-v1.md"
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


@pytest.fixture(autouse=True)
def isolated_git(monkeypatch, tmp_path):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", os.path.realpath(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for key, value in IDENTITY.items():
        monkeypatch.setenv(key, value)


def write(root, rel, text, newline="\n"):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    return path


def tree(root):
    """Every file under `root` but `.git/`, with its bytes, links shown by their target."""
    entries = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            entries[rel] = ("->" + os.readlink(path)) if path.is_symlink() else path.read_bytes()
    return entries


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_INDEX_FILE")}
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          env=env, text=True).stdout.strip()


def init_repo(root):
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "maintenance.auto", "false")
    git(root, "config", "gc.auto", "0")


def commit(root, message="c"):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def project(tmp_path):
    """A project root with the archives of task 033 and the next task's `docs/TASK.md`."""
    root = Path(os.path.realpath(tmp_path)) / "project"
    write(root, TASK, "# Task 033: Admission core V1\n\nBody.\n")
    write(root, PLAN, "# Plan 033\n\n[docs/TASK.md](../tasks/task-033-admission-core-v1.md)\n")
    write(root, "docs/TASK.md", "# Task 034: Next\n\nSee [PLAN.md](PLAN.md).\n")
    write(root, "docs/PLAN.md", "# Plan 034\n")
    return root


def records(result, action=None):
    return [(r.file, r.line, r.action) for r in result.records
            if action is None or r.action == action]


def run_cli(root, *args):
    return subprocess.run([sys.executable, str(REBASE), "--inbound", *args], cwd=root,
                          capture_output=True, text=True, timeout=120)


# --- the interface -----------------------------------------------------------------------------

def test_tc0_the_interface_exists():
    """TC-0. Passes on the stub of PLAN A1; fails at the base, where the module is absent."""
    assert issubclass(InboundError, Exception)
    assert slot_links.InboundResult._fields == ("records", "archived_slot_links", "scan", "since",
                                                "exit_code")
    assert slot_links.InboundRecord._fields == ("file", "line", "action", "authored",
                                                "new_target", "reason")
    assert callable(retarget_inbound) and callable(slot_links.main)


# --- own links: sub-tasks, added lines, ledgers, archives ----------------------------------------

def test_tc1_subtask_links_are_retargeted_others_listed(project):
    """TC-1, the WI-38 acceptance. Fails when sub-task files are not own."""
    sub = write(project, "docs/tasks/task-033-01-run-guards.md",
                "# Task 033-01: Guards\n\n| Plan | [docs/PLAN.md](../PLAN.md) |\n")
    other = write(project, "docs/design/notes.md", "See [the task](../TASK.md).\n")

    result = retarget_inbound(str(project), TASK, PLAN)

    assert "[plan-033](../plans/plan-033-admission-core-v1.md)" in sub.read_text()
    assert other.read_text() == "See [the task](../TASK.md).\n"
    assert records(result) == [("docs/design/notes.md", 1, "INBOUND"),
                               ("docs/tasks/task-033-01-run-guards.md", 3, "RETARGETED")]
    assert result.exit_code == 3
    for record in result.records:
        if record.action == "RETARGETED":
            assert slot_links._resolves(str(project), record)


def test_tc2_lines_added_since_the_base_are_own(project):
    """TC-2. Fails when whole changed files count as own."""
    design = write(project, "docs/design/core.md", "Old [spec](../TASK.md).\n\nText.\n")
    init_repo(project)
    base = commit(project)
    design.write_text("Old [spec](../TASK.md).\n\nText.\n\nNew [spec](../TASK.md).\n")

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert design.read_text() == ("Old [spec](../TASK.md).\n\nText.\n\n"
                                  "New [spec](../tasks/task-033-admission-core-v1.md).\n")
    assert records(result) == [("docs/design/core.md", 1, "INBOUND"),
                               ("docs/design/core.md", 5, "RETARGETED")]
    assert result.since == base


def test_tc3_an_untracked_document_is_own(project):
    init_repo(project)
    base = commit(project)
    new = write(project, "docs/design/new.md", "[docs/TASK.md](../TASK.md)\n")

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert new.read_text() == "[task-033](../tasks/task-033-admission-core-v1.md)\n"
    assert records(result, "RETARGETED") == [("docs/design/new.md", 1, "RETARGETED")]


def test_tc4_a_ledger_record_is_never_rewritten(project):
    init_repo(project)
    base = commit(project)
    record = write(project, "docs/backlog/wi-9-x.md", "Body [task](../TASK.md).\n")

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert record.read_text() == "Body [task](../TASK.md).\n"
    assert records(result) == [("docs/backlog/wi-9-x.md", 1, "INBOUND")]


def test_tc5_archives_are_counted_and_the_slots_not_read(project):
    """TC-5. Fails when archived documents are listed."""
    write(project, "docs/tasks/task-020-old.md", "# Task 020: Old\n\n[x](../TASK.md)\n")
    write(project, "docs/plans/plan-020-old.md", "# Plan\n\n[x](../PLAN.md) [y](../TASK.md)\n")

    result = retarget_inbound(str(project), TASK, PLAN)

    assert result.records == []
    assert result.archived_slot_links == 3
    assert result.exit_code == 0
    assert (project / "docs/TASK.md").read_text() == "# Task 034: Next\n\nSee [PLAN.md](PLAN.md).\n"


def test_tc6_fences_and_code_spans_are_not_links(project):
    text = ("# Task 033-02: x\n\n```md\n[a](../TASK.md)\n```\n\nUse `[b](../PLAN.md)` here.\n")
    sub = write(project, "docs/tasks/task-033-02-x.md", text)

    result = retarget_inbound(str(project), TASK, PLAN)

    assert sub.read_text() == text
    assert result.records == []
    assert result.exit_code == 0


@pytest.mark.parametrize("before, after", [
    ("[docs/TASK.md](../TASK.md)", "[task-033](task-033-admission-core-v1.md)"),
    ("[`TASK.md`](../TASK.md)", "[`task-033`](task-033-admission-core-v1.md)"),
    ("[../PLAN.md](../PLAN.md)", "[plan-033](../plans/plan-033-admission-core-v1.md)"),
    ("[TASK.md §3 UC-01](../TASK.md)", "[TASK.md §3 UC-01](task-033-admission-core-v1.md)"),
    ("![docs/TASK.md](../TASK.md)", "![docs/TASK.md](task-033-admission-core-v1.md)"),
    ("[see [docs/PLAN.md]](../PLAN.md)",
     "[see [docs/PLAN.md]](../plans/plan-033-admission-core-v1.md)"),
])
def test_tc7_link_text(project, before, after):
    sub = write(project, "docs/tasks/task-033-03-x.md", f"# Task 033-03: x\n\n{before}\n")
    retarget_inbound(str(project), TASK, PLAN)
    assert sub.read_text() == f"# Task 033-03: x\n\n{after}\n"


@pytest.mark.parametrize("before, after", [
    ("[s](../TASK.md#3-use-cases)", "[s](task-033-admission-core-v1.md#3-use-cases)"),
    ("[s](<../PLAN.md>)", "[s](<../plans/plan-033-admission-core-v1.md>)"),
    ("[ref]: ../TASK.md", "[ref]: task-033-admission-core-v1.md"),
    ('<a href="../PLAN.md">p</a>', '<a href="../plans/plan-033-admission-core-v1.md">p</a>'),
])
def test_tc8_fragment_brackets_and_reference_definitions(project, before, after):
    sub = write(project, "docs/tasks/task-033-04-x.md", f"# Task 033-04: x\n\n{before}\n")
    retarget_inbound(str(project), TASK, PLAN)
    assert sub.read_text() == f"# Task 033-04: x\n\n{after}\n"


# --- operands and git ---------------------------------------------------------------------------

@pytest.mark.parametrize("args", [
    ("--task", "docs/tasks/task-099-missing.md"),
    ("--task", "docs/tasks/task-033-01-guards.md"),
    ("--task", "docs/tasks/linked-033.md"),
    ("--task", "docs/TASK.md"),
    ("--task", "./" + TASK),
    ("--task", TASK, "--plan", "docs/plans/plan-034-admission-core-v1.md"),
    ("--task", "docs/tasks/task-033-linked.md"),
    ("--plan", PLAN),
])
def test_tc9_operands_exit_2_and_write_nothing(project, args):
    write(project, "docs/tasks/task-033-01-guards.md", "# Task 033-01: Guards\n\n[x](../TASK.md)\n")
    (project / "docs/tasks/task-033-linked.md").symlink_to(project / TASK)
    before = tree(project)
    result = run_cli(project, *args)
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stderr)["ok"] is False
    assert tree(project) == before


def test_tc10_since_errors_exit_2(project):
    write(project, "docs/tasks/task-033-01-x.md", "# Task 033-01: x\n\n[x](../TASK.md)\n")
    before = tree(project)
    walk = run_cli(project, "--task", TASK, "--since", "HEAD")  # walk mode
    assert walk.returncode == 2 and json.loads(walk.stderr)["ok"] is False
    init_repo(project)
    commit(project)
    git(project, "checkout", "-q", "-b", "side")
    write(project, "docs/side.md", "side\n")
    side = commit(project, "side")
    git(project, "checkout", "-q", "main")
    for since in ("--since=-x", "--since=deadbeef00", "--since=HEAD~5", f"--since={side}"):
        result = run_cli(project, "--task", TASK, since)
        assert result.returncode == 2, (since, result.stderr)
        assert json.loads(result.stderr)["ok"] is False
    after = tree(project)
    assert {k: v for k, v in after.items() if k in before} == before


def test_tc11_links_and_hard_links_are_not_written(project, tmp_path):
    outside = Path(os.path.realpath(tmp_path)) / "outside.md"
    outside.write_text("[x](../TASK.md)\n")
    (project / "docs/tasks").mkdir(parents=True, exist_ok=True)
    (project / "docs/tasks/task-033-05-link.md").symlink_to(outside)
    hard = write(project, "docs/tasks/task-033-06-hard.md", "# Task 033-06: h\n\n[x](../TASK.md)\n")
    os.link(hard, project / "alias.md")

    result = retarget_inbound(str(project), TASK, PLAN)

    assert outside.read_text() == "[x](../TASK.md)\n"
    assert hard.read_text() == "# Task 033-06: h\n\n[x](../TASK.md)\n"
    actions = {(r.file, r.action) for r in result.records}
    assert ("docs/tasks/task-033-05-link.md", "SKIPPED") in actions
    assert ("docs/tasks/task-033-06-hard.md", "REFUSED") in actions
    assert result.exit_code == 3


def test_tc12_dry_run_writes_nothing_and_reports_the_same(project):
    write(project, "docs/tasks/task-033-07-x.md", "# Task 033-07: x\n\n[a](../TASK.md)\n")
    write(project, "docs/other.md", "[b](TASK.md)\n")
    before = tree(project)

    dry = retarget_inbound(str(project), TASK, PLAN, dry_run=True)
    assert tree(project) == before
    real = retarget_inbound(str(project), TASK, PLAN)
    assert dry.records == real.records
    assert dry.exit_code == real.exit_code == 3


def test_tc13_crlf_is_kept(project):
    sub = write(project, "docs/tasks/task-033-08-crlf.md",
                "# Task 033-08: c\n\n[docs/PLAN.md](../PLAN.md)\nEnd\n", newline="\r\n")
    retarget_inbound(str(project), TASK, PLAN)
    assert sub.read_bytes() == (b"# Task 033-08: c\r\n\r\n"
                                b"[plan-033](../plans/plan-033-admission-core-v1.md)\r\nEnd\r\n")


def test_tc14_only_own_links_exit_0(project):
    write(project, "docs/tasks/task-033-09-x.md", "# Task 033-09: x\n\n[a](../TASK.md)\n")
    result = retarget_inbound(str(project), TASK, PLAN)
    assert result.exit_code == 0
    assert records(result) == [("docs/tasks/task-033-09-x.md", 3, "RETARGETED")]


def test_tc15_a_plan_link_without_plan_is_listed(project):
    sub = write(project, "docs/tasks/task-033-10-x.md",
                "# Task 033-10: x\n\n[p](../PLAN.md) [t](../TASK.md)\n")
    result = retarget_inbound(str(project), TASK)
    assert sub.read_text() == ("# Task 033-10: x\n\n"
                               "[p](../PLAN.md) [t](task-033-admission-core-v1.md)\n")
    assert ("docs/tasks/task-033-10-x.md", 3, "INBOUND") in records(result)


def test_tc16_a_subtask_of_another_task_is_listed(project):
    other = write(project, "docs/tasks/task-012-01-x.md", "# Task 012-01: x\n\n[t](../TASK.md)\n")
    result = retarget_inbound(str(project), TASK, PLAN)
    assert other.read_text() == "# Task 012-01: x\n\n[t](../TASK.md)\n"
    assert records(result) == [("docs/tasks/task-012-01-x.md", 3, "INBOUND")]


def test_tc17_an_undecodable_file_is_unreadable(project):
    (project / "docs/bad.md").write_bytes(b"[x](TASK.md) \xff\xfe\n")
    result = retarget_inbound(str(project), TASK, PLAN)
    assert [(r.file, r.line, r.action) for r in result.records] == [("docs/bad.md", None,
                                                                      "UNREADABLE")]
    assert result.exit_code == 3


def test_tc18_an_unresolved_rewrite_exits_1(project, monkeypatch):
    """TC-18. Fails when the postcondition is dropped."""
    write(project, "docs/tasks/task-033-11-x.md", "# Task 033-11: x\n\n[a](../TASK.md)\n")
    original = slot_links._write_file

    def write_then_remove_the_archive(*args):
        reason = original(*args)
        os.unlink(project / TASK)
        return reason

    monkeypatch.setattr(slot_links, "_write_file", write_then_remove_the_archive)
    assert retarget_inbound(str(project), TASK).exit_code == 1


def test_tc19_walk_mode_skips_git_node_modules_and_directory_links(project, tmp_path):
    outside = Path(os.path.realpath(tmp_path)) / "elsewhere"
    write(outside, "x.md", "[x](../docs/TASK.md)\n")
    write(project, ".git/notes.md", "[x](../docs/TASK.md)\n")
    write(project, "node_modules/pkg/README.md", "[x](../../docs/TASK.md)\n")
    write(project, "env/pyvenv.cfg", "home = /usr\n")
    write(project, "env/lib/README.md", "[x](../../docs/TASK.md)\n")
    (project / "linked").symlink_to(outside, target_is_directory=True)

    result = retarget_inbound(str(project), TASK, PLAN)

    assert result.scan == "walk"
    assert result.records == []
    assert result.exit_code == 0


def test_tc20_json_output(project):
    write(project, "docs/tasks/task-033-12-x.md", "# Task 033-12: x\n\n[a](../TASK.md)\n")
    write(project, "docs/other.md", "[b](TASK.md)\n")
    result = run_cli(project, "--task", TASK, "--plan", PLAN, "--json", "--dry-run")
    assert result.returncode == 3, result.stderr
    report = json.loads(result.stdout)
    assert set(report) == {"ok", "exit_code", "scan", "since", "archived_slot_links", "records"}
    assert report["ok"] is True and report["exit_code"] == 3 and report["scan"] == "walk"
    assert {r["action"] for r in report["records"]} == {"RETARGETED", "INBOUND"}
    assert set(report["records"][0]) == {"file", "line", "action", "authored", "new_target",
                                         "reason"}


# --- git hardening ------------------------------------------------------------------------------

def test_tc21_no_driver_filter_or_hook_runs(project, tmp_path):
    """TC-21. Fails when the module runs `git diff` or `git status`."""
    design = write(project, "docs/design/core.md", "Old [s](../TASK.md).\n")
    same = write(project, "docs/design/same.md", "aaaa\n")
    init_repo(project)
    base = commit(project)
    scratch = Path(os.path.realpath(tmp_path))
    sentinels = {}
    for name in ("external", "textconv", "clean", "smudge", "fsmonitor"):
        sentinels[name] = scratch / f"sentinel-{name}"
        hook = scratch / f"{name}.sh"
        body = ('cat "$1"' if name == "textconv"
                else "cat" if name in ("clean", "smudge") else "exit 0")
        hook.write_text(f"#!/bin/sh\ntouch '{sentinels[name]}'\n{body}\n")
        hook.chmod(0o755)
    for key, value in (("diff.external", scratch / "external.sh"),
                       ("diff.md.textconv", scratch / "textconv.sh"),
                       ("filter.sentinel.clean", scratch / "clean.sh"),
                       ("filter.sentinel.smudge", scratch / "smudge.sh"),
                       ("core.fsmonitor", scratch / "fsmonitor.sh")):
        git(project, "config", key, str(value))
    write(project, ".gitattributes", "*.md diff=md filter=sentinel\n")
    design.write_text("Old [s](../TASK.md).\n\nNew [s](../TASK.md).\n")

    # Positive control: each mechanism fires when git runs the command that uses it.
    for args in (("diff",), ("diff", "--no-ext-diff"),
                 ("hash-object", "--path", "docs/design/core.md", "docs/design/core.md"),
                 ("cat-file", "--filters", f"{base}:docs/design/core.md"),
                 ("status", "--porcelain")):
        subprocess.run(["git", "-C", str(project), *args], capture_output=True, check=False)
    assert all(path.exists() for path in sentinels.values()), \
        {name: path.exists() for name, path in sentinels.items()}
    for path in sentinels.values():
        path.unlink()
    # A tracked file changed at the same size: `git status` must read it through the clean
    # filter, since its size no longer tells it apart from the index.
    same.write_text("bbbb\n")
    stamp = same.stat()
    os.utime(same, (stamp.st_atime + 5, stamp.st_mtime + 5))

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert not [name for name, path in sentinels.items() if path.exists()]
    assert ("docs/design/core.md", 3, "RETARGETED") in records(result)


def test_tc22_inherited_git_variables_change_nothing(project, tmp_path, monkeypatch):
    write(project, "docs/design/core.md", "Old [s](../TASK.md).\n")
    init_repo(project)
    base = commit(project)
    write(project, "docs/design/core.md", "Old [s](../TASK.md).\nNew [s](../TASK.md).\n")
    expected = retarget_inbound(str(project), TASK, PLAN, since=base, dry_run=True)
    assert expected.exit_code in (0, 3) and expected.records

    elsewhere = Path(os.path.realpath(tmp_path)) / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.setenv("GIT_DIR", str(elsewhere))
    monkeypatch.setenv("GIT_INDEX_FILE", str(elsewhere / "index"))
    assert retarget_inbound(str(project), TASK, PLAN, since=base, dry_run=True) == expected


def test_tc23_a_root_below_the_top_level_through_a_link(tmp_path):
    real = Path(os.path.realpath(tmp_path))
    top = real / "mono"
    write(top / "project", TASK, "# Task 033: x\n")
    design = write(top / "project", "docs/design/core.md", "Old [s](../TASK.md).\n")
    init_repo(top)
    base = commit(top)
    design.write_text("Old [s](../TASK.md).\nNew [s](../TASK.md).\n")
    (real / "link").symlink_to(top, target_is_directory=True)

    result = retarget_inbound(str(real / "link" / "project"), TASK, since=base)

    assert records(result) == [("docs/design/core.md", 1, "INBOUND"),
                               ("docs/design/core.md", 2, "RETARGETED")]
    assert design.read_text() == ("Old [s](../TASK.md).\n"
                                  "New [s](../tasks/task-033-admission-core-v1.md).\n")


def test_tc24_only_the_added_copy_of_a_duplicated_line_is_own(project):
    line = "[s](../TASK.md)"
    design = write(project, "docs/design/core.md", f"A\n{line}\nB\n")
    init_repo(project)
    base = commit(project)
    design.write_text(f"A\n{line}\nB\n{line}\n")

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert records(result) == [("docs/design/core.md", 2, "INBOUND"),
                               ("docs/design/core.md", 4, "RETARGETED")]


def test_platform_without_o_nofollow_refuses(project, monkeypatch):
    monkeypatch.delattr(os, "O_NOFOLLOW")
    with pytest.raises(InboundError):
        retarget_inbound(str(project), TASK, PLAN)


# --- stage-2 round 1 ---------------------------------------------------------------------------

def _reason(result, file, action):
    return [r.reason for r in result.records if r.file == file and r.action == action]


def _after_read(monkeypatch, rel, change):
    """Run `change(path)` right after `_read` has read the file at `rel`."""
    original = slot_links._read

    def hooked(path):
        value = original(path)
        if path.endswith(rel):
            change(Path(path))
        return value

    monkeypatch.setattr(slot_links, "_read", hooked)


def test_tc26_a_parent_linked_outside_is_refused(project, tmp_path):
    write(project, "docs/design/x.md", "Old.\n")
    init_repo(project)
    base = commit(project)
    outside = Path(os.path.realpath(tmp_path)) / "outside"
    outside.mkdir()
    (outside / "x.md").write_text("Old.\nNew [s](../TASK.md).\n")
    shutil.rmtree(project / "docs" / "design")
    (project / "docs" / "design").symlink_to(outside, target_is_directory=True)

    result = retarget_inbound(str(project), TASK, PLAN, since=base)

    assert _reason(result, "docs/design/x.md", "REFUSED") == [
        "its directory resolves outside the working directory"]
    assert (outside / "x.md").read_text() == "Old.\nNew [s](../TASK.md).\n"


@pytest.mark.parametrize("how", ["replaced", "changed", "fifo"])
def test_tc26_a_file_changed_after_the_read_is_refused(project, monkeypatch, how):
    rel = "docs/tasks/task-033-20-x.md"
    sub = write(project, rel, "# Task 033-20: x\n\n[a](../TASK.md)\n")

    def change(path):
        if how == "replaced":
            fresh = path.with_name("fresh.tmp")
            fresh.write_bytes(path.read_bytes())
            os.replace(fresh, path)
        elif how == "changed":
            with open(path, "a") as handle:
                handle.write("more\n")
        else:
            path.unlink()
            os.mkfifo(path)

    _after_read(monkeypatch, rel, change)
    result = retarget_inbound(str(project), TASK, PLAN)

    expected = "is not a regular file" if how == "fifo" else "changed during the run"
    assert _reason(result, rel, "REFUSED") == [expected]
    if how != "fifo":
        assert "[a](../TASK.md)" in sub.read_text()


def test_tc27_a_file_replaced_after_the_write_is_refused(project, monkeypatch):
    rel = "docs/tasks/task-033-21-x.md"
    sub = write(project, rel, "# Task 033-21: x\n\n[a](../TASK.md)\n")
    real_fsync = os.fsync

    def editor_saves_after(fd):
        real_fsync(fd)
        fresh = sub.with_name("editor.tmp")
        fresh.write_text("# Task 033-21: x\n\n[a](../TASK.md) edited\n")
        os.replace(fresh, sub)

    monkeypatch.setattr(os, "fsync", editor_saves_after)
    result = retarget_inbound(str(project), TASK, PLAN)

    assert _reason(result, rel, "REFUSED") == ["changed during the run"]
    assert sub.read_text() == "# Task 033-21: x\n\n[a](../TASK.md) edited\n"


def test_tc28_the_dry_run_applies_the_write_guard(project):
    rel = "docs/tasks/task-033-22-x.md"
    sub = write(project, rel, "# Task 033-22: x\n\n[a](../TASK.md)\n")
    os.link(sub, project / "alias.md")

    dry = retarget_inbound(str(project), TASK, PLAN, dry_run=True)
    real = retarget_inbound(str(project), TASK, PLAN)

    assert dry.records == real.records
    assert _reason(dry, rel, "REFUSED") == ["has 2 hard links"]


def test_tc29_overlapping_edits_are_refused(project):
    rel = "docs/tasks/task-033-23-x.md"
    text = '# Task 033-23: x\n\n[x](href="../TASK.md"/../../../TASK.md) tail\n'
    sub = write(project, rel, text)

    result = retarget_inbound(str(project), TASK, PLAN)

    assert set(_reason(result, rel, "REFUSED")) == {"overlapping links"}
    assert sub.read_text() == text


def test_tc30_a_write_that_fails_after_its_first_byte_exits_1(project, monkeypatch):
    rel = "docs/tasks/task-033-24-x.md"
    write(project, rel, "# Task 033-24: x\n\n[a](../TASK.md)\n")
    real_write = os.write
    calls = []

    def short_then_full(fd, data):
        """A short write, then ENOSPC: what a filling disk does to a regular file."""
        calls.append(len(data))
        if len(calls) == 1:
            return real_write(fd, bytes(data[:max(1, len(data) // 2)]))
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(os, "write", short_then_full)
    result = retarget_inbound(str(project), TASK, PLAN)

    assert _reason(result, rel, "REFUSED") == ["partly written: No space left on device"]
    assert result.exit_code == 1


def test_tc31_the_text_output_escapes_and_json_is_ascii(project):
    (project / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (project / "docs" / "x\n[RETARGETED] forged.md").symlink_to(project / TASK)
    write(project, "docs/other.md", "[a](TASK.md#\u202eevil\x1b[2J)\n")

    text = run_cli(project, "--task", TASK, "--dry-run")
    assert text.returncode == 3, text.stderr
    assert not any(line.startswith("[RETARGETED] forged") for line in text.stdout.splitlines())
    assert "\u202e" not in text.stdout and "\x1b" not in text.stdout
    assert "\\u202e" in text.stdout and "\\u001b" in text.stdout
    raw = subprocess.run([sys.executable, str(REBASE), "--inbound", "--task", TASK, "--json",
                          "--dry-run"], cwd=project, capture_output=True, timeout=120).stdout
    assert all(byte < 128 for byte in raw)


def test_tc31_a_record_the_stream_cannot_encode_prints_escaped(monkeypatch, capsys):
    record = slot_links.InboundRecord("bad\udcff.md", None, "SKIPPED", "", "", "symbolic link")
    monkeypatch.setattr(slot_links, "retarget_inbound",
                        lambda *args: slot_links.InboundResult([record], 0, "walk", None, 3))
    assert slot_links.main(["--task", TASK]) == 3
    assert "bad\\udcff.md" in capsys.readouterr().out


def test_tc32_an_unexpected_error_exits_1(monkeypatch, capsys):
    def boom(*args):
        raise RuntimeError("boom")

    monkeypatch.setattr(slot_links, "retarget_inbound", boom)
    assert slot_links.main(["--task", TASK]) == 1
    report = json.loads(capsys.readouterr().err)
    assert report["ok"] is False and "RuntimeError: boom" in report["error"]


def test_tc33_no_protocol_and_a_foreign_worktree(project, tmp_path):
    assert slot_links._git_env()["GIT_ALLOW_PROTOCOL"] == "none"
    init_repo(project)
    commit(project)
    other = Path(os.path.realpath(tmp_path)) / "other"
    other.mkdir()
    git(project, "config", "core.worktree", str(other))
    with pytest.raises(InboundError):
        retarget_inbound(str(project), TASK, PLAN)


def test_tc34_size_and_line_bounds(project):
    big = project / "docs" / "big.md"
    big.write_bytes(b"[a](TASK.md)\n" + b"x" * (4 << 20))
    result = retarget_inbound(str(project), TASK, PLAN)
    assert _reason(result, "docs/big.md", "UNREADABLE") == ["larger than 4194304 bytes"]
    big.unlink()

    long = write(project, "docs/long.md", "line\n" * 20001)
    init_repo(project)
    base = commit(project)
    long.write_text("line\n" * 20001 + "[a](TASK.md)\n")
    write(project, "docs/new-long.md", "line\n" * 20001 + "[a](TASK.md)\n")   # untracked
    result = retarget_inbound(str(project), TASK, PLAN, since=base)
    assert _reason(result, "docs/long.md", "INBOUND") == ["not attributed: more than 20000 lines"]
    assert _reason(result, "docs/new-long.md", "INBOUND") == [
        "not attributed: more than 20000 lines"]


def test_tc35_a_ledger_directory_in_another_case_is_never_rewritten(project):
    init_repo(project)
    base = commit(project)
    record = write(project, "docs/Backlog/wi-1-x.md", "Body [task](../TASK.md).\n")
    result = retarget_inbound(str(project), TASK, PLAN, since=base)
    assert records(result) == [("docs/Backlog/wi-1-x.md", 1, "INBOUND")]
    assert record.read_text() == "Body [task](../TASK.md).\n"


def test_tc36_an_ignored_subtask_is_still_read(project):
    write(project, ".gitignore", "docs/tasks/\n")
    init_repo(project)
    commit(project)
    sub = write(project, "docs/tasks/task-033-25-x.md", "# Task 033-25: x\n\n[a](../TASK.md)\n")
    result = retarget_inbound(str(project), TASK, PLAN)
    assert records(result) == [("docs/tasks/task-033-25-x.md", 3, "RETARGETED")]
    assert "[a](task-033-admission-core-v1.md)" in sub.read_text()


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any directory")
def test_tc37_an_unreadable_directory_is_listed(project):
    secret = project / "docs" / "secret"
    secret.mkdir()
    secret.chmod(0)
    try:
        result = retarget_inbound(str(project), TASK, PLAN)
    finally:
        secret.chmod(0o755)
    assert [r.file for r in result.records if r.action == "UNREADABLE"] == ["docs/secret"]


def test_tc38_an_abbreviated_option_exits_2(project):
    result = run_cli(project, "--ta", TASK)
    assert result.returncode == 2
    assert json.loads(result.stderr)["ok"] is False


@pytest.mark.parametrize("before, after", [
    ("[<../TASK.md>](<../TASK.md>)", "[task-033](<task-033-admission-core-v1.md>)"),
    ("\\[docs/TASK.md](../TASK.md)", "\\[docs/TASK.md](task-033-admission-core-v1.md)"),
])
def test_tc39_link_text_forms(project, before, after):
    sub = write(project, "docs/tasks/task-033-26-x.md", f"# Task 033-26: x\n\n{before}\n")
    retarget_inbound(str(project), TASK, PLAN)
    assert sub.read_text() == f"# Task 033-26: x\n\n{after}\n"


@pytest.mark.parametrize("text, close, expected", [
    ("x [a](y)", 4, (2, 4)),
    ("[a [b] c](y)", 8, (0, 8)),
    ("\\[a](y)", 3, None),
    ("[a\n\nb](y)", 5, None),
])
def test_tc39_text_span(text, close, expected):
    assert text[close] == "]"
    assert slot_links._text_span(text, close) == expected


def test_tc40_an_lf_blob_checked_out_as_crlf(project):
    design = write(project, "docs/design/core.md", "Old [s](../TASK.md).\n")
    init_repo(project)
    base = commit(project)
    design.write_bytes(b"Old [s](../TASK.md).\r\nNew [s](../TASK.md).\r\n")
    result = retarget_inbound(str(project), TASK, PLAN, since=base)
    assert records(result) == [("docs/design/core.md", 1, "INBOUND"),
                               ("docs/design/core.md", 2, "RETARGETED")]


def test_tc41_a_leading_dash_is_named(project):
    init_repo(project)
    commit(project)
    result = run_cli(project, "--task", TASK, "--since=-x")
    assert result.returncode == 2
    assert "must not start with '-'" in json.loads(result.stderr)["error"]


# --- stage-2 round 2 ---------------------------------------------------------------------------

def test_tc42_autojunk_stays_off(project):
    """TC-42. With `autojunk=True`, popular rows become junk and old links read as added."""
    base_rows = []
    for i in range(120):
        base_rows += ["| see | [s](../TASK.md) |", f"| row {i} | old |"]
    design = write(project, "docs/design/table.md", "\n".join(base_rows) + "\n")
    init_repo(project)
    base = commit(project)
    work_rows = []
    for i in range(120):
        work_rows += ["| see | [s](../TASK.md) |", f"| row {i} | new |"]
    design.write_text("\n".join(work_rows + ["| added | [s](../TASK.md) |"]) + "\n")
    result = retarget_inbound(str(project), TASK, PLAN, since=base, dry_run=True)
    assert [r.line for r in result.records if r.action == "RETARGETED"] == [241]


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any directory")
def test_tc43_an_unreadable_tasks_directory_is_listed_in_git_mode(project):
    init_repo(project)
    commit(project)
    tasks = project / "docs" / "tasks"
    write(project, "docs/tasks/task-033-27-x.md", "# Task 033-27: x\n\n[a](../TASK.md)\n")
    tasks.chmod(0o300)
    try:
        result = retarget_inbound(str(project), TASK, PLAN)
    finally:
        tasks.chmod(0o755)
    assert [r.file for r in result.records if r.action == "UNREADABLE"] == ["docs/tasks"]
    assert result.exit_code == 3


def test_tc44_a_closed_stdout_exits_1_with_the_error_object(monkeypatch, capsys):
    class Closed:
        encoding = "utf-8"

        def write(self, text):
            raise BrokenPipeError(32, "Broken pipe")

        def flush(self):
            raise BrokenPipeError(32, "Broken pipe")

    monkeypatch.setattr(slot_links, "retarget_inbound",
                        lambda *args: slot_links.InboundResult([], 0, "walk", None, 0))
    monkeypatch.setattr(sys, "stdout", Closed())
    assert slot_links.main(["--task", TASK]) == 1
    assert json.loads(capsys.readouterr().err)["ok"] is False


def test_tc45_the_tasks_listing_reads_regular_files_only(project):
    init_repo(project)
    commit(project)
    (project / "docs" / "tasks" / "task-033-28-dir.md").mkdir()
    os.mkfifo(project / "docs" / "tasks" / "task-033-29-fifo.md")
    result = retarget_inbound(str(project), TASK, PLAN)
    assert result.records == []
    assert result.exit_code == 0


def test_tc46_a_file_without_a_slot_name_is_not_masked(project, monkeypatch):
    write(project, "docs/plain.md", "No slot name here.\n")
    write(project, "docs/named.md", "[a](TASK.md)\n")
    masked = []
    original = slot_links._rl._mask

    def counting(text):
        masked.append(text)
        return original(text)

    monkeypatch.setattr(slot_links._rl, "_mask", counting)
    retarget_inbound(str(project), TASK, PLAN)
    assert "No slot name here.\n" not in masked
    assert "[a](TASK.md)\n" in masked

