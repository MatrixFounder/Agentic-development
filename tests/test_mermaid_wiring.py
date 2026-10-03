"""Wiring test for `mermaid-authoring-guidelines` (TASK 108, R10, R12.2).

The skill decides whether a figure is drawn and in which form, and how a Mermaid figure is
checked. An agent reaches it only through the surfaces that point at it (TASK 108 R10,
ARCHITECTURE §10.6). A surface that loses its pointer fails silently: the agent draws from
memory, and nothing reports it.

This file pins every R10 surface:

* each surface names the skill, or carries the schedule anchor and the chart markers where those
  are the contract; every surface ARCHITECTURE §10.6 names is pinned here (``TC-01``);
* the replaced text is gone, and its replacement agrees with the rest of the surface: the two
  template placeholders, PlantUML, the MINOR "diagram clarity", the order "Mermaid → ASCII →
  lists" (``TC-02`` to ``TC-04``, ``TC-09``); the template slots state Step 0's first rule and
  hold their block in a skeleton that the figure lint accepts (``TC-02``);
* ``documentation-standards`` registers every anchor a script of the skill reads, the routing
  anchor included, and a consumer the registry names spells its anchor; §5.6 states the ``text
  figure`` fence and the legend condition (R10.2, ``TC-03``);
* review evidence follows D24: lint output is required, render output is optional, and
  ``not rendered: <reason>`` lets a review conclude without a pass (``TC-05``); a figure without
  lint output keeps the review from APPROVED, and ``has_critical_issues`` is true (UC-4 A1); a
  ``%% negative:`` line in a project document fails FIG-25 (``TC-05``); the plan reviewer's
  input data lists the caller-supplied ``plan_gantt.py --check`` and lint output (R10.3,
  ``TC-04``);
* ``.claude/settings.json`` allows the lint and ``plan_gantt.py --check`` and nothing else of the
  skill (D9); the read-only reviewers hold no Bash (R10.6, ``TC-06``);
* the bootstrap files carry the conditional load and one medium rule with the media of R2.3 and
  its UC-3 exception, word for word; a generated plan chart needs no load; the load condition
  sits under TIER 2 of ``skill-phase-context`` (R10.7, D2, ``TC-07``);
* the plan template and ``PLAN_EXAMPLE.md`` hold a valid ``plan-schedule/v1`` block, the example's
  block matches its task records, and ``plan_gantt.py --check`` passes on both (R10.8, R8.5,
  ``TC-08``);
* ``skill-product-solution-blueprint`` keeps its text-only rule (R10.9, ``TC-10``);
* no surface quotes a budget or threshold value of ``assets/notation.json`` (R10.10, ``TC-11``).
  The values are read from that file, so a changed budget changes the check;
* the skill directory holds every component ARCHITECTURE §10.1 lists (``TC-12``);
* the four gate workflows name the figure lint, and the plan workflows ``plan_gantt.py --check``,
  in the evidence the caller runs before a review (R10.5, ``TC-13``);
* CI runs the setup-script listing under a node at or above the floor of the check pair, the
  whole version compared, and no ``permissions`` entry of the workflow or of a job grants write
  (R12.5, A18, ``TC-14``).

Text is compared with whitespace collapsed and case folded, so a reflow passes. A reworded pin
fails by design: change the pin together with the surface.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

SKILL = "mermaid-authoring-guidelines"
SKILL_ROOT = PROJECT_ROOT / ".agent" / "skills" / SKILL
NOTATION = SKILL_ROOT / "assets" / "notation.json"
ARCHITECTURE = "docs/ARCHITECTURE.md"
SCRIPTS = f".agent/skills/{SKILL}/scripts/"

LINT, RENDER, GANTT, SETUP = ("lint_mermaid.py", "render_check.py", "plan_gantt.py",
                              "setup_renderers.sh")
SCHEDULE_ANCHOR = "<!-- contract:schedule -->"
SEQUENCE_ANCHOR = "<!-- contract:sequence -->"
ROUTING_ANCHOR = "<!-- contract:routing -->"
GANTT_START = "<!-- generated:plan-gantt-start -->"
GANTT_END = "<!-- generated:plan-gantt-end -->"
SCHEDULE_SCHEMA = "plan-schedule/v1"
#: D24: a review that holds a figure concludes on these two states; neither is a pass.
NOT_RENDERED = "not rendered: <reason>"
NOT_VERIFIED = "not verified"
#: D2: the load condition, and the clause that keeps the skill out of TIER 1.
LOAD_CONDITION = "before the first figure of any output"
NOT_LOADED = "not loaded for an output with no figure"
#: D2, R10.7: a generated plan chart needs no load.
CHART_CLAUSE = "plan chart that `plan_gantt.py` generates"
#: UC-3 A1: the exception to the medium rule, in the bootstrap files.
MEDIUM_EXCEPTION = ("asks for Mermaid source", "states that this medium does not render it")
#: R2.3: the media that show Mermaid as source, each named by the bootstrap rule.
MEDIA = ("a terminal", "a log", "an MCP response", "a chat without a diagram renderer")
#: R10.5: the caller's evidence before a review names this check.
FIGURE_LINT = "figure lint"

CORE = ".agent/skills/architecture-format-core/SKILL.md"
EXTENDED = ".agent/skills/architecture-format-extended/SKILL.md"
DOC_STANDARDS = ".agent/skills/documentation-standards/SKILL.md"
ARCHITECT_PROMPT = "System/Agents/04_architect_prompt.md"
REVIEWER_PROMPT = "System/Agents/05_architecture_reviewer_prompt.md"
PLANNER_PROMPT = "System/Agents/06_planner_prompt.md"
PLAN_REVIEWER_PROMPT = "System/Agents/07_plan_reviewer_prompt.md"
ARCHITECT_AGENT = ".claude/agents/architect.md"
SETTINGS = ".claude/settings.json"
PHASE_CONTEXT = ".agent/skills/skill-phase-context/SKILL.md"
SKILL_TIERS = "System/Docs/SKILL_TIERS.md"
BOOTSTRAP = ("CLAUDE.md", "AGENTS.md", "GEMINI.md")
BRAINSTORMING = ".agent/skills/brainstorming/SKILL.md"
THREAT_MODEL = ".agent/skills/security-audit/references/checklists/threat_model.md"
REVERSE = ".agent/skills/skill-reverse-engineering/SKILL.md"
PLANNING_FORMAT = ".agent/skills/skill-planning-format/SKILL.md"
PLAN_TEMPLATE = ".agent/skills/skill-planning-format/assets/templates/plan_md_template.md"
PLAN_EXAMPLE = ".agent/skills/skill-planning-format/examples/PLAN_EXAMPLE.md"
BLUEPRINT_DIR = ".agent/skills/skill-product-solution-blueprint"
#: R10.5 — the gate workflows whose caller runs the figure checks before a review; True marks a
#: plan gate, whose caller also runs `plan_gantt.py --check`.
GATE_WORKFLOWS = {
    ".agent/workflows/01-start-feature.md": False,
    ".agent/workflows/vdd-01-start-feature.md": False,
    ".agent/workflows/02-plan-implementation.md": True,
    ".agent/workflows/vdd-02-plan.md": True,
}

#: R10.4 — the four review checklists.
CHECKLISTS = {name: f".agent/skills/{name}/SKILL.md" for name in (
    "architecture-review-checklist",
    "plan-review-checklist",
    "task-review-checklist",
    "code-review-checklist",
)}
#: The reviewers whose wrappers are read-only: they read the evidence the caller supplies.
READ_ONLY_REVIEWERS = (".claude/agents/architecture-reviewer.md",
                       ".claude/agents/plan-reviewer.md",
                       ".claude/agents/task-reviewer.md")

_CHECKLIST_PINS = (SKILL, LINT, RENDER, NOT_RENDERED, NOT_VERIFIED, "caller")
#: TC-01 — every R10 surface and the strings that wire it to the skill.
SURFACES = {
    # R10.1 templates
    CORE: (SKILL,),
    EXTENDED: (SKILL, "erDiagram"),
    # R10.2 parent standard
    DOC_STANDARDS: (SKILL, NOT_RENDERED, NOT_VERIFIED, GANTT, "`contract:routing`"),
    # R10.3 prompts
    ARCHITECT_PROMPT: (SKILL, LOAD_CONDITION, LINT, RENDER, NOT_RENDERED),
    REVIEWER_PROMPT: (SKILL, "caller", NOT_RENDERED, NOT_VERIFIED),
    PLANNER_PROMPT: (SKILL, SCHEDULE_ANCHOR, GANTT, "--write", "8 or more tasks"),
    PLAN_REVIEWER_PROMPT: (GANTT, "--check", FIGURE_LINT, "caller supplies", NOT_RENDERED),
    # R10.4 checklists
    CHECKLISTS["architecture-review-checklist"]: _CHECKLIST_PINS,
    CHECKLISTS["plan-review-checklist"]: _CHECKLIST_PINS + (
        GANTT, "--check", SCHEDULE_ANCHOR, GANTT_START, GANTT_END),
    CHECKLISTS["task-review-checklist"]: _CHECKLIST_PINS,
    CHECKLISTS["code-review-checklist"]: _CHECKLIST_PINS,
    # R10.5 workflows
    **{name: (FIGURE_LINT,) + ((GANTT, "--check") if plan else ())
       for name, plan in GATE_WORKFLOWS.items()},
    # R10.6 permissions
    ARCHITECT_AGENT: (SKILL, LINT, RENDER),
    SETTINGS: (SKILL, LINT, GANTT),
    # R10.7 loading
    PHASE_CONTEXT: (SKILL, LOAD_CONDITION, NOT_LOADED, CHART_CLAUSE),
    SKILL_TIERS: (SKILL, LOAD_CONDITION),
    **{name: (SKILL, LOAD_CONDITION, NOT_LOADED, CHART_CLAUSE, "does not render Mermaid")
          + MEDIUM_EXCEPTION
       for name in BOOTSTRAP},
    # R10.8 other authoring skills
    BRAINSTORMING: (SKILL, "Step 0", "`text figure`"),
    THREAT_MODEL: (SKILL, "flowchart", "the data and its protocol"),
    REVERSE: (SKILL, "Write the text", "from that text"),
    PLANNING_FORMAT: (SKILL, GANTT, SCHEDULE_ANCHOR, SCHEDULE_SCHEMA, GANTT_START, GANTT_END),
    PLAN_TEMPLATE: (SCHEDULE_ANCHOR, SCHEDULE_SCHEMA, GANTT_START, GANTT_END),
    PLAN_EXAMPLE: (SEQUENCE_ANCHOR, SCHEDULE_ANCHOR, SCHEDULE_SCHEMA, GANTT_START, GANTT_END),
}
#: R10.2 — the §4.4 rows of the skill: anchor → (its consumer, relative to the skill's `scripts/`
#: or, with a slash, to the skill; a string the Document cell holds).
REGISTRY_ROWS = {
    "contract:schedule": (GANTT, "docs/PLAN.md"),
    "generated:plan-gantt-start": (GANTT, "docs/PLAN.md"),
    "generated:plan-gantt-end": (GANTT, "docs/PLAN.md"),
    "contract:routing": ("evals/run_evals.py", SKILL),
}
#: Paths relative to the skill that a surface cites without the skill prefix.
RELATIVE_CITES = {
    ARCHITECT_PROMPT: ("scripts/lint_mermaid.py", "scripts/render_check.py"),
    PLANNING_FORMAT: ("references/gantt.md",),
}
#: The placeholders R10.1 replaces.
OLD_PLACEHOLDERS = ("[Mermaid diagram showing connections between components]",
                    "[Mermaid diagram showing components and their interaction]")
#: R10.9 — the product-phase rule that stays.
BLUEPRINT_RULE = "Do NOT use Mermaid graphs for detailed logical flows. Use text lists."
#: R10.8 — an order that puts Mermaid ahead of ASCII.
MERMAID_FIRST = re.compile(r"mermaid\W{1,8}ascii", re.I)
#: The commands of the skill a surface may quote, in backticks.
QUOTED_COMMAND = re.compile(r"`((?:python3|bash) " + re.escape(SCRIPTS) + r"[^`]*)`")
#: Anchors written as HTML comments, as a script source spells them.
ANCHOR_LITERAL = re.compile(r"<!-- ((?:contract|generated|loop|feedback):[a-z0-9<>-]+) -->")

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def _read(rel):
    path = PROJECT_ROOT / rel
    if not path.is_file():
        raise AssertionError(f"{rel}: the file is missing")
    return path.read_text(encoding="utf-8")


def _flat(text):
    return " ".join(text.split()).casefold()


def _missing(needles, text):
    flat = _flat(text)
    return [n for n in needles if _flat(n) not in flat]


def _headings(lines):
    """Yield (index, level, title) of each heading outside a fenced block."""
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            m = HEADING.match(line)
            if m:
                yield i, len(m.group(1)), m.group(2)


def _section(text, title_pattern):
    """The body under the first heading whose title matches, up to the next heading of the same
    or a higher level; None when no heading matches."""
    lines = text.splitlines()
    heads = list(_headings(lines))
    for k, (i, level, title) in enumerate(heads):
        if re.search(title_pattern, title):
            end = next((j for j, lv, _ in heads[k + 1:] if lv <= level), len(lines))
            return "\n".join(lines[i + 1:end])
    return None


def _heading_index(text, title_pattern):
    """(line index, title) of the first heading whose title matches, or (None, None)."""
    for i, _, title in _headings(text.splitlines()):
        if re.search(title_pattern, title):
            return i, title
    return None, None


def _near(text, first, second, span=240):
    """True when `second` follows an occurrence of `first` within `span` characters."""
    flat, a, b = _flat(text), _flat(first), _flat(second)
    return any(b in flat[m.end():m.end() + span] for m in re.finditer(re.escape(a), flat))


def _table_rows(body):
    """The cells of each Markdown table row in `body`, header and delimiter rows excluded."""
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|", line):
            continue
        rows.append([c.strip() for c in re.split(r"(?<!\\)\|", line.strip("|"))])
    return rows[1:] if rows else rows


def _rule_matches(rule, command):
    """True when a `Bash(<pattern>)` permission rule matches `command`; `*` matches any text."""
    m = re.fullmatch(r"Bash\((.*)\)", rule, re.S)
    if not m:
        return False
    pattern = "".join(".*" if ch == "*" else re.escape(ch) for ch in m.group(1))
    return re.fullmatch(pattern, command, re.S) is not None


def _allow_rules():
    data = json.loads(_read(SETTINGS))
    return data.get("permissions", {}).get("allow", [])


class TestSurfacesNameTheSkill(unittest.TestCase):
    """TC-01 — each R10 surface carries its pointer; §10.6 names no surface this file skips."""

    def test_each_surface_holds_its_pins(self):
        problems = []
        for rel, needles in sorted(SURFACES.items()):
            problems.extend(f"{rel}: missing {n!r}" for n in _missing(needles, _read(rel)))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_every_architecture_surface_is_pinned(self):
        body = _section(_read(ARCHITECTURE), r"^10\.6\b")
        self.assertIsNotNone(body, f"{ARCHITECTURE}: no section 10.6")
        names = [tok for row in _table_rows(body) for tok in re.findall(r"`([^`]+)`", row[0])]
        self.assertGreater(len(names), 0, f"{ARCHITECTURE} §10.6: no surface found in the table")
        unpinned = [n for n in names
                    if not any(p.endswith(n) or f"/skills/{n}/" in f"/{p}" for p in SURFACES)]
        self.assertEqual(unpinned, [], f"{ARCHITECTURE} §10.6 names surfaces this test does not "
                                       f"pin: {unpinned}")

    def test_cited_skill_paths_exist(self):
        """A renamed script or reference leaves a surface pointing at nothing."""
        prefix = f".agent/skills/{SKILL}/"
        problems = []
        for rel in sorted(SURFACES):
            text = _read(rel)
            cited = {p.rstrip(".") for p in re.findall(re.escape(prefix) + r"[\w./-]*", text)}
            for relative in RELATIVE_CITES.get(rel, ()):
                if relative not in text:
                    problems.append(f"{rel}: missing {relative!r}")
                cited.add(prefix + relative)
            problems.extend(f"{rel}: cites {p!r}, which does not exist"
                            for p in sorted(cited) if not (PROJECT_ROOT / p).exists())
        self.assertEqual(problems, [], "\n".join(problems))


class TestArchitectureTemplates(unittest.TestCase):
    """TC-02 — R10.1: the placeholders are gone; each figure slot loads the skill."""

    def test_placeholders_are_gone(self):
        text = _read(CORE)
        left = [p for p in OLD_PLACEHOLDERS if p in text]
        self.assertEqual(left, [], f"{CORE}: placeholder still present: {left}")

    def test_extended_skill_is_not_said_to_carry_diagrams(self):
        lines = [f"{CORE}:{n}: {line.strip()}" for n, line in enumerate(_read(CORE).splitlines(), 1)
                 if "architecture-format-extended" in line and "diagram" in line.casefold()]
        self.assertEqual(lines, [], "a line still says the extended skill carries diagrams:\n"
                         + "\n".join(lines))

    def test_figure_slots_load_the_skill_and_hold_the_block(self):
        """The slot states Step 0's first rule, so the skill loads only for a figure, and shows the
        caption, fence and legend inside a ````markdown skeleton: an empty ```mermaid fence is a
        lint error (MA-SYN-07) and an error box on GitHub."""
        text = _read(CORE)
        for title in (r"^2\.2\.", r"^3\.3\."):
            with self.subTest(section=title):
                body = _section(text, title)
                self.assertIsNotNone(body, f"{CORE}: no section {title}")
                self.assertEqual(_missing((SKILL, "Draw a figure only when",
                                           "leave this subsection out"), body), [],
                                 f"{CORE} {title}: missing the skill or Step 0's first rule")
                lines = body.splitlines()
                outer = [i for i, line in enumerate(lines) if line.strip().startswith("````")]
                self.assertEqual([lines[i].strip() for i in outer], ["````markdown", "````"],
                                 f"{CORE} {title}: missing one '````markdown' skeleton")
                skeleton = [line.strip() for line in lines[outer[0] + 1:outer[1]] if line.strip()]
                self.assertTrue(skeleton and skeleton[0].startswith("**Figure"),
                                f"{CORE} {title}: the skeleton does not open with a bold caption")
                self.assertIn("```mermaid", skeleton, f"{CORE} {title}: no fence in the skeleton")
                start = skeleton.index("```mermaid")
                self.assertIn("```", skeleton[start + 1:], f"{CORE} {title}: the fence is not closed")
                end = skeleton.index("```", start + 1)
                self.assertTrue(end + 1 < len(skeleton) and not skeleton[end + 1].startswith("#"),
                                f"{CORE} {title}: missing a legend line directly below the fence")
                outside = [line for i, line in enumerate(lines)
                           if not outer[0] <= i <= outer[1] and line.strip().startswith("```mermaid")]
                self.assertEqual(outside, [], f"{CORE} {title}: a mermaid fence outside the skeleton")

    def test_templates_pass_the_figure_lint(self):
        """A template the architect copies holds no fence the lint rejects."""
        for rel in (CORE, EXTENDED):
            with self.subTest(template=rel):
                run = subprocess.run([sys.executable, str(SKILL_ROOT / "scripts" / LINT),
                                      str(PROJECT_ROOT / rel)],
                                     capture_output=True, text=True, timeout=60)
                self.assertEqual(run.returncode, 0, f"{rel}: the figure lint exits "
                                 f"{run.returncode}:\n{(run.stdout + run.stderr).strip()[:600]}")

    def test_er_diagram_is_mermaid_not_plantuml(self):
        body = _section(_read(EXTENDED), r"^4\.3\.")
        self.assertIsNotNone(body, f"{EXTENDED}: no section 4.3")
        self.assertEqual(_missing((SKILL, "erDiagram"), body), [],
                         f"{EXTENDED} §4.3: missing {SKILL!r} or 'erDiagram'")
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(body.split()))
        prescribing = [s for s in sentences if "plantuml" in s.casefold()
                       and not re.search(r"\b(?:not|never|no)\b", s, re.I)]
        self.assertEqual(prescribing, [], f"{EXTENDED} §4.3 prescribes PlantUML: {prescribing}")


