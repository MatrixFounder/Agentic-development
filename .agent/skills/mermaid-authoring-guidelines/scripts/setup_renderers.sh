#!/usr/bin/env bash
# Install the pinned Mermaid renderers for render_check.py (TASK 108, R7.1-R7.3, R7.9).
#
# Installs mermaid-cli with an exact mermaid version per tag into
#   ${MERMAID_RENDER_HOME:-$HOME/.cache/mermaid-authoring-guidelines}/<tag>/
# and writes <tag>/puppeteer.json pointing at the installed chrome-headless-shell.
#
#   v10  mermaid-cli 10.9.1  + mermaid 10.9.8   (floor)
#   v11  mermaid-cli 11.17.0 + mermaid 11.17.2  (the version GitHub runs)
#   v12  mermaid-cli 12.0.0  + mermaid 12.1.0   (forward check; with --forward)
#
# Source of each install: assets/renderers/<tag>/package.json and package-lock.json, installed
# with `npm ci --ignore-scripts`. The only install script in the three lockfiles is puppeteer's
# browser download, which is not wanted. The browser is the current stable chrome-headless-shell
# of Chrome for Testing (TASK 137 D16): the @puppeteer/browsers of the first install, whose
# version its lockfile pins, downloads it from BROWSER_BASE_URL into $RENDER_HOME/chrome, once per
# stable build, and removes the older builds there. This repository keeps no build number, so the
# security fixes of the browser arrive with the next run of this script. The browser so installed
# is trusted as downloaded. MERMAID_RENDER_CHROME names another browser binary instead, in a
# directory that holds that browser only; it runs only when the tree hash of its directory equals
# MERMAID_RENDER_BROWSER_SHA256, which the operator sets after confirming where the browser came
# from (TASK 110 R7.3). The tree hash is the sha256 of one JSON line per file and symbolic link
# under the directory that holds the executable, every symbolic link of the path resolved (see
# read_browser). That directory and the one above it must be private. The resolved path is
# written into puppeteer.json and, with the hash and the date of the install, into each install
# as .browser.sha256; render_check.py runs no install without it (R7.7), and it names a browser
# installed more than 30 days before the render.
#
# Never installs globally and never writes inside a git work tree; a home with a `.` or `..`
# segment is refused, since `mkdir -p` would follow it. The home must be private: it, or its
# nearest existing directory, belongs to this user or root, and no other user may write in it
# (its group only when that group is the user's own, named as the user); a new home is made
# with mode 0700. On Windows Git Bash shows no owner or mode that tells who may write: there the
# home must lie in the user profile, %USERPROFILE%, whose ACL keeps other users out, and its
# default lies in it (TASK 137 D12); a browser that MERMAID_RENDER_CHROME names is not checked
# there (D1). The checks of the browser there leave out the top-level file
# debug.log of one link, which Chrome writes beside its executable on Windows and never reads, and
# the mtime of a directory (D14). Not seen there: a file of the browser overwritten in place with its size
# and mtime restored; on a ReFS volume (Dev Drive) the stat digest never matches, so every render
# is refused. MERMAID_RENDER_CHROME must be an absolute
# path. The npm cache lives in $RENDER_HOME/.npm-cache, so nothing is written to ~/.npm. The
# browser keeps its sandbox; `--no-sandbox` is written into puppeteer.json only when
# MERMAID_RENDER_NO_SANDBOX=1.
# The browser resolves no host name, localhost included, and uses no proxy
# (--host-resolver-rules, --no-proxy-server), and puppeteer talks to it over a pipe ("pipe":
# true), so no DevTools port opens and a render fetches nothing from the network.
# render_check.py runs only a puppeteer.json that is exactly this. Each install directory also
# gets an empty .puppeteerrc.json: puppeteer searches its working directory and each parent for
# a configuration and runs one written in JavaScript, and the search ends at that file, since
# every render, the smoke render included, runs in the install directory. Each install is
# verified with a smoke render under that configuration.
#
# The overrides of the v10 package.json replace the puppeteer 19.11.1 of mermaid-cli 10.9.1 with
# 25.16.0, the version of v11 and v12 (TASK 110 R7.1, TASK 129 R3.2). 19.11.1 pinned extract-zip
# 2.0.1, tar-fs 2.1.1 and ws 8.13.0: 6 high advisories (npm audit, 2026-10-03), and extract-zip
# has no release with a fix. The overrides of each package.json also set dompurify to 3.4.17 and
# katex to 0.18.10 (TASK 129 R3.1). With these versions npm audit reports no advisory for the
# three lockfiles (2026-10-27). The render page takes no script from those two packages. It runs
# the copies that other packages embed, which advisories cover (WI-41):
#   v10  mermaid 10.9.8                                   DOMPurify 3.4.2   KaTeX 0.16.45
#   v11  mermaid 11.17.2, @mermaid-js/layout-elk 0.2.3    DOMPurify 3.4.12  KaTeX 0.16.47
#   v11  @mermaid-js/mermaid-zenuml 0.2.3                 DOMPurify 3.3.1
#   v12  mermaid 12.1.0                                   DOMPurify 3.4.12  KaTeX 0.16.47
#   v12  @mermaid-js/mermaid-zenuml 1.0.1                 DOMPurify 3.3.1
# On 2026-10-05 every reference figure rendered in v10 with the metrics measured under 19.11.1
# (TASK 110). On 2026-10-27 every reference figure rendered in v10, v11 and v12 with the status and
# the metrics it had with puppeteer 25.12.0 (TASK 129 R3.5).
#
# Usage: setup_renderers.sh [--forward] [--dry-run]
#   --dry-run writes nothing: it checks node and the install home (a home inside a git work
#   tree, or one that another user may write in, fails), lists every pinned pair, and prints the
#   steps for the pairs this run installs, with the tree hash of each browser candidate and
#   whether it is accepted.
# Exit:  0 installed (or planned, with --dry-run); 1 a step failed, and the message names it,
#        a browser with no accepted tree hash included; 3 usage error.
#
# Compatible with bash 3.2 (macOS), Linux bash and Git Bash on Windows. On Windows (TASK 137) the
# binary is chrome-headless-shell.exe, the paths of the variables take the form /c/..., and
# no owner or mode is checked: the tree hash and the stat digest guard the browser there.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS="$SKILL_DIR/assets/renderers"
NOTATION="$SKILL_DIR/assets/notation.json"
RENDER_HOME="${MERMAID_RENDER_HOME:-$HOME/.cache/mermaid-authoring-guidelines}"
# The browser: the stable channel of Chrome for Testing, from Google's storage (TASK 137 D16).
BROWSER_CHANNEL='chrome-headless-shell@stable'
BROWSER_BASE_URL='https://storage.googleapis.com/chrome-for-testing-public'
# The browser arguments of every puppeteer.json; render_check.py BROWSER_ARGS holds the same.
NET_BLOCK_ARG='--host-resolver-rules=MAP * ~NOTFOUND'
NO_PROXY_ARG='--no-proxy-server'
BROWSER_STAMP='.browser.sha256'

