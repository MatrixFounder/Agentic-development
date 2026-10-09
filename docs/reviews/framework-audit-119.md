# Framework Audit 119 — The in-process scans skip a file that is not regular

- **Task:** 119 `scanner-residuals`. It archives to `docs/tasks/task-119-scanner-residuals.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-09. **Base revision:** `5d0c83f0832a7960d98d6c1a00a5e94288250725`, clean tree
  at start.
- **Source:** WI-51, with the operator's request of 2026-10-09: start WI-51, and "старайся не
  раздувать задач, потому что правки не такие сложные".

## 0. Emergency Bypass

None.

## Archive (§1)

TASK 118 and PLAN 118 archived under ID 118 (`task_id_tool.py` `generated`):
`archive_move.py` twice, `"ok": true`; Step 5.5: 6 rewritten, exit 0; Step 7.6.5: 1
`SLOT_RESOLVED`, exit 0; Step 8 with `--since e1fb362…`: exit 3, 2 `INBOUND` records in the
v3.13.0 changelog entries, which carry no reason and stay. Step 8 rewrote no file.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent at fingerprint `1e63dcef7a39`. No §4 failure condition. Three
MAJOR: TC-F2 had no time limit and could hang the base-fail run; TC-F1 ran `--scan-type all`,
which starts real external tools; R7.2 pulled in TASK 118 R7 whole, whose files and renames differ.
Five MINOR: `O_NONBLOCK` on Windows; D3 named the routes by number; a blockquote on an open
record; per-section counts; `System/Docs` not stated. Revision 2 applies all eight: subprocess
cases per scan type with the fake `bin` as `PATH`; R7.2 to R7.4 state the differences and the
mutants; `getattr(os, "O_NONBLOCK", 0)`; WI-52 for the `mcp-scan` target; R6.4.

### Round 2 — TASK revision 2: PASS

The same agent at `12a8c1afe1ec`. Findings 1 to 8 RESOLVED. One MINOR: R7.4 took fewer sections of
TASK 118 R7 than R7.2 changes. Revision 3 rewords R7.4 to TASK 118 R7.2 to R7.11, and shortens the
subprocess timeout to 20 s: a scan of the fixture ends in seconds, and the base-fail run waits out
six timeouts.

**Mode A verdict:** APPROVED, TASK revision 3.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

A read-only `plan-reviewer` at `9c8810030c62`. Two MAJOR: B1 wrote R2.1's `PATH` with TC-F4, so
TC-F4 could not be Red, and C1's base set was wrong; the stage-3 restore was not planned. Five
MINOR: "renames"; the load order of mode `next`; no mutant for TC-F3; no register check for D1 and
E2; the caches and gate logs. PLAN revision 2 and TASK revision 4 apply all seven. `plan_gantt.py
--check`: exit 0.

### Round 2 — PLAN revision 2: PASS

The same agent at `d5c4f99e150c`. Findings 1 to 7 RESOLVED. One MINOR: G1 stated no result for a
hash mismatch at step 2 or a failed `git apply` at step 4. PLAN revision 3 states both, as PLAN 118
I1 does.

**Mode B verdict:** APPROVED, PLAN revision 3.

## §3 — Execution

- A1: `HEAD` equals the base; the edited paths are tracked; the created paths give
  `git check-ignore` exit 1. A2: three byte copies; the driver, mode `next` (staged `.helpers` and
  `.scanners`, final `__init__.py` and `.external`, with the identity checks of PLAN A2) and mode
  `base`: 59 cases each, 0 failures.
- B1, tests first: TC-F1 (five types) and TC-F2 error on their 20 s timeout, TC-F4 and TC-F5 fail,
  TC-F3 passes. B2: `open_regular_text`, the backslash escape, the six sites, the helper's `PATH`.
  The driver, mode `next`: 64 cases, 0 failures.
- C1, mode `base`: TC-F1 (five types) and TC-F2 error on the timeout, TC-F5 fails; no other case
  fails. TC-F3 passes, as TASK A2 states; TC-F4 passes because the `PATH` lives in the staged test
  module.
- C2: 6 of 6 mutants killed (a scan site keeps `open()`, the `requirements.txt` check keeps
  `open()`, no type check, the real `PATH`, no backslash escape, `O_NOFOLLOW`); SHA-256 equal after
  the restore. The first build of the first mutant named a wrong context and stopped before any
  write; it was rebuilt.
- D1 to D3: §2 (non-regular files, the backslash, the "no report" sentence); v3.40.1 in both
  changelogs; WI-51 done; WI-52 filed. Register: 0 `WARN` on added lines of the six files.
- E1: the patch, 6 sections; `git apply --check` passes. E2: `run_gates.sh` 17 PASS; the skill's
  tests 30 passed; every path of `git status` is declared.

### Stage 2, round 1 — fingerprint `ddd4aedea36e`

Both agents quoted the fingerprint and the four prefixes at their start and end; equal on return.

**Code review: CHANGES REQUESTED.** MAJOR: on Windows `os.open` without `O_BINARY` opens in text
mode, and a read stops at the first `0x1A`; the base `open()` read binary. MINOR: WI-52's
frontmatter is not valid YAML (`\'`); §2 and the changelogs say a socket is named `not a regular
file`, but `os.open` raises its own error; no test pins the descriptor's close.

**Security audit: PASS**, `scan_status: findings`. The scan ran with the tools installed: exit 0,
`external.status` COMPLETE, `not_run` empty; the tool exits are findings, none in a changed file;
bandit's LOW hits in the staged files are argument-list `subprocess` calls. FIFOs, links to
devices and a socket were skipped by every scan type within 0.1 s; 3,000 refusals left the
descriptor count unchanged. MEDIUM-1, kept by R1.3 and not a regression: a link to a file outside
the scanned root is read, and its matched line reaches the report. LOW-1: the size gate stats the
path, and the read is unbounded. INFO: `O_NOCTTY`; `O_NONBLOCK` left on the stream; the socket
wording; `printable` leaves Zs and Mn characters; `{e}` of the skip line is not escaped (safe:
the error text uses `repr`).

The auditor's script ran under `python3 -I`, which ignores `PYTHONDONTWRITEBYTECODE`, and wrote
four ignored `.pyc` files under `audit/__pycache__/`. The two of the staged modules were deleted;
the other two belong to tracked modules.

### Fix round 1

TASK revision 5 and PLAN revision 4 state it. Dispositions: the MAJOR, the three MINOR items, LOW-1,
`O_NOCTTY`, `O_NONBLOCK` and the socket wording are fixed; MEDIUM-1 goes to WI-53; Zs, Mn and `{e}`
are accepted as INFO.

- Tests first: TC-F6 (flags) and TC-F8 (size on the descriptor, blocking stream) failed against
  the code of round 1; TC-F7 (descriptor closed) passed at once, and its mutant below fails.
- Code: `_OPEN_FLAGS` (`O_NONBLOCK`, `O_NOCTTY`, `O_BINARY`, each where the platform has it); the
  size check against `config.MAX_FILE_SIZE` on `fstat`; `os.set_blocking(fd, True)` where
  `O_NONBLOCK` exists. The driver, mode `next`: 67 cases, 0 failures.
- Documents: §2 and both changelogs name the reason on stderr, not one fixed text, and scope the
  sentence to the five scans; WI-52's `value` uses U+2019, and `yaml.safe_load` reads WI-51, WI-52
  and WI-53; WI-53 filed with its index line.
- Mode `base`: 67 cases; the new cases TC-F1, TC-F2 and TC-F5 to TC-F8 fail or error; TC-F3 and
  TC-F4 pass, as stated; no other case fails. Mutations: 9 of 9 killed; SHA-256 equal after the
  restore. The patch regenerated, 6 sections, `git apply --check` passes. `run_gates.sh` 17 PASS;
  the skill's tests 30 passed; register 0 `WARN` on added lines; 16 paths, each declared.

### Stage 2, round 2 — fingerprint `5b58dd154290`

Both agents, resumed, quoted the fingerprint and the prefixes at their start and end; equal.

- **Code review: APPROVED.** Findings 1 to 4 RESOLVED. LOW: the docstring of
  `open_regular_text` says the size cannot change between the check and the read; a file that
  grows after `fstat` is read in full.
- **Security audit: PASS**, `scan_status: findings` (round 1's scan stands; the only changed
  scanned file is in the scanner's self-excluded directory). LOW-1 mostly RESOLVED: the size is the
  opened file's; a file that grows after the open, and Linux procfs through a link, are still read
  in full. INFO-6: a hash-pinned `requirements.txt` above `--max-size` now reads as no lock, a
  fail-closed false positive. O_NOCTTY, the blocking stream and the stderr wording RESOLVED.

**Operator decisions (2026-10-09), quoted.** The operator objected: "я вижу, что ты создал wi-52 и
wi-53. Мы так никогда не закроем задачу. Это надо решить и обозначить четко границы". Asked:

- D5, the boundary of TASK 119: "Только свои строки (Recommended)". The task holds WI-51 and the
  review findings in the lines it changes. Every other finding is one line in this record, marked
  as before the task; a new backlog record needs the operator's decision.
- D6, WI-53: "Исправить в TASK 119 (Recommended)". A file whose real path leaves the scanned root
  is skipped and counted; the record WI-53, never committed, is removed.
- D7, WI-52: "Удалить, строка в SKILL.md (Recommended)". The record, never committed, is removed;
  §2 states that the target of the `mcp-scan` fallback is not verified.

Under D5: the docstring LOW is fixed (its line changes); a file that grows after its open is the
read, not the open, and stays, as before the task; INFO-6 is in a changed line, fails closed and
needs a file above `--max-size`: accepted.

### Fix round 2

TASK revision 6 and PLAN revision 5 state it. Round 3 of stage 2 is the last of the bound.

- Tests first: TC-F9 (a link out of the root) failed against the code of round 2; TC-F3 now links
  inside the root and passes.
- Code: `open_regular_text(path, root)` refuses a real path outside the real path of `root`
  before any open, with `outside the scanned root`, and opens the real path; the six sites pass
  `project_path` or `base`. The docstring states that the size is the opened file's, at the open.
  The driver, mode `next`: 68 cases, 0 failures.
- Documents: §2 (the root rule; the `mcp-scan` line of D7), both changelogs, WI-51's blockquote.
  WI-52 and WI-53, never committed, are removed with their index lines.
- Mode `base`: the new cases TC-F1, TC-F2 and TC-F5 to TC-F9 fail or error; TC-F3 and TC-F4 pass.
  Mutations: 10 of 10 killed. The `O_NOFOLLOW` mutant was replaced: the real path is opened, so the
  flag no longer reaches a link; "the root check refuses every file" kills TC-F3 instead. The first
  run stopped at a site whose text the root argument changed, before any write.
- The patch regenerated, 6 sections, `git apply --check` passes; `run_gates.sh` 17 PASS; the
  skill's tests 30 passed; register 0 `WARN` on added lines; 14 paths, each declared.

### Stage 2, round 3 — fingerprint `f20c1a7a9b9b`

Both agents, resumed, quoted the fingerprint and the prefixes at their start and end; equal.

- **Code review: APPROVED.** The round-2 LOW RESOLVED. The root check was probed against a link
  out, a sibling `proj2` beside `proj`, a hop out and back in, dangling links in and out, a self
  link, `root="/"`, a root through a link or with a trailing slash, and `root="."`: each as R1.1
  states.
- **Security audit: PASS**, `scan_status: findings` (round 1's scan; the change is in the
  scanner's self-excluded directory). MEDIUM-1 RESOLVED: the round-1 fixture is skipped and emits
  no snippet. Prefix confusion, `..`, a relative link out and a chain out and back held. On a
  case-insensitive macOS volume, a link to an inside file spelled in another case is refused: a
  false refusal, counted and named.

Both agents name one LOW: a writer that swaps a directory of the checked path for a link between
`realpath` and `os.open` gets an outside file read. The audit adds an INFO: a hard link inside the
tree to an outside file is read; git carries no hard link. Both need write access to the tree
during or before the scan, the class of the round-2 LOW about a file that grows after its open;
they are accepted under D5, and no fix round follows: round 3 is the last of the bound.

**Stage 2 passes.**

## §4 — Documentation

`System/Docs` does not change (TASK R6.4, D2). No workflow or skill is added. No core prompt
changes, so no restart is needed for this task.

## Stage 3

### G1 — before the apply

1. §4.5: `check_positional_refs.py --targets-changed`, then with `--fix`; no `REFERENT_MOVED`; the
   fingerprint is the same before and after `--fix`, so no file was repaired. The errors the
   resolver reports are references to files of other repositories in old changelog entries and
   archived documents, as in TASK 118.
2. The patch and the staged files hash to the values round 3 quoted:

   ```text
   3ab4c8fbca34d42415124e0b52cd683fc7b8c8fe57645b771005be6be09b4fe3  docs/reviews/framework-audit-119-stage3.diff
   6eeed0641925e12fa16012af4e001d7848d246e8e5c9fcee32b4458958613b55  .agent/skills/security-audit/scripts/audit/helpers_next.py
   d77f1cc950a77d37b7cfb4f56f705dc38a214390dfa767cc653b1448a9a11073  .agent/skills/security-audit/scripts/audit/scanners_next.py
   ecd7c02178e7ef2099a6817198a0b63d22ea2389067d7de7e5038478da65103f  tests/staged_lockfile_audit.py
   ```

3. SHA-256 and mode of every file the patch touches, before the apply:

   | File | SHA-256 | Mode |
   | :--- | :--- | :--- |
   | `.agent/skills/security-audit/scripts/audit/helpers.py` | `22884bbfef9c8aa386ba20587ce4c078c75556b948129da43c451e6bf4be29e0` | `644` |
   | `.agent/skills/security-audit/scripts/audit/scanners.py` | `8f51b2b11888aa779e9d1ea28c81457c4469cc7b23d6fd62b823b11d5af44606` | `644` |
   | `tests/test_lockfile_audit.py` | `1bc4c753a2ec67ed267088f72329a05c6ea36257e69f47677a85694597a15cfe` | `644` |
   | `.agent/skills/security-audit/scripts/audit/helpers_next.py` | `6eeed0641925e12fa16012af4e001d7848d246e8e5c9fcee32b4458958613b55` | `644` |
   | `.agent/skills/security-audit/scripts/audit/scanners_next.py` | `d77f1cc950a77d37b7cfb4f56f705dc38a214390dfa767cc653b1448a9a11073` | `644` |
   | `tests/staged_lockfile_audit.py` | `ecd7c02178e7ef2099a6817198a0b63d22ea2389067d7de7e5038478da65103f` | `644` |

The patch text, as applied:

~~~~diff
diff --git a/.agent/skills/security-audit/scripts/audit/helpers.py b/.agent/skills/security-audit/scripts/audit/helpers.py
--- a/.agent/skills/security-audit/scripts/audit/helpers.py
+++ b/.agent/skills/security-audit/scripts/audit/helpers.py
@@ -4,6 +4,7 @@
 import os
 import unicodedata
 import shutil
+import stat
 import subprocess
 import sys
 import tempfile
@@ -11,6 +12,7 @@
 from pathlib import Path
 from typing import Dict, Iterator, List, Optional
 
+from . import config as _config
 from .config import (
     MCP_CONFIG_FILENAMES,
     SELF_DIR,
@@ -67,11 +69,14 @@
 
     A path or a message from the scanned tree can hold a newline, an ANSI escape, a bidirectional
     override or a line separator, and with it forge a line of the scanner's output. The categories
-    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`.
+    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`, and a backslash is doubled.
     """
     out = []
     for char in str(text):
-        if unicodedata.category(char) in ESCAPED_CATEGORIES:
+        if char == "\\":
+            # A literal backslash is doubled, so it never reads as an escape (TASK 119 R3).
+            out.append("\\\\")
+        elif unicodedata.category(char) in ESCAPED_CATEGORIES:
             code = ord(char)
             if code <= 0xFF:
                 out.append(f"\\x{code:02x}")
@@ -125,6 +130,44 @@
                 found.append(path)
                 break
     return found
+
+
+#: Flags of `open_regular_text`, each where the platform has it: a FIFO does not wait, a terminal
+#: does not become the controlling one, and Windows reads past a 0x1A byte, as `open()` does.
+_OPEN_FLAGS = ("O_NONBLOCK", "O_NOCTTY", "O_BINARY")
+
+
+def open_regular_text(path, root=None):
+    """A UTF-8 text stream of `path` when it is a regular file (TASK 119 R1).
+
+    With `root`, a path whose real path leaves the real path of `root` is refused before any open,
+    and the real path is opened (D6). The open does not wait on a FIFO. `fstat` then checks the
+    opened descriptor: its type, which cannot change after the open, and its size at the open. A
+    link to a regular file inside `root` is followed, as `open()` does. Each refusal raises
+    `OSError`, which each caller already reports as a skipped file.
+    """
+    if root is not None:
+        real = os.path.realpath(path)
+        base = os.path.realpath(root)
+        if real != base and not real.startswith(base.rstrip(os.sep) + os.sep):
+            raise OSError("outside the scanned root")
+        path = real
+    flags = os.O_RDONLY
+    for name in _OPEN_FLAGS:
+        flags |= getattr(os, name, 0)
+    fd = os.open(path, flags)
+    try:
+        info = os.fstat(fd)
+        if not stat.S_ISREG(info.st_mode):
+            raise OSError("not a regular file")
+        if info.st_size > _config.MAX_FILE_SIZE:
+            raise OSError("exceeds the size limit")
+        if getattr(os, "O_NONBLOCK", 0):
+            os.set_blocking(fd, True)
+        return os.fdopen(fd, "r", encoding="utf-8", errors="ignore")
+    except BaseException:
+        os.close(fd)
+        raise
 
 
 class LockfileCopyError(Exception):
diff --git a/.agent/skills/security-audit/scripts/audit/scanners.py b/.agent/skills/security-audit/scripts/audit/scanners.py
--- a/.agent/skills/security-audit/scripts/audit/scanners.py
+++ b/.agent/skills/security-audit/scripts/audit/scanners.py
@@ -24,6 +24,7 @@
     find_npm_lockfiles,
     is_self_path,
     npm_audit_dir,
+    open_regular_text,
     printable,
     shannon_entropy,
     sort_findings_by_severity,
@@ -162,7 +163,7 @@
         if not req.exists():
             return False
         try:
-            with open(req, 'r', encoding='utf-8', errors='ignore') as f:
+            with open_regular_text(req, base) as f:
                 # Stop scanning after 1MB; hash lines appear early in real pip-compile output.
                 sample = f.read(1024 * 1024)
             return '--hash=sha256:' in sample
@@ -247,7 +248,7 @@
             results["scanned_files"] += 1
 
             try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
+                with open_regular_text(filepath, project_path) as f:
                     content = f.read()
                     # ReDoS guard: filter out pathologically long lines before regex.
                     # All SECRET_PATTERNS are line-local (no multi-line matches in the
@@ -340,7 +341,7 @@
             results["scanned_files"] += 1
 
             try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
+                with open_regular_text(filepath, project_path) as f:
                     lines = f.readlines()
                     for line_num, line in enumerate(lines, 1):
                         # ReDoS guard: skip pathologically long lines (minified bundles, token blobs).
@@ -400,7 +401,7 @@
                 continue
 
             try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
+                with open_regular_text(filepath, project_path) as f:
                     content = f.read()
                     for pattern, issue, severity, cwe in CONFIG_PATTERNS:
                         if re.search(pattern, content, re.IGNORECASE):
@@ -458,7 +459,7 @@
             results["scanned_files"] += 1
 
             try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
+                with open_regular_text(filepath, project_path) as f:
                     content = f.read()
 
                     # ReDoS guard: IaC patterns may span lines (re.MULTILINE). Instead of
@@ -612,7 +613,7 @@
             results["scanned_files"] += 1
 
             try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
+                with open_regular_text(filepath, project_path) as f:
                     content = f.read()
 
                 rel = str(filepath.relative_to(project_path))
diff --git a/tests/test_lockfile_audit.py b/tests/test_lockfile_audit.py
--- a/tests/test_lockfile_audit.py
+++ b/tests/test_lockfile_audit.py
@@ -41,7 +41,20 @@
   lockfile that cannot be copied is not audited, and the scanner still prints its report
   (``TC-D8``);
 * a tool killed by a signal leaves its slot a part not run (``TC-E18``), and text from the scanned
-  tree reaches printed output with its control characters escaped (``TC-E19``).
+  tree reaches printed output with its control characters escaped (``TC-E19``, ``TC-E19b``).
+
+TASK 119 (WI-51) adds:
+
+* an in-process scan skips a file that is not regular, such as a FIFO, and counts it in
+  `skipped_files`; the run never blocks on it (``TC-F1``, ``TC-F2``); a link to a regular file in
+  the scanned root is still read (``TC-F3``), and one whose real path leaves the root is skipped
+  (``TC-F9``);
+* `AuditTestCase` runs the fake `npm` with `PATH` the fake `bin`, `/usr/bin` and `/bin` only
+  (``TC-F4``);
+* `printable` escapes the backslash (``TC-F5``);
+* `open_regular_text` opens with `O_BINARY` and `O_NOCTTY` where the platform has them, closes the
+  descriptor of a refused file, and checks the size limit on the opened descriptor (``TC-F6`` to
+  ``TC-F8``).
 
 `RUN_AUDIT_PATH` and `RUN_AUDIT_CMD` name the `run_audit.py` that the tests load and start; a test
 reads them at call time. The in-process cases stop the `.git` walk at their temporary directory;
@@ -131,7 +144,9 @@
         self.log = self.tmp / "npm.log"
         self.reply = self.tmp / "reply.json"
         self.set_reply({"vulnerabilities": {}})
-        env = {"PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
+        # The fake `npm` calls `ls`, `tr`, `cat` and `grep`; a tool installed elsewhere, such as
+        # under `/opt/homebrew/bin`, must not start in a case (TASK 119 R2).
+        env = {"PATH": os.pathsep.join((str(self.bin), "/usr/bin", "/bin")),
                "FAKE_NPM_LOG": str(self.log), "FAKE_NPM_REPLY": str(self.reply)}
         patcher = mock.patch.dict(os.environ, env)
         patcher.start()
@@ -930,5 +945,122 @@
         self.assertEqual(run_audit.exit_code(report, "critical"), 1)
 
 
+class TestNonRegularFiles(ToolCase):
+    """TC-F1 to TC-F3 (TASK 119 R1): a subprocess per scan type, `PATH` the fake `bin` only."""
+
+    #: FIFOs under the scanned root, and how many of them each in-process scan reads.
+    FIFOS = ("app.js", "config.json", "main.tf", ".mcp.json")
+    READS = {"secrets": 3, "code_patterns": 1, "configuration": 2, "iac": 3, "mcp_agentic": 3}
+    TYPES = {"secrets": "secrets", "code_patterns": "patterns", "configuration": "config",
+             "iac": "iac", "mcp_agentic": "mcp"}
+
+    def scan(self, scan_type):
+        """`run_audit.py --scan-type <type>` with a 20 s timeout; a blocked scan fails the case."""
+        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
+        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", scan_type,
+                               "--output", "json"], env=env, capture_output=True, text=True,
+                              timeout=20)
+
+    def test_f1_each_scan_skips_a_fifo(self):
+        for name in self.FIFOS:
+            os.mkfifo(self.project / name)
+        for section, scan_type in self.TYPES.items():
+            with self.subTest(scan=scan_type):
+                proc = self.scan(scan_type)
+                report = json.loads(proc.stdout)
+                self.assertEqual(report["scans"][section]["skipped_files"], self.READS[section],
+                                 proc.stderr)
+                self.assertEqual(proc.stderr.count("not a regular file"), self.READS[section],
+                                 proc.stderr)
+
+    def test_f2_a_fifo_requirements_txt_is_not_a_hash_pinned_lock(self):
+        (self.project / "pyproject.toml").write_text('[project]\nname = "x"\n')
+        os.mkfifo(self.project / "requirements.txt")
+        report = json.loads(self.scan("deps").stdout)
+        self.assertTrue(any(f.get("type") == "Missing Lock File" and "python" in f["message"]
+                            for f in report["scans"]["dependencies"]["findings"]), report)
+
+    @staticmethod
+    def secret(path):
+        path.write_text('const key = "' + "AKIA" + "Z" * 16 + '";\n')
+
+    def test_f3_a_link_to_a_regular_file_is_still_read(self):
+        (self.project / "sub").mkdir()
+        self.secret(self.project / "sub" / "real.txt")
+        (self.project / "link.js").symlink_to(self.project / "sub" / "real.txt")
+        report = json.loads(self.scan("secrets").stdout)
+        findings = report["scans"]["secrets"]["findings"]
+        self.assertTrue(any(f.get("file", "").endswith("link.js") for f in findings), findings)
+
+    def test_f9_a_link_out_of_the_root_is_skipped(self):
+        self.secret(self.tmp / "outside.txt")
+        (self.project / "out.js").symlink_to(self.tmp / "outside.txt")
+        proc = self.scan("secrets")
+        section = json.loads(proc.stdout)["scans"]["secrets"]
+        self.assertEqual(section["findings"], [], section)
+        self.assertEqual(section["skipped_files"], 1)
+        self.assertIn("outside the scanned root", proc.stderr)
+
+
+class TestHelperPath(AuditTestCase):
+    """TC-F4 (TASK 119 R2): the fake `npm` sees the system directories, not the machine's tools."""
+
+    def test_f4_path_is_the_fake_bin_and_the_system_directories(self):
+        self.assertEqual(os.environ["PATH"].split(os.pathsep), [str(self.bin), "/usr/bin", "/bin"])
+
+
+class TestOpenRegularText(unittest.TestCase):
+    """TC-F6 to TC-F8 (TASK 119 R1.1)."""
+
+    def setUp(self):
+        self.tmp = Path(tempfile.mkdtemp())
+        self.addCleanup(shutil.rmtree, self.tmp)
+
+    def test_f6_open_passes_binary_and_noctty(self):
+        seen = []
+
+        def fake_open(path, flags, *args, **kwargs):
+            seen.append(flags)
+            raise OSError("stop")
+
+        with mock.patch.object(helpers.os, "O_BINARY", 0x10000, create=True), \
+                mock.patch.object(helpers.os, "O_NOCTTY", 0x20000, create=True), \
+                mock.patch.object(helpers.os, "open", side_effect=fake_open):
+            with self.assertRaises(OSError):
+                helpers.open_regular_text(self.tmp / "x.js")
+        self.assertEqual(seen[0] & 0x30000, 0x30000, hex(seen[0]))
+
+    def test_f7_a_refusal_closes_the_descriptor(self):
+        link = self.tmp / "null.js"
+        link.symlink_to("/dev/null")
+        before = len(os.listdir("/dev/fd"))
+        for _ in range(1000):
+            with self.assertRaisesRegex(OSError, "not a regular file"):
+                helpers.open_regular_text(link)
+        self.assertEqual(len(os.listdir("/dev/fd")), before)
+
+    def test_f8_size_limit_on_the_descriptor_and_a_blocking_stream(self):
+        big = self.tmp / "big.js"
+        big.write_text("x" * 100)
+        config = importlib.import_module(f"{NAME}.config")
+        with mock.patch.object(config, "MAX_FILE_SIZE", 10):
+            with self.assertRaisesRegex(OSError, "exceeds the size limit"):
+                helpers.open_regular_text(big)
+        with helpers.open_regular_text(big) as stream:
+            if hasattr(os, "O_NONBLOCK"):
+                import fcntl
+                self.assertFalse(fcntl.fcntl(stream.fileno(), fcntl.F_GETFL) & os.O_NONBLOCK)
+            self.assertEqual(stream.read(), "x" * 100)
+
+
+class TestPrintableBackslash(unittest.TestCase):
+    """TC-F5 (TASK 119 R3)."""
+
+    def test_f5_printable_doubles_the_backslash(self):
+        self.assertEqual(helpers.printable("\\"), "\\\\")
+        self.assertEqual(helpers.printable("a\\x0ab"), "a\\\\x0ab")
+        self.assertEqual(helpers.printable("a\x1bb"), "a\\x1bb")
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/.agent/skills/security-audit/scripts/audit/helpers_next.py b/.agent/skills/security-audit/scripts/audit/helpers_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/helpers_next.py
+++ /dev/null
@@ -1,223 +0,0 @@
-"""Utility functions for the security audit scanner."""
-
-import math
-import os
-import unicodedata
-import shutil
-import stat
-import subprocess
-import sys
-import tempfile
-from contextlib import contextmanager
-from pathlib import Path
-from typing import Dict, Iterator, List, Optional
-
-from . import config as _config
-from .config import (
-    MCP_CONFIG_FILENAMES,
-    SELF_DIR,
-    SEVERITY_ORDER,
-    SKIP_DIRS,
-    IAC_FILENAMES,
-)
-
-
-#: Seconds one external tool may run before its record says `timed_out` (TASK 118 R1.1).
-#: `run_tool` reads it at each call. External SAST tools like semgrep can exceed 120 s on a
-#: non-trivial repository; a shorter limit killed them mid-scan.
-TOOL_TIMEOUT = 600
-
-
-def run_tool(cmd: List[str], cwd: str, slot: str, where: str = ".") -> Dict:
-    """Run one external tool and return its tool record (TASK 118 R1.1).
-
-    The record's `status` is `ran` with the tool's `exit_code`, `not_installed` when the executable
-    is not found, or `timed_out` past `TOOL_TIMEOUT`. The tool's stdout goes to file descriptor 2,
-    beside its stderr, so the scanner's stdout holds its report alone (R1.9).
-    """
-    record = {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where,
-              "status": "ran", "exit_code": None, "reason": None}
-    cmd_str = " ".join(cmd)
-    print(f"[*] Running: {cmd_str}", file=sys.stderr)
-    sys.stderr.flush()
-    try:
-        result = subprocess.run(cmd, cwd=cwd, check=False, timeout=TOOL_TIMEOUT, stdout=2)
-    except FileNotFoundError:
-        print(f"[!] Tool not found: {cmd[0]}", file=sys.stderr)
-        record["status"] = "not_installed"
-        return record
-    except subprocess.TimeoutExpired:
-        print(f"[!] Timeout: {cmd_str} exceeded {TOOL_TIMEOUT}s limit", file=sys.stderr)
-        record["status"] = "timed_out"
-        return record
-    record["exit_code"] = result.returncode
-    if result.returncode < 0:
-        # A signal ended the process: the tool did not finish its scan (TASK 118 D13).
-        record["status"] = "killed"
-        print(f"[!] {cmd_str} was killed by signal {-result.returncode}", file=sys.stderr)
-    elif result.returncode != 0:
-        print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
-    return record
-
-
-#: The Unicode categories `printable` escapes: control, format, line and paragraph separator.
-ESCAPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")
-
-
-def printable(text) -> str:
-    """`text` with each control, format or separator character escaped (TASK 118 R1.10).
-
-    A path or a message from the scanned tree can hold a newline, an ANSI escape, a bidirectional
-    override or a line separator, and with it forge a line of the scanner's output. The categories
-    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`, and a backslash is doubled.
-    """
-    out = []
-    for char in str(text):
-        if char == "\\":
-            # A literal backslash is doubled, so it never reads as an escape (TASK 119 R3).
-            out.append("\\\\")
-        elif unicodedata.category(char) in ESCAPED_CATEGORIES:
-            code = ord(char)
-            if code <= 0xFF:
-                out.append(f"\\x{code:02x}")
-            elif code <= 0xFFFF:
-                out.append(f"\\u{code:04x}")
-            else:
-                out.append(f"\\U{code:08x}")
-        else:
-            out.append(char)
-    return "".join(out)
-
-
-def is_self_path(filepath: str) -> bool:
-    """Check if file is within the scanner's own directory (false positive prevention)."""
-    try:
-        return str(Path(filepath).resolve()).startswith(SELF_DIR)
-    except (OSError, ValueError):
-        return False
-
-
-def sort_findings_by_severity(findings: List[Dict]) -> List[Dict]:
-    """Sort findings by severity (critical first) to ensure important items are not truncated."""
-    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "low"), 99))
-
-
-def shannon_entropy(s: str) -> float:
-    """Calculate Shannon entropy of a string."""
-    if not s:
-        return 0.0
-    prob = [float(s.count(c)) / len(s) for c in set(s)]
-    return -sum(p * math.log2(p) for p in prob if p > 0)
-
-
-#: npm lockfiles in the order npm reads them: `npm-shrinkwrap.json` wins over `package-lock.json`.
-NPM_LOCKFILES = ("npm-shrinkwrap.json", "package-lock.json")
-
-
-def find_npm_lockfiles(root_dir: str) -> List[Path]:
-    """One npm lockfile per directory under `root_dir` (TASK 111 R5.1).
-
-    The audit of a lockfile below the root was missing: `npm audit` ran at the root only. Skips the
-    directories of `SKIP_DIRS`, `node_modules` among them, and follows no symbolic link, to a
-    directory or to a lockfile. A directory holding both lockfiles yields `npm-shrinkwrap.json`.
-    """
-    found = []
-    for root, dirs, files in os.walk(root_dir, followlinks=False):
-        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
-        for name in NPM_LOCKFILES:
-            path = Path(root) / name
-            if name in files and not path.is_symlink():
-                found.append(path)
-                break
-    return found
-
-
-#: Flags of `open_regular_text`, each where the platform has it: a FIFO does not wait, a terminal
-#: does not become the controlling one, and Windows reads past a 0x1A byte, as `open()` does.
-_OPEN_FLAGS = ("O_NONBLOCK", "O_NOCTTY", "O_BINARY")
-
-
-def open_regular_text(path, root=None):
-    """A UTF-8 text stream of `path` when it is a regular file (TASK 119 R1).
-
-    With `root`, a path whose real path leaves the real path of `root` is refused before any open,
-    and the real path is opened (D6). The open does not wait on a FIFO. `fstat` then checks the
-    opened descriptor: its type, which cannot change after the open, and its size at the open. A
-    link to a regular file inside `root` is followed, as `open()` does. Each refusal raises
-    `OSError`, which each caller already reports as a skipped file.
-    """
-    if root is not None:
-        real = os.path.realpath(path)
-        base = os.path.realpath(root)
-        if real != base and not real.startswith(base.rstrip(os.sep) + os.sep):
-            raise OSError("outside the scanned root")
-        path = real
-    flags = os.O_RDONLY
-    for name in _OPEN_FLAGS:
-        flags |= getattr(os, name, 0)
-    fd = os.open(path, flags)
-    try:
-        info = os.fstat(fd)
-        if not stat.S_ISREG(info.st_mode):
-            raise OSError("not a regular file")
-        if info.st_size > _config.MAX_FILE_SIZE:
-            raise OSError("exceeds the size limit")
-        if getattr(os, "O_NONBLOCK", 0):
-            os.set_blocking(fd, True)
-        return os.fdopen(fd, "r", encoding="utf-8", errors="ignore")
-    except BaseException:
-        os.close(fd)
-        raise
-
-
-class LockfileCopyError(Exception):
-    """The lockfile or its `package.json` could not be copied, such as a FIFO (TASK 118 D16)."""
-
-
-@contextmanager
-def npm_audit_dir(lockfile: Path) -> Iterator[Optional[Path]]:
-    """A temporary directory holding copies of `lockfile` and its `package.json` (TASK 111 R5.2).
-
-    npm reads `.npmrc` from the directory it runs in, and an audited subdirectory may be vendored
-    code: its `.npmrc` could redirect the registry or the cache. A copy leaves it behind; the
-    operator's own npm configuration still applies. Yields `None` when no regular `package.json`
-    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead. Raises
-    `LockfileCopyError` when a copy raises `OSError`; `shutil` refuses a FIFO before it opens one.
-    """
-    package = lockfile.parent / "package.json"
-    if not package.is_file() or package.is_symlink():
-        yield None
-        return
-    with tempfile.TemporaryDirectory(prefix="npm-audit-") as tmp:
-        try:
-            shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
-            shutil.copyfile(package, Path(tmp) / "package.json")
-        except OSError as exc:
-            raise LockfileCopyError(str(exc)) from exc
-        yield Path(tmp)
-
-
-def detect_project_types(root_dir: str) -> List[str]:
-    """Detect project types based on file extensions and config files."""
-    types = set()
-    for root, dirs, files in os.walk(root_dir, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-        if any(f.endswith(".sol") for f in files):
-            types.add("solidity")
-        if any(f.endswith(".py") for f in files):
-            types.add("python")
-        if any(f.endswith(".js") or f.endswith(".ts") for f in files):
-            types.add("javascript")
-        if any(f.endswith(".rs") for f in files) or "Cargo.toml" in files:
-            types.add("rust")
-        if any(f.endswith(".go") for f in files) or "go.mod" in files:
-            types.add("go")
-        if any(f in IAC_FILENAMES for f in files) or any(f.endswith(".tf") for f in files):
-            types.add("iac")
-        if any(f in MCP_CONFIG_FILENAMES for f in files):
-            types.add("mcp")
-    # .vscode is in SKIP_DIRS (pruned above) but is the canonical mcp.json home —
-    # probe the project root explicitly so detection still triggers.
-    if (Path(root_dir) / ".vscode" / "mcp.json").exists():
-        types.add("mcp")
-    return list(types)
diff --git a/.agent/skills/security-audit/scripts/audit/scanners_next.py b/.agent/skills/security-audit/scripts/audit/scanners_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/scanners_next.py
+++ /dev/null
@@ -1,665 +0,0 @@
-"""Core scanning functions for the security audit scanner."""
-
-import json
-import os
-import re
-import subprocess
-import sys
-from pathlib import Path
-from typing import Any, Dict
-
-from . import config as _config
-from .config import (
-    CODE_EXTENSIONS,
-    CONFIG_EXTENSIONS,
-    IAC_EXTENSIONS,
-    IAC_FILENAMES,
-    MCP_CONFIG_FILENAMES,
-    MCP_SCAN_PRUNE,
-    SEVERITY_ORDER,
-    SKIP_DIRS,
-)
-from .helpers import (
-    LockfileCopyError,
-    find_npm_lockfiles,
-    is_self_path,
-    npm_audit_dir,
-    open_regular_text,
-    printable,
-    shannon_entropy,
-    sort_findings_by_severity,
-)
-from .patterns import (
-    CONFIG_PATTERNS,
-    DANGEROUS_PATTERNS,
-    IAC_PATTERNS,
-    MCP_AGENTIC_PATTERNS,
-    SECRET_PATTERNS,
-)
-
-
-#: Seconds one `npm audit` may run before its lockfile is reported as not audited (TASK 111 R5.2).
-NPM_AUDIT_TIMEOUT = 60
-
-#: npm's advisory severity → the scanner's severity (TASK 118 R3.1).
-NPM_SEVERITY = {"critical": "critical", "high": "high", "moderate": "medium", "low": "low",
-                "info": "info"}
-
-
-def _npm_audit(lockfile: Path, project_path: str):
-    """`(rel, findings, counts)` of `npm audit` for one lockfile (TASK 111 R5.2, R5.3, R5.6).
-
-    `--package-lock-only` reads the lockfile without `node_modules`, in a temporary copy of the
-    lockfile and its `package.json`. An audit that does not finish yields an `info` finding naming
-    the lockfile and the reason, never a silent pass; its `counts` is `None` (TASK 118 R3.3).
-    """
-    rel = os.path.relpath(lockfile, project_path).replace(os.sep, "/")
-    try:
-        with npm_audit_dir(lockfile) as workdir:
-            if workdir is None:
-                return rel, [_not_audited(rel, "no package.json beside it")], None
-            try:
-                result = subprocess.run(
-                    ["npm", "audit", "--json", "--package-lock-only"],
-                    cwd=workdir, capture_output=True, text=True, timeout=NPM_AUDIT_TIMEOUT,
-                )
-            except FileNotFoundError:
-                return rel, [_not_audited(rel, "npm is not installed")], None
-            except subprocess.TimeoutExpired:
-                return rel, [_not_audited(rel, f"npm audit ran past {NPM_AUDIT_TIMEOUT} s")], None
-    except LockfileCopyError:
-        return rel, [_not_audited(rel, "the lockfile could not be copied")], None
-    try:
-        audit_data = json.loads(result.stdout)
-    except json.JSONDecodeError:
-        return rel, [_not_audited(rel, "npm audit printed no JSON")], None
-    if not isinstance(audit_data, dict):
-        return rel, [_not_audited(rel, "npm audit printed no JSON object")], None
-    if "error" in audit_data:
-        error = audit_data["error"]
-        detail = (error.get("code") if isinstance(error, dict) else None) or audit_data.get("message")
-        reason = f"npm audit reported an error ({str(detail or 'no detail')[:120]})"
-        return rel, [_not_audited(rel, reason)], None
-    vulnerabilities = audit_data.get("vulnerabilities")
-    if vulnerabilities is not None and not isinstance(vulnerabilities, dict):
-        return rel, [_not_audited(rel, "npm audit printed no vulnerability map")], None
-    return rel, _npm_audit_findings(audit_data, rel), _npm_audit_counts(audit_data)
-
-
-def _not_audited(rel: str, reason: str) -> dict:
-    """The `info` finding of a lockfile that was not audited; `audited` marks it (TASK 118 R3.4)."""
-    return {
-        "type": "npm audit",
-        "severity": "info",
-        "cwe": "CWE-1104",
-        "message": f"{rel}: not audited, {reason}",
-        "audited": False,
-    }
-
-
-def _npm_audit_counts(audit_data: dict) -> dict:
-    """The counts of a finished `npm audit` per npm severity, and `unknown` (TASK 118 R3.2, R3.3).
-
-    An entry that is not a map, or holds no severity, counts as `low`, as before TASK 118; a
-    severity outside npm's five counts as `unknown`.
-    """
-    counts = dict.fromkeys((*NPM_SEVERITY, "unknown"), 0)
-    for vuln in (audit_data.get("vulnerabilities") or {}).values():
-        sev = str(vuln.get("severity") or "low").lower() if isinstance(vuln, dict) else "low"
-        counts[sev if sev in NPM_SEVERITY else "unknown"] += 1
-    return counts
-
-
-def _npm_audit_findings(audit_data: dict, rel: str) -> list:
-    """One finding per npm severity of a finished `npm audit`, at every severity (TASK 118 R3.1)."""
-    counts = _npm_audit_counts(audit_data)
-    findings = [{
-        "type": "npm audit",
-        "severity": NPM_SEVERITY[sev],
-        "cwe": "CWE-1104",
-        "message": f"{rel}: {count} {sev} vulnerabilities in dependencies",
-    } for sev, count in counts.items() if sev in NPM_SEVERITY and count]
-    if counts["unknown"]:
-        findings.append({
-            "type": "npm audit",
-            "severity": "low",
-            "cwe": "CWE-1104",
-            "message": f"{rel}: {counts['unknown']} vulnerabilities of unknown severity",
-        })
-    return findings
-
-
-def scan_dependencies(project_path: str) -> Dict[str, Any]:
-    """Validate supply chain security (OWASP A03:2025 Software Supply Chain Failures, CWE-1104)."""
-    results = {"tool": "dependency_scanner", "findings": [], "status": "[OK] Secure",
-               "npm_audit_counts": {}}
-
-    # Ecosystem -> (type markers, accepted lock files).
-    # `requirements.txt` lists deps but does NOT pin a full transitive graph
-    # with hashes, so it is NOT counted as a lock file by default. Exception:
-    # pip-compile output with `--hash=sha256:` lines IS effectively a lock.
-    ecosystems = {
-        "javascript": {
-            "markers": ["package.json"],
-            "locks": ["package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml"],
-        },
-        "python": {
-            "markers": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
-            "locks": ["Pipfile.lock", "poetry.lock", "uv.lock", "pdm.lock"],
-        },
-        "rust": {
-            "markers": ["Cargo.toml"],
-            "locks": ["Cargo.lock"],
-        },
-        "go": {
-            "markers": ["go.mod"],
-            "locks": ["go.sum"],
-        },
-    }
-
-    def _python_has_hash_pinned_requirements(base: Path) -> bool:
-        """pip-compile output: requirements.txt with `--hash=sha256:` is a de-facto lock."""
-        req = base / "requirements.txt"
-        if not req.exists():
-            return False
-        try:
-            with open_regular_text(req, base) as f:
-                # Stop scanning after 1MB; hash lines appear early in real pip-compile output.
-                sample = f.read(1024 * 1024)
-            return '--hash=sha256:' in sample
-        except OSError:
-            return False
-
-    for eco, spec in ecosystems.items():
-        base = Path(project_path)
-        is_type = any((base / m).exists() for m in spec["markers"])
-        if not is_type:
-            continue
-        has_lock = any((base / f).exists() for f in spec["locks"])
-        if not has_lock and eco == "python" and _python_has_hash_pinned_requirements(base):
-            has_lock = True  # pip-compile hash-pinned requirements.txt counts as lock
-        if not has_lock:
-            results["findings"].append({
-                "type": "Missing Lock File",
-                "severity": "high",
-                "cwe": "CWE-1104",
-                "message": f"{eco}: No lock file found (expected one of: {', '.join(spec['locks'])}). Supply chain integrity at risk."
-            })
-
-    # npm audit, once per lockfile directory (TASK 111 R5). The audit used to run at the root only,
-    # and a failed run produced no finding, so an offline scan read as a clean one.
-    not_audited = 0
-    for lockfile in find_npm_lockfiles(project_path):
-        rel, found, counts = _npm_audit(lockfile, project_path)
-        not_audited += sum(1 for f in found if f.get("audited") is False)
-        results["findings"].extend(found)
-        if counts is not None:
-            results["npm_audit_counts"][rel] = counts
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    # The first match sets the status (TASK 118 R3.5): a critical or high finding outranks an
-    # unaudited lockfile (TASK 111 R5.7), which outranks a finding below high.
-    max_sev = min((SEVERITY_ORDER.get(f.get("severity", "low"), 99) for f in results["findings"]),
-                  default=99)
-    if max_sev == 0:
-        results["status"] = "[!!] Critical vulnerabilities"
-    elif max_sev == 1:
-        results["status"] = "[!] HIGH: Dependency issues"
-    elif not_audited:
-        results["status"] = f"[?] Not audited: {not_audited} npm lockfile(s)"
-    elif any(f.get("severity") in ("medium", "low") for f in results["findings"]):
-        results["status"] = "[?] Dependency issues below high"
-
-    return results
-
-
-def scan_secrets(project_path: str) -> Dict[str, Any]:
-    """Validate no hardcoded secrets (OWASP A04:2025 Cryptographic Failures, CWE-798)."""
-    results = {
-        "tool": "secret_scanner",
-        "findings": [],
-        "status": "[OK] No secrets detected",
-        "scanned_files": 0,
-        "skipped_files": 0,
-        "by_severity": {"critical": 0, "high": 0}
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CODE_EXTENSIONS and ext not in CONFIG_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open_regular_text(filepath, project_path) as f:
-                    content = f.read()
-                    # ReDoS guard: filter out pathologically long lines before regex.
-                    # All SECRET_PATTERNS are line-local (no multi-line matches in the
-                    # current pattern set, including BEGIN...KEY which is one-line marker).
-                    all_lines = content.splitlines()
-                    safe_lines = [
-                        ln for ln in all_lines
-                        if len(ln) <= _config.MAX_LINE_LENGTH
-                    ]
-                    safe_content = "\n".join(safe_lines)
-                    # Count only genuinely over-long lines. (A prior `count("\n") + 1`
-                    # over-counted by 1 on newline-terminated files — splitlines() yields
-                    # no trailing empty element — emitting a phantom "skipped 1 line" WARN.)
-                    skipped_lines = len(all_lines) - len(safe_lines)
-                    if skipped_lines > 0:
-                        print(f"[WARN] {printable(filepath)}: skipped {skipped_lines} line(s) > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                    for pattern, secret_type, severity, cwe in SECRET_PATTERNS:
-                        matches = re.findall(pattern, safe_content, re.IGNORECASE)
-                        if matches:
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "type": secret_type,
-                                "severity": severity,
-                                "cwe": cwe,
-                                "count": len(matches)
-                            })
-                            if severity in results["by_severity"]:
-                                results["by_severity"][severity] += len(matches)
-
-                    # High-entropy string detection for suspicious variable names
-                    entropy_pattern = r'(?:secret|private[_-]?key|auth[_-]?token|api[_-]?key|password|credential)\s*[=:]\s*["\']([^"\']{16,})["\']'
-                    for match in re.finditer(entropy_pattern, safe_content, re.IGNORECASE):
-                        value = match.group(1)
-                        entropy = shannon_entropy(value)
-                        if entropy > 4.5:
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "type": "High-Entropy Secret",
-                                "severity": "high",
-                                "cwe": "CWE-798",
-                                "count": 1,
-                                "entropy": round(entropy, 2)
-                            })
-                            results["by_severity"]["high"] += 1
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    if results["by_severity"]["critical"] > 0:
-        results["status"] = "[!!] CRITICAL: Secrets exposed!"
-    elif results["by_severity"]["high"] > 0:
-        results["status"] = "[!] HIGH: Secrets found"
-
-    return results
-
-
-def scan_code_patterns(project_path: str) -> Dict[str, Any]:
-    """Validate dangerous code patterns (OWASP A05:2025 Injection, CWE-79/89/78)."""
-    results = {
-        "tool": "pattern_scanner",
-        "findings": [],
-        "status": "[OK] No dangerous patterns",
-        "scanned_files": 0,
-        "skipped_files": 0
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CODE_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open_regular_text(filepath, project_path) as f:
-                    lines = f.readlines()
-                    for line_num, line in enumerate(lines, 1):
-                        # ReDoS guard: skip pathologically long lines (minified bundles, token blobs).
-                        if len(line) > _config.MAX_LINE_LENGTH:
-                            continue
-                        for pattern, name, severity, category, cwe in DANGEROUS_PATTERNS:
-                            if re.search(pattern, line, re.IGNORECASE):
-                                results["findings"].append({
-                                    "file": str(filepath.relative_to(project_path)),
-                                    "line": line_num,
-                                    "pattern": name,
-                                    "severity": severity,
-                                    "category": category,
-                                    "cwe": cwe,
-                                    "snippet": line.strip()[:100]
-                                })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if critical > 0:
-        results["status"] = f"[!!] CRITICAL: {critical} dangerous patterns"
-    elif high > 0:
-        results["status"] = f"[!] HIGH: {high} dangerous patterns"
-    elif results["findings"]:
-        results["status"] = "[?] Patterns found"
-
-    return results
-
-
-def scan_configuration(project_path: str) -> Dict[str, Any]:
-    """Validate security configuration (OWASP A02:2025 Security Misconfiguration, CWE-16)."""
-    results = {"tool": "config_scanner", "findings": [], "status": "[OK] Config secure", "skipped_files": 0}
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CONFIG_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            try:
-                with open_regular_text(filepath, project_path) as f:
-                    content = f.read()
-                    for pattern, issue, severity, cwe in CONFIG_PATTERNS:
-                        if re.search(pattern, content, re.IGNORECASE):
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "issue": issue,
-                                "severity": severity,
-                                "cwe": cwe,
-                            })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    if any(f["severity"] == "critical" for f in results["findings"]):
-        results["status"] = "[!!] CRITICAL: Config issues"
-    elif any(f["severity"] == "high" for f in results["findings"]):
-        results["status"] = "[!] HIGH: Config issues"
-
-    return results
-
-
-def scan_iac(project_path: str) -> Dict[str, Any]:
-    """Validate Infrastructure as Code security (Docker, K8s, Terraform)."""
-    results = {
-        "tool": "iac_scanner",
-        "findings": [],
-        "status": "[OK] IaC secure",
-        "scanned_files": 0,
-        "skipped_files": 0,
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            filepath = Path(root) / file
-            ext = Path(file).suffix.lower()
-            is_iac_file = (ext in IAC_EXTENSIONS) or (file in IAC_FILENAMES) or file.startswith("Dockerfile")
-
-            if not is_iac_file:
-                continue
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open_regular_text(filepath, project_path) as f:
-                    content = f.read()
-
-                    # ReDoS guard: IaC patterns may span lines (re.MULTILINE). Instead of
-                    # filtering lines (breaks multi-line patterns), skip the entire file
-                    # if any line is pathologically long. Legit YAML/Dockerfile/Terraform
-                    # never has >4k-char lines; only minified blobs do.
-                    if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
-                        results["skipped_files"] += 1
-                        print(f"[WARN] Skipped IaC {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                        continue
-
-                    # Heuristic: for generic YAML/JSON files, only apply patterns
-                    # matching the detected IaC type (prevents false positives on docs)
-                    is_docker = file.startswith("Dockerfile") or file == "Containerfile"
-                    is_k8s = re.search(r'apiVersion\s*:', content) is not None
-                    is_terraform = ext in {'.tf', '.tfvars'}
-                    is_cloudformation = re.search(r'AWSTemplateFormatVersion|Resources\s*:', content) is not None
-                    is_compose = file in {'docker-compose.yml', 'docker-compose.yaml'}
-
-                    for pattern, name, severity, category, cwe in IAC_PATTERNS:
-                        # Skip category-specific patterns for non-matching file types
-                        if category == "Docker" and not (is_docker or is_compose):
-                            continue
-                        if category == "Kubernetes" and not is_k8s:
-                            continue
-                        if category == "Terraform" and not is_terraform:
-                            continue
-                        if category == "CloudFormation" and not is_cloudformation:
-                            continue
-
-                        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
-                            line_num = content[:match.start()].count('\n') + 1
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "line": line_num,
-                                "pattern": name,
-                                "severity": severity,
-                                "category": category,
-                                "cwe": cwe,
-                            })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if critical > 0:
-        results["status"] = f"[!!] CRITICAL: {critical} IaC issues"
-    elif high > 0:
-        results["status"] = f"[!] HIGH: {high} IaC issues"
-    elif results["findings"]:
-        results["status"] = "[?] IaC patterns found"
-
-    return results
-
-
-def scan_sbom(project_path: str) -> Dict[str, Any]:
-    """Check for SBOM presence recursively via os.walk with early SKIP_DIRS prune.
-
-    Uses os.walk (not Path.rglob) because rglob traverses SKIP_DIRS first and only
-    filters after yielding — on a monorepo with node_modules, that is O(millions).
-    os.walk with `dirs[:] = ...` pruning skips those subtrees entirely.
-    """
-    results = {
-        "tool": "sbom_scanner",
-        "findings": [],
-        "status": "[OK] SBOM check passed",
-    }
-
-    # Compiled fnmatch-style checks; case-insensitive so "SBOM.json" is caught.
-    sbom_patterns_re = [
-        re.compile(r'.*sbom.*', re.IGNORECASE),
-        re.compile(r'^bom\.(?:json|xml)$', re.IGNORECASE),
-        re.compile(r'.*\.spdx.*', re.IGNORECASE),
-        re.compile(r'.*\.cdx\..*', re.IGNORECASE),
-        re.compile(r'^cyclonedx-bom\..*$', re.IGNORECASE),
-    ]
-
-    sbom_files = []
-    for current_dir, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-        for f in files:
-            if any(rx.match(f) for rx in sbom_patterns_re):
-                sbom_files.append(Path(current_dir) / f)
-
-    if not sbom_files:
-        results["findings"].append({
-            "type": "Missing SBOM",
-            "severity": "medium",
-            "cwe": "CWE-1104",
-            "message": "No SBOM (Software Bill of Materials) found. Required by EU CRA & EO 14028. "
-                       "Generate with: npx @cyclonedx/cdxgen -o sbom.json (or syft . -o cyclonedx-json > sbom.json)"
-        })
-        results["status"] = "[?] SBOM missing"
-    else:
-        results["status"] = f"[OK] SBOM found: {', '.join(f.name for f in sbom_files[:3])}"
-
-    return results
-
-
-def scan_mcp_agentic(project_path: str) -> Dict[str, Any]:
-    """Scan MCP/agentic surfaces (OWASP ASI Top 10 2026, NSA MCP CSI).
-
-    Targets: well-known MCP config artifacts (MCP_CONFIG_FILENAMES) with full
-    pattern set + provenance finding; other config files (auto-approve keys,
-    bypass flags, unpinned runners); code files (tool-description poisoning
-    heuristics). Walks with MCP_SCAN_PRUNE (descends into .vscode, unlike
-    other scanners). Markdown is deliberately NOT scanned — semantic prose
-    poisoning is the LLM-review class (see references/checklists/
-    mcp_agentic_security.md "Scanner floor").
-    """
-    results = {
-        "tool": "mcp_agentic_scanner",
-        "findings": [],
-        "status": "[OK] No MCP/agentic risks detected",
-        "scanned_files": 0,
-        "skipped_files": 0,
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        # Custom prune: unlike other scanners, descend into .vscode (canonical
-        # home of mcp.json / chat.tools.autoApprove). Filename-targeted, so cheap.
-        dirs[:] = [d for d in dirs if d not in MCP_SCAN_PRUNE]
-
-        for file in files:
-            filepath = Path(root) / file
-            ext = Path(file).suffix.lower()
-            is_mcp_config = file in MCP_CONFIG_FILENAMES
-
-            if is_mcp_config:
-                applicable = MCP_AGENTIC_PATTERNS
-            elif ext in CONFIG_EXTENSIONS:
-                applicable = [p for p in MCP_AGENTIC_PATTERNS if p[5] == "any-config"]
-            elif ext in CODE_EXTENSIONS:
-                applicable = [p for p in MCP_AGENTIC_PATTERNS if p[5] == "code"]
-            else:
-                continue  # .md and everything else: LLM-review class, not regex floor
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open_regular_text(filepath, project_path) as f:
-                    content = f.read()
-
-                rel = str(filepath.relative_to(project_path))
-
-                if is_mcp_config:
-                    results["findings"].append({
-                        "file": rel,
-                        "type": "MCP Config Present",
-                        "severity": "low",
-                        "category": "Agentic Supply Chain (ASI04)",
-                        "cwe": "CWE-829",
-                        "message": "MCP config detected — verify provenance, version pinning, and "
-                                   "registry trust of each server (see checklists/mcp_agentic_security.md).",
-                    })
-
-                # ReDoS guard: whole-file matching uses newline-crossing character
-                # classes, so (IaC-style) skip the entire file on pathological lines.
-                if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped MCP scan of {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                    continue
-
-                lines = content.splitlines()
-                for pattern, name, severity, category, cwe, _scope in applicable:
-                    for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
-                        line_num = content[:match.start()].count('\n') + 1
-                        snippet = lines[line_num - 1].strip()[:100] if line_num <= len(lines) else ""
-                        results["findings"].append({
-                            "file": rel,
-                            "line": line_num,
-                            "pattern": name,
-                            "severity": severity,
-                            "category": category,
-                            "cwe": cwe,
-                            "snippet": snippet,
-                        })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if high > 0:
-        results["status"] = f"[!] HIGH: {high} MCP/agentic risks"
-    elif results["findings"]:
-        results["status"] = "[?] MCP/agentic surface present (review)"
-
-    return results
diff --git a/tests/staged_lockfile_audit.py b/tests/staged_lockfile_audit.py
deleted file mode 100644
--- a/tests/staged_lockfile_audit.py
+++ /dev/null
@@ -1,1066 +0,0 @@
-"""The dependency audit covers every npm lockfile (TASK 111 R5).
-
-Before TASK 111 the `security-audit` scanner ran `npm audit` at the project root only, and a failed
-run produced no finding. This repository holds three npm lockfiles under
-`.agent/skills/mermaid-authoring-guidelines/assets/renderers/` and none at the root. A fake `npm` on
-`PATH` records the directory it runs in, that directory's entries and its arguments, and prints a
-set reply. This file pins:
-
-* a lockfile below the root is audited, in a temporary copy of it and its `package.json`, so a
-  `.npmrc` beside the lockfile takes no part (``TC-L1``, ``TC-L13``);
-* each finding names its lockfile (``TC-L2``, ``TC-L12``);
-* `node_modules/` and symbolic links are skipped (``TC-L3``, ``TC-L11``), and a project without a
-  lockfile runs no audit (``TC-L4``);
-* an audit that does not finish yields an `info` finding and the section says so (``TC-L5``,
-  ``TC-L14``, ``TC-L15``);
-* one directory is audited once (``TC-L6``);
-* `run_external_tools` audits each lockfile, and only those (``TC-L7`` to ``TC-L9c``); it runs
-  `yarn audit` in a copy of `yarn.lock` and `package.json`, never through a link, and for a
-  javascript project only (``TC-Y1`` to ``TC-Y3``, TASK 112 R5.1);
-* a root `package.json` without a lockfile is reported, not audited (``TC-L10``);
-* the copy holds the original `package.json`, never a linked one (``TC-L16``, ``TC-L17``);
-* a finding outranks an unaudited lockfile in the status; an unexpected vulnerability field and a
-  timeout yield a named `info` finding (``TC-L18`` to ``TC-L20``).
-
-TASK 118 (WI-42) adds the status of each external tool and the findings of every npm severity. Its
-fake tools are `/bin/sh` scripts in a `bin` directory that is the whole `PATH`, so a tool installed
-on the runner does not start. This file pins:
-
-* `run_audit.py` reports each external tool and exits 3 when a part did not run (``TC-E1``,
-  ``TC-E11``, ``TC-E13``, ``TC-E15``); a tool's record says `ran`, `not_installed` or `timed_out`
-  (``TC-E2``, ``TC-E4``), and a fallback fills its slot (``TC-E5``);
-* a tool's non-zero exit fails `--fail-on` (``TC-E3``, ``TC-E10``), and the options that make a
-  finding exit non-zero are passed (``TC-E9``);
-* the secret scan reads the working tree with `--no-git`, and the history slot follows the `.git`
-  at or above the scanned root, never through a link (``TC-E6``, ``TC-E7``);
-* stdout holds one JSON document (``TC-E8``); the summary output lists each tool (``TC-E14``); the
-  external status and the overall status (``TC-E12``, ``TC-E16``); the summary counts every
-  finding before the cut (``TC-E17``);
-* npm advisories of every severity are findings, with a count map per lockfile, and an unaudited
-  lockfile carries `audited: false` (``TC-D1`` to ``TC-D7``; ``TC-D1`` replaces ``TC-L23``); a
-  lockfile that cannot be copied is not audited, and the scanner still prints its report
-  (``TC-D8``);
-* a tool killed by a signal leaves its slot a part not run (``TC-E18``), and text from the scanned
-  tree reaches printed output with its control characters escaped (``TC-E19``, ``TC-E19b``).
-
-TASK 119 (WI-51) adds:
-
-* an in-process scan skips a file that is not regular, such as a FIFO, and counts it in
-  `skipped_files`; the run never blocks on it (``TC-F1``, ``TC-F2``); a link to a regular file in
-  the scanned root is still read (``TC-F3``), and one whose real path leaves the root is skipped
-  (``TC-F9``);
-* `AuditTestCase` runs the fake `npm` with `PATH` the fake `bin`, `/usr/bin` and `/bin` only
-  (``TC-F4``);
-* `printable` escapes the backslash (``TC-F5``);
-* `open_regular_text` opens with `O_BINARY` and `O_NOCTTY` where the platform has them, closes the
-  descriptor of a refused file, and checks the size limit on the opened descriptor (``TC-F6`` to
-  ``TC-F8``).
-
-`RUN_AUDIT_PATH` and `RUN_AUDIT_CMD` name the `run_audit.py` that the tests load and start; a test
-reads them at call time. The in-process cases stop the `.git` walk at their temporary directory;
-the subprocess cases cannot. TC-E1 accepts either status of the history slot, and TC-E3 assumes
-no `.git` link or special file above the system temporary directory.
-"""
-import importlib
-import importlib.util
-import json
-import os
-import shutil
-import subprocess
-import sys
-import tempfile
-import unittest
-from pathlib import Path
-from unittest import mock
-
-PROJECT_ROOT = Path(__file__).resolve().parent.parent
-PACKAGE = PROJECT_ROOT / ".agent" / "skills" / "security-audit" / "scripts" / "audit"
-NAME = "security_audit_scanner_under_test"
-RUN_AUDIT_PATH = PACKAGE.parent / "run_audit.py"
-RUN_AUDIT_CMD = (sys.executable, str(RUN_AUDIT_PATH))
-
-
-def _load():
-    """The scanner package under a name no other test module uses."""
-    if NAME not in sys.modules:
-        spec = importlib.util.spec_from_file_location(
-            NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
-        module = importlib.util.module_from_spec(spec)
-        sys.modules[NAME] = module
-        spec.loader.exec_module(module)
-    return (importlib.import_module(f"{NAME}.scanners"),
-            importlib.import_module(f"{NAME}.external"),
-            importlib.import_module(f"{NAME}.helpers"))
-
-
-scanners, external, helpers = _load()
-
-
-def _run_audit_module():
-    """`RUN_AUDIT_PATH`, loaded while `audit` names the package under test."""
-    saved = sys.modules.get("audit")
-    sys.modules["audit"] = sys.modules[NAME]
-    try:
-        spec = importlib.util.spec_from_file_location("security_audit_run_audit_under_test",
-                                                      RUN_AUDIT_PATH)
-        module = importlib.util.module_from_spec(spec)
-        spec.loader.exec_module(module)
-    finally:
-        if saved is None:
-            del sys.modules["audit"]
-        else:
-            sys.modules["audit"] = saved
-    return module
-
-FAKE_NPM = """#!/bin/sh
-printf '%s\\t%s\\t%s\\t%s\\n' "$PWD" "$(ls -A | tr '\\n' ' ')" "$*" "$(cat package.json)" >> "$FAKE_NPM_LOG"
-if grep -q broken package.json; then echo "not json"; else cat "$FAKE_NPM_REPLY"; fi
-"""
-HIGH = {"vulnerabilities": {"x": {"severity": "high"}}}
-COPY = "package-lock.json package.json"
-GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
-GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
-ZERO_COUNTS = dict.fromkeys(("critical", "high", "moderate", "low", "info", "unknown"), 0)
-
-
-def _ran(cmd, slot, where="."):
-    """The tool record of a tool that ran and exited 0."""
-    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": "ran",
-            "exit_code": 0, "reason": None}
-
-
-class AuditTestCase(unittest.TestCase):
-
-    def setUp(self):
-        self.tmp = Path(tempfile.mkdtemp())
-        self.addCleanup(shutil.rmtree, self.tmp)
-        self.project = self.tmp / "project"
-        self.project.mkdir()
-        self.bin = self.tmp / "bin"
-        self.bin.mkdir()
-        npm = self.bin / "npm"
-        npm.write_text(FAKE_NPM)
-        npm.chmod(0o755)
-        self.log = self.tmp / "npm.log"
-        self.reply = self.tmp / "reply.json"
-        self.set_reply({"vulnerabilities": {}})
-        # The fake `npm` calls `ls`, `tr`, `cat` and `grep`; a tool installed elsewhere, such as
-        # under `/opt/homebrew/bin`, must not start in a case (TASK 119 R2).
-        env = {"PATH": os.pathsep.join((str(self.bin), "/usr/bin", "/bin")),
-               "FAKE_NPM_LOG": str(self.log), "FAKE_NPM_REPLY": str(self.reply)}
-        patcher = mock.patch.dict(os.environ, env)
-        patcher.start()
-        self.addCleanup(patcher.stop)
-
-    def set_reply(self, reply):
-        self.reply.write_text(reply if isinstance(reply, str) else json.dumps(reply))
-
-    def lockfile(self, rel, name="package-lock.json", package=True, content='{"name": "x"}'):
-        d = self.project / rel
-        d.mkdir(parents=True, exist_ok=True)
-        (d / name).write_text("{}")
-        if package:
-            (d / "package.json").write_text(content)
-        return d
-
-    def calls(self):
-        """`(directory, entries, arguments)` of each fake `npm` run."""
-        return [call[:3] for call in self.full_calls()]
-
-    def full_calls(self):
-        """`(directory, entries, arguments, package.json)` of each fake `npm` run."""
-        if not self.log.exists():
-            return []
-        return [tuple(part.strip() for part in line.split("\t"))
-                for line in self.log.read_text().splitlines()]
-
-    def scan(self):
-        return scanners.scan_dependencies(str(self.project))
-
-    def infos(self, findings):
-        return [f for f in findings if f.get("severity") == "info"]
-
-
-class TestScanDependencies(AuditTestCase):
-    """TC-L1 to TC-L6 and TC-L10 to TC-L15 drive `scan_dependencies`."""
-
-    def test_l1_lockfile_below_the_root_is_audited_in_a_copy(self):
-        # base-fail: the base runs npm audit only at a root package.json.
-        self.lockfile("sub")
-        self.scan()
-        [(where, entries, args)] = self.calls()
-        self.assertEqual(args, "audit --json --package-lock-only")
-        self.assertEqual(entries, COPY)
-        self.assertFalse(Path(where).resolve().is_relative_to(self.project.resolve()))
-
-    def test_l2_finding_names_its_lockfile(self):
-        self.lockfile("sub")
-        self.set_reply(HIGH)
-        findings = self.scan()["findings"]
-        high = [f for f in findings if f.get("severity") == "high" and f.get("type") == "npm audit"]
-        self.assertEqual(len(high), 1, findings)
-        self.assertTrue(high[0]["message"].startswith("sub/package-lock.json: 1 high"), high[0])
-
-    def test_l3_node_modules_is_skipped(self):
-        self.lockfile("node_modules/dep")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l4_no_lockfile_runs_no_audit(self):
-        (self.project / "package.json").write_text("{}")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l5_unfinished_audit_yields_an_info_finding(self):
-        self.lockfile("sub")
-        for label, reply in (("not json", "not json"), ("not an object", []),
-                             ("error object", {"error": {"code": "ENOAUDIT"}}),
-                             ("error message", {"message": "ECONNREFUSED", "error": {}})):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                info = self.infos(self.scan()["findings"])
-                self.assertEqual(len(info), 1, info)
-                self.assertTrue(info[0]["message"].startswith("sub/package-lock.json: not audited"))
-        with self.subTest(case="timeout"), mock.patch.object(
-                scanners.subprocess, "run",
-                side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
-            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)
-        with self.subTest(case="npm absent"), \
-                mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)
-
-    def test_l5_error_message_reaches_the_reason(self):
-        self.lockfile("sub")
-        self.set_reply({"message": "request to registry failed, ECONNREFUSED", "error": {}})
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("ECONNREFUSED", info["message"])
-
-    def test_l6_one_directory_is_audited_once(self):
-        self.lockfile("sub")
-        (self.project / "sub" / "npm-shrinkwrap.json").write_text("{}")
-        self.set_reply(HIGH)
-        findings = self.scan()["findings"]
-        [(_where, entries, _args)] = self.calls()
-        self.assertEqual(entries, "npm-shrinkwrap.json package.json")
-        self.assertTrue(any(f.get("message", "").startswith("sub/npm-shrinkwrap.json:")
-                            for f in findings))
-
-    def test_l10_root_package_json_without_lockfile_is_reported_not_audited(self):
-        (self.project / "package.json").write_text("{}")
-        findings = self.scan()["findings"]
-        self.assertTrue(any(f.get("type") == "Missing Lock File" and "javascript" in f["message"]
-                            for f in findings), findings)
-        self.assertEqual(self.calls(), [])
-
-    def test_l11_symbolic_links_are_not_followed(self):
-        real = self.lockfile("../outside")
-        (self.project / "linked").symlink_to(real, target_is_directory=True)
-        d = self.project / "plain"
-        d.mkdir()
-        (d / "package.json").write_text("{}")
-        (d / "package-lock.json").symlink_to(real / "package-lock.json")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l12_critical_finding_names_its_lockfile(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "critical"}, "b": {"severity": "high"}}})
-        result = self.scan()
-        messages = sorted(f["message"] for f in result["findings"] if f.get("type") == "npm audit")
-        self.assertEqual(messages, ["sub/package-lock.json: 1 critical vulnerabilities in dependencies",
-                                    "sub/package-lock.json: 1 high vulnerabilities in dependencies"])
-        self.assertIn("Critical", result["status"])
-
-    def test_l13_npmrc_beside_the_lockfile_is_not_copied(self):
-        d = self.lockfile("sub")
-        (d / ".npmrc").write_text("registry=http://attacker.invalid/\n")
-        self.scan()
-        [(_where, entries, _args)] = self.calls()
-        self.assertEqual(entries, COPY)
-
-    def test_l14_lockfile_without_package_json_is_not_audited(self):
-        self.lockfile("sub", package=False)
-        [info] = self.infos(self.scan()["findings"])
-        self.assertEqual(info["message"], "sub/package-lock.json: not audited, no package.json beside it")
-        self.assertEqual(self.calls(), [])
-
-    def test_l15_section_status_names_unaudited_lockfiles(self):
-        self.lockfile("sub")
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")
-
-    def test_l16_copy_holds_the_original_package_json(self):
-        self.lockfile("sub", content='{"name": "pinned-content"}')
-        self.scan()
-        [call] = self.full_calls()
-        self.assertEqual(call[3], '{"name": "pinned-content"}')
-
-    def test_l17_linked_package_json_is_not_used(self):
-        d = self.lockfile("sub", package=False)
-        real = self.tmp / "elsewhere.json"
-        real.write_text("{}")
-        (d / "package.json").symlink_to(real)
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("no package.json beside it", info["message"])
-        self.assertEqual(self.calls(), [])
-
-    def test_l18_a_finding_outranks_an_unaudited_lockfile_in_the_status(self):
-        self.lockfile("a")
-        self.lockfile("b", content='{"name": "broken"}')
-        self.set_reply({"vulnerabilities": {"x": {"severity": "critical"}}})
-        result = self.scan()
-        self.assertEqual(len(self.infos(result["findings"])), 1)
-        self.assertIn("Critical", result["status"])
-
-    def test_l19_vulnerability_field_shapes(self):
-        self.lockfile("sub")
-        for label, reply, infos in (("null", {"vulnerabilities": None}, 0),
-                                    ("list", {"vulnerabilities": []}, 1),
-                                    ("entry not a map", {"vulnerabilities": {"x": "high"}}, 0)):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                findings = self.scan()["findings"]
-                self.assertEqual(len(self.infos(findings)), infos, findings)
-                self.assertFalse([f for f in findings if f.get("severity") in ("high", "critical")])
-
-    def test_l20_timeout_reason_names_the_limit(self):
-        self.lockfile("sub")
-        with mock.patch.object(scanners.subprocess, "run",
-                               side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
-            [info] = self.infos(self.scan()["findings"])
-        self.assertEqual(info["message"], "sub/package-lock.json: not audited, npm audit ran past 60 s")
-
-    def test_l21_error_code_reaches_the_reason(self):
-        self.lockfile("sub")
-        self.set_reply({"error": {"code": "ENOAUDIT"}})
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("ENOAUDIT", info["message"])
-
-    def test_l22_status_counts_every_unaudited_lockfile(self):
-        self.lockfile("a")
-        self.lockfile("b")
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 2 npm lockfile(s)")
-
-    def test_d1_every_npm_severity_is_a_finding(self):
-        """TC-D1 (TASK 118 R3.1), in place of TC-L23: the base kept critical and high only."""
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "moderate"}, "b": {"severity": "low"},
-                                            "c": {"severity": "info"}}})
-        findings = [f for f in self.scan()["findings"] if f.get("type") == "npm audit"]
-        self.assertEqual([(f["severity"], f["message"]) for f in findings], [
-            ("medium", "sub/package-lock.json: 1 moderate vulnerabilities in dependencies"),
-            ("low", "sub/package-lock.json: 1 low vulnerabilities in dependencies"),
-            ("info", "sub/package-lock.json: 1 info vulnerabilities in dependencies")])
-
-    def test_l15_each_audit_has_a_60_second_timeout(self):
-        self.lockfile("sub")
-        with mock.patch.object(scanners.subprocess, "run", wraps=subprocess.run) as run:
-            self.scan()
-        self.assertEqual(run.call_args.kwargs.get("timeout"), 60)
-
-
-class TestExternalTools(AuditTestCase):
-    """TC-L7 to TC-L9c and TC-Y1 to TC-Y3 drive `run_external_tools` (R5.4, R5.5; TASK 112 R5.1)."""
-
-    def external(self, types):
-        recorded = []
-
-        def record(cmd, cwd=None, slot=None, where=".", **_kw):
-            entries = " ".join(sorted(os.listdir(cwd))) if cwd else ""
-            recorded.append((list(cmd), Path(cwd).resolve() if cwd else None, entries))
-            return _ran(cmd, slot, where)
-
-        with mock.patch.object(external, "run_tool", side_effect=record):
-            external.run_external_tools(str(self.project), types)
-        return recorded
-
-    def test_l7_external_tools_audit_each_lockfile_in_a_copy(self):
-        # base-fail: the base runs npm audit at the root, and only for a javascript project.
-        self.lockfile("sub")
-        npm = [r for r in self.external([]) if r[0][:1] == ["npm"]]
-        self.assertEqual(len(npm), 1, npm)
-        cmd, where, entries = npm[0]
-        self.assertEqual(cmd, ["npm", "audit", "--package-lock-only"])
-        self.assertEqual(entries, COPY)
-        self.assertFalse(where.is_relative_to(self.project.resolve()))
-
-    def test_l8_no_lockfile_runs_no_npm_audit(self):
-        npm = [r for r in self.external(["javascript"]) if r[0][:1] == ["npm"]]
-        self.assertEqual(npm, [])
-
-    def test_y3_yarn_audit_needs_a_javascript_project(self):
-        """TC-Y3 (TASK 112 R5.1), formerly TC-L9b."""
-        (self.project / "yarn.lock").write_text("")
-        (self.project / "package.json").write_text('{"name": "x"}')
-        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["yarn"]], [])
-
-    def test_l9c_lockfile_without_package_json_is_skipped(self):
-        self.lockfile("sub", package=False)
-        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["npm"]], [])
-
-    def test_y1_yarn_audit_runs_in_a_copy(self):
-        """TC-Y1 (TASK 112 R5.1): yarn reads `.yarnrc.yml` where it runs; `yarnPath` there names a
-        script yarn executes. Base-fail: the base runs `yarn audit` in the scanned root."""
-        (self.project / "yarn.lock").write_text("")
-        (self.project / "package.json").write_text(json.dumps({
-            "name": "x", "packageManager": "yarn@4.0.0", "dependencies": {"a": "1"},
-            "devEngines": {"packageManager": {"name": "yarn", "version": "4.0.0"}},
-            "scripts": {"preinstall": "evil"}, "resolutions": {"b": "2"}}))
-        (self.project / ".yarnrc.yml").write_text("yarnPath: evil.js\n")
-        copies = []
-
-        def record(cmd, cwd=None, slot=None, where=".", **_kw):
-            if cmd[:1] == ["yarn"]:
-                copies.append((list(cmd), Path(cwd).resolve(), " ".join(sorted(os.listdir(cwd))),
-                               json.loads((Path(cwd) / "package.json").read_text())))
-            return _ran(cmd, slot, where)
-
-        with mock.patch.object(external, "run_tool", side_effect=record):
-            external.run_external_tools(str(self.project), ["javascript"])
-        self.assertEqual(len(copies), 1, copies)
-        cmd, where, entries, package = copies[0]
-        self.assertEqual(cmd, ["yarn", "audit"])
-        self.assertEqual(entries, "package.json yarn.lock")
-        self.assertFalse(where.is_relative_to(self.project.resolve()))
-        # A corepack `yarn` shim would fetch the version `packageManager` or `devEngines` names;
-        # the copy keeps the dependency fields only (TASK 112 R5.1).
-        self.assertEqual(package, {"name": "x", "dependencies": {"a": "1"}, "resolutions": {"b": "2"}})
-
-    def test_y2_no_regular_package_json_or_a_linked_lockfile_runs_no_yarn(self):
-        """TC-Y2 (TASK 112 R5.1)."""
-        real = self.tmp / "real.lock"
-        real.write_text("")
-        for case in ("no package.json", "linked package.json", "linked yarn.lock"):
-            with self.subTest(case=case):
-                for name in ("yarn.lock", "package.json"):
-                    path = self.project / name
-                    if path.is_symlink() or path.exists():
-                        path.unlink()
-                if case == "linked yarn.lock":
-                    (self.project / "yarn.lock").symlink_to(real)
-                    (self.project / "package.json").write_text('{"name": "x"}')
-                else:
-                    (self.project / "yarn.lock").write_text("")
-                    if case == "linked package.json":
-                        (self.project / "package.json").symlink_to(real)
-                yarn = [r for r in self.external(["javascript"]) if r[0][:1] == ["yarn"]]
-                self.assertEqual(yarn, [])
-
-
-class TestDependencySeverities(AuditTestCase):
-    """TC-D2 to TC-D7 (TASK 118 R3): npm advisories at every severity."""
-
-    def npm_findings(self, result):
-        return [f for f in result["findings"] if f.get("type") == "npm audit"]
-
-    def test_d2_a_moderate_advisory_fails_fail_on_medium_only(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
-        run_audit = _run_audit_module()
-        report = run_audit.run_full_scan(str(self.project), "deps", fail_on="medium")
-        self.assertEqual(run_audit.exit_code(report, "medium"), 1)
-        self.assertEqual(run_audit.exit_code(report, "high"), 0)
-
-    def test_d3_an_info_advisory_is_audited_and_a_missing_npm_is_not(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "info"}}})
-        result = self.scan()
-        self.assertFalse(result["status"].startswith("[?] Not audited"), result["status"])
-        self.assertEqual([f.get("audited", True) for f in self.npm_findings(result)], [True])
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            [finding] = self.npm_findings(self.scan())
-        self.assertEqual((finding["severity"], finding["audited"]), ("info", False))
-
-    def test_d4_an_unknown_severity_and_an_entry_that_is_not_a_map(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "weird"}}})
-        result = self.scan()
-        self.assertEqual(result["npm_audit_counts"]["sub/package-lock.json"]["unknown"], 1)
-        self.assertEqual([(f["severity"], f["message"]) for f in self.npm_findings(result)], [
-            ("low", "sub/package-lock.json: 1 vulnerabilities of unknown severity")])
-        self.set_reply({"vulnerabilities": {"x": "high"}})
-        counts = self.scan()["npm_audit_counts"]["sub/package-lock.json"]
-        self.assertEqual((counts["low"], counts["unknown"]), (1, 0))
-
-    def test_d5_each_finished_audit_has_all_six_counts(self):
-        self.lockfile("sub")
-        self.assertEqual(self.scan()["npm_audit_counts"], {"sub/package-lock.json": ZERO_COUNTS})
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "low"}}})
-        self.assertEqual(self.scan()["npm_audit_counts"]["sub/package-lock.json"],
-                         dict(ZERO_COUNTS, low=2))
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["npm_audit_counts"], {})
-
-    def test_d6_section_status_first_match_wins(self):
-        self.lockfile("sub")
-        for label, reply, status in (
-                ("critical", {"vulnerabilities": {"x": {"severity": "critical"}}},
-                 "[!!] Critical vulnerabilities"),
-                ("high", HIGH, "[!] HIGH: Dependency issues"),
-                ("moderate", {"vulnerabilities": {"x": {"severity": "moderate"}}},
-                 "[?] Dependency issues below high"),
-                ("low", {"vulnerabilities": {"x": {"severity": "low"}}},
-                 "[?] Dependency issues below high"),
-                ("info only", {"vulnerabilities": {"x": {"severity": "info"}}}, "[OK] Secure"),
-                ("none", {"vulnerabilities": {}}, "[OK] Secure")):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                self.assertEqual(self.scan()["status"], status)
-        with self.subTest(case="not audited outranks moderate"):
-            self.lockfile("other", content='{"name": "broken"}')
-            self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")
-
-    def test_d7_summary_counts_low_and_info_and_findings_are_sorted(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "info"},
-                                            "c": {"severity": "critical"}}})
-        report = _run_audit_module().run_full_scan(str(self.project), "deps")
-        summary = report["summary"]
-        self.assertEqual((summary["critical"], summary["low"], summary["info"]), (1, 1, 1))
-        # Two lockfiles each yield a critical and a low finding: unsorted, a low one precedes the
-        # second critical one.
-        self.lockfile("tub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"},
-                                            "c": {"severity": "critical"}}})
-        severities = [f["severity"] for f in self.scan()["findings"]]
-        self.assertEqual(severities, ["critical", "critical", "low", "low"])
-
-    def test_d8_a_lockfile_that_cannot_be_copied_is_not_audited(self):
-        sub = self.project / "sub"
-        sub.mkdir()
-        os.mkfifo(sub / "package-lock.json")
-        (sub / "package.json").write_text('{"name": "x"}')
-        [info] = self.infos(self.scan()["findings"])
-        self.assertEqual((info["message"], info["audited"]),
-                         ("sub/package-lock.json: not audited, the lockfile could not be copied",
-                          False))
-        proc = subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", "deps",
-                               "--output", "json"], capture_output=True, text=True, timeout=120)
-        self.assertEqual(json.loads(proc.stdout)["summary"]["scan_complete"], False)
-        self.assertEqual(proc.returncode, 3, proc.stderr)
-
-
-class ToolCase(unittest.TestCase):
-    """A temporary project, and a `bin` directory of fake tools that is the whole `PATH`.
-
-    The `.git` walk of `run_external_tools` stops at the temporary directory, so a `.git` above it
-    takes no part.
-    """
-
-    def setUp(self):
-        self.tmp = Path(tempfile.mkdtemp()).resolve()
-        self.addCleanup(shutil.rmtree, self.tmp)
-        self.project = self.tmp / "project"
-        self.project.mkdir()
-        self.bin = self.tmp / "bin"
-        self.bin.mkdir()
-        patcher = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
-        patcher.start()
-        self.addCleanup(patcher.stop)
-        walk = external.find_git_entry
-        stopped = mock.patch.object(external, "find_git_entry",
-                                    side_effect=lambda root, stop=None: walk(root, stop=self.tmp))
-        stopped.start()
-        self.addCleanup(stopped.stop)
-
-    def tool(self, name, body="exit 0"):
-        path = self.bin / name
-        path.write_text(f"#!/bin/sh\n{body}\n")
-        path.chmod(0o755)
-
-    def tools(self, *names):
-        for name in names:
-            self.tool(name)
-
-    def records(self, types=(), fail_on=None):
-        return external.run_external_tools(str(self.project), list(types), fail_on=fail_on)
-
-    @staticmethod
-    def slot(records, slot):
-        return [r for r in records if r["slot"] == slot]
-
-    def cli(self, *args):
-        """`run_audit.py` as a subprocess, with `PATH` the fake tools only."""
-        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
-        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), *args], env=env,
-                              capture_output=True, text=True, timeout=120)
-
-    def cli_json(self, *args):
-        proc = self.cli(*args, "--output", "json")
-        return proc, json.loads(proc.stdout)
-
-
-class TestToolRecords(ToolCase):
-    """TC-E2, TC-E4 to TC-E7, TC-E9, TC-E13, TC-E15, TC-E16 drive `run_external_tools` in process."""
-
-    def test_e2_a_tool_that_exits_0_is_ran(self):
-        self.tool("semgrep")
-        [record] = self.slot(self.records(), "sast")
-        self.assertEqual((record["status"], record["exit_code"], record["tool"], record["where"]),
-                         ("ran", 0, "semgrep", "."))
-        self.assertIsNone(record["reason"])
-
-    def test_e2_a_missing_tool_is_not_installed(self):
-        [record] = self.slot(self.records(), "sast")
-        self.assertEqual((record["status"], record["exit_code"]), ("not_installed", None))
-
-    def test_e4_a_timeout_starts_the_fallback_of_the_tree_slot_only(self):
-        self.tool("gitleaks", "exec /bin/sleep 5")
-        self.tool("trufflehog")
-        (self.project / ".git").mkdir()
-        with mock.patch.object(helpers, "TOOL_TIMEOUT", 1):
-            records = self.records()
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
-                         [("gitleaks", "timed_out"), ("trufflehog", "ran")])
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-history")],
-                         [("gitleaks", "timed_out")])
-        self.assertIn("secrets-history", [slot for slot, _ in external.incomplete_slots(records)])
-
-    def test_e5_the_fallback_fills_the_tree_slot_and_the_history_slot_has_none(self):
-        self.tool("trufflehog")
-        (self.project / ".git").mkdir()
-        records = self.records()
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
-                         [("gitleaks", "not_installed"), ("trufflehog", "ran")])
-        self.assertEqual([r["tool"] for r in self.slot(records, "secrets-history")], ["gitleaks"])
-        missing = [slot for slot, _ in external.incomplete_slots(records)]
-        self.assertIn("secrets-history", missing)
-        self.assertNotIn("secrets-tree", missing)
-
-    def test_e6_the_git_entry_at_or_above_the_root(self):
-        find = external.find_git_entry.side_effect
-        self.assertIsNone(find(str(self.project)))
-        cases = (("a directory", lambda g: g.mkdir(), "dir"),
-                 ("a file", lambda g: g.write_text("gitdir: elsewhere\n"), "file"),
-                 ("a link", lambda g: g.symlink_to(self.tmp / "real", target_is_directory=True),
-                  "link"),
-                 ("a fifo", lambda g: os.mkfifo(g), "other"))
-        (self.tmp / "real").mkdir()
-        for label, make, kind in cases:
-            with self.subTest(case=label):
-                git = self.project / ".git"
-                make(git)
-                try:
-                    self.assertEqual(find(str(self.project)), kind)
-                finally:
-                    shutil.rmtree(git) if git.is_dir() and not git.is_symlink() else git.unlink()
-        with self.subTest(case="in the parent"):
-            (self.tmp / ".git").mkdir()
-            self.assertEqual(find(str(self.project)), "dir")
-            (self.tmp / ".git").rmdir()
-        with self.subTest(case="a root through a link"):
-            sub = self.tmp / "repo" / "sub"
-            sub.mkdir(parents=True)
-            (self.tmp / "repo" / ".git").mkdir()
-            (self.tmp / "alias").symlink_to(sub, target_is_directory=True)
-            self.assertEqual(external.find_git_entry(str(self.tmp / "alias"), stop=self.tmp), "dir")
-
-    def test_e6_the_history_slot_by_git_entry(self):
-        log = self.tmp / "gitleaks.log"
-        self.tool("gitleaks", f'printf "%s|%s\\n" "$PWD" "$*" >> "{log}"')
-        [record] = self.slot(self.records(), "secrets-history")
-        self.assertEqual((record["status"], record["reason"], record["command"]),
-                         ("not_applicable", "no .git at or above the scanned root", GITLEAKS_HISTORY))
-        (self.project / ".git").symlink_to(self.tmp, target_is_directory=True)
-        [record] = self.slot(self.records(), "secrets-history")
-        self.assertEqual((record["status"], record["reason"]), ("not_run", ".git is a symbolic link"))
-        (self.project / ".git").unlink()
-        expected = f"{self.project}|{' '.join(GITLEAKS_HISTORY[1:])}"
-        cases = (("a directory at the root", lambda: (self.project / ".git").mkdir()),
-                 ("a file at the root",
-                  lambda: (self.project / ".git").write_text("gitdir: elsewhere\n")),
-                 ("a directory in the parent", lambda: (self.tmp / ".git").mkdir()),
-                 ("a bare repository at the root", lambda: self.bare(self.project)))
-        for label, make in cases:
-            with self.subTest(case=label):
-                make()
-                if log.exists():
-                    log.unlink()
-                try:
-                    [record] = self.slot(self.records(), "secrets-history")
-                    self.assertEqual((record["status"], record["command"]),
-                                     ("ran", GITLEAKS_HISTORY))
-                    runs = [run for run in log.read_text().splitlines() if "--no-git" not in run]
-                    self.assertEqual(runs, [expected])
-                finally:
-                    for path in (self.project / ".git", self.tmp / ".git", self.project / "HEAD",
-                                 self.project / "objects", self.project / "refs"):
-                        if path.is_dir():
-                            shutil.rmtree(path)
-                        elif path.exists():
-                            path.unlink()
-
-    def bare(self, root):
-        (root / "HEAD").write_text("ref: refs/heads/main\n")
-        (root / "objects").mkdir()
-        (root / "refs").mkdir()
-
-    def test_e6_a_bare_repository_and_an_unreadable_directory(self):
-        find = external.find_git_entry.side_effect
-        self.bare(self.project)
-        self.assertEqual(find(str(self.project)), "bare")
-        shutil.rmtree(self.project / "objects")
-        (self.tmp / "objects").mkdir()
-        (self.project / "objects").symlink_to(self.tmp / "objects", target_is_directory=True)
-        self.assertEqual(find(str(self.project)), "bare-link")
-        for name in ("HEAD", "objects", "refs"):
-            path = self.project / name
-            shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()
-        if os.geteuid() == 0:
-            self.skipTest("root reads a directory without its search permission")
-        locked = self.project / "locked"
-        locked.mkdir()
-        locked.chmod(0o600)
-        self.addCleanup(locked.chmod, 0o700)
-        self.assertEqual(find(str(locked)), "unreadable")
-
-    def test_e6_each_declined_history_record(self):
-        for kind, status, reason in (
-                ("link", "not_run", ".git is a symbolic link"),
-                ("other", "not_run", ".git is not a directory or a regular file"),
-                ("unreadable", "not_run", ".git could not be read"),
-                ("bare-link", "not_run", "the bare repository holds a symbolic link"),
-                (None, "not_applicable", "no .git at or above the scanned root")):
-            with self.subTest(kind=kind):
-                external.find_git_entry.side_effect = lambda root, stop=None, kind=kind: kind
-                records = self.records()
-                [record] = self.slot(records, "secrets-history")
-                self.assertEqual((record["status"], record["reason"], record["command"]),
-                                 (status, reason, GITLEAKS_HISTORY))
-                missing = [slot for slot, _ in external.incomplete_slots(records)]
-                self.assertEqual("secrets-history" in missing, status == "not_run")
-
-    def test_e7_the_tree_slot_reads_the_working_tree(self):
-        self.tool("gitleaks")
-        [record] = self.slot(self.records(), "secrets-tree")
-        self.assertEqual(record["command"], GITLEAKS_TREE)
-
-    def test_e9_options_that_make_a_finding_exit_non_zero(self):
-        self.tools("trufflehog", "checkov", "trivy", "npm")
-        lock = self.project / "package-lock.json"
-        lock.write_text("{}")
-        (self.project / "package.json").write_text('{"name": "x"}')
-        records = self.records(["iac"])
-        [tree] = [r for r in self.slot(records, "secrets-tree") if r["tool"] == "trufflehog"]
-        self.assertIn("--fail", tree["command"])
-        [trivy] = self.slot(records, "iac-misconfig")
-        self.assertEqual(trivy["command"][-3:], ["--exit-code", "1", "."])
-        for fail_on, level in ((None, None), ("medium", "moderate"), ("high", "high"),
-                               ("critical", "critical")):
-            with self.subTest(fail_on=fail_on):
-                [npm] = self.slot(self.records(fail_on=fail_on), "npm-audit:package-lock.json")
-                levels = [a for a in npm["command"] if a.startswith("--audit-level")]
-                self.assertEqual(levels, [f"--audit-level={level}"] if level else [])
-
-    def test_e13_each_skip_reason_is_a_not_run_record(self):
-        self.tools("npm", "yarn")
-        sub = self.project / "sub"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        [npm] = self.slot(self.records(), "npm-audit:sub/package-lock.json")
-        self.assertEqual((npm["status"], npm["reason"], npm["where"]),
-                         ("not_run", "no package.json beside it", "sub/package-lock.json"))
-        shutil.rmtree(sub)
-        real = self.tmp / "real.lock"
-        real.write_text("")
-        lock, package = self.project / "yarn.lock", self.project / "package.json"
-        for label, reason in (("link", "yarn.lock is a link or not a regular file"),
-                              ("no package.json", "no package.json beside yarn.lock"),
-                              ("not an object", "package.json is not a JSON object")):
-            with self.subTest(case=label):
-                for path in (lock, package):
-                    if path.is_symlink() or path.exists():
-                        path.unlink()
-                if label == "link":
-                    lock.symlink_to(real)
-                else:
-                    lock.write_text("")
-                if label == "not an object":
-                    package.write_text("[]")
-                records = self.records(["javascript"])
-                [yarn] = self.slot(records, "yarn-audit")
-                self.assertEqual((yarn["status"], yarn["reason"], yarn["where"]),
-                                 ("not_run", reason, "yarn.lock"))
-                self.assertIn("yarn-audit", [slot for slot, _ in external.incomplete_slots(records)])
-                summary = _run_audit_module().summarize(
-                    {"scans": {}, "external": external.external_section(records)})
-                self.assertIn(f"external yarn-audit: yarn not_run, {reason}", summary["not_run"])
-        for path in (lock, package):
-            if path.is_symlink() or path.exists():
-                path.unlink()
-        with self.subTest(case="a lockfile that cannot be copied"):
-            os.mkfifo(self.project / "package-lock.json")
-            package.write_text('{"name": "x"}')
-            [npm] = self.slot(self.records(), "npm-audit:package-lock.json")
-            self.assertEqual((npm["status"], npm["reason"]),
-                             ("not_run", "the lockfile could not be copied"))
-
-    def test_e15_three_slots_run_for_a_project_with_no_type(self):
-        self.assertEqual(scanners_types(self.project), [])
-        report = _run_audit_module().run_full_scan(str(self.project), "external")
-        slots = [r["slot"] for r in report["external"]["tools"]]
-        for slot in ("sast", "secrets-tree", "secrets-history"):
-            self.assertIn(slot, slots)
-
-    def test_e16_external_section_status(self):
-        def rec(slot, status):
-            return {"slot": slot, "status": status}
-        section = external.external_section
-        self.assertEqual(section([rec("a", "ran"), rec("b", "not_applicable")])["status"],
-                         "COMPLETE")
-        self.assertEqual(section([rec("a", "ran"), rec("b", "not_installed")])["status"],
-                         "PARTIAL")
-        self.assertEqual(section([rec("a", "not_installed"), rec("a", "ran")])["status"],
-                         "COMPLETE")
-        self.assertEqual(section([rec("a", "not_installed"), rec("b", "not_applicable")])["status"],
-                         "NOT_RUN")
-
-
-def scanners_types(project):
-    return sys.modules[NAME].detect_project_types(str(project))
-
-
-class TestRunAudit(ToolCase):
-    """TC-E1, TC-E3, TC-E8, TC-E10 to TC-E12, TC-E14, TC-E17 drive `run_audit.py`."""
-
-    def test_e1_every_tool_missing_is_not_run_and_exits_3(self):
-        # base-fail: the base prints no report for `external` and exits 0.
-        proc = self.cli("--scan-type", "external", "--output", "json")
-        report = json.loads(proc.stdout)
-        statuses = {r["status"] for r in report["external"]["tools"]}
-        self.assertLessEqual(statuses, {"not_installed", "not_applicable"}, report["external"])
-        self.assertIn("not_installed", statuses)
-        self.assertEqual(report["external"]["status"], "NOT_RUN")
-        self.assertEqual(report["scans"], {})
-        self.assertFalse(report["summary"]["scan_complete"])
-        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
-        self.assertEqual(proc.returncode, 3, proc.stderr)
-
-    def complete_python_project(self):
-        (self.project / "app.py").write_text("x = 1\n")
-        self.tools("semgrep", "gitleaks", "pip-audit")
-        self.tool("bandit", "exit 1")
-
-    def test_e3_a_tool_exit_fails_fail_on_and_is_listed_without_it(self):
-        self.complete_python_project()
-        proc = self.cli("--scan-type", "external", "--fail-on", "critical")
-        self.assertEqual(proc.returncode, 1, proc.stderr)
-        self.assertIn("[GATE] --fail-on critical:", proc.stderr)
-        self.assertIn("bandit exited 1 (python-sast)", proc.stderr)
-        proc, report = self.cli_json("--scan-type", "external")
-        self.assertEqual(proc.returncode, 0, proc.stderr)
-        self.assertEqual(report["summary"]["tool_exits"], ["bandit exited 1 (python-sast)"])
-        self.assertTrue(report["summary"]["scan_complete"], report["summary"]["not_run"])
-
-    def test_e8_stdout_holds_one_json_document(self):
-        self.tool("semgrep", "echo semgrep-stdout; exit 1")
-        self.tool("gitleaks", "echo gitleaks-stdout")
-        proc = self.cli("--scan-type", "external", "--output", "json", "--fail-on", "critical")
-        report = json.loads(proc.stdout)
-        self.assertEqual(report["scan_type"], "external")
-        self.assertNotIn("semgrep-stdout", proc.stdout)
-        self.assertIn("semgrep-stdout", proc.stderr)
-        self.assertNotIn("[GATE]", proc.stdout)
-        self.assertIn("[GATE]", proc.stderr)
-        self.assertEqual(proc.returncode, 1)
-
-    def test_e10_a_breach_and_a_part_not_run_exit_1(self):
-        # The breach: the SBOM scan's medium finding for a project with no SBOM.
-        proc, report = self.cli_json("--scan-type", "all", "--fail-on", "medium")
-        self.assertIn("medium", [f["severity"] for f in report["scans"]["sbom"]["findings"]])
-        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
-        self.assertIn("[GATE] --fail-on medium:", proc.stderr)
-        self.assertIn("[INCOMPLETE]", proc.stderr)
-        self.assertEqual(proc.returncode, 1)
-
-    def test_e11_deps_with_npm_missing_exits_3(self):
-        sub = self.project / "sub"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        (sub / "package.json").write_text('{"name": "x"}')
-        proc, report = self.cli_json("--scan-type", "deps")
-        self.assertEqual(report["summary"]["not_run"],
-                         ["dependencies: sub/package-lock.json: not audited, npm is not installed"])
-        self.assertIn("[INCOMPLETE]", proc.stderr)
-        self.assertEqual(proc.returncode, 3)
-
-    def test_e12_overall_status(self):
-        run_audit = _run_audit_module()
-        report = run_audit.run_full_scan(str(self.project), "external")
-        self.assertTrue(report["summary"]["overall_status"].startswith("[?] INCOMPLETE: "),
-                        report["summary"])
-        self.complete_python_project()
-        report = run_audit.run_full_scan(str(self.project), "external")
-        self.assertEqual(report["summary"]["overall_status"], "[?] REVIEW RECOMMENDED")
-
-    def test_e14_summary_prints_one_line_per_record(self):
-        self.tools("semgrep", "gitleaks")
-        _proc, report = self.cli_json("--scan-type", "external")
-        out = self.cli("--scan-type", "external").stdout
-        for record in report["external"]["tools"]:
-            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
-            with self.subTest(slot=record["slot"], tool=record["tool"]):
-                self.assertEqual(sum(1 for x in out.splitlines() if x.startswith(line)), 1, out)
-        for label in ("Critical", "High", "Medium", "Low", "Info"):
-            self.assertIn(f"\n  {label}: 0\n", out)
-
-    def test_e18_a_killed_tool_leaves_its_slot_not_run(self):
-        self.tool("semgrep", "kill -9 $$")
-        records = self.records()
-        [record] = self.slot(records, "sast")
-        self.assertEqual(record["status"], "killed")
-        self.assertLess(record["exit_code"], 0)
-        self.assertIn("sast", [slot for slot, _ in external.incomplete_slots(records)])
-
-    def test_e19_printable_escapes_control_format_and_separator_characters(self):
-        self.assertEqual(helpers.printable("a\x1bb\nc\u202ed\u2028e\u2029f\U000e0001g h"),
-                         "a\\x1bb\\x0ac\\u202ed\\u2028e\\u2029f\\U000e0001g h")
-
-    def test_e19_tree_text_is_escaped_in_printed_output(self):
-        sub = self.project / "a\x1b[31mb"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        (sub / "package.json").write_text('{"name": "x"}')
-        summary = self.cli("--scan-type", "deps")
-        for stream in (summary.stdout, summary.stderr):
-            self.assertNotIn("\x1b", stream)
-        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stderr)
-        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stdout)
-        proc, report = self.cli_json("--scan-type", "deps")
-        self.assertNotIn("\x1b", proc.stdout)
-        self.assertIn("dependencies: a\x1b[31mb/package-lock.json: not audited, npm is not installed",
-                      report["summary"]["not_run"])
-
-    def test_e17_the_summary_counts_every_finding_before_the_cut(self):
-        run_audit = _run_audit_module()
-        findings = [{"type": "t", "severity": "low"}] * 30 + [{"type": "t", "severity": "critical"}]
-        stub = {"tool": "stub", "findings": findings, "status": "[?]"}
-        with mock.patch.object(run_audit, "scan_secrets", return_value=stub):
-            report = run_audit.run_full_scan(str(self.project), "secrets")
-        self.assertEqual((report["summary"]["total_findings"], report["summary"]["critical"]),
-                         (31, 1))
-        self.assertEqual(len(report["scans"]["secrets"]["findings"]), 30)
-        self.assertEqual(run_audit.exit_code(report, "critical"), 1)
-
-
-class TestNonRegularFiles(ToolCase):
-    """TC-F1 to TC-F3 (TASK 119 R1): a subprocess per scan type, `PATH` the fake `bin` only."""
-
-    #: FIFOs under the scanned root, and how many of them each in-process scan reads.
-    FIFOS = ("app.js", "config.json", "main.tf", ".mcp.json")
-    READS = {"secrets": 3, "code_patterns": 1, "configuration": 2, "iac": 3, "mcp_agentic": 3}
-    TYPES = {"secrets": "secrets", "code_patterns": "patterns", "configuration": "config",
-             "iac": "iac", "mcp_agentic": "mcp"}
-
-    def scan(self, scan_type):
-        """`run_audit.py --scan-type <type>` with a 20 s timeout; a blocked scan fails the case."""
-        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
-        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", scan_type,
-                               "--output", "json"], env=env, capture_output=True, text=True,
-                              timeout=20)
-
-    def test_f1_each_scan_skips_a_fifo(self):
-        for name in self.FIFOS:
-            os.mkfifo(self.project / name)
-        for section, scan_type in self.TYPES.items():
-            with self.subTest(scan=scan_type):
-                proc = self.scan(scan_type)
-                report = json.loads(proc.stdout)
-                self.assertEqual(report["scans"][section]["skipped_files"], self.READS[section],
-                                 proc.stderr)
-                self.assertEqual(proc.stderr.count("not a regular file"), self.READS[section],
-                                 proc.stderr)
-
-    def test_f2_a_fifo_requirements_txt_is_not_a_hash_pinned_lock(self):
-        (self.project / "pyproject.toml").write_text('[project]\nname = "x"\n')
-        os.mkfifo(self.project / "requirements.txt")
-        report = json.loads(self.scan("deps").stdout)
-        self.assertTrue(any(f.get("type") == "Missing Lock File" and "python" in f["message"]
-                            for f in report["scans"]["dependencies"]["findings"]), report)
-
-    @staticmethod
-    def secret(path):
-        path.write_text('const key = "' + "AKIA" + "Z" * 16 + '";\n')
-
-    def test_f3_a_link_to_a_regular_file_is_still_read(self):
-        (self.project / "sub").mkdir()
-        self.secret(self.project / "sub" / "real.txt")
-        (self.project / "link.js").symlink_to(self.project / "sub" / "real.txt")
-        report = json.loads(self.scan("secrets").stdout)
-        findings = report["scans"]["secrets"]["findings"]
-        self.assertTrue(any(f.get("file", "").endswith("link.js") for f in findings), findings)
-
-    def test_f9_a_link_out_of_the_root_is_skipped(self):
-        self.secret(self.tmp / "outside.txt")
-        (self.project / "out.js").symlink_to(self.tmp / "outside.txt")
-        proc = self.scan("secrets")
-        section = json.loads(proc.stdout)["scans"]["secrets"]
-        self.assertEqual(section["findings"], [], section)
-        self.assertEqual(section["skipped_files"], 1)
-        self.assertIn("outside the scanned root", proc.stderr)
-
-
-class TestHelperPath(AuditTestCase):
-    """TC-F4 (TASK 119 R2): the fake `npm` sees the system directories, not the machine's tools."""
-
-    def test_f4_path_is_the_fake_bin_and_the_system_directories(self):
-        self.assertEqual(os.environ["PATH"].split(os.pathsep), [str(self.bin), "/usr/bin", "/bin"])
-
-
-class TestOpenRegularText(unittest.TestCase):
-    """TC-F6 to TC-F8 (TASK 119 R1.1)."""
-
-    def setUp(self):
-        self.tmp = Path(tempfile.mkdtemp())
-        self.addCleanup(shutil.rmtree, self.tmp)
-
-    def test_f6_open_passes_binary_and_noctty(self):
-        seen = []
-
-        def fake_open(path, flags, *args, **kwargs):
-            seen.append(flags)
-            raise OSError("stop")
-
-        with mock.patch.object(helpers.os, "O_BINARY", 0x10000, create=True), \
-                mock.patch.object(helpers.os, "O_NOCTTY", 0x20000, create=True), \
-                mock.patch.object(helpers.os, "open", side_effect=fake_open):
-            with self.assertRaises(OSError):
-                helpers.open_regular_text(self.tmp / "x.js")
-        self.assertEqual(seen[0] & 0x30000, 0x30000, hex(seen[0]))
-
-    def test_f7_a_refusal_closes_the_descriptor(self):
-        link = self.tmp / "null.js"
-        link.symlink_to("/dev/null")
-        before = len(os.listdir("/dev/fd"))
-        for _ in range(1000):
-            with self.assertRaisesRegex(OSError, "not a regular file"):
-                helpers.open_regular_text(link)
-        self.assertEqual(len(os.listdir("/dev/fd")), before)
-
-    def test_f8_size_limit_on_the_descriptor_and_a_blocking_stream(self):
-        big = self.tmp / "big.js"
-        big.write_text("x" * 100)
-        config = importlib.import_module(f"{NAME}.config")
-        with mock.patch.object(config, "MAX_FILE_SIZE", 10):
-            with self.assertRaisesRegex(OSError, "exceeds the size limit"):
-                helpers.open_regular_text(big)
-        with helpers.open_regular_text(big) as stream:
-            if hasattr(os, "O_NONBLOCK"):
-                import fcntl
-                self.assertFalse(fcntl.fcntl(stream.fileno(), fcntl.F_GETFL) & os.O_NONBLOCK)
-            self.assertEqual(stream.read(), "x" * 100)
-
-
-class TestPrintableBackslash(unittest.TestCase):
-    """TC-F5 (TASK 119 R3)."""
-
-    def test_f5_printable_doubles_the_backslash(self):
-        self.assertEqual(helpers.printable("\\"), "\\\\")
-        self.assertEqual(helpers.printable("a\\x0ab"), "a\\\\x0ab")
-        self.assertEqual(helpers.printable("a\x1bb"), "a\\x1bb")
-
-
-if __name__ == "__main__":
-    unittest.main()
~~~~

