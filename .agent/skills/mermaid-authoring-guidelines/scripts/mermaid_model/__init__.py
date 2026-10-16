"""Parse model for the figures of a Markdown document (TASK 108, R6.1).

One module reads figures for three callers: `lint_mermaid.py`, `render_check.py` and the eval
grader. Each caller imports the dataclasses and functions below; none parses Mermaid on its own.

Scope of the parser. It reads the subset of Mermaid syntax that the skill's references license,
plus the constructs the lint must detect as hazards. It is not a Mermaid validator: a figure the
parser accepts may still fail to render, and `render_check.py` reports that.

Two lists on a Figure carry what the parser saw besides the structure:

* `hazards` — source constructs that the pinned renderers (10.9.8, 11.17.2, 12.1.0) reject,
  misread or change without a diagnostic, each with a `code` the lint maps to a rule;
* `parse_errors` — statements the parser could not read. An entry with `"internal": True` means
  the parser itself failed; the lint treats that as a broken instrument (TASK D20, exit 2).

Figures of a document: every `mermaid` fence and every `text figure` fence (FIGURE_LANGS,
TASK R2.5), found as CommonMark finds fences (`_scan`). A fence inside a blockquote, a GitHub
alert or a list item counts too, its opener on a list marker line included; its body loses the
container's markers and indent. A mermaid fence whose last body line is `%% negative: <names>`
shows a defect on purpose (`Fence.negative`, TASK R9.4). The marker counts only in a document
that `negative_allowed` accepts: the skill's references and test fixtures.

Every line number is a 1-based line of the file the figure came from.

Standard library only.

The model is a package (TASK 124): one module per section, in this order, each importing only
from the modules above it: `base`, `document`, `figure`, `hazards`, `labels`, `kinds`,
`settings`, `preprocessing`, `flowchart`, `sequence`, `state`, `gantt`, `er`, `other_kinds`
and `ascii_figures`. This module holds the entry points and binds every top-level name of the
15 modules, so a caller imports `mermaid_model` as before. A test that replaces a name assigns
it on the module whose code looks it up: `sys.modules[<function>.__module__]`.
"""

from __future__ import annotations

from pathlib import Path

from .base import (SKILL_DIR, NOTATION_PATH, FIGURE_LANGS, RENDER_CHECK_NAMES, NEGATIVE_MARKER,
                   NEGATIVE_ROOTS, negative_allowed, load_notation)
from .document import (Paragraph, NegativeMarker, Fence, negative_markers, _ATX_HEADING,
                       _SETEXT_UNDERLINE, _THEMATIC_BREAK, _COMMENT_LINE, _QUOTE_MARK, _LIST_ITEM,
                       _TABLE_ROW, _CM_FENCE, _CM_CLOSE, _CM_ATX, _CM_SETEXT, _CM_BREAK, _CM_BULLET,
                       _CM_ORDERED, _CM_SPECIAL, _HTML_BLOCK_NAMES, _HTML_ATTRIBUTE, _HTML_BLOCKS,
                       _Span, _quote_strip, _Line, _Block, _list_item, _html_kind, _BlockScan,
                       code_line_reader, _scan, _fence_spans, _is_boundary, _paragraph_before,
                       _paragraph_after, fence_sha256, normalize_text, fence_matches,
                       extract_fences, figure_from_mmd)
from .figure import (Settings, Node, Edge, Subgraph, Flowchart, Participant, Message, Note, Block,
                     Sequence, StateNode, Transition, StateDiagram, GanttTask, Gantt, ErEntity,
                     ErRelation, ErDiagram, AsciiBox, AsciiBlock, Hazard, Figure)
from .hazards import (HAZARD_CODES, ACC_UNSUPPORTED_KINDS, ALLOWED_TAGS, _TAGLIKE, _bad_tags,
                      _ENTITY, _printable_entity, _strip_entities)
from .labels import (_BR, _ANY_TAG, _MD_EMPHASIS, _decode_entities, label_lines, word_count,
                     char_count, _EMOJI_PRESENTATION, char_widths, display_width)
from .kinds import KIND_OF_KEYWORD, OTHER_KEYWORDS, diagram_keyword, _known_keywords
from .settings import (_DIRECTIVE, _parse_directive, YamlError, _yaml_scalar, _yaml_quoted,
                       _yaml_flow, _YAML_KEY, parse_yaml, _yaml_value_text, _yaml_unclosed,
                       _yaml_join_continuations, _yaml_block, _yaml_value_after_key, _yaml_map,
                       _yaml_seq)
from .preprocessing import (_body_lines, _YAML_HEX_COMMENT, _take_settings, _take_accessibility,
                            detect_kind)
from .flowchart import (_DIRECTIONS, _SHAPE_OPENERS, _LINK_FULL, _LINK_TEXT_START, _EDGE_ID_PREFIX,
                        _ID_STOP, _CLASS_NAME, _BRACKET_CHARS, _split_statements, _parse_props,
                        _Frame, _FlowParser, _join_open_quotes, _comment_start, _find_first,
                        _matching_brace, flowchart_edge_ids)
from .sequence import (_SEQ_ARROWS, _SEQ_MESSAGE, _SEQ_PARTICIPANT, _SEQ_NOTE, _SEQ_BLOCK,
                       _SEQ_CONT, _SEQ_BOX, _COLOR_PREFIX, _HEX_COLOUR_START, _seq_message,
                       _seq_text_hazards, _parse_sequence)
from .state import (_STATE_TRANSITION, _STATE_DECL, _STATE_DESC, _STATE_NOTE, _STATE_CLASS,
                    _state_label_hazards, _split_class_suffix, _parse_state, _first_label_colon,
                    state_parent_chain)
