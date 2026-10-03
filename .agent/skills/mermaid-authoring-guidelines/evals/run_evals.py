#!/usr/bin/env python3
"""Executor of the A/B evaluation of `mermaid-authoring-guidelines` (TASK 108, R11.2-R11.4, R11.10).

Two arms per case. They differ in ONE input. `with_skill` receives the case prompt preceded by one
block: `SKILL.md` and the reference files that the routing table of `SKILL.md` names for the
figure kind of the case's key. `without_skill` receives the case prompt alone. Template, model,
effort, flags, environment and working-directory shape are the same in both arms (ARCHITECTURE
section 7.6, L5).

This is the ONLY script of the evaluation that spends tokens. `--dry-run` prints every command,
the bundle files with their sha256 and word counts, the provenance state and the budget
projection, and spawns nothing.

Routing (TASK R1.4, R11.3)
  The table under the anchor line `<!-- contract:routing -->` of `SKILL.md` is read by column
  position: the first code span of column 1 is the figure kind, every code span of column 2 is a
  reference file. The header row is not read, so its wording and language are free. The row
  `none` names no file: a case whose key names no kind gets `SKILL.md` alone.

Key kind (TASK R11.2)
  The bundle uses the `kind` of the case's `key.json`. `evals.json` repeats it as `figure_kind`;
  a difference between the two is an instrument error (exit 2).

Provenance (TASK R11.10)
  A paid run starts only when `PROVENANCE.txt`, next to `evals.json`, lists the sha256 of
  `README.md`, of the prompt template and of every `key.json`, and every listed file still has
  that sha256. One line per file, in the output format of `shasum -a 256` run inside `evals/`:
  `<64 hex digits>  <path relative to evals/>`. Blank lines and lines that start with `#` are
  skipped. A listed file outside the required set, `evals.json` for example, is verified too.
  Every run record carries the verified hashes, and `campaign.json` binds them to its campaign.
  The orchestrator writes the file; this script never does. `--dry-run` reports its state and
  runs without it.

Isolation (TASK R11.4)
  * Every run starts `claude -p` in a fresh `tempfile.mkdtemp()` directory. `leaks_above` refuses
    a directory with a context file or a git repository at or above it (exit 2).
  * Tools, skills, MCP servers and slash commands are off: `--tools ""`, `--safe-mode`,
    `--disable-slash-commands`, `--strict-mcp-config` with an empty `--mcp-config`.
    `--disallowed-tools` repeats the denial for each tool name. `--no-session-persistence`
    keeps the runs out of the session store.
  * Model and effort are passed as flags: `--model` and `--effort`.
  * The child environment loses the named variables of `REMOVED_ENV_VARS`:
    - `SESSION_ENV_VARS`, the session-control variables of a calling Claude Code session. Six
      are named by the TASK; the others were set in the orchestrating session on 2026-10-02.
    - `PIN_OVERRIDE_VARS`, which override the pinned model, effort, thinking budget, output
      limit or session persistence. Their names come from the strings of Claude Code 2.1.287.
    Every other variable passes, authentication included: `CLAUDE_CODE_OAUTH_TOKEN`,
    `ANTHROPIC_API_KEY`, `CLAUDE_CONFIG_DIR`, `HOME`. Each run record names the variables
    removed from its environment. It also names every passed variable with a prefix the CLI
    reads that neither list names (`unlisted_env_names`).
  * stdin is closed, so nothing a caller pipes in reaches the prompt.

Flags (checked against `claude --help` of Claude Code 2.1.287 on 2026-10-02)
  Used: `-p`, `--output-format json`, `--model`, `--effort`, `--safe-mode`, `--tools ""`,
  `--disable-slash-commands`, `--strict-mcp-config`, `--mcp-config`, `--no-session-persistence`,
  `--max-budget-usd`, `--disallowed-tools`.
  Not used: `--bare` reads neither OAuth nor the keychain, so it ends the operator's login;
  `--restricted` keeps the file tools, which `--tools ""` removes.
  A real run reads `claude --help` again and exits 2 when a flag of `build_command` is gone.

Budget (TASK D18, A13)
  The spend is the summed `total_cost_usd` of every attempt recorded in an `attempts.jsonl`
  under `evals/corpus*/` and under `--budget-root`, wherever the out-root lies; both arms and
  the revision round share one cap. An attempt that reports no cost (a timeout, a process that
  printed no envelope) counts at the mean cost per run. A run is projected at the mean cost per
  run of its arm so far; with no cost of that arm recorded, at the mean of all runs; with none
  recorded, at `--run-cap-usd`, the most one run may spend. A new attempt starts only while the
  spend, the projections of the attempts in progress and its own projection stay within the
  cap. Every admission reads the ledgers again under one lock that every executor of this
  checkout takes for the same ledgers, so a second executor's settled attempts count at once
  (EI-17); its attempts in progress do not. The lock file sits in `evals/corpus/`, where git
  ignores `*.lock`, while it is held, and its holder removes it (R6). It is never opened through
  a symlink and must belong to the user; a lock held by another process for
  `BUDGET_LOCK_WAIT_S` stops the executor with exit 2 (SEC2-07). An attempt that cost money is
  recorded in its ledger even when the lock fails. `--budget-usd`, `--run-cap-usd` and
  `--timeout` take finite positive numbers only: a cap of nan or inf would admit every run
  (SEC2-04).

Corpus (the skill-creator viewer layout)
  <out-root>/campaign.json                       model, effort, provenance, removed variables,
                                                 run cap, timeout, retries, reps, CLI version
  <out-root>/attempts.jsonl, errors.jsonl        every attempt with its cost; failed attempts
  <out-root>/eval-<id>-<name>/eval_metadata.json read by aggregate_benchmark.py
  <out-root>/eval-<id>-<name>/<arm>/eval_metadata.json   read by the review viewer
  <out-root>/eval-<id>-<name>/<arm>/run-<k>/outputs/answer.md
                                     .../run-<k>/run.meta.json, timing.json, envelope.json
  An existing run directory is never written again. A run that produced no answer is listed in
  `errors.jsonl` and gets no run directory, so running the same command again repeats it.

Exit codes (TASK D20 and ARCHITECTURE section 7.4 for 2 and 3)
  0  every planned run completed, or existed already
  1  a run failed after its retries, or the budget stopped runs from starting
  2  not isolated, or an instrument error: a bundle, key or case file absent, or a case file
     outside `fixtures/`; a key kind that differs from `evals.json`; `PROVENANCE.txt` absent
     or a hash in it that differs; a flag absent from `claude --help`; a prompt, model, effort
     or bound setting (run cap, timeout, retries, reps, CLI version) that differs from the
     campaign's; a served model other than the pinned one; a second executor on the same
     campaign; or a budget lock that is not a regular file of this user, or that another
     process holds for `BUDGET_LOCK_WAIT_S`; or an interpreter below the framework's minimum
     Python
  3  usage error, a budget, run cap or timeout that is not a finite positive number included

Standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import hashlib
import json
import math
import os
import random
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
from typing import Optional

# The framework's minimum Python, stated in README §3. Checked before anything is imported from
# this repository or written. Exit 2: this interpreter cannot run the script.
if sys.version_info < (3, 11):
    _name = Path(sys.argv[0] if sys.argv and sys.argv[0].endswith(".py") else __file__).name
    if _name == "__main__.py":  # `python -m <package>`: name this module instead
        _name = Path(__file__).name
    sys.stderr.write(f"{_name} needs Python 3.11 or newer (3.14 is the main version); "
                     f"this is Python {sys.version_info[0]}.{sys.version_info[1]}.\n")
    sys.exit(2)

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
EVALS_PATH = HERE / "evals.json"
CORPUS_DIR = HERE / "corpus"
SKILL_NAME = "mermaid-authoring-guidelines"

EXIT_OK, EXIT_RUN_FAILED, EXIT_INSTRUMENT, EXIT_USAGE = 0, 1, 2, 3

ARMS = ("without_skill", "with_skill")

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "xhigh"
EFFORTS = ("low", "medium", "high", "xhigh", "max")
DEFAULT_REPS = 3
DEFAULT_BUDGET_USD = 60.0
DEFAULT_RUN_CAP_USD = 5.0
DEFAULT_TIMEOUT_S = 1200
DEFAULT_RETRIES = 1
#: Seconds before a retry; multiplied by the attempt number and a jitter in [0.5, 1.5).
BACKOFF_S = 15.0

#: The figure kind of a case whose prompt names none (TASK R11.2); its bundle is `SKILL.md` alone.
KIND_NONE = "none"
#: The anchor line above the routing table of `SKILL.md` (TASK R1.4).
ROUTING_ANCHOR = "<!-- contract:routing -->"
#: Word limits of TASK R1.5 and D26, counted as `len(text.split())`, as `validate_skill.py` counts.
SKILL_WORD_LIMIT = 3000
BUNDLE_WORD_LIMIT = 16000
#: The hash record of TASK R11.10, next to `evals.json`.
PROVENANCE_NAME = "PROVENANCE.txt"

#: A directory holding any of these hands the `without_skill` arm a context the other arm also
#: has, or the framework's catalogue that names the skill. `.git` is listed because the CLI puts
#: the repository status into its system prompt.
LEAK_NAMES = ("CLAUDE.md", "CLAUDE.local.md", ".agent", ".claude", "AGENTS.md", "GEMINI.md", ".git")

#: Defence in depth: `--tools ""` already removes every built-in tool.
DENIED_TOOLS = ("Bash", "Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Glob", "Grep",
                "WebFetch", "WebSearch", "Task", "Agent", "TodoWrite", "Skill")

EMPTY_MCP_CONFIG = '{"mcpServers":{}}'

#: Session-control variables of a calling Claude Code session (TASK R11.4). The first six are
#: named by the TASK; the others were set in the orchestrating session on 2026-10-02.
SESSION_ENV_VARS = (
    "CLAUDECODE", "CLAUDE_EFFORT", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_EXECPATH",
    "CLAUDE_CODE_ENABLE_TASKS", "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "CLAUDE_CODE_EMIT_STARTUP_TIMING",
    "CLAUDE_CODE_QUESTION_PREVIEW_FORMAT", "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_PID",
    "MCP_CONNECTION_NONBLOCKING", "AI_AGENT",
)

#: Variables that override the pinned model, effort, thinking budget, output limit or session
#: persistence of the child; none was set on 2026-10-02.
PIN_OVERRIDE_VARS = (
    "ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_MODEL", "ANTHROPIC_SMALL_FAST_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_FABLE_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_EFFORT_LEVEL", "MAX_THINKING_TOKENS",
    "CLAUDE_CODE_DISABLE_THINKING", "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS", "CLAUDE_CODE_FORCE_SESSION_PERSISTENCE",
)

#: The named list `sanitized_env` removes; nothing else is removed.
REMOVED_ENV_VARS = SESSION_ENV_VARS + PIN_OVERRIDE_VARS

#: Authentication variables. They pass like every variable outside `REMOVED_ENV_VARS`; this list
#: only names them in the dry run and keeps them out of `unlisted_env_names`.
AUTH_ENV_VARS = (
    "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR",
    "CLAUDE_CODE_OAUTH_REFRESH_TOKEN", "CLAUDE_CODE_API_KEY_FILE_DESCRIPTOR",
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CONFIG_DIR",
    "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
)

#: Name prefixes of the variables the CLI reads; `unlisted_env_names` reports a passed one.
CLI_ENV_PREFIXES = ("CLAUDE", "ANTHROPIC", "MCP_", "AI_AGENT")

#: The block `with_skill` prepends. The bundle's files sit between header and footer.
SKILL_BLOCK_HEADER = (f"The skill `{SKILL_NAME}` is loaded. Apply it to the task that follows.\n\n"
                      f"=== BEGIN SKILL {SKILL_NAME} ===\n")
SKILL_BLOCK_FOOTER = "=== END SKILL ===\n\n"

#: Placeholders of `prompts/task-template.md`. Each must occur in the template.
PLACEHOLDERS = ("section_ref", "doc_path", "document", "request", "environment_line",
                "output_instruction")
_PLACEHOLDER_RE = re.compile(r"\{(" + "|".join(PLACEHOLDERS) + r")\}")

#: Fields every case of `evals.json` carries.
CASE_FIELDS = ("id", "name", "lang", "figure_kind", "concern", "medium", "construction", "control",
               "document", "doc_path", "section_ref", "request", "environment_line",
               "output_instruction", "key", "pass", "fail", "fail_expect_failed", "decoys",
               "stresses")

_CAMPAIGN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


class NotIsolated(RuntimeError):
    """A working directory would hand a run a context file or a repository."""


class InstrumentError(RuntimeError):
    """A file, a flag, a hash or a pin the run needs is absent or differs (exit 2)."""


class UsageError(ValueError):
    """The invocation is wrong (exit 3)."""


# --------------------------------------------------------------------------- small helpers


def _read(path) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path, payload) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def _append_jsonl(path, payload) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _fmt_usd(value: float) -> str:
    return f"{value:g}"


def word_count(text: str) -> int:
    """Words as `validate_skill.py` counts them: runs of non-whitespace characters."""
    return len(text.split())


# --------------------------------------------------------------------------- eval set


class _EvalSet(dict):
    """`evals.json` as a dict that remembers its directory; case paths are relative to it."""

    base_dir: Path = HERE


def load_evals(path=None) -> dict:
    """Return `evals.json` (default: next to this script) as a dict."""
    p = Path(path) if path else EVALS_PATH
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    evals = _EvalSet(data)
    evals.base_dir = p.resolve().parent
    return evals


def _base_dir(evals) -> Path:
    return Path(getattr(evals, "base_dir", HERE))


def number_lines(text: str) -> str:
    """Number the lines of *text* as `%4d| ` the way the precedent executor does.

    CRLF becomes LF. A final newline adds no empty numbered line, so the numbers equal the line
    numbers a key cites.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return "\n".join(f"{i:>4}| {line}" for i, line in enumerate(lines, 1))


