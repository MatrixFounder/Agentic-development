"""Git-rollback contract test (TASK 107, WI-20).

``/framework-upgrade`` used to keep two rollback mechanisms: git, which holds every path an
upgrade edits, and copies under ``.agent/archive/<name>.bak``. Measured before this task: 60
copies, each one's content already among git's objects, named by basename so that two skills'
``SKILL.md`` could collide, and carrying text the tree had since changed.

The workflow now takes its rollback point from git alone. This file pins that in four places:

* §0 takes the rollback point before any edit; §2.2 and §3.1 declare and check every path; §5
  lists every change, stops on an undeclared one, records and confirms the list, and only then
  removes and restores; it ends on a status check (``TC-01``);
* no scanned instruction file names a copy outside version control (``TC-02``);
* the verificator's plan audit asks for the base commit, not for a copy (``TC-03``);
* the workflow names a command that acts on unnamed paths only in a sentence forbidding it
  (``TC-04``).

Text is compared with whitespace collapsed, so a reflow passes. Renaming a section number, a
check number or a step label fails by design: other documents cite them.

``TC-02`` is a tripwire for the known spellings of a copy, not a parser of intent: a copy described
in other words passes it.
"""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

WORKFLOW = PROJECT_ROOT / ".agent" / "workflows" / "framework-upgrade.md"
VERIFICATOR = PROJECT_ROOT / ".agent" / "skills" / "skill-self-improvement-verificator" / "SKILL.md"

#: §0 — the commands that take the rollback point.
SECTION_0_REQUIRED = (
    "git rev-parse --show-toplevel",
    "git ls-files --error-unmatch -- .agent/workflows/framework-upgrade.md",
    "git rev-parse HEAD",
    "update_state.py",
    "--add_decision",
)
#: §0 — the clean-tree check and its stop, in ONE list item.
SECTION_0_CLEAN = ("git status --porcelain --untracked-files=all", "**STOP**")
#: §2 — the planner declares every path, by full repo-relative path.
SECTION_2_REQUIRED = ("full repo-relative path of every file the run edits and every file it creates",)
#: §3.1 — the declared-path checks.
SECTION_3_1_REQUIRED = (
    "git rev-parse HEAD",
    "git ls-files --error-unmatch",
    "git check-ignore -q",
    "matches `[A-Za-z0-9._/-]+`, has no `.git` or `..` segment",
    "never uses `git add -f`",
)
#: §4.5 — the repairs the fallback treats as declared.
SECTION_4_5_REQUIRED = ("The audit lists every file a `--fix` repair touched",)
#: §5 — every control the fallback rests on.
SECTION_5_REQUIRED = (
    "Only the operator's own message confirms",
    "A subagent never runs §5",
    "top=$(git rev-parse --show-toplevel)",
    "git rev-parse HEAD",
    "git status --porcelain=v1 --untracked-files=all",
    "must be identical to a declared path",
    "a path the PLAN declares",
    "both must be declared",
    "Any other entry means **STOP**",
    "Record the list where the base is recorded",
    "Then list again; a different list means **STOP**",
    'rm -- "${top:?}/<path>"',
    "never `-r`",
    "git restore --source=<base> --staged --worktree -- <path>",
    "prints only the audit",
)
#: §5 — the order: list, confirm, remove, restore, check.
SECTION_5_ORDER = ("**List before restoring.**", "**Confirm.**", "**Remove created files.**",
                   "**Restore by name.**", "**Check.**")

#: Commands that act on paths no step named, and the only sentences allowed to name them.
UNNAMED_PATH_COMMAND = re.compile(
    r"git reset --hard|git clean|git stash|git checkout|git add -f|-delete\b"
    r"|\brm\s+(?:-\w*[rR]\w*|--recursive)\b"
    r"|git restore\b[^`]*?\s(?:--\s+)?(?::/|\.)(?=[\s`]|$)")
ALLOWED_SENTENCES = (
    "Do not use `git reset --hard`, `git clean`, `git checkout` or `git stash` here.",
    "ask the operator to commit, or to run `git stash -u`.",
    "The run never uses `git add -f`.",
)

#: The known spellings of a copy outside version control.
COPY_TOKEN = re.compile(r"(?i)\.(bak|orig|backup|old)\b|\.agent/(archive|backups)\b")

#: Instruction roots. Every root in REQUIRED_ROOTS must exist and hold at least one file; the
#: vendor roots are scanned where the checkout has them. Scripts are out of scope: the installer
#: snapshots a target project under `.agent/backups/`, where git may not exist (TASK 107 §7).
REQUIRED_ROOTS = (".agent/workflows", ".agent/skills", ".agent/rules", "System/Docs",
                  "System/Agents", ".claude/commands", ".claude/agents")
#: Vendor agent definitions are markdown, TOML (Codex) or JSON (Antigravity).
VENDOR_ROOTS = (".gemini/agents", ".codex/agents", ".cursor/agents", ".antigravity/agents")
VENDOR_PATTERNS = ("*.md", "*.toml", "*.json")
BOOTSTRAP_FILES = ("CLAUDE.md", "AGENTS.md", "GEMINI.md")


def _flat(text):
    return " ".join(text.split())


def _workflow():
    """The workflow text with HTML comments removed: a comment is not an instruction."""
    return re.sub(r"<!--.*?-->", "", WORKFLOW.read_text(encoding="utf-8"), flags=re.S)


def _section(text, number):
    """The body of `## <number>` up to the next `## ` heading, or ''."""
    m = re.search(rf"^## {re.escape(str(number))}\.?[ \t][^\n]*\n(.*?)(?=^## |\Z)", text,
                  re.M | re.S)
    return m.group(1) if m else ""


