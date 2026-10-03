"""Tests for plan_gantt.py (TASK 108: R8, A3, D11, D19, D20).

No test needs node or a browser. Files are written to a temporary directory outside the
repository. `TestPlannerSurfaces` reads the planner and plan-reviewer surfaces that run the
script, and skips when the skill is installed without them.

A3 is checked against `fixtures/plan-example-geometry.json`: the bar geometry of the 10-task
example (`fixtures/plan-example.json`) as rendered in mermaid 11.17.2, 10.9.8 and a dark 11.17.2,
bound to the sha256 of the fence it was rendered from. When the generated fence changes, the
binding test fails with "re-render". This command renders the block again with
`render_check.py --json` and rewrites the fixture; it needs node, the pinned renderers and a
browser, and DIR lies outside every git work tree:

    python3 .agent/skills/mermaid-authoring-guidelines/scripts/tests/test_plan_gantt.py \
        --regenerate-geometry DIR
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import unicodedata
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR.parent))
import mermaid_model as mm  # noqa: E402
import plan_gantt as pg  # noqa: E402

FIXTURES = TESTS_DIR / "fixtures"
EXAMPLE_PATH = FIXTURES / "plan-example.json"
GEOMETRY_PATH = FIXTURES / "plan-example-geometry.json"
GEOMETRY_SCHEMA = "plan-gantt-geometry/v1"
RENDER_CHECK = TESTS_DIR.parent / "render_check.py"
REGENERATE = ("python3 .agent/skills/mermaid-authoring-guidelines/scripts/tests/test_plan_gantt.py "
              "--regenerate-geometry <a directory outside the repository>")

# The 10-task example of research r4 §7, with statuses. Stages are areas, not time barriers: B4
# waits for O2, which a later stage holds, so a hand-written `after B3 O2` would place B4 too early.
EXAMPLE = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
# r4 §7 hand check: B3 = max(3, 4) = 4; O1 = 3; O2 = 7; B4 = max(8, 10) = 10; W2 = max(5, 8) = 8;
# W3 = 12; O3 = max(13, 15, 7) = 15. Critical path 19 h: B2 -> B3 -> W2 -> W3 -> O3.
EXPECTED_ES = {"B1": 0, "B2": 0, "B3": 4, "B4": 10, "W1": 3, "W2": 8, "W3": 12, "O1": 3,
               "O2": 7, "O3": 15}
EXPECTED_CRITICAL = ["B2", "B3", "W2", "W3", "O3"]
# r4 §7: slack O1, O2 and B4 2 h; W1 3 h; B1 1 h; the critical tasks 0.
EXPECTED_SLACK = {"B1": 1, "B2": 0, "B3": 0, "B4": 2, "W1": 3, "W2": 0, "W3": 0, "O1": 2,
                  "O2": 2, "O3": 0}

TASK_LINE_RE = re.compile(r"^    (?P<label>[^:\n]+):(?P<meta>[^\n]+)$")


def tasks_of(data):
    return [pg.Task(**t) for t in copy.deepcopy(data)["tasks"]]


def without_status(data):
    data = copy.deepcopy(data)
    for t in data["tasks"]:
        t.pop("status", None)
    return data


def chain(n, stage="Build"):
    """A plan of *n* tasks, each waiting for the one before it."""
    return {"schema": pg.SCHEMA, "tasks": [
        {"id": f"T{i}", "title": f"step {i}", "stage": stage, "est": 1,
         "deps": [f"T{i - 1}"] if i else []} for i in range(n)]}


def block_of(data, stages=None):
    tasks = tasks_of(data)
    return pg.render_block(tasks, pg.schedule(tasks), stages)


def fences(block):
    return re.findall(r"```mermaid\n(.*?)\n```", block, re.S)


def chart_signature(fence):
    """The chart without its words: per bar (section ordinal, figure id, tags, start, duration),
    and the gantt statements. Labels, section titles and the label-dependent paddings are out."""
    rows, statements, section = [], [], -1
    for line in fence.split("\n")[1:]:
        if line.startswith("  section "):
            section += 1
            continue
        m = TASK_LINE_RE.match(line)
        if m:
            parts = [p.strip() for p in m.group("meta").split(",")]
            rows.append((section, parts[-3], tuple(parts[:-3]), parts[-2], parts[-1]))
        elif not line.startswith("  acc"):
            statements.append(line)
    return rows, statements


def init_config(fence):
    first = fence.split("\n")[0]
    m = re.fullmatch(r"%%\{init: (\{.*\})\}%%", first)
    assert m, first
    return json.loads(m.group(1))


def notation_with(gantt_settings):
    """A copy of notation.json whose `settings.gantt` line holds *gantt_settings*."""
    notation = copy.deepcopy(pg.load_notation())
    notation["settings"]["gantt"] = ("%%{init: " + json.dumps(gantt_settings, ensure_ascii=False)
                                     + "}%%")
    return notation


def markdown_plan(data, prose="", heading="# Plan", blank=True, region=""):
    gap = "\n" if blank else ""
    return (f"{heading}\n\n{prose}\n\n{pg.SCHEDULE_ANCHOR}\n{gap}```json\n"
            f"{json.dumps(data, ensure_ascii=False, indent=1)}\n```\n\n"
            f"{pg.MARKER_START}\n{region}{pg.MARKER_END}\n\nTail text.\n")


def region_of(text):
    """The text from the start marker to the end marker, both included."""
    return text[text.index(pg.MARKER_START):text.index(pg.MARKER_END) + len(pg.MARKER_END)]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def example_block():
    """The block plan_gantt.py generates from the example file, and the body of its fence."""
    tasks = pg.load_tasks(EXAMPLE_PATH)
    block = pg.render_charts(tasks, pg.schedule(tasks), None, pg.load_notation()).text
    found = fences(block)
    if len(found) != 1:
        raise AssertionError(f"the example block holds {len(found)} mermaid fences, not 1")
    return block, found[0]


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = pg.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def snapshot(self):
        """Every file of the temporary directory with its bytes and modification time."""
        return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in sorted(self.dir.iterdir())}


# --------------------------------------------------------------------------- schedule


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.tasks = tasks_of(EXAMPLE)
        self.sched = pg.schedule(self.tasks)

    def test_the_example_file_is_the_ten_task_example(self):
        self.assertEqual([t["id"] for t in EXAMPLE["tasks"]], list(EXPECTED_ES))
        self.assertEqual(pg.load_tasks(EXAMPLE_PATH), self.tasks)

    def test_early_starts_of_the_r4_example(self):
        self.assertEqual(self.sched.es, EXPECTED_ES)

    def test_finishes_and_span(self):
        self.assertEqual(self.sched.ef, {t.id: EXPECTED_ES[t.id] + t.est for t in self.tasks})
        self.assertEqual(self.sched.span, 19)

    def test_critical_path_of_the_r4_example(self):
        self.assertEqual(self.sched.critical, EXPECTED_CRITICAL)

    def test_slack_of_the_r4_example(self):
        self.assertEqual(self.sched.slack, EXPECTED_SLACK)

    def test_ready_is_not_done_with_every_dependency_done(self):
        # B3 is in progress with B1 and B2 done; O1 waits only for B1, which is done.
        self.assertEqual(self.sched.ready, ["B3", "O1"])

    def test_without_status_the_roots_are_ready(self):
        sched = pg.schedule(tasks_of(without_status(EXAMPLE)))
        self.assertEqual(sched.ready, ["B1", "B2"])
        self.assertEqual(sched.es, EXPECTED_ES)

    def test_a_tie_goes_to_input_order(self):
        data = {"schema": pg.SCHEMA, "tasks": [
            {"id": "A", "title": "a", "stage": "s", "est": 2, "deps": []},
            {"id": "B", "title": "b", "stage": "s", "est": 2, "deps": []},
            {"id": "C", "title": "c", "stage": "s", "est": 1, "deps": ["B", "A"]},
        ]}
        sched = pg.schedule(tasks_of(data))
        self.assertEqual(sched.critical, ["A", "C"])
        self.assertEqual(sched.slack["B"], 0)
        block = pg.render_block(tasks_of(data), sched)
        self.assertIn("Also at zero slack: B.", block)

    def test_the_latest_finishing_task_ends_the_path(self):
        data = {"schema": pg.SCHEMA, "tasks": [
            {"id": "A", "title": "a", "stage": "s", "est": 1, "deps": []},
            {"id": "B", "title": "b", "stage": "s", "est": 9, "deps": []},
            {"id": "C", "title": "c", "stage": "s", "est": 1, "deps": ["A"]},
        ]}
        self.assertEqual(pg.schedule(tasks_of(data)).critical, ["B"])


# --------------------------------------------------------------------------- validation


class TestValidation(unittest.TestCase):
    def assertPlanError(self, data, *fragments):
        with self.assertRaises(pg.PlanError) as ctx:
            pg.schedule(tasks_of(data))
        for fragment in fragments:
            self.assertIn(fragment, str(ctx.exception))

    def mutate(self, tid, **changes):
        data = copy.deepcopy(EXAMPLE)
        for t in data["tasks"]:
            if t["id"] == tid:
                t.update(changes)
        return data

    def test_cycle_names_its_tasks(self):
        data = self.mutate("B1", deps=["O3"])
        with self.assertRaises(pg.PlanError) as ctx:
            pg.schedule(tasks_of(data))
        message = str(ctx.exception)
        self.assertIn("dependency cycle", message)
        self.assertIn("B1 depends on O3", message)

    def test_self_dependency(self):
        self.assertPlanError(self.mutate("W1", deps=["W1"]), "task W1: depends on itself")

    def test_unknown_dependency(self):
        self.assertPlanError(self.mutate("W2", deps=["W1", "X9"]),
                             "task W2: unknown dependency X9")

    def test_duplicate_id(self):
        data = copy.deepcopy(EXAMPLE)
        data["tasks"].append(dict(data["tasks"][0], title="again"))
        self.assertPlanError(data, "task B1: duplicate id")

    def test_non_integer_estimates(self):
        for bad in (2.5, "3", True, 0, -1, None):
            with self.subTest(est=bad):
                self.assertPlanError(self.mutate("B3", est=bad), "task B3: est must be a whole")

    def test_integral_float_estimate_is_accepted_from_json(self):
        data = self.mutate("B3", est=4.0)
        tasks = pg._tasks_from_data(data)
        self.assertEqual(pg.schedule(tasks).es, EXPECTED_ES)

    def test_unknown_status(self):
        self.assertPlanError(self.mutate("O2", status="started"), "task O2: unknown status")

    def test_reserved_and_date_ids(self):
        self.assertPlanError(self.mutate("B1", id="section"), "task section: the id opens")
        self.assertPlanError(self.mutate("B1", id="2026-01-05"), "the id opens a gantt")

    def test_figure_ids_must_not_collide(self):
        data = {"schema": pg.SCHEMA, "tasks": [
            {"id": "1.1", "title": "a", "stage": "s", "est": 1, "deps": []},
            {"id": "1-1", "title": "b", "stage": "s", "est": 1, "deps": []},
        ]}
        self.assertPlanError(data, "task 1-1: its figure id t1x1 equals that of task 1.1")

    def test_shape_errors_name_the_task(self):
        cases = [
            ({"schema": "plan/v0", "tasks": EXAMPLE["tasks"]}, '"schema" must be'),
            ({"schema": pg.SCHEMA, "tasks": []}, '"tasks" must be a non-empty list'),
            ({"schema": pg.SCHEMA, "tasks": EXAMPLE["tasks"], "extra": 1}, "unknown top-level"),
            (self.mutate("B2", owner="x"), "task B2: unknown key 'owner'"),
        ]
        for data, fragment in cases:
            with self.subTest(fragment=fragment):
                with self.assertRaises(pg.PlanError) as ctx:
                    pg._tasks_from_data(data)
                self.assertIn(fragment, str(ctx.exception))
        data = copy.deepcopy(EXAMPLE)
        del data["tasks"][3]["deps"]
        with self.assertRaises(pg.PlanError) as ctx:
            pg._tasks_from_data(data)
        self.assertIn("task B4: missing key deps", str(ctx.exception))

    def test_figure_id_shape(self):
        self.assertEqual(pg.figure_id("B1"), "tB1")
        self.assertEqual(pg.figure_id("108.3"), "t108x3")
        self.assertRegex(pg.figure_id("a_b-c.d"), r"^[A-Za-z0-9]+$")


# --------------------------------------------------------------------------- inputs


class TestInputs(TempDirCase):
    def test_markdown_block_equals_the_json_file(self):
        for data in (EXAMPLE, without_status(EXAMPLE)):
            with self.subTest(status="status" in data["tasks"][0]):
                from_json = pg.load_tasks(self.write("plan.json", json.dumps(data)))
                from_md = pg.load_tasks(self.write("PLAN.md", markdown_plan(data, prose="Prose.")))
                self.assertEqual(from_json, from_md)
                self.assertEqual(pg.render_block(from_json, pg.schedule(from_json)),
                                 pg.render_block(from_md, pg.schedule(from_md)))

    def test_status_is_optional_in_either_input(self):
        """TASK R8.1: `status` may appear in the JSON file and in the Markdown block alike; a task
        without it is not started."""
        mixed = copy.deepcopy(EXAMPLE)
        del mixed["tasks"][7]["status"]  # O1
        for name, text in (("plan.json", json.dumps(mixed)), ("PLAN.md", markdown_plan(mixed))):
            with self.subTest(input=name):
                status = {t.id: t.status for t in pg.load_tasks(self.write(name, text))}
                self.assertEqual(status["B3"], "in-progress")
                self.assertEqual(status["B1"], "done")
                self.assertEqual(status["O1"], "not-started")
        plain = self.write("PLAN.md", markdown_plan(without_status(EXAMPLE)))
        self.assertEqual({t.status for t in pg.load_tasks(plain)}, {"not-started"})

    def test_an_unknown_status_in_a_markdown_block_is_invalid(self):
        data = copy.deepcopy(EXAMPLE)
        data["tasks"][0]["status"] = "finished"
        with self.assertRaises(pg.PlanError) as ctx:
            pg.load_tasks(self.write("PLAN.md", markdown_plan(data)))
        self.assertIn("task B1: unknown status 'finished'", str(ctx.exception))

    def test_anchor_directly_above_the_fence(self):
        data = without_status(EXAMPLE)
        tasks = pg.load_tasks(self.write("PLAN.md", markdown_plan(data, blank=False)))
        self.assertEqual([t.id for t in tasks], [t["id"] for t in data["tasks"]])

    def test_no_block(self):
        with self.assertRaises(pg.PlanError) as ctx:
            pg.load_tasks(self.write("PLAN.md", "# Plan\n\n- Task 1.1\n"))
        self.assertIn("no schedule block", str(ctx.exception))

    def test_two_blocks(self):
        one = markdown_plan(without_status(EXAMPLE))
        with self.assertRaises(pg.PlanError) as ctx:
            pg.load_tasks(self.write("PLAN.md", one + "\n" + one))
        self.assertIn("appears 2 times", str(ctx.exception))

    def test_bad_json_names_the_document_line(self):
        # line 7 of the document is the second line of the JSON block
        text = (f"# Plan\n\n{pg.SCHEDULE_ANCHOR}\n\n```json\n"
                "{\"schema\": \"plan-schedule/v1\",\n \"tasks\": @\n}\n```\n")
        with self.assertRaises(pg.PlanError) as ctx:
            pg.load_tasks(self.write("PLAN.md", text))
        self.assertIn("line 7, column 11", str(ctx.exception))
        self.assertIn("not valid JSON", str(ctx.exception))

    def test_anchor_without_a_json_fence(self):
        cases = {
            "prose": f"{pg.SCHEDULE_ANCHOR}\nSome prose.\n",
            "two blank lines": f"{pg.SCHEDULE_ANCHOR}\n\n\n```json\n{{}}\n```\n",
            "yaml fence": f"{pg.SCHEDULE_ANCHOR}\n```yaml\nschema: x\n```\n",
            "unclosed": f"{pg.SCHEDULE_ANCHOR}\n```json\n{{}}\n",
        }
        for name, text in cases.items():
            with self.subTest(name):
                with self.assertRaises(pg.PlanError):
                    pg.load_tasks(self.write("PLAN.md", text))

    def test_anchor_inside_a_code_fence_is_not_an_anchor(self):
        quoted = f"````markdown\n{pg.SCHEDULE_ANCHOR}\n```json\n{{}}\n```\n````\n\n"
        text = quoted + markdown_plan(without_status(EXAMPLE))
        tasks = pg.load_tasks(self.write("PLAN.md", text))
        self.assertEqual(len(tasks), 10)

    def test_prose_is_never_parsed(self):
        prose = ("### Stage 1: Backend\n- **Task B4** — Notifications\n  - Dependencies: Task X9\n"
                 "  - Estimate: 99 h")
        tasks = pg.load_tasks(self.write("PLAN.md",
                                         markdown_plan(without_status(EXAMPLE), prose=prose)))
        self.assertEqual(pg.schedule(tasks).es, EXPECTED_ES)


class TestRussianTwin(TempDirCase):
    """TASK R8.7: a plan whose headings and titles are Russian yields the English twin's chart."""

    EN = {"schema": "plan-schedule/v1", "tasks": [
        {"id": "1.1", "title": "API skeleton and stubs", "stage": "Stage 1: Backend", "est": 3,
         "deps": []},
        {"id": "1.2", "title": "Orders: logic", "stage": "Stage 1: Backend", "est": 4,
         "deps": ["1.1", "2.2"]},
        {"id": "2.1", "title": "Staging environment", "stage": "Stage 2: Operations", "est": 2,
         "deps": ["1.1"]},
        {"id": "2.2", "title": "Mail relay", "stage": "Stage 2: Operations", "est": 3,
         "deps": ["2.1"]},
        {"id": "3.1", "title": "Release rehearsal", "stage": "Stage 3: Release", "est": 2,
         "deps": ["1.2", "2.2"]},
    ]}
    RU_TITLES = {"1.1": "Каркас API и заглушки", "1.2": "Заказы: логика",
                 "2.1": "Стенд для приёмки", "2.2": "Почтовый релей",
                 "3.1": "Репетиция релиза"}
    RU_STAGES = {"Stage 1: Backend": "Этап 1: бэкенд", "Stage 2: Operations": "Этап 2: эксплуатация",
                 "Stage 3: Release": "Этап 3: выпуск"}

    def ru(self):
        data = copy.deepcopy(self.EN)
        for t in data["tasks"]:
            t["title"] = self.RU_TITLES[t["id"]]
            t["stage"] = self.RU_STAGES[t["stage"]]
        return data

    def test_same_chart(self):
        en = self.write("PLAN-en.md", markdown_plan(
            self.EN, heading="# Plan 042", prose="### Stage 1\n- **Task 1.2**\n  - Dependencies: none"))
        ru = self.write("PLAN-ru.md", markdown_plan(
            self.ru(), heading="# План 042",
            prose="### Этап 1\n- **Задача 1.2**\n  - Зависимости: Задача 9.9\n  - Оценка: 40 ч"))
        en_tasks, ru_tasks = pg.load_tasks(en), pg.load_tasks(ru)
        en_sched, ru_sched = pg.schedule(en_tasks), pg.schedule(ru_tasks)
        for attr in ("es", "ef", "critical", "ready", "span", "slack"):
            self.assertEqual(getattr(en_sched, attr), getattr(ru_sched, attr), attr)
        en_block = pg.render_block(en_tasks, en_sched)
        ru_block = pg.render_block(ru_tasks, ru_sched)
        self.assertEqual(chart_signature(fences(en_block)[0]), chart_signature(fences(ru_block)[0]))
        self.assertEqual(en_block.rsplit("\n", 1)[1], ru_block.rsplit("\n", 1)[1])  # critical path

    def test_layout_counts_characters_not_words_or_script(self):
        latin = copy.deepcopy(self.EN)
        cyrillic = copy.deepcopy(self.EN)
        for t in cyrillic["tasks"]:  # same length per title, another script, other word counts
            t["title"] = ("Ж" * len(t["title"]))
        self.assertEqual(init_config(fences(block_of(latin))[0]),
                         init_config(fences(block_of(cyrillic))[0]))


