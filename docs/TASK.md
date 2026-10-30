# TASK 137 — The Mermaid renderers run on native Windows (MR-1)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 137 |
| Slug | mermaid-renderers-windows |
| Type | Standard pipeline of a TIER 2 skill, reduced process (D3) |
| Source | MR-1; the Windows report of loyalty-api-java (2026-10-28); the operator's request of 2026-10-29 |
| Base revision | `f4588ea` |
| Closes | MR-1 |
| Archive name | `task-137-mermaid-renderers-windows.md` |
| Revision | 4 |

**Request.** The operator filed the four open items of the Windows report and set their order:
MR-1, WI-60, WI-61, PT-1. This task is MR-1: on native Windows `setup_renderers.sh` accepts no
browser, so `render_check.py` renders no figure. Windows means Windows 10 or later with Git Bash,
Node.js 22.13 or later and Python 3.11 or later.

**Revision 2** follows the code review (CHANGES REQUESTED: one MAJOR, eight MINOR, eleven NIT)
and the security audit (FAIL: one CRITICAL, one MEDIUM, four LOW, eight INFO) of `76a02aa`. The
fix pass:
- C-1: the browser floor moves to 156.0.8078.73 (D11);
- M-1 and m3: on Windows the install home lies in the user profile (D12);
- m7: the Windows job has its own workflow (D13); L-3: npx runs no install script;
- m1, L-4, I-3: a reparse point is a link, a link has size 0, and a digest that cannot be built
  is a refusal; ReFS is a documented limit;
- L-1, L-2, I-1, I-2: a drive in each PATH entry, `taskkill` by `GetSystemDirectoryW`, no program
  by a bare name, the `bin` value checked by its text;
- m4: `render_check.py` writes no encoding error on Windows;
- m5, m6, N10: TC-W9 to TC-W16;
- M1, N2, N3, N7, N8, m8, I-4, I-5: the records, the comments and the documents.

Not taken, with the reason in §5: N1, N4, N6, N9, N11, I-6, I-7, I-8.

**Revision 3** follows the narrow security audit of the fix pass, `76a02aa..1780b3b` (FAIL: one
CRITICAL, one HIGH, one MEDIUM, two LOW, seven INFO), on the operator's choice of 2026-10-30. The
second fix pass:
- C-1 again: Chrome for Testing moved Stable to 156.0.8078.80 on 2026-10-29, 21 security fixes
  over .73 (CVE-2026-76024, Critical, among them); the floor follows (D11);
- H-1: `install_problem` refuses a stamped tree hash that `browsers.json` does not record and
  `MERMAID_RENDER_BROWSER_SHA256` does not name (R18);
- M-2: on Windows `--out` lies in the profile (R14);
- L-1: `debug.log` is left out only while it has one link (R15);
- L-2: the Windows job installs the browser with the `@puppeteer/browsers` of the v10 lockfile
  (R11);
- I-a, I-c, I-d, I-f: an absolute `USERPROFILE` in the setup, the bounds of
  `GetSystemDirectoryW`, `--json` in ASCII on Windows, the branch pattern `**`;
- I-b, I-e: documented in `references/scripts-and-setup.md` §3; I-g needs no change.

**Revision 4** follows the operator's choice of 2026-10-30 (D16): a pinned browser build went
stale in hours, and no one is to bump it again. The setup installs the current stable build
itself; `browsers.json`, `BROWSER_MIN_BUILD` and `PUPPETEER_CACHE_DIR` go.

**Measured at the base** (`f4588ea`; the report ran `155441a`, which holds the same code). S/
stands for `.agent/skills/mermaid-authoring-guidelines/scripts/` in prose; each positional
reference below names its full path:
1. The glob of `browser_candidates` names no `.exe`. Node reads the path without `.exe` and fails
   with `ENOENT` (the report).
   `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:219@f4588ea`
   `chrome-headless-shell-*/chrome-headless-shell; do`
2. Node on Windows defines no `process.getuid` (the report).
   `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:281@f4588ea`
   `uid = process.getuid()`
3. The owner and mode checks read `st.uid`, `st.gid` and the bits `0o002` and `0o020`. Node on
   Windows reports a writable file with mode `0o666`.
   `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:282@f4588ea`
   `const open = (st, full) =>`
4. `private_problem` reads the owner and mode that Git Bash emulates. Git for Windows mounts its
   drives with `noacl`, so the bits do not reflect the ACL.
   `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:164@f4588ea`
   `private_problem() {`
5. Python on Windows reports a writable `.exe` with mode `0o777`, so each browser is refused.
   `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py:470@f4588ea`
   `if mode & stat.S_IWOTH or`