def _items(body):
    """Top-level numbered list items of a section body."""
    return re.split(r"\n(?=\d+\. )", body)


def _missing(required, body):
    flat = _flat(body)
    return [r for r in required if _flat(r) not in flat]


def _is_scanned(path: Path) -> bool:
    """A file an agent reads as an instruction, not a recorded eval output or a build artifact.

    `evals/corpus*/` holds documents agents WROTE during a measurement campaign. They are
    evidence, preserved as produced, not instructions anyone follows. The exclusion keys on the
    `evals` parent, so a skill directory that merely starts with `corpus` is still scanned.
    """
    parts = path.relative_to(PROJECT_ROOT).parts
    if "__pycache__" in parts:
        return False
    return not any(parts[i].startswith("corpus") and parts[i - 1] == "evals"
                   for i in range(1, len(parts)))


def _files_under(root, patterns=("*.md",)):
    base = PROJECT_ROOT / root
    if not base.is_dir():
        return []
    found = sorted({p for pat in patterns for p in base.rglob(pat)})
    return [p for p in found if _is_scanned(p)]


class TestWorkflowCarriesGitRollback(unittest.TestCase):
    """TC-01 — §0 takes the rollback point; §2.2, §3.1 and §4.5 declare; §5 lists first."""

    def test_section_0_precedes_section_1(self):
        text = _workflow()
        s0, s1 = text.find("\n## 0."), text.find("\n## 1.")
        self.assertNotEqual(s0, -1, "the workflow has no §0")
        self.assertLess(s0, s1, "§0 must come before §1, which already edits the tree")

    def test_section_0_commands(self):
        body = _section(_workflow(), "0")
        self.assertEqual(_missing(SECTION_0_REQUIRED, body), [], "§0 lacks a command")
        clean = [i for i in _items(body) if _flat(SECTION_0_CLEAN[0]) in _flat(i)]
        self.assertTrue(clean and SECTION_0_CLEAN[1] in clean[0],
                        "§0's clean-tree item must carry its own **STOP**")

    def test_declaration_sections(self):
        text = _workflow()
        self.assertEqual(_missing(SECTION_2_REQUIRED, _section(text, "2")), [], "§2.2")
        rollback = next((i for i in _items(_section(text, "3")) if "**Base check**" in i), "")
        self.assertEqual(_missing(SECTION_3_1_REQUIRED, rollback), [], "§3.1")
        self.assertEqual(_missing(SECTION_4_5_REQUIRED, _section(text, "4.5")), [], "§4.5")

    def test_section_5_controls_and_order(self):
        body = _section(_workflow(), "5")
        self.assertEqual(_missing(SECTION_5_REQUIRED, body), [], "§5 lacks a control")
        flat = _flat(body)
        positions = [flat.find(m) for m in SECTION_5_ORDER]
        self.assertNotIn(-1, positions, f"§5 lacks a step of {SECTION_5_ORDER}")
        self.assertEqual(positions, sorted(positions),
                         "§5 must list and confirm before it removes, restore after, check last")


class TestNoCopyInstruction(unittest.TestCase):
    """TC-02 — no scanned instruction file names a copy outside version control."""

    def test_no_copy_token(self):
        hits, empty = [], []
        files = []
        for root in REQUIRED_ROOTS:
            found = _files_under(root, ("*.md", "*.yaml"))
            if not found:
                empty.append(root)
            files.extend(found)
        for root in VENDOR_ROOTS:
            files.extend(_files_under(root, VENDOR_PATTERNS))
        files.extend(PROJECT_ROOT / n for n in BOOTSTRAP_FILES if (PROJECT_ROOT / n).is_file())
        # A root that vanished would otherwise pass on nothing.
        self.assertEqual(empty, [], f"required roots with no instruction file: {empty}")
        for path in files:
            rel = path.relative_to(PROJECT_ROOT)
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError as exc:
                self.fail(f"{rel} is not UTF-8: {exc}")
            hits.extend(f"{rel}:{n}: {line.strip()[:80]}"
                        for n, line in enumerate(lines, 1) if COPY_TOKEN.search(line))
        self.assertEqual(hits, [], "copy outside version control:\n" + "\n".join(hits))


class TestVerificatorAsksForBase(unittest.TestCase):
    """TC-03 — Mode B check 2 asks for the base commit and names no copy."""

    def test_check_two_names_base_commit(self):
        text = VERIFICATOR.read_text(encoding="utf-8")
        mode_b = text.split("### Mode B", 1)
        self.assertEqual(len(mode_b), 2, "the verificator has no Mode B section")
        # The whole list item, continuation lines included, so a reflow does not split it.
        item = re.search(r"^2\. \[ \] \*\*Rollback\*\*.*?(?=^\d+\. \[|^#|\Z)", mode_b[1],
                         re.M | re.S)
        self.assertIsNotNone(item, "Mode B has no check 2 named Rollback")
        flat = _flat(item.group(0))
        self.assertIn("base commit", flat)
        self.assertIsNone(COPY_TOKEN.search(flat), f"check 2 names a copy: {flat}")


class TestNoUnnamedPathCommand(unittest.TestCase):
    """TC-04 — the workflow names such a command only in a sentence that forbids it."""

    def test_only_in_allowed_sentences(self):
        flat = _flat(_workflow())
        for sentence in ALLOWED_SENTENCES:
            self.assertIn(sentence, flat, f"the prohibition is gone: {sentence}")
            flat = flat.replace(sentence, "")
        hits = sorted({m.group(0) for m in UNNAMED_PATH_COMMAND.finditer(flat)})
        self.assertEqual(hits, [], f"named outside a prohibition: {hits}")


if __name__ == "__main__":
    unittest.main()