class TestDocumentationStandards(unittest.TestCase):
    """TC-03 — R10.2: §5.6 exists and states the ASCII fence and the legend condition; §4.4
    registers every anchor the skill's scripts read, and each consumer it names reads its anchor."""

    def setUp(self):
        self.text = _read(DOC_STANDARDS)

    def test_section_5_6_points_at_the_skill(self):
        body = _section(self.text, r"^5\.6\.\s+Figures")
        self.assertIsNotNone(body, f"{DOC_STANDARDS}: missing '### 5.6. Figures'")
        self.assertEqual(_missing((SKILL, NOT_RENDERED, NOT_VERIFIED), body), [],
                         f"{DOC_STANDARDS} §5.6: missing the skill or a D24 state")
        self.assertIn("`text figure`", body,
                      f"{DOC_STANDARDS} §5.6: the ASCII rung misses its fence '`text figure`' (R2.5)")

    def test_section_5_6_requires_a_legend_for_two_encodings_only(self):
        """R3.7: a legend sits below the fence when the figure uses two or more encodings."""
        body = _section(self.text, r"^5\.6\.\s+Figures")
        self.assertIsNotNone(body, f"{DOC_STANDARDS}: missing '### 5.6. Figures'")
        self.assertTrue(_near(body, "**Legend**",
                              "required only when the figure uses two or more encodings", span=120),
                        f"{DOC_STANDARDS} §5.6: the Legend item misses 'required only when the "
                        "figure uses two or more encodings'")

    def test_section_5_1_leaves_mermaid_labels_to_5_6(self):
        body = _section(self.text, r"^5\.1\.")
        self.assertIsNotNone(body, f"{DOC_STANDARDS}: no section 5.1")
        self.assertIn("§5.6", body, f"{DOC_STANDARDS} §5.1: missing '§5.6'")

    def _registry(self):
        body = _section(self.text, r"^4\.4\.")
        self.assertIsNotNone(body, f"{DOC_STANDARDS}: no section 4.4")
        return {row[0].strip("`"): row for row in _table_rows(body) if len(row) >= 4}

    def test_registry_holds_the_rows_of_the_skill(self):
        registry = self._registry()
        problems = []
        for anchor, (consumer, document) in sorted(REGISTRY_ROWS.items()):
            row = registry.get(anchor)
            if row is None:
                problems.append(f"{DOC_STANDARDS} §4.4: missing the row '`{anchor}`'")
                continue
            if document not in row[1]:
                problems.append(f"{DOC_STANDARDS} §4.4 `{anchor}`: document is not {document!r}")
            if consumer not in row[3]:
                problems.append(f"{DOC_STANDARDS} §4.4 `{anchor}`: consumer is not {consumer!r}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_each_named_consumer_spells_its_anchor(self):
        """A row whose consumer reads no anchor states a contract nobody keeps. The eval
        executor reads the routing table by its anchor and by column position (R1.4)."""
        problems = []
        for anchor, (consumer, _) in sorted(REGISTRY_ROWS.items()):
            path = SKILL_ROOT / (consumer if "/" in consumer else f"scripts/{consumer}")
            rel = path.relative_to(PROJECT_ROOT)
            if not path.is_file():
                problems.append(f"{rel}: the file is missing; §4.4 names it for '{anchor}'")
            elif f"<!-- {anchor} -->" not in path.read_text(encoding="utf-8"):
                problems.append(f"{rel} does not spell '<!-- {anchor} -->'; §4.4 names it the "
                                "consumer of that anchor")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_routing_anchor_sits_above_the_routing_table(self):
        """R1.4: the document the routing row names holds the anchor once, then the table."""
        lines = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
        at = [i for i, line in enumerate(lines) if line.strip() == ROUTING_ANCHOR]
        self.assertEqual(len(at), 1, f"{SKILL}/SKILL.md: missing one {ROUTING_ANCHOR!r} line")
        rest = [line for line in lines[at[0] + 1:] if line.strip()]
        self.assertTrue(rest and rest[0].lstrip().startswith("|"),
                        f"{SKILL}/SKILL.md: no table directly under {ROUTING_ANCHOR!r}")

    def test_every_anchor_a_script_reads_is_registered(self):
        """`documentation-standards` §4.4: a gate that reads an unregistered anchor is a defect."""
        registry = self._registry()
        read = {}
        sources = [*(SKILL_ROOT / "scripts").glob("*.py"), *(SKILL_ROOT / "evals").glob("*.py")]
        for script in sorted(sources):
            for anchor in ANCHOR_LITERAL.findall(script.read_text(encoding="utf-8")):
                read.setdefault(anchor, script.name)
        self.assertIn("contract:schedule", read,
                      f"no script of {SKILL} spells {SCHEDULE_ANCHOR!r}; the detector reads nothing")
        unregistered = [f"{name} reads '{anchor}'" for anchor, name in sorted(read.items())
                        if anchor not in registry]
        self.assertEqual(unregistered, [], f"{DOC_STANDARDS} §4.4 lacks: {unregistered}")


class TestRolePrompts(unittest.TestCase):
    """TC-04 — R10.3: the architect falls back without the skill; the reviewer rates a figure
    that contradicts its text MAJOR; the planner writes the schedule block; the plan reviewer's
    input data lists the evidence the caller supplies."""

    def test_plan_reviewer_lists_the_caller_evidence(self):
        body = _section(_read(PLAN_REVIEWER_PROMPT), r"^3\.\s+INPUT DATA")
        self.assertIsNotNone(body, f"{PLAN_REVIEWER_PROMPT}: no section '3. INPUT DATA'")
        missing = _missing((f"`{GANTT} docs/PLAN.md --check docs/PLAN.md`", FIGURE_LINT,
                            NOT_RENDERED, "caller supplies"), body)
        self.assertEqual(missing, [], f"{PLAN_REVIEWER_PROMPT} §3: missing {missing}")

    def test_architect_falls_back_when_the_skill_is_absent(self):
        missing = _missing(("is absent", "a list or a table"), _read(ARCHITECT_PROMPT))
        self.assertEqual(missing, [], f"{ARCHITECT_PROMPT}: missing {missing} (UC-1 A3)")

    def _severity(self, text, label):
        lines = [line for line in text.splitlines()
                 if line.lstrip().startswith(f"- **{label}:**")]
        self.assertEqual(len(lines), 1, f"one '- **{label}:**' line expected")
        return lines[0]

    def test_reviewer_rates_a_contradicting_figure_major(self):
        text = _read(REVIEWER_PROMPT)
        major, minor = self._severity(text, "MAJOR"), self._severity(text, "MINOR")
        self.assertIn("a figure that contradicts its text", major,
                      f"{REVIEWER_PROMPT}: MAJOR line misses 'a figure that contradicts its text'")
        for forbidden in ("diagram clarity", "contradict"):
            self.assertNotIn(forbidden, minor.casefold(),
                             f"{REVIEWER_PROMPT}: MINOR line still holds {forbidden!r}")
        self.assertIn("figure", minor, f"{REVIEWER_PROMPT}: MINOR line misses 'figure'")

    def test_planner_adds_no_chart_below_the_task_count(self):
        text = _read(PLANNER_PROMPT)
        self.assertTrue(_near(text, "fewer than 8 tasks", "add no chart", span=16),
                        f"{PLANNER_PROMPT}: missing 'Fewer than 8 tasks: add no chart' (UC-2 A2)")
        self.assertIn(_flat("Never hand-write the gantt"), _flat(text),
                      f"{PLANNER_PROMPT}: missing 'Never hand-write the gantt'")


class TestChecklistsTakeCallerEvidence(unittest.TestCase):
    """TC-05 — R10.4, D24: a Figures section after References; the Script Contract names the
    commands the caller runs; render exit 2 means not rendered."""

    def test_figures_section_follows_references(self):
        problems = []
        for name, rel in sorted(CHECKLISTS.items()):
            text = _read(rel)
            ref_at, ref_title = _heading_index(text, r"^\d+\. References")
            fig_at, fig_title = _heading_index(text, r"^\d+\. Figures")
            if ref_at is None or fig_at is None:
                problems.append(f"{rel}: missing '## N. References' or '## N. Figures'")
                continue
            if fig_at < ref_at or int(fig_title.split(".")[0]) <= int(ref_title.split(".")[0]):
                problems.append(f"{rel}: '## {fig_title}' must follow '## {ref_title}'")
            body = _section(text, r"^\d+\. Figures")
            problems.extend(f"{rel} '## {fig_title}': missing {n!r}"
                            for n in _missing((NOT_RENDERED, NOT_VERIFIED), body))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_script_contract_names_the_figure_commands(self):
        problems = []
        for name, rel in sorted(CHECKLISTS.items()):
            body = _section(_read(rel), r"^Script Contract")
            if body is None:
                problems.append(f"{rel}: missing '## Script Contract'")
                continue
            needles = (LINT, RENDER, "`2` not rendered") + (
                (GANTT, "--check") if name == "plan-review-checklist" else ())
            problems.extend(f"{rel} Script Contract: missing {n!r}"
                            for n in _missing(needles, body))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_architecture_checklist_agrees_with_the_reviewer_prompt(self):
        body = _section(_read(CHECKLISTS["architecture-review-checklist"]),
                        r"^Criticality Protocol")
        self.assertIsNotNone(body, "architecture-review-checklist: no Criticality Protocol")
        self.assertIn("a figure that contradicts its text", _flat(body),
                      f"{CHECKLISTS['architecture-review-checklist']}: MAJOR misses "
                      "'a figure that contradicts its text'")
        self.assertNotIn("diagram clarity", _flat(body))

    #: The MAJOR figure findings of the skill's review checklist §4 that the architecture review
    #: rates the same way as the plan, task and code reviews (STI-24).
    MAJOR_FIGURE_FINDINGS = ("a figure lint `error`", "does not render", "an edge through a node")

    def test_architecture_review_rates_figure_defects_major(self):
        prompt = next(line for line in _read(REVIEWER_PROMPT).splitlines()
                      if line.lstrip().startswith("- **MAJOR:**"))
        protocol = _section(_read(CHECKLISTS["architecture-review-checklist"]),
                            r"^Criticality Protocol") or ""
        major = protocol[protocol.find("**MAJOR:**"):protocol.find("**MINOR:**")]
        problems = [f"{rel}: MAJOR misses {n!r}" for rel, text in
                    ((REVIEWER_PROMPT, prompt), (CHECKLISTS["architecture-review-checklist"], major))
                    for n in _missing(self.MAJOR_FIGURE_FINDINGS, text)]
        self.assertEqual(problems, [], "\n".join(problems))

    #: UC-4 A1: the surfaces on which a figure without lint output keeps the review from APPROVED.
    NOT_VERIFIED_BLOCKS = (REVIEWER_PROMPT, PLAN_REVIEWER_PROMPT) + tuple(
        CHECKLISTS[name] for name in sorted(CHECKLISTS))
    #: The value UC-4 A1 sets, not only the field name: a surface that sets the flag to false
    #: names the field too.
    CRITICAL_FLAG = "`has_critical_issues` is true"
    #: The value no clause may set: a surface with two clauses fails when either one sets it.
    FALSE_FLAG = "`has_critical_issues` is false"

    def _flag_problems(self, rel, text):
        """The flag must follow a *not verified* clause, and no such clause may set it false."""
        problems = []
        if not _near(text, NOT_VERIFIED, self.CRITICAL_FLAG, span=160):
            problems.append(f"{rel}: {self.CRITICAL_FLAG!r} does not follow {NOT_VERIFIED!r}")
        if _near(text, NOT_VERIFIED, self.FALSE_FLAG, span=160):
            problems.append(f"{rel}: {self.FALSE_FLAG!r} follows {NOT_VERIFIED!r}")
        return problems

    def test_a_figure_not_verified_blocks_approval(self):
        problems = [p for rel in self.NOT_VERIFIED_BLOCKS for p in self._flag_problems(rel, _read(rel))]
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_flag_pin_rejects_a_false_flag(self):
        """A surface that names the flag and sets it to false fails the pin, also when another
        of its clauses sets it to true."""
        planted = ("Without it the figure is reported *not verified*: the review then approves "
                   "nothing, and `has_critical_issues` is {}.")
        self.assertTrue(self._flag_problems("planted", planted.format("false")))
        self.assertEqual(self._flag_problems("planted", planted.format("true")), [])
        both = planted.format("true") + "\n\n" + planted.format("false")
        self.assertTrue(self._flag_problems("planted", both))

    def test_the_plan_review_states_its_figure_lint_clause(self):
        """07 Step 1 states the figure clause on its own: a figure without lint output is reported
        *not verified*, and the verdict follows it. The chart clause of the same bullet does not
        satisfy this pin."""
        step1 = _section(_read(PLAN_REVIEWER_PROMPT), r"^Step 1\b")
        self.assertIsNotNone(step1, f"{PLAN_REVIEWER_PROMPT}: no '### Step 1'")
        clause = "A figure without lint output"
        problems = [f"{PLAN_REVIEWER_PROMPT} Step 1: {needle!r} does not follow {clause!r}"
                    for needle, span in ((NOT_VERIFIED, 80), ("does not return APPROVED", 160),
                                         (self.CRITICAL_FLAG, 160))
                    if not _near(step1, clause, needle, span=span)]
        self.assertEqual(problems, [], "\n".join(problems))

    def test_a_negative_marker_in_a_project_document_fails(self):
        """STI-01: a `%% negative:` line counts only in the skill's own files; elsewhere the lint
        reports it as MA-NEG-03, which fails FIG-25."""
        problems = []
        for name in sorted(CHECKLISTS):
            body = _section(_read(CHECKLISTS[name]), r"^\d+\. Figures") or ""
            problems += [f"{CHECKLISTS[name]} Figures: missing {n!r}"
                         for n in _missing(("%% negative:", "FIG-25", "MA-NEG-03"), body)]
        self.assertEqual(problems, [], "\n".join(problems))


class TestPermissions(unittest.TestCase):
    """TC-06 — R10.6, D9: settings allow the lint and `plan_gantt.py --check` only; the quoted
    commands match those rules; the read-only reviewers hold no Bash."""

    FORBIDDEN = (RENDER, SETUP, "--write", "evals/")

    def test_settings_allow_lint_and_check_only(self):
        rules = [r for r in _allow_rules() if SKILL in r]
        problems = [f"{SETTINGS}: allow rule {r!r} names {f!r}"
                    for r in rules for f in self.FORBIDDEN if f in r]
        problems += [f"{SETTINGS}: allow rule {r!r} is neither the lint nor {GANTT} --check"
                     for r in rules if LINT not in r and not (GANTT in r and "--check" in r)]
        problems += [f"{SETTINGS}: allow rule {r!r} has a '*' before its end"
                     for r in rules if "*" in r[:-2] or not r.endswith(" *)")]
        if not any(LINT in r for r in rules):
            problems.append(f"{SETTINGS}: missing an allow rule for {LINT}")
        if not any(GANTT in r and "--check" in r for r in rules):
            problems.append(f"{SETTINGS}: missing an allow rule for {GANTT} --check")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_quoted_commands_match_the_rules(self):
        rules = _allow_rules()
        quoted = {}
        for rel in sorted(SURFACES):
            for command in QUOTED_COMMAND.findall(_read(rel)):
                quoted.setdefault(command, rel)
        # Commands no surface may run without approval, quoted or not.
        for command in (f"python3 {SCRIPTS}{RENDER} docs/ARCHITECTURE.md",
                        f"bash {SCRIPTS}{SETUP}",
                        f"python3 {SCRIPTS}{GANTT} docs/PLAN.md --write docs/PLAN.md",
                        f"python3 .agent/skills/{SKILL}/evals/run_evals.py --arm with_skill"):
            quoted.setdefault(command, "(probe)")
        self.assertTrue(any(LINT in c for c in quoted), f"no surface quotes the {LINT} command")
        problems = []
        for command, rel in sorted(quoted.items()):
            allowed = any(_rule_matches(r, command) for r in rules)
            wanted = LINT in command or (GANTT in command and "--check" in command
                                         and "--write" not in command)
            if wanted and not allowed:
                problems.append(f"{rel}: `{command}` matches no allow rule of {SETTINGS}")
            if allowed and not wanted:
                problems.append(f"{rel}: `{command}` runs without approval; D9 forbids it")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_read_only_reviewers_hold_no_bash(self):
        problems = []
        for rel in READ_ONLY_REVIEWERS:
            tools = re.search(r"^tools:(.*)$", _read(rel), re.M)
            if tools is None or "Bash" in tools.group(1):
                problems.append(f"{rel}: the 'tools:' line must exist and hold no 'Bash'")
        self.assertEqual(problems, [], "\n".join(problems))


class TestLoading(unittest.TestCase):
    """TC-07 — R10.7, D2: the load condition sits next to the skill name; a generated plan chart
    needs no load; the bootstrap files carry one medium rule with its UC-3 exception, word for
    word; the tier table and the skill agree on tier 2."""

    def test_load_condition_names_the_skill(self):
        problems = [f"{rel}: {LOAD_CONDITION!r} does not follow {SKILL!r}"
                    for rel in (ARCHITECT_PROMPT, PHASE_CONTEXT, SKILL_TIERS) + BOOTSTRAP
                    if not _near(_read(rel), SKILL, LOAD_CONDITION)]
        self.assertEqual(problems, [], "\n".join(problems))

    def test_generated_plan_chart_needs_no_load(self):
        problems = []
        if not _near(_read(PHASE_CONTEXT), CHART_CLAUSE, "needs no load", span=24):
            problems.append(f"{PHASE_CONTEXT}: 'needs no load' does not follow {CHART_CLAUSE!r}")
        problems.extend(f"{rel}: {CHART_CLAUSE!r} does not follow {NOT_LOADED!r}"
                        for rel in BOOTSTRAP if not _near(_read(rel), NOT_LOADED, CHART_CLAUSE,
                                                          span=80))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_bootstrap_files_carry_one_medium_rule(self):
        rules = {}
        for rel in BOOTSTRAP:
            lines = [line.strip() for line in _read(rel).splitlines()
                     if line.strip().startswith("- **Figures**:")]
            self.assertEqual(len(lines), 1, f"{rel}: missing one '- **Figures**:' rule")
            rules[rel] = " ".join(lines[0].split())
        self.assertEqual(len(set(rules.values())), 1,
                         "the medium rule differs between the bootstrap files:\n"
                         + "\n".join(f"{k}: {v}" for k, v in rules.items()))
        rule = next(iter(rules.values()))
        self.assertEqual(_missing(("does not render Mermaid", "no Mermaid fence")
                                  + MEDIUM_EXCEPTION + MEDIA, rule), [],
                         f"the medium rule misses its terms, a medium of R2.3 or its UC-3 "
                         f"exception: {rule}")

    def test_the_figure_skill_is_condition_loaded_under_tier_2(self):
        """D2: the skill is TIER 2. Its load condition sits under the TIER 2 heading of
        `skill-phase-context`, not among the phase-entry loads of TIER 1."""
        text = _read(PHASE_CONTEXT)
        tier1 = _section(text, r"^TIER 1\b")
        tier2 = _section(text, r"^TIER 2\b")
        self.assertIsNotNone(tier2, f"{PHASE_CONTEXT}: no TIER 2 section")
        self.assertNotIn(SKILL, tier1 or "", f"{PHASE_CONTEXT}: {SKILL} sits under TIER 1")
        self.assertTrue(_near(tier2, SKILL, LOAD_CONDITION),
                        f"{PHASE_CONTEXT}: TIER 2 misses {SKILL} with {LOAD_CONDITION!r}")

    def test_tier_table_and_skill_agree_on_tier_2(self):
        row = re.search(r"^\|\s*`" + re.escape(SKILL) + r"`\s*\|\s*(\d)\s*\|",
                        _read(SKILL_TIERS), re.M)
        self.assertIsNotNone(row, f"{SKILL_TIERS}: missing the row '| `{SKILL}` | 2 |'")
        front = re.search(r"^tier:\s*(\d)\s*$", (SKILL_ROOT / "SKILL.md").read_text(
            encoding="utf-8"), re.M)
        self.assertIsNotNone(front, f"{SKILL}/SKILL.md: missing 'tier:'")
        self.assertEqual((row.group(1), front.group(1)), ("2", "2"),
                         f"{SKILL_TIERS} and {SKILL}/SKILL.md must both say tier 2 (D2)")


def _id_token(task_id):
    """A pattern that finds `task_id` as a whole token: `1.1` matches neither `11.1` nor `1.10`."""
    return re.compile(r"(?<![\w.])" + re.escape(task_id) + r"(?![\w]|\.\w)")


def _sequence_records(text):
    """[(heading above the record, [lines of the record])] for each top-level list item between
    the sequence anchor and the next `contract:` anchor. Found by position, never by a word."""
    lines = text.splitlines()
    at = [i for i, line in enumerate(lines) if line.strip() == SEQUENCE_ANCHOR]
    if len(at) != 1:
        return None
    end = next((i for i in range(at[0] + 1, len(lines))
                if lines[i].strip().startswith("<!-- contract:")), len(lines))
    records, heading, current = [], "", None
    for line in lines[at[0] + 1:end]:
        if line.startswith("- "):
            current = [line]
            records.append((heading, current))
        elif current is not None and line[:1] in (" ", "\t") and line.strip():
            current.append(line)
        elif line.strip():
            current = None
            if HEADING.match(line):
                heading = line
    return records


class TestPlanTemplate(unittest.TestCase):
    """TC-08 — R10.8, D19, R8.5: the template and the example hold a valid schedule block under
    the anchor, then the marker pair; the example's block matches its task records; and
    `plan_gantt.py --check` passes on both, whose regions are empty below the chart's task count."""

    #: Each plan as a planner holds it: the template's placeholder `{ID}` filled.
    PLANS = {PLAN_TEMPLATE: lambda text: text.replace("{ID}", "108"),
             PLAN_EXAMPLE: lambda text: text}

    def _block(self, rel, text):
        lines = text.splitlines()
        at = [i for i, line in enumerate(lines) if line.strip() == SCHEDULE_ANCHOR]
        self.assertEqual(len(at), 1, f"{rel}: missing one {SCHEDULE_ANCHOR!r}")
        rest = [(i, line) for i, line in enumerate(lines[at[0] + 1:], at[0] + 1) if line.strip()]
        self.assertTrue(rest and rest[0][1].strip() == "```json",
                        f"{rel}: missing a '```json' fence directly under the anchor")
        self.assertEqual(rest[0][0], at[0] + 2,
                         f"{rel}: one blank line separates {SCHEDULE_ANCHOR!r} from its fence")
        start = rest[0][0]
        end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "```"), None)
        self.assertIsNotNone(end, f"{rel}: the schedule fence is not closed")
        return lines, end, "\n".join(lines[start + 1:end])

    def _schedule(self, rel, text):
        """The parsed block, after the checks every plan's block passes."""
        lines, end, raw = self._block(rel, text)
        try:
            block = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.fail(f"{rel}: the schedule block is not JSON: {exc}")
        self.assertEqual(block.get("schema"), SCHEDULE_SCHEMA,
                         f"{rel}: missing '\"schema\": \"{SCHEDULE_SCHEMA}\"'")
        tasks = block.get("tasks")
        self.assertTrue(isinstance(tasks, list) and tasks, f"{rel}: no 'tasks' list")
        for task in tasks:
            self.assertEqual(set(task), {"id", "title", "stage", "est", "deps"},
                             f"{rel}: a task holds keys other than id, title, stage, est, deps "
                             f"(no 'status', D11): {task}")
            self.assertTrue(isinstance(task["est"], int) and not isinstance(task["est"], bool),
                            f"{rel}: 'est' is not an integer: {task}")
            self.assertIsInstance(task["deps"], list, f"{rel}: 'deps' is not a list")
        after = [line.strip() for line in lines[end + 1:]]
        for marker in (GANTT_START, GANTT_END):
            self.assertEqual(after.count(marker), 1,
                             f"{rel}: missing one {marker!r} after the schedule block")
        self.assertLess(after.index(GANTT_START), after.index(GANTT_END),
                        f"{rel}: {GANTT_START!r} must precede {GANTT_END!r}")
        return block

    def _gantt(self, text, *flags):
        """Run the generator on a temporary copy of a plan, with each flag aimed at that copy."""
        script = SKILL_ROOT / "scripts" / GANTT
        self.assertTrue(script.is_file(), f"{SCRIPTS}{GANTT}: the file is missing")
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "PLAN.md"
            plan.write_text(text, encoding="utf-8")
            argv = [sys.executable, str(script), str(plan)]
            for flag in flags:
                argv += [flag, str(plan)]
            return subprocess.run(argv, capture_output=True, text=True, timeout=60)

    def test_schedule_block_is_plan_schedule_v1(self):
        for rel in self.PLANS:
            with self.subTest(plan=rel):
                self._schedule(rel, _read(rel))

    def test_example_block_matches_its_task_records(self):
        """Each record of the sequence has one block entry with its id, title, stage heading and
        dependencies. Ids and titles are compared as data, so the check reads no language."""
        text = _read(PLAN_EXAMPLE)
        tasks = self._schedule(PLAN_EXAMPLE, text)["tasks"]
        records = _sequence_records(text)
        self.assertIsNotNone(records, f"{PLAN_EXAMPLE}: missing one {SEQUENCE_ANCHOR!r}")
        ids = [task["id"] for task in tasks]
        self.assertEqual(len(records), len(ids),
                         f"{PLAN_EXAMPLE}: {len(records)} task records, {len(ids)} block entries")
        by_id = {}
        for heading, lines in records:
            own = [i for i in ids if _id_token(i).search(lines[0])]
            self.assertEqual(len(own), 1, f"{PLAN_EXAMPLE}: a record names {own or 'no'} block "
                                          f"id in its first line: {lines[0].strip()!r}")
            by_id[own[0]] = (heading, lines)
        problems = []
        for task in tasks:
            heading, lines = by_id[task["id"]]
            named = {i for i in ids if i != task["id"]
                     and any(_id_token(i).search(line) for line in lines)}
            if task["title"] not in lines[0]:
                problems.append(f"{task['id']}: title {task['title']!r} is not the record's title")
            if task["stage"] not in heading:
                problems.append(f"{task['id']}: stage {task['stage']!r} is not in the heading "
                                f"above the record, {heading.strip()!r}")
            if named != set(task["deps"]):
                problems.append(f"{task['id']}: deps {sorted(task['deps'])} differ from the ids "
                                f"its record names, {sorted(named)}")
        self.assertEqual(problems, [], f"{PLAN_EXAMPLE}:\n" + "\n".join(problems))

    def test_generator_reads_the_block(self):
        for rel, fill in self.PLANS.items():
            with self.subTest(plan=rel):
                run = self._gantt(fill(_read(rel)))
                self.assertEqual(run.returncode, 0, f"{GANTT} rejects the block of {rel}: "
                                                    f"{(run.stderr or run.stdout).strip()[:400]}")

    def test_check_passes_on_the_empty_region(self):
        """R8.5: a plan below the chart's task count keeps an empty region, and `--check` passes
        on it. Both plans hold too few tasks for a chart."""
        for rel, fill in self.PLANS.items():
            with self.subTest(plan=rel):
                run = self._gantt(fill(_read(rel)), "--check")
                self.assertEqual(run.returncode, 0, f"{GANTT} --check fails on {rel}: "
                                                    f"{(run.stderr or run.stdout).strip()[:400]}")


