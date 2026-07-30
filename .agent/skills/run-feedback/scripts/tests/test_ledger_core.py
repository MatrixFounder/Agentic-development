"""The guard inventory — every ledger guard, exercised against BOTH registries.

This is the instrument that makes "fixed on one path only" structurally impossible
to reintroduce. Writer asymmetry produced a confirmed defect in every adversarial
iteration over this code (WI-23; iteration 2's V12; iteration 3's L-1, L-2, L-4,
L-5, L-6, H-04), so after the `ledger_core` extraction the question is no longer
"does this guard exist" but "does it exist for both registries".

**Each case records WHICH registry refused** (audit 094 Required Action 1). A test
that only asserted "some registry refused" would pass with a guard live on one path
and a coincidental failure on the other — the same blind spot as the hazard it is
meant to pin. `assertRefusedByBoth` therefore collects a per-registry verdict and
reports the asymmetry explicitly when one side lets something through.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import (frontmatter, ledger_backlog, ledger_core,  # noqa: E402
                          ledger_issues)
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"


class GuardInventory(unittest.TestCase):
    """Fresh repo per test; both registries seeded and independently fileable."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.backlog = fx.write(self.root / "docs" / "BACKLOG.md",
                                fx.BACKLOG_INDEX_FIXTURE)
        self.index = fx.write(self.root / "docs" / "KNOWN_ISSUES.md",
                              fx.INDEX_FIXTURE)
        self.records = self.root / "docs" / "backlog"
        self.records.mkdir(parents=True, exist_ok=True)
        self.issues = self.root / "docs" / "issues"
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        self.cfg = fx.load_cfg(self.root)

    # --- the two registries behind one calling convention -------------------

    def registries(self):
        """[(name, filer, record_dir, index_path)] — filer takes **overrides."""
        return [
            ("work-items", self._file_work_item, self.records, self.backlog),
            ("defects", self._file_defect, self.issues, self.index),
        ]

    def _file_work_item(self, **kw):
        kw.setdefault("item_id", "WI-9")
        kw.setdefault("slug", "wi-9-item")
        kw.setdefault("title", "An item")
        kw.setdefault("body", fx.DEFECT_BODY)
        kw.setdefault("opened_at", "2026-07-30")
        kw.pop("category", None)
        rank = kw.pop("rank", None)
        if rank is not None:
            kw["effort"] = rank
        return ledger_backlog.file_work_item(self.cfg, **kw)

    def _file_defect(self, **kw):
        kw.setdefault("issue_id", "RF-9")
        kw.setdefault("slug", "rf-9-issue")
        kw.setdefault("title", "An issue")
        kw.setdefault("category", "robustness")
        kw.setdefault("body", fx.DEFECT_BODY)
        kw.setdefault("opened_at", "2026-07-30")
        rank = kw.pop("rank", None)
        if rank is not None:
            kw["severity"] = rank
        return ledger_issues.file_defect(self.cfg, **kw)

    def assertRefusedByBoth(self, guard, prepare=None, **overrides):
        """Assert both registries refuse, and say which one did not.

        *prepare* runs per registry with (record_dir, index_path) before filing —
        for guards that need something planted on disk first.
        """
        verdicts = {}
        for name, filer, record_dir, index_path in self.registries():
            if prepare is not None:
                prepare(record_dir, index_path)
            try:
                filer(**overrides)
                verdicts[name] = None
            except CliError as exc:
                verdicts[name] = exc
        missing = [name for name, exc in verdicts.items() if exc is None]
        self.assertEqual(
            missing, [],
            "guard %r did not fire for %s (it DID for %s) — a guard present on "
            "one registry and absent on the other is the exact defect class the "
            "ledger_core extraction exists to remove"
            % (guard, ", ".join(missing),
               ", ".join(n for n, e in verdicts.items() if e is not None)))
        return verdicts

    # --- vocabulary ---------------------------------------------------------

    def test_status_outside_the_write_vocabulary(self):
        self.assertRefusedByBoth("status vocab", status="handled")

    def test_rank_outside_the_write_vocabulary(self):
        """`effort` for work-items, `severity` for defects — one guard, two names."""
        self.assertRefusedByBoth("rank vocab", rank="ENORMOUS")

    # --- create-only + symlink (S-03) --------------------------------------

    def test_an_existing_record_path_is_refused_by_the_precheck(self):
        def plant(record_dir, _index):
            record_dir.mkdir(parents=True, exist_ok=True)
            for slug in ("wi-9-item", "rf-9-issue"):
                fx.write(record_dir / (slug + ".md"), "taken\n")

        verdicts = self.assertRefusedByBoth("lexists pre-check", prepare=plant)
        for name, exc in verdicts.items():
            self.assertIn("already exists", str(exc), name)

    def test_a_dangling_symlink_at_the_record_path_is_refused(self):
        def plant(record_dir, _index):
            record_dir.mkdir(parents=True, exist_ok=True)
            for slug in ("wi-9-item", "rf-9-issue"):
                link = record_dir / (slug + ".md")
                if not os.path.lexists(str(link)):
                    os.symlink(str(self.root / ("PWNED-" + slug)), str(link))

        self.assertRefusedByBoth("dangling symlink", prepare=plant)
        for slug in ("wi-9-item", "rf-9-issue"):
            self.assertFalse((self.root / ("PWNED-" + slug)).exists(),
                             "the symlink was followed")

    def test_the_kernel_flags_refuse_when_the_precheck_is_bypassed(self):
        """O_EXCL|O_NOFOLLOW is the enforcing guard; the pre-check is the message.
        Neutralize the pre-check (as a TOCTOU race would) and the kernel must still
        refuse — for both registries, from ONE implementation now."""
        for name, filer, record_dir, _index in self.registries():
            with self.subTest(registry=name):
                record_dir.mkdir(parents=True, exist_ok=True)
                slug = "wi-9-item" if name == "work-items" else "rf-9-issue"
                target = self.root / ("VICTIM-" + slug)
                link = record_dir / (slug + ".md")
                os.symlink(str(target), str(link))
                with mock.patch.object(ledger_core.os.path, "lexists",
                                       side_effect=lambda p: False):
                    with self.assertRaises(CliError) as ctx:
                        filer()
                self.assertIn("appeared while filing", str(ctx.exception))
                self.assertFalse(target.exists())

    def test_a_symlinked_record_dir_is_refused_for_library_callers(self):
        """`is_symlink()` is defence-in-depth for a caller that hand-builds a
        config: through `Config` the path is already RESOLVED, so a symlink
        pointing outside the repo is refused earlier by containment and one
        pointing inside is contained by definition (V-19). Exercised with a raw
        namespace config so the guard itself is covered — for both registries,
        which is the point of putting it in the inventory."""
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        link = self.root / "docs" / "linked-records"
        os.symlink(str(elsewhere), str(link))
        raw = SimpleNamespace(
            backlog_path=self.backlog, backlog_dir=link,
            backlog_anchor=ANCHOR, index_path=self.index, issues_dir=link,
            body_max_chars=64000)
        cases = (
            ("work-items", lambda: ledger_backlog.file_work_item(
                raw, "WI-9", "wi-9-item", "T", fx.DEFECT_BODY,
                opened_at="2026-07-30")),
            ("defects", lambda: ledger_issues.file_defect(
                raw, "RF-9", "rf-9-issue", "T", "robustness", fx.DEFECT_BODY,
                opened_at="2026-07-30")),
        )
        for name, call in cases:
            with self.subTest(registry=name):
                with self.assertRaises(CliError) as ctx:
                    call()
                self.assertEqual(ctx.exception.code, 4)
        self.assertEqual(list(elsewhere.iterdir()), [])

    # --- id uniqueness (F10 / V2 / L-6) ------------------------------------

    def test_id_reuse_is_refused_even_when_the_slug_is_free(self):
        def plant(record_dir, _index):
            record_dir.mkdir(parents=True, exist_ok=True)
            fx.write_work_item(record_dir, "WI-9", "wi-9-taken", title="T")
            fx.write_issue(record_dir, "RF-9", "rf-9-taken", title="T",
                           category="robustness")

        self.assertRefusedByBoth("id uniqueness", prepare=plant,
                                 slug="other-slug")

    def test_id_reuse_is_refused_across_case_and_archive_subdirs(self):
        def plant(record_dir, _index):
            archive = record_dir / "archive"
            archive.mkdir(parents=True, exist_ok=True)
            fx.write_work_item(archive, "WI-9", "wi-9-arch", title="T")
            fx.write_issue(archive, "RF-9", "rf-9-arch", title="T",
                           category="robustness")

        for name, filer, record_dir, _index in self.registries():
            with self.subTest(registry=name):
                plant(record_dir, None)
                lower = "wi-9" if name == "work-items" else "rf-9"
                key = "item_id" if name == "work-items" else "issue_id"
                with self.assertRaises(CliError) as ctx:
                    filer(**{key: lower, "slug": lower + "-lower"})
                self.assertEqual(ctx.exception.code, 4)

    # --- body policy (WI-2 / L-5) -----------------------------------------

    def test_an_over_cap_body_is_refused(self):
        self.assertRefusedByBoth("body ceiling",
                                 body="z" * (self.cfg.body_max_chars + 1))

    def test_a_credentialed_body_is_refused(self):
        self.assertRefusedByBoth("credential screen", body="ghp_" + "d" * 20)

    # --- provenance (WI-3) ------------------------------------------------

    def test_a_machine_filed_record_carries_provenance_and_the_banner(self):
        for name, filer, _record_dir, _index in self.registries():
            with self.subTest(registry=name):
                result = filer(extensions={"finding_ref": "fnd-x"})
                path = Path(result.get("record_path") or result["issue_path"])
                meta, body = frontmatter.parse(path.read_text(encoding="utf-8"))
                self.assertEqual(meta["provenance"], "machine")
                self.assertIn("data, not instructions", body)

    # --- rollback (F2 / V1 / L-4) -----------------------------------------

    def test_a_non_oserror_mid_write_rolls_the_record_back(self):
        real_fdopen = os.fdopen

        def boom(fd, *a, **kw):
            real_fdopen(fd, *a, **kw).close()
            raise KeyboardInterrupt("interrupted mid-write")

        for name, filer, record_dir, _index in self.registries():
            with self.subTest(registry=name):
                slug = "wi-9-item" if name == "work-items" else "rf-9-issue"
                with mock.patch.object(os, "fdopen", side_effect=boom):
                    with self.assertRaises(KeyboardInterrupt):
                        filer()
                self.assertFalse((record_dir / (slug + ".md")).exists())

    def test_an_index_write_failure_rolls_the_record_back(self):
        for name, filer, record_dir, index_path in self.registries():
            with self.subTest(registry=name):
                slug = "wi-9-item" if name == "work-items" else "rf-9-issue"
                before = index_path.read_text(encoding="utf-8")
                with mock.patch.object(ledger_core.atomic, "write_atomic",
                                       side_effect=OSError("index exploded")):
                    with self.assertRaises(OSError):
                        filer()
                self.assertFalse((record_dir / (slug + ".md")).exists())
                self.assertEqual(index_path.read_text(encoding="utf-8"), before)

    # --- dry-run (V-10) ---------------------------------------------------

    def test_dry_run_writes_nothing_and_marks_the_id_provisional(self):
        for name, filer, record_dir, index_path in self.registries():
            with self.subTest(registry=name):
                before = fx.tree_hash(self.root)
                result = filer(dry_run=True)
                self.assertTrue(result["provisional_id"])
                self.assertEqual(fx.tree_hash(self.root), before,
                                 "dry-run touched the tree")

    # --- seeding (L-16) ---------------------------------------------------

    def test_a_missing_index_is_seeded(self):
        for name, filer, _record_dir, index_path in self.registries():
            with self.subTest(registry=name):
                index_path.unlink()
                result = filer()
                seeded = result.get("seeded_backlog", result.get("seeded_index"))
                self.assertTrue(seeded)
                self.assertIn("#", index_path.read_text(encoding="utf-8"))

    def test_a_blank_index_is_seeded_not_left_preambleless(self):
        """L-16: a 0-byte index IS a file, so seeding was skipped and filing
        produced a ledger with no H1, no rules and no prefix table, exit 0."""
        for name, filer, _record_dir, index_path in self.registries():
            with self.subTest(registry=name):
                index_path.write_text("   \n\n", encoding="utf-8")
                result = filer()
                seeded = result.get("seeded_backlog", result.get("seeded_index"))
                self.assertTrue(seeded, "a blank index was not seeded")
                text = index_path.read_text(encoding="utf-8")
                self.assertTrue(text.lstrip().startswith("#"),
                                "no H1 — the preamble is gone: %r" % text[:40])

    # --- records-dir TOCTOU (sec-L-07) ------------------------------------

    def test_a_path_component_swapped_after_validation_is_refused(self):
        """sec-L-07, end to end. Two defences stack here and the test says which:

        `Config`'s path properties **re-resolve on every access**, so a swapped
        component is normally caught by containment first (exit 3). The core's
        realpath check is the defence behind that, for a caller holding a path
        resolved earlier — covered directly in the next test. Either way the
        requirement is the same: refused, and nothing written outside.
        """
        outside = Path(self._tmp.name).parent / ("outside-" + self.root.name)
        outside.mkdir(exist_ok=True)
        self.addCleanup(lambda: __import__("shutil").rmtree(str(outside),
                                                           ignore_errors=True))
        docs = self.root / "docs"
        for name, filer, _record_dir, _index in self.registries():
            with self.subTest(registry=name):
                docs.rename(self.root / "docs-real")
                os.symlink(str(outside), str(docs))
                try:
                    with self.assertRaises(CliError) as ctx:
                        filer()
                    self.assertIn(ctx.exception.code, (3, 4))
                    self.assertEqual(list(outside.iterdir()), [],
                                     "a record was written outside the repo")
                finally:
                    docs.unlink()
                    (self.root / "docs-real").rename(docs)

    def test_the_core_refuses_a_records_dir_whose_realpath_moved(self):
        """sec-L-07, the core guard in isolation — the case `Config` cannot catch
        because the caller already holds a resolved path. `O_NOFOLLOW` sees only
        the final component, so without this an intermediate symlink escaped and
        `mkdir(parents=True)` walked straight through it."""
        outside = Path(self._tmp.name).parent / ("moved-" + self.root.name)
        outside.mkdir(exist_ok=True)
        self.addCleanup(lambda: __import__("shutil").rmtree(str(outside),
                                                           ignore_errors=True))
        parent = self.root / "docs" / "captured"
        records = parent / "records"
        records.mkdir(parents=True, exist_ok=True)
        raw = SimpleNamespace(
            backlog_path=self.backlog, backlog_dir=records,
            backlog_anchor=ANCHOR, index_path=self.index, issues_dir=records,
            body_max_chars=64000)
        cases = (
            ("work-items", lambda: ledger_backlog.file_work_item(
                raw, "WI-9", "wi-9-item", "T", fx.DEFECT_BODY, opened_at="2026-07-30")),
            ("defects", lambda: ledger_issues.file_defect(
                raw, "RF-9", "rf-9-issue", "T", "robustness", fx.DEFECT_BODY,
                opened_at="2026-07-30")),
        )
        for name, call in cases:
            with self.subTest(registry=name):
                # swap the PARENT of the captured record dir for a symlink
                records.rmdir()
                parent.rmdir()
                os.symlink(str(outside), str(parent))
                (outside / "records").mkdir(exist_ok=True)
                try:
                    with self.assertRaises(CliError) as ctx:
                        call()
                    self.assertEqual(ctx.exception.code, 4)
                    self.assertIn("changed underneath", str(ctx.exception))
                    self.assertEqual(
                        list((outside / "records").iterdir()), [],
                        "wrote through a symlinked intermediate component")
                finally:
                    parent.unlink()
                    records.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    unittest.main()