# --------------------------------------------------------------------------- encoding


class TestEncoding(unittest.TestCase):
    def setUp(self):
        self.block = block_of(EXAMPLE)
        self.fence = fences(self.block)[0]
        self.lines = self.fence.split("\n")

    def test_numeric_starts_and_no_after(self):
        self.assertNotRegex(self.fence, r"(?m)\bafter\b")
        rows, _ = chart_signature(self.fence)
        starts = {fid: int(start) for _, fid, _, start, _ in rows}
        self.assertEqual(starts, {pg.figure_id(k): v for k, v in EXPECTED_ES.items()})
        durations = {fid: dur for _, fid, _, _, dur in rows}
        self.assertEqual(durations, {pg.figure_id(t["id"]): f"{t['est']}ms"
                                     for t in EXAMPLE["tasks"]})

    def test_statements(self):
        for statement in ("gantt", "  dateFormat x", "  axisFormat %Q", "  tickInterval 2millisecond",
                          "  todayMarker off"):
            self.assertIn(statement, self.lines)
        self.assertNotIn("  topAxis", self.lines)  # the statement throws in 10.9 and 12.1
        self.assertFalse(any(line.strip().startswith("title ") for line in self.lines))

    def test_top_axis_above_thirty_bars(self):
        self.assertNotIn("topAxis", init_config(fences(block_of(chain(30)))[0])["gantt"])
        self.assertIs(init_config(fences(block_of(chain(31)))[0])["gantt"]["topAxis"], True)

    def test_tags_follow_status_and_the_critical_path(self):
        rows, _ = chart_signature(self.fence)
        tags = {fid: set(t) for _, fid, t, _, _ in rows}
        self.assertEqual(tags["tB1"], {"done"})
        self.assertEqual(tags["tB2"], {"done", "crit"})
        self.assertEqual(tags["tB3"], {"active", "crit"})
        self.assertEqual(tags["tO1"], set())
        self.assertEqual({fid for fid, t in tags.items() if "crit" in t},
                         {pg.figure_id(c) for c in EXPECTED_CRITICAL})

    def test_sections_are_contiguous_in_first_appearance_order(self):
        data = copy.deepcopy(without_status(EXAMPLE))
        data["tasks"].sort(key=lambda t: t["id"][1])  # interleave the stages in the input
        fence = fences(block_of(data))[0]
        sections = [line for line in fence.split("\n") if line.startswith("  section ")]
        self.assertEqual(len(sections), len(set(sections)))
        self.assertEqual(sections, ["  section Stage 1 — Backend",
                                    "  section Stage 2 — Web client",
                                    "  section Stage 3 — Operations"])

    def test_rows_in_a_section_follow_early_start(self):
        rows, _ = chart_signature(self.fence)
        for section in range(3):
            starts = [int(s) for sec, _, _, s, _ in rows if sec == section]
            self.assertEqual(starts, sorted(starts))

    def test_caption_above_and_legend_below_the_fence(self):
        paragraphs = self.block.split("\n\n")
        i = next(n for n, p in enumerate(paragraphs) if p.startswith("```mermaid"))
        self.assertTrue(paragraphs[i - 1].startswith("**Plan chart.**"))
        self.assertTrue(paragraphs[i + 1].startswith("Legend: "))
        self.assertNotIn("\n", paragraphs[i + 1])
        for item in ("green fill", "amber fill", "white fill", "red border"):
            self.assertIn(item, paragraphs[i + 1])

    def test_legend_names_only_the_notation_drawn(self):
        legend = next(p for p in block_of(without_status(EXAMPLE)).split("\n\n")
                      if p.startswith("Legend: "))
        self.assertNotIn("green fill", legend)
        self.assertNotIn("amber fill", legend)
        self.assertIn("white fill", legend)
        self.assertIn("red border", legend)

    def test_ready_list_and_critical_path_line(self):
        self.assertIn("- **O1** Staging environment — 4 h, slack 2 h", self.block)
        self.assertIn("- **B3** Orders: logic — 4 h, critical path, in progress", self.block)
        self.assertTrue(self.block.endswith(
            "Critical path — 19 h by estimates, 1 of 5 tasks done, 15 h remaining: "
            "B2 → B3 → W2 → W3 → O3."))
        plain = block_of(without_status(EXAMPLE))
        self.assertTrue(plain.endswith("Critical path — 19 h by estimates: "
                                       "B2 → B3 → W2 → W3 → O3."))

    def test_tick_interval_rule(self):
        cases = [((0, 7), 1), ((0, 9), 1), ((0, 10), 2), ((0, 19), 2), ((0, 20), 5), ((0, 49), 5),
                 ((0, 50), 10), ((0, 95), 10), ((0, 180), 20), ((0, 240), 25), ((20, 70), 10),
                 ((0, 1200), 200), ((0, 2400), 250), ((0, 100000), 20000)]
        for (lo, hi), step in cases:
            with self.subTest(lo=lo, hi=hi):
                self.assertEqual(pg.tick_step(lo, hi), step)
                self.assertLessEqual(hi // step - (-(-lo // step)) + 1, pg.TICKS_MAX)


# --------------------------------------------------------------------------- settings line


def _strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


class TestSettings(unittest.TestCase):
    """The settings line is `settings.gantt` of notation.json with the computed layout merged in;
    every key and value of it reaches mermaid unchanged."""

    def setUp(self):
        self.notation = pg.load_notation()
        self.base = pg._gantt_settings(self.notation)
        self.cfg = init_config(fences(block_of(EXAMPLE))[0])

    def test_the_line_is_notation_plus_the_computed_layout(self):
        self.assertEqual(set(self.cfg), set(self.base))  # no top-level key added or dropped
        self.assertEqual(self.cfg["themeVariables"], self.base["themeVariables"])
        self.assertEqual(self.cfg.get("themeCSS"), self.base.get("themeCSS"))
        self.assertIn("themeCSS", self.cfg)
        for key, value in self.base["gantt"].items():
            if key not in ("leftPadding", "rightPadding", "topAxis"):
                self.assertEqual(self.cfg["gantt"][key], value, key)
        self.assertEqual(set(self.cfg["gantt"]),
                         set(self.base["gantt"]) | {"useWidth", "leftPadding", "rightPadding"})

    def test_the_r4_layout_values(self):
        g = self.cfg["gantt"]
        self.assertEqual(g["useWidth"], self.base["gantt"]["useWidth"])
        self.assertEqual(g["useWidth"], g["leftPadding"] + g["rightPadding"] + 504)
        self.assertEqual((g["leftPadding"], g["rightPadding"]), (168, 228))  # r4 §7 values
        self.assertNotIn("topAxis", g)

    def test_use_width_of_the_settings_line_sets_the_layout(self):
        wide = copy.deepcopy(self.base)
        wide["gantt"]["useWidth"] = 1000
        g = init_config(fences(pg.render_block(tasks_of(EXAMPLE), pg.schedule(tasks_of(EXAMPLE)),
                                               None, notation_with(wide)))[0])["gantt"]
        self.assertEqual(g["useWidth"], 1000)
        self.assertEqual(g["leftPadding"], 168)  # the section titles set it, not the width
        self.assertGreater(1000 - g["leftPadding"] - g["rightPadding"], 504)

    def test_without_use_width_the_column_width_is_written(self):
        bare = copy.deepcopy(self.base)
        bare["gantt"].pop("useWidth", None)
        g = init_config(fences(pg.render_block(tasks_of(EXAMPLE), pg.schedule(tasks_of(EXAMPLE)),
                                               None, notation_with(bare)))[0])["gantt"]
        self.assertEqual(g["useWidth"], self.notation["column_px"])

    def test_every_value_is_sanitizer_safe(self):
        self.assertEqual(pg._setting_problems(self.cfg), [])
        # restated without the script's helpers
        self.assertNotIn("theme", self.cfg)
        self.assertLessEqual(set(self.cfg["gantt"]), pg.GANTT_CONFIG_KEYS)
        for value in self.cfg["themeVariables"].values():
            self.assertRegex(value, r'^[\d "#%(),.;A-Za-z]+$')
        for text in _strings(self.cfg):
            for unsafe in ("<", ">", "url(data:", "'", "%%", "\n"):
                self.assertNotIn(unsafe, text)
        depth = 0
        for ch in self.cfg["themeCSS"]:
            depth += {"{": 1, "}": -1}.get(ch, 0)
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)
        for value in self.cfg["gantt"].values():
            self.assertIsInstance(value, (int, bool))

    def test_unsafe_settings_are_named(self):
        cases = {
            "a fixed theme": ({"theme": "base"}, "theme:"),
            "a child combinator": ({"themeCSS": ".a > .b { fill: #fff; }"}, "'>'"),
            "an apostrophe": ({"themeCSS": ".a { font-family: 'x'; }"}, "\"'\""),
            "a comment opener": ({"themeCSS": ".a { width: 50%%; }"}, "'%%'"),
            "unbalanced braces": ({"themeCSS": ".a { fill: #fff; "}, "unbalanced braces"),
            "a closing brace first": ({"themeCSS": "} .a { fill: #fff; "}, "unbalanced braces"),
            "a line break": ({"themeCSS": ".a {\n}"}, "line break"),
            "a hyphenated theme value": ({"themeVariables": {"fontFamily": "sans-serif"}},
                                         "mermaid blanks it"),
            "a theme value that ends in a line break": ({"themeVariables": {"taskTextColor": "#212121\n"}},
                                                        "mermaid blanks it"),
            "a misspelt gantt key": ({"gantt": {"barheight": 16}}, "gantt.barheight"),
            "an unknown top-level key": ({"fontFamily": "Arial"}, "fontFamily: not a key"),
            "a null": ({"gantt": {"barGap": None}}, "null"),
            "a prototype key": ({"gantt": {"__proto__": 1}}, "mermaid deletes this key"),
        }
        for name, (patch, fragment) in cases.items():
            with self.subTest(name):
                cfg = copy.deepcopy(self.base)
                for key, value in patch.items():
                    if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                        cfg[key].update(value)
                    else:
                        cfg[key] = value
                problems = pg._setting_problems(cfg)
                self.assertTrue(any(fragment in p for p in problems), problems)

    def test_an_unsafe_notation_stops_the_chart(self):
        bad = copy.deepcopy(self.base)
        bad["themeCSS"] = ".a > .b { fill: #fff; }"
        tasks = tasks_of(EXAMPLE)
        with self.assertRaises(RuntimeError) as ctx:
            pg.render_block(tasks, pg.schedule(tasks), None, notation_with(bad))
        self.assertIn("themeCSS", str(ctx.exception))