class TestOtherAuthoringSkills(unittest.TestCase):
    """TC-09 — R10.8: brainstorming orders no form ahead of Step 0."""

    def test_brainstorming_puts_no_mermaid_ahead_of_ascii(self):
        lines = [f"{BRAINSTORMING}:{n}: {line.strip()[:100]}"
                 for n, line in enumerate(_read(BRAINSTORMING).splitlines(), 1)
                 if MERMAID_FIRST.search(line) or "**Primary**: **Mermaid**" in line]
        self.assertEqual(lines, [], "an order with Mermaid ahead of ASCII is left:\n"
                         + "\n".join(lines))


class TestBlueprintKeepsTextOnlyRule(unittest.TestCase):
    """TC-10 — R10.9: the product blueprint is not wired; its text-only rule stays."""

    def test_rule_stays_and_skill_is_not_named(self):
        root = PROJECT_ROOT / BLUEPRINT_DIR
        self.assertIn(_flat(BLUEPRINT_RULE), _flat(_read(f"{BLUEPRINT_DIR}/SKILL.md")),
                      f"{BLUEPRINT_DIR}/SKILL.md: missing {BLUEPRINT_RULE!r}")
        naming = [str(p.relative_to(PROJECT_ROOT)) for p in sorted(root.rglob("*.md"))
                  if SKILL in p.read_text(encoding="utf-8")]
        self.assertEqual(naming, [], f"names {SKILL!r} although R10.9 leaves it unwired: {naming}")