6. The stat digest holds `st_dev`, `st_mode` and `st_ctime_ns`. On Windows Python reports the
   64-bit volume serial, adds `0o111` to the mode of an `.exe`, and reports the creation time as
   `st_ctime`. Node reports the 32-bit serial, no `0o111`, and the change time. Not run on
   Windows; read from the CPython and libuv sources.
   `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py:399@f4588ea`
   `str(st.st_mode), str(st.st_size),`
7. On Windows `.bin/mmdc` is a shell script, which `CreateProcess` does not run (`WinError 193`).
   Each render ends `not_rendered`.
   `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py:697@f4588ea`
   `cmd = [str(renderer.mmdc), "-q",`
8. Neither `os.killpg` nor `signal.SIGKILL` exists on Windows, so a render that times out raises
   `AttributeError`.
   `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py:653@f4588ea`
   `os.killpg(proc.pid, sig)`
   `.agent/skills/mermaid-authoring-guidelines/scripts/render_check.py:685@f4588ea`
   `_signal_group(proc, signal.SIGKILL)`
9. `browsers.json` of the skill records a tree hash for `mac_arm` only.

Causes 3 to 9 hide behind causes 1 and 2: no run on Windows has reached them.

## 1. Decisions

- D1, 2026-10-29, operator: on Windows the browser check keeps the tree hash and the stat digest,
  and makes no owner or mode check. Rejected: the hash plus a path under `%USERPROFILE%`, which
  refuses a `PUPPETEER_CACHE_DIR` set elsewhere; the hash plus a read of the ACL, whose `icacls`
  output is localized and slow to parse.
- D2, 2026-10-29, operator: the Windows CI job measures the tree hash of the `win64` build by a
  smoke render, and `browsers.json` records it. Rejected: an override that the operator sets on
  each Windows machine.
- D3, 2026-10-29, operator: a reduced process, as TASK 134 D1. The run has a TASK and a PLAN,
  edits in place, the tests first and red, and the gates. One code reviewer with the exhaustive
  prompt and one security auditor review the change, and one fix pass follows. Rejected: the
  standard pipeline with its reviewer gates, for its cost; Light Mode, which has no security audit
  for a change of a security check. The skill is TIER 2, so `/framework-upgrade` does not apply.
- D4, orchestrator: on Windows a row of the stat digest is `[path, kind, inode, size, mtime in
  ns]`, with size 0 for a directory. Measured in CI run 40920523466 over the 297 entries of the
  `win64` build:
  - Node and Python agree on the inode, the mtime and the birth time of each entry;
  - they differ on `st_dev` (297 entries), `st_ctime_ns` (296) and `st_mode` (8: the `.exe`
    files and directories);
  - they differ on the size of 3 directories: Python reports the size of the NTFS index
    allocation, 4096, and Node reports 0.
- D5, orchestrator: the setup takes the platform from Node (`process.platform`), and
  `render_check.py` from `os.name`. Node reads the browser in the setup, so its view decides the
  form of the paths.
- D6, orchestrator: on Windows a render runs `node` with the script that the `bin` field of
  `@mermaid-js/mermaid-cli/package.json` names for `mmdc`. It never runs `mmdc.cmd`: `cmd.exe`
  parses the arguments of a `.cmd` file again.
- D7, orchestrator: on Windows a command that times out ends with its process tree, through
  `taskkill.exe /T /F /PID` by its path under `%SystemRoot%\System32`.
- D8, 2026-10-29, operator: the Windows job runs on the branch `task-137-mermaid-windows`,
  pushed to `origin`. The operator's yes covers the pushes of P5 on that branch; the merge into
  `main` waits for the operator's word.
- D9, orchestrator: on Windows `render_check.py` starts `node` by the absolute path of the first
  `node.exe` in an absolute entry of `PATH`. `CreateProcess` searches the directory of the caller
  for a bare name before `PATH`, so a `node.exe` planted in the project would run.
- D11, 2026-10-29, operator, superseded by D16: the browser floor `BROWSER_MIN_BUILD` moves to the stable build of
  Chrome for Testing, in this task (audit C-1). Advisories cover 150.0.7871.24: CVE-2026-17655
  (Critical, ANGLE) is fixed in 151.0.7922.72. Revision 2 set 156.0.8078.73; revision 3 sets
  156.0.8078.80, Stable from 2026-10-29 22:14 UTC. `browsers.json` records 156.0.8078.80 only:
  mac_arm measured on its install and on the official archive, win64 on the archive and by the
  Windows job. The evidence of `references/` is rendered again
  on it. Rejected: a separate task, which renders the evidence twice; keeping 150.