FORWARD=0
DRY_RUN=0
# 1 when Node reports Windows; set in the step 'check node and npm' (TASK 137 D5).
WINDOWS=0
STEP="arguments"

usage() {
  sed -n '2,/^[^#]/p' "${BASH_SOURCE[0]}" | sed '$d' | sed 's/^# \{0,1\}//'
}

fail() {
  echo "setup_renderers.sh: step '$STEP' failed: $*" >&2
  exit 1
}

say() {
  echo "setup_renderers.sh: $*"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --forward) FORWARD=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "setup_renderers.sh: unknown argument: $1" >&2; usage >&2; exit 3 ;;
  esac
  shift
done

TAGS="v10 v11"
if [ "$FORWARD" -eq 1 ]; then
  TAGS="$TAGS v12"
fi

# ----------------------------------------------------------------------------------- helpers

# Succeed when version $1 >= version $2 (dotted numbers, every one compared; a missing number
# counts as 0). A browser build has four: 150.0.7871.5 is older than 150.0.7871.24.
version_ge() {
  local a="$1" b="$2" i n x y
  local IFS=.
  # shellcheck disable=SC2206
  local A=($a) B=($b)
  n=${#A[@]}
  if [ "${#B[@]}" -gt "$n" ]; then n=${#B[@]}; fi
  for ((i = 0; i < n; i++)); do
    x="${A[$i]:-0}"; y="${B[$i]:-0}"
    x="${x%%[!0-9]*}"; y="${y%%[!0-9]*}"
    x="${x:-0}"; y="${y:-0}"
    if [ "$x" -gt "$y" ]; then return 0; fi
    if [ "$x" -lt "$y" ]; then return 1; fi
  done
  return 0
}

# Succeed when $1, or its nearest existing ancestor, lies inside a git work tree. Fails the
# current step when that ancestor is not a directory: the walk up from it would never end.
inside_git_work_tree() {
  local d="$1"
  while [ ! -e "$d" ]; do d="$(dirname "$d")"; done
  [ -d "$d" ] || fail "$1 runs through $d, which is not a directory"
  d="$(cd "$d" 2>/dev/null && pwd -P)" || fail "cannot enter the directory above $1"
  while :; do
    if [ -e "$d/.git" ]; then return 0; fi
    case "$d" in /|.|"") break ;; esac
    d="$(dirname "$d")"
  done
  if command -v git >/dev/null 2>&1; then
    d="$1"
    while [ ! -e "$d" ]; do d="$(dirname "$d")"; done
    if [ "$(cd "$d" && git rev-parse --is-inside-work-tree 2>/dev/null || true)" = "true" ]; then
      return 0
    fi
  fi
  return 1
}

# Fails the current step when directory $1, or its nearest existing ancestor, is open to another
# user: it must belong to this user or root, and no one else may write in it; its group only
# when that group is the user's own, named as the user (render_check.py private_dir_problem).
# Prints why <dir>, or its nearest existing ancestor, is open to another user, or nothing: it
# must belong to this user or root, and no one else may write in it (render_check.py
# private_dir_problem makes the same check).
private_problem() {
  local d="$1"
  # Windows: Git Bash emulates the owner and the mode, and mounts with `noacl`, so neither shows
  # who may write. Nothing is checked there; the tree hash and the stat digest guard the browser
  # (TASK 137 D1), as render_check.py private_dir_problem checks nothing there.
  if [ "$WINDOWS" -eq 1 ]; then return 0; fi
  while [ ! -e "$d" ]; do d="$(dirname "$d")"; done
  if [ -z "$(find -H "$d" -prune \( -user "$(id -u)" -o -user 0 \) -print)" ]; then
    echo "$d belongs to another user"
  elif [ -n "$(find -H "$d" -prune -perm -0002 -print)" ]; then
    echo "$d is writable by every user"
  elif [ -n "$(find -H "$d" -prune -perm -0020 -print)" ] \
      && ! { [ "$(id -gn)" = "$(id -un)" ] && [ -n "$(find -H "$d" -prune -group "$(id -g)" -print)" ]; }; then
    echo "$d is writable by its group"
  fi
}

# Windows: prints why <dir>, its nearest existing directory resolved, lies outside the user
# profile, or nothing; prints nothing on POSIX (TASK 137 D12, render_check.py profile_problem).
profile_problem() {
  [ "$WINDOWS" -eq 1 ] || return 0
  local d="$1" tail="" base lower_d lower_base
  base="$(cd "$PROFILE" 2>/dev/null && pwd -P)" || { echo "the user profile $PROFILE cannot be entered"; return 0; }
  while [ ! -e "$d" ]; do tail="/${d##*/}$tail"; d="$(dirname "$d")"; done
  d="$(cd "$d" 2>/dev/null && pwd -P)" || { echo "cannot enter the directory above $1"; return 0; }
  lower_d="$(printf '%s' "$d$tail/" | tr '[:upper:]' '[:lower:]')"
  lower_base="$(printf '%s' "$base/" | tr '[:upper:]' '[:lower:]')"
  case "$lower_d" in
    "$lower_base"*) ;;
    *) echo "$1 lies outside %USERPROFILE% ($PROFILE); on Windows the install home lies in the user profile, whose ACL keeps other users out" ;;
  esac
}

