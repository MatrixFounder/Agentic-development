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

DEFAULTS = {
    "v": CONFIG_VERSION,
    "issues_dir": "docs/issues",
    "index_path": "docs/KNOWN_ISSUES.md",
    "backlog_path": None,
    "backlog_anchor": "<!-- feedback:discovered-issues -->",
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

    # --- ledger paths (relative to the examined checkout) -----------------
    @property
    def issues_dir(self):
        return self.repo_root / self._values["issues_dir"]

    @property
    def index_path(self):
        return self.repo_root / self._values["index_path"]

    @property
    def backlog_path(self):
        raw = self._values.get("backlog_path")
        return (self.repo_root / raw) if raw else None

    @property
    def backlog_anchor(self):
        return self._values["backlog_anchor"]

    @property
    def id_prefixes(self):
        return dict(self._values.get("id_prefixes") or {})

    @property
    def excerpt_max_chars(self):
        return int(self._values.get("excerpt_max_chars", 2000))

    # --- machine state (always on the main working tree) ------------------
    @property
    def feedback_dir(self):
        return self.data_root / self._values["feedback_dir"]

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