# --------------------------------------------------------------------------- routing and bundle

_ANCHOR_LINE = re.compile(r"^ {0,3}<!--\s*contract:routing\s*-->\s*$")
_TABLE_LINE = re.compile(r"^\s*\|")
_DELIMITER_ROW = re.compile(r"^\s*\|(\s*:?-{3,}:?\s*\|)+\s*$")
_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_CODE_SPAN = re.compile(r"`([^`]+)`")
_KIND_TOKEN = re.compile(r"^[a-z][a-z0-9-]*$")
_REL_PATH = re.compile(r"^[A-Za-z0-9._/-]+$")
_FORBIDDEN_TOP = ("scripts", "assets", "evals")


def _split_row(line: str) -> list:
    """Split a Markdown table row into cells; a pipe inside a code span stays in its cell."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i, tick = [], [], 0, 0
    while i < len(s):
        ch = s[i]
        if ch == "`":
            j = i
            while j < len(s) and s[j] == "`":
                j += 1
            run = j - i
            if tick == 0:
                tick = run
            elif tick == run:
                tick = 0
            cur.append(s[i:j])
            i = j
            continue
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "|" and tick == 0:
            cells.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _check_routed_path(rel: str, kind: str) -> None:
    parts = rel.split("/")
    if (not _REL_PATH.match(rel) or rel.startswith("/") or ".." in parts or not rel.endswith(".md")
            or parts[0] in _FORBIDDEN_TOP or rel == "SKILL.md"):
        raise ValueError(f"routing row {kind!r}: {rel!r} is not a reference file of the skill")


def _anchor_lines(lines: list) -> list:
    """Indices of the routing anchor lines that lie outside fenced blocks."""
    found, fence = [], None
    for idx, line in enumerate(lines):
        m = _FENCE_OPEN.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
            elif _ANCHOR_LINE.match(line):
                found.append(idx)
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                and not m.group(2).strip():
            fence = None
    return found


def parse_routing(skill_md_text: str) -> dict:
    """Return `{figure kind: [reference files relative to the skill dir]}` (TASK R1.4).

    The table is the first one below the anchor line `<!-- contract:routing -->`, with only blank
    lines between them; an anchor inside a fenced block does not count. Columns are read by
    position: the first code span of column 1 is the kind, every code span of column 2 is a
    file. The header row is not read. The row `none` names no file; every other row names one or
    more. These raise `ValueError`: no anchor or two; no table below the anchor; a row without a
    kind; a kind twice; a `none` row with a file; another row without one; a file twice in a row;
    a file that is not a Markdown file of the skill outside `scripts/`, `assets/` and `evals/`.
    """
    lines = skill_md_text.replace("\r\n", "\n").split("\n")
    anchors = _anchor_lines(lines)
    if not anchors:
        raise ValueError(f"SKILL.md holds no `{ROUTING_ANCHOR}` line outside a fenced block")
    if len(anchors) > 1:
        raise ValueError(f"SKILL.md holds {len(anchors)} `{ROUTING_ANCHOR}` lines")
    head = anchors[0] + 1
    while head < len(lines) and not lines[head].strip():
        head += 1
    if head >= len(lines) or not _TABLE_LINE.match(lines[head]):
        raise ValueError(f"no table follows the `{ROUTING_ANCHOR}` line")
    if head + 1 >= len(lines) or not _DELIMITER_ROW.match(lines[head + 1]):
        raise ValueError("the routing table has no delimiter row under its header")
    if len(_split_row(lines[head])) < 2:
        raise ValueError("the routing table has fewer than two columns")
    routing = {}
    for line in lines[head + 2:]:
        if not _TABLE_LINE.match(line):
            break
        cells = _split_row(line)
        if len(cells) < 2:
            raise ValueError(f"routing row has fewer than two cells: {line.strip()!r}")
        kinds = [k.strip() for k in _CODE_SPAN.findall(cells[0])]
        files = [f.strip() for f in _CODE_SPAN.findall(cells[1])]
        if not kinds or not _KIND_TOKEN.match(kinds[0]):
            raise ValueError(f"routing row names no figure kind: {line.strip()!r}")
        kind = kinds[0]
        if kind in routing:
            raise ValueError(f"routing table names the kind {kind!r} twice")
        if kind == KIND_NONE and files:
            raise ValueError(f"routing row {KIND_NONE!r} names a file; the row routes "
                             f"SKILL.md alone")
        if kind != KIND_NONE and not files:
            raise ValueError(f"routing row {kind!r} names no file")
        for rel in files:
            _check_routed_path(rel, kind)
        if len(set(files)) != len(files):
            raise ValueError(f"routing row {kind!r} names a file twice")
        routing[kind] = files
    if not routing:
        raise ValueError("the routing table has no rows")
    return routing


def _routing_of(skill_dir) -> dict:
    skill_dir = Path(skill_dir)
    try:
        return parse_routing(_read(skill_dir / "SKILL.md"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise InstrumentError(f"routing table of {skill_dir / 'SKILL.md'}: {exc}") from exc


def _routed_files(kind: str, skill_dir) -> list:
    routing = _routing_of(skill_dir)
    if kind not in routing:
        raise InstrumentError(f"the routing table of SKILL.md has no row for the figure kind "
                              f"{kind!r}; rows: {', '.join(routing)}")
    return ["SKILL.md"] + list(routing[kind])


def bundle_manifest(kind: str, skill_dir=SKILL_DIR) -> list:
    """Return `[{path, bytes, words, sha256}]` per bundle file; `{path, absent: True}` when absent."""
    out = []
    for rel in _routed_files(kind, skill_dir):
        path = Path(skill_dir) / rel
        try:
            raw = path.read_bytes()
            words = word_count(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError):
            out.append({"path": rel, "absent": True})
            continue
        out.append({"path": rel, "bytes": len(raw), "words": words,
                    "sha256": hashlib.sha256(raw).hexdigest()})
    return out


def bundle_for(kind: str, skill_dir=SKILL_DIR) -> tuple:
    """Return `(bundle_text, [files])` for a figure kind.

    `bundle_text` is the whole block `with_skill` prepends: the header, then `--- <file> ---` and
    the file's text for `SKILL.md` and each routed reference in routing-table order, then the
    footer. `files` lists the bundle's paths relative to the skill directory, `SKILL.md` first;
    for the kind `none` it is `SKILL.md` alone. An absent or unreadable file raises
    `InstrumentError`.
    """
    skill_dir = Path(skill_dir)
    files = _routed_files(kind, skill_dir)
    root = skill_dir.resolve()
    absent, parts = [], [SKILL_BLOCK_HEADER]
    for rel in files:
        path = (skill_dir / rel).resolve()
        if root not in path.parents:
            raise InstrumentError(f"bundle file {rel} resolves outside the skill directory")
        try:
            text = _read(path)
        except (OSError, UnicodeDecodeError):
            absent.append(rel)
            continue
        if not text.endswith("\n"):
            text += "\n"
        parts.append(f"--- {rel} ---\n{text}")
    if absent:
        raise InstrumentError(f"bundle {kind!r} is incomplete; absent or unreadable: "
                              f"{', '.join(absent)}")
    parts.append(SKILL_BLOCK_FOOTER)
    return "".join(parts), files


def routing_words(skill_dir=SKILL_DIR) -> dict:
    """`{kind: words of SKILL.md plus its routed files, or the error text}` for every row."""
    out = {}
    for kind in _routing_of(skill_dir):
        try:
            manifest = bundle_manifest(kind, skill_dir)
        except InstrumentError as exc:
            out[kind] = str(exc)
            continue
        absent = [m["path"] for m in manifest if m.get("absent")]
        out[kind] = (f"absent: {', '.join(absent)}" if absent
                     else sum(m["words"] for m in manifest))
    return out


# --------------------------------------------------------------------------- keys


def case_path(case: dict, field_: str, evals=None) -> Path:
    """The file a case names (`key`, `document`), resolved inside `fixtures/` next to
    `evals.json`. A path that leaves it raises `InstrumentError`: what a case names goes into
    the paid prompt (SEC-13)."""
    base = _base_dir(evals if evals is not None else load_evals()).resolve()
    path = (base / str(case[field_])).resolve()
    if (base / "fixtures").resolve() not in path.parents:
        raise InstrumentError(f"case {case.get('id')}: {field_} {case[field_]!r} lies outside "
                              f"{base / 'fixtures'}")
    return path


def load_key(case: dict, evals=None) -> dict:
    """Return the `key.json` of *case*; an absent or malformed key raises `InstrumentError`."""
    evals = evals if evals is not None else load_evals()
    path = case_path(case, "key", evals)
    try:
        data = json.loads(_read(path))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise InstrumentError(f"case {case.get('id')}: key {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InstrumentError(f"case {case.get('id')}: key {path} is not a JSON object")
    return data


def case_kind(case: dict, evals=None) -> str:
    """The figure kind that routes the `with_skill` bundle of *case* (TASK R11.2, R11.3).

    It is the `kind` of the case's key. `evals.json` `figure_kind` holds the same value; a
    difference, or a key without a kind token, raises `InstrumentError`.
    """
    key = load_key(case, evals)
    kind = key.get("kind")
    if not isinstance(kind, str) or not _KIND_TOKEN.match(kind):
        raise InstrumentError(f"case {case.get('id')}: the key names no figure kind (`kind`)")
    if case.get("figure_kind") != kind:
        raise InstrumentError(f"case {case.get('id')}: evals.json figure_kind "
                              f"{case.get('figure_kind')!r} differs from the key's kind {kind!r}")
    return kind


# --------------------------------------------------------------------------- prompts


def _fill(template: str, values: dict) -> str:
    """Replace each placeholder once, in one pass, so inserted text is never re-scanned."""
    return _PLACEHOLDER_RE.sub(lambda m: values[m.group(1)], template)


def case_prompt(case: dict, evals=None) -> str:
    """Return the `without_skill` prompt of *case*: the template filled, document line-numbered."""
    evals = evals if evals is not None else load_evals()
    base = _base_dir(evals)
    template_path = (base / evals.get("prompt_template", "prompts/task-template.md")).resolve()
    if base.resolve() not in template_path.parents:
        raise InstrumentError(f"prompt template {template_path} lies outside {base}")
    try:
        template = _read(template_path)
    except OSError as exc:
        raise InstrumentError(f"prompt template {template_path}: {exc}") from exc
    missing = [p for p in PLACEHOLDERS if "{" + p + "}" not in template]
    if missing:
        raise InstrumentError(f"prompt template lacks {', '.join('{' + p + '}' for p in missing)}")
    doc_path = case_path(case, "document", evals)
    try:
        document = _read(doc_path)
    except OSError as exc:
        raise InstrumentError(f"case {case.get('id')}: document {doc_path}: {exc}") from exc
    values = {"section_ref": case["section_ref"], "doc_path": case["doc_path"],
              "document": number_lines(document), "request": case["request"],
              "environment_line": case["environment_line"],
              "output_instruction": case["output_instruction"]}
    return _fill(template, values)


def build_prompt(case: dict, arm: str, evals=None, bundle_text: Optional[str] = None) -> str:
    """Return the prompt of *arm* for *case*.

    `without_skill` is the filled template. `with_skill` is the skill block followed by the
    `without_skill` prompt byte for byte. The block is the bundle of the key's kind;
    `bundle_text` replaces it.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; known: {', '.join(ARMS)}")
    prompt = case_prompt(case, evals)
    if arm == "without_skill":
        return prompt
    if bundle_text is None:
        bundle_text, _ = bundle_for(case_kind(case, evals))
    return bundle_text + prompt