check_private() {
  local problem
  problem="$(private_problem "$1")"
  [ -z "$problem" ] || fail "$problem; use a directory of your own"
  problem="$(profile_problem "$1")"
  [ -z "$problem" ] || fail "$problem"
}

# A field of a JSON file, read with node: json_field <file> <dotted.key.path>
# Prints nothing when a key on the path is absent; fails when the file cannot be read, so every
# caller writes `|| fail` and the failing step is named.
json_field() {
  node -e 'let v;
           try { v = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")); }
           catch (e) { process.stderr.write(String(e.message).split("\n")[0] + "\n"); process.exit(1); }
           for (const k of process.argv[2].split(".")) {
             v = (v !== null && typeof v === "object" && k in v) ? v[k] : undefined;
             if (v === undefined) break;
           }
           process.stdout.write(v === undefined || v === null ? "" : String(v));' "$1" "$2"
}

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    sha256sum "$1" | cut -d' ' -f1
  fi
}

# Prints the browser executable for the installs: the binary MERMAID_RENDER_CHROME names, or the
# stable chrome-headless-shell, which the @puppeteer/browsers of the install <dir> installs into
# BROWSER_HOME. A build already there is reported without a download. Fails the current step
# when the tool cannot install it, offline among others: fetch_browser <dir>
fetch_browser() {
  local tool="$1/node_modules/.bin/browsers" out log
  if [ -n "${MERMAID_RENDER_CHROME:-}" ]; then
    echo "$MERMAID_RENDER_CHROME"
    return 0
  fi
  [ -x "$tool" ] || fail "no @puppeteer/browsers in $1/node_modules/.bin"
  ( umask 077 && mkdir -p "$BROWSER_HOME" ) || fail "cannot create $BROWSER_HOME"
  check_private "$BROWSER_HOME"
  log="$(mktemp "${TMPDIR:-/tmp}/mermaid-browser.XXXXXX")"
  if ! out="$("$tool" install "$BROWSER_CHANNEL" --path "$BROWSER_HOME" \
                --base-url "$BROWSER_BASE_URL" --format '{{buildId}}	{{path}}' 2>"$log")"; then
    out="$(head -c 600 "$log" 2>/dev/null || true)"
    rm -f "$log"
    fail "cannot install $BROWSER_CHANNEL into $BROWSER_HOME: $out; without the network the operator may name a browser at hand with MERMAID_RENDER_CHROME and its tree hash with MERMAID_RENDER_BROWSER_SHA256"
  fi
  rm -f "$log"
  out="$(printf '%s\n' "$out" | tail -n 1)"
  case "$out" in
    *"	"*) echo "${out#*	}" ;;
    *) fail "cannot read the browser that @puppeteer/browsers installed: $out" ;;
  esac
}

