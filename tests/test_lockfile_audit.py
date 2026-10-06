"""The dependency audit covers every npm lockfile (TASK 111 R5).

Before TASK 111 the `security-audit` scanner ran `npm audit` at the project root only, and a failed
run produced no finding. This repository holds three npm lockfiles under
`.agent/skills/mermaid-authoring-guidelines/assets/renderers/` and none at the root. A fake `npm` on
`PATH` records the directory it runs in, that directory's entries and its arguments, and prints a
set reply. This file pins:

* a lockfile below the root is audited, in a temporary copy of it and its `package.json`, so a
  `.npmrc` beside the lockfile takes no part (``TC-L1``, ``TC-L13``);
* each finding names its lockfile (``TC-L2``, ``TC-L12``);
* `node_modules/` and symbolic links are skipped (``TC-L3``, ``TC-L11``), and a project without a
  lockfile runs no audit (``TC-L4``);
* an audit that does not finish yields an `info` finding and the section says so (``TC-L5``,
  ``TC-L14``, ``TC-L15``);
* one directory is audited once (``TC-L6``);
* `run_external_tools` audits each lockfile, and only those (``TC-L7`` to ``TC-L9``);
* a root `package.json` without a lockfile is reported, not audited (``TC-L10``);
* the copy holds the original `package.json`, never a linked one (``TC-L16``, ``TC-L17``);
* a finding outranks an unaudited lockfile in the status; an unexpected vulnerability field and a
  timeout yield a named `info` finding (``TC-L18`` to ``TC-L20``).
"""
import importlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = PROJECT_ROOT / ".agent" / "skills" / "security-audit" / "scripts" / "audit"
NAME = "security_audit_scanner_under_test"


def _load():
    """The scanner package under a name no other test module uses."""
    if NAME not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[NAME] = module
        spec.loader.exec_module(module)
    return (importlib.import_module(f"{NAME}.scanners"),
            importlib.import_module(f"{NAME}.external"))


scanners, external = _load()

FAKE_NPM = """#!/bin/sh
printf '%s\\t%s\\t%s\\t%s\\n' "$PWD" "$(ls -A | tr '\\n' ' ')" "$*" "$(cat package.json)" >> "$FAKE_NPM_LOG"
if grep -q broken package.json; then echo "not json"; else cat "$FAKE_NPM_REPLY"; fi
"""
HIGH = {"vulnerabilities": {"x": {"severity": "high"}}}
COPY = "package-lock.json package.json"


class AuditTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.project = self.tmp / "project"
        self.project.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        npm = self.bin / "npm"
        npm.write_text(FAKE_NPM)
        npm.chmod(0o755)
        self.log = self.tmp / "npm.log"
        self.reply = self.tmp / "reply.json"
        self.set_reply({"vulnerabilities": {}})
        env = {"PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
               "FAKE_NPM_LOG": str(self.log), "FAKE_NPM_REPLY": str(self.reply)}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def set_reply(self, reply):
        self.reply.write_text(reply if isinstance(reply, str) else json.dumps(reply))

    def lockfile(self, rel, name="package-lock.json", package=True, content='{"name": "x"}'):
        d = self.project / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text("{}")
        if package:
            (d / "package.json").write_text(content)
        return d

    def calls(self):
        """`(directory, entries, arguments)` of each fake `npm` run."""
        return [call[:3] for call in self.full_calls()]

    def full_calls(self):
        """`(directory, entries, arguments, package.json)` of each fake `npm` run."""
        if not self.log.exists():
            return []
        return [tuple(part.strip() for part in line.split("\t"))
                for line in self.log.read_text().splitlines()]

    def scan(self):
        return scanners.scan_dependencies(str(self.project))

    def infos(self, findings):
        return [f for f in findings if f.get("severity") == "info"]