# --------------------------------------------------------------------------- provenance

_PROVENANCE_LINE = re.compile(r"^([0-9A-Fa-f]{64}) [ *](\S.*)$")


def _norm_rel(rel: str) -> str:
    rel = rel.strip()
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def provenance_targets(evals) -> list:
    """Paths, relative to the directory of `evals.json`, that `PROVENANCE.txt` must list.

    `README.md`, the prompt template, the key of every case of `evals.json`, and every
    `fixtures/*/key.json` on disk (TASK R11.10).
    """
    base = _base_dir(evals)
    keys = {_norm_rel(str(c["key"])) for c in evals.get("evals", []) if c.get("key")}
    keys.update(p.relative_to(base).as_posix() for p in base.glob("fixtures/*/key.json"))
    return (["README.md", _norm_rel(evals.get("prompt_template", "prompts/task-template.md"))]
            + sorted(keys))


def read_provenance(path) -> dict:
    """Return `{relative path: sha256}` from a `PROVENANCE.txt`.

    A line is `<64 hex digits>  <path>` or `<64 hex digits> *<path>`. Blank lines and lines that
    start with `#` are skipped. A malformed line, an absolute path, a `..` part or a path listed
    twice raises `InstrumentError`.
    """
    try:
        text = _read(path)
    except (OSError, UnicodeDecodeError) as exc:
        raise InstrumentError(f"{path}: {exc}") from exc
    entries = {}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _PROVENANCE_LINE.match(line)
        if not m:
            raise InstrumentError(f"{path}:{n}: expected `<sha256>  <path>`, found {raw!r}")
        rel = _norm_rel(m.group(2))
        if rel.startswith("/") or "\\" in rel or ".." in rel.split("/"):
            raise InstrumentError(f"{path}:{n}: {rel!r} is not a path inside evals/")
        if rel in entries:
            raise InstrumentError(f"{path}:{n}: {rel} is listed twice")
        entries[rel] = m.group(1).lower()
    return entries


def check_provenance(evals) -> dict:
    """Verify `PROVENANCE.txt` and return the record each run carries.

    Returns `{"file": "PROVENANCE.txt", "sha256": <of the file>, "files": {path: sha256}}`.
    Raises `InstrumentError` when the file is absent, when a path of `provenance_targets` is not
    listed, or when a listed file is absent or has another sha256.
    """
    base = _base_dir(evals)
    path = base / PROVENANCE_NAME
    if not path.is_file():
        raise InstrumentError(
            f"{path} is absent. A paid run starts only after the sha256 of README.md, the prompt "
            f"template and every key.json is recorded there and in the audit (TASK R11.10). "
            f"Format: `shasum -a 256` lines, run inside {base}")
    entries = read_provenance(path)
    problems = [f"{rel} is not listed" for rel in provenance_targets(evals) if rel not in entries]
    for rel, recorded in sorted(entries.items()):
        target = base / rel
        actual = _sha256_file(target) if target.is_file() else None
        if actual is None:
            problems.append(f"{rel} is absent")
        elif actual != recorded:
            problems.append(f"{rel} has sha256 {actual[:16]}, recorded {recorded[:16]}")
    if problems:
        raise InstrumentError(f"{path}: " + "; ".join(problems))
    return {"file": PROVENANCE_NAME, "sha256": _sha256_file(path), "files": dict(sorted(entries.items()))}


def provenance_state(evals) -> tuple:
    """`(record, None)` when `check_provenance` passes, else `(None, reason)`; never raises."""
    try:
        return check_provenance(evals), None
    except InstrumentError as exc:
        return None, str(exc)


# --------------------------------------------------------------------------- isolation


def leaks_above(path) -> list:
    """Return every entry of `LEAK_NAMES` at or above *path*, up to and excluding `$HOME`.

    `~/.claude` is user-level configuration: identical in both arms, not holding this skill, and
    switched off by `--safe-mode`. Walking into `$HOME` would report a leak no directory choice
    removes.
    """
    found = []
    home = os.path.realpath(os.path.expanduser("~"))
    cur = os.path.realpath(path)
    while cur != home:
        for name in LEAK_NAMES:
            candidate = os.path.join(cur, name)
            if os.path.lexists(candidate):
                found.append(candidate)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return found


def isolated_workdir(base=None) -> str:
    """Create a fresh working directory and raise `NotIsolated` when anything leaks into it."""
    path = tempfile.mkdtemp(prefix="mermaid-eval-", dir=base)
    leaks = leaks_above(path)
    if leaks:
        shutil.rmtree(path, ignore_errors=True)
        raise NotIsolated("; ".join(leaks))
    return path