# The build of an installed chrome-headless-shell, read from its directory name, or "unknown".
build_of() {
  local d="$1"
  # Node gives a Windows path with `\` separators.
  if [ "$WINDOWS" -eq 1 ]; then d="${d//\\//}"; fi
  d="$(dirname "$(dirname "$d")")"; d="${d##*/}"
  case "$d" in
    *-[0-9]*.[0-9]*) echo "${d#*-}" ;;
    *) echo "unknown" ;;
  esac
}

# Reads the browser named by an executable path, once per path (TASK 110 R7.3; review round 1
# M1, L1, L2): sets BROWSER_EXE to the path with every symbolic link resolved and BROWSER_HASH to
# the tree hash of the directory that holds it, or BROWSER_PROBLEM to why it cannot be read. The
# tree hash is the sha256 of one line per entry under that directory, sorted bytewise by path:
# the JSON array ["file", "./<path>", "<sha256 of the content>"] or ["link", "./<path>",
# "<target>"], each followed by a newline. A path or a name with a control character, a file
# that cannot be read, an entry that is neither a file, a directory nor a symbolic link, and an
# entry another user may write in are refused, so no byte of the directory is left out of the hash
# or open to a change after it: an entry must belong to this user or root, and only the user's own
# group may write in it. A link whose file name differs from its target's is refused: it may name
# a launcher, not the browser (TASK 110 review rounds 2 and 3). BROWSER_STAT is the sha256 of one
# JSON line per entry, the directory itself included: [path, kind, dev, inode, mode, size, mtime
# in ns, ctime in ns]. It is stamped, and every render compares it, so a file changed or swapped
# after the hash shows (review round 3, N1). On Windows no entry is checked for its owner or
# mode, a stat line is [path, kind, inode, size, mtime in ns], with size 0 for a directory and a
# link and mtime 0 for a directory, and the top-level file debug.log is left out of both
# (TASK 137 D1, D4, D14).
BROWSER_CACHE_LINES=""
read_browser() {
  local given="$1" line out status rest own_gid=-1
  BROWSER_EXE="" BROWSER_HASH="" BROWSER_STAT="" BROWSER_PROBLEM=""
  # Group write is allowed only to the user's own group, as private_problem and render_check.py
  # _own_group allow it (TASK 110 review round 3, RG3-2).
  if [ "$(id -gn)" = "$(id -un)" ]; then own_gid="$(id -g)"; fi
  while IFS= read -r line; do
    if [ "${line%%	*}" = "$given" ]; then
      out="${line#*	}"
      break
    fi
  done <<EOF_CACHE
$BROWSER_CACHE_LINES
EOF_CACHE
  if [ -z "${out:-}" ]; then
    out="$(node -e 'const fs = require("fs"), path = require("path"), crypto = require("crypto");
      const bad = (s) => /[\u0000-\u001f\u007f]/.test(s);
      // Windows (TASK 137): the long canonical path, which Python os.path.realpath also gives
      // (D10); names compared without letter case, as NTFS compares them; no owner or mode
      // check, since Node reports no owner there and mode 0o666 for each writable file, so the
      // tree hash and the stat digest are the checks (D1); stat rows of the fields that Node
      // and Python read alike there, with size 0 for a directory and a link (D4); no mtime of a
      // directory, and no top-level file debug.log of one link, which Chrome writes there
      // beside its executable, the default of its logging on Windows, and never reads (D14).
      const win = process.platform === "win32";
      const fold = (s) => win ? s.toLowerCase() : s;
      try {
        const given = process.argv[1];
        if (bad(given)) throw new Error("the browser path holds a control character");
        const exe = (win ? fs.realpathSync.native : fs.realpathSync)(given);
        if (bad(exe)) throw new Error("the resolved browser path holds a control character");
        // On Windows an 8.3 short name differs from the long one with no link between them: there
        // the names count only when the given path ends in a link (TASK 137, TC-W13).
        const linked = fs.lstatSync(given).isSymbolicLink();
        if ((!win || linked) && fold(path.basename(exe)) !== fold(path.basename(given)))
          throw new Error(given + " leads to " + exe + " under another name, which may be a launcher; name the browser binary itself");
        const ownGid = Number(process.argv[2]), uid = win ? -1 : process.getuid();
        const open = (st, full) => {
          if (win) return;
          if (st.uid !== uid && st.uid !== 0) throw new Error(full + " belongs to another user");
          if (st.mode & 0o002) throw new Error(full + " is writable by every user");
          if ((st.mode & 0o020) && st.gid !== ownGid) throw new Error(full + " is writable by its group");
        };
        const rows = [], stats = [];
        const stamp = (full, rel, kind) => {
          const st = fs.lstatSync(full, {bigint: true});
          stats.push(win ? [rel, kind, String(st.ino), kind === "file" ? String(st.size) : "0",
                            kind === "dir" ? "0" : String(st.mtimeNs)]
                         : [rel, kind, String(st.dev), String(st.ino), String(st.mode),
                            String(st.size), String(st.mtimeNs), String(st.ctimeNs)]);
        };
        const walk = (dir, rel) => {
          for (const name of fs.readdirSync(dir)) {
            if (bad(name)) throw new Error("a name under " + dir + " holds a control character");
            const full = path.join(dir, name), r = rel ? rel + "/" + name : name;
            const st = fs.lstatSync(full);
            if (win && r === "debug.log" && st.isFile() && st.nlink === 1) continue;
            if (!st.isSymbolicLink()) open(st, full);
            stamp(full, "./" + r, st.isSymbolicLink() ? "link" : st.isDirectory() ? "dir" : "file");
            if (st.isSymbolicLink()) rows.push(["link", "./" + r, fs.readlinkSync(full)]);
            else if (st.isDirectory()) walk(full, r);
            else if (st.isFile()) rows.push(["file", "./" + r,
              crypto.createHash("sha256").update(fs.readFileSync(full)).digest("hex")]);
            else throw new Error(full + " is neither a file, a directory nor a symbolic link");
          }
        };
        const root = path.dirname(exe);
        open(fs.lstatSync(root), root);
        stamp(root, ".", "dir");
        walk(root, "");
        rows.sort((a, b) => Buffer.compare(Buffer.from(a[1]), Buffer.from(b[1])));
        const h = crypto.createHash("sha256");
        for (const row of rows) h.update(JSON.stringify(row) + "\n");
        // The stat digest: render_check.py browser_stat_digest compares it at every render.
        stats.sort((a, b) => Buffer.compare(Buffer.from(a[0]), Buffer.from(b[0])));
        const sd = crypto.createHash("sha256");
        for (const row of stats) sd.update(JSON.stringify(row) + "\n");
        process.stdout.write("ok\t" + exe + "\t" + h.digest("hex") + "\t" + sd.digest("hex"));
      } catch (e) {
        process.stdout.write("no\t" + String(e.message).replace(/[\u0000-\u001f\u007f]/g, " "));
      }' "$given" "$own_gid")" || out="no	node could not read the browser"
    case "$given" in
      *[[:cntrl:]]*) ;;
      *) BROWSER_CACHE_LINES="$BROWSER_CACHE_LINES
