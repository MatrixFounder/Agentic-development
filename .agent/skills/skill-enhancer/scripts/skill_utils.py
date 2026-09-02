#!/usr/bin/env python3
import argparse
import atexit
import codecs
import json
import os
import sys
import re

class VanillaYamlParser:
    """
    Zero-Dependency YAML Parser for strict subset of YAML.
    Supports:
    - Key-Value pairs (key: value)
    - Lists (- item)
    - Basic Nesting (2-3 levels)
    - Quoted strings ("foo", 'bar')
    - Comments (#)
    """
    def parse(self, content):
        lines = content.splitlines()
        root = {}
        stack = [(root, -1)]  # (container, indent_level)
        last_key = None 
        in_block_scalar = False
        block_scalar_key = None
        block_scalar_indent = -1
        block_scalar_lines = []
        block_scalar_type = None # '>' or '|'
        
        for line in lines:
            raw_line = line.rstrip()
            stripped = raw_line.lstrip()
            
            # Skip empty or comments
            if not in_block_scalar and (not stripped or stripped.startswith('#')):
                continue
                
            indent = len(raw_line) - len(stripped)
            
            # Handle block scalar content
            if in_block_scalar:
                if not raw_line.strip():
                    block_scalar_lines.append("")
                    continue
                if indent <= block_scalar_indent:
                    # End of block scalar
                    content_str = "\n".join(block_scalar_lines) if block_scalar_type.startswith('|') else " ".join(l.strip() for l in block_scalar_lines if l.strip())
                    current_container, _ = stack[-1]
                    current_container[block_scalar_key] = content_str
                    in_block_scalar = False
                    block_scalar_lines = []
                else:
                    block_scalar_lines.append(raw_line[block_scalar_indent+1:]) # strip up to indent
                    continue
            line_content = stripped.split('#')[0].strip()
            
            # Hierarchy management
            while len(stack) > 1 and indent <= stack[-1][1]:
                stack.pop()
            
            current_container, _ = stack[-1]

            # Case 1: List Item "- value" or "- key: value"
            if line_content.startswith('- '):
                value = line_content[2:].strip()
                processed_val = self._parse_value(value)
                
                # Check for "Empty Dict -> List" conversion
                if isinstance(current_container, dict) and len(current_container) == 0:
                    if len(stack) > 1:
                        parent, _ = stack[-2]
                        target_k = None
                        if isinstance(parent, dict):
                            for k, v in parent.items():
                                if v is current_container:
                                    target_k = k
                                    break
                        
                        if target_k:
                            # Swap dict for list
                            new_list = []
                            parent[target_k] = new_list
                            
                            # Capture old indent (of the dict/key) from stack before popping
                            _, old_indent = stack[-1]
                            stack.pop()
                            # Use old_indent so list container logic works for siblings
                            stack.append((new_list, old_indent))
                            current_container = new_list
                
                if isinstance(current_container, list):
                    current_container.append(processed_val)
                    if isinstance(processed_val, dict):
                         stack.append((processed_val, indent))
                
                # Fallback: If we popped the list container, append to parent
                elif isinstance(current_container, dict) and last_key:
                    if last_key not in current_container or not isinstance(current_container[last_key], list):
                        current_container[last_key] = []
                    
                    if isinstance(processed_val, dict) and hasattr(processed_val, 'items'):
                         # Support "- key: val" style
                         # processed_val is already dict from _parse_value
                         current_container[last_key].append(processed_val)
                         # Push with current indent so keys inside match scope
                         stack.append((processed_val, indent))
                    else:
                        current_container[last_key].append(processed_val)
                continue

            # Case 2: Key-Value "key: value" or Parent "key:"
            if ':' in line_content:
                key_part, val_part = line_content.split(':', 1)
                key = key_part.strip()
                val = val_part.strip()
                
                if not val:
                    new_container = {} 
                    current_container[key] = new_container
                    last_key = key
                    stack.append((new_container, indent))
                elif val.startswith('>') or val.startswith('|'):
                    in_block_scalar = True
                    block_scalar_key = key
                    block_scalar_indent = indent
                    block_scalar_type = val
                else:
                    current_container[key] = self._parse_value(val)
                    last_key = key
                continue

        # Handle trailing block scalar at EOF
        if in_block_scalar:
             content_str = "\n".join(block_scalar_lines) if block_scalar_type.startswith('|') else " ".join(l.strip() for l in block_scalar_lines if l.strip())
             current_container, _ = stack[-1]
             current_container[block_scalar_key] = content_str

        return root

    def _parse_value(self, val_str):
        val_str = val_str.strip()
        
        # Check for inline dict "key: val" (for list items)
        # Only support simple keys to avoid false positives with text containing colons
        if ':' in val_str and not (val_str.startswith('"') or val_str.startswith("'")):
            k, v = val_str.split(':', 1)
            k = k.strip()
            # Simple heuristic: valid key shouldn't have brackets or extensive spaces
            # If k has spaces but is short, might be ok? 
            # Safest: prevent keys with [], (), or multiple words unless strictly needed.
            if re.match(r'^[\w\-\.]+$', k): 
                 return {k: self._parse_value(v)}
            
        # Quotes
        if (val_str.startswith('"') and val_str.endswith('"')) or \
           (val_str.startswith("'") and val_str.endswith("'")):
            return val_str[1:-1]
            
        # Booleans / Nulls
        if not isinstance(val_str, str):
            return val_str

        val_lower = val_str.lower()
        if val_lower == 'true': return True
        if val_lower == 'false': return False
        if val_lower == 'null': return None
        
        # Numbers
        if val_str.isdigit(): return int(val_str)
        try:
            return float(val_str)
        except ValueError:
            pass
            
        return val_str