def sanitized_env(environ=None) -> dict:
    """Return a copy of *environ* (default `os.environ`) without the names of `REMOVED_ENV_VARS`.

    Every other variable stays: `HOME`, `USER` and `PATH`, through which the CLI finds the
    login, and the authentication variables of `AUTH_ENV_VARS`.
    """
    src = os.environ if environ is None else environ
    return {k: v for k, v in src.items() if k not in REMOVED_ENV_VARS}


def removed_env_names(environ=None) -> list:
    """Names `sanitized_env` removes from *environ*; recorded per run, values never."""
    src = os.environ if environ is None else environ
    return sorted(k for k in src if k in REMOVED_ENV_VARS)


def unlisted_env_names(environ=None) -> list:
    """Passed names with a prefix of `CLI_ENV_PREFIXES` that no list of this module names."""
    src = os.environ if environ is None else environ
    return sorted(k for k in src if k.upper().startswith(CLI_ENV_PREFIXES)
                  and k not in REMOVED_ENV_VARS and k not in AUTH_ENV_VARS)


# --------------------------------------------------------------------------- command and spawn


def build_command(prompt: str, model: str, effort: str,
                  run_cap_usd: float = DEFAULT_RUN_CAP_USD) -> list:
    """Return the argv of one `claude -p` run. The prompt is one argv element."""
    if prompt.startswith("-"):
        raise ValueError("a prompt starting with '-' would be read as an option")
    return ["claude", "-p", prompt,
            "--output-format", "json",
            "--model", model,
            "--effort", effort,
            "--safe-mode",
            "--tools", "",
            "--disable-slash-commands",
            "--strict-mcp-config", "--mcp-config", EMPTY_MCP_CONFIG,
            "--no-session-persistence",
            "--max-budget-usd", _fmt_usd(run_cap_usd),
            "--disallowed-tools", *DENIED_TOOLS]


def command_flags(argv: list) -> list:
    """The option tokens of *argv*, e.g. `-p`, `--model`."""
    return [a for a in argv[1:] if a.startswith("-") and len(a) > 1]


def missing_flags(help_text: str, argv: Optional[list] = None) -> list:
    """Flags of *argv* (default: a `build_command` argv) that *help_text* does not list."""
    argv = argv or build_command("<prompt>", DEFAULT_MODEL, DEFAULT_EFFORT)
    listed = set(re.findall(r"(?<![\w-])(--?[A-Za-z][\w-]*)", help_text))
    return [f for f in command_flags(argv) if f not in listed]


def _parse_envelope(stdout: str):
    text = stdout.strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    return None


def spawn(prompt: str, model: str, effort: str, workdir, timeout: float = DEFAULT_TIMEOUT_S,
          run_cap_usd: float = DEFAULT_RUN_CAP_USD) -> dict:
    """Run one agent and return its JSON envelope. The only call that spends tokens.

    A timeout, a process that cannot start, an empty or unparsable output come back as an
    envelope with `is_error: true` and an `error` text, so one failed run never discards others.
    A process that never started reports a cost of 0. A process that ran and printed no envelope
    carries `cost_unknown: true`, and the budget counts it at the mean cost per run.
    """
    argv = build_command(prompt, model, effort, run_cap_usd)
    try:
        proc = subprocess.run(argv, cwd=workdir, env=sanitized_env(os.environ),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"is_error": True, "result": "", "error": f"timed out after {timeout}s",
                "returncode": None, "cost_unknown": True}
    except OSError as exc:
        return {"is_error": True, "result": "", "error": f"claude did not start: {exc}",
                "returncode": None, "total_cost_usd": 0}
    envelope = _parse_envelope(proc.stdout)
    if envelope is None:
        detail = (proc.stderr or proc.stdout or "").strip()[-2000:]
        return {"is_error": True, "result": "", "returncode": proc.returncode,
                "error": f"no JSON envelope (exit {proc.returncode}): {detail}",
                "cost_unknown": True}
    if proc.returncode != 0:
        envelope.setdefault("returncode", proc.returncode)
        if not envelope.get("is_error"):
            envelope["is_error"] = True
            envelope.setdefault("error", f"claude exited {proc.returncode}")
    return envelope


def envelope_error(envelope: dict) -> str:
    """Why an envelope failed, in the CLI's own words. A CLI error envelope can carry
    `subtype: success` with the cause in `result` and `api_error_status`; the subtype alone said
    `success` for 30 failed runs of the first campaign attempt (2026-10-03)."""
    if envelope.get("error"):
        return str(envelope["error"])
    if not envelope.get("is_error"):
        return "empty answer"
    parts = []
    if envelope.get("api_error_status") is not None:
        parts.append(f"api_error_status {envelope['api_error_status']}")
    if envelope.get("terminal_reason") not in (None, "completed"):
        parts.append(f"terminal_reason {envelope['terminal_reason']}")
    text = str(envelope.get("result") or "").strip()
    if text:
        parts.append("result: " + text[:300])
    parts.append(f"subtype {envelope.get('subtype')}")
    return "; ".join(parts)


def cost_unknown(envelope) -> bool:
    """True when an attempt may have spent money that its envelope does not report."""
    if not isinstance(envelope, dict):
        return True
    cost = envelope.get("total_cost_usd")
    return bool(envelope.get("cost_unknown")) or not isinstance(cost, (int, float)) \
        or isinstance(cost, bool)


# --------------------------------------------------------------------------- answer


def unwrap_outer_fence(text: str) -> tuple:
    """Strip ONE fence that encloses the whole answer and return `(text, unwrapped)`.

    Unwrapped: an enclosing fence whose info string is `markdown`, `md` or `gfm`; the last line
    closes it even where an inner fence of the same length would close it first, which is how a
    model writes the wrapper. A fence with no info string is unwrapped only when it holds a fence
    of its own and its own closing line is the last line (`_own_close`). A `mermaid` or `text`
    fence alone is the figure and stays.
    """
    lines = text.split("\n")
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    last = next((i for i in range(len(lines) - 1, -1, -1) if lines[i].strip()), None)
    if first is None or last is None or last <= first:
        return text, False
    m = _FENCE_OPEN.match(lines[first])
    if not m:
        return text, False
    marker, info = m.group(1), m.group(2).strip()
    closing = lines[last].strip()
    if not (closing and set(closing) == {marker[0]} and len(closing) >= len(marker)):
        return text, False
    inner = lines[first + 1:last]
    word = info.split()[0].lower() if info else ""
    if word in ("markdown", "md", "gfm"):
        pass
    elif word == "" and any(_FENCE_OPEN.match(l) for l in inner) \
            and _own_close(lines, first, marker) == last:
        pass                                  # a bare fence that encloses the whole answer
    else:
        return text, False
    body = "\n".join(inner)
    return (body + "\n" if body and not body.endswith("\n") else body), True


def _own_close(lines: list, first: int, marker: str) -> Optional[int]:
    """The line that closes the fence opened at *first*, by CommonMark: the next fence line of
    the same character, at least as long, with no info string. A bare fence that a fence of its
    own closes before the last line is a figure followed by more text, not a wrapper (EI-14)."""
    for i in range(first + 1, len(lines)):
        m = _FENCE_OPEN.match(lines[i])
        if m and m.group(1)[0] == marker[0] and len(m.group(1)) >= len(marker) \
                and not m.group(2).strip():
            return i
    return None


def extract_answer(envelope) -> str:
    """Return the answer of an envelope: its `result`, CRLF made LF, one enclosing wrapper fence
    removed (`unwrap_outer_fence`). A missing or non-text `result` gives an empty string."""
    text = envelope.get("result") if isinstance(envelope, dict) else None
    if not isinstance(text, str):
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unwrap_outer_fence(text)[0]


def served_model(envelope) -> Optional[str]:
    """The model that produced most output tokens of a run, from `modelUsage`; else `model`."""
    if not isinstance(envelope, dict):
        return None
    usage = envelope.get("modelUsage")
    if isinstance(usage, dict) and usage:
        def weight(item):
            v = item[1] if isinstance(item[1], dict) else {}
            return (v.get("outputTokens") or 0, v.get("costUSD") or 0)
        return max(usage.items(), key=weight)[0]
    model = envelope.get("model")
    return model if isinstance(model, str) and model else None


def served_model_ok(envelope, model: str) -> bool:
    """True when the served model is the pinned one, a dated or context-suffixed id included."""
    served = served_model(envelope)
    if not served:
        return False
    return served == model or served.startswith(model + "-20") or served.startswith(model + "[")


def _usage_totals(envelope: dict) -> dict:
    usage = envelope.get("usage") if isinstance(envelope.get("usage"), dict) else {}
    totals = {"input": usage.get("input_tokens") or 0, "output": usage.get("output_tokens") or 0,
              "cache_read": usage.get("cache_read_input_tokens") or 0,
              "cache_creation": usage.get("cache_creation_input_tokens") or 0}
    model_usage = envelope.get("modelUsage")
    if isinstance(model_usage, dict) and model_usage:
        agg = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
        for v in model_usage.values():
            if isinstance(v, dict):
                agg["input"] += v.get("inputTokens") or 0
                agg["output"] += v.get("outputTokens") or 0
                agg["cache_read"] += v.get("cacheReadInputTokens") or 0
                agg["cache_creation"] += v.get("cacheCreationInputTokens") or 0
        if sum(agg.values()):
            totals = agg
    return totals


# --------------------------------------------------------------------------- plan


def eval_dir_name(case: dict) -> str:
    """`eval-<id>-<name>`: `aggregate_benchmark.py` reads the id after the first dash."""
    return f"eval-{case['id']}-{case['name']}"


def run_dir(out_root, case: dict, arm: str, rep: int) -> Path:
    return Path(out_root) / eval_dir_name(case) / arm / f"run-{rep}"


def _run_exists(out_root, case: dict, arm: str, rep: int) -> bool:
    rd = run_dir(out_root, case, arm, rep)
    return rd.is_dir() and any(rd.iterdir())


def _case_names(case: dict) -> set:
    slug = case.get("slug") or Path(case.get("document", "x/x")).parent.name
    return {str(case["id"]), case["name"], slug, slug.split("-")[0]}