#: Unit word of each `notation.json` key, in match order: the first word found in the key names
#: the unit. A key that matches none fails TC-11, so a new budget gets a unit before it ships.
UNIT_OF_KEY = (
    ("px", r"px|pixels?"),
    ("contrast", r"contrast"),
    ("chars", r"char(?:acter)?s?"),
    ("columns", r"columns?"),
    ("crossings", r"crossings?"),
    ("overlaps", r"overlaps?"),
    ("clipped", r"clipped"),
    ("ratio", r"ratios?"),
    ("edges", r"edges?"),
    ("nodes", r"nodes?"),
    ("participants", r"participants?"),
    ("messages", r"messages?"),
    ("phase_blocks", r"blocks?"),
    ("states", r"states?"),
    ("bars", r"bars?|tasks?"),
    ("entities", r"entit(?:y|ies)"),
    ("elements", r"elements?"),
    ("classes", r"class(?:es)?"),
    ("periods", r"periods?"),
    ("commits", r"commits?"),
    ("tasks", r"tasks?"),
    ("lines", r"lines?"),
)
#: Unit words the surfaces also use for something else: a plan has tasks, a paragraph has lines,
#: a list item has an ordinal. A value next to one counts only when a word naming the figure part
#: it limits stands in the same window. Unit regex → (context regex, the word the probe uses).
UNIT_CONTEXT = {
    r"tasks?": (r"journeys?", "journey"),
    r"lines?": (r"labels?|messages?|notes?", "note"),
}
#: The `notation.json` trees that hold budgets and thresholds (TASK D14, R7.6, R4.4, D25). Its
#: top-level numbers count as well.
VALUE_TREES = ("budgets", "thresholds", "labels", "structure", "ascii")
#: Trees that hold numbers but no budget or threshold, each with its reason. A numeric tree in
#: neither set fails TC-11, so a new tree is classified before the check reads past it.
OTHER_TREES = {
    "renderers": "pinned renderer versions and the render canvas width",
    "lint": "parameters of single lint rules, none of them a D14, R7.6, R4.4 or D25 value",
}
#: A number standing alone: not part of a version, a section sign, an id or a colour.
NUMBER = re.compile(r"(?<![\w.§#])(\d+(?:\.\d+)?)(?![\w]|\.\d)")
TOKEN_SPLIT = re.compile(r"[\s/\-–—]+")
WINDOW = 3