class TestScanDependencies(AuditTestCase):
    """TC-L1 to TC-L6 and TC-L10 to TC-L15 drive `scan_dependencies`."""

    def test_l1_lockfile_below_the_root_is_audited_in_a_copy(self):
        # base-fail: the base runs npm audit only at a root package.json.
        self.lockfile("sub")
        self.scan()
        [(where, entries, args)] = self.calls()
        self.assertEqual(args, "audit --json --package-lock-only")
        self.assertEqual(entries, COPY)
        self.assertFalse(Path(where).resolve().is_relative_to(self.project.resolve()))

    def test_l2_finding_names_its_lockfile(self):
        self.lockfile("sub")
        self.set_reply(HIGH)
        findings = self.scan()["findings"]
        high = [f for f in findings if f.get("severity") == "high" and f.get("type") == "npm audit"]
        self.assertEqual(len(high), 1, findings)
        self.assertTrue(high[0]["message"].startswith("sub/package-lock.json: 1 high"), high[0])

    def test_l3_node_modules_is_skipped(self):
        self.lockfile("node_modules/dep")
        self.scan()
        self.assertEqual(self.calls(), [])

    def test_l4_no_lockfile_runs_no_audit(self):
        (self.project / "package.json").write_text("{}")
        self.scan()
        self.assertEqual(self.calls(), [])

    def test_l5_unfinished_audit_yields_an_info_finding(self):
        self.lockfile("sub")
        for label, reply in (("not json", "not json"), ("not an object", []),
                             ("error object", {"error": {"code": "ENOAUDIT"}}),
                             ("error message", {"message": "ECONNREFUSED", "error": {}})):
            with self.subTest(case=label):
                self.set_reply(reply)
                info = self.infos(self.scan()["findings"])
                self.assertEqual(len(info), 1, info)
                self.assertTrue(info[0]["message"].startswith("sub/package-lock.json: not audited"))
        with self.subTest(case="timeout"), mock.patch.object(
                scanners.subprocess, "run",
                side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)
        with self.subTest(case="npm absent"), \
                mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)

    def test_l5_error_message_reaches_the_reason(self):
        self.lockfile("sub")
        self.set_reply({"message": "request to registry failed, ECONNREFUSED", "error": {}})
        [info] = self.infos(self.scan()["findings"])
        self.assertIn("ECONNREFUSED", info["message"])

    def test_l6_one_directory_is_audited_once(self):
        self.lockfile("sub")
        (self.project / "sub" / "npm-shrinkwrap.json").write_text("{}")
        self.set_reply(HIGH)
        findings = self.scan()["findings"]
        [(_where, entries, _args)] = self.calls()
        self.assertEqual(entries, "npm-shrinkwrap.json package.json")
        self.assertTrue(any(f.get("message", "").startswith("sub/npm-shrinkwrap.json:")
                            for f in findings))

    def test_l10_root_package_json_without_lockfile_is_reported_not_audited(self):
        (self.project / "package.json").write_text("{}")
        findings = self.scan()["findings"]
        self.assertTrue(any(f.get("type") == "Missing Lock File" and "javascript" in f["message"]
                            for f in findings), findings)
        self.assertEqual(self.calls(), [])

    def test_l11_symbolic_links_are_not_followed(self):
        real = self.lockfile("../outside")
        (self.project / "linked").symlink_to(real, target_is_directory=True)
        d = self.project / "plain"
        d.mkdir()
        (d / "package.json").write_text("{}")
        (d / "package-lock.json").symlink_to(real / "package-lock.json")
        self.scan()
        self.assertEqual(self.calls(), [])

    def test_l12_critical_finding_names_its_lockfile(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"a": {"severity": "critical"}, "b": {"severity": "high"}}})
        result = self.scan()
        messages = sorted(f["message"] for f in result["findings"] if f.get("type") == "npm audit")
        self.assertEqual(messages, ["sub/package-lock.json: 1 critical vulnerabilities in dependencies",
                                    "sub/package-lock.json: 1 high vulnerabilities in dependencies"])
        self.assertIn("Critical", result["status"])

    def test_l13_npmrc_beside_the_lockfile_is_not_copied(self):
        d = self.lockfile("sub")
        (d / ".npmrc").write_text("registry=http://attacker.invalid/\n")
        self.scan()
        [(_where, entries, _args)] = self.calls()
        self.assertEqual(entries, COPY)

    def test_l14_lockfile_without_package_json_is_not_audited(self):
        self.lockfile("sub", package=False)
        [info] = self.infos(self.scan()["findings"])
        self.assertEqual(info["message"], "sub/package-lock.json: not audited, no package.json beside it")
        self.assertEqual(self.calls(), [])

    def test_l15_section_status_names_unaudited_lockfiles(self):
        self.lockfile("sub")
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")

    def test_l16_copy_holds_the_original_package_json(self):
        self.lockfile("sub", content='{"name": "pinned-content"}')
        self.scan()
        [call] = self.full_calls()
        self.assertEqual(call[3], '{"name": "pinned-content"}')

    def test_l17_linked_package_json_is_not_used(self):
        d = self.lockfile("sub", package=False)
        real = self.tmp / "elsewhere.json"
        real.write_text("{}")
        (d / "package.json").symlink_to(real)
        [info] = self.infos(self.scan()["findings"])
        self.assertIn("no package.json beside it", info["message"])
        self.assertEqual(self.calls(), [])

    def test_l18_a_finding_outranks_an_unaudited_lockfile_in_the_status(self):
        self.lockfile("a")
        self.lockfile("b", content='{"name": "broken"}')
        self.set_reply({"vulnerabilities": {"x": {"severity": "critical"}}})
        result = self.scan()
        self.assertEqual(len(self.infos(result["findings"])), 1)
        self.assertIn("Critical", result["status"])

    def test_l19_vulnerability_field_shapes(self):
        self.lockfile("sub")
        for label, reply, infos in (("null", {"vulnerabilities": None}, 0),
                                    ("list", {"vulnerabilities": []}, 1),
                                    ("entry not a map", {"vulnerabilities": {"x": "high"}}, 0)):
            with self.subTest(case=label):
                self.set_reply(reply)
                findings = self.scan()["findings"]
                self.assertEqual(len(self.infos(findings)), infos, findings)
                self.assertFalse([f for f in findings if f.get("severity") in ("high", "critical")])

    def test_l20_timeout_reason_names_the_limit(self):
        self.lockfile("sub")
        with mock.patch.object(scanners.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
            [info] = self.infos(self.scan()["findings"])
        self.assertEqual(info["message"], "sub/package-lock.json: not audited, npm audit ran past 60 s")

    def test_l21_error_code_reaches_the_reason(self):
        self.lockfile("sub")
        self.set_reply({"error": {"code": "ENOAUDIT"}})
        [info] = self.infos(self.scan()["findings"])
        self.assertIn("ENOAUDIT", info["message"])

    def test_l22_status_counts_every_unaudited_lockfile(self):
        self.lockfile("a")
        self.lockfile("b")
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
            self.assertEqual(self.scan()["status"], "[?] Not audited: 2 npm lockfile(s)")

    def test_l23_a_moderate_advisory_is_no_finding(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
        findings = [f for f in self.scan()["findings"] if f.get("type") == "npm audit"]
        self.assertEqual(findings, [])

    def test_l15_each_audit_has_a_60_second_timeout(self):
        self.lockfile("sub")
        with mock.patch.object(scanners.subprocess, "run", wraps=subprocess.run) as run:
            self.scan()
        self.assertEqual(run.call_args.kwargs.get("timeout"), 60)


class TestExternalTools(AuditTestCase):
    """TC-L7 to TC-L9 drive `run_external_tools` (R5.4, R5.5)."""

    def external(self, types):
        recorded = []

        def record(cmd, cwd=None, **_kw):
            entries = " ".join(sorted(os.listdir(cwd))) if cwd else ""
            recorded.append((list(cmd), Path(cwd).resolve() if cwd else None, entries))

        with mock.patch.object(external, "run_command", side_effect=record):
            external.run_external_tools(str(self.project), types)
        return recorded

    def test_l7_external_tools_audit_each_lockfile_in_a_copy(self):
        # base-fail: the base runs npm audit at the root, and only for a javascript project.
        self.lockfile("sub")
        npm = [r for r in self.external([]) if r[0][:1] == ["npm"]]
        self.assertEqual(len(npm), 1, npm)
        cmd, where, entries = npm[0]
        self.assertEqual(cmd, ["npm", "audit", "--package-lock-only"])
        self.assertEqual(entries, COPY)
        self.assertFalse(where.is_relative_to(self.project.resolve()))

    def test_l8_no_lockfile_runs_no_npm_audit(self):
        npm = [r for r in self.external(["javascript"]) if r[0][:1] == ["npm"]]
        self.assertEqual(npm, [])

    def test_l9b_yarn_audit_needs_a_javascript_project(self):
        (self.project / "yarn.lock").write_text("")
        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["yarn"]], [])

    def test_l9c_lockfile_without_package_json_is_skipped(self):
        self.lockfile("sub", package=False)
        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["npm"]], [])

    def test_l9_root_yarn_lock_runs_yarn_audit_at_the_root(self):
        (self.project / "yarn.lock").write_text("")
        yarn = [r[:2] for r in self.external(["javascript"]) if r[0][:1] == ["yarn"]]
        self.assertEqual(yarn, [(["yarn", "audit"], self.project.resolve())])


if __name__ == "__main__":
    unittest.main()