def load_config(project_root="."):
    """
    Loads configuration by merging:
    1. Bundled Defaults (skill_standards_default.yaml)
    2. Project Overlay (.agent/rules/skill_standards.yaml)
    
    Auto-detects project_root if not provided.
    """
    parser = VanillaYamlParser()
    config = {}
    
    # 0. Resolve Proj Root (Search Upwards)
    # Treat project_root as "start_dir"
    search_dir = os.path.abspath(project_root)
    found_root = None
    
    current = search_dir
    while True:
        if os.path.exists(os.path.join(current, ".agent")) or \
           os.path.exists(os.path.join(current, ".git")):
            found_root = current
            break
        parent = os.path.dirname(current)
        if parent == current: # Reached fs root
            break
        current = parent
        
    # Use found root if available, else fallback to original input (likely just CWD)
    final_root = found_root if found_root else project_root
    
    # 1. Load Defaults
    script_dir = os.path.dirname(os.path.abspath(__file__))

    default_path = os.path.join(script_dir, "skill_standards_default.yaml")
    
    if os.path.exists(default_path):
        try:
            # encoding= is load-bearing twice over. Without it the codec comes
            # from the process locale, and this file carries non-ASCII (an em
            # dash on line 49): under LC_ALL=C the read raised
            # UnicodeDecodeError, the bare `except` below swallowed it, and
            # load_config() returned {} at exit 0 -- every default silently
            # gone. The warning went to stdout on top of that, landing ahead of
            # analyze_gaps.py --json's document and making it unparseable.
            with open(default_path, 'r', encoding='utf-8') as f:
                config = parser.parse(f.read())
        except Exception as e:
            # stderr, never stdout: stdout is a machine-readable channel here.
            print(f"Warning: Failed to load bundled defaults: {e}", file=sys.stderr)
    
    # 2. Load Project Overlay
    project_config_path = os.path.join(final_root, ".agent", "rules", "skill_standards.yaml")
    if os.path.exists(project_config_path):
        try:
            with open(project_config_path, 'r', encoding='utf-8') as f:
                overlay = parser.parse(f.read())
                _deep_merge(config, overlay)
        except Exception as e:
            print(f"Warning: Failed to load project config at {project_config_path}: {e}",
                  file=sys.stderr)
            
    return config

