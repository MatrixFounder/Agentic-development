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
import subprocess
import sys
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
    "feedback_dir": ".agent/feedback",
}


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
    """Resolve the MAIN working tree for *repo_root* (worktree-safe)."""
    repo_root = Path(repo_root)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10)
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
    resolved = (root / candidate).resolve()
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
    if parts and parts[0] in _FORBIDDEN_ROOTS:
        raise CliError(
            "config key %r points into %s/, which is executable agent surface, "
            "not a ledger (%s) in %s"
            % (key, parts[0], raw, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="put ledgers under docs/ (or another documentation "
                        "tree); run-feedback must not write agent instructions")
    if resolved.name in _FORBIDDEN_NAMES:
        raise CliError(
            "config key %r targets the bootstrap instruction file %s in %s"
            % (key, resolved.name, source or "built-in defaults"),
            code=EXIT_CONFIG, err_type="ConfigError",
            remediation="choose a ledger file, e.g. docs/BACKLOG.md")
    # return the RESOLVED path: returning the unresolved one let a symlink
    # planted between the check and the write escape anyway (V-14)
    return resolved


class Config:
    def __init__(self, values, repo_root, source):
        self._values = values
        self.repo_root = Path(repo_root)
        self.source = source  # path of the config file, or None for defaults
        self.data_root = main_worktree_root(self.repo_root)

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
        return self._values["backlog_anchor"]

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
        return dict(self._values.get("id_prefixes") or {})

    @property
    def excerpt_max_chars(self):
        return int(self._values.get("excerpt_max_chars", 2000))

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