def select_cases(evals: dict, tokens=None) -> list:
    """Return the cases *tokens* name, in `evals.json` order. A token is an id, a name, a slug
    (`c8-frontends-services-k33`) or its prefix (`c8`); commas separate tokens."""
    cases = list(evals["evals"])
    if not tokens:
        return cases
    wanted = set()
    for raw in tokens:
        for tok in (t.strip() for t in str(raw).split(",")):
            if not tok:
                continue
            hits = [c["id"] for c in cases if tok in _case_names(c)]
            if not hits:
                raise UsageError(f"unknown case {tok!r}; known ids: "
                                 f"{', '.join(str(c['id']) for c in cases)}")
            wanted.update(hits)
    return [c for c in cases if c["id"] in wanted]


def plan_runs(evals: dict, cases=None, arms=None, reps: int = 1) -> list:
    """Every `(case, arm, rep)` of an invocation, ordered case, arm, rep. Built before anything
    spawns, so `--dry-run` prints the set a real run executes."""
    selected = select_cases(evals, cases)
    chosen = [a for a in ARMS if a in set(arms)] if arms else list(ARMS)
    return [(c, a, r) for c in selected for a in chosen for r in range(1, reps + 1)]


def _check_case(case: dict) -> None:
    missing = [f for f in CASE_FIELDS if f not in case]
    if missing:
        raise InstrumentError(f"case {case.get('id')!r} lacks {', '.join(missing)}")


def prepare_prompts(evals: dict, plan: list, skill_dir=SKILL_DIR) -> tuple:
    """Build every prompt of *plan* once, before any spawn.

    Returns `(prompts, bundles, errors)`: prompts keyed `(case id, arm)` with their texts, hashes
    and the key's kind; bundles keyed by figure kind, with manifest, sha256 and word count; the
    error texts of what could not be built. Every planned case has its key kind checked against
    `evals.json`, whichever arm runs.
    """
    prompts, bundles, errors = {}, {}, []
    for case, arm, _rep in plan:
        key = (case["id"], arm)
        if key in prompts:
            continue
        try:
            _check_case(case)
            kind = case_kind(case, evals)
            base_prompt = case_prompt(case, evals)
        except (InstrumentError, KeyError) as exc:
            errors.append(str(exc))
            prompts[key] = None
            continue
        bundle = None
        if arm == "with_skill":
            if kind not in bundles:
                try:
                    text, files = bundle_for(kind, skill_dir)
                    manifest = bundle_manifest(kind, skill_dir)
                    bundles[kind] = {"text": text, "files": files, "manifest": manifest,
                                     "sha256": _sha256_text(text),
                                     "words": sum(m.get("words", 0) for m in manifest)}
                except InstrumentError as exc:
                    bundles[kind] = {"error": str(exc)}
            bundle = bundles[kind]
            if "error" in bundle:
                errors.append(bundle["error"])
                prompts[key] = None
                continue
        text = (bundle["text"] if bundle else "") + base_prompt
        prompts[key] = {"text": text, "sha256": _sha256_text(text), "bytes": len(text.encode()),
                        "kind": kind, "case_prompt": base_prompt,
                        "case_prompt_sha256": _sha256_text(base_prompt), "bundle": bundle}
    unique = []
    for e in errors:
        if e not in unique:
            unique.append(e)
    return prompts, bundles, unique


# --------------------------------------------------------------------------- budget


def ledger_files(out_root=None, budget_root=None) -> list:
    """The `attempts.jsonl` files whose costs count toward the budget: every ledger below
    `evals/corpus*/`, wherever the out-root lies, every ledger below `budget_root`, and the
    out-root's own ledger. A campaign started outside `evals/` still counts the others' spend
    (EI-17)."""
    found = set()
    for corpus in HERE.glob("corpus*"):
        if corpus.is_dir():
            found.update(corpus.glob("**/attempts.jsonl"))
    if budget_root is not None:
        found.update(Path(budget_root).glob("**/attempts.jsonl"))
    if out_root is not None:
        own = Path(out_root) / "attempts.jsonl"
        if own.is_file():
            found.add(own)
    return sorted({p.resolve() for p in found})


class Spend:
    """Recorded attempt costs and the per-run projection of TASK D18.

    `known` holds, per arm, the sum and the count of attempts with a positive `total_cost_usd`.
    `unknown` counts, per arm, the attempts that report no cost; `total()` counts each of them at
    `per_run(arm)`. `zero` counts attempts that reported a cost of 0.
    """

    def __init__(self, run_cap_usd: float = DEFAULT_RUN_CAP_USD):
        self.run_cap_usd = float(run_cap_usd)
        self.known = {}
        self.unknown = {}
        self.zero = 0

    def add(self, record: dict) -> None:
        """Count one ledger record."""
        arm = str(record.get("arm") or "")
        cost = record.get("total_cost_usd")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost > 0:
            entry = self.known.setdefault(arm, [0.0, 0])
            entry[0] += float(cost)
            entry[1] += 1
        elif record.get("cost_unknown"):
            self.unknown[arm] = self.unknown.get(arm, 0) + 1
        else:
            self.zero += 1

    def mean(self, arm: Optional[str] = None) -> Optional[float]:
        """Mean cost of the attempts of *arm* (all arms when None) with a known cost; else None."""
        rows = [self.known[arm]] if arm is not None and arm in self.known else (
            [] if arm is not None else list(self.known.values()))
        count = sum(r[1] for r in rows)
        return math.fsum(r[0] for r in rows) / count if count else None

    def per_run(self, arm: str) -> float:
        """Projection of one attempt of *arm*: its arm's mean, else the overall mean, else the cap."""
        value = self.mean(arm)
        if value is None:
            value = self.mean()
        return self.run_cap_usd if value is None else value

    def basis(self, arm: str) -> str:
        """What `per_run(arm)` is computed from, for the dry run."""
        if self.mean(arm) is not None:
            return f"mean of {self.known[arm][1]} {arm} attempt(s)"
        if self.mean() is not None:
            return f"mean of {sum(r[1] for r in self.known.values())} attempt(s) of all arms"
        return "--run-cap-usd; no cost recorded yet"

    def known_total(self) -> float:
        return math.fsum(r[0] for r in self.known.values())

    def unknown_count(self) -> int:
        return sum(self.unknown.values())

    def attempts(self) -> int:
        return sum(r[1] for r in self.known.values()) + self.unknown_count() + self.zero

    def total(self) -> float:
        """Known costs plus every attempt without a reported cost at its arm's projection."""
        return self.known_total() + math.fsum(n * self.per_run(arm)
                                              for arm, n in self.unknown.items())


def ledger_spend(files, run_cap_usd: float = DEFAULT_RUN_CAP_USD) -> Spend:
    """Return the `Spend` of the attempts in *files*. A line that does not parse counts as an
    attempt without a reported cost, because a crash can cut the last line of a ledger."""
    spend = Spend(run_cap_usd)
    for path in files:
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                record = None
            spend.add(record if isinstance(record, dict) else {"cost_unknown": True})
    return spend


# --------------------------------------------------------------------------- CLI checks


