"""Config resolution order, validation, and repo-root discovery."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import config as config_mod  # noqa: E402
from feedback_lib.config import find_repo_root, load_config  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        # keep the outer environment out of every test
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop(config_mod.CONFIG_ENV, None)


class TestDefaults(ConfigTestCase):
    def test_defaults_when_no_config_file(self):
        cfg = load_config(repo_root=str(self.root))
        self.assertIsNone(cfg.source)
        self.assertEqual(cfg.repo_root, self.root)
        self.assertEqual(cfg.issues_dir, self.root / "docs" / "issues")
        self.assertEqual(cfg.index_path, self.root / "docs" / "KNOWN_ISSUES.md")
        self.assertIsNone(cfg.backlog_path)
        self.assertEqual(cfg.backlog_anchor,
                         "<!-- feedback:discovered-issues -->")
        self.assertEqual(cfg.id_prefixes, {"_default": "RF"})
        self.assertEqual(cfg.feedback_dir, self.root / ".agent" / "feedback")

    def test_work_item_ledger_defaults_to_the_two_level_layout(self):
        cfg = load_config(repo_root=str(self.root))
        self.assertEqual(cfg.backlog_dir, self.root / "docs" / "backlog")
        self.assertEqual(cfg.backlog_prefix, "WI")
        self.assertEqual(cfg.backlog_layout, "index+files")

    def test_pre_existing_config_without_the_new_keys_loads_clean(self):
        """A config written before the two-level layout existed must keep
        working — no version bump, no unknown-key warning, and it lands on the
        layout its project already maintains by hand."""
        cfg_path = fx.write(
            self.root / "docs" / "feedback" / "config.json",
            json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md",
                        "backlog_anchor": "<!-- feedback:discovered-issues -->"}))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            cfg = load_config(repo_root=str(self.root))
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(cfg.source, str(cfg_path))
        self.assertEqual(cfg.backlog_path, self.root / "docs" / "BACKLOG.md")
        self.assertEqual(cfg.backlog_dir, self.root / "docs" / "backlog")
        self.assertEqual(cfg.backlog_layout, "index+files")

    def test_unknown_backlog_layout_raises_code_3(self):
        cfg_path = fx.write(self.root / "layout.json",
                            json.dumps({"v": 1, "backlog_layout": "one-file"}))
        cfg = load_config(config_arg=str(cfg_path), repo_root=str(self.root))
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_layout
        self.assertEqual(ctx.exception.code, 3)

    def test_data_root_falls_back_to_repo_root_without_real_git(self):
        cfg = load_config(repo_root=str(self.root))
        self.assertEqual(cfg.data_root, self.root)


class TestResolutionOrder(ConfigTestCase):
    def test_repo_config_auto_picked(self):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "issues_dir": "custom/issues"}))
        cfg = load_config(repo_root=str(self.root))
        self.assertTrue(str(cfg.source).endswith("config.json"))
        self.assertEqual(cfg.issues_dir, self.root / "custom" / "issues")

    def test_env_var_respected_and_beats_repo_config(self):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "issues_dir": "from-repo"}))
        env_cfg = fx.write(self.root / "env-config.json",
                           json.dumps({"v": 1, "issues_dir": "from-env"}))
        with mock.patch.dict(os.environ,
                             {config_mod.CONFIG_ENV: str(env_cfg)}):
            cfg = load_config(repo_root=str(self.root))
        self.assertEqual(cfg.issues_dir, self.root / "from-env")
        self.assertEqual(cfg.source, str(env_cfg))

    def test_explicit_path_wins_over_env(self):
        arg_cfg = fx.write(self.root / "arg-config.json",
                           json.dumps({"v": 1, "issues_dir": "from-arg"}))
        env_cfg = fx.write(self.root / "env-config.json",
                           json.dumps({"v": 1, "issues_dir": "from-env"}))
        with mock.patch.dict(os.environ,
                             {config_mod.CONFIG_ENV: str(env_cfg)}):
            cfg = load_config(config_arg=str(arg_cfg),
                              repo_root=str(self.root))
        self.assertEqual(cfg.issues_dir, self.root / "from-arg")
        self.assertEqual(cfg.source, str(arg_cfg))


class TestValidation(ConfigTestCase):
    def test_bad_json_raises_config_error_code_3(self):
        bad = fx.write(self.root / "bad.json", "{nope,,,")
        with self.assertRaises(CliError) as ctx:
            load_config(config_arg=str(bad), repo_root=str(self.root))
        self.assertEqual(ctx.exception.code, 3)

    def test_missing_explicit_config_raises_code_3(self):
        with self.assertRaises(CliError) as ctx:
            load_config(config_arg=str(self.root / "absent.json"),
                        repo_root=str(self.root))
        self.assertEqual(ctx.exception.code, 3)

    def test_wrong_schema_version_raises_code_3(self):
        bad = fx.write(self.root / "v99.json",
                       json.dumps({"v": 99, "issues_dir": "x"}))
        with self.assertRaises(CliError) as ctx:
            load_config(config_arg=str(bad), repo_root=str(self.root))
        self.assertEqual(ctx.exception.code, 3)

    def test_non_object_config_raises_code_3(self):
        bad = fx.write(self.root / "list.json", "[1, 2]")
        with self.assertRaises(CliError) as ctx:
            load_config(config_arg=str(bad), repo_root=str(self.root))
        self.assertEqual(ctx.exception.code, 3)

    def test_unknown_keys_warn_on_stderr_but_load(self):
        cfg_path = fx.write(
            self.root / "extra.json",
            json.dumps({"v": 1, "issues_dir": "loaded", "mystery_knob": 7}))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            cfg = load_config(config_arg=str(cfg_path),
                              repo_root=str(self.root))
        self.assertIn("mystery_knob", err.getvalue())
        self.assertIn("unknown config key", err.getvalue())
        self.assertEqual(cfg.issues_dir, self.root / "loaded")
        # the unknown key is not adopted into the config values
        self.assertIsNone(cfg.get("mystery_knob"))


class TestFindRepoRoot(ConfigTestCase):
    def test_walks_up_to_git_dir(self):
        nested = self.root / "a" / "b" / "c"
        nested.mkdir(parents=True)
        self.assertEqual(find_repo_root(start=str(nested)), self.root)

    def test_outside_a_repo_raises_code_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            plain = Path(tmp).resolve()
            if any((c / ".git").exists() for c in (plain, *plain.parents)):
                self.skipTest("temp dir unexpectedly inside a git repo")
            with self.assertRaises(CliError) as ctx:
                find_repo_root(start=str(plain))
            self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
