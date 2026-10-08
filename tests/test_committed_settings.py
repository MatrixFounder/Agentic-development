"""The committed Claude Code settings hold framework permissions only (TASK 111 R1.12, R2; TASK 112).

`System/scripts/vendors.yaml` copies `.claude/settings.json` into every new consumer project. Before
TASK 111 it held one operator's permissions: home paths, `Bash(python3 -)`, `Bash(git push *)`. This
file pins:

* the allow list equals Appendix A of TASK 112 (``TC-S1``);
* no string under `permissions` names a home or absolute path, and no rule runs arbitrary Python
  or a git subcommand that writes; no command of `WRITING_FORMS` has a wildcard rule, which would
  admit `--output`, `-o` or a write to a ref; each rule's command name is one of a fixed set
  (``TC-S3``, TASK 111 R2.7, TASK 112 TC-S3);
* the repository ignores the operator's local settings file (``TC-S4``);
* the settings hold `env`, `permissions.allow`, `permissions.deny` and the one PostToolUse hook
  of the base, nothing else; the deny list is TASK 116 §10.1 (``TC-S6``);
* every part of every shell block of `skill-archive-task` matches a committed rule; no part runs
  `mv`, `test` or `mkdir`; each archive command calls `archive_move.py` with operands the script
  accepts (``TC-S7``, TASK 111 D13, TASK 112 R6.2); each `--inbound` command is one line, has
  `--inbound` first and names operands the inbound mode accepts (``TC-S7``, ``TC-S7b``,
  ``TC-S7c``, TASK 116 R2.3 to R2.5);
* `skill-safe-commands`, the READMEs' Antigravity lists, `GEMINI.md` and `AGENTS.md` state the
  limit of R2.7 for every vendor; the pattern block, the command table and the fence lists equal
  their reviewed text; table and patterns name the same commands; no pattern admits an option that
  runs a program or writes (``TC-S8``, TASK 112 R3, R6.1);
* the deny rules match `git stash`, `git reset --hard` and `git clean`, alone and in a compound
  command; they match none of six listed commands that the framework's steps run, and no archive
  command (``TC-S9``, TASK 116 R4.4).

A fence is read as CommonMark reads it: three or more backticks or tildes, any info string. A shell
fence is one whose first info word is `bash`, `sh`, `shell`, `zsh` or `console`.
"""
import importlib.util
import json
import re
import shlex
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"
ARCHIVE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-archive-task" / "SKILL.md"
SAFE_SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-safe-commands" / "SKILL.md"

