#!/usr/bin/env bash
# Install the pinned Mermaid renderers for render_check.py (TASK 108, R7.1-R7.3, R7.9).
#
# Installs mermaid-cli with an exact mermaid version per tag into
#   ${MERMAID_RENDER_HOME:-$HOME/.cache/mermaid-authoring-guidelines}/<tag>/
# and writes <tag>/puppeteer.json pointing at a cached chrome-headless-shell.
#
#   v10  mermaid-cli 10.9.1  + mermaid 10.9.8   (floor)
#   v11  mermaid-cli 11.17.0 + mermaid 11.17.2  (the version GitHub runs)
#   v12  mermaid-cli 12.0.0  + mermaid 12.1.0   (forward check; with --forward)
#
# Source of each install: assets/renderers/<tag>/package.json and package-lock.json, installed
# with `npm ci --ignore-scripts`. The only install script in the three lockfiles is puppeteer's
# browser download, which is not wanted: the script reuses a cached chrome-headless-shell from
# ${PUPPETEER_CACHE_DIR:-$HOME/.cache/puppeteer}/chrome-headless-shell/ of build
# BROWSER_MIN_BUILD or newer (the build the committed render evidence was measured with), or the
# binary named by MERMAID_RENDER_CHROME. It never downloads a browser. A browser is used only when
# the tree hash of its directory is recorded in assets/renderers/browsers.json, or equals
# MERMAID_RENDER_BROWSER_SHA256, which the operator sets after confirming where the browser came
# from (TASK 110 R7.3). The tree hash is the sha256 of one JSON line per file and symbolic link
# under the directory that holds the executable, every symbolic link of the path resolved (see
# read_browser). That directory and the one above it must be private. MERMAID_RENDER_CHROME names
# the browser binary itself, in a directory that holds that browser only. The resolved path is written
# into puppeteer.json and, with the accepted hash, into each install as .browser.sha256;
# render_check.py runs no install without it (R7.7).
#
# Never installs globally and never writes inside a git work tree; a home with a `.` or `..`
# segment is refused, since `mkdir -p` would follow it. The home must be private: it, or its
# nearest existing directory, belongs to this user or root, and no other user may write in it
# (its group only when that group is the user's own, named as the user); a new home is made
# with mode 0700. PUPPETEER_CACHE_DIR and MERMAID_RENDER_CHROME must be absolute paths. The npm
# cache lives in $RENDER_HOME/.npm-cache, so nothing is written to ~/.npm. The browser keeps its
# sandbox; `--no-sandbox` is written into puppeteer.json only when MERMAID_RENDER_NO_SANDBOX=1.
# The browser resolves no host name, localhost included, and uses no proxy
# (--host-resolver-rules, --no-proxy-server), and puppeteer talks to it over a pipe ("pipe":
# true), so no DevTools port opens and a render fetches nothing from the network.
# render_check.py runs only a puppeteer.json that is exactly this. Each install directory also
# gets an empty .puppeteerrc.json: puppeteer searches its working directory and each parent for
# a configuration and runs one written in JavaScript, and the search ends at that file, since
# every render, the smoke render included, runs in the install directory. Each install is
# verified with a smoke render under that configuration.
#
# The v10 lockfile overrides the puppeteer 19.11.1 of mermaid-cli 10.9.1 with 25.12.0, the
# version of v11 (TASK 110 R7.1). 19.11.1 pinned extract-zip 2.0.1, tar-fs 2.1.1 and ws 8.13.0:
# 6 high advisories (npm audit, 2026-10-03), and extract-zip has no release with a fix. With the
# override, npm audit reports none for the three lockfiles (2026-10-05), and every reference
# figure rendered in 10.9.8 with the metrics measured under 19.11.1.
#
# Usage: setup_renderers.sh [--forward] [--dry-run]
#   --dry-run writes nothing: it checks node and the install home (a home inside a git work
#   tree, or one that another user may write in, fails), lists every pinned pair, and prints the
#   steps for the pairs this run installs, with the tree hash of each browser candidate and
#   whether it is accepted.
# Exit:  0 installed (or planned, with --dry-run); 1 a step failed, and the message names it,
#        a browser with no accepted tree hash included; 3 usage error.
#
# Compatible with bash 3.2 (macOS) and Linux bash.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS="$SKILL_DIR/assets/renderers"
NOTATION="$SKILL_DIR/assets/notation.json"
RENDER_HOME="${MERMAID_RENDER_HOME:-$HOME/.cache/mermaid-authoring-guidelines}"
BROWSER_CACHE="${PUPPETEER_CACHE_DIR:-$HOME/.cache/puppeteer}"
# The browser arguments of every puppeteer.json; render_check.py BROWSER_ARGS holds the same.
NET_BLOCK_ARG='--host-resolver-rules=MAP * ~NOTFOUND'
NO_PROXY_ARG='--no-proxy-server'
BROWSER_MIN_BUILD='150.0.7871.24'
BROWSER_TABLE="$ASSETS/browsers.json"
BROWSER_STAMP='.browser.sha256'

