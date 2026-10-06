"""The committed Claude Code settings hold framework permissions only (TASK 111 R1.12, R2).

`System/scripts/vendors.yaml` copies `.claude/settings.json` into every new consumer project. Before
TASK 111 it held one operator's permissions: home paths, `Bash(python3 -)`, `Bash(git push *)`. This
file pins:

* the allow list equals Appendix A of TASK 111 (``TC-S1``);
* no string under `permissions` names a home or absolute path, and no rule runs arbitrary Python
  or a git subcommand that writes; no command of `WRITING_FORMS` has a wildcard rule, which would
  admit `--output`, `-o` or a write to a ref (``TC-S3``, TASK 111 R2.7);
* the repository ignores the operator's local settings file (``TC-S4``);
* the settings hold `env`, `permissions.allow` and the one PostToolUse hook of the base, nothing
  else (``TC-S6``);
* every part of every shell block of `skill-archive-task` matches a committed rule, except the
  `test -e` guard that WI-35's archive script absorbs (``TC-S7``, TASK 111 D13);
* `skill-safe-commands`, the READMEs' Antigravity lists, `GEMINI.md` and `AGENTS.md` state the
  limit of R2.7 for every vendor (``TC-S8``).
"""
import json
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"
ARCHIVE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-archive-task" / "SKILL.md"
SAFE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-safe-commands" / "SKILL.md"

#: TASK 111 Appendix A. A rule joins the committed file only when `skill-safe-commands` lists its
#: command, `framework-gates.yml` runs its script, or a test of `tests/` pins it (TASK R2.1). Each
#: names its command whole: `X` and `X *`, never `X*`, which also matches `X`-prefixed commands
#: such as `git difftool` (TASK R2.6).
FRAMEWORK_ALLOW_RULES = (
    "Bash(ls *)",
    "Bash(cat *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(grep *)",
    "Bash(wc *)",
    "Bash(stat *)",
    "Bash(file *)",
    "Bash(du *)",
    "Bash(df *)",
    "Bash(echo *)",
    "Bash(git status)",
    "Bash(git status *)",
    "Bash(git log)",
    "Bash(git diff)",
    "Bash(git show)",
    "Bash(git branch)",
    "Bash(git remote)",
    "Bash(git tag)",
    "Bash(mv docs/TASK.md docs/tasks/*)",
    "Bash(mv docs/PLAN.md docs/plans/*)",
    "Bash(mkdir -p docs/*)",
    "Bash(mkdir -p .agent/*)",
    "Bash(mkdir -p tests/*)",
    "Bash(python -m pytest)",
    "Bash(python3 -m pytest)",
    "Bash(npm test)",
    "Bash(cargo test)",
    "Bash(python3 .agent/skills/skill-session-state/scripts/update_state.py *)",
    "Bash(python3 .agent/tools/task_id_tool.py *)",
    "Bash(python3 .agent/skills/skill-creator/scripts/validate_skill.py *)",
    "Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)",
    "Bash(python3 .agent/tools/rebase_links.py *)",
    "Bash(python3 .agent/skills/artifact-formalizer/scripts/scan_register.py *)",
    "Bash(python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py *)",
    "Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py *)",
    "Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py --check *)",
    "Bash(python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py docs/PLAN.md --check *)",
    "Bash(python3 System/scripts/doctor.py)",
    "Bash(python3 System/scripts/doctor.py *)",
    "Bash(python3 tests/run_tests.py)",
    "Bash(python System/scripts/validate_skills.py --root .)",
    "Bash(python System/scripts/validate_skills.py --root . --quiet)",
    "Bash(python System/scripts/check_prompt_references.py --root .)",
    "Bash(python System/scripts/security_lint.py --root .)",
    "Bash(python System/scripts/smoke_workflows.py --root .)",
)
GIT_WRITES = ("add", "commit", "push", "reset", "restore")
#: TASK 111 R2.7: commands with a form that writes or runs a program. Their bare forms may stay;
#: Claude Code's built-in check approves the read forms of `git` with no rule.
WRITING_FORMS = ("git log", "git diff", "git show", "git branch", "git tag", "git remote", "tree",
                 "python -m pytest", "python3 -m pytest", "npm test", "npx jest", "cargo test")