### G1 — the apply and the gates

- `git apply --whitespace=nowarn`: exit 0. Postcondition: each final path hashes to its staged
  file's recorded value; the staged files are gone; `git apply --check -R` passes.
- `run_gates.sh`: 17 PASS; `tests/run_tests.py` ran 610 tests, OK (601 before). The skill's tests:
  30 passed. `validate_skill.py .agent/skills/security-audit`: exit 0. `check_positional_refs.py
  --targets-changed`: no `REFERENT_MOVED` or `REFERENT_ABSENT` from the patch. 14 paths, each
  declared.

## Stage 4 — fingerprint `3ac73864ba94`

Both agents, resumed, quoted the fingerprint at their start and end; equal.

- **Code review: APPROVED**, no finding. The final files hash to the approved staged texts, the
  modes are unchanged, the staged files are gone; `tests/test_lockfile_audit.py` on the final
  paths: 68 passed. The staged names remain only in the records of TASK 118 and TASK 119.
- **Security audit: PASS**, `scan_status: findings`. The scanner on disk: exit 0,
  `external.status` COMPLETE, `not_run` empty; the tool exits are findings, none in a changed file;
  bandit's LOW hits in the changed files are argument-list calls. The repository holds no FIFO,
  socket, device or link out of the root that the scans would read, so the run reports no such
  skip.

Under D5 the record keeps two accepted items: the race between `realpath` and the open, and a hard
link to an outside file.

**Scratch files deleted after G:** `staging.py`, `stage_driver.py`, `bootstrap_next.py`,
`mutation_driver.py`, `gen_stage3_patch.py`, `regcheck.py`, `gates/` with its logs, `g1-*.txt`, and
the reviewers' directories.

## Retro (§6)

The retro question listed three candidates. The operator chose one: "Ревью расширяли задачу". It
is filed as WI-52, "Stage-2 reviews can widen a framework-upgrade task beyond its changed lines"
(a work-item for the framework owner's review: state the boundary of D5 in `framework-upgrade`
stage 2 and in the reviewer briefs). The number 52 was free again: the earlier WI-52 of this run
was never committed. The other two candidates are dropped. The claim
`framework-upgrade-wi-51-scanner-residuals` is released.