- D12, 2026-10-29, operator: on Windows the install home and the install directories lie in
  `%USERPROFILE%`, and both scripts default to it (audit M-1, review m3). Its default ACL keeps
  other users out. `PUPPETEER_CACHE_DIR` stays free (D1). Rejected: a private ACL written by the
  setup on a new home only; a statement in the documents only.
- D13, 2026-10-29, operator: the Windows job runs in its own workflow, on a change of the skill
  or of that workflow, with a timeout of 30 minutes (review m7). Rejected: each push.
- D14, orchestrator, 2026-10-30: on Windows the tree hash and the stat digest leave out the
  top-level file `debug.log` of the browser directory, and a directory row has mtime 0. CI run
  40953801835 showed that a render with build 156 creates that file beside
  `chrome-headless-shell.exe`, the default of Chromium logging on Windows, and changes the mtime
  of the directory; Chrome never reads the file. A `debug.log` of another kind, or one in a
  subdirectory, stays an entry. Rejected: a browser argument that moves the log, which changes
  `puppeteer.json` on every platform and depends on which process logs.
- D16, 2026-10-30, operator: the browser follows the stable channel of Chrome for Testing, and the
  repository keeps no build number. The setup installs `chrome-headless-shell@stable` with the
  `@puppeteer/browsers` of the first install, which its lockfile pins, from
  `https://storage.googleapis.com/chrome-for-testing-public` into `<home>/chrome`, and removes the
  older builds there. It trusts that browser as downloaded over HTTPS; the stamp records its tree
  hash, its stat digest and the date of the install. `render_check.py` refuses a stamp without
  the date and names a browser installed more than 30 days before the render.
  `MERMAID_RENDER_CHROME` with `MERMAID_RENDER_BROWSER_SHA256` stays for a browser at hand.
  Rejected: a pinned build bumped by hand (D11), which the narrow audit found stale within a day;
  a pin kept with the risk accepted, which each later audit would report again.
- D15, 2026-10-30, operator: the flags, exit codes, inputs, outputs and setup rules of `SKILL.md`
  §4 and §5 move to the new `references/scripts-and-setup.md`. `SKILL.md` keeps the commands,
  the rule of negative fences and the rules an agent acts on. It held 3014 words against the
  budget of 3000 (TC-ME-32) with the Windows rules; it holds 2737 after the move. Rejected: a
  higher budget, paid at each load of the skill.
- D10, orchestrator: on Windows the Node check of the setup resolves the browser path with
  `fs.realpathSync.native`. It returns the long canonical path, as `os.path.realpath` does in
  Python; `fs.realpathSync` keeps a short `8.3` name such as `RUNNER~1`.

## 2. Requirements

<!-- contract:requirements -->

Windows here is the platform that D5 detects. Each requirement leaves the POSIX branch as at the
base.

`setup_renderers.sh`:
- **R1** `browser_candidates` takes `chrome-headless-shell-*/chrome-headless-shell.exe` beside the
  POSIX name. Superseded by D16: `@puppeteer/browsers` reports the path of the binary it installed.
- **R2** On Windows the Node check of `read_browser` calls no `process.getuid` and makes no owner
  or mode check. It resolves the path as D10 states. It keeps:
  - the tree hash;
  - the name check of a link, with letter case ignored; on Windows it applies only when the given
    path ends in a link, since an 8.3 short name is no link;
  - the control-character checks;
  - the refusal of an entry that is not a file, a directory or a link.
- **R3** On Windows `private_problem` reports nothing (D1). The check of the tree hash against
  `browsers.json` or `MERMAID_RENDER_BROWSER_SHA256` stays.
