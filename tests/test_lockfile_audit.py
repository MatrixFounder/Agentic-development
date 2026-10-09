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
* `run_external_tools` audits each lockfile, and only those (``TC-L7`` to ``TC-L9c``); it runs
  `yarn audit` in a copy of `yarn.lock` and `package.json`, never through a link, and for a
  javascript project only (``TC-Y1`` to ``TC-Y3``, TASK 112 R5.1);
* a root `package.json` without a lockfile is reported, not audited (``TC-L10``);
* the copy holds the original `package.json`, never a linked one (``TC-L16``, ``TC-L17``);
* a finding outranks an unaudited lockfile in the status; an unexpected vulnerability field and a
  timeout yield a named `info` finding (``TC-L18`` to ``TC-L20``).

TASK 118 (WI-42) adds the status of each external tool and the findings of every npm severity. Its
fake tools are `/bin/sh` scripts in a `bin` directory that is the whole `PATH`, so a tool installed
on the runner does not start. This file pins:

* `run_audit.py` reports each external tool and exits 3 when a part did not run (``TC-E1``,
  ``TC-E11``, ``TC-E13``, ``TC-E15``); a tool's record says `ran`, `not_installed` or `timed_out`
  (``TC-E2``, ``TC-E4``), and a fallback fills its slot (``TC-E5``);
* a tool's non-zero exit fails `--fail-on` (``TC-E3``, ``TC-E10``), and the options that make a
  finding exit non-zero are passed (``TC-E9``);
* the secret scan reads the working tree with `--no-git`, and the history slot follows the `.git`
  at or above the scanned root, never through a link (``TC-E6``, ``TC-E7``);
* stdout holds one JSON document (``TC-E8``); the summary output lists each tool (``TC-E14``); the
  external status and the overall status (``TC-E12``, ``TC-E16``); the summary counts every
  finding before the cut (``TC-E17``);
* npm advisories of every severity are findings, with a count map per lockfile, and an unaudited
  lockfile carries `audited: false` (``TC-D1`` to ``TC-D7``; ``TC-D1`` replaces ``TC-L23``); a
  lockfile that cannot be copied is not audited, and the scanner still prints its report
  (``TC-D8``);
* a tool killed by a signal leaves its slot a part not run (``TC-E18``), and text from the scanned
  tree reaches printed output with its control characters escaped (``TC-E19``, ``TC-E19b``).

TASK 119 (WI-51) adds:

* an in-process scan skips a file that is not regular, such as a FIFO, and counts it in
  `skipped_files`; the run never blocks on it (``TC-F1``, ``TC-F2``); a link to a regular file in
  the scanned root is still read (``TC-F3``), and one whose real path leaves the root is skipped
  (``TC-F9``);
* `AuditTestCase` runs the fake `npm` with `PATH` the fake `bin`, `/usr/bin` and `/bin` only
  (``TC-F4``);
* `printable` escapes the backslash (``TC-F5``);
* `open_regular_text` opens with `O_BINARY` and `O_NOCTTY` where the platform has them, closes the
  descriptor of a refused file, and checks the size limit on the opened descriptor (``TC-F6`` to
  ``TC-F8``).

`RUN_AUDIT_PATH` and `RUN_AUDIT_CMD` name the `run_audit.py` that the tests load and start; a test
reads them at call time. The in-process cases stop the `.git` walk at their temporary directory;
the subprocess cases cannot. TC-E1 accepts either status of the history slot, and TC-E3 assumes
no `.git` link or special file above the system temporary directory.
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
RUN_AUDIT_PATH = PACKAGE.parent / "run_audit.py"
RUN_AUDIT_CMD = (sys.executable, str(RUN_AUDIT_PATH))


def _load():
    """The scanner package under a name no other test module uses."""
    if NAME not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[NAME] = module
        spec.loader.exec_module(module)
    return (importlib.import_module(f"{NAME}.scanners"),
            importlib.import_module(f"{NAME}.external"),
            importlib.import_module(f"{NAME}.helpers"))


scanners, external, helpers = _load()


