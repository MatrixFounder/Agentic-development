"""Unit tests for installer.vendors — loader + per-action schema validator.

Task 063-02. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

from _base import FRAMEWORK_ROOT, InstallerTestCase
from installer.errors import ConfigurationError, InstallerError
from installer.vendors import (
    load_vendors,
    resolve_profile,
    validate_component,
    validate_profile,
)

VENDORS_YAML = FRAMEWORK_ROOT / "System" / "scripts" / "vendors.yaml"
_REAL_VENDORS = {"claude", "antigravity", "codex", "cursor", "gemini-cli"}


class TestLoadVendors(InstallerTestCase):

    def test_load_real_vendors_yaml(self) -> None:
        data = load_vendors(VENDORS_YAML)
        self.assertEqual(data["version"], 1)
        self.assertEqual(set(data["vendors"]), _REAL_VENDORS)
        self.assertIn("defaults", data)

    def test_missing_file_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            load_vendors(self.tmp / "nope.yaml")

    def test_malformed_yaml_rejected(self) -> None:
        bad = self.tmp / "bad.yaml"
        bad.write_text("version: 1\nvendors: [1, 2\n", encoding="utf-8")  # unclosed flow seq
        with self.assertRaises(ConfigurationError):
            load_vendors(bad)

    def test_missing_version_rejected(self) -> None:
        f = self.tmp / "v.yaml"
        f.write_text("vendors:\n  claude: {}\n", encoding="utf-8")
        with self.assertRaises(ConfigurationError):
            load_vendors(f)

    def test_missing_vendors_rejected(self) -> None:
        f = self.tmp / "v.yaml"
        f.write_text("version: 1\n", encoding="utf-8")
        with self.assertRaises(ConfigurationError):
            load_vendors(f)


class TestValidateProfile(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = load_vendors(VENDORS_YAML)

    def test_all_real_profiles_validate(self) -> None:
        for name, profile in self.data["vendors"].items():
            with self.subTest(vendor=name):
                validate_profile(name, profile, FRAMEWORK_ROOT)  # must not raise

    def test_resolved_profiles_validate(self) -> None:
        """The merged (defaults + vendor) profile also passes validation."""
        for name in _REAL_VENDORS:
            with self.subTest(vendor=name):
                resolved = resolve_profile(self.data, name)
                validate_profile(name, resolved, FRAMEWORK_ROOT)

    def test_real_defaults_components_validate(self) -> None:
        defaults = self.data["defaults"]
        for comp in defaults["agent_components"] + defaults["root_components"]:
            with self.subTest(component=comp["path"]):
                validate_component(comp, FRAMEWORK_ROOT, context="defaults")

    def test_invalid_bootstrap_strategy_rejected(self) -> None:
        profile = {"bootstrap_strategy": "telepathy", "components": []}
        with self.assertRaises(ConfigurationError):
            validate_profile("x", profile, FRAMEWORK_ROOT)

    def test_marker_block_requires_bootstrap_source(self) -> None:
        profile = {"bootstrap_strategy": "marker_block", "bootstrap_file": "X.md",
                   "components": []}
        with self.assertRaises(ConfigurationError):
            validate_profile("x", profile, FRAMEWORK_ROOT)

    def test_git_root_required_must_be_bool(self) -> None:
        profile = {"bootstrap_strategy": "none", "git_root_required": "yes",
                   "components": []}
        with self.assertRaises(ConfigurationError):
            validate_profile("x", profile, FRAMEWORK_ROOT)

    def test_bootstrap_file_must_be_str_or_null(self) -> None:
        profile = {"bootstrap_strategy": "none", "bootstrap_file": 123,
                   "components": []}
        with self.assertRaises(ConfigurationError):
            validate_profile("x", profile, FRAMEWORK_ROOT)

    def test_vendor_dir_must_be_str_or_null(self) -> None:
        profile = {"bootstrap_strategy": "none", "vendor_dir": ["nope"],
                   "components": []}
        with self.assertRaises(ConfigurationError):
            validate_profile("x", profile, FRAMEWORK_ROOT)


class TestValidateComponent(InstallerTestCase):

    def test_mkdir_with_source_rejected(self) -> None:
        comp = {"path": ".codex", "action": "mkdir", "source": ".codex"}
        with self.assertRaises(ConfigurationError):
            validate_component(comp, FRAMEWORK_ROOT)

    def test_mkdir_without_source_ok(self) -> None:
        validate_component({"path": ".agent/sessions", "action": "mkdir"}, FRAMEWORK_ROOT)

    def test_link_missing_source_rejected(self) -> None:
        comp = {"path": ".x", "action": "link_folder", "source": "no/such/dir/xyz"}
        with self.assertRaises(ConfigurationError):
            validate_component(comp, FRAMEWORK_ROOT)

    def test_link_missing_source_optional_ok(self) -> None:
        comp = {"path": ".x", "action": "link_folder", "source": "no/such/dir/xyz",
                "optional": True}
        validate_component(comp, FRAMEWORK_ROOT)  # must not raise

    def test_missing_path_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            validate_component({"action": "mkdir"}, FRAMEWORK_ROOT)

    def test_unknown_action_rejected(self) -> None:
        comp = {"path": ".x", "action": "teleport", "source": "System"}
        with self.assertRaises(ConfigurationError):
            validate_component(comp, FRAMEWORK_ROOT)

    def test_non_dict_component_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            validate_component("not-a-mapping", FRAMEWORK_ROOT)


class TestResolveProfile(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = load_vendors(VENDORS_YAML)

    def test_resolve_merges_defaults_in_order(self) -> None:
        resolved = resolve_profile(self.data, "claude")
        paths = [c["path"] for c in resolved["components"]]
        # defaults.agent_components first, then root_components, then vendor's own.
        self.assertEqual(paths[0], ".agent/skills")
        self.assertIn("System", paths)
        self.assertIn(".claude/skills", paths)
        self.assertLess(paths.index(".agent/skills"), paths.index(".claude/skills"))
        self.assertLess(paths.index("System"), paths.index(".claude/skills"))

    def test_resolve_count(self) -> None:
        resolved = resolve_profile(self.data, "claude")
        defaults = self.data["defaults"]
        expected = (len(defaults["agent_components"]) + len(defaults["root_components"])
                    + len(self.data["vendors"]["claude"]["components"]))
        self.assertEqual(len(resolved["components"]), expected)

    def test_resolve_does_not_mutate_source(self) -> None:
        before = len(self.data["vendors"]["claude"]["components"])
        resolve_profile(self.data, "claude")
        self.assertEqual(len(self.data["vendors"]["claude"]["components"]), before)

    def test_unknown_vendor_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            resolve_profile(self.data, "emacs-doctor")


class TestErrors(InstallerTestCase):

    def test_configuration_error_exit_code(self) -> None:
        self.assertEqual(ConfigurationError("boom").exit_code, 2)

    def test_exit_code_override(self) -> None:
        self.assertEqual(InstallerError("boom", exit_code=7).exit_code, 7)

    def test_default_exit_code(self) -> None:
        self.assertEqual(InstallerError("boom").exit_code, 1)