#: The only `git` rule with a wildcard: `git status` has no form that writes.
GIT_WILDCARDS = ("Bash(git status *)",)
ENV = {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}
#: The base PostToolUse hook, the only one registered (TASK 111 D11 deferred the PreToolUse hook).
HOOKS = {
    "PostToolUse": [
        {"matcher": "Write|Edit",
         "hooks": [{"type": "command", "command": ".claude/hooks/validate_skill_hook.sh"}]},
    ],
}
#: Placeholders of `skill-archive-task`'s shell blocks, filled with a sample archive name; any
#: other `{...}` becomes `112`.
PLACEHOLDERS = {"{filename}": "task-112-sample.md", "{plan_filename}": "plan-112-sample.md"}
#: Step 5's collision guard, whole: no committed rule covers it, and WI-35's archive script
#: absorbs it.
NOT_COMMITTED = re.compile(r"test -e docs/tasks/task-[\w.-]+\.md")
#: Shell syntax that Claude Code checks apart from the rule: a redirect or a substitution.
SHELL_EXTRAS = re.compile(r"[<>`]|\$\(")
#: A `python` rule runs a bare `-m pytest` or a named script, never `-c` or arbitrary code.
PYTHON_RULE = re.compile(r"Bash\(python3? (-m pytest|[\w./-]+\.py( .*)?)\)")
ARCHIVE_COMMANDS = ("mv docs/TASK.md", "mv docs/PLAN.md", "mkdir -p docs/",
                    "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py")


def _settings():
    return json.loads(SETTINGS.read_text(encoding="utf-8"))


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def _approves(rule, command):
    """Claude Code's documented match: the whole command text, `*` standing in for any text."""
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    pattern = ".*".join(re.escape(part) for part in m.group(1).split("*"))
    return re.fullmatch(pattern, command, re.S) is not None