def _is_number(node):
    return isinstance(node, (int, float)) and not isinstance(node, bool)


def _holds_number(node):
    if isinstance(node, dict):
        return any(_holds_number(v) for v in node.values())
    if isinstance(node, list):
        return any(_holds_number(v) for v in node)
    return _is_number(node)


def _notation_units():
    """{unit regex: values} from `notation.json`; raises on an unclassified numeric tree and on
    a key no unit word names."""
    data = json.loads(NOTATION.read_text(encoding="utf-8"))
    unclassified = [k for k, v in data.items() if isinstance(v, (dict, list))
                    and _holds_number(v) and k not in VALUE_TREES and k not in OTHER_TREES]
    if unclassified:
        raise AssertionError(f"{NOTATION.relative_to(PROJECT_ROOT)}: numeric trees {unclassified} "
                             "are in neither VALUE_TREES nor OTHER_TREES of "
                             "tests/test_mermaid_wiring.py")
    leaves = [(k, v) for k, v in data.items() if _is_number(v)]

    def walk(node, key=""):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            leaves.extend((key, v) for v in node if _is_number(v))
        elif _is_number(node):
            leaves.append((key, node))

    for tree in VALUE_TREES:
        walk(data.get(tree, {}))
    units = {}
    for key, value in leaves:
        unit = next((regex for word, regex in UNIT_OF_KEY if word in key), None)
        if unit is None:
            raise AssertionError(f"{NOTATION.relative_to(PROJECT_ROOT)}: key {key!r} has no unit "
                                 "word in UNIT_OF_KEY of tests/test_mermaid_wiring.py")
        units.setdefault(unit, set()).add(float(value))
    return units