def _deep_merge(base, overlay):
    """Recursive merge of dicts."""
    for k, v in overlay.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


# ---------------------------------------------------------------------------
# stdout JSON channel
#
# Duplicated verbatim in the sibling tooling skills (skill-creator and
# skill-enhancer carry it in their own `skill_utils.py`, skill-validator in
# `validate.py`, skill-auto-improve in `common.py`). The duplication is
# deliberate: each skill must be installable and runnable in isolation,
# including as a packaged `.skill` archive, so no skill imports a helper from
# another. There is no diff -q gate on these copies -- unlike the office
# skills' `_errors.py`, they are not a declared replication unit.
# ---------------------------------------------------------------------------

def abandon_stdout():
    """Point a dead stdout's file descriptor at os.devnull. Best effort.

    Call this after a BrokenPipeError. Without it the interpreter flushes the
    same dead fd again while shutting down: it prints "Exception ignored while
    flushing sys.stdout" on stderr and **replaces the exit status with 120**,
    so the process contradicts the verdict it just returned. A stream with no
    real fd (a test's StringIO, a wrapper's proxy object) has nothing to
    redirect and needs nothing, hence the swallowed exceptions.
    """
    try:
        fd = sys.stdout.fileno()
    except (OSError, ValueError, AttributeError):
        return
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
    except OSError:
        return
    try:
        os.dup2(devnull, fd)
    except OSError:
        pass
    finally:
        os.close(devnull)


def emit_text(text):
    """Write `text` plus a newline to stdout and flush, surviving a dead pipe.

    Returns True when the line reached stdout, False when the sink was already
    gone. See `emit_json` for the two failure modes this exists to close; this
    is the same contract for a stdout payload that is not JSON (e.g. a bare
    digest).
    """
    if sys.stdout is None:
        return False
    line = text + "\n"
    # No degradation here. This helper's contract is "the line reached stdout",
    # and a non-ASCII character used to break it by raising rather than by
    # returning False -- but the repair belongs to the stream, not to every
    # writer: `install_human_channel()` puts the ASCII-fallback handler on
    # stdout once, and every write in the process inherits it.
    try:
        sys.stdout.write(line)
        sys.stdout.flush()
    except BrokenPipeError:
        abandon_stdout()
        return False
    return True


def emit_json(payload, indent=2):
    """Write `payload` to stdout as one JSON document, then flush.

    Replaces `print(json.dumps(payload, indent=2))`, which has two measured
    failure modes.

    **A reader that is already gone.** Payload size is not the gate: a reader
    that disappeared before the write raises EPIPE for a 65-byte document just
    as readily as for a 500 KB one (measured on CPython 3.14.4 / macOS: the
    immutability gate's 83-byte `{"ok": ..., "reason": ...}` line, written into
    a pipe whose read end was already closed, turned `return 1` into exit 120).
    Size only decides *which way* a bare `print()` fails. Measured on this
    machine, with the reader gone before the write: at 131_071 payload bytes
    and below the text stays in `sys.stdout`'s buffer, `print()` returns
    normally, and only the interpreter's shutdown flush hits the dead fd --
    which prints "Exception ignored while flushing sys.stdout" on stderr and
    replaces the exit status with 120; at 131_072 bytes and above the write
    itself raises and the traceback escapes with exit 1. Both land in
    `emit_text`'s `except` arm, where `abandon_stdout()` leaves the shutdown
    flush nothing to fail on, so the caller's own exit code survives.

    (A reader that is merely *slow* rather than gone -- `... | head -c 20` --
    reaches those same two modes, but only once the document outgrows the
    ~64 KB pipe buffer. That is why the tests use the already-gone reader: it
    takes payload size out of the contract, so a shrinking fixture cannot turn
    a real regression green.)

    **fd 1 closed before the process started** (`prog >&-`): CPython sets
    `sys.stdout` to None and makes `print()` a silent no-op, so the caller sees
    exit 0 and no document. Detected here and reported through the return value
    rather than raising AttributeError.

    `json.dumps` runs to completion before anything is written, so a reader
    gets a whole document or none of it, never one truncated mid-serialization.

    `ensure_ascii` keeps its default, so the document is pure ASCII and the
    text layer's codec (`PYTHONIOENCODING`, then the process locale) can
    neither alter these bytes nor abort mid-write on them. A caller that needs
    non-ASCII output must move to a byte-level write (as
    `_errors.write_json_stdout` does in the office skills), not merely flip
    `ensure_ascii`.

    Returns True when the document reached stdout, False when the sink was
    already gone. The caller's exit path runs unchanged either way.
    """
    return emit_text(json.dumps(payload, indent=indent))


