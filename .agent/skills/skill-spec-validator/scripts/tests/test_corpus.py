"""Corpus anti-drift tests for skill-spec-validator (TASK 092 / R9-R11).

Why these exist, and why unit fixtures alone are not enough (WI-1): both
matchers in `validate.py` had drifted away from the convention this repo
actually writes, and failed on 100% of shipped artifacts across ≥2 prior
"fixes" — silently, because a gate that never passes looks exactly like a gate
nobody tripped. Fixture-only tests would not have caught it: the next author to
re-tighten the regex would have updated the fixtures to match their new idea of
the convention.

So these tests are anchored to the ARTIFACTS, not to strings invented here:

  * R9  — an independent, deliberately loose probe finds every RTM-ish heading
          in `docs/tasks/`; `RTM_HEADER` must match every one of them. Finding
          no headings at all is a FAILURE, not a green run (a discovery pass
          that discovers nothing is the same trap in miniature).
  * R10 — liveness floors: a minimum number of shipped tasks/plan-pairs must
          still pass end to end. A matcher that dies again collapses these to
          roughly zero.

The floors are CANARIES, not targets — set below the counts measured when this
suite was written (2026-07-30: 20 tasks, 14 pairs) so that ordinary artifact
churn never turns the suite red, while a dead gate always does. Raising a floor
to "lock in" a better number would make every future non-conforming task the
suite's problem instead of the reviewer's.

Portability (R11): the corpus lives in the framework repo. Once this skill is
installed into a consumer project the corpus is absent, so these tests SKIP
rather than fail — a skipped corpus test is honest, a failing one would train
people to ignore the suite.
"""
import functools  # noqa: E402
import re  # noqa: E402
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

validate = fx.validate

#: measured 2026-07-30 at 20 passing tasks / 14 passing pairs; see module docstring
MIN_TASKS_PASSING = 15
MIN_PLAN_PAIRS_PASSING = 10
MIN_RTM_HEADINGS_FOUND = 15

#: **Strictly wider than `RTM_HEADER`, by design.** The first version of this
#: probe required `requirements traceability` or a literal `(rtm)` — i.e. a
#: SUBSET of what the matcher accepts — so "every probed heading matches" was
#: true by construction and the test could only fail if someone NARROWED the
#: matcher (vdd-multi F8). It could not see the corpus drifting to a shape
#: neither regex knew, which is the drift it exists to catch. This version keys
#: on the `trace*` / `rtm` stems ALONE, in any wording. `RTM_HEADER` needs the
#: PHRASE `Requirements Traceability` or a bare `\bRTM\b`; this probe accepts
#: `trace*` on its own, so `## Traceability Matrix` (a plausible drift) is
#: probed and would FAIL the assertion below — which is the information the
#: first version lacked. The bare `requirements?` stem is deliberately NOT here:
#: it matched `## 3. Non-functional Requirements`, i.e. over-matching would have
#: turned this guard into noise instead of a signal.
LOOSE_PROBE = re.compile(
    r"^#{2,4}\s+.*\b(?:trace\w*|rtm)\b.*$",
    re.MULTILINE | re.IGNORECASE)

#: shape = the heading with hashes and any `N.`/`N)` section number stripped, so
#: `### 2. Requirements (RTM)` and `### 3. Requirements (RTM)` are ONE shape
#: (F9: counting raw strings meant section-number churn satisfied the floor,
#: and normalizing the corpus to one canonical heading would have turned the
#: suite red for a *good* cleanup)
_SHAPE_STRIP_RE = re.compile(r"^#{2,4}\s+(?:\d+(?:\.\d+)*[.)]?\s+)?")


def heading_shape(heading):
    return _SHAPE_STRIP_RE.sub("", heading.strip()).strip().lower()


#: Corpus headings that mention the RTM but are NOT an RTM section, so
#: `RTM_HEADER` is RIGHT to ignore them. Declared explicitly rather than hidden
#: behind a narrower probe: the whole point of the wide probe is that a NEW
#: unmatched shape must show up as a failure, and the reviewer then decides
#: whether it is corpus drift (widen the matcher) or prose (extend this set).
#: Currently one entry — a section of `task-050-hardening-quality.md` discussing
#: the analysis phase, not tabulating requirements.
KNOWN_NON_RTM_SHAPES = frozenset({
    'analysis phase: the "traceability matrix"',
})

BYPASS = "[BYPASS_" + "VALIDATION]"