def _word(token):
    return token.strip("`*_()[]{}.,;:!?\"'<>|≤≥=~").casefold()


def _restated(text, units):
    """(value, unit token, snippet) for each value of `units` within WINDOW tokens of its unit;
    a unit of UNIT_CONTEXT counts only with its context word in the same window."""
    tokens = [t for t in TOKEN_SPLIT.split(re.sub(r"(\d)(px)\b", r"\1 \2", text)) if t]
    hits = []
    for i, token in enumerate(tokens):
        word = _word(token)
        for unit, values in units.items():
            if not re.fullmatch(unit, word):
                continue
            window = tokens[max(0, i - WINDOW):i] + tokens[i + 1:i + 1 + WINDOW]
            context = UNIT_CONTEXT.get(unit)
            if context and not any(re.fullmatch(context[0], _word(t)) for t in window):
                continue
            snippet = " ".join(tokens[max(0, i - WINDOW):i + 1 + WINDOW])
            for near in window:
                for number in NUMBER.findall(near):
                    hit = (number, word, snippet)
                    if float(number) in values and hit not in hits:
                        hits.append(hit)
    return hits


class TestNoRestatedValue(unittest.TestCase):
    """TC-11 — R10.10, R12.2: a surface points at the skill and quotes none of its budget or
    threshold values. The detector is probed first, so a dead detector fails here."""

    def setUp(self):
        self.units = _notation_units()

    def test_detector_fires_on_every_unit_and_spares_plain_text(self):
        canonical = {regex: word for word, regex in UNIT_OF_KEY}
        dead = []
        for unit, values in self.units.items():
            word = canonical[unit].replace("_", " ")
            context = UNIT_CONTEXT.get(unit)
            tail = f"per {context[1]}" if context else "in one figure"
            for value in values:
                probe = f"at most {value:g} {word} {tail}"
                if not _restated(probe, {unit: values}):
                    dead.append(probe)
        self.assertEqual(dead, [], f"the detector misses: {dead}")
        for clean in ("Hard-wrap prose at 100 characters", "Hard limit: ≤ 120 characters",
                      "With fewer than 8 tasks, add no chart.", "§2.1 nodes and §3.3 edges",
                      "mermaid 10.9.8 and 11.17.2 draw the nodes",
                      "**Figures** in Step 3 states what to run",
                      "3. **Task Files:** (`docs/tasks/*.md`).\n4. **Plan Chart Evidence:**",
                      "`03-develop-single-task`, `04-update-docs`",
                      "(`skill-archive-task` if new task) | ~3,100-4,000",
                      "A list item that grows past ~3 lines becomes its own paragraph."):
            self.assertEqual(_restated(clean, self.units), [], f"false positive on {clean!r}")

    def test_no_surface_quotes_a_value(self):
        problems = []
        for rel in sorted(SURFACES):
            problems.extend(f"{rel}: quotes {value} next to {word!r} in '{snippet}'"
                            for value, word, snippet in _restated(_read(rel), self.units))
        self.assertEqual(problems, [], "point at the skill instead:\n" + "\n".join(problems))