def _run_audit_module():
    """`RUN_AUDIT_PATH`, loaded while `audit` names the package under test."""
    saved = sys.modules.get("audit")
    sys.modules["audit"] = sys.modules[NAME]
    try:
        spec = importlib.util.spec_from_file_location("security_audit_run_audit_under_test",
                                                      RUN_AUDIT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if saved is None:
            del sys.modules["audit"]
        else:
            sys.modules["audit"] = saved
    return module

FAKE_NPM = """#!/bin/sh
printf '%s\\t%s\\t%s\\t%s\\n' "$PWD" "$(ls -A | tr '\\n' ' ')" "$*" "$(cat package.json)" >> "$FAKE_NPM_LOG"
if grep -q broken package.json; then echo "not json"; else cat "$FAKE_NPM_REPLY"; fi
"""
HIGH = {"vulnerabilities": {"x": {"severity": "high"}}}
COPY = "package-lock.json package.json"
GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
ZERO_COUNTS = dict.fromkeys(("critical", "high", "moderate", "low", "info", "unknown"), 0)


def _ran(cmd, slot, where="."):
    """The tool record of a tool that ran and exited 0."""
    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": "ran",
            "exit_code": 0, "reason": None}


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
        # The fake `npm` calls `ls`, `tr`, `cat` and `grep`; a tool installed elsewhere, such as
        # under `/opt/homebrew/bin`, must not start in a case (TASK 119 R2).
        env = {"PATH": os.pathsep.join((str(self.bin), "/usr/bin", "/bin")),
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

    def test_d1_every_npm_severity_is_a_finding(self):
        """TC-D1 (TASK 118 R3.1), in place of TC-L23: the base kept critical and high only."""
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"a": {"severity": "moderate"}, "b": {"severity": "low"},
                                            "c": {"severity": "info"}}})
        findings = [f for f in self.scan()["findings"] if f.get("type") == "npm audit"]
        self.assertEqual([(f["severity"], f["message"]) for f in findings], [
            ("medium", "sub/package-lock.json: 1 moderate vulnerabilities in dependencies"),
            ("low", "sub/package-lock.json: 1 low vulnerabilities in dependencies"),
            ("info", "sub/package-lock.json: 1 info vulnerabilities in dependencies")])

    def test_l15_each_audit_has_a_60_second_timeout(self):
        self.lockfile("sub")
        with mock.patch.object(scanners.subprocess, "run", wraps=subprocess.run) as run:
            self.scan()
        self.assertEqual(run.call_args.kwargs.get("timeout"), 60)


class TestExternalTools(AuditTestCase):
    """TC-L7 to TC-L9c and TC-Y1 to TC-Y3 drive `run_external_tools` (R5.4, R5.5; TASK 112 R5.1)."""

    def external(self, types):
        recorded = []

        def record(cmd, cwd=None, slot=None, where=".", **_kw):
            entries = " ".join(sorted(os.listdir(cwd))) if cwd else ""
            recorded.append((list(cmd), Path(cwd).resolve() if cwd else None, entries))
            return _ran(cmd, slot, where)

        with mock.patch.object(external, "run_tool", side_effect=record):
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

    def test_y3_yarn_audit_needs_a_javascript_project(self):
        """TC-Y3 (TASK 112 R5.1), formerly TC-L9b."""
        (self.project / "yarn.lock").write_text("")
        (self.project / "package.json").write_text('{"name": "x"}')
        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["yarn"]], [])

    def test_l9c_lockfile_without_package_json_is_skipped(self):
        self.lockfile("sub", package=False)
        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["npm"]], [])

    def test_y1_yarn_audit_runs_in_a_copy(self):
        """TC-Y1 (TASK 112 R5.1): yarn reads `.yarnrc.yml` where it runs; `yarnPath` there names a
        script yarn executes. Base-fail: the base runs `yarn audit` in the scanned root."""
        (self.project / "yarn.lock").write_text("")
        (self.project / "package.json").write_text(json.dumps({
            "name": "x", "packageManager": "yarn@4.0.0", "dependencies": {"a": "1"},
            "devEngines": {"packageManager": {"name": "yarn", "version": "4.0.0"}},
            "scripts": {"preinstall": "evil"}, "resolutions": {"b": "2"}}))
        (self.project / ".yarnrc.yml").write_text("yarnPath: evil.js\n")
        copies = []

        def record(cmd, cwd=None, slot=None, where=".", **_kw):
            if cmd[:1] == ["yarn"]:
                copies.append((list(cmd), Path(cwd).resolve(), " ".join(sorted(os.listdir(cwd))),
                               json.loads((Path(cwd) / "package.json").read_text())))
            return _ran(cmd, slot, where)

        with mock.patch.object(external, "run_tool", side_effect=record):
            external.run_external_tools(str(self.project), ["javascript"])
        self.assertEqual(len(copies), 1, copies)
        cmd, where, entries, package = copies[0]
        self.assertEqual(cmd, ["yarn", "audit"])
        self.assertEqual(entries, "package.json yarn.lock")
        self.assertFalse(where.is_relative_to(self.project.resolve()))
        # A corepack `yarn` shim would fetch the version `packageManager` or `devEngines` names;
        # the copy keeps the dependency fields only (TASK 112 R5.1).
        self.assertEqual(package, {"name": "x", "dependencies": {"a": "1"}, "resolutions": {"b": "2"}})

    def test_y2_no_regular_package_json_or_a_linked_lockfile_runs_no_yarn(self):
        """TC-Y2 (TASK 112 R5.1)."""
        real = self.tmp / "real.lock"
        real.write_text("")
        for case in ("no package.json", "linked package.json", "linked yarn.lock"):
            with self.subTest(case=case):
                for name in ("yarn.lock", "package.json"):
                    path = self.project / name
                    if path.is_symlink() or path.exists():
                        path.unlink()
                if case == "linked yarn.lock":
                    (self.project / "yarn.lock").symlink_to(real)
                    (self.project / "package.json").write_text('{"name": "x"}')
                else:
                    (self.project / "yarn.lock").write_text("")
                    if case == "linked package.json":
                        (self.project / "package.json").symlink_to(real)
                yarn = [r for r in self.external(["javascript"]) if r[0][:1] == ["yarn"]]
                self.assertEqual(yarn, [])