- **R4** On Windows the stat digest that the setup stamps has the rows of D4.
- **R5** `build_of` reads the build from a path with `\` separators.

`render_check.py`:
- **R6** On Windows `install_problem` makes no `S_IWOTH` or `S_IWGRP` test of the browser. It
  compares the resolved path with the path of `puppeteer.json` after `os.path.normcase`. The
  stamp, the `puppeteer.json` match and the stat digest stay.
- **R7** On Windows `browser_stat_digest` builds the rows of D4.
- **R8** On Windows a render runs `node` with the `bin` script of D6. The script resolves inside
  `node_modules/@mermaid-js/mermaid-cli/`; any other path is refused as an install problem.
- **R8a** On Windows `mmdc_command` and `measure_command` start `node` by the path of D9. No such
  `node.exe` is an install problem.
- **R9** On Windows a render that times out ends with its process tree (D7) and raises no
  exception.

Data, CI and documents:
- **R10** `setup_renderers.sh` installs the current stable chrome-headless-shell into
  `<home>/chrome` and keeps no build number (D16); `browsers.json` is removed. The evidence
  fixtures of `references/` are rendered on the build of 2026-10-30, 156.0.8078.80.
- **R11** The workflow `mermaid-render-windows.yml` runs on a change of the skill or of itself,
  with a timeout of 30 minutes (D13). On `windows-latest` with Node.js 22 and Python 3.14, it runs
  the new Windows tests, `setup_renderers.sh`, which installs the stable browser, and
  `render_check.py` on one reference figure.
- **R12** Each Windows branch carries a comment that states what it does not check, as the
  Windows branch of `archive_move.py` does.
- **R13** `SKILL.md` of the skill states that the renderers run on Windows under Git Bash, with
  the guarantee of D1 and D12 and the limits of §5 items 5 and 6. MR-1 closes in its record and
  in `docs/KNOWN_ISSUES.md`; both changelogs carry the release.

Revision 2, on Windows:
- **R14** The default install home and browser cache lie in `%USERPROFILE%`. `setup_renderers.sh`
  and `install_problem` refuse an install home or directory whose resolved path lies outside it,
  `render_check.py` refuses such an `--out`, and the setup refuses a `USERPROFILE` that is not
  absolute (D12).
- **R15** The stat digest reads a reparse point, a junction among them, as a link and does not
  enter it, and a link row has size 0 on both sides. Both checks leave out the top-level file
  `debug.log` while it has one link, and a directory row has mtime 0 (D14). A digest that raises `ValueError` or
  `RecursionError` is refused as a changed browser.
- **R16** `_run` starts no program named by a relative path or a bare name. `node_executable`
  takes an entry with a drive only. `taskkill` comes from the directory of
  `GetSystemDirectoryW` when its result fits the buffer and is absolute. `mmdc_script` refuses a `bin` value with a drive, a root or `..` before
  it resolves a path.
- **R17** `render_check.py` writes its output with `backslashreplace` for a character that the
  code page of the console or the pipe cannot hold, and its `--json` output in ASCII.

Revision 3, on every platform:
- **R18** `install_problem` refuses a stamp without the date of the install, so an install of a
  pinned build made before D16 runs again only after a new setup. `browser_age_note` names a
  browser installed more than 30 days before the render (D16).

## 3. Files

- `S/setup_renderers.sh`, `S/render_check.py`;
- `S/tests/test_renderers_windows.py` (new); `S/tests/test_setup_renderers.py`, whose build above
  the floor is derived from it;
- `.github/workflows/mermaid-render-windows.yml` (new, D13); `docs/ARCHITECTURE.md`;
- the evidence fixtures `paired-examples-geometry.json` and `references-geometry.json`;
- `assets/renderers/browsers.json` and `SKILL.md` of the skill; `references/scripts-and-setup.md`
  (new, D15) and its entry in `references-geometry.json`;
- `docs/issues/mr-1-*.md`, `docs/KNOWN_ISSUES.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`;
- `docs/TASK.md`, `docs/PLAN.md`; the archive of TASK 136.

## 4. Acceptance

<!-- contract:acceptance -->

On POSIX the tests simulate Windows. For the setup, a module that `NODE_OPTIONS` preloads sets
`process.platform` to `win32` and removes `process.getuid`. For `render_check.py`, a test patches
its platform flag.

- TC-W1 — the setup, simulated Windows, a stand-in `chrome-headless-shell.exe` of mode `0o777`
  whose hash the override vouches for → exit 0, and `puppeteer.json` names the `.exe`.
- TC-W2 — TC-W1 with no override → exit 1, and the message says the hash is not recorded.
- TC-W3 — the stat digest that TC-W1 stamps equals `browser_stat_digest` of the same directory
  under the Windows flag.
- TC-W4 — `install_problem` under the Windows flag, the install of TC-W1 → `None`. A byte
  appended to a file of the browser directory → a problem that names the stat digest.
- TC-W5 — `mmdc_command` under the Windows flag, `PATH` of `.` and a directory with a stand-in
  `node.exe` → that `node.exe` and the `bin` script; `measure_command` → the same `node.exe`. A
  `bin` that leads outside the package, or a `PATH` of `.` only → an install problem.
- TC-W6 — `_run` under the Windows flag, a command that times out → `taskkill.exe` by its
  absolute path with `/T /F /PID <pid>`, and no exception.
- TC-W7 — the job of R11 → `setup_renderers.sh` exits 0, and `render_check.py` reports the figure
  `pass` with exit 0.
- TC-W8 — `test_setup_renderers.py` and `test_render_check.py` pass on POSIX; the one change
  derives a build above the floor from it.

Revision 2:
- TC-W9 — the setup with `USERPROFILE` beside the home → exit 1, "lies outside %USERPROFILE%";
  `install_problem` with that profile → the same refusal.
- TC-W10 — `_run` under the Windows flag with `["node", "-v"]` → refused, and no process starts.
- TC-W11 — `mmdc_script` with a `bin` value of a drive, a root, a share or `..` → refused with
  `Path.resolve` patched to fail; a `src/cli.js` linked outside the package → refused.
- TC-W12 — `install_problem` whose digest raises `UnicodeEncodeError` or `RecursionError` →
  "changed since the setup hashed it".
- TC-W1, TC-W5, TC-W6 gain: a link to the browser named in other letter case is accepted; a
  quoted `PATH` entry is read; the timed-out command has exited when `_run` returns.
- Native only, in the Windows job:
  - TC-W13 — an 8.3 short cache path → stamped in its long form;
  - TC-W14 — a stamped path in other letter case → the same browser;
  - TC-W15 — a junction in the browser directory → a link on both sides;
  - TC-W16 — a timed-out command → its grandchild ends.

- TC-W17 — a `debug.log` beside the browser:
  - present at the setup → the hash without it is accepted, and the stamped digest equals the
    render check's;
  - written or appended after the setup → no problem;
  - a directory of that name → "changed since the setup hashed it".

Revision 3:
- TC-W17 gains: a `debug.log` with a second link → hashed at the setup, and refused after it.
- TC-W18 — `rc.main` under the Windows flag with `--out` outside `USERPROFILE` → exit 3,
  "lies outside %USERPROFILE%".
- TC-W19 — `_json_out` under the Windows flag with Cyrillic, an arrow and an emoji → ASCII that
  reads back to the report.
- `test_render_check.py`: a stamp without the date of the install → refused; a browser installed
  31 days before → named, and 30 days before → not named.
- `test_setup_renderers.py`, revision 4:
  - the installed browser → stamped with its hash, its digest and the date;
  - a browser the tool cannot install → the step fails and names `MERMAID_RENDER_CHROME`;
  - a browser of `MERMAID_RENDER_CHROME` → runs with its hash only;
  - an installed browser that links outside `<home>/chrome` → refused;
  - an older build in the cache → removed.

On POSIX, 38 mutations each revert one branch of this task, and a test fails for each: 32 of
the Windows branches and 6 of D16.

Each of TC-W1 to TC-W6 fails on the base.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. A `--with-browser` flag that runs the browser install (the report's proposal 3).
2. Drive-letter paths (`C:\…`) in `MERMAID_RENDER_HOME`, `PUPPETEER_CACHE_DIR` and
   `MERMAID_RENDER_CHROME`. In Git Bash they take the form `/c/…`, as at the base.
3. A run of `setup_renderers.sh` from PowerShell or `cmd.exe`; it needs bash.
4. The other test modules of the skill on Windows; many of them test POSIX modes.
5. On Windows, a file of the browser directory overwritten in place with its size and mtime
   restored is not detected after the setup (D1, D4), nor is the content of `debug.log` (D14). With `PUPPETEER_CACHE_DIR` outside the
   profile, another user who may write there can also swap the directory between the check and
   the launch (D1, audit M-1).
6. On a ReFS volume (Dev Drive), Python 3.12 and later report a 128-bit inode and Node a 64-bit
   one: the digest differs, and every render is refused (review m2, audit I-3).
7. Review N1: the header of `setup_renderers.sh`, which `--help` prints, gained the Windows
   rules; this is the one change of POSIX output.
8. Review N4, audit I-1: `measure_command` keeps a bare `node` as its last resort on Windows;
   R16 refuses it in `_run`, so it never starts.
9. Review N6: on an NTFS directory with per-directory case sensitivity, `os.path.normcase` joins
   two names; the stat digest still detects a swap.
10. Review N9: on the base, TC-W1 to TC-W5 fail in the setup of the test, before their bodies.
11. Review N11: the Windows job runs Python 3.14 only; the floor 3.11 runs the session-state
    jobs there.
12. Audit I-6 to I-8:
    - the tests start `cygpath` and `bash` by name;
    - a `NODE_OPTIONS` that redefines the platform turns the POSIX checks off, and it runs code
      in every node anyway;
    - `pip` and `node-version: "22"` float, as in the other jobs.
