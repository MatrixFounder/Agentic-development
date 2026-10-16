"""The header of the parse model: the skill's paths, the fence specs, the negative-fence
marker and its roots, `negative_allowed` and `load_notation` (TASK 124)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional
SKILL_DIR = Path(__file__).resolve().parents[2]
NOTATION_PATH = SKILL_DIR / "assets" / "notation.json"

#: Fence specs the model extracts by default (TASK R2.5, R6.1). A spec is the first word of the
#: info string, or that word and a marker token: `text figure` matches a fence whose info string
#: starts with `text` and holds the token `figure` later. A plain `text` fence is a listing, a
#: log or command output, never a figure. A caller that wants every `text` fence passes `text`.
FIGURE_LANGS = ("mermaid", "text figure")

#: Render check names a negative-fence marker may name (TASK R9.4). `render_check.py` evaluates
#: them; the lint accepts them in a marker and leaves them to the render check.
RENDER_CHECK_NAMES = ("crossings", "edges_through_nodes", "title_crossings",
                      "edges_through_labels", "label_overlaps", "clipped_labels", "font_swap",
                      "legibility", "contrast", "lifeline_through_label", "gantt_overflow")

#: The negative-fence marker: a Mermaid comment `%% negative: <names>`, the last body line of a
#: fence that shows a defect on purpose. Names are comma-separated.
NEGATIVE_MARKER = re.compile(r"^[ \t]*%%[ \t]*negative:(?P<names>.*)$")

#: The directories whose documents may show a defect on purpose: the skill's references and its
#: test fixtures. Anywhere else a marker would let one comment line silence the lint gate.
NEGATIVE_ROOTS = (SKILL_DIR / "references", SKILL_DIR / "scripts" / "tests" / "fixtures")


def negative_allowed(path) -> bool:
    """True when *path* names an existing file under NEGATIVE_ROOTS, symlinks resolved.

    The lint and the render check honour a `%% negative:` marker only in such a file. A
    pseudo-path such as `<text>` names no file and is never allowed."""
    try:
        resolved = Path(path).resolve()
        if not resolved.is_file():
            return False
    except (OSError, RuntimeError, ValueError, TypeError):
        return False
    for root in NEGATIVE_ROOTS:
        try:
            resolved.relative_to(Path(root).resolve())
            return True
        except (OSError, RuntimeError, ValueError):
            continue
    return False


def load_notation(path: Optional[Path] = None) -> dict:
    """Return `assets/notation.json` as a dict. The single source of every threshold."""
    with open(path or NOTATION_PATH, encoding="utf-8") as fh:
        return json.load(fh)