class TestDependencySeverities(AuditTestCase):
    """TC-D2 to TC-D7 (TASK 118 R3): npm advisories at every severity."""

    def npm_findings(self, result):
        return [f for f in result["findings"] if f.get("type") == "npm audit"]

    def test_d2_a_moderate_advisory_fails_fail_on_medium_only(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
        run_audit = _run_audit_module()
        report = run_audit.run_full_scan(str(self.project), "deps", fail_on="medium")
        self.assertEqual(run_audit.exit_code(report, "medium"), 1)
        self.assertEqual(run_audit.exit_code(report, "high"), 0)

    def test_d3_an_info_advisory_is_audited_and_a_missing_npm_is_not(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"x": {"severity": "info"}}})
        result = self.scan()
        self.assertFalse(result["status"].startswith("[?] Not audited"), result["status"])
        self.assertEqual([f.get("audited", True) for f in self.npm_findings(result)], [True])
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
            [finding] = self.npm_findings(self.scan())
        self.assertEqual((finding["severity"], finding["audited"]), ("info", False))

    def test_d4_an_unknown_severity_and_an_entry_that_is_not_a_map(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"x": {"severity": "weird"}}})
        result = self.scan()
        self.assertEqual(result["npm_audit_counts"]["sub/package-lock.json"]["unknown"], 1)
        self.assertEqual([(f["severity"], f["message"]) for f in self.npm_findings(result)], [
            ("low", "sub/package-lock.json: 1 vulnerabilities of unknown severity")])
        self.set_reply({"vulnerabilities": {"x": "high"}})
        counts = self.scan()["npm_audit_counts"]["sub/package-lock.json"]
        self.assertEqual((counts["low"], counts["unknown"]), (1, 0))

    def test_d5_each_finished_audit_has_all_six_counts(self):
        self.lockfile("sub")
        self.assertEqual(self.scan()["npm_audit_counts"], {"sub/package-lock.json": ZERO_COUNTS})
        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "low"}}})
        self.assertEqual(self.scan()["npm_audit_counts"]["sub/package-lock.json"],
                         dict(ZERO_COUNTS, low=2))
        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
            self.assertEqual(self.scan()["npm_audit_counts"], {})

    def test_d6_section_status_first_match_wins(self):
        self.lockfile("sub")
        for label, reply, status in (
                ("critical", {"vulnerabilities": {"x": {"severity": "critical"}}},
                 "[!!] Critical vulnerabilities"),
                ("high", HIGH, "[!] HIGH: Dependency issues"),
                ("moderate", {"vulnerabilities": {"x": {"severity": "moderate"}}},
                 "[?] Dependency issues below high"),
                ("low", {"vulnerabilities": {"x": {"severity": "low"}}},
                 "[?] Dependency issues below high"),
                ("info only", {"vulnerabilities": {"x": {"severity": "info"}}}, "[OK] Secure"),
                ("none", {"vulnerabilities": {}}, "[OK] Secure")):
            with self.subTest(case=label):
                self.set_reply(reply)
                self.assertEqual(self.scan()["status"], status)
        with self.subTest(case="not audited outranks moderate"):
            self.lockfile("other", content='{"name": "broken"}')
            self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")

    def test_d7_summary_counts_low_and_info_and_findings_are_sorted(self):
        self.lockfile("sub")
        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "info"},
                                            "c": {"severity": "critical"}}})
        report = _run_audit_module().run_full_scan(str(self.project), "deps")
        summary = report["summary"]
        self.assertEqual((summary["critical"], summary["low"], summary["info"]), (1, 1, 1))
        # Two lockfiles each yield a critical and a low finding: unsorted, a low one precedes the
        # second critical one.
        self.lockfile("tub")
        self.set_reply({"vulnerabilities": {"a": {"severity": "low"},
                                            "c": {"severity": "critical"}}})
        severities = [f["severity"] for f in self.scan()["findings"]]
        self.assertEqual(severities, ["critical", "critical", "low", "low"])

    def test_d8_a_lockfile_that_cannot_be_copied_is_not_audited(self):
        sub = self.project / "sub"
        sub.mkdir()
        os.mkfifo(sub / "package-lock.json")
        (sub / "package.json").write_text('{"name": "x"}')
        [info] = self.infos(self.scan()["findings"])
        self.assertEqual((info["message"], info["audited"]),
                         ("sub/package-lock.json: not audited, the lockfile could not be copied",
                          False))
        proc = subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", "deps",
                               "--output", "json"], capture_output=True, text=True, timeout=120)
        self.assertEqual(json.loads(proc.stdout)["summary"]["scan_complete"], False)
        self.assertEqual(proc.returncode, 3, proc.stderr)