$given	$out" ;;
    esac
  fi
  status="${out%%	*}"
  rest="${out#*	}"
  if [ "$status" = "ok" ]; then
    BROWSER_EXE="${rest%%	*}"
    rest="${rest#*	}"
    BROWSER_HASH="${rest%%	*}"
    BROWSER_STAT="${rest#*	}"
  else
    BROWSER_PROBLEM="$rest"
  fi
}

# Succeeds when the browser named by <executable> may run: its directory and the one above are
# private, and either it lies in BROWSER_HOME, where fetch_browser installed it, or its tree hash
# equals MERMAID_RENDER_BROWSER_SHA256, which only the operator sets, for the binary that
# MERMAID_RENDER_CHROME names. Sets BROWSER_EXE, BROWSER_HASH and, on a refusal, BROWSER_PROBLEM:
# browser_accepted <executable>
browser_accepted() {
  local d problem
  read_browser "$1"
  [ -z "$BROWSER_PROBLEM" ] || return 1
  for d in "$(dirname "$BROWSER_EXE")" "$(dirname "$(dirname "$BROWSER_EXE")")"; do
    problem="$(private_problem "$d")"
    if [ -n "$problem" ]; then
      BROWSER_PROBLEM="$problem"
      return 1
    fi
  done
  if [ -n "${MERMAID_RENDER_CHROME:-}" ]; then
    if [ -n "${MERMAID_RENDER_BROWSER_SHA256:-}" ] && [ "$BROWSER_HASH" = "$MERMAID_RENDER_BROWSER_SHA256" ]; then
      return 0
    fi
    BROWSER_PROBLEM="not vouched"
    return 1
  fi
  # The downloaded browser: its resolved path lies in BROWSER_HOME, so no link leads elsewhere.
  if node -e 'const fs = require("fs"), path = require("path");
              const real = process.platform === "win32" ? fs.realpathSync.native : fs.realpathSync;
              const rel = path.relative(real(process.argv[1]), process.argv[2]);
              process.exit(rel && !rel.startsWith("..") && !path.isAbsolute(rel) ? 0 : 1);' \
       "$BROWSER_HOME" "$BROWSER_EXE"; then
    return 0
  fi
  BROWSER_PROBLEM="$BROWSER_EXE lies outside $BROWSER_HOME, where the setup installs the browser"
  return 1
}