#: TASK 112 Appendix A. A rule joins the committed file only when `skill-safe-commands` lists its
#: command, `framework-gates.yml` runs its script, or a test of `tests/` pins it (TASK 111 R2.1).
#: Each names its command whole: `X` and `X *`, never `X*`, which also matches `X`-prefixed commands
#: such as `git difftool` (TASK 111 R2.6).
FRAMEWORK_ALLOW_RULES = (
    "Bash(ls *)",
    "Bash(cat *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(grep *)",
    "Bash(wc *)",
    "Bash(stat *)",
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
    "Bash(mkdir -p docs/tasks)",
    "Bash(mkdir -p docs/plans)",
    "Bash(mkdir -p docs/architectures)",
    "Bash(python -m pytest)",
    "Bash(python3 -m pytest)",
    "Bash(npm test)",
    "Bash(cargo test)",
    "Bash(python3 .agent/tools/archive_move.py *)",
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
#: TASK 112 TC-S3: the command name of every allow rule. An interpreter or a runner under another
#: name (`python3.14`, `py`, `node`, `bash`, `env`, `uv`) is none of these.
COMMAND_NAMES = frozenset({"ls", "cat", "head", "tail", "grep", "wc", "stat", "du", "df", "echo",
                           "git", "mkdir", "python", "python3", "npm", "cargo"})
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
#: Shell syntax that Claude Code checks apart from the rule: a redirect or a substitution.
SHELL_EXTRAS = re.compile(r"[<>`]|\$\(")
#: A `python` rule runs a bare `-m pytest` or a named script, never `-c` or arbitrary code.
PYTHON_RULE = re.compile(r"Bash\(python3? (-m pytest|[\w./-]+\.py( .*)?)\)")
ARCHIVE_SCRIPT = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
#: The module of `rebase_links.py --inbound`; TC-S7 reads the options of its `main` as text.
SLOT_LINKS = PROJECT_ROOT / ".agent" / "tools" / "slot_links.py"
#: TASK 116 §10.1: Claude Code refuses these three git commands, bare and with arguments.
DENY_RULES = ("Bash(git stash)", "Bash(git stash *)", "Bash(git reset --hard)",
              "Bash(git reset --hard *)", "Bash(git clean)", "Bash(git clean *)")
ARCHIVE_COMMANDS = ("python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/",
                    "python3 .agent/tools/archive_move.py docs/PLAN.md docs/plans/",
                    "python3 .agent/tools/task_id_tool.py", "python3 .agent/tools/rebase_links.py",
                    "python3 .agent/tools/rebase_links.py --inbound")
#: A part of an archive block that moves, guards or creates outside the script (TASK 112 R1.5).
OUTSIDE_THE_SCRIPT = re.compile(r"^(mv|test|mkdir|\[)\s")
#: The info words that make a fence a shell block (TASK 112 R6.1).
SHELL = ("bash", "sh", "shell", "zsh", "console")
#: The first info word of every fence, in order; an added or relabelled fence fails (R6.1).
ARCHIVE_FENCES = ("", "", "bash", "python", "", "bash", "bash", "", "", "", "bash", "bash", "",
                  "bash", "bash", "bash", "bash", "bash", "bash")
SAFE_FENCES = ("", "markdown")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")


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


def _archive_module():
    spec = importlib.util.spec_from_file_location("archive_move_for_tc_s7", ARCHIVE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _approves(rule, command):
    """Claude Code's documented match: the whole command text, `*` standing in for any text.

    One difference: here a ` *` after a space needs an argument, while Claude Code also matches the
    bare command. Each rule is therefore written in both forms (TASK 116 D4).
    """
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    pattern = ".*".join(re.escape(part) for part in m.group(1).split("*"))
    return re.fullmatch(pattern, command, re.S) is not None


def _fences(text):
    """`(first info word, body)` of every fenced block: backticks or tildes, any info string.

    A fence closes at a line of the same character, at least as long, and nothing else. A backtick
    fence whose info string holds a backtick is no fence (CommonMark).
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m or (m.group(1)[0] == "`" and "`" in m.group(2)):
            i += 1
            continue
        mark = m.group(1)
        info = m.group(2).split()
        close = re.compile(rf"[ \t]*{re.escape(mark[0])}{{{len(mark)},}}[ \t]*")
        j = i + 1
        while j < len(lines) and not close.fullmatch(lines[j]):
            j += 1
        yield (info[0] if info else ""), "\n".join(lines[i + 1:j])
        i = j + 1


def _shell_blocks(text):
    """The bodies of the shell fences, indented fences included."""
    for word, body in _fences(text):
        if word in SHELL:
            yield body


def _archive_commands(text=None):
    """Every part of every shell command of `text`, read by `_shell_commands`.

    With no `text`, the text of `skill-archive-task`, as at the base (TASK 116 TC-S7d).
    """
    if text is None:
        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
    for _, line in _shell_commands(text):
        line = re.sub(r'"<[^<>"]+>"', '"sample"', _fill(line))
        for part in re.split(r"&&|\|\||[;|&]", line):
            part = " ".join(part.split())
            if part:
                yield part


def _fill(line):
    """`line` with the placeholders of `skill-archive-task` filled: `PLACEHOLDERS`, then `112`."""
    for key, value in PLACEHOLDERS.items():
        line = line.replace(key, value)
    return re.sub(r"\{[^}]+\}", "112", line)


def _shell_commands(text):
    """`(physical lines, joined text)` of every command of every shell block of `text`.

    A line that ends with `\\` continues on the next one, as the shell reads it. A comment line is
    no command and continues no line.
    """
    for block in _shell_blocks(text):
        lines = block.splitlines()
        i = 0
        while i < len(lines):
            group = [lines[i]]
            comment = lines[i].strip().startswith("#")
            while not comment and group[-1].endswith("\\") and i + 1 < len(lines):
                i += 1
                group.append(lines[i])
            i += 1
            if group[0].strip().startswith("#"):
                continue
            joined = " ".join(line[:-1] if line.endswith("\\") else line for line in group)
            yield group, " ".join(joined.split())


def _wrapped_inbound(text):
    """The `--inbound` commands of `text` that a line continuation wraps (TASK 116 R2.3)."""
    return [joined for group, joined in _shell_commands(text)
            if "rebase_links.py --inbound" in joined
            and any(line.rstrip().endswith("\\") for line in group)]


def _inbound_options():
    """`{option: takes a value}` of the `add_argument` calls of `slot_links.main`, read as text."""
    text = SLOT_LINKS.read_text(encoding="utf-8")
    main = text[text.index("def main("):]
    return {m.group(1): 'action="store_true"' not in m.group(2)
            for m in re.finditer(r'add_argument\("(--[a-z-]+)"(.*)$', main, re.M)}


def _inbound_problems(text, options, pairs):
    """Why an `--inbound` command of `text` would not run as Step 8 means it (TASK 116 R2.4).

    The placeholders are filled as TC-S7 fills them. `--task` names
    `docs/tasks/task-<ID>-<slug>.md`, and `--plan` the plan of the same `<ID>` and `<slug>`, by the
    name patterns of `archive_move.PAIRS`.
    """
    problems = []
    for _, joined in _shell_commands(text):
        if "rebase_links.py" not in joined or "--inbound" not in joined:
            continue
        words = _fill(joined).split()
        args = words[words.index(".agent/tools/rebase_links.py") + 1:]
        if args[:1] != ["--inbound"]:
            problems.append((joined, "--inbound is not the first argument"))
            continue
        seen, problem, i, rest = {}, None, 0, args[1:]
        while i < len(rest) and problem is None:
            name, eq, value = rest[i].partition("=")
            if not name.startswith("--"):
                problem = f"a positional argument {rest[i]!r}"
            elif name not in options:
                problem = f"{name} is not an option of the inbound mode"
            elif options[name] and not eq:
                i += 1
                if i < len(rest) and not rest[i].startswith("--"):
                    seen[name] = rest[i]
                else:
                    problem = f"{name} has no value"
            elif options[name]:
                seen[name] = value
            elif eq:
                problem = f"{name} takes no value"
            else:
                seen[name] = True
            i += 1
        task, plan = seen.get("--task"), seen.get("--plan")
        if problem is None and not (isinstance(task, str) and task.startswith("docs/tasks/")
                                    and pairs["docs/TASK.md"][1].fullmatch(task[11:])):
            problem = "--task is not docs/tasks/task-<ID>-<slug>.md"
        if problem is None and plan is not None and not (
                isinstance(plan, str) and plan.startswith("docs/plans/")
                and pairs["docs/PLAN.md"][1].fullmatch(plan[11:])
                and plan[len("docs/plans/plan-"):] == task[len("docs/tasks/task-"):]):
            problem = "--plan is not the plan of the --task"
        if problem:
            problems.append((joined, problem))
    return problems


def _pattern_block():
    """The lines of the fence of `skill-safe-commands` §Pattern Matching Rules."""
    blocks = [body for _, body in _fences(SAFE_SKILL.read_text(encoding="utf-8"))
              if body.startswith("# Read-only filesystem")]
    assert len(blocks) == 1, f"{len(blocks)} pattern blocks"
    return blocks[0].splitlines()


def _safe_patterns():
    """The regexes of `skill-safe-commands` §Pattern Matching Rules."""
    return [re.compile(ln) for ln in _pattern_block() if ln.strip() and not ln.startswith("#")]


def _table():
    """Every line of the command table under `## Auto-Run Command Categories`."""
    text = SAFE_SKILL.read_text(encoding="utf-8")
    section = text.split("## Auto-Run Command Categories", 1)[1]
    lines = section.lstrip("\n").splitlines()
    table = []
    for line in lines:
        if not line.startswith("|"):
            break
        table.append(line)
    return table


def _table_commands():
    """The code spans of the table's command column, the **Tool calls** row excepted (R3.5)."""
    for row in _table()[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if cells[0] == "**Tool calls**":
            continue
        # A span that starts with `-` names an option the row excludes, such as `--output`.
        yield from (span for span in re.findall(r"`([^`]+)`", cells[1])
                    if not span.startswith("-"))


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

    def test_s3_every_rule_runs_a_known_command(self):
        for rule in _settings()["permissions"]["allow"]:
            with self.subTest(rule=rule):
                m = re.match(r"Bash\(([^\s)]+)", rule)
                self.assertTrue(m, "not a Bash rule")
                self.assertIn(m.group(1), COMMAND_NAMES, "a command outside the fixed set")


class TestHooks(unittest.TestCase):
    """TC-S6: a settings key takes effect in the running session; none joins without review.

    `permissions` holds the allow list and the deny list of TASK 116 §10.1, in that order.
    """

    def test_s6_settings_hold_env_allow_deny_and_the_base_hook_only(self):
        settings = _settings()
        self.assertEqual(sorted(settings), ["env", "hooks", "permissions"])
        self.assertEqual(list(settings["permissions"]), ["allow", "deny"])
        self.assertEqual(tuple(settings["permissions"]["deny"]), DENY_RULES)
        self.assertEqual(settings["env"], ENV)
        self.assertEqual(settings["hooks"], HOOKS)


#: The two `--inbound` commands of `skill-archive-task`, Step 8 and Example Flow item 11.
STEP8 = ("python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/{filename} "
         "--plan docs/plans/{plan_filename} --since {base_revision}")
FLOW = ("python3 .agent/tools/rebase_links.py --inbound "
        "--task docs/tasks/task-{OLD_ID}-{old-slug}.md "
        "--plan docs/plans/plan-{OLD_ID}-{old-slug}.md --since {old-base}")


class TestArchiving(unittest.TestCase):
    """TC-S7: archiving stays automatic (TASK 111 D13); TC-S7b to TC-S7d (TASK 116 R2.5)."""

    def test_s7_archive_commands_match_a_committed_rule(self):
        allow = _settings()["permissions"]["allow"]
        commands = list(_archive_commands())
        module = _archive_module()
        for prefix in ARCHIVE_COMMANDS:
            with self.subTest(expected=prefix):
                self.assertTrue(any(c.startswith(prefix) for c in commands),
                                f"no archive command starts with {prefix!r}")
        for command in commands:
            with self.subTest(command=command):
                self.assertNotRegex(command, SHELL_EXTRAS, "a redirect or a substitution")
                self.assertNotRegex(command, OUTSIDE_THE_SCRIPT, "a move or a guard outside the script")
                self.assertTrue(any(_approves(rule, command) for rule in allow),
                                "no committed rule approves this archive command")
                if command.startswith("python3 .agent/tools/archive_move.py "):
                    operands = command.split()[2:]
                    self.assertEqual(len(operands), 2)
                    module._parse(*operands)  # raises Refused on an operand the script refuses

    def test_s7_inbound_commands_are_one_line_with_known_operands(self):
        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
        self.assertEqual(len([j for _, j in _shell_commands(text) if "--inbound" in j]), 2)
        self.assertEqual(_wrapped_inbound(text), [])
        self.assertEqual(_inbound_problems(text, _inbound_options(), _archive_module().PAIRS), [])

    def test_s7b_a_wrapped_inbound_command_is_found(self):
        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
        self.assertIn(STEP8, text)
        for wrapped in (STEP8.replace(" --plan", " \\\n  --plan"),
                        STEP8.replace(" --inbound", " \\\n  --inbound")):
            with self.subTest(wrapped=wrapped):
                self.assertTrue(_wrapped_inbound(text.replace(STEP8, wrapped, 1)))

    def test_s7d_a_comment_continues_no_line(self):
        # bash, sh and zsh run the line after a comment that ends with a backslash.
        text = "```bash\n# a note \\\nmv a b\n```\n"
        self.assertEqual([joined for _, joined in _shell_commands(text)], ["mv a b"])
        self.assertIn("mv a b", list(_archive_commands(text)))

    def test_s7c_an_inbound_command_with_wrong_operands_is_found(self):
        text = ARCHIVE_SKILL.read_text(encoding="utf-8")
        options, pairs = _inbound_options(), _archive_module().PAIRS
        self.assertIn(STEP8, text)
        self.assertIn(FLOW, text)
        plan = "--plan is not the plan of the --task"
        task = "--task is not docs/tasks/task-<ID>-<slug>.md"
        plantings = (
            # one planting per sub-check of `--task` and `--plan`: a directory of the right
            # length, and a name in the right directory
            (STEP8, STEP8.replace("docs/tasks/{filename}", "docs/taskz/{filename}"), task),
            (STEP8, STEP8.replace("docs/tasks/{filename}", "docs/tasks/ksat-112-sample.md"), task),
            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/planz/{plan_filename}"), plan),
            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/plans/nalp-112-sample.md"),
             plan),
            (STEP8, STEP8.replace("--since", "--base"),
             "--base is not an option of the inbound mode"),
            (STEP8, STEP8.replace("docs/plans/{plan_filename}", "docs/plan/{plan_filename}"), plan),
            (STEP8, STEP8.replace("docs/tasks/{filename}", "{filename}"), task),
            (FLOW, FLOW.replace("--inbound --task docs/tasks/task-{OLD_ID}-{old-slug}.md",
                                "--task docs/tasks/task-{OLD_ID}-{old-slug}.md --inbound"),
             "--inbound is not the first argument"),
            (FLOW, FLOW.replace("plan-{OLD_ID}", "plan-113"), plan),
            (STEP8, STEP8 + " extra", "a positional argument 'extra'"),
            (STEP8, STEP8 + " --dry-run=1", "--dry-run takes no value"),
            (STEP8, STEP8.replace("--since {base_revision}", "--since --dry-run"),
             "--since has no value"),
        )
        for old, new, reason in plantings:
            with self.subTest(planted=new):
                problems = _inbound_problems(text.replace(old, new, 1), options, pairs)
                self.assertEqual([found for _, found in problems], [reason])

    def test_s7_fences_of_the_archive_skill(self):
        words = tuple(word for word, _ in _fences(ARCHIVE_SKILL.read_text(encoding="utf-8")))
        self.assertEqual(words, ARCHIVE_FENCES)

    def test_s7_fence_parser_reads_every_spelling(self):
        text = ("~~~bash\nmv a b\n~~~\n"
                "```sh title=x\nmv c d\n```\n"
                "  ````console\nmv e f\n  ````\n"
                "```text\nmv g h\n```\n")
        self.assertEqual(list(_shell_blocks(text)), ["mv a b", "mv c d", "mv e f"])


class TestEveryVendor(unittest.TestCase):
    """TC-S8: the limit of R2.7 holds in every vendor's guidance (TASK 111, TASK 112 R3)."""

    maxDiff = None

    ACCEPT = ("git status", "git status -s", "git diff", "git diff HEAD --stat",
              "git log --oneline -5", "git show HEAD", "git branch", "git tag", "git remote",
              "ls -la", "python3 -m pytest", "python -m pytest", "npm test", "cargo test",
              # TASK 112 §4.1
              "ls -L .agent", "rg foo", "rg -L foo", "rg --follow foo",
              "rg --pre-glob '*.gz' foo", "fd -L foo", "fd -e md", "mkdir -p docs/tasks",
              "python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-112-x.md")
    REJECT = ("git diff --output=x", "git log -p --output x", "git show HEAD --output=x",
              "git branch -D x", "git tag v1", "git remote set-url origin x", "tree -o x",
              "find . -name x", "python3 -m pytest -x", "python -m pytest tests", "npm test -- x",
              "npx jest", "cargo test x",
              # TASK 112 §4.1
              "rg --pre cat x", "rg --pre=cat x", "rg -L --pre cat x", "rg foo --pre cat",
              "rg --hostname-bin x y",
              "fd -x rm", "fd -X rm", "fd -Hx rm", "fd -xrm", "fd -L -x rm", "fd -e md -x rm",
              "fd --exec rm", "fd --exec=rm", "fd --exec-batch rm", "fd --exe rm",
              "fd -1x rm", "fd -0X rm", "fd -H1x rm", "rg foo '--pre' cat", "fd foo '-x' rm",
              "fd foo \\\n\\\n-x rm", "rg foo \\\n\\\n--pre cat",
              "git diff HEAD \\\n\\\n--output=x",
              "file x", "file -C",
              "mkdir -p docs/x /tmp/y", "mkdir -p .agent/x", "mkdir -p tests/x",
              "mv docs/TASK.md docs/tasks/x.md",
              "python -c 'x'", "python3 -c 'from scripts.tool_runner import x'",
              "python3 .agent/tools/task_id_tool.py.evil x")
    #: TASK 112 R3.6: one Antigravity list for the skill and both READMEs.
    ANTIGRAVITY_LIST = ("ls,cat,head,tail,grep,wc,stat,du,df,git status,"
                        "python3 .agent/tools/archive_move.py")
    PATTERN_BLOCK = (
        "# Read-only filesystem",
        r"^(ls|cat|head|tail|grep|wc|stat|du|df|echo)(?:\s|$)",
        "",
        "# Symlink-aware listing — framework dirs (.agent/, .agents/, System/, .agentic-development/) may be symlinks",
        r"^ls\s+-[a-zA-Z]*L",
        "",
        "# rg and fd, except the options that run a program; -L and --follow follow symlinks",
        r"^rg(?![\s\S]*\s--(?:pre|hostname-bin)(?:[=\s]|$))(?:\s|$)",
        r"^fd(?![\s\S]*\s(?:-[^-\s]*[xX]|--exe))(?:\s|$)",
        "",
        "# Git read operations (the boundary keeps `git difftool -x <program>` out; `--output` writes a file)",
        r"^git\s+(status|log|diff|show)(?![\s\S]*\s--output)(\s|$)",
        r"^git\s+(branch|remote|tag)$",
        "",
        "# Archiving: the script refuses every operand but the two archive pairs",
        r"^python3\s+\.agent/tools/archive_move\.py(\s|$)",
        "",
        "# Directory creation (three fixed directories)",
        r"^mkdir\s+-p\s+docs/(tasks|plans|architectures)$",
        "",
        "# Python testing (bare forms only)",
        r"^(python|python3)\s+-m\s+pytest$",
        "",
        "# Node and Rust testing (bare forms only)",
        r"^npm\s+test$",
        r"^cargo\s+test$",
        "",
        "# Framework scripts (each pattern ends at the script's name)",
        r"^python3\s+\.agent/skills/skill-session-state/scripts/update_state\.py(\s|$)",
        r"^python3\s+\.agent/tools/task_id_tool\.py(\s|$)",
        r"^python3\s+\.agent/tools/rebase_links\.py(\s|$)",
        r"^python3\s+\.agent/skills/skill-creator/scripts/(validate_skill|init_skill)\.py(\s|$)",
        r"^python3\s+\.agent/skills/artifact-formalizer/scripts/(scan_register|selftest_scan)\.py(\s|$)",
        r"^python3\s+\.agent/skills/artifact-formalizer/evals/(selftest_evals|grade_run)\.py(\s|$)",
        r"^python3\s+System/scripts/doctor\.py(\s|$)",
    )
    #: The command table, every line: the patterns decide, and the table names the same commands.
    TABLE = (
        '| Category | Commands | Reason |',
        '|----------|----------|--------|',
        '| **Read-only** | `ls`, `cat`, `head`, `tail`, `grep`, `rg`, `fd`, `wc`, `echo` | Do not modify state; `rg` and `fd` without the options that run a program |',
        '| **Symlink-aware** | `ls -L`, `rg --follow` / `rg -L`, `fd -L` | Read-only, but follow symlinks into framework dirs (`.agent/`, `.agents/`, `.cursor/skills/`, `System/`, `.agentic-development/`). Plain `find`/`ls`/`rg` do **not** descend into symlinked directories |',
        '| **File info** | `stat`, `du`, `df` | Informational only |',
        '| **Git read** | `git status`; `git log`, `git diff`, `git show` without `--output`; `git branch`, `git remote`, `git tag` with no argument | Read-only git operations |',
        '| **Archiving** | `python3 .agent/tools/archive_move.py` | Moves `docs/TASK.md` and `docs/PLAN.md` into `docs/tasks/` and `docs/plans/`; refuses every other operand (TASK 112) |',
        '| **Directory** | `mkdir -p docs/tasks`, `mkdir -p docs/plans`, `mkdir -p docs/architectures` | Idempotent; three fixed directories |',
        '| **Tool calls** | `generate_task_archive_filename`, `list_directory`, `read_file` | Native tools |',
        '| **Framework scripts** | `python3 .agent/skills/skill-session-state/scripts/update_state.py`, `python3 .agent/tools/task_id_tool.py`, `python3 .agent/tools/rebase_links.py`, `python3 .agent/skills/skill-creator/scripts/validate_skill.py`, `python3 .agent/skills/skill-creator/scripts/init_skill.py`, `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py`, `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py`, `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py`, `python3 .agent/skills/artifact-formalizer/evals/grade_run.py`, `python3 System/scripts/doctor.py` | Framework automation; `rebase_links.py` writes markdown in the working directory by real path, `init_skill.py` by path |',
        '| **Testing** | `python -m pytest`, `python3 -m pytest`, `npm test`, `cargo test`, with no argument | Their options can run a program, delete a directory or overwrite a file (TASK 111 D14) |',
    )

    def test_s8_patterns_accept_read_forms_and_reject_writing_forms(self):
        # A pattern applies after the shell removes quotes (skill §Pattern Matching Rules).
        patterns = _safe_patterns()
        for command in self.ACCEPT:
            with self.subTest(accept=command):
                text = " ".join(shlex.split(command))
                self.assertTrue(any(p.search(text) for p in patterns))
        for command in self.REJECT:
            with self.subTest(reject=command):
                text = " ".join(shlex.split(command))
                self.assertFalse(any(p.search(text) for p in patterns))

    def test_s8_pattern_block_is_the_reviewed_block(self):
        self.assertEqual(tuple(_pattern_block()), self.PATTERN_BLOCK)

    def test_s8_fences_of_the_safe_skill(self):
        words = tuple(word for word, _ in _fences(SAFE_SKILL.read_text(encoding="utf-8")))
        self.assertEqual(words, SAFE_FENCES)

    def test_s8_table_is_the_reviewed_table(self):
        self.assertEqual(tuple(_table()), self.TABLE)

    def test_s8_table_and_patterns_name_the_same_commands(self):
        patterns = _safe_patterns()
        commands = list(_table_commands())
        for command in commands:
            with self.subTest(table=command):
                self.assertTrue(any(p.search(command) for p in patterns), "no pattern matches it")
        for pattern in patterns:
            with self.subTest(pattern=pattern.pattern):
                self.assertTrue(any(pattern.search(c) for c in commands), "no table command")

    def test_s8_prefix_lists_name_no_writing_form(self):
        # The whole list: the skill's in backticks, each README's on a line of its own.
        lists = {"skill": (SAFE_SKILL, rf"`{re.escape(self.ANTIGRAVITY_LIST)}`")}
        for rel in ("README.md", "README.ru.md"):
            lists[rel] = (PROJECT_ROOT / rel,
                          rf"(?m)^[ \t]*{re.escape(self.ANTIGRAVITY_LIST)}[ \t]*$")
        for name, (path, whole) in lists.items():
            with self.subTest(file=name):
                self.assertRegex(path.read_text(encoding="utf-8"), whole)
        for entry in self.ANTIGRAVITY_LIST.split(","):
            with self.subTest(entry=entry):
                self.assertFalse(any(entry == c or entry.startswith(c + " ")
                                     for c in WRITING_FORMS + ("find", "tree", "rg", "fd",
                                                               "file", "mkdir", "mv")), entry)

    def test_s8_skill_states_the_rules(self):
        text = _flat(SAFE_SKILL.read_text(encoding="utf-8"))
        for sentence in (
            "`--output` makes `git log`, `git diff` and `git show` write a file.",
            "With an argument, `git branch`, `git tag` and `git remote` create or delete a ref or "
            "change a remote.",
            "The patterns match the bare commands only. `npx jest` is off this list",
            "A pattern applies to each simple command of a compound command, after the shell "
            "removes its quotes.",
            "A simple command with an output redirection to a file other than `/dev/null`, a "
            "command substitution or a process substitution is not safe.",
            "Neither is a command with a line continuation, `$'…'` or `$\"…\"` quoting, a "
            "parameter or brace expansion, or, for `rg`, `fd` and `git`, an unquoted glob: the "
            "shell can turn each into an option the patterns never see.",
            "Claude Code's built-in check approves the read forms of `git` with no rule, and the "
            "committed settings name only the bare forms of these commands (TASK 111 D13).",
            "`file` is off this list: `-C`, and its abbreviation `--co`, write a compiled magic "
            "file (TASK 112 D2).",
            "Check whether the command matches a pattern above. The table names the same "
            "commands; it approves no command that no pattern matches.",
            "An entry cannot exclude an option, so the list names only commands with no option "
            "that writes or runs a program.",
            "Do not shorten an entry to a bare command such as `mv` or `git`: it then admits "
            "every form of that command.",
        ):
            with self.subTest(sentence=sentence):
                self.assertIn(sentence, text)
        self.assertNotIn("stays safe from the project root", text)
        self.assertNotIn("try shortening the allowed rule", text)

    def test_s8_vendor_prompts_follow_the_skill(self):
        for rel in ("GEMINI.md", "AGENTS.md"):
            text = _flat((PROJECT_ROOT / rel).read_text(encoding="utf-8"))
            with self.subTest(file=rel):
                self.assertIn("`find -L` asks for approval, because `find -exec` runs a program", text)
                self.assertIn("the read forms of `git` and bare test runs) are "
                              "`SafeToAutoRun: true`", text)


class TestDenyList(unittest.TestCase):
    """TC-S9: the deny rules refuse three git commands that discard work (TASK 116 R4.4)."""

    DENIED = ("git stash", "git stash -u", "git stash pop", "git stash list",
              "git reset --hard", "git reset --hard HEAD~1", "git clean -fdx",
              "git status && git stash -q")
    NOT_DENIED = ("git restore --source=c8aba597ed06545a8fc0933238aaa4510f059db2 --staged "
                  "--worktree -- docs/TASK.md",
                  "git status", "git diff", "git reset",
                  "git apply -R --whitespace=nowarn docs/reviews/framework-audit-116-stage3.diff",
                  "rm -- docs/reviews/x.md")

    @staticmethod
    def _denied(command):
        """A deny rule matches a part of `command`, split on the operators TC-S7 splits on.

        Claude Code also splits on a newline and looks inside a subshell; no listed command holds
        either.
        """
        deny = _settings()["permissions"].get("deny", [])
        parts = [" ".join(part.split()) for part in re.split(r"&&|\|\||[;|&]", command)]
        return any(_approves(rule, part) for rule in deny for part in parts if part)

    def test_s9_denied_commands_match_a_rule(self):
        for command in self.DENIED:
            with self.subTest(command=command):
                self.assertTrue(self._denied(command))

    def test_s9_other_commands_match_none(self):
        for command in self.NOT_DENIED:
            with self.subTest(command=command):
                self.assertFalse(self._denied(command))

    def test_s9_archive_commands_match_none(self):
        for command in _archive_commands():
            with self.subTest(command=command):
                self.assertFalse(self._denied(command))


class TestGitignore(unittest.TestCase):
    """TC-S4: the operator's local settings never reach a commit."""

    def test_s4_local_settings_ignored(self):
        lines = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".claude/settings.local.json", [ln.strip() for ln in lines])


if __name__ == "__main__":
    unittest.main()