class ToolCase(unittest.TestCase):
    """A temporary project, and a `bin` directory of fake tools that is the whole `PATH`.

    The `.git` walk of `run_external_tools` stops at the temporary directory, so a `.git` above it
    takes no part.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.project = self.tmp / "project"
        self.project.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        patcher = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
        patcher.start()
        self.addCleanup(patcher.stop)
        walk = external.find_git_entry
        stopped = mock.patch.object(external, "find_git_entry",
                                    side_effect=lambda root, stop=None: walk(root, stop=self.tmp))
        stopped.start()
        self.addCleanup(stopped.stop)

    def tool(self, name, body="exit 0"):
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n")
        path.chmod(0o755)

    def tools(self, *names):
        for name in names:
            self.tool(name)

    def records(self, types=(), fail_on=None):
        return external.run_external_tools(str(self.project), list(types), fail_on=fail_on)

    @staticmethod
    def slot(records, slot):
        return [r for r in records if r["slot"] == slot]

    def cli(self, *args):
        """`run_audit.py` as a subprocess, with `PATH` the fake tools only."""
        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), *args], env=env,
                              capture_output=True, text=True, timeout=120)

    def cli_json(self, *args):
        proc = self.cli(*args, "--output", "json")
        return proc, json.loads(proc.stdout)


class TestToolRecords(ToolCase):
    """TC-E2, TC-E4 to TC-E7, TC-E9, TC-E13, TC-E15, TC-E16 drive `run_external_tools` in process."""

    def test_e2_a_tool_that_exits_0_is_ran(self):
        self.tool("semgrep")
        [record] = self.slot(self.records(), "sast")
        self.assertEqual((record["status"], record["exit_code"], record["tool"], record["where"]),
                         ("ran", 0, "semgrep", "."))
        self.assertIsNone(record["reason"])

    def test_e2_a_missing_tool_is_not_installed(self):
        [record] = self.slot(self.records(), "sast")
        self.assertEqual((record["status"], record["exit_code"]), ("not_installed", None))

    def test_e4_a_timeout_starts_the_fallback_of_the_tree_slot_only(self):
        self.tool("gitleaks", "exec /bin/sleep 5")
        self.tool("trufflehog")
        (self.project / ".git").mkdir()
        with mock.patch.object(helpers, "TOOL_TIMEOUT", 1):
            records = self.records()
        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
                         [("gitleaks", "timed_out"), ("trufflehog", "ran")])
        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-history")],
                         [("gitleaks", "timed_out")])
        self.assertIn("secrets-history", [slot for slot, _ in external.incomplete_slots(records)])

    def test_e5_the_fallback_fills_the_tree_slot_and_the_history_slot_has_none(self):
        self.tool("trufflehog")
        (self.project / ".git").mkdir()
        records = self.records()
        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
                         [("gitleaks", "not_installed"), ("trufflehog", "ran")])
        self.assertEqual([r["tool"] for r in self.slot(records, "secrets-history")], ["gitleaks"])
        missing = [slot for slot, _ in external.incomplete_slots(records)]
        self.assertIn("secrets-history", missing)
        self.assertNotIn("secrets-tree", missing)

    def test_e6_the_git_entry_at_or_above_the_root(self):
        find = external.find_git_entry.side_effect
        self.assertIsNone(find(str(self.project)))
        cases = (("a directory", lambda g: g.mkdir(), "dir"),
                 ("a file", lambda g: g.write_text("gitdir: elsewhere\n"), "file"),
                 ("a link", lambda g: g.symlink_to(self.tmp / "real", target_is_directory=True),
                  "link"),
                 ("a fifo", lambda g: os.mkfifo(g), "other"))
        (self.tmp / "real").mkdir()
        for label, make, kind in cases:
            with self.subTest(case=label):
                git = self.project / ".git"
                make(git)
                try:
                    self.assertEqual(find(str(self.project)), kind)
                finally:
                    shutil.rmtree(git) if git.is_dir() and not git.is_symlink() else git.unlink()
        with self.subTest(case="in the parent"):
            (self.tmp / ".git").mkdir()
            self.assertEqual(find(str(self.project)), "dir")
            (self.tmp / ".git").rmdir()
        with self.subTest(case="a root through a link"):
            sub = self.tmp / "repo" / "sub"
            sub.mkdir(parents=True)
            (self.tmp / "repo" / ".git").mkdir()
            (self.tmp / "alias").symlink_to(sub, target_is_directory=True)
            self.assertEqual(external.find_git_entry(str(self.tmp / "alias"), stop=self.tmp), "dir")

    def test_e6_the_history_slot_by_git_entry(self):
        log = self.tmp / "gitleaks.log"
        self.tool("gitleaks", f'printf "%s|%s\\n" "$PWD" "$*" >> "{log}"')
        [record] = self.slot(self.records(), "secrets-history")
        self.assertEqual((record["status"], record["reason"], record["command"]),
                         ("not_applicable", "no .git at or above the scanned root", GITLEAKS_HISTORY))
        (self.project / ".git").symlink_to(self.tmp, target_is_directory=True)
        [record] = self.slot(self.records(), "secrets-history")
        self.assertEqual((record["status"], record["reason"]), ("not_run", ".git is a symbolic link"))
        (self.project / ".git").unlink()
        expected = f"{self.project}|{' '.join(GITLEAKS_HISTORY[1:])}"
        cases = (("a directory at the root", lambda: (self.project / ".git").mkdir()),
                 ("a file at the root",
                  lambda: (self.project / ".git").write_text("gitdir: elsewhere\n")),
                 ("a directory in the parent", lambda: (self.tmp / ".git").mkdir()),
                 ("a bare repository at the root", lambda: self.bare(self.project)))
        for label, make in cases:
            with self.subTest(case=label):
                make()
                if log.exists():
                    log.unlink()
                try:
                    [record] = self.slot(self.records(), "secrets-history")
                    self.assertEqual((record["status"], record["command"]),
                                     ("ran", GITLEAKS_HISTORY))
                    runs = [run for run in log.read_text().splitlines() if "--no-git" not in run]
                    self.assertEqual(runs, [expected])
                finally:
                    for path in (self.project / ".git", self.tmp / ".git", self.project / "HEAD",
                                 self.project / "objects", self.project / "refs"):
                        if path.is_dir():
                            shutil.rmtree(path)
                        elif path.exists():
                            path.unlink()

    def bare(self, root):
        (root / "HEAD").write_text("ref: refs/heads/main\n")
        (root / "objects").mkdir()
        (root / "refs").mkdir()

    def test_e6_a_bare_repository_and_an_unreadable_directory(self):
        find = external.find_git_entry.side_effect
        self.bare(self.project)
        self.assertEqual(find(str(self.project)), "bare")
        shutil.rmtree(self.project / "objects")
        (self.tmp / "objects").mkdir()
        (self.project / "objects").symlink_to(self.tmp / "objects", target_is_directory=True)
        self.assertEqual(find(str(self.project)), "bare-link")
        for name in ("HEAD", "objects", "refs"):
            path = self.project / name
            shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()
        if os.geteuid() == 0:
            self.skipTest("root reads a directory without its search permission")
        locked = self.project / "locked"
        locked.mkdir()
        locked.chmod(0o600)
        self.addCleanup(locked.chmod, 0o700)
        self.assertEqual(find(str(locked)), "unreadable")

    def test_e6_each_declined_history_record(self):
        for kind, status, reason in (
                ("link", "not_run", ".git is a symbolic link"),
                ("other", "not_run", ".git is not a directory or a regular file"),
                ("unreadable", "not_run", ".git could not be read"),
                ("bare-link", "not_run", "the bare repository holds a symbolic link"),
                (None, "not_applicable", "no .git at or above the scanned root")):
            with self.subTest(kind=kind):
                external.find_git_entry.side_effect = lambda root, stop=None, kind=kind: kind
                records = self.records()
                [record] = self.slot(records, "secrets-history")
                self.assertEqual((record["status"], record["reason"], record["command"]),
                                 (status, reason, GITLEAKS_HISTORY))
                missing = [slot for slot, _ in external.incomplete_slots(records)]
                self.assertEqual("secrets-history" in missing, status == "not_run")

    def test_e7_the_tree_slot_reads_the_working_tree(self):
        self.tool("gitleaks")
        [record] = self.slot(self.records(), "secrets-tree")
        self.assertEqual(record["command"], GITLEAKS_TREE)

    def test_e9_options_that_make_a_finding_exit_non_zero(self):
        self.tools("trufflehog", "checkov", "trivy", "npm")
        lock = self.project / "package-lock.json"
        lock.write_text("{}")
        (self.project / "package.json").write_text('{"name": "x"}')
        records = self.records(["iac"])
        [tree] = [r for r in self.slot(records, "secrets-tree") if r["tool"] == "trufflehog"]
        self.assertIn("--fail", tree["command"])
        [trivy] = self.slot(records, "iac-misconfig")
        self.assertEqual(trivy["command"][-3:], ["--exit-code", "1", "."])
        for fail_on, level in ((None, None), ("medium", "moderate"), ("high", "high"),
                               ("critical", "critical")):
            with self.subTest(fail_on=fail_on):
                [npm] = self.slot(self.records(fail_on=fail_on), "npm-audit:package-lock.json")
                levels = [a for a in npm["command"] if a.startswith("--audit-level")]
                self.assertEqual(levels, [f"--audit-level={level}"] if level else [])

    def test_e13_each_skip_reason_is_a_not_run_record(self):
        self.tools("npm", "yarn")
        sub = self.project / "sub"
        sub.mkdir()
        (sub / "package-lock.json").write_text("{}")
        [npm] = self.slot(self.records(), "npm-audit:sub/package-lock.json")
        self.assertEqual((npm["status"], npm["reason"], npm["where"]),
                         ("not_run", "no package.json beside it", "sub/package-lock.json"))
        shutil.rmtree(sub)
        real = self.tmp / "real.lock"
        real.write_text("")
        lock, package = self.project / "yarn.lock", self.project / "package.json"
        for label, reason in (("link", "yarn.lock is a link or not a regular file"),
                              ("no package.json", "no package.json beside yarn.lock"),
                              ("not an object", "package.json is not a JSON object")):
            with self.subTest(case=label):
                for path in (lock, package):
                    if path.is_symlink() or path.exists():
                        path.unlink()
                if label == "link":
                    lock.symlink_to(real)
                else:
                    lock.write_text("")
                if label == "not an object":
                    package.write_text("[]")
                records = self.records(["javascript"])
                [yarn] = self.slot(records, "yarn-audit")
                self.assertEqual((yarn["status"], yarn["reason"], yarn["where"]),
                                 ("not_run", reason, "yarn.lock"))
                self.assertIn("yarn-audit", [slot for slot, _ in external.incomplete_slots(records)])
                summary = _run_audit_module().summarize(
                    {"scans": {}, "external": external.external_section(records)})
                self.assertIn(f"external yarn-audit: yarn not_run, {reason}", summary["not_run"])
        for path in (lock, package):
            if path.is_symlink() or path.exists():
                path.unlink()
        with self.subTest(case="a lockfile that cannot be copied"):
            os.mkfifo(self.project / "package-lock.json")
            package.write_text('{"name": "x"}')
            [npm] = self.slot(self.records(), "npm-audit:package-lock.json")
            self.assertEqual((npm["status"], npm["reason"]),
                             ("not_run", "the lockfile could not be copied"))

    def test_e15_three_slots_run_for_a_project_with_no_type(self):
        self.assertEqual(scanners_types(self.project), [])
        report = _run_audit_module().run_full_scan(str(self.project), "external")
        slots = [r["slot"] for r in report["external"]["tools"]]
        for slot in ("sast", "secrets-tree", "secrets-history"):
            self.assertIn(slot, slots)

    def test_e16_external_section_status(self):
        def rec(slot, status):
            return {"slot": slot, "status": status}
        section = external.external_section
        self.assertEqual(section([rec("a", "ran"), rec("b", "not_applicable")])["status"],
                         "COMPLETE")
        self.assertEqual(section([rec("a", "ran"), rec("b", "not_installed")])["status"],
                         "PARTIAL")
        self.assertEqual(section([rec("a", "not_installed"), rec("a", "ran")])["status"],
                         "COMPLETE")
        self.assertEqual(section([rec("a", "not_installed"), rec("b", "not_applicable")])["status"],
                         "NOT_RUN")


def scanners_types(project):
    return sys.modules[NAME].detect_project_types(str(project))


class TestRunAudit(ToolCase):
    """TC-E1, TC-E3, TC-E8, TC-E10 to TC-E12, TC-E14, TC-E17 drive `run_audit.py`."""

    def test_e1_every_tool_missing_is_not_run_and_exits_3(self):
        # base-fail: the base prints no report for `external` and exits 0.
        proc = self.cli("--scan-type", "external", "--output", "json")
        report = json.loads(proc.stdout)
        statuses = {r["status"] for r in report["external"]["tools"]}
        self.assertLessEqual(statuses, {"not_installed", "not_applicable"}, report["external"])
        self.assertIn("not_installed", statuses)
        self.assertEqual(report["external"]["status"], "NOT_RUN")
        self.assertEqual(report["scans"], {})
        self.assertFalse(report["summary"]["scan_complete"])
        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
        self.assertEqual(proc.returncode, 3, proc.stderr)

    def complete_python_project(self):
        (self.project / "app.py").write_text("x = 1\n")
        self.tools("semgrep", "gitleaks", "pip-audit")
        self.tool("bandit", "exit 1")

    def test_e3_a_tool_exit_fails_fail_on_and_is_listed_without_it(self):
        self.complete_python_project()
        proc = self.cli("--scan-type", "external", "--fail-on", "critical")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("[GATE] --fail-on critical:", proc.stderr)
        self.assertIn("bandit exited 1 (python-sast)", proc.stderr)
        proc, report = self.cli_json("--scan-type", "external")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(report["summary"]["tool_exits"], ["bandit exited 1 (python-sast)"])
        self.assertTrue(report["summary"]["scan_complete"], report["summary"]["not_run"])

    def test_e8_stdout_holds_one_json_document(self):
        self.tool("semgrep", "echo semgrep-stdout; exit 1")
        self.tool("gitleaks", "echo gitleaks-stdout")
        proc = self.cli("--scan-type", "external", "--output", "json", "--fail-on", "critical")
        report = json.loads(proc.stdout)
        self.assertEqual(report["scan_type"], "external")
        self.assertNotIn("semgrep-stdout", proc.stdout)
        self.assertIn("semgrep-stdout", proc.stderr)
        self.assertNotIn("[GATE]", proc.stdout)
        self.assertIn("[GATE]", proc.stderr)
        self.assertEqual(proc.returncode, 1)

    def test_e10_a_breach_and_a_part_not_run_exit_1(self):
        # The breach: the SBOM scan's medium finding for a project with no SBOM.
        proc, report = self.cli_json("--scan-type", "all", "--fail-on", "medium")
        self.assertIn("medium", [f["severity"] for f in report["scans"]["sbom"]["findings"]])
        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
        self.assertIn("[GATE] --fail-on medium:", proc.stderr)
        self.assertIn("[INCOMPLETE]", proc.stderr)
        self.assertEqual(proc.returncode, 1)

    def test_e11_deps_with_npm_missing_exits_3(self):
        sub = self.project / "sub"
        sub.mkdir()
        (sub / "package-lock.json").write_text("{}")
        (sub / "package.json").write_text('{"name": "x"}')
        proc, report = self.cli_json("--scan-type", "deps")
        self.assertEqual(report["summary"]["not_run"],
                         ["dependencies: sub/package-lock.json: not audited, npm is not installed"])
        self.assertIn("[INCOMPLETE]", proc.stderr)
        self.assertEqual(proc.returncode, 3)

    def test_e12_overall_status(self):
        run_audit = _run_audit_module()
        report = run_audit.run_full_scan(str(self.project), "external")
        self.assertTrue(report["summary"]["overall_status"].startswith("[?] INCOMPLETE: "),
                        report["summary"])
        self.complete_python_project()
        report = run_audit.run_full_scan(str(self.project), "external")
        self.assertEqual(report["summary"]["overall_status"], "[?] REVIEW RECOMMENDED")

    def test_e14_summary_prints_one_line_per_record(self):
        self.tools("semgrep", "gitleaks")
        _proc, report = self.cli_json("--scan-type", "external")
        out = self.cli("--scan-type", "external").stdout
        for record in report["external"]["tools"]:
            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
            with self.subTest(slot=record["slot"], tool=record["tool"]):
                self.assertEqual(sum(1 for x in out.splitlines() if x.startswith(line)), 1, out)
        for label in ("Critical", "High", "Medium", "Low", "Info"):
            self.assertIn(f"\n  {label}: 0\n", out)

    def test_e18_a_killed_tool_leaves_its_slot_not_run(self):
        self.tool("semgrep", "kill -9 $$")
        records = self.records()
        [record] = self.slot(records, "sast")
        self.assertEqual(record["status"], "killed")
        self.assertLess(record["exit_code"], 0)
        self.assertIn("sast", [slot for slot, _ in external.incomplete_slots(records)])

    def test_e19_printable_escapes_control_format_and_separator_characters(self):
        self.assertEqual(helpers.printable("a\x1bb\nc\u202ed\u2028e\u2029f\U000e0001g h"),
                         "a\\x1bb\\x0ac\\u202ed\\u2028e\\u2029f\\U000e0001g h")

    def test_e19_tree_text_is_escaped_in_printed_output(self):
        sub = self.project / "a\x1b[31mb"
        sub.mkdir()
        (sub / "package-lock.json").write_text("{}")
        (sub / "package.json").write_text('{"name": "x"}')
        summary = self.cli("--scan-type", "deps")
        for stream in (summary.stdout, summary.stderr):
            self.assertNotIn("\x1b", stream)
        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stderr)
        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stdout)
        proc, report = self.cli_json("--scan-type", "deps")
        self.assertNotIn("\x1b", proc.stdout)
        self.assertIn("dependencies: a\x1b[31mb/package-lock.json: not audited, npm is not installed",
                      report["summary"]["not_run"])

    def test_e17_the_summary_counts_every_finding_before_the_cut(self):
        run_audit = _run_audit_module()
        findings = [{"type": "t", "severity": "low"}] * 30 + [{"type": "t", "severity": "critical"}]
        stub = {"tool": "stub", "findings": findings, "status": "[?]"}
        with mock.patch.object(run_audit, "scan_secrets", return_value=stub):
            report = run_audit.run_full_scan(str(self.project), "secrets")
        self.assertEqual((report["summary"]["total_findings"], report["summary"]["critical"]),
                         (31, 1))
        self.assertEqual(len(report["scans"]["secrets"]["findings"]), 30)
        self.assertEqual(run_audit.exit_code(report, "critical"), 1)


class TestNonRegularFiles(ToolCase):
    """TC-F1 to TC-F3 (TASK 119 R1): a subprocess per scan type, `PATH` the fake `bin` only."""

    #: FIFOs under the scanned root, and how many of them each in-process scan reads.
    FIFOS = ("app.js", "config.json", "main.tf", ".mcp.json")
    READS = {"secrets": 3, "code_patterns": 1, "configuration": 2, "iac": 3, "mcp_agentic": 3}
    TYPES = {"secrets": "secrets", "code_patterns": "patterns", "configuration": "config",
             "iac": "iac", "mcp_agentic": "mcp"}

    def scan(self, scan_type):
        """`run_audit.py --scan-type <type>` with a 20 s timeout; a blocked scan fails the case."""
        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", scan_type,
                               "--output", "json"], env=env, capture_output=True, text=True,
                              timeout=20)

    def test_f1_each_scan_skips_a_fifo(self):
        for name in self.FIFOS:
            os.mkfifo(self.project / name)
        for section, scan_type in self.TYPES.items():
            with self.subTest(scan=scan_type):
                proc = self.scan(scan_type)
                report = json.loads(proc.stdout)
                self.assertEqual(report["scans"][section]["skipped_files"], self.READS[section],
                                 proc.stderr)
                self.assertEqual(proc.stderr.count("not a regular file"), self.READS[section],
                                 proc.stderr)

    def test_f2_a_fifo_requirements_txt_is_not_a_hash_pinned_lock(self):
        (self.project / "pyproject.toml").write_text('[project]\nname = "x"\n')
        os.mkfifo(self.project / "requirements.txt")
        report = json.loads(self.scan("deps").stdout)
        self.assertTrue(any(f.get("type") == "Missing Lock File" and "python" in f["message"]
                            for f in report["scans"]["dependencies"]["findings"]), report)

    @staticmethod
    def secret(path):
        path.write_text('const key = "' + "AKIA" + "Z" * 16 + '";\n')

    def test_f3_a_link_to_a_regular_file_is_still_read(self):
        (self.project / "sub").mkdir()
        self.secret(self.project / "sub" / "real.txt")
        (self.project / "link.js").symlink_to(self.project / "sub" / "real.txt")
        report = json.loads(self.scan("secrets").stdout)
        findings = report["scans"]["secrets"]["findings"]
        self.assertTrue(any(f.get("file", "").endswith("link.js") for f in findings), findings)

    def test_f9_a_link_out_of_the_root_is_skipped(self):
        self.secret(self.tmp / "outside.txt")
        (self.project / "out.js").symlink_to(self.tmp / "outside.txt")
        proc = self.scan("secrets")
        section = json.loads(proc.stdout)["scans"]["secrets"]
        self.assertEqual(section["findings"], [], section)
        self.assertEqual(section["skipped_files"], 1)
        self.assertIn("outside the scanned root", proc.stderr)


class TestHelperPath(AuditTestCase):
    """TC-F4 (TASK 119 R2): the fake `npm` sees the system directories, not the machine's tools."""

    def test_f4_path_is_the_fake_bin_and_the_system_directories(self):
        self.assertEqual(os.environ["PATH"].split(os.pathsep), [str(self.bin), "/usr/bin", "/bin"])


