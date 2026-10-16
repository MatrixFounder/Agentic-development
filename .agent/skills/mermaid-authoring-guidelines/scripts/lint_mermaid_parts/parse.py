"""PARSE rules of the figure lint: the parse hazards that the parse model records
(TASK 126)."""

from __future__ import annotations

from .base import rule, _doc, _hazard_check


rule("MA-PARSE-01", "error", "Bracket or quote that breaks a node label or subgraph title",
     'Quote the label: id["text (detail)"]; mermaid 10.9, 11.17 and 12.1 reject ( ) [ ] { } and a '
     "leading / or \\ in an unquoted label.",
     _doc("flowchart TB\n  A[API (gateway)] --> B"),
     _doc('flowchart TB\n  A["API (gateway)"] --> B'))(
    _hazard_check("label-unquoted-bracket", "label-leading-slash", "shape-unclosed"))

rule("MA-PARSE-02", "error", "Raw quote inside a quoted label",
     "Write #quot; for a quote inside a quoted label.",
     _doc('flowchart TB\n  A["say "hi" now"] --> B'),
     _doc('flowchart TB\n  A["say #quot;hi#quot; now"] --> B'))(
    _hazard_check("label-quote-inside"))

rule("MA-PARSE-03", "error", "Edge label that the parser rejects",
     'Use the pipe form with a quoted label: A -->|"text (x)"| B.',
     _doc("flowchart TB\n  A -->|x (y)| B"),
     _doc('flowchart TB\n  A -->|"x (y)"| B'))(
    _hazard_check("edge-label-bracket", "edge-label-dotted-dot", "edge-label-double-dash"))

rule("MA-PARSE-04", "error", "Tag-like text that the renderer strips from a label",
     "Write #lt; and #gt; for angle brackets; the tags a label may hold are <br/>, <b>, <i>.",
     _doc('flowchart TB\n  A["List<T> x"] --> B'),
     _doc('flowchart TB\n  A["List #lt;T#gt;<br/>x"] --> B'))(
    _hazard_check("html-tag"))

rule("MA-PARSE-05", "error", "The keyword `end` used as an id",
     "Rename the id (End, done); `end` closes a block and the figure does not parse.",
     _doc("flowchart TB\n  A --> end"),
     _doc("flowchart TB\n  A --> End"))(
    _hazard_check("end-id"))

rule("MA-PARSE-06", "error", "`;` or `#` in a sequence message or note",
     "`;` ends the statement and `#` cuts the text; write #59; and #35;, or reword.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: step #1; done"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: step #35;1#59; done"))(
    _hazard_check("seq-semicolon", "seq-hash"))

rule("MA-PARSE-07", "error", "`:`, `;` or `#n;` in a state label",
     "Reword the label: `:` fails in mermaid 10.9, `;` creates stray states, `#1;` is a character code.",
     _doc("stateDiagram-v2\n  a --> b : x; y"),
     _doc("stateDiagram-v2\n  a --> b : x and y"))(
    _hazard_check("state-label-colon", "state-label-semicolon", "state-label-entity"))

rule("MA-PARSE-08", "error", "Literal \\n that the renderer prints as text",
     "Break the line with <br/>.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: one\\ntwo"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: one<br/>two"))(
    _hazard_check("literal-newline"))


@rule("MA-PARSE-09", "error", "Message endpoint that no participant line declares",
      "Declare every participant with an alias, or fix the arrow: `V--xFO` sends to a new "
      "participant FO.",
      _doc("sequenceDiagram\n  participant O as Orchestrator\n  participant V as Validator\n"
           "  V--xFO: error log"),
      _doc("sequenceDiagram\n  participant O as Orchestrator\n  participant V as Validator\n"
           "  V--xO: error log"))
def _check_phantom(fig, ctx):
    seq = fig.sequence
    if seq is None or not any(p.declared for p in seq.participants):
        return []
    return [(p.line, f"`{p.id}` appears in a message or note but no participant line declares it")
            for p in seq.participants if not p.declared]


rule("MA-PARSE-10", "error", "An id glued to an `o` or `x` arrowhead",
     "Put a space after the link: `A --- ops`; `A---ops` draws a circle edge to `ps`.",
     _doc("flowchart TB\n  A---ops"),
     _doc("flowchart TB\n  A --- ops"))(
    _hazard_check("link-head-id"))

rule("MA-PARSE-11", "error", "linkStyle index past the edges defined so far",
     "Count edges from 0 in definition order and put linkStyle after them.",
     _doc("flowchart TB\n  A --> B\n  linkStyle 3 stroke:#546E7A"),
     _doc("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#546E7A"))(
    _hazard_check("linkstyle-range"))

rule("MA-PARSE-12", "error", "`direction` followed by a direction in a subgraph title",
     "Reword the title; `direction LR` in a title is a parse error, quoted or not.",
     _doc('flowchart TB\n  subgraph S["direction LR here"]\n    A\n    B\n  end'),
     _doc('flowchart TB\n  subgraph S["the flow"]\n    A\n    B\n  end'))(
    _hazard_check("subgraph-direction-title"))

rule("MA-PARSE-13", "error", "Deactivating a participant that is not active",
     "Balance activate/deactivate (or +/-); mermaid stops the render on an inactive participant.",
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: x\n  deactivate B"),
     _doc("sequenceDiagram\n  participant A\n  participant B\n  A->>+B: x\n  B-->>-A: y"))(
    _hazard_check("seq-deactivate-inactive"))


rule("MA-PARSE-14", "error", "Comment after a flowchart statement",
     "Put the `%%` comment on its own line; after a statement it is a parse error.",
     _doc("flowchart TB\n  A --> B %% note"),
     _doc("flowchart TB\n  %% note\n  A --> B"))(
    _hazard_check("inline-comment"))

rule("MA-PARSE-15", "error", "`accTitle` or `accDescr` in a mindmap or sankey-beta figure",
     "Drop accTitle and accDescr from this kind; the caption above the fence carries the title.",
     _doc("mindmap\n  accTitle: Topics\n  root((Guide))\n    Forms"),
     _doc("mindmap\n  root((Guide))\n    Forms"))(
    _hazard_check("acc-unsupported"))

rule("MA-PARSE-16", "error", "State `class` statement that lists an id with a non-ASCII character",
     "Put the class on the state line instead, `Новый:::hold --> done`, or use ASCII ids.",
     _doc("stateDiagram-v2\n  Новый --> done\n  classDef hold fill:#E8F0FB,color:#0F2A47\n  class Новый hold"),
     _doc("stateDiagram-v2\n  Новый:::hold --> done\n  classDef hold fill:#E8F0FB,color:#0F2A47"))(
    _hazard_check("state-class-ids"))

rule("MA-PARSE-17", "error", "Flowchart header line that mermaid cannot read",
     "Write the keyword and one direction (TB, TD, BT, LR or RL) alone on the first line; put each "
     "statement on a line of its own or after `;`.",
     (_doc("flowchart TB A --> B"), _doc("flowchart A --> B")),
     _doc("flowchart TB\n  A --> B"))(
    _hazard_check("header-line"))

rule("MA-PARSE-18", "error", "Character code `#n;` in a flowchart label",
     "Write #35; for `#` and #59; for `;`, or reword: `#1;` renders as character 1, so "
     "\"step #1; done\" shows `step  done`.",
     _doc('flowchart TB\n  A["step #1; done"] --> B'),
     _doc('flowchart TB\n  A["step #35;1#59; done"] --> B'))(
    _hazard_check("label-entity"))