def _shell_blocks(text):
    """The bodies of the `bash`, `sh` and `shell` fences, indented fences included."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^[ \t]*```(\S*)\s*$", lines[i])
        if not m:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() != "```":
            j += 1
        if m.group(1) in ("bash", "sh", "shell", "zsh", "console"):
            yield "\n".join(lines[i + 1:j])
        i = j + 1


def _archive_commands():
    """Every part of every shell block of `skill-archive-task`."""
    for block in _shell_blocks(ARCHIVE_SKILL.read_text(encoding="utf-8")):
        block = block.replace("\\\n", " ")
        for line in block.splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            for key, value in PLACEHOLDERS.items():
                line = line.replace(key, value)
            line = re.sub(r"\{[^}]+\}", "112", line)
            line = re.sub(r'"<[^<>"]+>"', '"sample"', line)
            for part in re.split(r"&&|\|\||[;|&]", line):
                part = " ".join(part.split())
                if part:
                    yield part


def _safe_patterns():
    """The regexes of `skill-safe-commands` §Pattern Matching Rules."""
    text = SAFE_SKILL.read_text(encoding="utf-8")
    block = re.search(r"^```\n(# Read-only filesystem.*?)^```", text, re.M | re.S).group(1)
    return [re.compile(ln) for ln in block.splitlines() if ln.strip() and not ln.startswith("#")]


def _flat(text):
    return " ".join(text.split())


class TestAllowList(unittest.TestCase):
    """TC-S1 (base-fail) and TC-S3."""

    def test_s1_allow_list_is_appendix_a(self):
        allow = _settings()["permissions"]["allow"]
        self.assertEqual(len(allow), len(set(allow)), "duplicate allow rules")
        self.assertEqual(sorted(allow), sorted(FRAMEWORK_ALLOW_RULES))

    def test_s5_every_rule_names_its_command_whole(self):
        for rule in _settings()["permissions"]["allow"]:
            with self.subTest(rule=rule):
                self.assertNotRegex(rule, r"[^\s/]\*\)$", "`X*` also matches `X`-prefixed commands")
                self.assertFalse(rule.startswith("Bash(find"), "`find -exec` runs any command")

    def test_s3_no_home_path_no_arbitrary_python_no_git_write(self):
        permissions = _settings()["permissions"]
        for text in _strings(permissions):
            with self.subTest(rule=text):
                self.assertNotRegex(text, r"(^|[\s(])(/|~)", "absolute or home path")
        for rule in permissions.get("allow", []):
            with self.subTest(rule=rule):
                self.assertNotEqual(rule, "Bash(python3 -)")
                m = re.match(r"Bash\(git (\w+)", rule)
                self.assertFalse(m and m.group(1) in GIT_WRITES, "git subcommand that writes")
                for command in WRITING_FORMS:
                    self.assertFalse(rule.startswith(f"Bash({command} ") and "*" in rule,
                                     "a wildcard admits an option that writes or runs a program")
                if rule.startswith("Bash(git ") and "*" in rule:
                    self.assertIn(rule, GIT_WILDCARDS, "a git wildcard beyond `git status`")
                self.assertFalse(rule.startswith("Bash(npx jest"), "`npx jest` downloads jest")
                if rule.startswith("Bash(python"):
                    self.assertRegex(rule, PYTHON_RULE, "a python rule that runs arbitrary code")


class TestHooks(unittest.TestCase):
    """TC-S6: a settings key takes effect in the running session; none joins without review."""

    def test_s6_settings_hold_env_allow_and_the_base_hook_only(self):
        settings = _settings()
        self.assertEqual(sorted(settings), ["env", "hooks", "permissions"])
        self.assertEqual(list(settings["permissions"]), ["allow"])
        self.assertEqual(settings["env"], ENV)
        self.assertEqual(settings["hooks"], HOOKS)


class TestArchiving(unittest.TestCase):
    """TC-S7: archiving stays automatic (TASK 111 D13)."""

    def test_s7_archive_commands_match_a_committed_rule(self):
        allow = _settings()["permissions"]["allow"]
        commands = list(_archive_commands())
        for prefix in ARCHIVE_COMMANDS:
            with self.subTest(expected=prefix):
                self.assertTrue(any(c.startswith(prefix) for c in commands),
                                f"no archive command starts with {prefix!r}")
        for command in commands:
            with self.subTest(command=command):
                self.assertNotRegex(command, SHELL_EXTRAS, "a redirect or a substitution")
                if NOT_COMMITTED.fullmatch(command):
                    continue
                self.assertTrue(any(_approves(rule, command) for rule in allow),
                                "no committed rule approves this archive command")


class TestEveryVendor(unittest.TestCase):
    """TC-S8: the limit of R2.7 holds in every vendor's guidance."""

    ACCEPT = ("git status", "git status -s", "git diff", "git diff HEAD --stat",
              "git log --oneline -5", "git show HEAD", "git branch", "git tag", "git remote",
              "ls -la", "python3 -m pytest", "python -m pytest", "npm test", "cargo test")
    REJECT = ("git diff --output=x", "git log -p --output x", "git show HEAD --output=x",
              "git branch -D x", "git tag v1", "git remote set-url origin x", "tree -o x",
              "find . -name x", "python3 -m pytest -x", "python -m pytest tests", "npm test -- x",
              "npx jest", "cargo test x")
    SKILL_LIST = ("ls,cat,head,tail,ls -L,grep,rg,rg --follow,fd,fd -L,wc,stat,file,du,df,git status,"
                  "mv docs/TASK.md,mv docs/PLAN.md,mkdir -p docs,mkdir -p .agent,mkdir -p tests")
    README_LIST = ("ls,cat,head,tail,grep,wc,stat,file,du,df,git status,mv docs/TASK.md,"
                   "mv docs/PLAN.md,mkdir -p docs,mkdir -p .agent,mkdir -p tests")

    def test_s8_patterns_accept_read_forms_and_reject_writing_forms(self):
        patterns = _safe_patterns()
        for command in self.ACCEPT:
            with self.subTest(accept=command):
                self.assertTrue(any(p.search(command) for p in patterns))
        for command in self.REJECT:
            with self.subTest(reject=command):
                self.assertFalse(any(p.search(command) for p in patterns))

    def test_s8_prefix_lists_name_no_writing_form(self):
        # The whole list: the skill's in backticks, each README's on a line of its own.
        lists = {"skill": (SAFE_SKILL, self.SKILL_LIST, rf"`{re.escape(self.SKILL_LIST)}`")}
        for rel in ("README.md", "README.ru.md"):
            lists[rel] = (PROJECT_ROOT / rel, self.README_LIST,
                          rf"(?m)^[ \t]*{re.escape(self.README_LIST)}[ \t]*$")
        for name, (path, expected, whole) in lists.items():
            with self.subTest(file=name):
                self.assertRegex(path.read_text(encoding="utf-8"), whole)
                for entry in expected.split(","):
                    self.assertFalse(any(entry == c or entry.startswith(c + " ")
                                         for c in WRITING_FORMS + ("find", "tree")), entry)

    def test_s8_skill_states_the_rules(self):
        text = _flat(SAFE_SKILL.read_text(encoding="utf-8"))
        for sentence in (
            "| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with "
            "no argument |",
            "`--output` makes `git log`, `git diff` and `git show` write a file.",
            "With an argument, `git branch`, `git tag` and `git remote` create or delete a ref or "
            "change a remote.",
            "The patterns match the bare commands only. `npx jest` is off this list",
            "A pattern applies to each simple command of a compound command, after the shell "
            "removes its quotes.",
            "A simple command with an output redirection to a file other than `/dev/null`, a "
            "command substitution or a process substitution is not safe.",
            "Read as prefixes, as Troubleshooting item 2 assumes, the list cannot exclude an option.",
            "Claude Code's built-in check approves the read forms of `git` with no rule, and the "
            "committed settings name only the bare forms of these commands (TASK 111 D13).",
        ):
            with self.subTest(sentence=sentence):
                self.assertIn(sentence, text)
        self.assertNotIn("stays safe from the project root", text)

    #: The command table, row by row: the agent accepts a match on the table or the patterns.
    TABLE = (
        '| **Read-only** | `ls`, `cat`, `head`, `tail`, `grep`, `rg`, `fd`, `wc`, `echo` | Do not modify state |',
        '| **Symlink-aware** | `ls -L`, `rg --follow` / `rg -L`, `fd -L` | Read-only, but follow symlinks into framework dirs (`.agent/`, `.agents/`, `.cursor/skills/`, `System/`, `.agentic-development/`). Plain `find`/`ls`/`rg` do **not** descend into symlinked directories |',
        '| **File info** | `stat`, `file`, `du`, `df` | Informational only |',
        '| **Git read** | `git status`; `git log`, `git diff`, `git show` without `--output`; `git branch`, `git remote`, `git tag` with no argument | Read-only git operations |',
        '| **Archiving** | `mv docs/TASK.md docs/tasks/...`, `mv docs/PLAN.md docs/plans/...` | Documented, non-destructive moves (TASK/PLAN rotate in lockstep) |',
        '| **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures`, `mkdir -p .agent/skills/*` | Idempotent operations |',
        '| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |',
        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 System/scripts/doctor.py` | Framework automation |',
        '| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |',
    )

    def test_s8_table_rows_are_the_reviewed_rows(self):
        rows = [ln for ln in SAFE_SKILL.read_text(encoding="utf-8").splitlines()
                if ln.startswith("| **")]
        self.assertEqual(rows, list(self.TABLE))

    def test_s8_vendor_prompts_follow_the_skill(self):
        for rel in ("GEMINI.md", "AGENTS.md"):
            text = _flat((PROJECT_ROOT / rel).read_text(encoding="utf-8"))
            with self.subTest(file=rel):
                self.assertIn("`find -L` asks for approval, because `find -exec` runs a program", text)
                self.assertIn("the read forms of `git` and bare test runs) are "
                              "`SafeToAutoRun: true`", text)


class TestGitignore(unittest.TestCase):
    """TC-S4: the operator's local settings never reach a commit."""

    def test_s4_local_settings_ignored(self):
        lines = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".claude/settings.local.json", [ln.strip() for ln in lines])


if __name__ == "__main__":
    unittest.main()