class TestOpenRegularText(unittest.TestCase):
    """TC-F6 to TC-F8 (TASK 119 R1.1)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_f6_open_passes_binary_and_noctty(self):
        seen = []

        def fake_open(path, flags, *args, **kwargs):
            seen.append(flags)
            raise OSError("stop")

        with mock.patch.object(helpers.os, "O_BINARY", 0x10000, create=True), \
                mock.patch.object(helpers.os, "O_NOCTTY", 0x20000, create=True), \
                mock.patch.object(helpers.os, "open", side_effect=fake_open):
            with self.assertRaises(OSError):
                helpers.open_regular_text(self.tmp / "x.js")
        self.assertEqual(seen[0] & 0x30000, 0x30000, hex(seen[0]))

    def test_f7_a_refusal_closes_the_descriptor(self):
        link = self.tmp / "null.js"
        link.symlink_to("/dev/null")
        before = len(os.listdir("/dev/fd"))
        for _ in range(1000):
            with self.assertRaisesRegex(OSError, "not a regular file"):
                helpers.open_regular_text(link)
        self.assertEqual(len(os.listdir("/dev/fd")), before)

    def test_f8_size_limit_on_the_descriptor_and_a_blocking_stream(self):
        big = self.tmp / "big.js"
        big.write_text("x" * 100)
        config = importlib.import_module(f"{NAME}.config")
        with mock.patch.object(config, "MAX_FILE_SIZE", 10):
            with self.assertRaisesRegex(OSError, "exceeds the size limit"):
                helpers.open_regular_text(big)
        with helpers.open_regular_text(big) as stream:
            if hasattr(os, "O_NONBLOCK"):
                import fcntl
                self.assertFalse(fcntl.fcntl(stream.fileno(), fcntl.F_GETFL) & os.O_NONBLOCK)
            self.assertEqual(stream.read(), "x" * 100)


class TestPrintableBackslash(unittest.TestCase):
    """TC-F5 (TASK 119 R3)."""

    def test_f5_printable_doubles_the_backslash(self):
        self.assertEqual(helpers.printable("\\"), "\\\\")
        self.assertEqual(helpers.printable("a\\x0ab"), "a\\\\x0ab")
        self.assertEqual(helpers.printable("a\x1bb"), "a\\x1bb")


if __name__ == "__main__":
    unittest.main()