class TestLabels(unittest.TestCase):
    def one(self, title, stage="Stage"):
        data = {"schema": pg.SCHEMA, "tasks": [
            {"id": "T1", "title": title, "stage": stage, "est": 2, "deps": []}]}
        return block_of(data)

    def task_lines(self, block):
        return [line for line in fences(block)[0].split("\n") if TASK_LINE_RE.match(line)]

    def test_colon_hash_semicolon_and_line_breaks(self):
        line = self.task_lines(self.one("Orders: retry #1; then\nnotify %%{init}%%"))[0]
        label = TASK_LINE_RE.match(line).group("label")
        self.assertEqual(label.count(":"), 0)
        self.assertNotIn("#", label)
        self.assertNotIn(";", label)
        self.assertNotIn("%%", label)
        self.assertEqual(label, "T1 Orders — retry 1, then" + pg.ELLIPSIS)  # 32-char limit
        short = TASK_LINE_RE.match(self.task_lines(self.one("a\tb\nc %%x"))[0]).group("label")
        self.assertEqual(short, "T1 a b c %x")

    def test_label_limit_in_characters(self):
        limit = pg.load_notation()["labels"]["gantt_label_chars_max"]
        for title in ("A" * 80, "word " * 20, "Длинное " * 9):
            with self.subTest(title=title[:10]):
                label = TASK_LINE_RE.match(self.task_lines(self.one(title))[0]).group("label")
                self.assertLessEqual(len(label), limit)
                self.assertTrue(label.endswith(pg.ELLIPSIS))
                self.assertTrue(label.startswith("T1 "))

    def test_section_titles_wrap_in_characters(self):
        limit = pg.load_notation()["labels"]["gantt_label_chars_max"]
        stage = "Stage 4: operations, monitoring and backups; part #2"
        section = next(line for line in fences(self.one("x", stage=stage))[0].split("\n")
                       if line.startswith("  section "))
        lines = section[len("  section "):].split("<br>")
        self.assertLessEqual(len(lines), 2)
        for line in lines:
            self.assertLessEqual(len(line), limit)
            self.assertFalse(set(line) & set(":#;"))

    def test_a_title_cannot_close_the_generated_block(self):
        block = self.one(f"evil {pg.MARKER_END} title")
        self.assertNotIn(pg.MARKER_END, block)
        self.assertNotIn("<!--", block.split("```")[-1])


class TestStages(unittest.TestCase):
    def test_named_stages_keep_absolute_hours(self):
        tasks = tasks_of(EXAMPLE)
        sched = pg.schedule(tasks)
        block = pg.render_block(tasks, sched, ["Stage 3 — Operations"])
        fence = fences(block)[0]
        rows, statements = chart_signature(fence)
        self.assertEqual({fid: int(s) for _, fid, _, s, _ in rows},
                         {"tO1": 3, "tO2": 7, "tO3": 15})
        self.assertIn("  tickInterval 2millisecond", statements)
        self.assertTrue(block.startswith("**Plan chart: Stage 3 — Operations.**"))
        self.assertIn("start of the whole plan", block.split("\n")[0])
        self.assertIn("B2 → B3 → W2 → W3 → O3", block)  # whole-plan path

    def test_groups_give_one_chart_each_and_one_ready_list(self):
        tasks = tasks_of(EXAMPLE)
        out = pg.render_charts(tasks, pg.schedule(tasks),
                               [["Stage 1 — Backend"], ["Stage 2 — Web client",
                                                             "Stage 3 — Operations"]])
        self.assertEqual(len(fences(out.text)), 2)
        self.assertEqual(out.bars, [4, 6])
        self.assertEqual(out.text.count("Ready to start"), 1)
        self.assertEqual(out.text.count("Critical path —"), 1)

    def test_unknown_stage(self):
        tasks = tasks_of(EXAMPLE)
        with self.assertRaises(pg.PlanError):
            pg.render_block(tasks, pg.schedule(tasks), ["Stage 9"])


# --------------------------------------------------------------------------- markers and CLI


class TestMarkers(unittest.TestCase):
    def test_region_layout(self):
        doc = f"head\n{pg.MARKER_START}\nold\n{pg.MARKER_END}\ntail\n"
        self.assertEqual(pg.replace_between_markers(doc, "new\nblock\n"),
                         f"head\n{pg.MARKER_START}\n\nnew\nblock\n\n{pg.MARKER_END}\ntail\n")

    def test_an_empty_block_leaves_the_markers_adjacent(self):
        doc = f"head\n{pg.MARKER_START}\n\nold\n\n{pg.MARKER_END}\ntail\n"
        for block in ("", "\n", "  \n\n"):
            with self.subTest(block=block):
                self.assertEqual(pg.replace_between_markers(doc, block),
                                 f"head\n{pg.MARKER_START}\n{pg.MARKER_END}\ntail\n")

    def test_region_is_empty(self):
        for region, empty in (("", True), ("\n", True), ("  \n\t\n", True), ("x\n", False),
                              ("\n```mermaid\n```\n", False)):
            with self.subTest(region=region):
                doc = f"head\n{pg.MARKER_START}\n{region}{pg.MARKER_END}\n"
                self.assertIs(pg.region_is_empty(doc), empty)

    def test_marker_errors(self):
        for doc in ("no markers\n", f"{pg.MARKER_START}\n", f"{pg.MARKER_END}\n{pg.MARKER_START}\n",
                    f"{pg.MARKER_START}\n{pg.MARKER_END}\n{pg.MARKER_START}\n{pg.MARKER_END}\n"):
            with self.subTest(doc=doc):
                with self.assertRaises(pg.PlanError):
                    pg.replace_between_markers(doc, "x")
                with self.assertRaises(pg.PlanError):
                    pg.region_is_empty(doc)

    def test_markers_in_a_code_fence_are_text(self):
        doc = (f"```markdown\n{pg.MARKER_START}\n{pg.MARKER_END}\n```\n\n"
               f"{pg.MARKER_START}\n{pg.MARKER_END}\n")
        new = pg.replace_between_markers(doc, "x")
        self.assertTrue(new.startswith(f"```markdown\n{pg.MARKER_START}\n{pg.MARKER_END}\n```"))
        self.assertTrue(new.endswith(f"{pg.MARKER_START}\n\nx\n\n{pg.MARKER_END}\n"))

    def test_a_damaged_region_is_replaced_whole(self):
        doc = f"{pg.MARKER_START}\n```mermaid\ngantt\n{pg.MARKER_END}\nafter\n"
        self.assertEqual(pg.replace_between_markers(doc, "x"),
                         f"{pg.MARKER_START}\n\nx\n\n{pg.MARKER_END}\nafter\n")