# Write puppeteer.json for an install: write_puppeteer_config <file> <executable> <headless>
# The sandbox flag is added only when the operator sets MERMAID_RENDER_NO_SANDBOX=1.
write_puppeteer_config() {
  local file="$1" exe="$2" headless="$3" no_sandbox=""
  if [ "${MERMAID_RENDER_NO_SANDBOX:-}" = "1" ]; then
    no_sandbox="--no-sandbox"
  fi
  node -e 'const fs = require("fs");
           const [file, exe, headless, netBlock, noProxy, noSandbox] = process.argv.slice(1);
           const args = [netBlock, noProxy];
           if (noSandbox) args.push(noSandbox);
           const cfg = {executablePath: exe, headless: headless === "true" ? true : headless,
                        args: args, pipe: true};
           fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n");' \
    "$file" "$exe" "$headless" "$NET_BLOCK_ARG" "$NO_PROXY_ARG" "$no_sandbox"
}

# Smoke render with an install's mmdc and a puppeteer config; succeeds when an SVG is written.
# mmdc runs in the install directory, as every render of render_check.py does, never in the
# caller's directory, whose puppeteer configuration it would run.
smoke_render() {
  local dest="$1" pp="$2" tmp rc
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/mermaid-setup.XXXXXX")"
  tmp="$(cd "$tmp" && pwd -P)"
  printf 'flowchart TB\n  A["smoke"] --> B["test"]\n' > "$tmp/smoke.mmd"
  printf '{"securityLevel": "strict"}\n' > "$tmp/config.json"
  rc=0
  ( cd "$dest" && "$dest/node_modules/.bin/mmdc" -q -p "$pp" -c "$tmp/config.json" \
      -i "$tmp/smoke.mmd" -o "$tmp/smoke.svg" ) >"$tmp/log" 2>&1 || rc=$?
  if [ "$rc" -eq 0 ] && grep -q "<svg" "$tmp/smoke.svg" 2>/dev/null; then
    rm -rf "$tmp"
    return 0
  fi
  SMOKE_LOG="$(head -c 600 "$tmp/log" 2>/dev/null || true)"
  rm -rf "$tmp"
  return 1
}

# ----------------------------------------------------------------------------------- checks