def check_cli(timeout: float = 60) -> str:
    """Return `claude --version`; raise `InstrumentError` when the CLI is absent or no longer
    lists a flag of `build_command`. Spends no token."""
    exe = shutil.which("claude")
    if not exe:
        raise InstrumentError("claude is not on PATH")
    env = sanitized_env(os.environ)
    try:
        version = subprocess.run([exe, "--version"], env=env, stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=timeout)
        helped = subprocess.run([exe, "--help"], env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InstrumentError(f"claude --version / --help: {exc}") from exc
    gone = missing_flags(helped.stdout + helped.stderr)
    if gone:
        raise InstrumentError(f"claude --help no longer lists {', '.join(gone)}")
    return version.stdout.strip() or version.stderr.strip()


class _CampaignLock:
    """An exclusive lock on `<out-root>/.executor.lock`; released when the process ends."""

    def __init__(self, out_root: Path):
        self.path = out_root / ".executor.lock"
        self.fh = None

    def __enter__(self):
        self.fh = open(self.path, "a+")
        try:
            import fcntl
        except ImportError:  # not POSIX: no second-executor guard
            return self
        try:
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.fh.close()
            raise InstrumentError(f"another executor holds {self.path}") from exc
        return self

    def __exit__(self, *exc):
        if self.fh:
            self.fh.close()
        return False


#: Seconds an executor waits for the budget lock before it stops with exit 2 (SEC2-07). A
#: holder keeps it while it reads the ledgers or appends one record: milliseconds.
BUDGET_LOCK_WAIT_S = 60.0


class _BudgetLock:
    """An exclusive lock that every executor counting the same ledgers takes while it reads the
    spend and admits a run, and while it records an attempt (EI-17). It sits in `evals/corpus/`
    of the user's own checkout, where git ignores `*.lock`, named by the ledgers' root. A
    predictable name in a shared temporary directory let another local user stop or hang a
    campaign (SEC2-07). So the file is opened without following a symlink, it must be a regular
    file of this user, and a lock not taken within `BUDGET_LOCK_WAIT_S` stops the executor: each
    of these raises InstrumentError (exit 2).

    The holder removes the file before it lets go, so no lock file outlives its use (R6). A
    waiter that then holds the removed file locks again on the path: the lock it holds counts
    only while the path names its file."""

    def __init__(self, budget_root=None, wait_s: float = BUDGET_LOCK_WAIT_S):
        root = str(Path(budget_root).resolve()) if budget_root else str(HERE.resolve())
        name = "budget-" + hashlib.sha256(root.encode("utf-8")).hexdigest()[:16]
        self.path = HERE / "corpus" / f".{name}.lock"
        self.wait_s = float(wait_s)
        self.fd = None

    def _open(self) -> int:
        """A descriptor of the lock file: created 0600, never through a symlink, owned by us."""
        flags = (os.O_RDWR | os.O_CREAT | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_CLOEXEC", 0))
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:              # a symlink at the path (ELOOP), or no access
            raise InstrumentError(f"budget lock {self.path}: {exc}") from exc
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid():
            os.close(fd)
            raise InstrumentError(f"budget lock {self.path} is not a regular file of this user; "
                                  f"remove it")
        return fd

    def __enter__(self):
        try:
            import fcntl
        except ImportError:  # not POSIX: one process at a time is the operator's to keep
            return self
        deadline = time.monotonic() + self.wait_s
        while True:
            fd = self._open()
            try:
                while True:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            raise InstrumentError(f"budget lock {self.path} stayed held for "
                                                  f"{self.wait_s:g} s by another process") from None
                        time.sleep(0.005)
                    except OSError as exc:
                        raise InstrumentError(f"budget lock {self.path}: {exc}") from exc
                try:
                    held, named = os.fstat(fd), os.lstat(self.path)
                    same = (held.st_dev, held.st_ino) == (named.st_dev, named.st_ino)
                except FileNotFoundError:
                    same = False
            except BaseException:
                os.close(fd)
                raise
            if same:
                self.fd = fd
                return self
            os.close(fd)                   # the holder before removed it: lock the new file

    def __exit__(self, *exc):
        if self.fd is not None:
            try:
                os.unlink(self.path)       # still held, so no waiter takes the old file for it
            except OSError:
                pass
            os.close(self.fd)
            self.fd = None
        return False


# --------------------------------------------------------------------------- execution


class _Executor:
    """Runs the planned attempts and writes the corpus. Shared counters sit behind one lock."""

    def __init__(self, args, out_root: Path, prompts: dict, cli_version: str, spend: Spend,
                 campaign_id: str, provenance: dict):
        self.args = args
        self.out_root = out_root
        self.prompts = prompts
        self.cli_version = cli_version
        self.campaign_id = campaign_id
        self.provenance = provenance
        self.lock = threading.Lock()
        self.spend = spend
        self.spent_now = 0.0
        self.reserved = 0.0
        self.inflight = 0
        self.stop = None          # instrument stop: exit 2
        self.budget_hit = False
        self.ledger = out_root / "attempts.jsonl"
        self.errors = out_root / "errors.jsonl"
        self.env_removed = removed_env_names()
        self.env_unlisted = unlisted_env_names()
        self.budget_lock = _BudgetLock(getattr(args, "budget_root", None))

    # -- budget -----------------------------------------------------------------------------

    def _reserve(self, arm: str) -> tuple:
        """Admit one attempt of *arm*: `(None, its projection)`, or `(reason, 0.0)`.

        The attempt starts only while the spend, the projections of the attempts in progress and
        its own projection stay within the cap (TASK D18). The spend is read from the ledgers
        again for each admission, so the settled attempts of every executor count (EI-17).
        """
        with self.lock:
            if self.stop:
                return f"stopped: {self.stop}", 0.0
            with self.budget_lock:
                self.spend = ledger_spend(ledger_files(self.out_root,
                                                       getattr(self.args, "budget_root", None)),
                                          self.args.run_cap_usd)
            per_run = self.spend.per_run(arm)
            spent = self.spend.total()
            cap = self.args.budget_usd
            if spent >= cap or spent + self.reserved + per_run > cap:
                self.budget_hit = True
                return (f"budget: {spent:.2f} USD spent, {self.inflight} attempt(s) in progress "
                        f"projected at {self.reserved:.2f} USD, the next {arm} attempt projected "
                        f"at {per_run:.2f} USD, cap {cap:.2f} USD"), 0.0
            self.inflight += 1
            self.reserved += per_run
            return None, per_run

    def _release(self, reservation: float) -> None:
        with self.lock:
            self.inflight -= 1
            self.reserved = max(0.0, self.reserved - reservation)

    def _settle(self, record: dict, reservation: float) -> None:
        with self.lock:
            self.inflight -= 1
            self.reserved = max(0.0, self.reserved - reservation)
            self.spend.add(record)
            cost = record.get("total_cost_usd")
            if isinstance(cost, (int, float)) and cost > 0:
                self.spent_now += float(cost)
            try:
                with self.budget_lock:
                    _append_jsonl(self.ledger, record)
            except InstrumentError as exc:  # the attempt is paid: record it, then admit no more
                _append_jsonl(self.ledger, record)
                self.stop = self.stop or str(exc)

    # -- one run ----------------------------------------------------------------------------

    def run_guarded(self, case: dict, arm: str, rep: int) -> dict:
        """`run`, and on any exception stop every other worker before re-raising."""
        try:
            return self.run(case, arm, rep)
        except BaseException as exc:
            with self.lock:
                self.stop = self.stop or f"{type(exc).__name__}: {exc}"
            raise

    def run(self, case: dict, arm: str, rep: int) -> dict:
        label = f"{eval_dir_name(case)}/{arm}/run-{rep}"
        rd = run_dir(self.out_root, case, arm, rep)
        if rd.exists() and any(rd.iterdir()):
            return {"label": label, "status": "exists"}
        prompt = self.prompts[(case["id"], arm)]
        last_error = None
        attempts = 1 + max(0, self.args.retries)
        for attempt in range(1, attempts + 1):
            refused, reservation = self._reserve(arm)
            if refused:
                status = "stopped" if refused.startswith("stopped") else "budget"
                return {"label": label, "status": status, "error": refused}
            started, t0 = _now(), time.monotonic()
            workdir = None
            try:
                workdir = isolated_workdir()
                envelope = spawn(prompt["text"], self.args.model, self.args.effort, workdir,
                                 self.args.timeout, self.args.run_cap_usd)
            except NotIsolated as exc:
                self._release(reservation)
                with self.lock:
                    self.stop = f"not isolated: {exc}"
                raise
            except BaseException:
                self._release(reservation)
                raise
            finally:
                if workdir:
                    shutil.rmtree(workdir, ignore_errors=True)
            wall_s = time.monotonic() - t0
            if not isinstance(envelope, dict):
                envelope = {"is_error": True, "result": "", "error": "spawn returned no envelope",
                            "cost_unknown": True}
            answer = extract_answer(envelope)
            ok = not envelope.get("is_error") and bool(answer.strip())
            error = None if ok else envelope_error(envelope)
            self._settle({"campaign_id": self.campaign_id, "case_id": case["id"], "arm": arm,
                          "rep": rep, "attempt": attempt, "started_at": started,
                          "total_cost_usd": envelope.get("total_cost_usd"),
                          "cost_unknown": cost_unknown(envelope),
                          "projected_usd": round(reservation, 6),
                          "is_error": not ok, "error": (str(error)[:500] if error else None),
                          "served_model": served_model(envelope),
                          "session_id": envelope.get("session_id"),
                          "provenance_sha256": self.provenance["sha256"]}, reservation)
            if ok:
                return self._finish(case, arm, rep, rd, label, prompt, envelope, answer,
                                    attempt, started, wall_s)
            last_error = str(error)
            with self.lock:
                _append_jsonl(self.errors, {"label": label, "attempt": attempt,
                                            "error": last_error[:2000], "started_at": started})
            if attempt < attempts and BACKOFF_S > 0:
                # exponential: a burst of API errors outlasts a fixed few seconds
                time.sleep(BACKOFF_S * (2 ** (attempt - 1)) * (0.5 + random.random()))
        return {"label": label, "status": "failed", "error": last_error}

    def _finish(self, case, arm, rep, rd, label, prompt, envelope, answer, attempt, started,
                wall_s) -> dict:
        unwrapped = unwrap_outer_fence(
            str(envelope.get("result") or "").replace("\r\n", "\n").replace("\r", "\n"))[1]
        served = served_model(envelope)
        model_ok = served_model_ok(envelope, self.args.model)
        tokens = _usage_totals(envelope)
        duration_ms = envelope.get("duration_ms")
        bundle = prompt["bundle"]
        meta = {
            "schema": "mermaid-run-meta/v2",
            "campaign_id": self.campaign_id,
            "case_id": case["id"], "case_name": case["name"], "arm": arm, "rep": rep,
            "attempt": attempt,
            "model": self.args.model, "effort": self.args.effort,
            "served_model": served, "served_model_ok": model_ok,
            "models_used": sorted((envelope.get("modelUsage") or {}).keys())
            if isinstance(envelope.get("modelUsage"), dict) else [],
            "cli_version": self.cli_version,
            "argv": build_command("<prompt>", self.args.model, self.args.effort,
                                  self.args.run_cap_usd),
            "figure_kind": prompt["kind"],
            "prompt_sha256": prompt["sha256"], "prompt_bytes": prompt["bytes"],
            "case_prompt_sha256": prompt["case_prompt_sha256"],
            "bundle_kind": prompt["kind"] if bundle else None,
            "bundle": bundle["manifest"] if bundle else [],
            "bundle_sha256": bundle["sha256"] if bundle else None,
            "bundle_words": bundle["words"] if bundle else 0,
            "provenance": self.provenance,
            "is_error": bool(envelope.get("is_error")), "subtype": envelope.get("subtype"),
            "error": envelope.get("error"), "num_turns": envelope.get("num_turns"),
            "permission_denials": envelope.get("permission_denials", []),
            "total_cost_usd": envelope.get("total_cost_usd"),
            "usage": tokens, "total_tokens": sum(tokens.values()),
            "duration_ms": duration_ms, "duration_api_ms": envelope.get("duration_api_ms"),
            "session_id": envelope.get("session_id"),
            "answer_chars": len(answer), "unwrapped_outer_fence": unwrapped,
            "env_removed": self.env_removed,
            "env_passed_unlisted": self.env_unlisted,
            "timeout_s": self.args.timeout, "run_cap_usd": self.args.run_cap_usd,
            "started_at": started,
        }
        finished = _now()
        timing = {"total_tokens": sum(tokens.values()),
                  "duration_ms": duration_ms,
                  "total_duration_seconds": round((duration_ms or wall_s * 1000) / 1000.0, 3),
                  "executor_start": started, "executor_end": finished,
                  "executor_duration_seconds": round(wall_s, 3)}
        with self.lock:
            self._write_metadata(case, arm, prompt)
            self._write_run_dir(rd, answer, meta, timing, envelope)
            if not model_ok:
                self.stop = (f"served model {served!r} is not the pinned {self.args.model!r} "
                             f"({label})")
        status = "ok" if model_ok else "invalid_model"
        return {"label": label, "status": status, "chars": len(answer),
                "cost": envelope.get("total_cost_usd")}

    def _write_metadata(self, case, arm, prompt) -> None:
        eval_dir = self.out_root / eval_dir_name(case)
        arm_dir = eval_dir / arm
        arm_dir.mkdir(parents=True, exist_ok=True)
        top = eval_dir / "eval_metadata.json"
        if not top.exists():
            _write_json(top, {"eval_id": case["id"], "eval_name": case["name"],
                              "prompt": prompt["case_prompt"],
                              "prompt_sha256": prompt["case_prompt_sha256"],
                              "figure_kind": prompt["kind"], "lang": case["lang"],
                              "medium": case["medium"], "concern": case["concern"],
                              "control": case["control"]})
        side = arm_dir / "eval_metadata.json"
        if not side.exists():
            bundle = prompt["bundle"]
            _write_json(side, {"eval_id": case["id"], "eval_name": case["name"], "arm": arm,
                               "prompt": prompt["case_prompt"],
                               "case_prompt_sha256": prompt["case_prompt_sha256"],
                               "arm_prompt_sha256": prompt["sha256"],
                               "bundle_kind": prompt["kind"] if bundle else None,
                               "bundle": bundle["manifest"] if bundle else [],
                               "bundle_sha256": bundle["sha256"] if bundle else None})

    def _write_run_dir(self, rd: Path, answer, meta, timing, envelope) -> None:
        """Write into a hidden partial directory, then rename it to `run-<k>` in one step."""
        tmp = Path(tempfile.mkdtemp(prefix=f".partial-{rd.name}-", dir=rd.parent))
        (tmp / "outputs").mkdir()
        with open(tmp / "outputs" / "answer.md", "w", encoding="utf-8") as fh:
            fh.write(answer)
        _write_json(tmp / "run.meta.json", meta)
        _write_json(tmp / "timing.json", timing)
        _write_json(tmp / "envelope.json", envelope)
        if rd.exists():
            if any(rd.iterdir()):
                raise InstrumentError(f"{rd} appeared during the run; the answer stays in {tmp}")
            rd.rmdir()
        os.rename(tmp, rd)


#: Settings besides model and effort that a campaign binds: the arms run in separate
#: invocations and must not differ in how a run is capped, timed, retried or counted (EI-19).
BOUND_SETTINGS = ("run_cap_usd", "timeout_s", "retries", "reps", "cli_version")
#: The bound settings a run record names, for a campaign.json written before they were bound.
_RUN_RECORD_SETTINGS = ("run_cap_usd", "timeout_s", "cli_version")


def bound_settings(args, cli_version: str) -> dict:
    """The values of `BOUND_SETTINGS` of this invocation."""
    return {"run_cap_usd": float(args.run_cap_usd), "timeout_s": float(args.timeout),
            "retries": int(args.retries), "reps": int(args.reps), "cli_version": cli_version}


def _setting_differs(want, got) -> bool:
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        return float(want) != float(got)
    return want != got


def _check_campaign(out_root: Path, args, prompts: dict, plan: list, campaign_id: str,
                    provenance: dict, cli_version: str = "") -> None:
    """One campaign holds one model, one effort, one set of provenance hashes, one prompt per
    case and arm, and one value of each bound setting (`BOUND_SETTINGS`). A campaign.json
    written before the settings were bound is checked against its run records instead."""
    cfile = out_root / "campaign.json"
    mine = bound_settings(args, cli_version)
    if cfile.exists():
        recorded = json.loads(cfile.read_text(encoding="utf-8"))
        for field in ("model", "effort"):
            if recorded.get(field) != getattr(args, field):
                raise InstrumentError(f"{cfile} records {field} {recorded.get(field)!r}; this "
                                      f"invocation asks for {getattr(args, field)!r}")
        if any(k in recorded for k in BOUND_SETTINGS):
            bound = {k: recorded.get(k) for k in BOUND_SETTINGS if k in recorded}
            where = cfile.name
        else:
            bound, where = {}, "its run records"
            for rec in sorted(out_root.glob("eval-*/*/run-*/run.meta.json")):
                meta = json.loads(rec.read_text(encoding="utf-8"))
                for k in _RUN_RECORD_SETTINGS:
                    if meta.get(k) is not None:
                        bound.setdefault(k, meta[k])
        differ = [k for k, v in sorted(bound.items()) if _setting_differs(v, mine[k])]
        if differ:
            raise InstrumentError(
                f"campaign {out_root.name} ran with " + ", ".join(
                    f"{k} {bound[k]!r}" for k in differ) + f" ({where}); this invocation asks "
                f"for " + ", ".join(f"{k} {mine[k]!r}" for k in differ) + "; rerun with the "
                f"campaign's settings or use a new --campaign-id")
        files = (recorded.get("provenance") or {}).get("files")
        if files is not None and files != provenance["files"]:
            changed = sorted(k for k in set(files) | set(provenance["files"])
                             if files.get(k) != provenance["files"].get(k))
            raise InstrumentError(f"{cfile} was started under other provenance hashes "
                                  f"({', '.join(changed)}); use a new --campaign-id")
    for case, arm, _rep in plan:
        prompt = prompts[(case["id"], arm)]
        eval_dir = out_root / eval_dir_name(case)
        top = eval_dir / "eval_metadata.json"
        if top.exists():
            sha = json.loads(top.read_text(encoding="utf-8")).get("prompt_sha256")
            if sha != prompt["case_prompt_sha256"]:
                raise InstrumentError(f"the case prompt of {eval_dir.name} differs from the one "
                                      f"this campaign started with; use a new --campaign-id")
        side = eval_dir / arm / "eval_metadata.json"
        if side.exists():
            sha = json.loads(side.read_text(encoding="utf-8")).get("arm_prompt_sha256")
            if sha != prompt["sha256"]:
                raise InstrumentError(f"the {arm} prompt of {eval_dir.name} differs from the one "
                                      f"this campaign started with; use a new --campaign-id")
    if not cfile.exists():
        _write_json(cfile, dict({"campaign_id": campaign_id, "model": args.model,
                                 "effort": args.effort, "created": _now(),
                                 "evals_sha256": _sha256_file(args.evals),
                                 "provenance": provenance,
                                 "removed_env_vars": list(REMOVED_ENV_VARS)}, **mine))


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_evals.py",
        description="Run the A/B campaign of mermaid-authoring-guidelines "
                    "(the only script of the evaluation that spends tokens)")
    p.add_argument("--evals", default=str(EVALS_PATH), help="evals.json to run")
    p.add_argument("--cases", action="append",
                   help="case id, name or slug; repeatable or comma-separated (default: all)")
    p.add_argument("--arm", action="append", dest="arms", choices=ARMS,
                   help="arm to run; repeatable (default: both)")
    p.add_argument("--reps", type=int, default=None,
                   help="repetitions per case and arm; odd (default: evals.json campaign.reps)")
    p.add_argument("--jobs", type=int, default=1, help="concurrent runs (default 1)")
    p.add_argument("--model", default=None,
                   help="model id (default: evals.json campaign.model)")
    p.add_argument("--effort", default=None, choices=EFFORTS,
                   help="effort level (default: evals.json campaign.effort)")
    p.add_argument("--campaign-id",
                   help="campaign directory name under evals/corpus/; required for a real run "
                        "unless --out-root is given")
    p.add_argument("--out-root", help="campaign directory (default evals/corpus/<campaign-id>)")
    p.add_argument("--budget-usd", type=float, default=None,
                   help="cap on the summed cost of every recorded attempt "
                        "(default: evals.json campaign.budget_usd)")
    p.add_argument("--budget-root",
                   help="directory whose attempts.jsonl files count toward the budget "
                        "(default: evals/corpus*/ when the out-root is under evals/)")
    p.add_argument("--run-cap-usd", type=float, default=DEFAULT_RUN_CAP_USD,
                   help="--max-budget-usd passed to each claude run, and the projection of a run "
                        "before any cost is recorded (default 5)")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S,
                   help="seconds per attempt (default 1200)")
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                   help="further attempts after a failed one (default 1)")
    p.add_argument("--skill-dir", default=str(SKILL_DIR),
                   help="skill directory whose SKILL.md routes the bundle")
    p.add_argument("--dry-run", action="store_true",
                   help="print the commands, bundles, provenance state and budget projection; "
                        "spawn nothing")
    return p