FORWARD=0
DRY_RUN=0
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

check_private() {
  local problem
  problem="$(private_problem "$1")"
  [ -z "$problem" ] || fail "$problem; use a directory of your own"
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

# Candidate chrome-headless-shell binaries, the preferred version first, then newest first. A
# cached build older than BROWSER_MIN_BUILD is never offered: untrusted figures render in it.
browser_candidates() {
  local preferred="$1" base="$BROWSER_CACHE/chrome-headless-shell" d ver exe
  if [ -n "${MERMAID_RENDER_CHROME:-}" ]; then
    echo "$MERMAID_RENDER_CHROME"
    return 0
  fi
  [ -d "$base" ] || return 0
  {
    for d in "$base"/*/; do
      [ -d "$d" ] || continue
      ver="${d%/}"; ver="${ver##*/}"; ver="${ver#*-}"
      version_ge "$ver" "$BROWSER_MIN_BUILD" || continue
      for exe in "$d"chrome-headless-shell-*/chrome-headless-shell; do
        if [ -x "$exe" ]; then
          if [ -n "$preferred" ] && [ "$ver" = "$preferred" ]; then
            echo "999999.0.0.0 $exe"
          else
            echo "$ver $exe"
          fi
        fi
      done
    done
  } | sort -t. -k1,1nr -k2,2nr -k3,3nr -k4,4nr | cut -d' ' -f2-
}

# The build of a cached chrome-headless-shell, read from its directory name, or "unknown".
build_of() {
  local d
  d="$(dirname "$(dirname "$1")")"; d="${d##*/}"
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
# after the hash shows (review round 3, N1).
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
      try {
        const given = process.argv[1];
        if (bad(given)) throw new Error("the browser path holds a control character");
        const exe = fs.realpathSync(given);
        if (bad(exe)) throw new Error("the resolved browser path holds a control character");
        if (path.basename(exe) !== path.basename(given))
          throw new Error(given + " leads to " + exe + " under another name, which may be a launcher; name the browser binary itself");
        const ownGid = Number(process.argv[2]), uid = process.getuid();
        const open = (st, full) => {
          if (st.uid !== uid && st.uid !== 0) throw new Error(full + " belongs to another user");
          if (st.mode & 0o002) throw new Error(full + " is writable by every user");
          if ((st.mode & 0o020) && st.gid !== ownGid) throw new Error(full + " is writable by its group");
        };
        const rows = [], stats = [];
        const stamp = (full, rel, kind) => {
          const st = fs.lstatSync(full, {bigint: true});
          stats.push([rel, kind, String(st.dev), String(st.ino), String(st.mode), String(st.size),
                      String(st.mtimeNs), String(st.ctimeNs)]);
        };
        const walk = (dir, rel) => {
          for (const name of fs.readdirSync(dir)) {
            if (bad(name)) throw new Error("a name under " + dir + " holds a control character");
            const full = path.join(dir, name), r = rel ? rel + "/" + name : name;
            const st = fs.lstatSync(full);
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
# private, and its tree hash is recorded in BROWSER_TABLE or equals MERMAID_RENDER_BROWSER_SHA256,
# which only the operator sets. Sets BROWSER_EXE, BROWSER_HASH and, on a refusal,
# BROWSER_PROBLEM: browser_accepted <executable>
browser_accepted() {
  local recorded d problem
  read_browser "$1"
  [ -z "$BROWSER_PROBLEM" ] || return 1
  for d in "$(dirname "$BROWSER_EXE")" "$(dirname "$(dirname "$BROWSER_EXE")")"; do
    problem="$(private_problem "$d")"
    if [ -n "$problem" ]; then
      BROWSER_PROBLEM="$problem"
      return 1
    fi
  done
  if [ -n "${MERMAID_RENDER_BROWSER_SHA256:-}" ] && [ "$BROWSER_HASH" = "$MERMAID_RENDER_BROWSER_SHA256" ]; then
    return 0
  fi
  recorded="$(node -e 'const t = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
                       for (const b of t.browsers || []) process.stdout.write(String(b.tree_sha256) + "\n");' \
                "$BROWSER_TABLE")" || { BROWSER_PROBLEM="cannot read $BROWSER_TABLE"; return 1; }
  case "
$recorded
" in
    *"
$BROWSER_HASH
"*) return 0 ;;
  esac
  BROWSER_PROBLEM="not recorded"
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

STEP="check the browser paths"
# Every render runs in an install directory; a relative path would be read from there.
case "$BROWSER_CACHE" in
  /*) ;;
  *) fail "PUPPETEER_CACHE_DIR must be an absolute path: $BROWSER_CACHE" ;;
esac
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
# The browser download tool named in a failure hint: the exact version the v11 lockfile pins.
BROWSERS_TOOL="$(json_field "$ASSETS/v11/package-lock.json" "packages.node_modules/@puppeteer/browsers.version")" \
  || fail "cannot read $ASSETS/v11/package-lock.json"

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
    found="$(browser_candidates "")"
    if [ -n "$found" ]; then
      old_ifs="$IFS"
      IFS='
'
      set -f  # a path is one candidate, never a glob
      for exe in $found; do
        IFS="$old_ifs"
        if browser_accepted "$exe"; then
          say "  browser: $BROWSER_EXE (build $(build_of "$BROWSER_EXE")), tree sha256 $BROWSER_HASH: accepted"
        elif [ -n "$BROWSER_HASH" ] && [ "$BROWSER_PROBLEM" = "not recorded" ]; then
          say "  browser: $BROWSER_EXE (build $(build_of "$BROWSER_EXE")), tree sha256 $BROWSER_HASH: refused, not recorded"
        else
          say "  browser: $exe (build $(build_of "$exe")): refused: $BROWSER_PROBLEM"
        fi
      done
      set +f
      IFS="$old_ifs"
    else
      say "  browser: none at or above $BROWSER_MIN_BUILD under $BROWSER_CACHE/chrome-headless-shell"
    fi
    say "  write $RENDER_HOME/$tag/puppeteer.json, the empty .puppeteerrc.json and $BROWSER_STAMP, and verify them with a smoke render run in $RENDER_HOME/$tag"
  done
  if [ "${MERMAID_RENDER_NO_SANDBOX:-}" = "1" ]; then
    say "MERMAID_RENDER_NO_SANDBOX=1: the browser would run without its sandbox"
  fi
  exit 0
fi

# ----------------------------------------------------------------------------------- install

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
  preferred=""
  for revisions in "$dest/node_modules/puppeteer-core/lib/cjs/puppeteer/revisions.js" \
                   "$dest/node_modules/puppeteer-core/lib/puppeteer/revisions.js"; do
    if [ -z "$preferred" ] && [ -f "$revisions" ]; then
      preferred="$(sed -n "s/.*'chrome-headless-shell': '\([0-9.]*\)'.*/\1/p" "$revisions" | head -n 1)"
    fi
  done
  if [ "$pptr_major" -ge 22 ] 2>/dev/null; then
    headless="shell"
  else
    headless="new"
  fi
  # Puppeteer's search for a configuration ends at this file (render_check.py PUPPETEER_RC).
  printf '{}\n' > "$dest/.puppeteerrc.json" || fail "cannot write $dest/.puppeteerrc.json"
  chosen=""
  chosen_hash=""
  chosen_stat=""
  refused=""
  smoked=0
  SMOKE_LOG=""
  candidates="$(browser_candidates "$preferred")"
  [ -n "$candidates" ] || fail "no chrome-headless-shell at or above $BROWSER_MIN_BUILD under $BROWSER_CACHE/chrome-headless-shell and MERMAID_RENDER_CHROME is unset; install one with 'npx --yes @puppeteer/browsers@$BROWSERS_TOOL install chrome-headless-shell@$BROWSER_MIN_BUILD --path $BROWSER_CACHE', the build $BROWSER_TABLE records, and run this script again; another build needs MERMAID_RENDER_BROWSER_SHA256, which the operator sets"
  old_ifs="$IFS"
  IFS='
'
  set -f  # a path is one candidate, never a glob
  for exe in $candidates; do
    IFS="$old_ifs"
    if ! browser_accepted "$exe"; then
      if [ "$BROWSER_PROBLEM" = "not recorded" ]; then
        say "$tag: browser $exe refused: tree sha256 $BROWSER_HASH is not recorded in $BROWSER_TABLE"
        refused="$refused $BROWSER_HASH"
      else
        say "$tag: browser $exe refused: $BROWSER_PROBLEM"
      fi
      continue
    fi
    # The resolved path runs and is stamped: the browser that was hashed is the one that runs.
    write_puppeteer_config "$dest/puppeteer.json" "$BROWSER_EXE" "$headless"
    smoked=1
    if smoke_render "$dest" "$dest/puppeteer.json"; then
      chosen="$BROWSER_EXE"
      chosen_hash="$BROWSER_HASH"
      chosen_stat="$BROWSER_STAT"
      break
    fi
  done
  set +f
  IFS="$old_ifs"
  if [ -z "$chosen" ]; then
    rm -f "$dest/puppeteer.json" "$dest/$BROWSER_STAMP"
    if [ "$smoked" -eq 0 ] && [ -n "$refused" ]; then
      fail "no browser for $tag is accepted (tree sha256:$refused); the operator may confirm where this browser came from, then set MERMAID_RENDER_BROWSER_SHA256 to its tree hash and run this script again; an agent stops here and reports this refusal"
    fi
    if [ "$smoked" -eq 0 ]; then
      fail "no browser for $tag is accepted; each refusal is named above; an agent stops here and reports it"
    fi
    fail "no cached chrome-headless-shell renders with $tag under the sandbox and the network block; last log: $SMOKE_LOG"
  fi
  printf '%s  %s\nstat %s\n' "$chosen_hash" "$chosen" "$chosen_stat" > "$dest/$BROWSER_STAMP" \
    || fail "cannot write $dest/$BROWSER_STAMP"
  say "$tag: mermaid $installed, puppeteer $pptr, browser $chosen (build $(build_of "$chosen"), headless: $headless, tree sha256 $chosen_hash)"
done

if [ "${MERMAID_RENDER_NO_SANDBOX:-}" = "1" ]; then
  say "warning: MERMAID_RENDER_NO_SANDBOX=1, the browser runs without its sandbox"
fi
say "installed: $TAGS under $RENDER_HOME"
exit 0