class TestUnterminatedRegion(TempDirCase):
    def test_a_start_marker_without_end_hides_nothing(self):
        text = markdown_plan(without_status(EXAMPLE)).replace(pg.MARKER_END, "")
        text = f"{pg.MARKER_START}\n\n" + text.replace(pg.MARKER_START, "")
        plan = self.write("PLAN.md", text)
        self.assertEqual(len(pg.load_tasks(plan)), 10)  # the anchor below the marker is found
        code, _, err = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("found 1 and 0", err)


class TestSmallPlan(TempDirCase):
    """TASK R8.5: a plan of fewer than 8 tasks gets an empty region; UC-2 A2."""

    def test_the_threshold(self):
        self.assertEqual(pg.MIN_TASKS, 8)

    def stale_small_plan(self):
        """A 7-task plan whose region still holds the chart of its earlier 8-task version."""
        big = self.write("PLAN.md", markdown_plan(chain(8)))
        self.assertEqual(run_cli(str(big), "--write", str(big))[0], pg.EXIT_OK)
        chart = region_of(big.read_text(encoding="utf-8"))
        self.assertIn("```mermaid", chart)
        small = markdown_plan(chain(7)).replace(f"{pg.MARKER_START}\n{pg.MARKER_END}", chart)
        return self.write("PLAN.md", small)

    def test_write_empties_the_region_and_names_the_reason(self):
        plan = self.stale_small_plan()
        code, out, err = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("emptied", out)
        self.assertIn("7 tasks, fewer than 8", err)
        self.assertIn("R8.5", err)
        text = plan.read_text(encoding="utf-8")
        self.assertIn(f"{pg.MARKER_START}\n{pg.MARKER_END}\n\nTail text.\n", text)
        self.assertNotIn("```mermaid", text)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_check_fails_on_a_chart_in_the_region_and_writes_nothing(self):
        plan = self.stale_small_plan()
        before = self.snapshot()
        code, _, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("stale", err)
        self.assertIn("fewer than 8", err)
        self.assertEqual(self.snapshot(), before)

    def test_check_passes_on_an_empty_region(self):
        for region in ("", "\n", "\n\n"):
            with self.subTest(region=region):
                plan = self.write("PLAN.md", markdown_plan(chain(7), region=region))
                before = self.snapshot()
                code, out, _ = run_cli(str(plan), "--check", str(plan))
                self.assertEqual(code, pg.EXIT_OK)
                self.assertIn("empty", out)
                self.assertEqual(self.snapshot(), before)

    def test_write_on_an_empty_region_changes_nothing(self):
        plan = self.write("PLAN.md", markdown_plan(chain(3)))
        before = self.snapshot()
        code, out, err = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("unchanged", out)
        self.assertIn("3 tasks, fewer than 8", err)
        self.assertEqual(self.snapshot(), before)

    def test_eight_tasks_get_the_chart(self):
        for n, charted in ((7, False), (8, True)):
            with self.subTest(tasks=n):
                plan = self.write("PLAN.md", markdown_plan(chain(n)))
                self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
                self.assertIs("```mermaid" in plan.read_text(encoding="utf-8"), charted)
                self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_a_json_plan_into_a_separate_document(self):
        plan = self.write("plan.json", json.dumps(chain(5)))
        doc = self.write("report.md",
                         f"# Report\n\n{pg.MARKER_START}\nold chart\n{pg.MARKER_END}\n")
        self.assertEqual(run_cli(str(plan), "--check", str(doc))[0], pg.EXIT_FAIL)
        self.assertEqual(run_cli(str(plan), "--write", str(doc))[0], pg.EXIT_OK)
        self.assertEqual(doc.read_text(encoding="utf-8"),
                         f"# Report\n\n{pg.MARKER_START}\n{pg.MARKER_END}\n")
        self.assertEqual(run_cli(str(plan), "--check", str(doc))[0], pg.EXIT_OK)

    def test_print_previews_the_chart_of_a_small_plan(self):
        plan = self.write("PLAN.md", markdown_plan(chain(2)))
        code, out, err = run_cli(str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("```mermaid", out)
        self.assertIn("fewer than 8", err)
        self.assertIn("preview", err)

    def test_missing_markers_exit_1(self):
        plan = self.write("PLAN.md", markdown_plan(chain(3)).replace(pg.MARKER_END, ""))
        for option in ("--check", "--write"):
            with self.subTest(option=option):
                code, _, err = run_cli(str(plan), option, str(plan))
                self.assertEqual(code, pg.EXIT_FAIL)
                self.assertIn("found 1 and 0", err)

    def test_a_small_plan_is_still_validated(self):
        data = chain(3)
        data["tasks"][0]["deps"] = ["T2"]
        plan = self.write("PLAN.md", markdown_plan(data))
        code, _, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("dependency cycle", err)
        good = self.write("PLAN.md", markdown_plan(chain(3)))
        self.assertEqual(run_cli(str(good), "--check", str(good), "--stages", "Nope")[0],
                         pg.EXIT_USAGE)

    def test_every_mode_runs_every_check_of_a_chart(self):
        """A small plan gets no chart, yet the preview, `--write` and `--check` give one exit code
        for one plan. Two stages with one section title exit 1, an unsafe settings line exits 2,
        and the document keeps its bytes. The region is empty, or holds an old chart that
        `--write` would empty."""
        shared = chain(3)
        shared["tasks"][0]["stage"], shared["tasks"][1]["stage"] = "Ops#", "Ops"
        unsafe = pg._gantt_settings(pg.load_notation())
        unsafe["themeCSS"] = ".a > .b { fill: #fff; }"
        cases = {
            "shared title": (shared, pg.load_notation(), pg.EXIT_FAIL,
                             "stages 'Ops#' and 'Ops' give the same section title 'Ops'"),
            "unsafe settings": (chain(3), notation_with(unsafe), pg.EXIT_INTERNAL, "themeCSS"),
        }
        for name, (data, notation, code, fragment) in cases.items():
            for region in ("", "old chart\n"):
                plan = self.write("PLAN.md", markdown_plan(data, region=region))
                before = self.snapshot()
                with mock.patch.object(pg, "load_notation",
                                       lambda path=None, n=notation: copy.deepcopy(n)):
                    for mode in ((), ("--write", str(plan)), ("--check", str(plan))):
                        with self.subTest(case=name, region=region, mode=mode[:1]):
                            got, out, err = run_cli(str(plan), *mode)
                            self.assertEqual((got, out), (code, ""))
                            self.assertIn(fragment, err)
                with self.subTest(case=name, region=region, document="unchanged"):
                    self.assertEqual(self.snapshot(), before)

    def test_write_with_check_exits_3_and_writes_nothing(self):
        plan = self.stale_small_plan()
        before = self.snapshot()
        self.assertEqual(run_cli(str(plan), "--write", str(plan), "--check", str(plan))[0],
                         pg.EXIT_USAGE)
        self.assertEqual(self.snapshot(), before)


class TestCli(TempDirCase):
    def plan(self, data=None):
        return self.write("PLAN.md", markdown_plan(data or without_status(EXAMPLE)))

    def test_write_then_check(self):
        plan = self.plan()
        code, out, _ = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("written", out)
        text = plan.read_text(encoding="utf-8")
        self.assertIn("```mermaid", text)
        self.assertTrue(text.endswith(f"{pg.MARKER_END}\n\nTail text.\n"))
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)
        code, out, _ = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("unchanged", out)
        self.assertEqual(plan.read_text(encoding="utf-8"), text)

    def test_a_markdown_plan_with_statuses(self):
        plan = self.plan(EXAMPLE)
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
        text = plan.read_text(encoding="utf-8")
        self.assertIn(":active, crit, tB3, 4, 4ms", text)
        self.assertIn("1 of 5 tasks done", text)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_check_finds_a_stale_block_and_writes_nothing(self):
        plan = self.plan()
        run_cli(str(plan), "--write", str(plan))
        edited = plan.read_text(encoding="utf-8").replace('"est": 4', '"est": 5', 1)
        plan.write_text(edited, encoding="utf-8")
        before = self.snapshot()
        code, _, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("stale", err)
        self.assertEqual(self.snapshot(), before)
        hand_edit = self.plan()
        run_cli(str(hand_edit), "--write", str(hand_edit))
        text = hand_edit.read_text(encoding="utf-8").replace(":crit, tB2", ":tB2")
        hand_edit.write_text(text, encoding="utf-8")
        self.assertEqual(run_cli(str(hand_edit), "--check", str(hand_edit))[0], pg.EXIT_FAIL)

    def test_check_on_an_empty_region_of_a_large_plan_is_stale(self):
        plan = self.plan()
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_FAIL)

    def test_check_order_of_arguments(self):
        plan = self.plan()
        run_cli(str(plan), "--write", str(plan))
        self.assertEqual(run_cli("--check", str(plan), str(plan))[0], pg.EXIT_OK)

    def test_write_keeps_crlf_line_ends(self):
        plan = self.dir / "PLAN.md"
        plan.write_bytes(markdown_plan(without_status(EXAMPLE)).replace("\n", "\r\n")
                         .encode("utf-8"))
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
        raw = plan.read_bytes()
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_write_keeps_a_byte_order_mark(self):
        plan = self.dir / "PLAN.md"
        plan.write_bytes(b"\xef\xbb\xbf" + markdown_plan(without_status(EXAMPLE)).encode("utf-8"))
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
        self.assertTrue(plan.read_bytes().startswith(b"\xef\xbb\xbf# Plan"))
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_json_plan_into_a_separate_document(self):
        plan = self.write("plan.json", json.dumps(EXAMPLE))
        doc = self.write("report.md", f"# Report\n\n{pg.MARKER_START}\n{pg.MARKER_END}\n")
        self.assertEqual(run_cli(str(plan), "--write", str(doc))[0], pg.EXIT_OK)
        self.assertIn(":active, crit, tB3, 4, 4ms", doc.read_text(encoding="utf-8"))
        self.assertEqual(run_cli(str(plan), "--check", str(doc))[0], pg.EXIT_OK)

    def test_no_block_exits_1(self):
        plan = self.write("PLAN.md", f"# Plan\n\n{pg.MARKER_START}\n{pg.MARKER_END}\n")
        code, _, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("no schedule block", err)

    def test_invalid_plan_exits_1_with_the_message(self):
        data = without_status(EXAMPLE)
        data["tasks"][0]["deps"] = ["O3"]
        code, out, err = run_cli(str(self.write("plan.json", json.dumps(data))))
        self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
        self.assertIn("dependency cycle", err)

    def test_missing_markers_exit_1(self):
        plan = self.write("PLAN.md", markdown_plan(without_status(EXAMPLE)).replace(
            pg.MARKER_START, ""))
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_FAIL)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_FAIL)

    def test_print_wraps_the_block_in_markers(self):
        code, out, err = run_cli(str(self.plan()))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertTrue(out.startswith(pg.MARKER_START + "\n\n**Plan chart.**"))
        self.assertTrue(out.endswith("\n\n" + pg.MARKER_END + "\n"))
        self.assertNotIn("preview", err)

    def test_usage_errors_exit_3(self):
        plan = self.plan()
        cases = [
            (),
            (str(self.dir / "missing.md"),),
            (str(plan), "--write", str(plan), "--check", str(plan)),
            (str(plan), "--stages", "Stage 9"),
            (str(plan), "--stages", ","),
            (str(plan), "--check", str(self.dir / "missing.md")),
            (str(plan), "--write", str(self.dir / "missing.md")),
            (str(plan), "--no-such-option"),
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                self.assertEqual(run_cli(*argv)[0], pg.EXIT_USAGE)
        self.assertEqual(run_cli("--help")[0], pg.EXIT_OK)

    def test_a_document_that_cannot_be_written_exits_3(self):
        original = pg._write_doc

        def refuse(*args, **kwargs):
            raise PermissionError(13, "Permission denied")
        for data in (without_status(EXAMPLE), chain(3)):
            with self.subTest(tasks=len(data["tasks"])):
                plan = self.write("PLAN.md", markdown_plan(data, region="stale\n"))
                pg._write_doc = refuse
                try:
                    code, _, err = run_cli(str(plan), "--write", str(plan))
                finally:
                    pg._write_doc = original
                self.assertEqual(code, pg.EXIT_USAGE)
                self.assertIn("cannot write", err)

    def test_help_states_the_d20_exit_codes(self):
        code, out, _ = run_cli("--help")
        self.assertEqual(code, pg.EXIT_OK)
        text = " ".join(re.sub(r"\x1b\[[0-9;]*m", "", out).split())  # argparse may colour it
        self.assertIn("--strict exit 1 when a chart exceeds the hard bar budget", text)
        self.assertIn(pg.EXIT_CODES_HELP, text)
        self.assertEqual(pg.EXIT_CODES_HELP, "exit codes (TASK 108 D20): 0 ok; 1 stale region or "
                                             "invalid plan; 2 instrument broken; 3 usage error")
        self.assertEqual((pg.EXIT_OK, pg.EXIT_FAIL, pg.EXIT_INTERNAL, pg.EXIT_USAGE), (0, 1, 2, 3))

    def test_stage_names_holding_a_comma(self):
        data = without_status(EXAMPLE)
        for t in data["tasks"]:
            t["stage"] = t["stage"].replace("Stage 3 — Operations", "Ops, support")
        plan = self.write("plan.json", json.dumps(data))
        code, out, err = run_cli(str(plan), "--stages", "Ops, support,Stage 1 — Backend",
                                 "--stages", "Stage 2 — Web client")
        self.assertEqual(code, pg.EXIT_OK, err)
        first, second = fences(out)
        self.assertEqual((first.count("  section "), second.count("  section ")), (2, 1))
        self.assertIn(pg.groups_line([["Stage 1 — Backend", "Ops, support"],
                                      ["Stage 2 — Web client"]]), out)

    def test_budgets(self):
        soft, hard = pg.load_notation()["budgets"]["gantt"]["bars"]

        def plan(n):
            return self.write(f"plan{n}.json", json.dumps({"schema": pg.SCHEMA, "tasks": [
                {"id": f"T{i}", "title": "t", "stage": f"S{i // 20}", "est": 1,
                 "deps": [f"T{i - 1}"] if i else []} for i in range(n)]}))
        code, _, err = run_cli(str(plan(soft + 1)), "--strict")
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("soft budget", err)
        code, _, err = run_cli(str(plan(hard + 1)))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("hard budget", err)
        code, out, err = run_cli(str(plan(hard + 1)), "--strict")
        self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
        self.assertIn("--strict", err)
        split = ("--stages", "S0,S1", "--stages", "S2,S3")
        self.assertEqual(run_cli(str(plan(hard + 1)), "--strict", *split)[0], pg.EXIT_OK)

    def test_internal_failure_exits_2(self):
        original = pg.render_charts

        def broken(*args, **kwargs):
            raise RuntimeError("boom")
        pg.render_charts = broken
        try:
            code, _, err = run_cli(str(self.plan()))
        finally:
            pg.render_charts = original
        self.assertEqual(code, pg.EXIT_INTERNAL)
        self.assertIn("internal error", err)

    def test_an_unsafe_settings_line_exits_2(self):
        bad = pg._gantt_settings(pg.load_notation())
        bad["themeCSS"] = ".a > .b { fill: #fff; }"
        bad_notation = notation_with(bad)
        original = pg.load_notation
        pg.load_notation = lambda path=None: copy.deepcopy(bad_notation)
        try:
            code, out, err = run_cli(str(self.plan()))
        finally:
            pg.load_notation = original
        self.assertEqual((code, out), (pg.EXIT_INTERNAL, ""))
        self.assertIn("internal error", err)
        self.assertIn("themeCSS", err)

    def test_markers(self):
        self.assertEqual(pg.MARKER_START, "<!-- generated:plan-gantt-start -->")
        self.assertEqual(pg.MARKER_END, "<!-- generated:plan-gantt-end -->")
        self.assertEqual(pg.SCHEDULE_ANCHOR, "<!-- contract:schedule -->")


# --------------------------------------------------------------------------- stage groups


STAGES4 = ["S0", "S1", "S2", "S3"]
SPLIT = ("--stages", "S0,S1", "--stages", "S2,S3")
SPLIT_LINE = '<!-- plan-gantt-groups: [["S0", "S1"], ["S2", "S3"]] -->'


def staged(n, stages=STAGES4):
    """A chain of *n* one-hour tasks, spread in order over *stages*."""
    per = -(-n // len(stages))
    return {"schema": pg.SCHEMA, "tasks": [
        {"id": f"T{i}", "title": f"step {i}", "stage": stages[i // per], "est": 1,
         "deps": [f"T{i - 1}"] if i else []} for i in range(n)]}


def region_lines(text):
    """The lines between the two markers."""
    return region_of(text).split("\n")[1:-1]


class TestStoredStageGroups(TempDirCase):
    """UC-2 A3: a chart split with `--stages` passes the plain `--check` every surface runs, and
    the plain `--write` keeps the split."""

    def split_plan(self, n=70):
        plan = self.write("PLAN.md", markdown_plan(staged(n)))
        code, _, err = run_cli(str(plan), *SPLIT, "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK, err)
        return plan

    def test_a_split_write_then_the_plain_check_is_current(self):
        plan = self.split_plan()
        text = plan.read_text(encoding="utf-8")
        self.assertEqual(len(fences(text)), 2)
        self.assertEqual(next(line for line in region_lines(text) if line.strip()), SPLIT_LINE)
        code, out, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_OK, err)
        self.assertIn("current", out)
        self.assertNotIn("budget", err)
        code, out, _ = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn("unchanged", out)
        self.assertEqual(plan.read_text(encoding="utf-8"), text)

    def test_the_stale_message_names_the_stages(self):
        plan = self.split_plan()
        plan.write_text(plan.read_text(encoding="utf-8").replace('"est": 1', '"est": 2', 1),
                        encoding="utf-8")
        code, _, err = run_cli(str(plan), "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        doc = shlex.quote(str(plan))
        self.assertIn(f"run plan_gantt.py {doc} --stages S0,S1 --stages S2,S3 --write {doc}", err)
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
        self.assertEqual(len(fences(plan.read_text(encoding="utf-8"))), 2)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_the_order_of_groups_and_stages_does_not_matter(self):
        plan = self.write("PLAN.md", markdown_plan(staged(70)))
        code, _, err = run_cli(str(plan), "--stages", "S3,S2", "--stages", "S1,S0",
                               "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK, err)
        self.assertIn(SPLIT_LINE, plan.read_text(encoding="utf-8"))
        self.assertEqual(run_cli(str(plan), "--check", str(plan), "--stages", "S2,S3",
                                 "--stages", "S0,S1")[0], pg.EXIT_OK)

    def test_explicit_stages_replace_the_stored_groups(self):
        plan = self.split_plan()
        code, _, err = run_cli(str(plan), "--stages", "S0,S1,S2", "--stages", "S3",
                               "--check", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("--stages S0,S1,S2 --stages S3 --write", err)
        code, _, err = run_cli(str(plan), "--stages", "S0,S1,S2,S3", "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK, err)
        text = plan.read_text(encoding="utf-8")
        self.assertEqual(len(fences(text)), 1)  # one group of every stage is one chart
        self.assertNotIn(pg.GROUPS_PREFIX, text)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_groups_that_leave_out_or_repeat_a_stage_exit_1(self):
        plan = self.write("PLAN.md", markdown_plan(staged(70)))
        cases = {("S0,S1",): "left out: S2; S3",
                 ("S0,S1", "S1,S2,S3"): "named more than once: S1",
                 ("S0,S0,S1", "S2,S3"): "named more than once: S0"}
        for stages, fragment in cases.items():
            argv = [arg for value in stages for arg in ("--stages", value)]
            for mode in ((), ("--write", str(plan)), ("--check", str(plan))):
                with self.subTest(stages=stages, mode=mode[:1]):
                    before = self.snapshot()
                    code, out, err = run_cli(str(plan), *argv, *mode)
                    self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
                    self.assertIn(f"--stages must name every stage exactly once; {fragment}",
                                  err)
                    self.assertEqual(self.snapshot(), before)

    def test_stored_groups_that_no_longer_fit_the_plan_exit_1(self):
        region = "\n".join(region_lines(self.split_plan().read_text(encoding="utf-8"))) + "\n"
        cases = ((staged(70, ["S0", "S1", "S2", "S9"]), "name stage S3, which the plan does not"),
                 (staged(70, STAGES4 + ["S4"]), "left out: S4"))
        for data, fragment in cases:
            with self.subTest(fragment=fragment):
                plan = self.write("PLAN.md", markdown_plan(data, region=region))
                before = self.snapshot()
                for option in ("--check", "--write"):
                    code, _, err = run_cli(str(plan), option, str(plan))
                    self.assertEqual(code, pg.EXIT_FAIL)
                    self.assertIn(fragment, err)
                    self.assertIn("pass --stages to regroup", err)
                self.assertEqual(self.snapshot(), before)

    def test_a_damaged_groups_line_exits_1_until_stages_replace_it(self):
        plan = self.split_plan()
        plan.write_text(plan.read_text(encoding="utf-8").replace(SPLIT_LINE, SPLIT_LINE[:-6]
                                                                 + " -->"), encoding="utf-8")
        before = self.snapshot()
        code, _, err = run_cli(str(plan), "--write", str(plan))
        self.assertEqual(code, pg.EXIT_FAIL)
        self.assertIn("the stored stage groups are not a JSON list", err)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(run_cli(str(plan), *SPLIT, "--write", str(plan))[0], pg.EXIT_OK)
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    def test_stage_names_survive_the_groups_line(self):
        names = ["Ops, support", 'A --> B <x> "q" \\ \u2028 Ж']
        groups = [[names[0]], [names[1]]]
        line = pg.groups_line(groups)
        self.assertTrue(line.startswith(pg.GROUPS_PREFIX) and line.endswith(pg.GROUPS_SUFFIX))
        self.assertEqual(line.count("-->"), 1)
        self.assertNotIn("<", line[len("<!--"):])
        self.assertNotIn("\u2028", line)
        self.assertEqual(json.loads(line[len(pg.GROUPS_PREFIX):-len(pg.GROUPS_SUFFIX)]), groups)
        plan = self.write("PLAN.md", markdown_plan(staged(16, names)))
        code, _, err = run_cli(str(plan), "--stages", names[0], "--stages", names[1],
                               "--write", str(plan))
        self.assertEqual(code, pg.EXIT_OK, err)
        self.assertIn(line, plan.read_text(encoding="utf-8"))
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)


# --------------------------------------------------------------------------- lost markers


COVERAGE = ("<!-- contract:coverage -->\n\n## Use Case Coverage\n\n| Use Case | Tasks |\n"
            "|---|---|\n| UC-01 | T0 |\n\n")


class TestLostMarkers(TempDirCase):
    """A lost or extra marker never lets `--write` replace document text; the file keeps its
    bytes, on the chart path and on the small-plan path alike."""

    def assertRefused(self, middle, fragment):
        for n in (8, 4):
            plan = self.write("PLAN.md", f"# Plan\n\n{pg.SCHEDULE_ANCHOR}\n\n```json\n"
                                         f"{json.dumps(chain(n))}\n```\n\n{middle}")
            before = self.snapshot()
            for option in ("--write", "--check"):
                with self.subTest(tasks=n, option=option):
                    code, _, err = run_cli(str(plan), option, str(plan))
                    self.assertEqual(code, pg.EXIT_FAIL)
                    self.assertIn(fragment, err)
            self.assertEqual(self.snapshot(), before)

    def test_two_start_markers_and_one_end_marker(self):
        self.assertRefused(f"{pg.MARKER_START}\n\n{COVERAGE}## Plan chart\n\n"
                           f"{pg.MARKER_START}\n{pg.MARKER_END}\n", "found 2 and 1")

    def test_a_lost_end_marker_and_a_fenced_quote_of_both_markers(self):
        self.assertRefused(f"{pg.MARKER_START}\n\n{COVERAGE}````markdown\n{pg.MARKER_START}\n"
                           f"{pg.MARKER_END}\n````\n\nFinal paragraph that must survive.\n",
                           "found 1 and 0")

    def test_a_lost_end_marker_and_a_fenced_quote_of_the_end_marker(self):
        self.assertRefused(f"{pg.MARKER_START}\n\n{COVERAGE}````markdown\n{pg.MARKER_END}\n````\n\n"
                           "Final paragraph that must survive.\n",
                           "holds an HTML comment ('<!-- contract:coverage -->')")

    def test_the_scan_stops_at_either_marker(self):
        lines = [pg.MARKER_START, "text", pg.MARKER_START, "chart", pg.MARKER_END]
        self.assertEqual(pg._scan(lines), ([], [0, 2], [4]))

    def test_markers_in_indented_code_are_text(self):
        """R2-09: an example of the markers indented 4 columns is an indented code block; with
        no other pair, `--write` and `--check` refuse the plan and keep its bytes."""
        self.assertRefused(f"Example of the markers:\n\n    {pg.MARKER_START}\n    {pg.MARKER_END}\n",
                           "found 0 and 0")

    def test_the_scan_reads_code_as_commonmark_does(self):
        """R2-09: markers and the anchor in indented code, or in a fence opened on a list marker
        line, are text; a marker inside a list item is an HTML comment there, not code."""
        cases = [
            (["Example:", "", "    " + pg.MARKER_START, "    " + pg.MARKER_END, "", pg.MARKER_START,
              pg.MARKER_END], ([], [5], [6])),
            (["- ```markdown", "  " + pg.MARKER_START, "  " + pg.MARKER_END, "  ```", pg.MARKER_START,
              pg.MARKER_END], ([], [4], [5])),
            (["Example:", "", "    " + pg.SCHEDULE_ANCHOR, "", pg.SCHEDULE_ANCHOR], ([4], [], [])),
            (["- Example:", "", "    " + pg.MARKER_START, "    " + pg.MARKER_END], ([], [2], [3])),
        ]
        for lines, expected in cases:
            with self.subTest(lines=lines):
                self.assertEqual(pg._scan(lines), expected)

    def test_the_example_stays_and_the_chart_goes_to_the_real_region(self):
        """R2-09: the indented example keeps its bytes; the chart is written between the real
        markers, and `--check` then passes."""
        example = f"Example of the markers:\n\n    {pg.MARKER_START}\n    {pg.MARKER_END}\n\n"
        plan = self.write("PLAN.md", f"# Plan\n\n{example}{pg.SCHEDULE_ANCHOR}\n\n```json\n"
                                     f"{json.dumps(chain(8))}\n```\n\n{pg.MARKER_START}\n{pg.MARKER_END}\n")
        self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
        text = plan.read_text(encoding="utf-8")
        self.assertIn(example + pg.SCHEDULE_ANCHOR, text)
        self.assertEqual(text.count("```mermaid"), 1)
        self.assertGreater(text.index("```mermaid"), text.index(pg.SCHEDULE_ANCHOR))
        self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)


class TestRegionContent(unittest.TestCase):
    """The region holds what `plan_gantt.py` writes; document text in it means a lost marker."""

    def doc(self, region):
        return f"head\n{pg.MARKER_START}\n{region}{pg.MARKER_END}\ntail\n"

    def test_document_text_in_the_region_is_refused(self):
        groups = pg.groups_line([["A"], ["B"]])
        cases = {
            "## Use Case Coverage\n": "a heading or a rule",
            "Title\n---\n": "a heading or a rule",
            "<!-- contract:coverage -->\n": "an HTML comment",
            "Text <!-- note -->\n": "an HTML comment",
            f"{groups}\n\n{groups}\n": "an HTML comment",
            "```json\n{}\n```\n": "a fence that is not mermaid",
            "~~~\nx\n~~~\n": "a fence that is not mermaid",
        }
        for region, fragment in cases.items():
            with self.subTest(region=region):
                with self.assertRaises(pg.PlanError) as ctx:
                    pg.replace_between_markers(self.doc(region), "x")
                self.assertIn(fragment, str(ctx.exception))
                self.assertIn("the document is unchanged", str(ctx.exception))
                with self.assertRaises(pg.PlanError):
                    pg.region_is_empty(self.doc(region))

    def test_generated_text_is_accepted(self):
        data = without_status(EXAMPLE)
        data["tasks"][0]["title"] = f"evil {pg.MARKER_END} <!-- x --> # Heading"
        regions = ("", "\n", "x\n", "```mermaid\ngantt\n",
                   f"\n{pg.groups_line([['A'], ['B']])}\n\n{block_of(data)}\n\n")
        for region in regions:
            with self.subTest(region=region[:40]):
                self.assertEqual(pg.replace_between_markers(self.doc(region), ""),
                                 self.doc(""))


# --------------------------------------------------------------------------- input rules


class TestInputRules(TempDirCase):
    def test_ids_that_start_with_a_boundary_keyword(self):
        """mermaid's lexer reads `gantt`, `topAxis` and `inclusiveEndDates` at a word boundary."""
        for bad in ("gantt-1", "topAxis.2", "inclusiveEndDates-3", "GANTT.4", "Gantt"):
            with self.subTest(id=bad):
                with self.assertRaises(pg.PlanError) as ctx:
                    pg.validate_tasks([pg.Task(id=bad, title="t", stage="s", est=1)])
                self.assertIn(f"task {bad}: the id opens a gantt statement", str(ctx.exception))
        for good in ("gantt_1", "gnatt-1", "ganttx", "section-1", "title.2", "topAxisX"):
            with self.subTest(id=good):
                pg.validate_tasks([pg.Task(id=good, title="t", stage="s", est=1)])

    def test_an_id_with_a_line_break_is_refused(self):
        """SEC2-03: the id is matched whole. `$` alone matches before a final line break, so
        `click` plus a line break passed, and its bar line opened a `click` statement."""
        for bad in ("click\n", "dateFormat\n", "B1\n", "B1\n\n", "\nB1", "B1\r"):
            with self.subTest(id=bad):
                with self.assertRaises(pg.PlanError) as ctx:
                    pg.validate_tasks([pg.Task(id=bad, title="t", stage="s", est=1)])
                self.assertIn("id must be a string matching", str(ctx.exception))
        data = chain(8)
        data["tasks"][1]["id"] = "click\n"
        data["tasks"][2]["deps"] = ["click\n"]
        code, out, err = run_cli(str(self.write("plan.json", json.dumps(data))))
        self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
        self.assertIn("id must be a string matching", err)

    def test_stages_that_share_a_section_title_exit_1(self):
        long = "Stage 4: operations, monitoring, alerting and backups for the platform, part"
        for a, b in (("Stage 1: Backend", "Stage 1 — Backend"), ("Ops#", "Ops"),
                     (long + " one", long + " two")):
            data = {"schema": pg.SCHEMA, "tasks": [
                {"id": "T1", "title": "a", "stage": a, "est": 1, "deps": []},
                {"id": "T2", "title": "b", "stage": "Web", "est": 1, "deps": []},
                {"id": "T3", "title": "c", "stage": b, "est": 1, "deps": []}]}
            with self.subTest(stages=(a, b)):
                code, out, err = run_cli(str(self.write("plan.json", json.dumps(data))))
                self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
                self.assertIn(f"stages {a!r} and {b!r} give the same section title", err)

    def test_a_title_or_stage_without_a_drawable_character(self):
        for key, value in (("stage", "#"), ("stage", "\u200b"), ("stage", "# \u200d #"),
                           ("title", "#"), ("title", "\ufeff")):
            data = chain(8)
            data["tasks"][0][key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(pg.PlanError) as ctx:
                    pg.validate_tasks(tasks_of(data))
                self.assertIn(f"task T0: {key} {value!r} holds no drawable character",
                              str(ctx.exception))

    def test_stages_without_a_drawable_character_exit_1_not_2(self):
        data = chain(8)
        for k, t in enumerate(data["tasks"]):
            t["stage"] = "#" if k % 2 else "##"
        code, out, err = run_cli(str(self.write("plan.json", json.dumps(data))))
        self.assertEqual((code, out), (pg.EXIT_FAIL, ""))
        self.assertNotIn("internal error", err)


# --------------------------------------------------------------------------- the document file


class TestDocumentFile(TempDirCase):
    def test_write_keeps_mixed_line_ends_outside_the_region(self):
        """Only the region changes; its lines take the end marker line's line end."""
        lines = markdown_plan(without_status(EXAMPLE)).split("\n")
        at = lines.index(pg.MARKER_END)
        for eol in ("\r\n", "\n"):
            ends = ["\r\n" if k % 3 == 0 else "\n" for k in range(len(lines) - 1)]
            ends[at] = eol
            raw = "".join(line + e for line, e in zip(lines, ends)) + lines[-1]
            with self.subTest(end_marker=repr(eol)):
                plan = self.dir / "PLAN.md"
                plan.write_bytes(raw.encode("utf-8"))
                self.assertEqual(run_cli(str(plan), "--write", str(plan))[0], pg.EXIT_OK)
                new = plan.read_bytes().decode("utf-8")
                head = raw[:raw.index(pg.MARKER_START) + len(pg.MARKER_START)]
                head += ends[lines.index(pg.MARKER_START)]
                tail = raw[raw.index(pg.MARKER_END):]
                self.assertTrue(new.startswith(head))
                self.assertTrue(new.endswith(tail))
                region = new[len(head):len(new) - len(tail)]
                self.assertIn("```mermaid", region)
                rest = region.replace(eol, "")  # every region line ends with the end marker's
                self.assertNotIn("\n", rest)
                self.assertNotIn("\r", rest)
                self.assertEqual(run_cli(str(plan), "--check", str(plan))[0], pg.EXIT_OK)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes a read-only file")
    def test_a_read_only_document_exits_3_and_keeps_its_bytes(self):
        """The rename of `--write` would replace a file its owner made read-only."""
        for data in (without_status(EXAMPLE), chain(3)):
            with self.subTest(tasks=len(data["tasks"])):
                plan = self.write("PLAN.md", markdown_plan(data, region="stale\n"))
                os.chmod(plan, 0o444)
                try:
                    before = self.snapshot()
                    code, _, err = run_cli(str(plan), "--write", str(plan))
                    after = self.snapshot()
                finally:
                    os.chmod(plan, 0o644)
                self.assertEqual(code, pg.EXIT_USAGE)
                self.assertIn("read-only", err)
                self.assertEqual(after, before)


# --------------------------------------------------------------------------- text


class TestUnicodeIndependence(unittest.TestCase):
    """One plan gives one chart on every interpreter, whatever its Unicode version."""

    def test_the_chart_does_not_read_the_unicode_database(self):
        data = chain(8)
        data["tasks"][0]["title"] = "Review \U0001FAE8 step"
        data["tasks"][1]["title"] = "Отчёт 中文 e\u0301 a\u200db"
        for t in data["tasks"][4:]:
            t["stage"] = "Этап 中 \U0001F680"
        before = block_of(data)
        self.assertIn("T0 Review \U0001FAE8 step", before)
        with mock.patch.object(unicodedata, "category", lambda ch: "Cn"), \
                mock.patch.object(unicodedata, "east_asian_width", lambda ch: "N"), \
                mock.patch.object(unicodedata, "combining", lambda ch: 0):
            self.assertEqual(block_of(data), before)

    def test_controls_are_replaced_and_joiners_kept(self):
        self.assertEqual(pg._clean("a\x00b\x85c\u2028d\u202ee\u2066f\ud800g"), "a b c d e f g")
        joined = "a\u200db \U0001F469\u200d\U0001F4BB"
        self.assertEqual(pg._clean(joined), joined)

    def test_the_width_table(self):
        for text, em in (("中", 1.0), ("\U0001FAE8", 1.0), ("가", 1.0), ("ｱ", 0.6),
                         ("e\u0301", 0.6), ("a\u200bb", 1.2), ("Ж—", 1.2)):
            with self.subTest(text=text):
                self.assertAlmostEqual(pg._text_px(text, 10), em * 10)


class TestLabelShortening(TempDirCase):
    """The limit counts `<id> <title>`; the id stays whole, and a cut is reported."""

    def test_a_long_id_keeps_title_characters(self):
        task = pg.Task(id="108.3-stub-renderer-x", title="Implementation of probes", stage="s",
                       est=1)
        self.assertEqual(pg._bar_label(task, 32), "108.3-stub-renderer-x Implement" + pg.ELLIPSIS)

    def test_the_id_is_never_trimmed(self):
        self.assertEqual(pg._fit_label("v2. Orders and more", 3, 0.0, 12), "v2." + pg.ELLIPSIS)
        self.assertEqual(pg._fit_label("v2- Orders", 3, 0.0, 12), "v2-" + pg.ELLIPSIS)
        self.assertEqual(pg._fit_label("T1 Orders and more", 2, 0.0, 12), "T1" + pg.ELLIPSIS)

    def test_a_shortened_label_is_reported(self):
        limit = pg.load_notation()["labels"]["gantt_label_chars_max"]
        data = chain(8)
        data["tasks"][0]["title"] = "Render check for the dark theme"
        code, _, err = run_cli(str(self.write("plan.json", json.dumps(data))))
        self.assertEqual(code, pg.EXIT_OK)
        self.assertIn(f"{pg.WARNING_PREFIX} label of T0 shortened to {limit} characters, its id "
                      "included", err)
        self.assertNotIn("label of T1 ", err)

    def test_an_id_that_leaves_no_room_for_a_title_is_named(self):
        """The id stays whole, so a long id shows no title character, and an id over the limit
        gives a label over the limit. The warning then names the id and states no length."""
        limit = pg.load_notation()["labels"]["gantt_label_chars_max"]
        for size, shows_title in ((limit - 3, True), (limit - 2, False), (limit + 3, False)):
            with self.subTest(id_chars=size):
                tid = "T" + "a" * (size - 1)
                data = chain(8)
                data["tasks"][-1].update(id=tid, title="Render check")
                code, _, err = run_cli(str(self.write("plan.json", json.dumps(data))))
                self.assertEqual(code, pg.EXIT_OK)
                label = pg._bar_label(pg.Task(id=tid, title="Render check", stage="s", est=1),
                                      limit)
                self.assertEqual(label.startswith(f"{tid} R"), shows_title)
                if shows_title:
                    self.assertIn(f"label of {tid} shortened to {limit} characters", err)
                else:
                    self.assertIn(f"{pg.WARNING_PREFIX} label of {tid} shows no title: the id "
                                  f"leaves no room in {limit} characters; shorten the id", err)
                    self.assertNotIn(f"label of {tid} shortened to", err)


class TestProse(unittest.TestCase):
    def test_a_title_opens_no_link_image_or_emphasis(self):
        """A title copied from outside fetches no remote image in the rendered plan."""
        data = without_status(EXAMPLE)
        data["tasks"][0]["title"] = ("![pixel](https://attacker.example/p.png) "
                                     "[docs](javascript:alert(1)) *x* _y_ `z` # <!-- w")
        item = next(line for line in block_of(data).split("\n") if line.startswith("- **B1**"))
        self.assertEqual(item, r"- **B1** \!\[pixel\]\(https://attacker.example/p.png\) "
                               r"\[docs\]\(javascript:alert\(1\)\) \*x\* \_y\_ \`z\` \# "
                               r"&lt;\!-- w — 3 h, slack 1 h")


# --------------------------------------------------------------------------- planner surfaces


REPO = TESTS_DIR.parents[4]
PLANNING_FORMAT = REPO / ".agent/skills/skill-planning-format/SKILL.md"
PLAN_TEMPLATE = REPO / ".agent/skills/skill-planning-format/assets/templates/plan_md_template.md"
PLAN_EXAMPLE = REPO / ".agent/skills/skill-planning-format/examples/PLAN_EXAMPLE.md"
PLANNER_PROMPT = REPO / "System/Agents/06_planner_prompt.md"
PLAN_REVIEWER_PROMPT = REPO / "System/Agents/07_plan_reviewer_prompt.md"
PLAN_REVIEW_CHECKLIST = REPO / ".agent/skills/plan-review-checklist/SKILL.md"
WRITE_COMMAND = ("`python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py "
                 "docs/PLAN.md --write docs/PLAN.md`")


def flat(text):
    return " ".join(text.split()).casefold()


def between(text, first, last=None):
    """The text from the line that starts with *first* up to the next line that starts with
    *last*, or to the end."""
    lines = text.splitlines()
    i = next(k for k, line in enumerate(lines) if line.startswith(first))
    j = next((k for k in range(i + 1, len(lines)) if last and lines[k].startswith(last)),
             len(lines))
    return "\n".join(lines[i:j])


class TestPlannerSurfaces(unittest.TestCase):
    """The planner and plan-reviewer surfaces state what the script does. Text is compared with
    whitespace collapsed and case folded."""

    def read(self, path):
        if not path.is_file():
            self.skipTest(f"{path} is absent: the skill is installed without the framework")
        return path.read_text(encoding="utf-8")

    def test_the_planner_runs_the_generator_for_every_plan(self):
        """A small plan's block is validated before review, not one round later."""
        for path in (PLANNING_FORMAT, PLANNER_PROMPT):
            with self.subTest(path=path.name):
                self.assertIn(flat(f"For every plan, run {WRITE_COMMAND}"), flat(self.read(path)))
        item = between(self.read(PLANNER_PROMPT), "- [ ] **Schedule:**", "- [ ]")
        self.assertIn(flat("At every plan size, does `plan_gantt.py docs/PLAN.md --check "
                           "docs/PLAN.md` exit 0?"), flat(item))

    def test_the_input_rules_are_stated_where_the_planner_reads_them(self):
        """The planner reads §2.1, not the script."""
        text = self.read(PLANNING_FORMAT)
        self.assertIn(f"`{pg.ID_RE.pattern}`", text)
        named = {w.casefold() for w in re.findall(r"`(\w+)`", between(text, "1. Directly under",
                                                                       "2. "))}
        prefixes = re.search(r"\(\?:(.*?)\)", pg.GANTT_KEYWORD_PREFIX_RE.pattern).group(1)
        self.assertLessEqual(set(prefixes.split("|")), named)
        self.assertIn(flat("whole number, at least 1"), flat(text))

    def test_the_id_collision_rule_is_the_rule_of_figure_id(self):
        """`figure_id` maps each `.`, `-` and `_` to `x`, so `x` takes part in a collision; the
        ids §2.1 gives as colliding collide in the script."""
        for c in "._-":
            self.assertEqual(pg.figure_id(f"1{c}1"), pg.figure_id("1x1"))
        item = " ".join(between(self.read(PLANNING_FORMAT), "   - `id`", "   - ").split())
        sentence = next(s for s in re.split(r"(?<=\.)\s", item) if "collide" in s)
        named = set(re.findall(r"`([^`]+)`", sentence))
        self.assertLessEqual({".", "-", "_", "x"}, named, sentence)
        ids = sorted(w for w in named if len(w) > 1 and pg.ID_RE.fullmatch(w))
        self.assertGreaterEqual(len(ids), 2, sentence)
        self.assertTrue(any("x" in i for i in ids), sentence)
        with self.assertRaises(pg.PlanError) as ctx:
            pg.validate_tasks([pg.Task(id=i, title="a", stage="s", est=1) for i in ids])
        self.assertEqual(str(ctx.exception).count("its figure id"), len(ids) - 1)

    def test_without_the_skill_no_plan_size_is_left_out(self):
        """Step 2 runs the script for every plan. The step for a project without the skill
        therefore adds no chart at any plan size, not only from 8 tasks on."""
        steps = between(self.read(PLANNING_FORMAT), "### 2.1", "**Why.**")
        step = " ".join(between(steps, "7. ").split()).casefold()
        self.assertIn("mermaid-authoring-guidelines/", step)
        no_chart = [s for s in re.split(r"(?<=\.)\s", step) if "add no chart" in s]
        self.assertTrue(no_chart, step)
        for sentence in no_chart:
            self.assertNotRegex(sentence, r"\d+ or more tasks|fewer than \d+ tasks")

    def test_the_planner_acts_on_each_warning(self):
        """Every warning exits 0, so the planner reads stderr."""
        for path in (PLANNING_FORMAT, PLANNER_PROMPT):
            with self.subTest(path=path.name):
                self.assertIn(f"`{pg.WARNING_PREFIX}`", self.read(path))

    def test_the_split_is_stored_where_the_planner_reads_it(self):
        """The plain commands stay valid for a split chart."""
        self.assertIn(pg.GROUPS_PREFIX.strip(), self.read(PLANNING_FORMAT))

    def test_the_plan_reviewer_reads_the_chart_evidence(self):
        """The reviewer's loop reads inputs 4 and 5; a project without the skill is not
        rated for following the planner's rule."""
        text = self.read(PLAN_REVIEWER_PROMPT)
        step1 = flat(between(text, "### Step 1", "### Step 2"))
        self.assertIn(flat("`plan-review-checklist` §6 to inputs 4 and 5"), step1)
        major = flat(between(text, "- **MAJOR:**", "- **MINOR:**"))
        self.assertIn(flat("`plan_gantt.py --check` exit 1"), major)
        self.assertIn("plan_gantt.py", flat(between(text, "## 5. QUALITY CHECKLIST")))
        figures = flat(between(self.read(PLAN_REVIEW_CHECKLIST), "## 6. Figures", "## "))
        self.assertIn(flat("`figures` field of the planner's return JSON"), figures)

    def test_an_absent_skill_goes_to_the_figures_field_at_every_plan_size(self):
        """STI-04: the orchestrator stops on `blocking_questions`, so the planner states an
        absent skill in the `figures` field of its return JSON. It does so at every plan size:
        the plan reviewer reads that field to report the chart items *not examined*, which a
        missing check output would otherwise leave *not verified*."""
        prompt = self.read(PLANNER_PROMPT)
        surfaces = {
            "06 Skill absent": between(prompt, "    - **Skill absent:**", "### Step 3"),
            "§2.1 step 7": between(between(self.read(PLANNING_FORMAT), "### 2.1", "**Why.**"),
                                   "7. "),
            "§6 Skill absent": between(self.read(PLAN_REVIEW_CHECKLIST),
                                       "- [ ] **Skill absent:**", "- [ ]"),
        }
        for name, text in surfaces.items():
            with self.subTest(surface=name):
                text = flat(text)
                self.assertIn(flat("`figures` field"), text)
                self.assertNotIn("blocking_questions", text)
                self.assertNotRegex(text, r"\d+ or more tasks|fewer than \d+ tasks")
        fence = re.search(r"\*\*Return Format \(JSON\):\*\*\s*```json\n(.*?)\n```", prompt, re.S)
        self.assertIsNotNone(fence, "06 holds no Return Format (JSON) fence")
        returned = json.loads(fence.group(1))
        self.assertIn("skill absent", returned.get("figures", ""))
        self.assertIn("blocking_questions", returned)
        inputs = flat(between(self.read(PLAN_REVIEWER_PROMPT), "## 3. INPUT DATA", "## 4."))
        self.assertIn(flat("the `figures` field of the planner's return JSON in its place"), inputs)

    def test_the_plan_reviewer_loads_the_skill_for_a_hand_drawn_figure(self):
        """STI-33: the 07 prompt loads the skill before a hand-drawn figure, as the 06 prompt
        does before drawing one. The generated chart needs no load."""
        tier2 = flat(between(self.read(PLAN_REVIEWER_PROMPT), "### Active Skills (TIER 2", "## "))
        for needle in ("`mermaid-authoring-guidelines` → load before you review the first "
                       "hand-drawn figure", "plan chart that `plan_gantt.py` generates needs no "
                       "load"):
            self.assertIn(flat(needle), tier2)

    #: UC-4 A1 for the plan review, word for word; a planted "is false" does not match.
    VERDICT = "The review then does not return APPROVED, and `has_critical_issues` is true."

    def test_a_figure_not_verified_keeps_the_plan_review_from_approved(self):
        """STI-03: every statement of §6 that reports an item or a figure *not verified* carries
        the verdict rule, and so does the reviewer's Step 1."""
        verdict = flat(self.VERDICT)
        step1 = flat(between(self.read(PLAN_REVIEWER_PROMPT), "- **Schedule and chart:**",
                             "### Step 2"))
        self.assertIn(flat("*not verified*"), step1)
        self.assertIn(verdict, step1)
        checklist = self.read(PLAN_REVIEW_CHECKLIST)
        parts = re.split(r"\n(?=- \[ \])", between(checklist, "## 6. Figures", "## "))
        stating = [part for part in parts if "*not verified*" in part]
        self.assertGreaterEqual(len(stating), 2, "§6 intro and **Other figures**")
        for part in stating:
            with self.subTest(part=part.splitlines()[0][:40]):
                self.assertIn(verdict, flat(part))
        gate = flat(between(checklist, "- **Quality Gate:**", "## "))
        self.assertIn(flat("reported *not verified* keeps the review from APPROVED"), gate)

    def test_a_negative_marker_fails_the_plan_review(self):
        """FIG-25: a `%% negative:` line counts only in the skill's own files. The severity the
        item names is the severity the lint gives MA-NEG-03."""
        import lint_mermaid as lm  # imported here: no other test of this file needs the lint
        severity = next(r.severity for r in lm.RULES if r.id == "MA-NEG-03")
        article = "an" if severity[0] in "aeiou" else "a"
        figures = between(self.read(PLAN_REVIEW_CHECKLIST), "## 6. Figures", "## ")
        item = flat(between(figures, "- [ ] **No negative marker:**", "- [ ]"))
        for needle in ("`%% negative:`", "FIG-25"):
            self.assertIn(flat(needle), item)
        self.assertIn(flat(f"MA-NEG-03, {article} {severity}"), item,
                      f"lint_mermaid.py rates MA-NEG-03 {severity!r}; the item must name the same "
                      "severity. Change the rule or the item.")

    def test_the_framework_plans_need_no_shortened_label(self):
        """The example and the template keep `<id> <title>` within the label limit."""
        limit = pg.load_notation()["labels"]["gantt_label_chars_max"]
        for path in (PLAN_TEMPLATE, PLAN_EXAMPLE):
            text = self.read(path).replace("{ID}", "108")
            for t in pg._tasks_from_data(pg._markdown_schedule(text)):
                with self.subTest(path=path.name, task=t.id):
                    self.assertEqual(pg._bar_label(t, limit), pg._clean(f"{t.id} {t.title}"))


# --------------------------------------------------------------------------- rendered geometry


class TestRenderedGeometry(unittest.TestCase):
    """A3: in each render, every bar of the example starts at its computed early start. The
    geometry was read from SVGs of the fence whose sha256 the fixture holds."""

    @classmethod
    def setUpClass(cls):
        cls.geometry = (json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
                        if GEOMETRY_PATH.is_file() else {})
        cls.tasks = pg.load_tasks(EXAMPLE_PATH)
        cls.sched = pg.schedule(cls.tasks)
        cls.block, cls.fence = example_block()

    def assertBound(self):
        if not self.geometry:
            self.fail(f"re-render: {GEOMETRY_PATH.name} is missing. Run: {REGENERATE}")
        digest = mm.fence_sha256(self.fence)
        if digest != self.geometry.get("fence_sha256"):
            self.fail(f"re-render: the fence generated from {EXAMPLE_PATH.name} has sha256 "
                      f"{digest}; {GEOMETRY_PATH.name} holds the geometry of "
                      f"{self.geometry.get('fence_sha256')}. Run: {REGENERATE}")

    def test_the_fixture_is_bound_to_the_generated_fence(self):
        self.assertBound()
        self.assertEqual(self.geometry.get("schema"), GEOMETRY_SCHEMA)
        self.assertEqual(self.geometry.get("source"), EXAMPLE_PATH.name)

    def test_the_renders_are_the_check_pair_and_the_dark_render(self):
        self.assertBound()
        notation = pg.load_notation()
        installs = notation["renderers"]["installs"]
        pair = notation["renderers"]["check_pair"]
        seen = sorted((r["tag"], r["dark"]) for r in self.geometry["renders"])
        self.assertEqual(seen, sorted([(tag, False) for tag in pair] + [(pair[0], True)]))
        for render in self.geometry["renders"]:
            with self.subTest(tag=render["tag"], dark=render["dark"]):
                self.assertEqual(render["mermaid"], installs[render["tag"]]["mermaid"])
                self.assertEqual(render["mermaid_cli"], installs[render["tag"]]["cli"])
                self.assertTrue(render["browser"])
                self.assertEqual((render["status"], render["pass"]), ("ok", True))
        self.assertEqual(self.geometry["render_check"]["exit"], 0)

    def test_every_bar_starts_at_its_early_start(self):
        self.assertBound()
        gantt = init_config(self.fence)["gantt"]
        left, width = gantt["leftPadding"], gantt["useWidth"]
        lo = min(self.sched.es.values())
        span = max(self.sched.ef.values()) - lo
        px_per_hour = (width - left - gantt["rightPadding"]) / span
        for render in self.geometry["renders"]:
            label = render["tag"] + (" dark" if render["dark"] else "")
            with self.subTest(render=label):
                self.assertEqual(render["width"], width, f"{label}: useWidth is not honoured")
                bars = render["bars"]
                self.assertEqual(set(bars), {pg.figure_id(t.id) for t in self.tasks})
                for t in self.tasks:
                    bar = bars[pg.figure_id(t.id)]
                    hour = lo + (bar["x"] - left) / px_per_hour
                    self.assertEqual(round(hour), self.sched.es[t.id],
                                     f"{label}: bar {t.id} starts at hour {hour:.2f}; its early "
                                     f"start is hour {self.sched.es[t.id]}")
                    expected_x = left + (self.sched.es[t.id] - lo) * px_per_hour
                    self.assertLessEqual(abs(bar["x"] - expected_x), 1.0,
                                         f"{label}: bar {t.id} x = {bar['x']}, computed "
                                         f"{expected_x:.1f}")
                    self.assertLessEqual(abs(bar["width"] - t.est * px_per_hour), 1.0,
                                         f"{label}: bar {t.id} is {bar['width']} px wide for "
                                         f"{t.est} h")

    def test_b4_waits_for_a_task_declared_below_it(self):
        """The case `after` gets wrong (gantt.md G1): B4 waits for O2, declared below it."""
        self.assertBound()
        self.assertEqual(self.sched.es["B4"], self.sched.ef["O2"])
        self.assertGreater(self.sched.ef["O2"], self.sched.ef["B3"])
        for render in self.geometry["renders"]:
            bars = render["bars"]
            self.assertGreater(bars["tB4"]["x"], bars["tB3"]["x"] + bars["tB3"]["width"])
            self.assertAlmostEqual(bars["tB4"]["x"], bars["tO2"]["x"] + bars["tO2"]["width"],
                                   delta=1.0)


# --------------------------------------------------------------------------- fixture upkeep


def _number(value: float):
    return int(value) if float(value).is_integer() else round(value, 3)


def bars_of_svg(svg_text: str):
    """Return `(width, height, {figure id: {"x", "width"}})` of a rendered gantt: the size of
    its viewBox and every bar `rect`, its x moved by the translations of its ancestors."""
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(svg_text)
    box = [float(v) for v in re.split(r"[\s,]+", (root.get("viewBox") or "").strip()) if v]
    if len(box) != 4:
        raise ValueError("the SVG has no viewBox")
    prefix = (root.get("id") or "") + "-"
    bars = {}

    def walk(el, dx):
        own = el.get("transform")
        if own:
            m = re.fullmatch(r"\s*translate\(\s*([-+\d.eE]+)(?:[\s,]+([-+\d.eE]+))?\s*\)\s*", own)
            if not m:
                raise ValueError(f"a transform other than a translation: {own!r}")
            dx += float(m.group(1))
        if el.tag == ns + "rect" and "task" in (el.get("class") or "").split():
            ident = el.get("id") or ""
            if prefix != "-" and ident.startswith(prefix):
                ident = ident[len(prefix):]
            if ident in bars:
                raise ValueError(f"two bars with the id {ident}")
            bars[ident] = {"x": _number(float(el.get("x")) + dx),
                           "width": _number(float(el.get("width")))}
        for child in el:
            walk(child, dx)

    walk(root, 0.0)
    return _number(box[2]), _number(box[3]), bars


def dump_geometry(geometry: dict) -> str:
    """The fixture as JSON with one line per bar, so a diff shows one bar per changed line."""
    text = json.dumps(geometry, indent=1, ensure_ascii=False)
    return re.sub(r'\{\n\s*"x": ([-\d.]+),\n\s*"width": ([-\d.]+)\n\s*\}',
                  r'{"x": \1, "width": \2}', text) + "\n"


def regenerate_geometry(out_dir) -> int:
    """Render the example block with `render_check.py --json` and rewrite GEOMETRY_PATH.

    Needs node, the pinned renderers and a browser; no test calls it. *out_dir* receives the
    block and the renders and must lie outside every git work tree. Returns 0 when the fixture
    is written; otherwise the exit code of render_check.py, or 3 for a bad *out_dir*, or 2 when
    the renders do not match the fence, and the fixture stays as it was.
    """
    import render_check as rc  # stdlib only; imported here so the tests never load it

    out_dir = Path(out_dir).expanduser().absolute()
    if rc.inside_git_work_tree(out_dir):
        print(f"{out_dir} lies inside a git work tree; renders stay outside every repository",
              file=sys.stderr)
        return 3
    out_dir.mkdir(parents=True, exist_ok=True)
    block, fence = example_block()
    source = out_dir / "plan-example.md"
    source.write_text(f"{pg.MARKER_START}\n\n{block}\n\n{pg.MARKER_END}\n", encoding="utf-8")
    run = subprocess.run([sys.executable, str(RENDER_CHECK), str(source), "--json",
                          "--out", str(out_dir / "renders")],
                         capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        sys.stderr.write(run.stderr)
        print(f"render_check.py exited {run.returncode}; {GEOMETRY_PATH.name} is unchanged",
              file=sys.stderr)
        return run.returncode
    report = json.loads(run.stdout)
    figures = [f for src in report["inputs"] for f in src["figures"]]
    if len(figures) != 1:
        print(f"render_check.py found {len(figures)} figures, not 1", file=sys.stderr)
        return 2
    renders = []
    for r in figures[0]["renders"]:
        svg = Path(r["svg"])
        rendered = svg.with_suffix(".mmd").read_text(encoding="utf-8")
        if rendered != fence + "\n":
            print(f"{svg.with_suffix('.mmd')} is not the generated fence", file=sys.stderr)
            return 2
        width, height, found = bars_of_svg(svg.read_text(encoding="utf-8"))
        order = [pg.figure_id(t["id"]) for t in EXAMPLE["tasks"]]
        bars = {k: found[k] for k in order if k in found}
        bars.update((k, v) for k, v in found.items() if k not in bars)
        renders.append({"tag": r["tag"], "dark": r["dark"], "mermaid": r.get("mermaid"),
                        "mermaid_cli": r.get("mermaid_cli"), "browser": r.get("browser"),
                        "status": r.get("status"), "pass": r.get("pass"),
                        "findings": len(r.get("findings") or []), "width": width,
                        "height": height, "bars": bars})
    geometry = {
        "schema": GEOMETRY_SCHEMA,
        "source": EXAMPLE_PATH.name,
        "fence_sha256": mm.fence_sha256(fence),
        "fence_text": "mermaid_model.fence_sha256 of the fence body plan_gantt.py generates from "
                      "the source: its lines, each ended by LF, in UTF-8; the text render_check.py "
                      "renders",
        "rendered": time.strftime("%Y-%m-%d"),
        "render_check": {"exit": run.returncode, "status": report["inputs"][0]["status"]},
        "regenerate": REGENERATE,
        "renders": renders,
    }
    GEOMETRY_PATH.write_text(dump_geometry(geometry), encoding="utf-8")
    print(f"{GEOMETRY_PATH}: {len(renders)} renders written; renders in {out_dir}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--regenerate-geometry":
        sys.exit(regenerate_geometry(sys.argv[2]))
    unittest.main()
