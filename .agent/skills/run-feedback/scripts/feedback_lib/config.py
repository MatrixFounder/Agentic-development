"""Per-repo configuration for the run-feedback engine.

Resolution order (first hit wins):
  1. explicit ``--config PATH`` argument
  2. ``RUN_FEEDBACK_CONFIG`` environment variable
  3. ``<repo-root>/docs/feedback/config.json``
  4. built-in defaults

JSON, not YAML, on purpose: the engine is stdlib-only and the framework's
one hand-rolled YAML parser (skill-session-state) is a documented source
of pain.

Two distinct roots:
  * ``repo_root``  — the checkout whose ledgers we read/write (walk-up to
    ``.git`` from cwd).
  * ``data_root``  — where ``.agent/feedback/`` lives. Always the MAIN
    working tree (via ``git rev-parse --git-common-dir``) so captures made
    inside a linked worktree survive its teardown.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from .envelope import EXIT_CONFIG, CliError

CONFIG_VERSION = 1
CONFIG_ENV = "RUN_FEEDBACK_CONFIG"
CONFIG_REL_PATH = Path("docs") / "feedback" / "config.json"

#: work-item ledger layouts — the two-level contract, or the legacy one-bullet
#: append (see ledger_backlog for why the latter now refuses long bodies)
LEDGER_LAYOUTS = ("index+files", "flat")

#: first path components a configured ledger path may never point into: these
#: hold agent instructions, skills, commands and git internals — executable
#: surface, not documentation (see _contained)
_FORBIDDEN_ROOTS = frozenset({".git", ".claude", ".agent", ".codex", ".cursor",
                              ".gemini", ".antigravity", "System"})

#: bootstrap instruction files a ledger path may never target
_FORBIDDEN_NAMES = frozenset({"CLAUDE.md", "GEMINI.md", "AGENTS.md",
                              "SKILL.md", "README.md"})

#: config keys that name a ledger FILE (as opposed to a record directory); these
#: must be Markdown, because the writer appends markdown structure to them
_LEDGER_FILE_KEYS = frozenset({"index_path", "backlog_path"})

DEFAULTS = {
    "v": CONFIG_VERSION,
    "issues_dir": "docs/issues",
    "index_path": "docs/KNOWN_ISSUES.md",
    "backlog_path": None,
    "backlog_anchor": "<!-- feedback:discovered-issues -->",
    "backlog_dir": "docs/backlog",
    "backlog_prefix": "WI",
    "backlog_layout": "index+files",
    "id_prefixes": {"_default": "RF"},
    "excerpt_max_chars": 2000,
    "body_max_chars": 64000,
    "feedback_dir": ".agent/feedback",
}

#: an ID prefix becomes part of a record id and of a filename stem, so it may not
#: carry path separators, whitespace or markdown. The `-` is load-bearing: live
#: consumers ship `TF-X`, `WIKI-INGEST`, `HTML2MD` (audit 093 Risk 1).
_PREFIX_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")


def find_repo_root(start=None):
    """Walk up from *start* (default cwd) to the first dir containing .git."""
    cur = Path(start or os.getcwd()).resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / ".git").exists():
            return candidate
    raise CliError(
        "not inside a git repository (no .git found walking up from %s)" % cur,
        code=EXIT_CONFIG, err_type="ConfigError",
        remediation="run from inside the target repo or pass --repo-root")


def main_worktree_root(repo_root):
    """Resolve the MAIN working tree for *repo_root* (worktree-safe).

    ``timeout=2``, not 10: this is one `git rev-parse` against a local checkout,
    and the only reason it would hang is a broken `.git` file, a stalled network
    or FUSE mount, or index.lock contention — none of which get better with eight
    more seconds. It used to run from ``Config.__init__``, so that timeout was the
    worst-case stall of *every* invocation including the synchronous PostToolUse
    hook (WI-4). Failure is silent by design: the fallback is ``repo_root``.
    """
    repo_root = Path(repo_root)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=2)
        if out.returncode == 0:
            common = Path(out.stdout.strip())
            if not common.is_absolute():
                common = (repo_root / common).resolve()
            if common.name == ".git":
                return common.parent
    except (OSError, subprocess.SubprocessError):
        pass
    return repo_root


def _contained(root, raw, key, source, ledger=True):
    """Resolve ``root / raw`` and refuse anything that leaves *root*.

    ``pathlib`` DISCARDS the left operand when the right is absolute, so
    ``"backlog_dir": "/etc/cron.d"`` used to write to `/etc/cron.d`, and
    ``"../../.."`` traversed out of the checkout (verified exploit S-05) — while
    SKILL.md §5 promises writes land ONLY in the configured ledger paths of the
    examined repo. A config file is repo-supplied data, not a trusted argument.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise CliError("config key %r must be a non-empty relative path (got "
                       "%r) in %s" % (key, raw, source or "built-in defaults"),
                       code=EXIT_CONFIG, err_type="ConfigError")
    candidate = Path(raw)
    if candidate.is_absolute():
        raise CliError("config key %r must be RELATIVE to the repo root (got "
                       "%r) in %s" % (key, raw, source or "built-in defaults"),
                       code=EXIT_CONFIG, err_type="ConfigError",
                       remediation="use a path inside the repo, e.g. docs/backlog")
    root = Path(root).resolve()
    try:
        resolved = (root / candidate).resolve()
    except (OSError, ValueError) as exc:
        # ValueError, not OSError, is what an embedded NUL raises — so a corrupt or
        # hostile config escaped as a bare traceback instead of the ConfigError
        # every other bad value gets (iteration 3, L-23)
        raise CliError("config key %r is not a usable path (%r): %s"
                       % (key, raw, exc),
                       code=EXIT_CONFIG, err_type="ConfigError")
    if resolved != root and root not in resolved.parents:
        raise CliError("config key %r escapes the repo root (%s -> %s) in %s"
                       % (key, raw, resolved, source or "built-in defaults"),
                       code=EXIT_CONFIG, err_type="ConfigError",
                       remediation="run-feedback only writes inside the "
                                   "examined repo (SKILL.md §5)")
    # Staying inside the repo is not enough. Containment was repo-granular, so a
    # config could aim ledger writes at the agent's own instruction files —
    # `"index_path": "CLAUDE.md"` rewrites the orchestrator's prompt with an
    # attacker-controlled title line, `"backlog_dir": ".claude/commands"` turns
    # an unbounded record body into a new slash command (vdd-multi iteration 2,
    # V-11). Ledgers are documentation; these trees are executable surface.
    # ...but only for LEDGER paths. `feedback_dir` legitimately lives at
    # `.agent/feedback` (gitignored machine state) — this guard is about the
    # documentation files humans and agents READ, not about internal state.
    parts = resolved.relative_to(root).parts if resolved != root else ()
    if not ledger:
        return resolved
    # Compared CASEFOLDED and NFC-normalized, against EVERY component rather than
    # just the first. `Path.resolve()` does not canonicalize case, and macOS/APFS
    # and Windows are case-insensitive — so `".Claude/commands"` sailed past an
    # exact-match check on `".claude"` and wrote an attacker-influenced record body
    # into the real `.claude/commands/`, creating a slash command. That is the V-11
    # exploit this control exists to stop, reachable by changing one letter's case
    # (verified exploit, iteration 3 H-02). `.Agent`, `system`, `Claude.md` and
    # `readme.md` bypassed identically.
    folded = [unicodedata.normalize("NFC", part).casefold() for part in parts]
    forbidden = {name.casefold() for name in _FORBIDDEN_ROOTS}
    hit = next((part for part, fold in zip(parts, folded) if fold in forbidden),
               None)
    if hit is not None:
        raise CliError(
            "config key %r points into %s/, which is executable agent surface, "
            "not a ledger (%s) in %s"
            % (key, hit, raw, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="put ledgers under docs/ (or another documentation "
                        "tree); run-feedback must not write agent instructions")
    # STRUCTURAL rules, not just a denylist. Eight forbidden dirs and five
    # forbidden basenames is not a containment policy: everything else in the repo
    # was a legal ledger target, and `insert_index_line` needs no anchor, so it
    # would append a `## <category>` block to ANY text file. Reachable targets
    # included `.cursorrules`, `.github/copilot-instructions.md` and any `@`-imported
    # doc (agent-instruction injection), and `.envrc` — where the generated index
    # line's backticks are command substitution to bash (iteration 3, H-03).
    # Refusing dot-components kills that class outright, and both live consumer
    # configs already satisfy both rules.
    # `record_link`'s output is interpolated into a markdown link target, and only
    # the link TEXT was escaped — so a config path containing `)` closed the link
    # early and the rest became an attacker-controlled `[click here](https://…)`
    # inside a git-tracked, agent-read index (iteration 3, sec-M-05). Control
    # characters additionally forge lines in `doctor` output and in `hint:` lines,
    # both of which the orchestrator reads as fact (sec-M-06).
    bad = [ch for ch in raw if ch in "()[]<>|`\"'" or not ch.isprintable()]
    if bad:
        raise CliError(
            "config key %r contains characters that are unsafe in a markdown "
            "link or a report line (%s) in %s"
            % (key, ", ".join(sorted({repr(c) for c in bad})),
               source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="use a plain path: letters, digits, '.', '-', '_', '/'")
    dotted = next((part for part in parts if part.startswith(".")), None)
    if dotted is not None:
        raise CliError(
            "config key %r points at a dotfile/dotdir component %r (%s) in %s"
            % (key, dotted, raw, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="ledgers are documentation — put them under docs/. "
                        "Dot-paths are tool configuration and agent instructions, "
                        "never a ledger")
    if key in _LEDGER_FILE_KEYS and resolved.suffix.lower() != ".md":
        raise CliError(
            "config key %r must name a Markdown file (got %r) in %s"
            % (key, raw, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="a thin-index ledger is a .md file; pointing this at a "
                        "structured file (package.json, a workflow yml) would "
                        "append markdown into it")
    if (unicodedata.normalize("NFC", resolved.name).casefold()
            in {name.casefold() for name in _FORBIDDEN_NAMES}):
        raise CliError(
            "config key %r targets the bootstrap instruction file %s in %s"
            % (key, resolved.name, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="choose a ledger file, e.g. docs/BACKLOG.md")
    # return the RESOLVED path: returning the unresolved one let a symlink
    # planted between the check and the write escape anyway (V-14)
    return resolved


def _positive_int(values, key, source, default):
    raw = values.get(key, default)
    try:
        number = int(raw)
    except (TypeError, ValueError):
        raise CliError("config key %r must be an integer (got %r) in %s"
                       % (key, raw, source or "built-in defaults"),
                       code=EXIT_CONFIG, err_type="ConfigError")
    if number < 1:
        raise CliError("config key %r must be >= 1 (got %r) in %s"
                       % (key, number, source or "built-in defaults"),
                       code=EXIT_CONFIG, err_type="ConfigError")
    return number


class Config:
    def __init__(self, values, repo_root, source):
        self._values = values
        self.repo_root = Path(repo_root)
        self.source = source  # path of the config file, or None for defaults
        self._data_root = None

    @property
    def data_root(self):
        """Main working tree, resolved on FIRST USE and cached per instance.

        Only ``feedback_dir`` and its children need this, so ``doctor``,
        ``issues``, ``triage`` and every ``--dry-run`` used to pay a fork+exec
        they never read — and the hook paid it on every tool call, before the two
        cheap filters that discard most events (WI-4).

        The per-instance cache is not an optimization, it is a correctness
        requirement: ``feedback_dir`` is read many times per run, and an uncached
        property would spawn ``git`` on each access — worse than the eager call it
        replaced. There is deliberately NO module-level memo: it would buy nothing
        once the property is lazy, and a cache keyed on a path outlives the
        temporary checkout it describes (audit 093 Risk 3).
        """
        if self._data_root is None:
            self._data_root = main_worktree_root(self.repo_root)
        return self._data_root

    def __getitem__(self, key):
        return self._values[key]

    def get(self, key, default=None):
        return self._values.get(key, default)

    # --- ledger paths (relative to the examined checkout, containment-checked)
    @property
    def issues_dir(self):
        return _contained(self.repo_root, self._values["issues_dir"],
                          "issues_dir", self.source)

    @property
    def index_path(self):
        return _contained(self.repo_root, self._values["index_path"],
                          "index_path", self.source)

    @property
    def backlog_path(self):
        raw = self._values.get("backlog_path")
        if not raw:
            return None
        return _contained(self.repo_root, raw, "backlog_path", self.source)

    @property
    def backlog_anchor(self):
        """The insertion marker. Validated, because an empty or padded value is
        not a harmless typo: ``anchor_positions`` compares ``line.strip() ==
        anchor``, so ``""`` matches EVERY blank line in the ledger and the
        exactly-one-match guard then reports "found 47 times" — or, in a ledger
        with a single blank line, silently inserts there (V-13)."""
        value = self._values["backlog_anchor"]
        if not isinstance(value, str) or not value.strip():
            raise CliError(
                "config key 'backlog_anchor' must be a non-empty string (got "
                "%r) in %s" % (value, self.source or "built-in defaults"),
                code=EXIT_CONFIG, err_type="ConfigError",
                remediation="use the default "
                            "'<!-- feedback:discovered-issues -->'")
        if value != value.strip() or "\n" in value or "\r" in value:
            raise CliError(
                "config key 'backlog_anchor' must be a single line with no "
                "leading/trailing whitespace (got %r) in %s"
                % (value, self.source or "built-in defaults"),
                code=EXIT_CONFIG, err_type="ConfigError",
                remediation="the anchor is compared against a stripped ledger "
                            "line, so padding could never match")
        return value

    @property
    def backlog_dir(self):
        """Record dir of the work-item ledger (Registry B, index+files layout)."""
        return _contained(self.repo_root, self._values["backlog_dir"],
                          "backlog_dir", self.source)

    @property
    def backlog_prefix(self):
        return self._values["backlog_prefix"]

    @property
    def backlog_layout(self):
        """``index+files`` (default, the known-issues-format contract) or the
        legacy single-bullet ``flat``."""
        value = self._values["backlog_layout"]
        if value not in LEDGER_LAYOUTS:
            raise CliError(
                "backlog_layout %r unsupported (expected one of %s)"
                % (value, list(LEDGER_LAYOUTS)),
                code=EXIT_CONFIG, err_type="ConfigError",
                remediation="fix backlog_layout in %s"
                            % (self.source or "docs/feedback/config.json"))
        return value

    @property
    def id_prefixes(self):
        """component -> ID prefix. Values reach a record id AND a filename stem,
        so an unvalidated one produced ids like ``../x-1`` or ``a b-1`` that no
        `next_number` pattern could ever match again (V-13)."""
        raw = self._values.get("id_prefixes") or {}
        if not isinstance(raw, dict):
            raise CliError(
                "config key 'id_prefixes' must be an object (got %r) in %s"
                % (type(raw).__name__, self.source or "built-in defaults"),
                code=EXIT_CONFIG, err_type="ConfigError")
        for component, prefix in raw.items():
            if not isinstance(prefix, str) or not _PREFIX_RE.match(prefix):
                raise CliError(
                    "id_prefixes[%r] = %r is not a usable ID prefix in %s"
                    % (component, prefix,
                       self.source or "built-in defaults"),
                    code=EXIT_CONFIG, err_type="ConfigError",
                    remediation="a prefix starts with a letter and contains "
                                "only letters, digits, '_' and '-' (max 32) — "
                                "it becomes part of an id and a filename")
        return dict(raw)

    @property
    def excerpt_max_chars(self):
        return _positive_int(self._values, "excerpt_max_chars", self.source,
                             2000)

    @property
    def body_max_chars(self):
        """Ceiling for an operator-supplied record body (WI-2). Generous on
        purpose: no honest triage summary approaches it, so hitting it means a log
        got pasted where a summary belongs. Over-cap bodies are REFUSED, never
        truncated — see ``feedback_lib/body.py`` for why nothing is rewritten."""
        return _positive_int(self._values, "body_max_chars", self.source, 64000)

    # --- machine state (always on the main working tree) ------------------
    @property
    def feedback_dir(self):
        # contained against data_root (the MAIN worktree), not repo_root: that
        # is the documented home of machine state for linked worktrees
        return _contained(self.data_root, self._values["feedback_dir"],
                          "feedback_dir", self.source, ledger=False)

    @property
    def inbox_dir(self):
        return self.feedback_dir / "inbox"

    @property
    def filed_dir(self):
        return self.feedback_dir / "filed"

    @property
    def dismissed_dir(self):
        return self.feedback_dir / "dismissed"

    @property
    def journal_dir(self):
        return self.feedback_dir / "journal"

    @property
    def filing_lock(self):
        return self.feedback_dir / ".filing.lock"

    @property
    def retro_owner_path(self):
        return self.feedback_dir / "retro_owner"

    @property
    def mine_state_path(self):
        return self.feedback_dir / "mine_state.json"


def load_config(config_arg=None, repo_root=None, env=None):
    env = env if env is not None else os.environ
    root = Path(repo_root).resolve() if repo_root else find_repo_root()

    path = None
    if config_arg:
        path = Path(config_arg)
    elif env.get(CONFIG_ENV):
        path = Path(env[CONFIG_ENV])
    elif (root / CONFIG_REL_PATH).is_file():
        path = root / CONFIG_REL_PATH

    values = dict(DEFAULTS)
    if path is not None:
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise CliError("config file not found: %s" % path,
                           code=EXIT_CONFIG, err_type="ConfigError")
        except (OSError, json.JSONDecodeError) as exc:
            raise CliError("config file unreadable: %s (%s)" % (path, exc),
                           code=EXIT_CONFIG, err_type="ConfigError")
        if not isinstance(raw, dict):
            raise CliError("config must be a JSON object: %s" % path,
                           code=EXIT_CONFIG, err_type="ConfigError")
        if raw.get("v", CONFIG_VERSION) != CONFIG_VERSION:
            raise CliError(
                "config schema v%s unsupported (engine speaks v%s): %s"
                % (raw.get("v"), CONFIG_VERSION, path),
                code=EXIT_CONFIG, err_type="ConfigError")
        for key in raw:
            if key not in DEFAULTS:
                sys.stderr.write(
                    "run-feedback: warning: unknown config key %r in %s\n"
                    % (key, path))
        values.update({k: v for k, v in raw.items() if k in DEFAULTS})

    return Config(values, root, str(path) if path else None)
