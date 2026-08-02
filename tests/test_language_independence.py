"""Language independence of framework tooling (TASK 095 / WI-30, generalized).

WI-30 reported ONE language-coupled gate. A sweep found the same defect class in
three more places, one of them silent. These tests pin the class, not the single
instance, so the next tool that reaches for an English word in an authored
document has a test to fail against.

The class, per `documentation-standards` §4.3: a machine that keys on the prose
of a document it did not write is asserting that the document is in a particular
language — an assertion nobody made and it cannot check.

Two failure shapes, and the quiet one is worse:

  * LOUD  — `exit 1` on a perfectly good document. The author rewrites it in a
    language they do not use, or stops running the step; a step that can be
    quietly skipped is indistinguishable from one that passed.
  * SILENT — a non-latin slug normalizes to `"untitled"`, so two different
    documents resolve to ONE filename and the second overwrites the first.
    Nothing reports it. This is the one nobody had filed.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".agent" / "tools"))

import task_id_tool  # noqa: E402


class TestSlugsDoNotSilentlyCollapse:
    """`.agent/tools/task_id_tool.py` — the silent one.

    `normalize_slug` strips every non-`[a-z0-9-]` character and then falls back
    to the literal `"untitled"`. For any non-latin title the strip removes
    everything, so the fallback fires — and it fires with the SAME value every
    time. Measured before the fix: `task_id_tool.py "реестр-инструментов"` and
    `task_id_tool.py "единый-реестр"` both returned `task-095-untitled.md`.
    """

    def test_a_non_latin_slug_does_not_become_untitled(self):
        assert task_id_tool.normalize_slug("реестр-инструментов") != "untitled"

    def test_two_different_non_latin_slugs_do_not_collide(self):
        a = task_id_tool.normalize_slug("реестр-инструментов")
        b = task_id_tool.normalize_slug("единый-реестр")
        assert a != b, (
            "two different titles normalized to the same slug %r — this is a "
            "silent overwrite in docs/tasks/, not a cosmetic naming issue" % a)

    def test_the_result_is_still_a_safe_filename_stem(self):
        """Whatever the transliteration, the output must stay filename-safe:
        the slug becomes a path component, so a stray `/`, space, or dot is a
        different (and worse) bug than the one being fixed."""
        import re
        for title in ("реестр-инструментов", "Отчёт по задаче №5",
                      "ЕДИНЫЙ Реестр", "混合 chars ここ"):
            slug = task_id_tool.normalize_slug(title)
            assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), \
                "unsafe slug %r from %r" % (slug, title)

    def test_latin_slugs_are_completely_unchanged(self):
        """The regression guard. Every existing archived task was named by this
        function; a change in its latin behaviour would silently re-slug the
        corpus."""
        for raw, expected in (
            ("New Feature", "new-feature"),
            ("my_task", "my-task"),
            ("  Multiple   Spaces  ", "multiple-spaces"),
            ("UPPER-case", "upper-case"),
            ("a--b", "a-b"),
            ("weird!@#chars", "weirdchars"),
        ):
            assert task_id_tool.normalize_slug(raw) == expected, raw

    def test_a_genuinely_empty_slug_still_falls_back(self):
        assert task_id_tool.normalize_slug("") == "untitled"
        assert task_id_tool.normalize_slug("!!!") == "untitled"


class TestWsjfReadsColumnsStructurally:
    """`skill-product-backlog-prioritization/scripts/calculate_wsjf.py`.

    Same defect as the reported one, in a file nobody filed against: the four
    WSJF inputs are matched by exact English string against the header cells of
    an AUTHORED backlog table, so a Russian `PRODUCT_BACKLOG.md` exits 1 with
    "No valid Backlog table found".
    """

    @pytest.fixture()
    def wsjf(self):
        import importlib.util
        path = (REPO_ROOT / ".agent/skills/skill-product-backlog-prioritization"
                / "scripts/calculate_wsjf.py")
        spec = importlib.util.spec_from_file_location("calculate_wsjf", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_english_headers_still_resolve(self, wsjf):
        headers = ['ID', 'User Value', 'Time Criticality', 'Risk Reduction',
                   'Job Size', 'WSJF']
        mapping, missing = wsjf.get_column_indices(headers)
        assert missing == []
        assert mapping['User Value'] == 1 and mapping['Job Size'] == 4

    def test_bolded_english_headers_still_resolve(self, wsjf):
        headers = ['ID', '**User Value**', '**Time Criticality**',
                   '**Risk Reduction**', '**Job Size**']
        _mapping, missing = wsjf.get_column_indices(headers)
        assert missing == []

    def test_non_english_headers_resolve_by_position(self, wsjf):
        """The structural contract: the four WSJF inputs are the four columns
        following the id column, in the documented order. Column NAMES are
        prose and carry no contract."""
        headers = ['ИД', 'Ценность', 'Срочность', 'Снижение риска', 'Объём работ']
        mapping, missing = wsjf.get_column_indices(headers)
        assert missing == [], "non-English backlog rejected: %r" % missing
        assert mapping['User Value'] == 1
        assert mapping['Time Criticality'] == 2
        assert mapping['Risk Reduction'] == 3
        assert mapping['Job Size'] == 4

    def test_a_table_that_is_genuinely_wrong_is_still_rejected(self, wsjf):
        """Positional fallback must not become a rubber stamp: a table with
        too few columns has no WSJF inputs at all, in any language."""
        _mapping, missing = wsjf.get_column_indices(['ИД', 'Ценность'])
        assert missing, "a 2-column table was accepted as a WSJF backlog"


class TestArchiveProtocolDerivesSlugsTheSameWay:
    """`.agent/tools/archive_protocol.py` — the second half of the silent one.

    Archiving derives a slug in TWO places of its own — from the `| Slug |`
    meta row, and from the H1 title when there is no meta table — each with its
    own private character class, neither of which survives a non-latin title.
    Both then fall through to the same literal `"untitled"` as `task_id_tool`
    did, so the collision reappears on the archive path even once the tool is
    fixed.

    Three private implementations of one rule is the shape WI-32 describes:
    the fix is one declaration with readers, not three synchronized copies.
    These tests assert the DELEGATION, so a future fourth copy fails here.
    """

    @pytest.fixture()
    def ap(self):
        import importlib.util
        path = REPO_ROOT / ".agent/tools/archive_protocol.py"
        spec = importlib.util.spec_from_file_location("archive_protocol", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_slug_from_a_non_latin_meta_row_is_not_lost(self, ap):
        content = (
            "# Задача\n\n## 0. Meta\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Task ID | 042 |\n| Slug | единый-реестр |\n"
        )
        meta = ap.parse_task_meta(content)
        assert meta.get("slug"), "non-latin Slug row was dropped entirely"
        assert meta["slug"] != "untitled"

    def test_slug_from_a_non_latin_h1_title_is_not_lost(self, ap):
        """No meta table -> the H1 title is the fallback source."""
        meta = ap.parse_task_meta("# Реестр инструментов\n\nТекст.\n")
        assert meta.get("slug"), "non-latin H1 produced an empty slug"
        assert meta["slug"] != "untitled"

    def test_two_different_non_latin_titles_archive_to_different_names(self, ap):
        a = ap.parse_task_meta("# Реестр инструментов\n")["slug"]
        b = ap.parse_task_meta("# Единый реестр\n")["slug"]
        assert a != b, "both titles archive to %r — silent overwrite" % a

    def test_it_delegates_rather_than_reimplementing(self, ap):
        """The point is one rule, not three that agree today."""
        assert ap.parse_task_meta("# Единый реестр\n")["slug"] == \
            task_id_tool.normalize_slug("Единый реестр")

    def test_latin_behaviour_is_unchanged(self, ap):
        """Both meta-section markers keep working, and so does the H1 fallback.

        The English `Meta Information` probe is exercised alongside the anchor
        on purpose: it is the only thing every TASK.md written before this
        change has, so a regression there would break archiving for the whole
        existing corpus while the new tests stayed green.
        """
        for marker in ("## 0. Meta Information", "<!-- contract:meta -->"):
            content = ("# T\n\n%s\n\n| Field | Value |\n|---|---|\n"
                       "| Task ID | 042 |\n| Slug | existing-feature |\n" % marker)
            meta = ap.parse_task_meta(content)
            assert meta["has_meta"] is True, marker
            assert meta["task_id"] == "042", marker
            assert meta["slug"] == "existing-feature", marker

        # No marker at all -> H1 fallback, unchanged for latin titles.
        no_meta = ap.parse_task_meta("# New Feature Work\n")
        assert no_meta["has_meta"] is False
        assert no_meta["slug"] == "new-feature-work"


class TestPositionalFallbackNeedsStructuralEvidence:
    """The guard on the fallback added by TestWsjfReadsColumnsStructurally.

    Filed by a reviewing agent against TASK 095, and correct: the first version of
    the positional fallback fired on ANY row of >= 5 cells, because with no English
    names to recognize there was nothing left telling it a row was a header at all.
    A lone `| Bad | 1 | 1 | 1 | 0 | 0 |` was therefore consumed AS the header row,
    leaving zero data rows, and the script exited 0 — a malformed backlog turned
    into a silent success. That is the same class of defect the language fix exists
    to remove, reintroduced one layer down.

    The structural evidence is the markdown separator row (`|---|---|`) that follows
    a header. The English path gets the equivalent for free by recognizing its
    column names; the positional path has to ask for it.
    """

    @pytest.fixture()
    def wsjf(self):
        import importlib.util
        path = (REPO_ROOT / ".agent/skills/skill-product-backlog-prioritization"
                / "scripts/calculate_wsjf.py")
        spec = importlib.util.spec_from_file_location("calculate_wsjf_guard", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _run(self, wsjf, tmp_path, content):
        """Drive main() over a backlog file; return its exit code."""
        import sys
        from unittest.mock import patch
        p = tmp_path / "BACKLOG.md"
        p.write_text(content, encoding="utf-8")
        with patch.object(sys, "argv", ["calculate_wsjf.py", "--file", str(p)]):
            try:
                wsjf.main()
            except SystemExit as exc:
                return exc.code if exc.code is not None else 0
        return 0

    def test_a_headerless_row_is_not_accepted_as_a_header(self, wsjf, tmp_path):
        """The exact regression: no separator row -> no positional fallback."""
        code = self._run(wsjf, tmp_path, "| Bad | 1 | 1 | 1 | 0 | 0 |\n")
        assert code == 1, "a headerless row was accepted as a WSJF backlog"

    def test_job_size_zero_is_rejected_in_a_wellformed_english_table(self, wsjf, tmp_path):
        """The protection `test_product_scripts.py::test_job_size_zero_protection`
        names, now actually reached.

        `calculate_wsjf.py` used to read `if js == 0: js = 1  # Avoid div by zero`,
        so a row sized 0 was silently rescored against a denominator nobody wrote:
        (8+5+3)/0 came out as 16.0 and sorted to the top of the backlog, looking
        exactly like a real 16. The named test asserted exit 1 and passed the whole
        time on an unrelated path — its fixture is a headerless row, rejected
        earlier as a malformed table — so the guard had never run.
        """
        code = self._run(wsjf, tmp_path,
            "| ID | User Value | Time Criticality | Risk Reduction | Job Size | WSJF |\n"
            "|----|-----------|------------------|----------------|----------|------|\n"
            "| A1 | 8 | 5 | 3 | 0 | |\n")
        assert code == 1, "Job Size = 0 was scored instead of refused"

    def test_job_size_zero_is_rejected_on_the_positional_path_too(self, wsjf, tmp_path):
        """The non-English path added by TASK 095 gets the same guard — a fix that
        held on one of two paths is the half-applied shape this task is about."""
        code = self._run(wsjf, tmp_path,
            "| ИД | Ценность | Срочность | Снижение риска | Объём работ | WSJF |\n"
            "|----|----------|-----------|----------------|-------------|------|\n"
            "| A1 | 8 | 5 | 3 | 0 | |\n")
        assert code == 1, "Job Size = 0 slipped through the positional path"

    def test_the_backlog_is_not_rewritten_when_a_row_is_refused(self, wsjf, tmp_path):
        """Refusing must not leave the file half-scored: the caller re-runs after
        fixing the row, and a partially rewritten backlog would make that ambiguous."""
        content = (
            "| ID | User Value | Time Criticality | Risk Reduction | Job Size | WSJF |\n"
            "|----|-----------|------------------|----------------|----------|------|\n"
            "| A1 | 8 | 5 | 3 | 2 | |\n"
            "| A2 | 4 | 4 | 4 | 0 | |\n")
        code = self._run(wsjf, tmp_path, content)
        assert code == 1
        assert (tmp_path / "BACKLOG.md").read_text(encoding="utf-8") == content, \
            "the backlog was modified despite the run being refused"

    def test_a_wellformed_non_english_backlog_still_succeeds(self, wsjf, tmp_path):
        """The guard must not have cost the feature it guards."""
        code = self._run(wsjf, tmp_path,
            "| ИД | Ценность | Срочность | Снижение риска | Объём работ | WSJF |\n"
            "|----|----------|-----------|----------------|-------------|------|\n"
            "| A1 | 8 | 5 | 3 | 2 | |\n")
        assert code == 0