class TestSkillDirectory(unittest.TestCase):
    """TC-12 — the skill directory holds every component ARCHITECTURE §10.1 lists."""

    def test_components_exist(self):
        body = _section(_read(ARCHITECTURE), r"^10\.1\b")
        self.assertIsNotNone(body, f"{ARCHITECTURE}: no section 10.1")
        paths = [m.group(1) for row in _table_rows(body)
                 for m in [re.match(r"`([^`]+)`", row[0])] if m]
        for script in (LINT, RENDER, SETUP, GANTT):
            self.assertIn(f"scripts/{script}", paths,
                          f"{ARCHITECTURE} §10.1: missing the component 'scripts/{script}'")
        tags = json.loads(NOTATION.read_text(encoding="utf-8"))["renderers"]["installs"]
        missing = []
        for path in paths:
            if "<tag>" in path:
                for tag in sorted(tags):
                    folder = SKILL_ROOT / path.replace("<tag>", tag)
                    missing.extend(f"{path.replace('<tag>', tag)}{name}"
                                   for name in ("package.json", "package-lock.json")
                                   if not (folder / name).is_file())
            elif "*" in path:
                if not list(SKILL_ROOT.glob(path)):
                    missing.append(path)
            elif path.endswith("/"):
                if not (SKILL_ROOT / path).is_dir():
                    missing.append(path)
            elif not (SKILL_ROOT / path).is_file():
                missing.append(path)
        self.assertEqual(missing, [], f"{ARCHITECTURE} §10.1 lists components absent from "
                                      f".agent/skills/{SKILL}/: {missing}")