def _parse(argv) -> argparse.Namespace:
    p = build_parser()
    p.exit_on_error = False
    try:
        return p.parse_args(argv)
    except argparse.ArgumentError as exc:
        p.print_usage(sys.stderr)
        raise UsageError(str(exc)) from exc


def _validate(args, evals: dict) -> None:
    campaign = evals.get("campaign", {}) if isinstance(evals.get("campaign"), dict) else {}
    args.model = args.model or campaign.get("model") or DEFAULT_MODEL
    args.effort = args.effort or campaign.get("effort") or DEFAULT_EFFORT
    args.reps = args.reps if args.reps is not None else int(campaign.get("reps", DEFAULT_REPS))
    if args.budget_usd is None:
        args.budget_usd = float(campaign.get("budget_usd", DEFAULT_BUDGET_USD))
    if args.effort not in EFFORTS:
        raise UsageError(f"--effort must be one of {', '.join(EFFORTS)}")
    if args.reps < 1 or args.reps % 2 == 0:
        raise UsageError("--reps must be odd and at least 1, so each case has a median run")
    if args.jobs < 1:
        raise UsageError("--jobs must be at least 1")
    if args.retries < 0:
        raise UsageError("--retries must be 0 or more")
    # nan and inf pass `<= 0`, and a nan or inf cap admits every run (SEC2-04)
    if not all(math.isfinite(v) and v > 0 for v in (args.budget_usd, args.run_cap_usd,
                                                     args.timeout)):
        raise UsageError("--budget-usd, --run-cap-usd and --timeout must be finite and positive")
    if args.campaign_id is not None and (not _CAMPAIGN_ID_RE.fullmatch(args.campaign_id)
                                         or ".." in args.campaign_id):
        raise UsageError("--campaign-id takes letters, digits, '.', '_' and '-' only")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:\[\]-]*", args.model):
        raise UsageError(f"--model {args.model!r} is not a model id")