def find_repo_root():
    """The framework checkout, or None when installed into a consumer repo."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "docs" / "tasks").is_dir() and (candidate / ".git").exists():
            return candidate
    return None


REPO_ROOT = find_repo_root()
requires_corpus = unittest.skipIf(
    REPO_ROOT is None,
    "framework corpus (docs/tasks) not present — skill installed standalone")


@functools.lru_cache(maxsize=1)
def _corpus():
    """[(path, text)] for the task corpus — read ONCE per process.

    Without the memo `probed_headings()` re-read all 111 files once per test
    method (~431 opens, ~1.65 MB per 36-test run, each file opened up to 6×) and
    the cost grew linearly with a corpus this repo extends every task
    (vdd-multi M-03).
    """
    out = []
    for path in sorted((REPO_ROOT / "docs" / "tasks").glob("*.md")):
        try:
            out.append((path, path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return tuple(out)


def probed_headings():
    """[(path, heading_line)] for every RTM-ish heading in the task corpus."""
    return [(path, heading.strip())
            for path, text in _corpus()
            for heading in LOOSE_PROBE.findall(text)]


@requires_corpus
class TestHeadingMatcherAgainstTheCorpus(unittest.TestCase):
    """R9."""

    def test_probe_finds_a_real_corpus(self):
        found = probed_headings()
        self.assertGreaterEqual(
            len(found), MIN_RTM_HEADINGS_FOUND,
            "the loose probe found %d RTM headings in docs/tasks/ — either the "
            "corpus moved or the probe broke; a discovery run that discovers "
            "nothing must never read as green" % len(found))
        # Shape COUNT is reported, never asserted: a floor here would turn the
        # suite red if the corpus were ever canonicalized to one heading — i.e.
        # it would penalize a good cleanup (vdd-multi iteration 2, V6). What
        # matters is that the matcher covers whatever shapes exist, which is the
        # next test's job.
        shapes = {heading_shape(h) for _, h in found}
        self.assertGreaterEqual(len(shapes), 1, "no RTM heading shapes at all")

    def test_rtm_header_matches_every_shipped_rtm_heading(self):
        """Drift detector: every `trace*`/`rtm` heading in the corpus is either
        matched by the gate or an explicitly declared non-RTM mention."""
        unmatched = sorted(
            {(str(p.relative_to(REPO_ROOT)), h) for p, h in probed_headings()
             if not validate.RTM_HEADER.search(h + "\n")
             and heading_shape(h) not in KNOWN_NON_RTM_SHAPES})
        self.assertEqual(
            unmatched, [],
            "a heading naming traceability/RTM is not matched by RTM_HEADER — "
            "this is exactly the drift WI-1 was filed for. If it IS an RTM "
            "section, widen the matcher (never narrow the corpus); if it is "
            "prose, add its shape to KNOWN_NON_RTM_SHAPES so the exclusion is "
            "visible in review.")

    def test_the_declared_non_rtm_exclusions_are_still_real(self):
        """An allow-list that outlives its entries silently widens itself."""
        live = {heading_shape(h) for _, h in probed_headings()}
        self.assertEqual(
            KNOWN_NON_RTM_SHAPES - live, frozenset(),
            "KNOWN_NON_RTM_SHAPES names shapes no longer in the corpus — drop "
            "them, or the exclusion covers something nobody reviewed.")


class TestNeverNarrowed(unittest.TestCase):
    """Deliberately NOT `@requires_corpus`: this pin needs no corpus, and a
    consumer install (where the corpus tests skip) is exactly where a narrowing
    would otherwise go unnoticed (vdd-multi iteration 2, V5)."""

    def test_no_currently_matched_shape_is_ever_dropped(self):
        """Regression pin against the historical failure: the matcher was
        narrowed twice. These shapes are DATA taken from the corpus, so this
        assertion cannot become a tautology of the regex it guards."""
        must_match = (
            # the two most common corpus shapes, both missing from the first
            # version of this pin — see test_validate.SHIPPED (V5)
            "## RTM (acceptance criteria)",
            "## 2. RTM",
            "## Requirements Traceability",
            "## Requirements Traceability Matrix (RTM)",
            "## 2. Requirements Traceability Matrix (RTM)",
            "### 2. Requirements Traceability Matrix (RTM)",
            "### 2. Requirements (RTM)",
            "#### Requirements (RTM)",
            "## 6. Acceptance Criteria (Requirements Traceability Matrix)",
            "## 5. Acceptance Criteria (RTM)",
        )
        broken = [h for h in must_match
                  if not validate.RTM_HEADER.search(h + "\n")]
        self.assertEqual(broken, [], "RTM_HEADER was narrowed: %r" % broken)


@requires_corpus
class TestGateLivenessOnTheCorpus(unittest.TestCase):
    """R10 — the gate must still PASS on real artifacts, not merely match."""

    def test_task_mode_still_passes_on_shipped_tasks(self):
        candidates = {p for p, _ in probed_headings()}
        texts = dict(_corpus())  # already in memory — do not re-open (M-03)
        passing = []
        for path in sorted(candidates):
            if BYPASS in texts.get(path, ""):
                continue  # a bypassed file proves nothing about the matcher
            code, _out = fx.run(validate.validate_task, str(path))
            if code == 0:
                passing.append(path.name)
        self.assertGreaterEqual(
            len(passing), MIN_TASKS_PASSING,
            "only %d shipped tasks pass --mode task (floor %d). A gate that "
            "cannot pass on the artifacts it governs is not a gate."
            % (len(passing), MIN_TASKS_PASSING))

    def test_plan_mode_still_passes_on_shipped_pairs(self):
        plans_dir, tasks_dir = REPO_ROOT / "docs" / "plans", REPO_ROOT / "docs" / "tasks"
        passing = []
        for plan in sorted(plans_dir.glob("plan-*.md")):
            # exact-slug pairing: `plan-091-x.md` <-> `task-091-x.md`, so a
            # sub-task file (task-091-02-x.md) is never mispaired with a parent
            task = tasks_dir / ("task-" + plan.name[len("plan-"):])
            if not task.is_file():
                continue
            code, _out = fx.run(validate.validate_plan, str(plan), str(task))
            if code == 0:
                passing.append(plan.name)
        self.assertGreaterEqual(
            len(passing), MIN_PLAN_PAIRS_PASSING,
            "only %d plan/task pairs pass --mode plan (floor %d) — the ID "
            "coverage matcher has probably drifted again."
            % (len(passing), MIN_PLAN_PAIRS_PASSING))


if __name__ == "__main__":
    unittest.main()