class TestGateWorkflows(unittest.TestCase):
    """TC-13 — R10.5: the evidence the caller runs before a review names the figure lint, and
    `plan_gantt.py --check` for a plan. The caller runs both, because the reviewer holds no
    execution tool; `test_frozen_tree_contract` pins the fingerprint line of the same briefs."""

    #: The parenthetical that lists what the caller runs: "(its `Script Contract` — ...)".
    LIST_START = "its `Script Contract` —"

    def test_evidence_names_the_figure_checks(self):
        problems = []
        for rel, plan in sorted(GATE_WORKFLOWS.items()):
            text = _read(rel)
            if _flat(self.LIST_START) not in _flat(text):
                problems.append(f"{rel}: missing {self.LIST_START!r}")
                continue
            needles = (FIGURE_LINT,) + ((f"`{GANTT} --check`",) if plan else ())
            problems.extend(f"{rel}: the list after {self.LIST_START!r} misses {n!r}"
                            for n in needles if not _near(text, self.LIST_START, n, span=160))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_only_a_plan_gate_runs_the_plan_check(self):
        """`plan_gantt.py --check` reads `docs/PLAN.md`; a TASK or ARCHITECTURE gate has none."""
        named = [rel for rel, plan in sorted(GATE_WORKFLOWS.items())
                 if not plan and GANTT in _read(rel)]
        self.assertEqual(named, [], f"a gate without a plan names {GANTT}: {named}")


#: A list item of a workflow: a step, or an item of another list.
_LIST_ITEM = re.compile(r"(?m)^[ \t]*-[ \t]+\S")
#: A setup-node `node-version` value: a version or its leading numbers, `x` for any number.
_NODE_SPEC = re.compile(r"v?(\d+)(?:\.(\d+|x|\*))?(?:\.(\d+|x|\*))?")
#: A `permissions` key at any level of a workflow, and the value written on its own line.
_PERMISSIONS = re.compile(r"^(?P<indent>[ \t]*)permissions:[ \t]*(?P<value>[^#]*?)[ \t]*(?:#.*)?$")


def _node_versions(workflow):
    """The `node-version` value of each `actions/setup-node` step, as written; None for a step
    without one."""
    starts = [m.start() for m in _LIST_ITEM.finditer(workflow)] + [len(workflow)]
    out = []
    for a, b in zip(starts, starts[1:]):
        step = workflow[a:b]
        if re.search(r"(?m)^[ \t]*(?:-[ \t]+)?uses:[ \t]*[\"']?actions/setup-node@", step):
            m = re.search(r"(?m)^[ \t]*node-version:[ \t]*[\"']?([^\"'\s#]+)", step)
            out.append(m.group(1) if m else None)
    return out


def _node_release(spec):
    """The newest release a `node-version` value admits, as a tuple to compare with a floor:
    `22` and `22.x` admit every 22 release, `22.12` only the 22.12 releases. A number left out,
    or written `x`, compares above every number. None when the value is no version."""
    m = _NODE_SPEC.fullmatch(spec.strip())
    if m is None:
        return None
    return tuple(int(g) if g is not None and g.isdigit() else float("inf") for g in m.groups())


def _floor_release(floor):
    """`>=22.13.0` -> (22, 13, 0); a number left out counts as 0."""
    nums = [int(p) for p in floor.strip().lstrip(">=v").strip().split(".")[:3]]
    return tuple(nums + [0] * (3 - len(nums)))


def _node_problems(workflow, floors):
    """Why the setup-node steps of *workflow* miss a floor of *floors* ({tag: `>=x.y.z`})."""
    versions = _node_versions(workflow)
    if not versions:
        return ["no actions/setup-node step; the dry-run listing test skips under the runner's "
                "own node"]
    problems = []
    for spec in versions:
        release = _node_release(spec) if spec else None
        if release is None:
            problems.append(f"setup-node: node-version {spec!r} is not a version to compare with "
                            "the floor")
            continue
        problems += [f"setup-node: node {spec} is below the {tag} floor {floor}"
                     for tag, floor in sorted(floors.items()) if release < _floor_release(floor)]
    return problems


def _write_grants(workflow):
    """Each line of a `permissions` entry, at the workflow or the job level, that grants write:
    `contents: write`, `write-all`, or a flow mapping that holds `write`."""
    lines = workflow.splitlines()
    grants = []
    for i, line in enumerate(lines):
        m = _PERMISSIONS.match(line)
        if m is None:
            continue
        if m.group("value"):
            if "write" in m.group("value"):
                grants.append(f"line {i + 1}: {line.strip()}")
            continue
        for j in range(i + 1, len(lines)):
            body = lines[j]
            if not body.strip() or body.lstrip().startswith("#"):
                continue
            if len(body) - len(body.lstrip()) <= len(m.group("indent")):
                break
            if re.search(r":[ \t]*[\"']?write\b", body):
                grants.append(f"line {j + 1}: {body.strip()}")
    return grants


class TestContinuousIntegration(unittest.TestCase):
    """TC-14 — R12.5, A18: CI runs the setup-script listing under a node that meets the floor
    of the check pair, compared in full (22.12 is below a 22.13 floor), and no `permissions`
    entry of the workflow or of a job grants write."""

    WORKFLOW = ".github/workflows/framework-gates.yml"

    @staticmethod
    def floors():
        """{tag: `engines.node`} of the check pair's install manifests that name a floor."""
        notation = json.loads(NOTATION.read_text(encoding="utf-8"))
        out = {}
        for tag in notation["renderers"]["check_pair"]:
            manifest = json.loads((SKILL_ROOT / "assets" / "renderers" / tag / "package.json")
                                  .read_text(encoding="utf-8"))
            floor = manifest.get("engines", {}).get("node", "")
            if floor:
                out[tag] = floor
        return out

    def test_node_meets_the_floor_of_the_check_pair(self):
        problems = [f"{self.WORKFLOW}: {p}" for p in _node_problems(_read(self.WORKFLOW),
                                                                    self.floors())]
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_floor_check_reads_the_whole_version(self):
        step = ("jobs:\n  t:\n    steps:\n      - name: Setup Node\n"
                "        uses: actions/setup-node@v4\n        with:\n          cache: npm\n"
                "          node-version: {}\n      - name: Next\n        run: node -v\n")
        floors = {"v11": ">=22.13.0"}
        for spec, meets in (('"22"', True), ("22.x", True), ('"22.13"', True), ("22.13.0", True),
                            ("'24'", True), ('"22.12"', False), ("22.12.9", False), ("21", False),
                            ("lts/*", False)):
            with self.subTest(spec=spec):
                self.assertEqual(_node_problems(step.format(spec), floors) == [], meets)
        self.assertNotEqual(_node_problems("jobs: {}\n", floors), [])

    def test_the_workflow_token_only_reads(self):
        text = _read(self.WORKFLOW)
        found = re.search(r"(?m)^permissions:[ \t]*\n[ \t]+contents:[ \t]*read[ \t]*$", text)
        self.assertIsNotNone(found, f"{self.WORKFLOW}: no workflow-level "
                                    "`permissions: contents: read`")
        grants = _write_grants(text)
        self.assertEqual(grants, [], f"{self.WORKFLOW}: a permission grants write: {grants}")

    def test_a_job_level_write_is_found(self):
        workflow = ("permissions:\n  contents: read\n\njobs:\n  gates:\n    runs-on: ubuntu-latest\n"
                    "{}    steps:\n      - run: true\n")
        for job, writes in (("", 0), ("    permissions:\n      contents: read\n", 0),
                            ("    permissions:\n      contents: write\n", 1),
                            ("    permissions:\n      # one scope\n      pull-requests: 'write'\n", 1),
                            ("    permissions: write-all\n", 1),
                            ("    permissions: { contents: write }\n", 1)):
            with self.subTest(job=job):
                self.assertEqual(len(_write_grants(workflow.format(job))), writes)


if __name__ == "__main__":
    unittest.main()