from .gantt import GANTT_TAGS, _parse_gantt, gantt_refs
from .er import (_ER_RELATION, _ER_ENTITY_OPEN, _STYLING_DETAIL, _STYLING_STATEMENT,
                 _styling_statement, _parse_er)
from .other_kinds import (_CLASS_LINK, _CLASS_SKIP, _class_name, _count_classes, _count_mindmap,
                          _count_timeline, _count_journey, _count_gitgraph, _COUNTERS, _class_items,
                          _MINDMAP_NODE, _mindmap_items, _timeline_items, _journey_items,
                          _gitgraph_items, _pie_items, _ITEMS, ITEM_KINDS, THEME_KINDS,
                          _THEME_STYLING, _THEME_STATEMENT, OTHER_SCANNED_KINDS, _scan_other)
from .ascii_figures import (_BOX_TOP_LEFT, _BOX_TOP_RIGHT, _BOX_BOTTOM_LEFT, _BOX_BOTTOM_RIGHT,
                            _BOX_HORIZONTAL, _BOX_VERTICAL, _TOP_JUNCTION, _BOTTOM_JUNCTION,
                            _SIDE_JUNCTION, _LAYER_LEFT, _LAYER_RIGHT, _ALIGN_CHARS, _SEGMENT_SPLIT,
                            _ARROW_TOKEN, _COLUMN_GAP, _FORK_GLYPHS, _JOIN_GLYPHS, _MERGE_GLYPHS,
                            _JOIN_CANDIDATES, _ARROWHEADS, _DOWN_ARROWHEADS, _box_strokes,
                            _UP_STROKE, _DOWN_STROKE, _cells, _segments, _anchors, _Grid, _drift,
                            _arrow_after, _turns_down, _arrow_below, _frame_bottom, _forks, _joins,
                            _parse_ascii, _find_boxes, _text_between, _claim_box, _BOX_SIDE,
                            _BOX_EDGE, _border_end, _trace_box)


def parse_figure(fence: Fence) -> Figure:
    """Parse one fence into a Figure. Never raises on bad input; records `parse_errors`.

    A `mermaid` fence is parsed as Mermaid. Any other fence a caller extracted (`text figure`, or
    a plain `text` fence when the caller asked for one) is read as an ASCII figure.
    """
    if fence.lang != "mermaid":
        fig = Figure(fence=fence, kind="ascii", keyword=fence.lang or "text")
        try:
            fig.ascii = _parse_ascii(fence)
        except Exception as exc:  # noqa: BLE001 — the instrument reports its own failure
            fig.parse_errors.append({"line": fence.start, "message": f"internal parser error: {exc!r}",
                                     "internal": True})
        return fig
    fig = Figure(fence=fence, kind="unknown", keyword="")
    try:
        rows = _take_settings(_body_lines(fence), fig)
        valid = [s for s in fig.settings_blocks if s.form == "directive"] or fig.settings_blocks
        fig.settings = valid[0] if valid else None
        rows = _take_accessibility(rows, fig)
        if not rows:
            # kind "unknown" with no keyword: the lint reports it as a fence no viewer renders
            return fig
        keyword = diagram_keyword(rows[0][1])
        fig.keyword = keyword
        if keyword in KIND_OF_KEYWORD:
            fig.kind = KIND_OF_KEYWORD[keyword]
        elif keyword in _known_keywords():
            fig.kind = keyword
        else:
            fig.kind = "unknown"
        if fig.kind == "flowchart":
            fig.flowchart = _FlowParser(fig).run(rows)
        elif fig.kind == "sequence":
            fig.sequence = _parse_sequence(rows, fig)
        elif fig.kind == "state":
            fig.state = _parse_state(rows, fig)
        elif fig.kind == "gantt":
            fig.gantt = _parse_gantt(rows, fig)
        elif fig.kind == "er":
            fig.er = _parse_er(rows, fig)
        elif fig.kind in OTHER_SCANNED_KINDS:
            _scan_other(rows, fig)
        if fig.kind == "timeline":
            _timeline_header(rows[0], fig)
        if fig.kind in ACC_UNSUPPORTED_KINDS:
            for line in fig.acc_lines:
                fig.hazard("acc-unsupported", line, "accTitle / accDescr",
                           f"`accTitle` and `accDescr` stop the render of a {fig.kind} figure in "
                           "mermaid 10.9, 11.17 and 12.1")
    except Exception as exc:  # noqa: BLE001 — the instrument reports its own failure
        fig.parse_errors.append({"line": fence.start, "message": f"internal parser error: {exc!r}",
                                 "internal": True})
    return fig


def _timeline_header(row: tuple, fig: Figure) -> None:
    """Text after `timeline` on its header line. Mermaid 10.9.8 draws it as a first period, and
    11.17.2 reads `TD` as a direction and draws the figure top to bottom (TASK 110 R2)."""
    line, text = row
    header = text.strip()
    # A `%%` comment after the keyword draws nothing in 10.9.8 or 11.17.2 (measured 2026-10-05).
    rest = header[len("timeline"):].split("%%", 1)[0].strip()
    if rest:
        fig.hazard("timeline-header", line, header,
                   f"`{rest}` after `timeline`: mermaid 10.9 draws it as a period")


def parse_document(text: str, langs: tuple = FIGURE_LANGS) -> list:
    """Return a Figure for every fence of a Markdown document that *langs* selects: by default
    every `mermaid` fence and every `text figure` fence (TASK R6.1)."""
    return [parse_figure(f) for f in extract_fences(text, langs)]


def parse_path(path, langs: tuple = FIGURE_LANGS) -> list:
    """Parse a `.md` or `.mmd` file; a `.mmd` file is one figure."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".mmd":
        return [parse_figure(figure_from_mmd(text))]
    return parse_document(text, langs)