def _out_root(args) -> Optional[Path]:
    if args.out_root:
        return Path(args.out_root)
    if args.campaign_id:
        return CORPUS_DIR / args.campaign_id
    return None


def _print_plan(args, evals, plan, prompts, bundles, errors, out_root, ledgers,
                spend: Spend) -> None:
    w = sys.stdout.write
    w("run_evals.py dry run: nothing is spawned\n")
    w(f"evals:      {args.evals}  sha256 {_sha256_file(args.evals)}\n")
    tpl = _base_dir(evals) / evals.get("prompt_template", "prompts/task-template.md")
    if tpl.is_file():
        w(f"template:   {tpl}  sha256 {_sha256_file(tpl)}\n")
    record, problem = provenance_state(evals)
    if record:
        w(f"provenance: {PROVENANCE_NAME} sha256 {record['sha256']}; "
          f"{len(record['files'])} file(s) match\n")
    else:
        w(f"provenance: a paid run exits 2: {problem}\n")
    w(f"campaign:   {args.campaign_id or '<campaign-id>'}   out-root: "
      f"{out_root if out_root else CORPUS_DIR / '<campaign-id>'}\n")
    w(f"model: {args.model}   effort: {args.effort}   reps: {args.reps}   jobs: {args.jobs}   "
      f"retries: {args.retries}   timeout: {args.timeout:g} s\n")
    unknown = spend.unknown_count()
    w(f"budget:     cap {args.budget_usd:.2f} USD; spent {spend.total():.2f} USD over "
      f"{spend.attempts()} attempt(s) in {len(ledgers)} attempts.jsonl file(s)"
      + (f", {unknown} without a reported cost" if unknown else "") + "\n")
    if unknown:     # information only; the stop rule counts them at the mean (README, D18)
        w(f"            at most {spend.known_total() + unknown * args.run_cap_usd:.2f} USD if "
          f"each attempt without a reported cost spent the run cap of "
          f"{args.run_cap_usd:g} USD\n")
    for arm in ARMS:
        w(f"            {arm} run projected at {spend.per_run(arm):.2f} USD "
          f"({spend.basis(arm)})\n")
    todo = [(c, a, r) for c, a, r in plan if not (out_root and _run_exists(out_root, c, a, r))]
    projected = math.fsum(spend.per_run(a) for _c, a, _r in todo)
    w(f"            this plan starts {len(todo)} run(s), projected {projected:.2f} USD; the "
      f"stop rule admits a run only within the cap\n")
    w("command:    " + shlex.join(build_command("<prompt>", args.model, args.effort,
                                                args.run_cap_usd)) + "\n")
    w("            the prompt is one argv element; stdin is closed; cwd is a fresh mkdtemp "
      "directory\n")
    w(f"env:        removes the {len(REMOVED_ENV_VARS)} names of REMOVED_ENV_VARS: "
      + ", ".join(REMOVED_ENV_VARS) + "\n")
    removed = removed_env_names()
    w("            removed from this environment: " + (", ".join(removed) or "none") + "\n")
    auth = [n for n in AUTH_ENV_VARS if n in os.environ]
    w("            authentication variables kept: " + (", ".join(auth) or "none set") + "\n")
    w("            passed, on no list: " + (", ".join(unlisted_env_names()) or "none") + "\n")
    w("cli:        a real run checks every flag above against `claude --help` first\n")
    try:
        words = routing_words(args.skill_dir)
        skill_words = word_count(_read(Path(args.skill_dir) / "SKILL.md"))
        w(f"routing:    {ROUTING_ANCHOR} of SKILL.md; SKILL.md {skill_words} words "
          f"(limit {SKILL_WORD_LIMIT})\n")
        for kind, value in words.items():
            if isinstance(value, int):
                verdict = "within" if value < BUNDLE_WORD_LIMIT else "OVER"
                w(f"            {kind:<10} {value:>6} words, {verdict} the limit of "
                  f"{BUNDLE_WORD_LIMIT} (TASK R1.5)\n")
            else:
                w(f"            {kind:<10} {value}\n")
    except (InstrumentError, OSError, UnicodeDecodeError) as exc:
        w(f"routing:    {exc}\n")
    for kind in sorted(bundles):
        bundle = bundles[kind]
        cases = sorted({c["id"] for c, a, _r in plan if a == "with_skill"
                        and (prompts.get((c["id"], a)) or {}).get("kind") == kind})
        w(f"bundle {kind} (with_skill; cases {', '.join(str(c) for c in cases) or '-'}):\n")
        if "error" in bundle:
            w(f"  {bundle['error']}\n")
            continue
        for item in bundle["manifest"]:
            w(f"  {item['path']:<40} {item['bytes']:>7} B {item['words']:>6} words  "
              f"sha256 {item['sha256']}\n")
        w(f"  block sha256 {bundle['sha256']}  ({len(bundle['text'].encode())} B, "
          f"{bundle['words']} words)\n")
    w(f"plan ({len(plan)} run{'s' if len(plan) != 1 else ''}):\n")
    for case, arm, rep in plan:
        label = f"{eval_dir_name(case)}/{arm}/run-{rep}"
        prompt = prompts.get((case["id"], arm))
        if not prompt:
            w(f"  {label}   prompt not built\n")
            continue
        w(f"  {label}   kind {prompt['kind']}   prompt {prompt['bytes']} B sha256 "
          f"{prompt['sha256'][:16]}   case prompt sha256 {prompt['case_prompt_sha256'][:16]}\n")
    for e in errors:
        w(f"instrument error: {e}\n")


def main(argv: Optional[list] = None) -> int:
    try:
        args = _parse(argv)
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except SystemExit as exc:  # --help
        return EXIT_OK if not exc.code else EXIT_USAGE
    if not os.path.isfile(args.evals):
        print(f"usage error: no eval file at {args.evals}", file=sys.stderr)
        return EXIT_USAGE
    try:
        evals = load_evals(args.evals)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"instrument error: {args.evals}: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    try:
        _validate(args, evals)
        plan = plan_runs(evals, args.cases, args.arms, args.reps)
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except (KeyError, TypeError) as exc:
        print(f"instrument error: evals.json: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    if not plan:
        print("usage error: the selection plans no run", file=sys.stderr)
        return EXIT_USAGE

    prompts, bundles, errors = prepare_prompts(evals, plan, args.skill_dir)
    out_root = _out_root(args)
    ledgers = ledger_files(out_root, args.budget_root)
    spend = ledger_spend(ledgers, args.run_cap_usd)

    if args.dry_run:
        _print_plan(args, evals, plan, prompts, bundles, errors, out_root, ledgers, spend)
        return EXIT_INSTRUMENT if errors else EXIT_OK

    if out_root is None:
        print("usage error: a real run needs --campaign-id or --out-root", file=sys.stderr)
        return EXIT_USAGE
    if errors:
        for e in errors:
            print(f"instrument error: {e}", file=sys.stderr)
        return EXIT_INSTRUMENT
    try:
        provenance = check_provenance(evals)
    except InstrumentError as exc:
        print(f"instrument error: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    if spend.total() >= args.budget_usd:
        print(f"budget: {spend.total():.2f} USD spent already, cap {args.budget_usd:.2f} USD; "
              f"no run started", file=sys.stderr)
        return EXIT_RUN_FAILED
    print(f"budget: cap {args.budget_usd:.2f} USD; {spend.total():.2f} USD spent before this "
          f"invocation")                   # a cap other than the campaign's shows (SEC2-04)
    campaign_id = args.campaign_id or out_root.name
    try:
        cli_version = check_cli()
        probe = isolated_workdir()
        shutil.rmtree(probe, ignore_errors=True)
        out_root.mkdir(parents=True, exist_ok=True)
        with _CampaignLock(out_root):
            _check_campaign(out_root, args, prompts, plan, campaign_id, provenance, cli_version)
            return _execute(args, out_root, prompts, plan, cli_version, spend, campaign_id,
                            provenance)
    except NotIsolated as exc:
        print(f"not isolated: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    except InstrumentError as exc:
        print(f"instrument error: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    except Exception:  # an executor defect: report it as a broken instrument, never as a pass
        traceback.print_exc()
        return EXIT_INSTRUMENT


def _execute(args, out_root, prompts, plan, cli_version, spend, campaign_id, provenance) -> int:
    ex = _Executor(args, out_root, prompts, cli_version, spend, campaign_id, provenance)
    results = []

    def report(res):
        results.append(res)
        status = res["status"]
        if status == "ok":
            cost = res.get("cost")
            cost_s = f"  {cost:.4f} USD" if isinstance(cost, (int, float)) else ""
            print(f"  {res['label']}: ok, {res['chars']} chars{cost_s}")
        elif status == "exists":
            print(f"  {res['label']}: exists, not run again")
        else:
            print(f"  {res['label']}: {status.upper()} {res.get('error') or ''}".rstrip())

    try:
        if args.jobs == 1:
            for case, arm, rep in plan:
                report(ex.run_guarded(case, arm, rep))
        else:
            pool = concurrent.futures.ThreadPoolExecutor(args.jobs)
            try:
                futures = [pool.submit(ex.run_guarded, c, a, r) for c, a, r in plan]
                for fut in concurrent.futures.as_completed(futures):
                    report(fut.result())
            finally:
                pool.shutdown(wait=True, cancel_futures=True)
    except NotIsolated as exc:
        print(f"not isolated: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT
    except InstrumentError as exc:
        print(f"instrument error: {exc}", file=sys.stderr)
        return EXIT_INSTRUMENT

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"\n{len(plan)} planned: " + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())))
    unknown = ex.spend.unknown_count()
    print(f"spent in this invocation: {ex.spent_now:.2f} USD; campaign spend "
          f"{ex.spend.total():.2f} of {args.budget_usd:.2f} USD"
          + (f" ({unknown} attempt(s) without a reported cost, counted at the mean)"
             if unknown else ""))
    if ex.stop:
        print(f"instrument stop: {ex.stop}", file=sys.stderr)
        return EXIT_INSTRUMENT
    if any(r["status"] in ("failed", "budget", "stopped") for r in results):
        return EXIT_RUN_FAILED
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