# --------------------------------------------------------------------- #
# The HUMAN channel — reports, progress, --help
# --------------------------------------------------------------------- #
#
# The machine helpers above must ignore the caller's locale: JSON is UTF-8 by
# RFC 8259 §8.1. Prose is the opposite — it must OBEY the caller's codec,
# because UTF-8 written into a terminal that declared cp1252 is mojibake, not
# robustness.
#
# Until this existed it obeyed by dying. stderr is opened
# errors="backslashreplace" and survives; stdout gets "surrogateescape" (or
# "strict" under an explicit PYTHONIOENCODING), and NEITHER can represent an
# em dash — surrogateescape rescues lone surrogates and nothing else. So one
# `—` or `✓` in a report, or in an argparse `help=` string, took the whole
# command down.
#
# The fix belongs to the STREAM, not to the call sites. `codecs.register_error`
# is the documented extension point for exactly this question — "what should
# happen to a character this codec cannot represent?" — and once the handler
# is on stdout it covers `print`, argparse's own `file.write`, a bare
# `sys.stdout.write` deep inside a renderer, and any third-party write in the
# same process. Nothing to remember at the call site, because there is no call
# site to remember.
#
# The first version of this fix did the opposite: a `say()` wrapper, a
# `HumanArgumentParser` subclass and a stream shim, ~157 lines copied into
# every skill, with every `print` rewritten to match. It worked, and it was
# the wrong shape — mutation testing showed a forgotten `print` still slipped
# through, and the duplicated block was mechanism rather than data. What is
# left below is data (the table) plus fifteen lines that hand it to CPython.
#
# Issue: docs/issues/human-cli-output-locale-class.md.

#: Name under which the handler is registered process-wide. Also usable as an
#: `errors=` argument anywhere: `text.encode("ascii", HUMAN_ERRORS)` gives
#: exactly what a report would look like under that codec, which is how the
#: tests state their expectations without restating the table.
HUMAN_ERRORS = "human_channel.asciify"

#: ASCII spellings for the decoration these reports print. A FALLBACK table,
#: not a transliterator: consulted only for characters the caller's codec has
#: already rejected, and anything missing from it degrades to a
#: `backslashreplace` escape rather than being dropped.
_ASCII_FALLBACK = {
    "—": "--", "–": "-", "…": "...", "→": "->", "←": "<-",
    "✓": "+", "✔": "+", "✗": "x", "✘": "x", "×": "x",
    "⚠": "!", "❌": "x", "✅": "+", "❗": "!", "•": "*", "§": "S",
    "±": "+/-", "≥": ">=", "≤": "<=", "≠": "!=", "°": " deg",
    "‘": "'", "’": "'", "“": '"', "”": '"', " ": " ",
    # U+FE0F / U+FE0E only select an emoji's presentation; they carry no
    # meaning of their own. `⚠️` is U+26A0 U+FE0F, so mapping just the base
    # glyph left the selector behind and the report read `!️`. Dropping
    # them is the whole fix — the base character already says it.
    "️": "", "︎": "",
}