STEP="check node and npm"
command -v node >/dev/null 2>&1 || fail "node is not on PATH"
command -v npm >/dev/null 2>&1 || fail "npm is not on PATH"
NODE_VERSION="$(node -p 'process.versions.node')"
# Node reads the browser, so its view of the platform decides the form of the paths and the
# checks that apply (TASK 137 D5).
if [ "$(node -p 'process.platform')" = "win32" ]; then WINDOWS=1; fi
# Windows: the profile holds the defaults, as Node os.homedir() and Python expanduser read it;
# Git Bash may set HOME elsewhere (TASK 137 D12).
PROFILE=""
if [ "$WINDOWS" -eq 1 ]; then
  [ -n "${USERPROFILE:-}" ] || fail "USERPROFILE is not set; on Windows the install home lies in the user profile"
  PROFILE="$USERPROFILE"
  if command -v cygpath >/dev/null 2>&1; then PROFILE="$(cygpath -u "$USERPROFILE")"; fi
  case "$PROFILE" in
    /*) ;;
    *) fail "USERPROFILE is not an absolute path: $USERPROFILE" ;;
  esac
  RENDER_HOME="${MERMAID_RENDER_HOME:-$PROFILE/.cache/mermaid-authoring-guidelines}"
fi

STEP="check the install home"
case "$RENDER_HOME" in
  /*) ;;
  *) fail "MERMAID_RENDER_HOME must be an absolute path: $RENDER_HOME" ;;
esac
case "/$RENDER_HOME/" in
  */./*|*/../*) fail "MERMAID_RENDER_HOME must not hold a . or .. segment: $RENDER_HOME" ;;
esac
if inside_git_work_tree "$RENDER_HOME"; then
  fail "$RENDER_HOME lies inside a git work tree; set MERMAID_RENDER_HOME to a directory outside any repository"
fi
check_private "$RENDER_HOME"
# The stable browser that fetch_browser installs (TASK 137 D16).
BROWSER_HOME="$RENDER_HOME/chrome"

STEP="check the browser paths"
# Every render runs in an install directory; a relative path would be read from there.
case "${MERMAID_RENDER_CHROME:-/}" in
  /*) ;;
  *) fail "MERMAID_RENDER_CHROME must be an absolute path: $MERMAID_RENDER_CHROME" ;;
esac

STEP="check the committed manifests"
for tag in $TAGS; do
  [ -f "$ASSETS/$tag/package.json" ] || fail "missing $ASSETS/$tag/package.json"
  [ -f "$ASSETS/$tag/package-lock.json" ] || fail "missing $ASSETS/$tag/package-lock.json"
done
[ -f "$NOTATION" ] || fail "missing $NOTATION"

for tag in $TAGS; do
  STEP="node version for $tag"
  floor="$(json_field "$ASSETS/$tag/package.json" engines.node)" || fail "cannot read $ASSETS/$tag/package.json"
  floor="${floor#>=}"
  if [ -n "$floor" ] && ! version_ge "$NODE_VERSION" "$floor"; then
    fail "node $NODE_VERSION is older than $floor, which the $tag install requires (TASK 108 section 3)"
  fi
done

# ----------------------------------------------------------------------------------- plan

if [ "$DRY_RUN" -eq 1 ]; then
  say "dry run; nothing is written"
  say "install home: $RENDER_HOME"
  say "node $NODE_VERSION, npm $(npm --version)"
  # Every pinned pair is listed; the forward pair is installed only with --forward.
  for tag in v10 v11 v12; do
    STEP="plan $tag"
    pin="$(json_field "$NOTATION" "renderers.installs.$tag.mermaid")" || fail "cannot read $NOTATION"
    cli="$(json_field "$NOTATION" "renderers.installs.$tag.cli")" || fail "cannot read $NOTATION"
    case " $TAGS " in
      *" $tag "*) say "$tag: mermaid-cli $cli + mermaid $pin" ;;
      *) say "$tag: mermaid-cli $cli + mermaid $pin (installed with --forward; skipped in this run)"
         continue ;;
    esac
    say "  copy $ASSETS/$tag/{package.json,package-lock.json} -> $RENDER_HOME/$tag/"
    say "  (cd $RENDER_HOME/$tag && PUPPETEER_SKIP_DOWNLOAD=1 npm_config_cache=$RENDER_HOME/.npm-cache npm ci --ignore-scripts)"
    if [ -n "${MERMAID_RENDER_CHROME:-}" ]; then
      if browser_accepted "$MERMAID_RENDER_CHROME"; then
        say "  browser: $BROWSER_EXE (build $(build_of "$BROWSER_EXE")), tree sha256 $BROWSER_HASH: accepted"
      elif [ -n "$BROWSER_HASH" ] && [ "$BROWSER_PROBLEM" = "not vouched" ]; then
        say "  browser: $BROWSER_EXE (build $(build_of "$BROWSER_EXE")), tree sha256 $BROWSER_HASH: refused, MERMAID_RENDER_BROWSER_SHA256 does not name it"
      else
        say "  browser: $MERMAID_RENDER_CHROME: refused: $BROWSER_PROBLEM"
      fi
    else
      say "  browser: $BROWSER_CHANNEL from $BROWSER_BASE_URL into $BROWSER_HOME, with the @puppeteer/browsers of the install"
    fi
    say "  write $RENDER_HOME/$tag/puppeteer.json, the empty .puppeteerrc.json and $BROWSER_STAMP, and verify them with a smoke render run in $RENDER_HOME/$tag"
  done
  if [ "${MERMAID_RENDER_NO_SANDBOX:-}" = "1" ]; then
    say "MERMAID_RENDER_NO_SANDBOX=1: the browser would run without its sandbox"
  fi
  exit 0
fi

# ----------------------------------------------------------------------------------- install

FETCHED=""
TODAY="$(date -u +%Y-%m-%d)"
STEP="create the install home"
( umask 077 && mkdir -p "$RENDER_HOME" ) || fail "cannot create $RENDER_HOME"
check_private "$RENDER_HOME"

for tag in $TAGS; do
  dest="$RENDER_HOME/$tag"
  STEP="read the $tag pins"
  pin="$(json_field "$NOTATION" "renderers.installs.$tag.mermaid")" || fail "cannot read $NOTATION"
  lock_sha="$(sha256_of "$ASSETS/$tag/package-lock.json")"

  STEP="copy the $tag manifests"
  ( umask 077 && mkdir -p "$dest" ) || fail "cannot create $dest"
  check_private "$dest"
  installed=""
  if [ -f "$dest/.lock.sha256" ] && [ -f "$dest/node_modules/mermaid/package.json" ] \
      && [ -x "$dest/node_modules/.bin/mmdc" ]; then
    installed="$(json_field "$dest/node_modules/mermaid/package.json" version)" \
      || fail "cannot read $dest/node_modules/mermaid/package.json"
  fi
  if [ -n "$installed" ] && [ "$installed" = "$pin" ] \
      && [ "$(cat "$dest/.lock.sha256")" = "$lock_sha" ]; then
    say "$tag: mermaid $installed already installed from the committed lockfile"
  else
    cp "$ASSETS/$tag/package.json" "$ASSETS/$tag/package-lock.json" "$dest/"
    rm -f "$dest/.lock.sha256"

    STEP="npm ci for $tag"
    say "$tag: npm ci --ignore-scripts in $dest"
    # The npm cache stays in the install home (TASK 108 R7.2), not in ~/.npm.
    ( cd "$dest" && PUPPETEER_SKIP_DOWNLOAD=1 PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1 \
        npm_config_cache="$RENDER_HOME/.npm-cache" \
        npm ci --ignore-scripts --no-audit --no-fund --loglevel=error ) \
      || fail "npm ci exited non-zero in $dest"

    STEP="verify the $tag version"
    installed="$(json_field "$dest/node_modules/mermaid/package.json" version)" \
      || fail "cannot read $dest/node_modules/mermaid/package.json"
    [ "$installed" = "$pin" ] || fail "installed mermaid $installed, pinned $pin"
    [ -x "$dest/node_modules/.bin/mmdc" ] || fail "no mmdc in $dest/node_modules/.bin"
    echo "$lock_sha" > "$dest/.lock.sha256"
  fi

  STEP="browser for $tag"
  pptr="$(json_field "$dest/node_modules/puppeteer/package.json" version)" \
    || fail "cannot read $dest/node_modules/puppeteer/package.json"
  pptr_major="${pptr%%.*}"
  if [ "$pptr_major" -ge 22 ] 2>/dev/null; then
    headless="shell"
  else
    headless="new"
  fi
  # Puppeteer's search for a configuration ends at this file (render_check.py PUPPETEER_RC).
  printf '{}\n' > "$dest/.puppeteerrc.json" || fail "cannot write $dest/.puppeteerrc.json"
  if [ -z "$FETCHED" ]; then
    FETCHED="$(fetch_browser "$dest")"
  fi
  if ! browser_accepted "$FETCHED"; then
    rm -f "$dest/puppeteer.json" "$dest/$BROWSER_STAMP"
    if [ "$BROWSER_PROBLEM" = "not vouched" ]; then
      fail "the browser $BROWSER_EXE (tree sha256 $BROWSER_HASH) is not the one MERMAID_RENDER_BROWSER_SHA256 names; the operator may confirm where this browser came from, then set MERMAID_RENDER_BROWSER_SHA256 to its tree hash and run this script again; an agent stops here and reports this refusal"
    fi
    fail "the browser $FETCHED is refused: $BROWSER_PROBLEM; an agent stops here and reports it"
  fi
  # The resolved path runs and is stamped: the browser that was hashed is the one that runs.
  write_puppeteer_config "$dest/puppeteer.json" "$BROWSER_EXE" "$headless"
  SMOKE_LOG=""
  if ! smoke_render "$dest" "$dest/puppeteer.json"; then
    rm -f "$dest/puppeteer.json" "$dest/$BROWSER_STAMP"
    fail "the browser $BROWSER_EXE does not render with $tag under the sandbox and the network block; last log: $SMOKE_LOG"
  fi
  printf '%s  %s\nstat %s\ninstalled %s\n' "$BROWSER_HASH" "$BROWSER_EXE" "$BROWSER_STAT" "$TODAY" \
    > "$dest/$BROWSER_STAMP" || fail "cannot write $dest/$BROWSER_STAMP"
  say "$tag: mermaid $installed, puppeteer $pptr, browser $BROWSER_EXE (build $(build_of "$BROWSER_EXE"), headless: $headless, tree sha256 $BROWSER_HASH)"
done

# The older stable builds leave BROWSER_HOME once each install runs the new one.
if [ -z "${MERMAID_RENDER_CHROME:-}" ] && [ -n "$FETCHED" ]; then
  STEP="remove the older browsers"
  keep="$(build_of "$FETCHED")"
  if [ "$keep" != "unknown" ]; then
    for d in "$BROWSER_HOME"/chrome-headless-shell/*/; do
      [ -d "$d" ] || continue
      case "${d%/}" in
        *-"$keep") ;;
        *) rm -rf "${d%/}" || say "could not remove ${d%/}" ;;
      esac
    done
  fi
fi

if [ "${MERMAID_RENDER_NO_SANDBOX:-}" = "1" ]; then
  say "warning: MERMAID_RENDER_NO_SANDBOX=1, the browser runs without its sandbox"
fi
say "installed: $TAGS under $RENDER_HOME"
exit 0