def _asciify(exc):
    """Spell an unencodable run in ASCII instead of letting it kill the write.

    The codec calls this once per unencodable RUN, not once per character:
    `exc.object[exc.start:exc.end]` can be several characters long, hence the
    loop. Degradation stays per character so a codec keeps everything it can
    carry — under cp1251 `доклад — ✓` keeps the Cyrillic AND the em dash and
    only the check mark moves.

    Anything the table does not know falls back to `backslashreplace`, which
    is what stderr has always done and precisely why stderr never crashed.

    Re-raises anything that is not an encode error. A decode error reaching
    here would mean the handler was installed on a readable stream, where
    guessing would corrupt input rather than tidy output.
    """
    if not isinstance(exc, UnicodeEncodeError):
        raise exc
    spelled = []
    for ch in exc.object[exc.start:exc.end]:
        replacement = _ASCII_FALLBACK.get(ch)
        if replacement is None:
            # Escaped against ASCII, NOT against `exc.encoding`. For every
            # charmap codec -- cp1251, cp1252, latin-1, cp850, cp932 -- the
            # exception reports `exc.encoding == "charmap"`, the literal
            # string, not the codec's name. Re-encoding through *that* does
            # not raise: the bare `charmap` codec falls back to Latin-1 and
            # hands back the RAW BYTE, so `é` came out of cp1251 as b"\xe9"
            # and the following decode blew up. ASCII escapes are also the
            # only universally safe answer -- the character is here precisely
            # because the caller's codec rejected it.
            replacement = ch.encode("ascii", "backslashreplace").decode("ascii")
        spelled.append(replacement)
    return "".join(spelled), exc.end


codecs.register_error(HUMAN_ERRORS, _asciify)


def _quiet_a_dead_stdout():
    """Drain stdout at exit, and if it is already gone, point fd 1 at devnull.

    Registered by `install_human_channel`, and the second half of the exit-code
    contract. `line_buffering` makes the CLI's own `except BrokenPipeError`
    handler see the failure and return its verdict — but the interpreter then
    flushes the SAME dead fd again during finalization, prints "Exception
    ignored while flushing sys.stdout" on stderr, and replaces that verdict
    with 120. Measured: `install_components.py` with no reader at all printed
    its own broken-pipe line, returned 1, and exited 120.

    atexit callbacks run before that final flush, so draining here leaves it
    nothing to fail on. A stream with no real fd (a test's StringIO) has
    nothing to redirect and needs nothing, hence the swallowed exceptions.
    """
    try:
        sys.stdout.flush()
    except (BrokenPipeError, ValueError, OSError):
        try:
            fd = sys.stdout.fileno()
        except (OSError, ValueError, AttributeError):
            return
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
        except OSError:
            return
        try:
            os.dup2(devnull, fd)
        finally:
            os.close(devnull)
    except AttributeError:
        pass


def install_human_channel(*streams):
    """Point stdout's and stderr's error handler at `_asciify`.

    Call once, early in `main()` — NOT at import. Registering the handler
    above is inert, but `reconfigure` mutates a process-wide stream, and a
    module that does that on import imposes it on everything that merely
    imports the module.

    stderr is included even though it never crashed: its `backslashreplace`
    turns an em dash into the six characters `\\u2014`, and `--` is strictly
    better for the same cost.

    `line_buffering` is set for a second, unrelated reason, and it matters:
    piped stdout is BLOCK-buffered, so `report | head` surfaces the dead reader
    during interpreter shutdown, where CPython prints "Exception ignored while
    flushing sys.stdout" and **replaces the exit status with 120** — a command
    contradicting the verdict it just gave. Line-buffered, the write itself
    raises BrokenPipeError inside `main()`, where the CLI's own handler sees
    it. This also just restores the behaviour stdout already has on a terminal;
    only redirection took it away.

    Failure is silent by design. A replaced stdout — a test's `StringIO`, a
    capture proxy, `prog >&-` leaving `sys.stdout` as None — has no
    `reconfigure` to call, and none of that is a reason to fail a report.
    """
    if not streams:
        atexit.register(_quiet_a_dead_stdout)
    for stream in streams or (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors=HUMAN_ERRORS, line_buffering=True)
        except (AttributeError, ValueError, OSError):
            pass


if __name__ == "__main__":
    cfg = load_config()
    emit_json(cfg)
