"""Tests for lint_mermaid.py and mermaid_model.py (TASK 108, R6, R2.5, R2.7, R3.3, R3.7, D20, D21,
D25, D26).

The rule ids are pinned as a literal set (TASK R6.6) and compared with the registry both ways: a
deleted, renamed or added rule fails here, because the expected set is declared in this file and
not read from the registry (ARCHITECTURE L4). Every rule also has a targeted case below, written
independently of the rule's own probe pair.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import lint_mermaid as lm  # noqa: E402
import mermaid_model as mm  # noqa: E402

NOTATION = mm.load_notation()

RULE_IDS = {
    "MA-PARSE-01", "MA-PARSE-02", "MA-PARSE-03", "MA-PARSE-04", "MA-PARSE-05", "MA-PARSE-06",
    "MA-PARSE-07", "MA-PARSE-08", "MA-PARSE-09", "MA-PARSE-10", "MA-PARSE-11", "MA-PARSE-12",
    "MA-PARSE-13", "MA-PARSE-14", "MA-PARSE-15", "MA-PARSE-16", "MA-PARSE-17", "MA-PARSE-18",
    "MA-SYN-01", "MA-SYN-02", "MA-SYN-03", "MA-SYN-04", "MA-SYN-05", "MA-SYN-06", "MA-SYN-07",
    "MA-SYN-08",
    "MA-SET-01", "MA-SET-02", "MA-SET-03", "MA-SET-04", "MA-SET-05", "MA-SET-06", "MA-SET-07",
    "MA-ID-01", "MA-ID-02",
    "MA-BUDGET-01", "MA-BUDGET-02",
    "MA-FLOW-01", "MA-FLOW-02", "MA-FLOW-03", "MA-FLOW-04", "MA-FLOW-05", "MA-FLOW-06",
    "MA-FLOW-07", "MA-FLOW-08", "MA-FLOW-09",
    "MA-STATE-01", "MA-STATE-02", "MA-STATE-03", "MA-STATE-04",
    "MA-SEQ-01", "MA-SEQ-02", "MA-SEQ-03",
    "MA-LABEL-01", "MA-LABEL-02", "MA-LABEL-03", "MA-LABEL-04", "MA-LABEL-05", "MA-LABEL-06",
    "MA-LABEL-07", "MA-LABEL-08", "MA-LABEL-09", "MA-LABEL-10", "MA-LABEL-11",
    "MA-LABEL-12", "MA-LABEL-13",
    "MA-CLASS-01", "MA-CLASS-02", "MA-CLASS-03", "MA-CLASS-04", "MA-CLASS-05", "MA-CLASS-06",
    "MA-CLASS-07",
    "MA-GANTT-01", "MA-GANTT-02", "MA-GANTT-03", "MA-GANTT-04", "MA-GANTT-05", "MA-GANTT-06",
    "MA-GANTT-07", "MA-GANTT-08",
    "MA-ASCII-01", "MA-ASCII-02", "MA-ASCII-03", "MA-ASCII-04", "MA-ASCII-05", "MA-ASCII-06",
    "MA-ASCII-07",
    "MA-DOC-01", "MA-DOC-02", "MA-DOC-03", "MA-DOC-04", "MA-DOC-05",
    "MA-MODEL-01",
    "MA-NEG-01", "MA-NEG-02", "MA-NEG-03",
}

ERROR_RULES = {
    "MA-PARSE-01", "MA-PARSE-02", "MA-PARSE-03", "MA-PARSE-04", "MA-PARSE-05", "MA-PARSE-06",
    "MA-PARSE-07", "MA-PARSE-08", "MA-PARSE-09", "MA-PARSE-10", "MA-PARSE-11", "MA-PARSE-12",
    "MA-PARSE-13", "MA-PARSE-14", "MA-PARSE-15", "MA-PARSE-16", "MA-PARSE-17", "MA-PARSE-18",
    "MA-SYN-01", "MA-SYN-02",
    "MA-SYN-03", "MA-SYN-05", "MA-SYN-06", "MA-SYN-07", "MA-SYN-08", "MA-SET-01", "MA-SET-02",
    "MA-SET-03", "MA-SET-04", "MA-ID-01", "MA-BUDGET-02", "MA-FLOW-02", "MA-STATE-01",
    "MA-STATE-02", "MA-SEQ-01", "MA-SEQ-03", "MA-CLASS-01", "MA-CLASS-06", "MA-GANTT-01",
    "MA-GANTT-02", "MA-GANTT-03", "MA-GANTT-04", "MA-GANTT-06", "MA-GANTT-08", "MA-ASCII-01",
    "MA-ASCII-06", "MA-NEG-01", "MA-NEG-02", "MA-NEG-03",
}

ASCII = "text figure"


def doc(body, lang="mermaid", caption="**Figure 1.** Test figure.", legend="Legend: test notation."):
    return f"{caption}\n\n```{lang}\n{body}\n```\n\n{legend}\n"


GANTT = "gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker off\n"
LABELS = NOTATION["labels"]
BUDGETS = NOTATION["budgets"]


def chain(n, direction="TB"):
    return "\n".join([f"flowchart {direction}"] + [f"  N{k} --> N{k + 1}" for k in range(1, n)])


def participants(n):
    lines = ["sequenceDiagram"] + [f"  participant P{k}" for k in range(1, n + 1)]
    return "\n".join(lines + ["  P1->>P2: x"])


def messages(n):
    lines = ["sequenceDiagram", "  participant P1", "  participant P2"]
    return "\n".join(lines + [f"  P{1 + k % 2}->>P{2 - k % 2}: m{k}" for k in range(n)])


def states(n):
    return "\n".join(["stateDiagram-v2"] + [f"  s{k} --> s{k + 1}" for k in range(1, n)])


def gantt_label(n):
    return doc(GANTT + "  section S\n  " + "y" * n + " :a, 0, 3ms")


def br_lines(n, word="w"):
    return "<br/>".join(f"{word}{k}" for k in range(1, n + 1))


SETTINGS_FLOW = NOTATION["settings"]["flowchart"]

# rule id -> (a document on which the rule fires, a document on which it stays quiet)
CASES = {
    "MA-PARSE-01": (doc("flowchart TB\n  A{decide (x)} --> B"), doc('flowchart TB\n  A{"decide (x)"} --> B')),
    "MA-PARSE-02": (doc('flowchart TB\n  A -->|"say "hi""| B'), doc('flowchart TB\n  A -->|"say #quot;hi#quot;"| B')),
    "MA-PARSE-03": (doc("flowchart TB\n  A -. uses v2.0 .-> B"), doc('flowchart TB\n  A -.->|"uses v2.0"| B')),
    "MA-PARSE-04": (doc("stateDiagram-v2\n  a --> b : Map<K> ready"), doc("stateDiagram-v2\n  a --> b : map ready")),
    "MA-PARSE-05": (doc("sequenceDiagram\n  participant end\n  participant B\n  end->>B: x"),
                    doc("sequenceDiagram\n  participant End\n  participant B\n  End->>B: x")),
    "MA-PARSE-06": (doc("sequenceDiagram\n  participant A\n  Note over A: retry #2"),
                    doc("sequenceDiagram\n  participant A\n  Note over A: retry #35;2")),
    "MA-PARSE-07": (doc("stateDiagram-v2\n  a : waits: for input\n  a --> b"),
                    doc("stateDiagram-v2\n  a : waits for input\n  a --> b")),
    "MA-PARSE-08": (doc(GANTT + "  section S\n  one\\ntwo :a, 0, 3ms"), doc(GANTT + "  section S\n  one two :a, 0, 3ms")),
    "MA-PARSE-09": (doc("sequenceDiagram\n  participant A as Api\n  A->>B: x"),
                    doc("sequenceDiagram\n  participant A as Api\n  participant B as Db\n  A->>B: x")),
    "MA-PARSE-10": (doc("flowchart TB\n  A---xray"), doc("flowchart TB\n  A--xray")),
    "MA-PARSE-11": (doc("flowchart TB\n  linkStyle 0 stroke:#546E7A\n  A --> B"),
                    doc("flowchart TB\n  A --> B\n  linkStyle 0 stroke:#546E7A")),
    "MA-PARSE-12": (doc("flowchart TB\n  subgraph S [direction TB view]\n    A\n    B\n  end"),
                    doc("flowchart TB\n  subgraph S [view of the flow]\n    A\n    B\n  end")),
    "MA-PARSE-13": (doc("sequenceDiagram\n  participant A\n  participant B\n  A->>-B: x"),
                    doc("sequenceDiagram\n  participant A\n  participant B\n  A->>+B: x\n  B->>-A: y")),
    "MA-PARSE-14": (doc("flowchart TB\n  A --> B %% why"), doc("flowchart TB\n  A --> B\n  %% why")),
    "MA-PARSE-15": (doc("sankey-beta\naccTitle: Flows\nA,B,10"), doc("sankey-beta\nA,B,10")),
    "MA-PARSE-16": (doc("stateDiagram-v2\n  a --> Готов\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class a,Готов c"),
                    doc("stateDiagram-v2\n  a --> Готов:::c\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class a c")),
    "MA-PARSE-17": (doc("graph TD A-->B"), doc("graph TD\n  A-->B")),
    "MA-PARSE-18": (doc('flowchart TB\n  A -->|"retry #3; then fail"| B'),
                    doc('flowchart TB\n  A -->|"retry #35;3 then fail"| B')),
    "MA-SYN-01": (doc('sequenceDiagram\n  participant DB@{ "type": "database" }\n  participant A\n  A->>DB: q'),
                  doc("sequenceDiagram\n  participant DB\n  participant A\n  A->>DB: q")),
    "MA-SYN-02": (doc("flowchart TB\n  A --> B\n  class e1 animate"), doc("flowchart TB\n  A --> B")),
    "MA-SYN-03": (doc("architecture-beta\n  service a(server)[A]"), doc("erDiagram\n  A ||--o{ B : has")),
    "MA-SYN-04": (doc('C4Context\n  Person(a, "A")'), doc("timeline\n  2024 : x")),
    "MA-SYN-05": (doc(GANTT + "  section S\n  t1 :a, 0, 3ms\n  cut :vert, v1, 2, 0ms"),
                  doc(GANTT + "  section S\n  t1 :a, 0, 3ms\n  cut :milestone, m1, 2, 0ms")),
    "MA-SYN-06": (doc("sequenceDiagram\n  participant A\n  participant B\n  A-|\\B: x"),
                  doc("sequenceDiagram\n  participant A\n  participant B\n  A->>B: x")),
    "MA-SYN-07": (doc("flowchartTB\n  A --> B"), doc("flowchart TB\n  A --> B")),
    "MA-SYN-08": (doc("requirementDiagram\n  element e1 {\n    type: service\n  }\n  style e1 fill:#FFF4E0"),
                  doc("classDiagram\n  class Dog\n  style Dog fill:#FFF4E0,color:#4A2C00")),
    "MA-SET-01": (doc("%%{init: {'look': 'classic' 'layout': 'dagre'}}%%\nflowchart TB\n  A --> B"),
                  doc("%%{init: {'look': 'classic', 'layout': 'dagre'}}%%\nflowchart TB\n  A --> B")),
    "MA-SET-02": (doc("---\nconfig:\n\tlook: classic\n---\nflowchart TB\n  A --> B"),
                  doc("---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B")),
    "MA-SET-03": (doc('%%{init: {"themeVariables": {"lineColor": "var(--x)"}}}%%\nflowchart TB\n  A --> B'),
                  doc('%%{init: {"themeVariables": {"lineColor": "#546E7A"}}}%%\nflowchart TB\n  A --> B')),
    "MA-SET-04": (doc("---\nconfig:\n  fontFamily: Arial\n---\nflowchart TB\n  A --> B"),
                  doc("---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B")),
    "MA-SET-05": (doc("---\nconfig:\n  theme: dark\n---\nflowchart TB\n  A --> B"),
                  doc("---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B")),
    "MA-SET-06": (doc('%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B'),
                  doc('%%{init: {"layout": "dagre", "look": "classic"}}%%\nflowchart TB\n  A --> B')),
    "MA-SET-07": (doc('%%{init: {"look": "classic"}}%%\nsequenceDiagram\n  A->>B: x') + "\n"
                  + doc('%%{init: {"look": "classic", "sequence": {"wrap": true}}}%%\nsequenceDiagram\n  A->>B: y'),
                  doc('%%{init: {"look": "classic"}}%%\nsequenceDiagram\n  A->>B: x') + "\n"
                  + doc('%%{init: {"look": "classic"}}%%\nsequenceDiagram\n  A->>B: y')),
    "MA-ID-01": (doc("flowchart TB\n  x --> y_z\n  x_y --> z"), doc("flowchart TB\n  x --> yz\n  xy --> z")),
    "MA-ID-02": (doc("stateDiagram-v2\n  waiting_room --> done"), doc("stateDiagram-v2\n  waitingRoom --> done")),
    "MA-BUDGET-01": (doc(messages(BUDGETS["sequence"]["messages"][0] + 1)),
                     doc(messages(BUDGETS["sequence"]["messages"][0]))),
    "MA-BUDGET-02": (doc(states(BUDGETS["state"]["states"][1] + 1)), doc(states(BUDGETS["state"]["states"][1]))),
    "MA-FLOW-01": (doc("flowchart TB\n  A --> B\n  A -.-> B"), doc("flowchart TB\n  A --> B\n  A ~~~ B")),
    "MA-FLOW-02": (doc('flowchart TB\n  subgraph G["Grp"]\n    A\n    B\n  end\n  G --> C'),
                   doc('flowchart TB\n  subgraph G["Grp"]\n    A\n    B\n  end\n  B --> C')),
    "MA-FLOW-03": (doc('flowchart TB\n  subgraph E["Empty"]\n  end\n  A --> B'),
                   doc('flowchart TB\n  subgraph E["Pair"]\n    A\n    B\n  end\n  A --> B')),
    "MA-FLOW-04": (doc('flowchart TB\n  A -->|"(1) init"| B\n  B -->|"(2) run"| C'),
                   doc('flowchart TB\n  A -->|"init"| B\n  B -->|"2 retries"| C')),
    "MA-FLOW-05": (doc("flowchart TB\n  A --> B & C & D & E\n  B --> C & D & E\n  C --> D & E\n  D --> E"),
                   doc("flowchart TB\n  A --> B & C & D\n  B --> C & D\n  C --> D")),
    "MA-FLOW-06": (doc(chain(NOTATION["structure"]["lr_max_nodes"] + 1, "RL")),
                   doc(chain(NOTATION["structure"]["lr_max_nodes"], "LR"))),
    "MA-FLOW-07": (doc("flowchart TB\n  A --> B\n  style Ghost fill:#FFFFFF,color:#263238"),
                   doc("flowchart TB\n  style A fill:#FFFFFF,color:#263238\n  A --> B")),
    "MA-FLOW-08": (doc("flowchart TB\n  A --> B\n  linkStyle default stroke:#546E7A"), doc("flowchart TB\n  A -.-> B")),
    "MA-FLOW-09": (doc('flowchart TB\n  subgraph G["Grp"]\n    direction RL\n    A\n    B\n  end'),
                   doc('flowchart RL\n  subgraph G["Grp"]\n    A\n    B\n  end')),
    "MA-STATE-01": (doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  state H {\n    p --> q\n  }\n  y --> p"),
                    doc("stateDiagram-v2\n  state W {\n    x --> y\n  }\n  state H {\n    p --> q\n  }\n  W --> H")),
    "MA-STATE-02": (doc("stateDiagram-v2\n  a --> b\n  style a fill:#E8F0FB,stroke:#2E5A8A"),
                    doc("stateDiagram-v2\n  a:::hold --> b\n  classDef hold fill:#E8F0FB,color:#0F2A47")),
    "MA-STATE-03": (doc("stateDiagram-v2\n  [*] --> a\n  [*] --> a\n  a --> [*]"),
                    doc("stateDiagram-v2\n  [*] --> a\n  a --> [*]\n  a --> b\n  b --> a")),
    "MA-STATE-04": (doc("stateDiagram-v2\n  s1 : 'Waiting'\n  s1 --> s2"),
                    doc('stateDiagram-v2\n  state "Waiting" as s1\n  s1 --> s2')),
    "MA-SEQ-01": (doc("sequenceDiagram\n  participant A\n  A->>A: x\n  style A fill:#FFFFFF"),
                  doc("sequenceDiagram\n  participant A\n  A->>A: x")),
    "MA-SEQ-02": (doc("sequenceDiagram\n  participant A\n  participant B\n  participant C\n  participant D\n"
                      "  A->>D: " + "w" * (LABELS["edge_label_chars_max"] + 5)),
                  doc("sequenceDiagram\n  participant A\n  participant B\n  participant C\n  participant D\n"
                      "  C->>D: " + "w" * (LABELS["edge_label_chars_max"] + 5))),
    "MA-SEQ-03": (doc("sequenceDiagram\n  box #E8F0FB Backend\n    participant A\n  end\n  A->>A: x"),
                  doc("sequenceDiagram\n  box rgba(127,127,127,0.08) Backend\n    participant A\n  end\n  A->>A: x")),
    "MA-LABEL-01": (doc('flowchart TB\n  A["' + "Ж" * (LABELS["node_line1_chars_max"] + 1) + '"] --> B'),
                    doc('flowchart TB\n  A["' + "Ж" * LABELS["node_line1_chars_max"] + '"] --> B')),
    "MA-LABEL-02": (doc('flowchart TB\n  A["n<br/>' + "r" * (LABELS["node_second_line_chars_max"] + 1) + '"] --> B'),
                    doc('flowchart TB\n  A["n<br/>' + "r" * LABELS["node_second_line_chars_max"] + '"] --> B')),
    "MA-LABEL-03": (doc("stateDiagram-v2\n  a --> b : " + "t" * (LABELS["edge_label_chars_max"] + 1)),
                    doc("stateDiagram-v2\n  a --> b : " + "t" * LABELS["edge_label_chars_max"])),
    "MA-LABEL-04": (doc("sequenceDiagram\n  A->>B: " + "m" * (LABELS["sequence_message_chars_max"] + 1)),
                    doc("sequenceDiagram\n  A->>B: " + "m" * LABELS["sequence_message_chars_max"])),
    "MA-LABEL-05": (doc("stateDiagram-v2\n  a --> b\n  note right of a : " + "n" * (LABELS["note_chars_max"] + 1)),
                    doc("stateDiagram-v2\n  a --> b\n  note right of a : " + "n" * LABELS["note_chars_max"])),
    "MA-LABEL-06": (gantt_label(LABELS["gantt_label_chars_max"] + 1), gantt_label(LABELS["gantt_label_chars_max"])),
    "MA-LABEL-07": (doc("flowchart TB\n  A -->|Читает| B"), doc("flowchart TB\n  A -->|читает SQL| B")),
    "MA-LABEL-08": (doc("stateDiagram-v2\n" + "".join(f"  a : d{k}\n" for k in range(LABELS["node_label_lines_max"] + 1))
                        + "  a --> b"),
                    doc("stateDiagram-v2\n" + "".join(f"  a : d{k}\n" for k in range(LABELS["node_label_lines_max"]))
                        + "  a --> b")),
    "MA-LABEL-09": (doc("sequenceDiagram\n  A->>B: " + br_lines(LABELS["sequence_message_lines_max"] + 1)),
                    doc("sequenceDiagram\n  A->>B: " + br_lines(LABELS["sequence_message_lines_max"]))),
    "MA-LABEL-10": (doc("sequenceDiagram\n  actor U as " + "Ж" * (LABELS["participant_chars_max"] + 1) + "\n  U->>U: x"),
                    doc("sequenceDiagram\n  actor U as " + "Ж" * LABELS["participant_chars_max"] + "\n  U->>U: x")),
    "MA-LABEL-11": (doc("stateDiagram-v2\n  a --> b\n  note right of a\n"
                        + "".join(f"    n{k}\n" for k in range(LABELS["note_lines_max"] + 1)) + "  end note"),
                    doc("stateDiagram-v2\n  a --> b\n  note right of a\n"
                        + "".join(f"    n{k}\n" for k in range(LABELS["note_lines_max"])) + "  end note")),
    "MA-LABEL-12": (doc("flowchart TB\n  A -->|" + br_lines(LABELS["edge_label_lines_max"] + 1) + "| B"),
                    doc("flowchart TB\n  A -->|" + br_lines(LABELS["edge_label_lines_max"]) + "| B")),
    "MA-LABEL-13": (doc("sequenceDiagram\n  participant P as " + br_lines(LABELS["participant_lines_max"] + 1)
                        + "\n  P->>P: x"),
                    doc("sequenceDiagram\n  participant P as " + br_lines(LABELS["participant_lines_max"])
                        + "\n  P->>P: x")),
    "MA-CLASS-01": (doc("flowchart TB\n  A --> B\n  style A fill:#777777,color:#888888"),
                    doc("flowchart TB\n  A --> B\n  style A fill:#FFFFFF,color:#263238")),
    "MA-CLASS-02": (doc("flowchart TB\n  A --> B\n  class A ghost"),
                    doc("flowchart TB\n  A --> B\n  class A ghost\n  classDef ghost fill:#FFFFFF,color:#263238")),
    "MA-CLASS-03": (doc("stateDiagram-v2\n  a --> b\n  classDef idle fill:#FFFFFF,color:#263238"),
                    doc("stateDiagram-v2\n  a --> b\n  classDef idle fill:#FFFFFF,color:#263238\n  class a idle")),
    "MA-CLASS-04": (doc("flowchart TB\n  A --> B\n  classDef default fill:#FFFFFF"), doc("flowchart TB\n  A --> B")),
    "MA-CLASS-05": (doc("stateDiagram-v2\n  a:::dark --> b\n  classDef dark fill:#263238"),
                    doc("stateDiagram-v2\n  a:::dark --> b\n  classDef dark fill:#263238,color:#FFFFFF")),
    "MA-CLASS-06": (doc("flowchart TB\n  class A,B c\n  A --> B\n  classDef c fill:#FFFFFF,color:#263238"),
                    doc("flowchart TB\n  A --> B\n  class A,B c\n  classDef c fill:#FFFFFF,color:#263238")),
    "MA-CLASS-07": (doc("mindmap\n  root((Guide))\n    Forms\n    :::urgent"), doc("mindmap\n  root((Guide))\n    Forms")),
    "MA-GANTT-01": (doc(GANTT + "  section S\n  t1 :a, 0, 3ms\n  t2 :b, after zz, 2ms"),
                    doc(GANTT + "  section S\n  t1 :a, 0, 3ms\n  t2 :b, after a, 2ms")),
    "MA-GANTT-02": (doc(GANTT + "  section S\n  t1 :x, 0, 3ms\n  t2 :b, 1, until x.y"),
                    doc(GANTT + "  section S\n  t1 :xy, 0, 3ms\n  t2 :b, 1, until xy")),
    "MA-GANTT-03": (doc(GANTT + "  section S\n  Step 1: draft :a, 0, 3ms"), doc(GANTT + "  section S\n  Step 1 draft :a, 0, 3ms")),
    "MA-GANTT-04": (doc(GANTT + "  section Анализ\n  t1 :a, 0, 3ms\n  section Сборка\n  t2 :b, 3, 3ms\n  section Анализ\n  t3 :c, 6, 1ms"),
                    doc(GANTT + "  section Анализ\n  t1 :a, 0, 3ms\n  section Сборка\n  t2 :b, 3, 3ms")),
    "MA-GANTT-05": (doc("gantt\n  dateFormat x\n  axisFormat %-L\n  todayMarker off\n  section S\n  t1 :a, 0, 3ms"),
                    doc(GANTT + "  section S\n  t1 :a, 0, 3ms")),
    "MA-GANTT-06": (doc(GANTT + "  section S\n  t1 :a, 0, 3ms\n  topAxis"), doc(GANTT + "  section S\n  t1 :a, 0, 3ms")),
    "MA-GANTT-07": (doc("gantt\n  dateFormat x\n  axisFormat %Q\n  todayMarker stroke-width:5px\n  section S\n  t1 :a, 0, 3ms"),
                    doc(GANTT + "  section S\n  t1 :a, 0, 3ms")),
    "MA-GANTT-08": (doc("gantt\n  dateFormat X\n  axisFormat %S\n  todayMarker off\n  section S\n  t1 :a, 0, 5"),
                    doc("gantt\n  dateFormat X\n  axisFormat %S\n  todayMarker off\n  section S\n  t1 :a, 0, 5s")),
    "MA-ASCII-01": (doc("root\n└──\tleaf", ASCII), doc("root\n└── leaf", ASCII)),
    "MA-ASCII-02": (doc("┌──────┐\n│ ✅ ok │\n└──────┘", ASCII), doc("┌──────┐\n│ имя  │\n└──────┘", ASCII)),
    "MA-ASCII-03": (doc("-" * (NOTATION["ascii"]["max_columns"] + 1), ASCII),
                    doc("-" * NOTATION["ascii"]["max_columns"], ASCII)),
    "MA-ASCII-04": (doc("+----+\n| ab  |\n+----+", ASCII), doc("+----+\n| ab |\n+----+", ASCII)),
    "MA-ASCII-05": (doc("root\n" + "\n".join(f"├── item{k}" for k in range(BUDGETS["ascii"]["elements"][0])), ASCII),
                    doc("root\n" + "\n".join(f"├── item{k}" for k in range(BUDGETS["ascii"]["elements"][0] - 1)), ASCII)),
    "MA-ASCII-06": (doc("root\n" + "\n".join(f"├── item{k}" for k in range(BUDGETS["ascii"]["elements"][1])), ASCII),
                    doc("root\n" + "\n".join(f"├── item{k}" for k in range(BUDGETS["ascii"]["elements"][1] - 1)), ASCII)),
    "MA-ASCII-07": (doc("print server\n├── spooler\n│   └── job queue\n ├── renderer", ASCII),
                    doc("print server\n├── spooler\n│   └── job queue\n├── renderer", ASCII)),
    "MA-DOC-01": ("Intro.\n\n\n```mermaid\nflowchart TB\n  A --> B\n```\n\n\nOutro.\n",
                  "Intro.\n\n```mermaid\nflowchart TB\n  A --> B\n```\n"),
    "MA-DOC-02": ("**Figure 1.** Three shapes.\n\n```mermaid\nflowchart TB\n  A([a]) --> B[(b)] --> C{c}\n```\n\n## Next\n",
                  "**Figure 1.** Three shapes.\n\n```mermaid\nflowchart TB\n  A([a]) --> B[(b)] --> C{c}\n```\n"
                  "- stadium: client\n- cylinder: store\n- rhombus: decision\n"),
    "MA-DOC-03": (doc("stateDiagram-v2\n  a:::hold --> b\n  classDef hold fill:#E8F0FB,color:#0F2A47") + "\n"
                  + doc("stateDiagram-v2\n  c:::hold --> d\n  classDef hold fill:#FFFFFF,color:#0F2A47"),
                  doc("stateDiagram-v2\n  a:::hold --> b\n  classDef hold fill:#E8F0FB,color:#0F2A47") + "\n"
                  + doc("stateDiagram-v2\n  c:::hold --> d\n  classDef hold fill:#E8F0FB,color:#0F2A47")),
    "MA-DOC-04": (doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
                  + doc("sequenceDiagram\n  participant A as API\n  A->>A: y"),
                  doc("sequenceDiagram\n  participant A as Api\n  A->>A: x") + "\n"
                  + doc("sequenceDiagram\n  participant A as Api\n  A->>A: y")),
    "MA-DOC-05": ("```mermaid\nflowchart TB\n  A --> B\n```\n\n**Рисунок 1.** Подпись снизу.\n",
                  "**Рисунок 1.** Подпись сверху.\n\n```mermaid\nflowchart TB\n  A --> B\n```\n"),
    "MA-MODEL-01": (doc("flowchart TB\n  A <-- B"), doc("flowchart TB\n  A --> B")),
    "MA-NEG-01": (doc("stateDiagram-v2\n  a --> b\n  %% negative: state"),
                  doc('stateDiagram-v2\n  a --> b : "go"\n  %% negative: state')),
    "MA-NEG-02": (doc("flowchart TB\n  %% negative: MA-FLOW-01\n  A --> B\n  B --> A"),
                  doc("flowchart TB\n  A --> B\n  B --> A\n  %% negative: flow, crossings")),
    "MA-NEG-03": (doc("stateDiagram-v2\n  a --> b : x\n  %% negative: MA-STATE-04"), doc("stateDiagram-v2\n  a --> b : x")),
}


def rule(rule_id):
    return next(r for r in lm.RULES if r.id == rule_id)


def run(text, rule_id=None, is_mmd=False, langs=mm.FIGURE_LANGS, negative=True):
    """Lint *text* as a test fixture: negative markers count unless *negative* is False."""
    rules = None if rule_id is None else [rule(rule_id)]
    return lm.lint_text(text, "<test>", is_mmd=is_mmd, notation=NOTATION, rules=rules, langs=langs,
                        negative=negative)


def ids(findings):
    return sorted({f.rule for f in findings})


def counted(findings):
    return [f for f in findings if not f.expected]


def call_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = lm.main(argv)
    return code, out.getvalue(), err.getvalue()


# --------------------------------------------------------------------------- registry


class TestRegistry(unittest.TestCase):
    def test_registry_holds_every_literal_rule_id(self):
        registry = {r.id for r in lm.RULES}
        self.assertEqual(RULE_IDS - registry, set(), "rule ids missing from the registry")

    def test_literal_holds_every_registry_rule_id(self):
        registry = {r.id for r in lm.RULES}
        self.assertEqual(registry - RULE_IDS, set(), "registry rules missing from the literal set")

    def test_rule_ids_are_unique(self):
        ids_ = [r.id for r in lm.RULES]
        self.assertEqual(len(ids_), len(set(ids_)))

    def test_rule_shape(self):
        for r in lm.RULES:
            self.assertRegex(r.id, r"^MA-[A-Z]+-\d{2}$")
            self.assertIn(r.severity, ("error", "warn"))
            self.assertTrue(r.title and r.hint, r.id)
            self.assertIn(r.scope, ("figure", "document", "marker"))

    def test_error_severities_are_pinned(self):
        self.assertEqual({r.id for r in lm.RULES if r.severity == "error"}, ERROR_RULES)

    def test_family_table_covers_the_registry(self):
        prefixes = {r.id.rsplit("-", 1)[0] + "-" for r in lm.RULES if r.scope != "marker"}
        self.assertEqual(set(lm.FAMILY_PREFIXES.values()), prefixes)
        self.assertEqual(len(set(lm.FAMILY_PREFIXES.values())), len(lm.FAMILY_PREFIXES))
        for name in lm.FAMILY_PREFIXES:
            self.assertNotIn(name, mm.RENDER_CHECK_NAMES)

    def test_every_probe_is_live(self):
        self.assertEqual(lm.run_probes(notation=NOTATION), [])

    def test_a_dead_rule_is_reported(self):
        dead = lm.Rule(id="MA-TEST-01", severity="warn", title="t", hint="h", check=lambda f, c: [],
                       probe_fire=doc("flowchart TB\n  A --> B"), probe_quiet=doc("flowchart TB\n  A --> B"))
        self.assertEqual(lm.run_probes([dead], NOTATION), ["MA-TEST-01"])

    def test_a_rule_that_fires_on_its_quiet_probe_is_dead(self):
        noisy = lm.Rule(id="MA-TEST-02", severity="warn", title="t", hint="h", check=lambda f, c: [(1, "x")],
                        probe_fire=doc("flowchart TB\n  A --> B"), probe_quiet=doc("flowchart TB\n  A --> B"))
        self.assertEqual(lm.run_probes([noisy], NOTATION), ["MA-TEST-02"])


class TestTargetedCases(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        self.assertEqual(set(CASES), RULE_IDS)

    def test_cases(self):
        for rule_id, (fire, quiet) in CASES.items():
            with self.subTest(rule=rule_id):
                negative = rule(rule_id).probe_negative
                fired = run(fire, rule_id, negative=negative)
                self.assertTrue(fired, f"{rule_id} did not fire")
                self.assertTrue(all(f.rule == rule_id for f in fired))
                self.assertEqual(run(quiet, rule_id, negative=negative), [], f"{rule_id} fired on its quiet case")

    def test_every_finding_keeps_its_fence_line(self):
        for rule_id, (fire, _quiet) in CASES.items():
            with self.subTest(rule=rule_id):
                fences = {f.start: f for f in mm.extract_fences(fire)}
                for finding in run(fire, rule_id, negative=rule(rule_id).probe_negative):
                    self.assertIn(finding.fence, fences, finding)
                    fence = fences[finding.fence]
                    self.assertTrue(fence.start <= finding.line <= fence.end, finding)

    def test_more_parse_hazards(self):
        cases = {
            "MA-PARSE-01": ['flowchart TB\n  subgraph S [title (x)]\n    A\n    B\n  end',
                            "flowchart TB\n  A[/api/hooks] --> B", 'flowchart TB\n  A["Lesson"| --> B',
                            'flowchart TB\n  A[say "hi" now] --> B'],
            "MA-PARSE-03": ["flowchart TB\n  A -- CDP -- live --> B", "flowchart TB\n  A -->|x [y]| B"],
            "MA-PARSE-04": ["flowchart TB\n  A -->|List<T> x| B", 'flowchart TB\n  subgraph S["List<T>"]\n    A\n    B\n  end'],
            "MA-PARSE-06": ["sequenceDiagram\n  A->>B: a &lt;zone&gt; b", "sequenceDiagram\n  A->>B: step #1; done",
                            "sequenceDiagram\n  participant A as Team #1\n  A->>A: x"],
            "MA-PARSE-07": ["stateDiagram-v2\n  a --> b : #1; x", "stateDiagram-v2\n  a --> b : x: y",
                            'stateDiagram-v2\n  state "x #1; y" as a\n  a --> b'],
            "MA-PARSE-08": ["stateDiagram-v2\n  a --> b : one\\ntwo", "sequenceDiagram\n  Note over A: one\\ntwo"],
            "MA-STATE-02": ["stateDiagram-v2\n  a --> b\n  style a fill:#fff"],
        }
        for rule_id, bodies in cases.items():
            for body in bodies:
                with self.subTest(rule=rule_id, body=body):
                    self.assertTrue(run(doc(body), rule_id))

    def test_safe_constructs_stay_quiet(self):
        safe = [
            'flowchart TB\n  A["API (gateway)"] --> B["x; y #1 & z"]',
            "flowchart TB\n  A -- a-b (c) {d} --> B",
            'flowchart TB\n  A -->|"x (y)"| B\n  A -->|v2.0; a # b| C',
            "flowchart TB\n  End --> end1 --> endpoint",
            'flowchart TB\n  A["first\\nsecond<br/><small>x</small>"] --> B',
            "flowchart TB\n  A --o B\n  A--text-->C\n  C-.text.->D\n  D==text==>E",
            "sequenceDiagram\n  participant A\n  participant B\n  A->>B: a: b, List<T> (x)",
            "stateDiagram-v2\n  a --> b : call() x [y]\n  a : step #1 done",
            'stateDiagram-v2\n  state "waits: input; now" as a\n  a --> b',
            "stateDiagram-v2\n  Новый:::c --> b\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class a, b c",
            "gantt\n  dateFormat YYYY-MM-DD HH:mm\n  axisFormat %H:%M\n  todayMarker off\n  section S\n"
            "  fix #12; bug :a, 2024-01-01 10:00, 30m",
            "timeline\n  accTitle: Releases\n  2024 : first",
        ]
        parse_rules = [r for r in RULE_IDS if r.startswith(("MA-PARSE", "MA-SYN", "MA-GANTT-03", "MA-MODEL"))]
        for body in safe:
            with self.subTest(body=body):
                found = [f for f in run(doc(body)) if f.rule in parse_rules]
                self.assertEqual(found, [], body)


# --------------------------------------------------------------------------- engine and rules


class TestRuleDetails(unittest.TestCase):
    def test_phantom_needs_a_declared_participant(self):
        self.assertEqual(run(doc("sequenceDiagram\n  A->>B: x\n  B-->>A: y"), "MA-PARSE-09"), [])

    def test_phantom_from_a_typo_arrow(self):
        body = ("sequenceDiagram\n  participant O as Orchestrator\n  participant V as Validator\n"
                "  O->>V: validate\n  V--xFO: error log")
        found = run(doc(body), "MA-PARSE-09")
        self.assertEqual(len(found), 1)
        self.assertIn("FO", found[0].message)

    def test_v1_state_kind_is_avoided(self):
        self.assertTrue(run(doc("stateDiagram\n  a --> b"), "MA-SYN-04"))

    def test_budget_soft_and_hard_do_not_double_report(self):
        soft, hard = BUDGETS["flowchart"]["nodes"]
        over_hard = doc(chain(hard + 1))
        self.assertTrue(run(over_hard, "MA-BUDGET-02"))
        self.assertEqual([f for f in run(over_hard, "MA-BUDGET-01") if "nodes" in f.message], [])

    def test_planarity_runs_only_within_the_hard_budget(self):
        hard = BUDGETS["flowchart"]["edges"][1]
        k33 = "flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2 & B3\n  A3 --> B1 & B2 & B3"
        self.assertTrue(run(doc(k33), "MA-FLOW-05"))
        padding = "\n".join(f"  X{k} --> X{k + 1}" for k in range(hard))
        self.assertEqual(run(doc(k33 + "\n" + padding), "MA-FLOW-05"), [])

    def test_planarity_ignores_invisible_links(self):
        body = ("flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2 & B3\n  A3 --> B1 & B2\n  A3 ~~~ B3")
        self.assertEqual(run(doc(body), "MA-FLOW-05"), [])

    def test_edge_id_collision_message(self):
        found = run(doc("flowchart TB\n  a --> b_c\n  a_b --> c"), "MA-ID-01")
        self.assertEqual(len(found), 1)
        self.assertIn("L_a_b_c_0", found[0].message)

    def test_contrast_uses_both_pages_for_translucent_fills(self):
        ratio = lm._style_contrast({"fill": "#00000080", "color": "#FFFFFF"}, NOTATION)
        self.assertLess(ratio, lm._style_contrast({"fill": "#000000", "color": "#FFFFFF"}, NOTATION))
        self.assertAlmostEqual(lm.contrast_ratio((255, 255, 255), (0, 0, 0)), 21.0, places=3)

    def test_colour_forms(self):
        self.assertEqual(lm._rgba("#ABC"), (170, 187, 204, 1.0))
        self.assertEqual(lm._rgba("rgb(232, 240, 251)")[:3], (232.0, 240.0, 251.0))
        self.assertAlmostEqual(lm._rgba("rgba(127,127,127,0.10)")[3], 0.10)
        self.assertEqual(tuple(round(c) for c in lm._rgba("hsl(0, 0%, 100%)")[:3]), (255, 255, 255))
        self.assertEqual(tuple(round(c) for c in lm._rgba("hsl(120deg 100% 25%)")[:3]), (0, 128, 0))
        for value in ("none", "currentColor", "var(--x)", "rgb(1,2)", ""):
            self.assertIsNone(lm._rgba(value), value)
        self.assertEqual(lm._rgba("transparent"), (0, 0, 0, 0.0))

    def test_named_colours(self):
        """LM-15: a CSS colour name is a colour; `fill:yellow,color:white` measures 1.07:1."""
        self.assertEqual(len(lm._CSS_NAMED), 148)
        self.assertEqual(lm._rgba("lightblue"), (173, 216, 230, 1.0))
        self.assertEqual(lm._rgba("Yellow"), (255, 255, 0, 1.0))
        self.assertEqual(lm._rgba("rebeccapurple"), (102, 51, 153, 1.0))
        found = run(doc("flowchart TB\n  A:::warn --> B\n  classDef warn fill:yellow,color:white"), "MA-CLASS-01")
        self.assertEqual(len(found), 1)
        self.assertIn("1.07:1", found[0].message)
        self.assertTrue(run(doc("flowchart TB\n  A:::k --> B\n  classDef k fill:black"), "MA-CLASS-05"))
        self.assertEqual(run(doc("flowchart TB\n  A:::k --> B\n  classDef k fill:navy,color:white"), "MA-CLASS-01"), [])

    def test_palette_of_notation_passes_contrast(self):
        body = "flowchart TB\n  A --> B\n" + "\n".join(
            f"  classDef {name} {props}" for name, props in NOTATION["palette"]["flowchart"].items())
        self.assertEqual(run(doc(body), "MA-CLASS-01"), [])
        self.assertEqual(run(doc(body), "MA-CLASS-05"), [])

    def test_notation_settings_lines_pass_the_settings_rules(self):
        bodies = {"flowchart": "flowchart TB\n  A --> B", "state": "stateDiagram-v2\n  a --> b",
                  "sequence": "sequenceDiagram\n  A->>B: x", "er": "erDiagram\n  A ||--o{ B : has",
                  "gantt": GANTT + "  section S\n  t1 :a, 0, 3ms", "class": "classDiagram\n  A <|-- B",
                  "requirement": "requirementDiagram\n  element e1 {\n    type: service\n  }"}
        for kind, body in bodies.items():
            with self.subTest(kind=kind):
                text = doc(NOTATION["settings"][kind] + "\n" + body)
                found = [f for f in run(text) if f.rule.startswith("MA-SET")]
                self.assertEqual(found, [], kind)

    def test_class_and_requirement_settings_need_the_pinned_line(self):
        for body in ("classDiagram\n  A <|-- B", "requirementDiagram\n  element e1 {\n    type: x\n  }"):
            with self.subTest(body=body):
                self.assertTrue(run(doc(body), "MA-SET-06"))

    def test_gantt_after_below(self):
        body = GANTT + "  section S\n  t2 :b, after c, 2ms\n  t3 :c, 0, 4ms"
        found = run(doc(body), "MA-GANTT-01")
        self.assertEqual(len(found), 1)
        self.assertIn("below", found[0].message)

    def test_edge_label_case_rule_keeps_acronyms_and_uncased_scripts(self):
        for label in ("SQL rows", "HTTP", "读取数据", "v2 sync", "читает"):
            self.assertEqual(run(doc(f'flowchart TB\n  A -->|"{label}"| B'), "MA-LABEL-07"), [], label)
        for label in ("Reads", "REJECT moat", "Ünder"):
            self.assertTrue(run(doc(f'flowchart TB\n  A -->|"{label}"| B'), "MA-LABEL-07"), label)

    def test_a_name_the_figure_draws_keeps_its_case(self):
        """STI-40: an edge label may start with a name that a node, state, entity or group label
        of the figure shows, in the same case; a common word still fires."""
        quiet = ['flowchart LR\n  P[Producer] -->|Kafka topic| K[Kafka]',
                 "flowchart LR\n  P -->|Kafka topic| Kafka",
                 'flowchart LR\n  subgraph S["Kafka cluster"]\n    a\n    b\n  end\n  P -->|Kafka topic| a',
                 "stateDiagram-v2\n  Idle --> Busy : Busy signal",
                 'erDiagram\n  CUSTOMER["Customer"] {\n    int id\n  }\n  CUSTOMER ||--o{ ORDER : "Customer places"']
        for body in quiet:
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-LABEL-07"), [])
        loud = ['flowchart LR\n  P[Producer] -->|Kafka topic| K[kafka]',
                'flowchart LR\n  P[Producer] -->|Kafka topic| K[Broker]',
                'flowchart LR\n  P[Producer] -->|Sends data| K[Kafka]',
                'flowchart LR\n  P[Сервис] -->|Отправка в Kafka| K[Kafka]']
        for body in loud:
            with self.subTest(body=body):
                self.assertEqual(ids(run(doc(body), "MA-LABEL-07")), ["MA-LABEL-07"])
        self.assertIn("names", rule("MA-LABEL-07").hint)

    def test_the_subgraph_edge_hint_states_the_measured_behaviour(self):
        """RF-03: both ends of a subgraph edge sit on box borders; no arbitrary node is picked."""
        hint = rule("MA-FLOW-02").hint
        self.assertNotIn("arbitrary", hint)
        self.assertIn("box border", hint)

    def test_chart_kinds_whose_fills_merge_into_the_page_are_avoided(self):
        """STI-30: pie, xychart-beta and sankey-beta pass both checks while their fills merge into
        the light or the dark page (other-kinds.md §14); the lint points to a table."""
        self.assertEqual(NOTATION["kinds"]["avoid"].count("pie"), 1)
        for body in ('pie\n  "A4" : 70\n  "A3" : 30',
                     "xychart-beta\n  x-axis [Mon, Tue]\n  bar [12, 30]",
                     "sankey-beta\ngateway,decoder,120"):
            with self.subTest(kind=body.split()[0]):
                found = run(doc(body), "MA-SYN-04")
                self.assertEqual(ids(found), ["MA-SYN-04"])
                self.assertEqual(found[0].severity, "warn")
        for kind in ("pie", "xychart-beta", "sankey-beta"):
            self.assertNotIn(kind, NOTATION["kinds"]["allowed"])
        self.assertIn("a table", rule("MA-SYN-04").hint)

    def test_findings_are_sorted_by_line(self):
        text = doc("flowchart TB\n  A[x (y)] --> B\n  C --> end")
        lines = [f.line for f in run(text)]
        self.assertEqual(lines, sorted(lines))

    def test_mmd_lines_and_whole_figure_findings(self):
        text = "flowchart TB\n  A[x (y)] --> B\n"
        found = run(text, is_mmd=True)
        parse = [f for f in found if f.rule == "MA-PARSE-01"]
        self.assertEqual((parse[0].line, parse[0].fence), (2, 0))
        settings = [f for f in found if f.rule == "MA-SET-06"]
        self.assertEqual(settings[0].line, 0)
        self.assertFalse({"MA-DOC-01", "MA-DOC-02", "MA-DOC-05"} & set(ids(found)))


class TestTextFigureMarker(unittest.TestCase):
    """TASK R2.5, R6.1: only a `text figure` fence is an ASCII figure."""

    BAD = "root\n└──\tleaf\n" + "x" * (NOTATION["ascii"]["max_columns"] + 20)

    def test_fence_specs(self):
        specs = mm.FIGURE_LANGS
        for info, wanted in (("text figure", True), ("text title=x figure", True), ("Text FIGURE", True),
                             ("mermaid", True), ("text", False), ("figure text", False),
                             ("textfigure", False), ("text figures", False), ("python figure", False),
                             ("", False)):
            with self.subTest(info=info):
                self.assertEqual(mm.fence_matches(info, specs), wanted)
        self.assertTrue(mm.fence_matches("", ("",)))
        self.assertFalse(mm.fence_matches("text", ("",)))
        self.assertTrue(mm.fence_matches("text", ("mermaid", "text")))

    def test_a_plain_text_fence_is_never_a_figure(self):
        text = f"**Figure 1.** A log.\n\n```text\n{self.BAD}\n```\n\nNext.\n"
        self.assertEqual(mm.extract_fences(text), [])
        self.assertEqual(run(text), [])
        no_caption = f"## Output\n\n```text\n{self.BAD}\n```\n"
        self.assertEqual(run(no_caption), [])

    def test_a_text_figure_fence_is_linted(self):
        found = run(doc(self.BAD, ASCII))
        self.assertEqual(ids(found), ["MA-ASCII-01", "MA-ASCII-03"])
        fence = mm.extract_fences(doc(self.BAD, ASCII))[0]
        self.assertEqual((fence.lang, fence.info), ("text", "text figure"))

    def test_a_caller_may_read_every_text_fence(self):
        text = f"**Figure 1.** A chain.\n\n```text\n{self.BAD}\n```\n\nLegend.\n"
        self.assertEqual(ids(run(text, langs=("mermaid", "text"))), ["MA-ASCII-01", "MA-ASCII-03"])
        fig = mm.parse_document(text, ("mermaid", "text"))[0]
        self.assertEqual(fig.kind, "ascii")

    def test_a_non_mermaid_fence_a_caller_asks_for_is_ascii(self):
        fig = mm.parse_figure(mm.Fence(lang="txt", start=1, end=3, body="a -> b"))
        self.assertEqual((fig.kind, fig.ascii is not None), ("ascii", True))

    def test_an_ascii_figure_needs_a_caption_above(self):
        self.assertEqual(ids(run(f"## Tree\n\n```{ASCII}\nroot\n└── leaf\n```\n")), ["MA-DOC-01"])
        self.assertEqual(ids(run(f"```{ASCII}\nroot\n└── leaf\n```\n\n**Figure 2.** Below.\n")), ["MA-DOC-05"])
        self.assertEqual(run(f"**Figure 2.** Above.\n\n```{ASCII}\nroot\n└── leaf\n```\n"), [])


class TestCaptionAndLegendByPosition(unittest.TestCase):
    """TASK R3.7, D13, L1: caption directly above, legend directly below, in any language."""

    BODY = ("flowchart TB\n  A:::ext --> B:::wf\n  classDef ext fill:#FFFFFF,color:#263238\n"
            "  classDef wf fill:#E8F0FB,color:#0F2A47")
    PLAIN = "flowchart TB\n  A --> B"

    def doc_rules(self, text):
        return [f for f in run(text) if f.rule in ("MA-DOC-01", "MA-DOC-02", "MA-DOC-05")]

    def test_english(self):
        text = doc(self.BODY, caption="**Figure 3.** Containers — who calls whom.",
                   legend="Legend: dashed border = external system; blue = owned workflow.")
        self.assertEqual(self.doc_rules(text), [])

    def test_russian(self):
        text = doc(self.BODY, caption="**Рисунок 3.** Контейнеры — кто кого вызывает.",
                   legend="Обозначения: пунктирная рамка — внешняя система; синий — свой процесс.")
        self.assertEqual(self.doc_rules(text), [])

    def test_words_do_not_matter(self):
        for caption, legend in (("Schema.", "Notes."), ("图 3。容器。", "图例：虚线 = 外部。"),
                                ("- list item caption", "| a | b |\n| - | - |")):
            with self.subTest(caption=caption):
                self.assertEqual(self.doc_rules(doc(self.BODY, caption=caption, legend=legend)), [])

    def test_heading_is_not_a_caption_in_any_language(self):
        for heading in ("## Containers", "### Контейнеры"):
            text = f"{heading}\n\n```mermaid\nflowchart TB\n  A --> B\n```\n"
            self.assertEqual(ids(self.doc_rules(text)), ["MA-DOC-01"])

    def test_caption_above_alone_is_enough_without_encodings(self):
        self.assertEqual(self.doc_rules(f"**Рисунок 1.** Подпись.\n\n```mermaid\n{self.PLAIN}\n```\n\n## Далее\n"), [])

    def test_legend_missing_below(self):
        text = f"**Рисунок 1.** Контейнеры.\n\n```mermaid\n{self.BODY}\n```\n\n## Далее\n"
        self.assertEqual(ids(self.doc_rules(text)), ["MA-DOC-02"])

    def test_caption_below_is_a_warning(self):
        text = f"```mermaid\n{self.PLAIN}\n```\n\n**Рисунок 1.** Подпись снизу.\n"
        found = self.doc_rules(text)
        self.assertEqual(ids(found), ["MA-DOC-05"])
        self.assertEqual(found[0].severity, "warn")
        self.assertIn("caption below the fence", found[0].message)

    def test_paragraph_below_a_figure_with_encodings_is_its_legend(self):
        text = f"## Containers\n\n```mermaid\n{self.BODY}\n```\n\nLegend: two classes.\n"
        self.assertEqual(ids(self.doc_rules(text)), ["MA-DOC-01"])

    def test_no_neighbours_and_encodings(self):
        text = f"## Containers\n\n```mermaid\n{self.BODY}\n```\n\n## Next\n"
        self.assertEqual(ids(self.doc_rules(text)), ["MA-DOC-01", "MA-DOC-02"])


class TestDuplicateEdges(unittest.TestCase):
    """TASK R3.3: one edge per node pair; a decision flow and a state diagram one per direction."""

    def flow(self, body):
        return run(doc("flowchart TB\n" + body), "MA-FLOW-01")

    def test_opposite_edges_without_a_decision_node(self):
        self.assertEqual(len(self.flow("  A --> B\n  B --> A")), 1)

    def test_opposite_edges_in_a_decision_flow(self):
        self.assertEqual(self.flow('  D{"ok?"} -->|yes| E\n  E -->|retry| D'), [])

    def test_same_direction_in_a_decision_flow(self):
        found = self.flow('  D{"ok?"} -->|yes| E\n  D -->|no| E')
        self.assertEqual(len(found), 1)
        self.assertIn("in this direction", found[0].message)

    def test_a_third_edge_in_a_decision_flow(self):
        self.assertEqual(len(self.flow("  D{x} --> E\n  E --> D\n  D -.-> E")), 1)

    def test_an_open_or_two_headed_edge_claims_both_directions(self):
        self.assertEqual(len(self.flow("  D{x} --- E\n  E --> D")), 1)
        self.assertEqual(len(self.flow("  D{x} <--> E\n  D --> E")), 1)

    def test_reversed_arrow_is_the_same_direction(self):
        self.assertEqual(len(self.flow("  D{x} --> E\n  E <--- D")), 1)

    def test_invisible_links_do_not_count(self):
        self.assertEqual(self.flow("  A --> B\n  A ~~~ B"), [])

    def test_state_diagram(self):
        st = lambda body: run(doc("stateDiagram-v2\n" + body), "MA-STATE-03")  # noqa: E731
        self.assertEqual(st("  a --> b\n  b --> a"), [])
        self.assertEqual(len(st("  a --> b : go\n  a --> b : again")), 1)
        self.assertEqual(st("  state W {\n    [*] --> x\n  }\n  state H {\n    [*] --> y\n  }\n  [*] --> W"), [])
        self.assertEqual(run(doc("stateDiagram-v2\n  a --> b\n  a --> b"), "MA-FLOW-01"), [])


class TestLabelLimits(unittest.TestCase):
    """TASK D25, D26: characters per line, lines split at <br/>, from notation.labels."""

    def test_message_lines_are_split_at_br(self):
        n = LABELS["sequence_message_chars_max"]
        ok = "sequenceDiagram\n  A->>B: " + "m" * n + "<br/>" + "m" * n
        self.assertEqual(run(doc(ok), "MA-LABEL-04"), [])
        self.assertEqual(run(doc(ok), "MA-LABEL-09"), [])
        long = "sequenceDiagram\n  A->>B: " + "m" * n + "<br/>" + "m" * (n + 1)
        self.assertEqual(len(run(doc(long), "MA-LABEL-04")), 1)

    def test_participant_name_with_and_without_alias(self):
        n = LABELS["participant_chars_max"]
        self.assertTrue(run(doc(f"sequenceDiagram\n  participant {'P' * (n + 1)}\n  A->>A: x"), "MA-LABEL-10"))
        self.assertTrue(run(doc(f"sequenceDiagram\n  A->>{'Q' * (n + 1)}: x"), "MA-LABEL-10"))
        self.assertEqual(run(doc(f"sequenceDiagram\n  participant A as {'Ж' * n}\n  A->>A: x"), "MA-LABEL-10"), [])

    def test_node_lines(self):
        n = LABELS["node_label_lines_max"]
        self.assertTrue(run(doc(f'flowchart TB\n  A["{br_lines(n + 1)}"] --> B'), "MA-LABEL-08"))
        self.assertEqual(run(doc(f'flowchart TB\n  A["{br_lines(n)}"] --> B'), "MA-LABEL-08"), [])

    def test_note_lines_in_a_sequence(self):
        n = LABELS["note_lines_max"]
        body = "sequenceDiagram\n  participant A\n  Note over A: {}"
        self.assertTrue(run(doc(body.format(br_lines(n + 1))), "MA-LABEL-11"))
        self.assertEqual(run(doc(body.format(br_lines(n))), "MA-LABEL-11"), [])


class TestMeasuredRules(unittest.TestCase):
    """Rules measured against 10.9.8, 11.17.2 and 12.1.0 on 2026-10-02."""

    def test_bidirectional_sequence_arrows(self):
        for arrow in ("<<->>", "<<-->>"):
            for body in (f"  A{arrow}B: sync", f"  A {arrow} B: sync"):
                with self.subTest(body=body):
                    found = run(doc("sequenceDiagram\n  participant A\n  participant B\n" + body), "MA-SYN-06")
                    self.assertEqual(len(found), 1)
                    self.assertIn("A<<", found[0].message)

    def test_hex_colours_in_rect_and_box(self):
        bad = ["  rect #E8F0FB\n    A->>A: x\n  end", "  box #FFF Backend\n    participant A\n  end"]
        good = ["  rect rgba(127,127,127,0.10)\n    A->>A: x\n  end", "  rect rgb(232,240,251)\n    A->>A: x\n  end",
                "  box LightGrey Backend\n    participant A\n  end", "  box Backend\n    participant A\n  end"]
        for body in bad:
            self.assertTrue(run(doc("sequenceDiagram\n" + body), "MA-SEQ-03"), body)
        for body in good:
            self.assertEqual(run(doc("sequenceDiagram\n" + body), "MA-SEQ-03"), [], body)

    def test_styling_by_kind(self):
        bad = ["erDiagram\n  A ||--o{ B : has\n  classDef hot fill:#FFF4E0",
               "erDiagram\n  A ||--o{ B : has\n  class A hot",
               "erDiagram\n  A ||--o{ B : has\n  style A fill:#FFF4E0",
               "erDiagram\n  A:::hot ||--o{ B : has",
               "classDiagram\n  class Dog\n  classDef hot fill:#FFF4E0",
               "requirementDiagram\n  element e1 {\n    type: x\n  }\n  classDef hot fill:#FFF4E0",
               "requirementDiagram\n  element e1 {\n    type: x\n  }\n  class e1 hot",
               "requirementDiagram\n  element e1:::hot {\n    type: x\n  }"]
        good = ["classDiagram\n  class Dog:::hot\n  cssClass \"Dog\" hot\n  style Dog fill:#FFF4E0",
                "erDiagram\n  style ||--o{ ORDER : has\n  class ||--o{ ORDER : has",
                "erDiagram\n  A {\n    string class\n  }"]
        for body in bad:
            self.assertTrue(run(doc(body), "MA-SYN-08"), body)
        for body in good:
            self.assertEqual(run(doc(body), "MA-SYN-08"), [], body)

    def test_er_styling_does_not_add_entities(self):
        fig = mm.parse_figure(mm.figure_from_mmd("erDiagram\n  A:::hot ||--o{ B : has\n  class A hot"))
        self.assertEqual(sorted(fig.er.entities), ["A", "B"])

    def test_accessibility_statements_by_kind(self):
        bad = ["mindmap\n  accTitle: Topics\n  root((Guide))", "mindmap\n  accDescr {\n    x\n  }\n  root((G))",
               "sankey-beta\naccDescr: flows\nA,B,10"]
        good = ["timeline\n  accTitle: T\n  2024 : a", "flowchart TB\n  accTitle: T\n  A --> B"]
        for body in bad:
            self.assertTrue(run(doc(body), "MA-PARSE-15"), body)
        for body in good:
            self.assertEqual(run(doc(body), "MA-PARSE-15"), [], body)

    def test_state_class_ids(self):
        for ids_ in ("Готов", "a,Готов", "café", "a, 完成"):
            body = f"stateDiagram-v2\n  a --> b\n  classDef c fill:#E8F0FB,color:#0F2A47\n  class {ids_} c"
            self.assertTrue(run(doc(body), "MA-PARSE-16"), ids_)
        fig = mm.parse_figure(mm.figure_from_mmd("stateDiagram-v2\n  a --> b\n  class a, b c"))
        self.assertEqual((fig.state.states["a"].classes, fig.state.states["b"].classes), (["c"], ["c"]))
        self.assertEqual(fig.parse_errors, [])

    def test_quoted_state_labels(self):
        for body in ('a --> b : "go"', "a --> b : 'go'", 's1 : "Waiting"\n  s1 --> b'):
            self.assertTrue(run(doc("stateDiagram-v2\n  " + body), "MA-STATE-04"), body)
        for body in ('state "Waiting" as s1\n  s1 --> b', 'a --> b : say "go"'):
            self.assertEqual(run(doc("stateDiagram-v2\n  " + body), "MA-STATE-04"), [], body)

    def test_fill_without_color(self):
        fire = ["flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB",
                "flowchart TB\n  A --> B\n  style A fill:rgb(232\\,240\\,251)",
                "flowchart TB\n  A:::c --> B\n  classDef c fill:#37474F"]
        quiet = ["flowchart TB\n  A:::c --> B\n  classDef c fill:#7F7F7F0D,stroke:#90A4AE",
                 "flowchart TB\n  A:::c --> B\n  classDef c fill:none,stroke:#90A4AE",
                 "flowchart TB\n  A:::c --> B\n  classDef c stroke:#90A4AE,stroke-width:2px",
                 "flowchart TB\n  A:::c --> B\n  classDef c fill:#E8F0FB,color:#0F2A47"]
        for body in fire:
            self.assertTrue(run(doc(body), "MA-CLASS-05"), body)
        for body in quiet:
            self.assertEqual(run(doc(body), "MA-CLASS-05"), [], body)
        found = run(doc(fire[0]), "MA-CLASS-05")[0]
        self.assertIn("dark theme", found.message)
        self.assertNotIn("default theme", found.message)

    def test_settings_consistency_ignores_per_chart_gantt_keys(self):
        def gantt(extra):
            settings = {"gantt": dict({"barHeight": 16}, **extra)}
            return doc("%%{init: " + json.dumps(settings) + "}%%\n" + GANTT + "  section S\n  t1 :a, 0, 3ms")
        same = gantt({"useWidth": 900}) + "\n" + gantt({"useWidth": 600, "leftPadding": 80, "rightPadding": 20,
                                                         "topAxis": True})
        self.assertEqual(run(same, "MA-SET-07"), [])
        other = gantt({"useWidth": 900}) + "\n" + gantt({"useWidth": 900, "barHeight": 20})
        self.assertEqual(len(run(other, "MA-SET-07")), 1)

    def test_budgets_of_the_other_kinds(self):
        def classes(n):
            return "classDiagram\n" + "\n".join(f"  class C{k}" for k in range(n))

        def mindmap(n):
            return "mindmap\n  root((R))\n" + "\n".join(f"    n{k}" for k in range(n - 1))

        def timeline(n):
            return "timeline\n  title T\n" + "\n".join(f"  {2000 + k} : e{k}\n       : more" for k in range(n))

        def journey(n):
            return "journey\n  title T\n  section S\n" + "\n".join(f"    task {k}: 5: Me" for k in range(n))

        def gitgraph(n):
            return "gitGraph\n" + "\n".join("  commit" for _ in range(n))

        makers = {("class", "classes"): classes, ("mindmap", "nodes"): mindmap,
                  ("timeline", "periods"): timeline, ("journey", "tasks"): journey,
                  ("gitgraph", "commits"): gitgraph}
        for (kind, metric), make in makers.items():
            soft, hard = BUDGETS[kind][metric]
            with self.subTest(kind=kind):
                self.assertEqual(run(doc(make(soft)), "MA-BUDGET-01"), [])
                # a soft budget equal to the hard one has no warning band: past it is an error
                self.assertEqual(bool(run(doc(make(soft + 1)), "MA-BUDGET-01")), soft < hard)
                self.assertEqual(run(doc(make(hard)), "MA-BUDGET-02"), [])
                self.assertTrue(run(doc(make(hard + 1)), "MA-BUDGET-02"))

    def test_class_count_reads_links_members_and_bodies(self):
        fig = mm.parse_figure(mm.figure_from_mmd(
            "classDiagram\n  class Decoder {\n    <<interface>>\n    +decode(frame) Reading\n  }\n"
            "  Decoder <|.. MqttDecoder\n  Decoder ..> Reading : returns\n  Animal : +int age\n"
            '  Shop "1" *-- "many" Item : holds\n  note for Shop "x"'))
        self.assertEqual(fig.counts, {"classes": 6})


class TestNegativeFences(unittest.TestCase):
    """The negative-fence marker: expected findings, MA-NEG-01, MA-NEG-02 and MA-NEG-03 (TASK R9.4,
    R6.7). A marker makes expected only the findings of the rules and families it names, and it
    counts only in the skill's references and test fixtures (LM-20, STI-01)."""

    CLEAN = "**Figure 1.** Clean.\n\n```mermaid\n" + SETTINGS_FLOW + "\nflowchart TB\n  A --> B\n```\n\nLegend.\n"

    def negative(self, body, names, settings=True):
        """A captioned negative fence; *settings* puts the flowchart settings line first, so the
        fence holds no finding besides the defect it shows."""
        head = SETTINGS_FLOW + "\n" if settings else ""
        return f"**Figure 2.** Negative.\n\n```mermaid\n{head}{body}\n  %% negative: {names}\n```\n\nLegend.\n"

    def test_marker_parsing(self):
        fence = mm.extract_fences("```mermaid\nflowchart TB\n  A --> B\n  %% negative: MA-FLOW-01 , crossings,\n\n```\n")[0]
        self.assertEqual((fence.negative.names, fence.negative.line, fence.negative.last),
                         (["MA-FLOW-01", "crossings"], 4, True))
        early = mm.extract_fences("```mermaid\n%% negative: x\nflowchart TB\n  A --> B\n```\n")[0]
        self.assertIsNone(early.negative)
        self.assertEqual([m.last for m in early.markers], [False])
        text_fence = mm.extract_fences(f"```{ASCII}\na -> b\n%% negative: x\n```\n")[0]
        self.assertEqual((text_fence.markers, text_fence.negative), ([], None))

    def test_name_classes(self):
        self.assertEqual(lm.classify_marker_name("MA-FLOW-02")[0], "rule")
        self.assertEqual(lm.classify_marker_name("ma-flow-02")[0], "rule")
        for name in ("budget", "BUDGET", "MA-BUDGET", "ma-budget"):
            kind, rules = lm.classify_marker_name(name)
            self.assertEqual(kind, "family")
            self.assertEqual({r.id for r in rules}, {"MA-BUDGET-01", "MA-BUDGET-02"})
        for name in mm.RENDER_CHECK_NAMES:
            self.assertEqual(lm.classify_marker_name(name), ("render", []))
        for name in ("MA-NEG-01", "MA-NEG-03", "neg", "MA-FLOW-99", "edge through node", "Crossings", ""):
            self.assertIsNone(lm.classify_marker_name(name), name)

    def test_findings_of_a_negative_fence_are_expected(self):
        text = self.CLEAN + "\n" + self.negative('flowchart TB\n  subgraph G["Grp"]\n    A\n    B\n  end\n  G --> C',
                                                  "MA-FLOW-02")
        found = run(text)
        self.assertEqual(counted(found), [])
        self.assertIn("MA-FLOW-02", ids([f for f in found if f.expected]))
        neg_start = mm.extract_fences(text)[1].start
        self.assertTrue(all(f.fence == neg_start for f in found if f.expected))

    def test_only_the_named_rules_are_expected(self):
        """LM-20: a marker naming one check leaves every other finding of the fence counted."""
        broken = 'flowchart TB\n  A[API (gateway)] --> end\n  classDef c fill:#FFFFFF,color:#EEEEEE\n  class A c'
        for names in ("legibility", "MA-SET-06", "set", "crossings", "MA-CLASS-01"):
            with self.subTest(names=names):
                found = run(self.negative(broken, names, settings=False))
                errors = {f.rule for f in counted(found) if f.severity == "error"}
                self.assertTrue({"MA-PARSE-01", "MA-PARSE-05"} <= errors, errors)
                named = {r.id for r in lm.classify_marker_name(names)[1]} if lm.classify_marker_name(names) else set()
                self.assertTrue(all(f.rule in named for f in found if f.expected), found)
        found = run(self.negative(broken, "MA-CLASS-01", settings=False))
        self.assertEqual(ids([f for f in found if f.expected]), ["MA-CLASS-01"])
        self.assertIn("MA-SET-06", ids(counted(found)))

    def test_family_and_render_names(self):
        k33 = "flowchart TB\n  A1 --> B1 & B2 & B3\n  A2 --> B1 & B2 & B3\n  A3 --> B1 & B2 & B3"
        found = run(self.negative(k33, "flow, crossings"))
        self.assertEqual(counted(found), [])
        self.assertEqual(ids([f for f in found if f.expected]), ["MA-FLOW-05"])
        self.assertEqual(counted(run(self.negative("flowchart TB\n  A --> B", "crossings, legibility"))), [])
        # a marker that names render checks only makes no lint finding expected
        bare = counted(run(self.negative("flowchart TB\n  A --> B", "crossings", settings=False)))
        self.assertEqual(ids(bare), ["MA-SET-06"])

    def test_a_negative_that_passes_is_an_error(self):
        found = counted(run(self.negative("flowchart TB\n  A --> B", "MA-FLOW-01, crossings")))
        self.assertEqual(ids(found), ["MA-NEG-01"])
        self.assertEqual(found[0].severity, "error")
        self.assertIn("MA-FLOW-01", found[0].message)

    def test_document_rules_on_a_negative_fence(self):
        bare = "flowchart TB\n  X --> Y"
        text = self.negative(bare, "MA-SET-07, MA-SET-06", settings=False) + "\n" + self.CLEAN + "\n" + self.CLEAN
        found = run(text)
        self.assertEqual(counted(found), [])
        expected = [f for f in found if f.expected and f.rule == "MA-SET-07"]
        self.assertEqual(len(expected), 1)
        self.assertEqual(expected[0].fence, mm.extract_fences(text)[0].start)
        self.assertEqual(ids(counted(run(self.negative(bare, "MA-SET-07") + "\n" + self.CLEAN))), ["MA-NEG-01"])

    def test_malformed_markers(self):
        cases = {"unknown": self.negative("flowchart TB\n  A --> B\n  B --> A", "MA-FLOW-01; crossings"),
                 "empty": self.negative("flowchart TB\n  A --> B\n  B --> A", ""),
                 "early": "**F.** x\n\n```mermaid\nflowchart TB\n  %% negative: MA-FLOW-01\n  A --> B\n  B --> A\n```\n\nL.\n"}
        for name, text in cases.items():
            with self.subTest(case=name):
                found = counted(run(text))
                self.assertIn("MA-NEG-02", ids(found))
        early = counted(run(cases["early"]))
        self.assertIn("MA-FLOW-01", ids(early))

    def test_trailing_blank_lines_and_mmd(self):
        text = SETTINGS_FLOW + "\nflowchart TB\n  A --> B\n  B --> A\n  %% negative: MA-FLOW-01\n\n"
        found = run(text, is_mmd=True)
        self.assertEqual(counted(found), [])
        self.assertIn("MA-FLOW-01", ids([f for f in found if f.expected]))

    def test_a_marker_outside_the_skill_counts_nothing(self):
        """STI-01: in a document outside references/ and scripts/tests/fixtures/ the marker is a
        counted error and every finding of the fence counts."""
        text = self.negative('flowchart TB\n  subgraph G["Grp"]\n    A\n    B\n  end\n  G --> C', "MA-FLOW-02")
        found = run(text, negative=False)
        self.assertEqual([f for f in found if f.expected], [])
        self.assertIn("MA-FLOW-02", ids(counted(found)))
        neg03 = [f for f in found if f.rule == "MA-NEG-03"]
        self.assertEqual((len(neg03), neg03[0].severity, neg03[0].expected), (1, "error", False))
        self.assertNotIn("MA-NEG-01", ids(found))
        early = "**F.** x\n\n```mermaid\nflowchart TB\n  %% negative: MA-FLOW-01\n  A --> B\n```\n\nL.\n"
        self.assertEqual(ids([f for f in run(early, negative=False) if f.rule.startswith("MA-NEG")]), ["MA-NEG-03"])

    def test_the_path_decides_where_markers_count(self):
        reference = mm.SKILL_DIR / "references" / "paired-examples.md"
        fixture = next((mm.SKILL_DIR / "scripts" / "tests" / "fixtures").glob("*.mmd"))
        self.assertTrue(mm.negative_allowed(reference))
        self.assertTrue(mm.negative_allowed(str(fixture)))
        self.assertTrue(mm.negative_allowed(mm.SKILL_DIR / "references" / ".." / "references" / "ascii.md"))
        for path in ("<text>", "<probe>", "answer.md", mm.SKILL_DIR / "SKILL.md",
                     mm.SKILL_DIR / "references" / "missing.md", mm.SKILL_DIR / "references"):
            with self.subTest(path=str(path)):
                self.assertFalse(mm.negative_allowed(path))
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp, "doc.md")
            outside.write_text(self.negative("flowchart TB\n  A --> B\n  B --> A", "MA-FLOW-01"), encoding="utf-8")
            self.assertFalse(mm.negative_allowed(outside))
            link = Path(tmp, "link.md")
            try:
                os.symlink(reference, link)
            except (OSError, NotImplementedError):
                link = None
            if link is not None:
                self.assertTrue(mm.negative_allowed(link))
            found = lm.lint_text(outside.read_text(encoding="utf-8"), str(outside), notation=NOTATION)
            self.assertIn("MA-FLOW-01", ids(counted(found)))
            self.assertIn("MA-NEG-03", ids(found))

    def test_a_marker_in_a_project_document_fails_the_gate(self):
        """STI-01: the marker alone fails a project document, even when it names a render check
        only and the fence holds no other finding: the lint exits 1."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "design.md")
            path.write_text(self.negative("flowchart TB\n  A --> B", "crossings"), encoding="utf-8")
            code, out, _ = call_main([str(path)])
            self.assertEqual(code, lm.EXIT_FINDINGS, out)
            self.assertIn("MA-NEG-03", out)
            found = lm.lint_text(path.read_text(encoding="utf-8"), str(path), notation=NOTATION)
            self.assertEqual([(f.rule, f.severity) for f in found], [("MA-NEG-03", "error")])

    def test_one_root_list_decides_for_every_instrument(self):
        """`negative_allowed` reads NEGATIVE_ROOTS when called: the lint and the render check
        share this one definition, and a test that moves the roots moves both."""
        roots = (mm.SKILL_DIR / "references", mm.SKILL_DIR / "scripts" / "tests" / "fixtures")
        self.assertEqual(mm.NEGATIVE_ROOTS, roots)
        reference = mm.SKILL_DIR / "references" / "ascii.md"
        saved = mm.NEGATIVE_ROOTS
        with tempfile.TemporaryDirectory() as tmp:
            inside = Path(tmp, "doc.md")
            inside.write_text("x\n", encoding="utf-8")
            mm.NEGATIVE_ROOTS = (Path(tmp),)
            try:
                self.assertEqual((mm.negative_allowed(inside), mm.negative_allowed(reference)), (True, False))
            finally:
                mm.NEGATIVE_ROOTS = saved
        self.assertTrue(mm.negative_allowed(reference))

    def test_markers_are_read_once_per_fence(self):
        """SEC-08: a fence with thousands of findings does not rescan its body per finding."""
        body = "flowchart TB\n" + "\n".join("  A --> B" for _ in range(3000))
        text = self.negative(body, "MA-FLOW-01")
        calls = []
        original = mm.negative_markers

        def counting(fence):
            calls.append(fence.start)
            return original(fence)
        mm.negative_markers = counting
        try:
            start = time.perf_counter()
            found = run(text)
            elapsed = time.perf_counter() - start
        finally:
            mm.negative_markers = original
        self.assertGreater(len([f for f in found if f.expected]), 1000)
        self.assertLess(len(calls), 10)
        self.assertLess(elapsed, 2.0, f"{elapsed:.2f} s")


# --------------------------------------------------------------------------- CLI


CLEAN = ("**Figure 1.** Two components.\n\n```mermaid\n" + SETTINGS_FLOW
         + '\nflowchart TB\n  api["API"] --> db[("Orders DB")]\n```\n\nLegend: cylinder = store.\n')
NEGATIVE = ("**Figure 2.** A boundary edge.\n\n```mermaid\n" + SETTINGS_FLOW
            + '\nflowchart TB\n  subgraph G["Grp"]\n    A\n    B\n  end\n  G --> C\n  %% negative: MA-FLOW-02\n```\n\n'
            "Legend: none.\n")


class TestCli(unittest.TestCase):
    """The files of these tests stand in for fixtures: their directory joins NEGATIVE_ROOTS, so
    their negative markers count. TestNegativeFences covers a document outside the roots."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.roots = mm.NEGATIVE_ROOTS
        mm.NEGATIVE_ROOTS = self.roots + (self.dir,)

    def tearDown(self):
        mm.NEGATIVE_ROOTS = self.roots
        self.tmp.cleanup()

    def write(self, name, text, encoding="utf-8"):
        path = self.dir / name
        path.write_bytes(text.encode(encoding) if isinstance(text, str) else text)
        return str(path)

    def test_exit_0_clean(self):
        code, out, _ = call_main([self.write("clean.md", CLEAN)])
        self.assertEqual(code, lm.EXIT_OK, out)
        self.assertIn("0 error / 0 warn / 0 expected", out)

    def test_exit_0_with_warnings_only(self):
        code, out, _ = call_main([self.write("warn.md", "## Title\n\n```mermaid\nflowchart TB\n  A --> B\n```\n")])
        self.assertEqual(code, lm.EXIT_OK)
        self.assertIn("MA-DOC-01 [fence 3]", out)

    def test_exit_1_error_finding(self):
        code, out, _ = call_main([self.write("bad.mmd", "flowchart TB\n  A[API (gateway)] --> B\n")])
        self.assertEqual(code, lm.EXIT_FINDINGS)
        self.assertIn("error MA-PARSE-01", out)

    def test_negative_fence_errors_set_no_exit_code(self):
        path = self.write("neg.md", CLEAN + "\n" + NEGATIVE)
        code, out, _ = call_main([path])
        self.assertEqual(code, lm.EXIT_OK, out)
        self.assertIn("expected on negative fences (not counted):", out)
        self.assertIn("error MA-FLOW-02 [fence 13]", out)
        self.assertTrue(out.rstrip().endswith("0 error / 0 warn / 1 expected"), out)

    def test_a_negative_that_passes_exits_1(self):
        path = self.write("neg.md", CLEAN + "\n" + NEGATIVE.replace("G --> C", "B --> C"))
        code, out, _ = call_main([path])
        self.assertEqual(code, lm.EXIT_FINDINGS)
        self.assertIn("error MA-NEG-01", out)

    def test_counts_per_file(self):
        a, b = self.write("a.md", CLEAN), self.write("b.md", CLEAN + "\n" + NEGATIVE)
        code, out, _ = call_main([a, b])
        self.assertEqual(code, lm.EXIT_OK)
        self.assertIn(f"{a}: 0 error / 0 warn / 0 expected", out)
        self.assertIn(f"{b}: 0 error / 0 warn / 1 expected", out)

    def test_exit_2_dead_rule(self):
        dead = lm.Rule(id="MA-TEST-01", severity="warn", title="t", hint="h", check=lambda f, c: [],
                       probe_fire="x", probe_quiet="x")
        lm.RULES.append(dead)
        try:
            code, _, err = call_main([self.write("clean.md", CLEAN)])
            probe_code, _, _ = call_main(["--probe"])
        finally:
            lm.RULES.remove(dead)
        self.assertEqual(code, lm.EXIT_INTERNAL)
        self.assertEqual(probe_code, lm.EXIT_INTERNAL)
        self.assertIn("MA-TEST-01", err)

    def test_exit_2_rule_fails_on_the_document(self):
        def check(fig, ctx):
            if ctx.path != "<probe>":
                raise RuntimeError("boom")
            return [(1, "x")] if "FIRE" in fig.fence.body else []
        broken = lm.Rule(id="MA-TEST-03", severity="warn", title="t", hint="h", check=check,
                         probe_fire=doc("flowchart TB\n  FIRE --> B"), probe_quiet=doc("flowchart TB\n  A --> B"))
        lm.RULES.append(broken)
        try:
            code, _, err = call_main([self.write("clean.md", CLEAN)])
        finally:
            lm.RULES.remove(broken)
        self.assertEqual(code, lm.EXIT_INTERNAL)
        self.assertIn("MA-TEST-03", err)

    def test_exit_2_notation_unreadable(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lm.main([self.write("clean.md", CLEAN)], notation_path=self.dir / "missing.json")
        self.assertEqual(code, lm.EXIT_INTERNAL)
        self.assertIn("notation", err.getvalue())

    def test_no_option_replaces_the_notation(self):
        """STI-05, SEC-06: the auto-approved command line cannot lint against relaxed budgets."""
        lenient = json.loads(json.dumps(NOTATION))
        lenient["budgets"]["flowchart"] = {"nodes": [100, 200], "edges": [100, 200]}
        path = self.dir / "lenient.json"
        path.write_text(json.dumps(lenient), encoding="utf-8")
        big = self.write("big.md", doc(SETTINGS_FLOW + "\n" + chain(BUDGETS["flowchart"]["nodes"][1] + 2)))
        self.assertEqual(call_main(["--notation", str(path), big])[0], lm.EXIT_USAGE)
        self.assertNotIn("--notation", lm.build_parser().format_help())
        self.assertEqual(call_main([big])[0], lm.EXIT_FINDINGS)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(lm.main([big], notation_path=path), lm.EXIT_OK)

    def test_exit_2_parser_failure(self):
        original = mm._parse_er
        mm._parse_er = lambda rows, fig: 1 / 0
        try:
            code, _, _ = call_main([self.write("er.md", doc("erDiagram\n  A ||--o{ B : has"))])
        finally:
            mm._parse_er = original
        self.assertEqual(code, lm.EXIT_INTERNAL)

    def test_exit_3_usage(self):
        self.assertEqual(call_main([])[0], lm.EXIT_USAGE)
        self.assertEqual(call_main(["--bogus", "x.md"])[0], lm.EXIT_USAGE)
        self.assertEqual(call_main([str(self.dir / "missing.md")])[0], lm.EXIT_USAGE)
        self.assertEqual(call_main([self.write("latin1.md", "caf\xe9".encode("latin-1"))])[0], lm.EXIT_USAGE)

    def test_help_exits_zero(self):
        self.assertEqual(call_main(["--help"])[0], lm.EXIT_OK)

    def test_probe_flag(self):
        code, out, _ = call_main(["--probe"])
        self.assertEqual(code, lm.EXIT_OK)
        self.assertIn(f"{len(RULE_IDS)}/{len(RULE_IDS)} rules live", out)

    def test_probe_with_paths_is_a_usage_error(self):
        """LM-28: `--probe docs/*.md` would otherwise pass without linting a file."""
        bad = self.write("bad.mmd", "flowchart TB\n  A[API (gateway)] --> B\n")
        for argv in (["--probe", bad], ["--probe", str(self.dir / "missing.md")], ["--probe", "--json"]):
            with self.subTest(argv=argv):
                code, out, err = call_main(argv)
                self.assertEqual(code, lm.EXIT_USAGE)
                self.assertIn("--probe", err)
                self.assertNotIn("rules live", out)

    def test_a_dead_fire_probe_among_several_is_reported(self):
        def check(fig, ctx):
            return [(1, "x")] if "ONE" in fig.fence.body else []
        rule_ = lm.Rule(id="MA-TEST-04", severity="warn", title="t", hint="h", check=check,
                        probe_fire=(doc("flowchart TB\n  ONE --> B"), doc("flowchart TB\n  TWO --> B")),
                        probe_quiet=doc("flowchart TB\n  A --> B"))
        self.assertEqual(lm.run_probes([rule_], NOTATION), ["MA-TEST-04"])
        rule_.probe_fire = (doc("flowchart TB\n  ONE --> B"),)
        self.assertEqual(lm.run_probes([rule_], NOTATION), [])

    def test_one_line_per_finding(self):
        """LM-32 (TASK R6.4): the hint sits on the finding's line."""
        bad = self.write("bad.md", "## Title\n\n```mermaid\nflowchart TB\n  A[x (y)] --> end\n```\n")
        code, out, _ = call_main([bad])
        self.assertEqual(code, lm.EXIT_FINDINGS)
        lines = out.rstrip("\n").split("\n")
        findings = lines[:-1]
        self.assertTrue(findings)
        self.assertTrue(all(line.startswith(bad + ":") for line in findings), lines)
        self.assertFalse(any(line.startswith(" ") for line in lines), lines)
        parse = next(line for line in findings if "MA-PARSE-01" in line)
        self.assertIn(" → Quote the label", parse)
        total = lm.counts(lm.lint_text(Path(bad).read_text(encoding="utf-8"), bad, notation=NOTATION))
        self.assertEqual(len(findings), total["error"] + total["warn"])

    def test_exit_codes_distinct(self):
        self.assertEqual(len({lm.EXIT_OK, lm.EXIT_FINDINGS, lm.EXIT_INTERNAL, lm.EXIT_USAGE}), 4)

    def test_json_shape(self):
        bad = self.write("bad.mmd", "flowchart TB\n  A[API (gateway)] --> B\n")
        neg = self.write("neg.md", CLEAN + "\n" + NEGATIVE)
        code, out, _ = call_main(["--json", bad, neg])
        self.assertEqual(code, lm.EXIT_FINDINGS)
        data = json.loads(out)
        self.assertEqual(data["schema"], "mermaid-lint/v1")
        self.assertEqual(set(data), {"schema", "files", "rules", "counts", "per_file", "findings", "expected"})
        self.assertEqual(data["rules"], len(RULE_IDS))
        self.assertEqual(data["files"], [bad, neg])
        self.assertEqual(set(data["counts"]), {"error", "warn", "expected"})
        self.assertGreaterEqual(data["counts"]["error"], 1)
        for f in data["findings"] + data["expected"]:
            self.assertEqual(set(f), {"rule", "severity", "path", "line", "fence", "message", "hint"})
        self.assertEqual(data["counts"]["error"], sum(1 for f in data["findings"] if f["severity"] == "error"))
        self.assertEqual(data["counts"]["expected"], len(data["expected"]))
        self.assertEqual({f["rule"] for f in data["expected"]}, {"MA-FLOW-02"})
        self.assertTrue(all(f["fence"] == 13 for f in data["expected"]))
        self.assertEqual(data["per_file"][neg], {"error": 0, "warn": 0, "expected": 1})
        self.assertEqual([f["fence"] for f in data["findings"] if f["path"] == bad], [0] * sum(
            1 for f in data["findings"] if f["path"] == bad))

    def test_inventory_columns(self):
        text = doc('flowchart TB\n  subgraph G["Gate"]\n    A["API v2"]\n    B[(Store)]\n  end\n'
                   '  A -->|"writes 3 rows"| B')
        path = self.write("inv.md", text)
        code, out, _ = call_main(["--inventory", path])
        self.assertEqual(code, lm.EXIT_OK)
        self.assertIn("| kind | id | text | line | support |", out)
        code, out, _ = call_main(["--inventory", "--json", path])
        rows = json.loads(out)["figures"][0]["rows"]
        self.assertTrue(all(set(r) == {"kind", "id", "text", "line", "support"} for r in rows))
        self.assertTrue(all(r["support"] == "" for r in rows))
        kinds = {r["kind"] for r in rows}
        self.assertTrue({"group", "node", "edge", "label", "number"} <= kinds, kinds)
        numbers = {r["text"] for r in rows if r["kind"] == "number"}
        self.assertTrue({"2", "3"} <= numbers, numbers)

    def test_inventory_kinds_per_diagram(self):
        figures = mm.parse_document(
            doc("sequenceDiagram\n  participant A as Api\n  participant B\n  rect rgba(127,127,127,0.10)\n"
                "  A->>B: call\n  end\n  Note over A: waits") + "\n"
            + doc("stateDiagram-v2\n  state W {\n    a --> b : go\n  }") + "\n"
            + doc(GANTT + "  section Build\n  compile :c1, 0, 2ms"))
        kinds = [{r["kind"] for r in lm.inventory(f)} for f in figures]
        self.assertTrue({"node", "message", "note", "group"} <= kinds[0], kinds[0])
        self.assertTrue({"node", "transition", "group"} <= kinds[1], kinds[1])
        self.assertTrue({"task", "group"} <= kinds[2], kinds[2])


# The guard runs the lint in a fresh interpreter with an audit hook that records every write-mode
# open and every file-system change (TASK R6: the lint writes no file). Hooks cannot be removed,
# so the guard never runs inside the test process.
GUARD = r"""
import json, os, sys
sys.path.insert(0, {scripts!r})
WRITE = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
CHANGES = {{"os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.symlink", "os.link", "os.truncate",
           "os.chmod", "os.chown", "os.utime", "shutil.copyfile", "shutil.copytree", "shutil.move",
           "shutil.rmtree", "tempfile.mkstemp", "tempfile.mkdtemp"}}
seen = []
def hook(event, args):
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & WRITE):
            seen.append([event, str(path)])
    elif event in CHANGES:
        seen.append([event, str(args[0]) if args else ""])
sys.addaudithook(hook)
{body}
sys.stderr.write("\nGUARD " + json.dumps({{"code": code, "writes": seen}}) + "\n")
"""


class TestWritesNoFile(unittest.TestCase):
    def guard(self, body, cwd):
        code = GUARD.format(scripts=str(SCRIPTS), body=body)
        proc = subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True, text=True,
                              timeout=120)
        line = next(x for x in proc.stderr.splitlines() if x.startswith("GUARD "))
        return json.loads(line[len("GUARD "):])

    def test_the_guard_sees_a_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self.guard("open('written.txt', 'w').write('x')\ncode = 0", tmp)
        self.assertTrue(report["writes"])

    def test_the_lint_writes_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "doc.md").write_text(CLEAN + "\n" + NEGATIVE + "\n" + doc("a -> b", ASCII), encoding="utf-8")
            Path(tmp, "fig.mmd").write_text("flowchart TB\n  A[x (y)] --> B\n", encoding="utf-8")
            before = sorted(p.name for p in Path(tmp).iterdir())
            for argv in (["doc.md"], ["--json", "doc.md", "fig.mmd"], ["--inventory", "doc.md"],
                         ["--inventory", "--json", "fig.mmd"], ["--probe"]):
                with self.subTest(argv=argv):
                    report = self.guard(f"import lint_mermaid\ncode = lint_mermaid.main({argv!r})", tmp)
                    self.assertEqual(report["writes"], [], argv)
                    self.assertIn(report["code"], (lm.EXIT_OK, lm.EXIT_FINDINGS))
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), before)


class TestPerformance(unittest.TestCase):
    """TASK R6.8: one document in under 2 seconds."""

    @staticmethod
    def document(total=500, count=20):
        """A document of *total* lines holding *count* figures of six kinds, each with a caption
        above and a legend below, and text lines between them."""
        bodies = [
            SETTINGS_FLOW + "\nflowchart TB\n" + "\n".join(f'  N{k}["Node {k}"] -->|"step {k}"| N{k + 1}["Node {k + 1}"]'
                                                       for k in range(1, 15)),
            NOTATION["settings"]["sequence"] + "\nsequenceDiagram\n  autonumber\n"
            + "\n".join(f"  participant P{k} as Part {k}" for k in range(1, 7))
            + "\n" + "\n".join(f"  P{1 + k % 5}->>P{2 + k % 5}: call {k}" for k in range(16)),
            NOTATION["settings"]["state"] + "\nstateDiagram-v2\n  [*] --> s1\n"
            + "\n".join(f"  s{k} --> s{k + 1} : go {k}" for k in range(1, 12)),
            GANTT + "  section Build\n" + "\n".join(f"  task {k} :t{k}, {k * 2}, 2ms" for k in range(14)),
            "erDiagram\n" + "\n".join(f"  E{k} ||--o{{ E{k + 1} : has" for k in range(7)),
        ]
        blocks = []
        for k in range(count):
            tree = k % 6 == 5
            body = "root\n├── a\n│   └── b\n└── c" if tree else bodies[k % len(bodies)]
            block = [f"**Figure {k + 1}.** Figure number {k + 1}.", "", f"```{ASCII if tree else 'mermaid'}",
                     body, "```", "", "Legend: one encoding per item.", ""]
            blocks.append("\n".join(block).split("\n"))
        lines = ["# Performance document", ""]
        spare = total - len(lines) - sum(len(b) for b in blocks)
        for k, block in enumerate(blocks):
            lines += block
            share = spare // count + (1 if k < spare % count else 0)
            lines += [f"Text line {j} after figure {k + 1}." for j in range(share - 1)] + [""] * min(share, 1)
        return "\n".join(lines) + "\n", count

    def test_a_500_line_document_with_20_figures(self):
        text, figures = self.document()
        self.assertEqual(text.count("\n"), 500)
        self.assertEqual(len(mm.extract_fences(text)), figures)
        self.assertEqual(figures, 20)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "big.md")
            path.write_text(text, encoding="utf-8")
            start = time.perf_counter()
            code, _out, _err = call_main([str(path)])
            elapsed = time.perf_counter() - start
        self.assertIn(code, (lm.EXIT_OK, lm.EXIT_FINDINGS))
        self.assertLess(elapsed, 2.0, f"{elapsed:.2f} s")


# --------------------------------------------------------------------------- model


class TestFences(unittest.TestCase):
    def test_backtick_tilde_info_string_and_lines(self):
        text = ("a\n\n```mermaid title=x\nflowchart TB\n```\n\n~~~text figure\nx -> y\n~~~\n\n~~~text\nlog\n~~~\n\n"
                "```python\nprint()\n```\n")
        fences = mm.extract_fences(text)
        self.assertEqual([(f.lang, f.start, f.end) for f in fences], [("mermaid", 3, 5), ("text", 7, 9)])
        self.assertEqual(fences[0].body, "flowchart TB")
        self.assertEqual(fences[0].body_start, 4)
        self.assertEqual(fences[0].info, "mermaid title=x")

    def test_crlf_and_byte_order_mark(self):
        fences = mm.extract_fences("﻿Caption.\r\n\r\n```mermaid\r\nflowchart TB\r\n  A --> B\r\n```\r\nLegend.\r\n")
        self.assertEqual((fences[0].start, fences[0].end, fences[0].body), (3, 6, "flowchart TB\n  A --> B"))
        self.assertEqual(fences[0].after.text, "Legend.")
        fig = mm.parse_figure(mm.figure_from_mmd("﻿flowchart TB\r\n  A --> B\r\n"))
        self.assertEqual((fig.kind, len(fig.flowchart.edges)), ("flowchart", 1))

    def test_fence_inside_a_longer_fence_is_not_a_figure(self):
        text = "````markdown\n```mermaid\nflowchart TB\n```\n````\n"
        self.assertEqual(mm.extract_fences(text), [])

    def test_fence_inside_an_html_comment_is_not_a_figure(self):
        text = "<!--\n```mermaid\nflowchart TB\n```\n-->\n"
        self.assertEqual(mm.extract_fences(text), [])

    def test_indented_fence_in_a_list(self):
        text = "1. Step\n\n   ```mermaid\n   flowchart TB\n     A --> B\n   ```\n"
        fence = mm.extract_fences(text)[0]
        self.assertEqual(fence.body, "flowchart TB\n  A --> B")

    def test_unclosed_fence_runs_to_the_end(self):
        fence = mm.extract_fences("```mermaid\nflowchart TB\n  A --> B\n")[0]
        self.assertIn("A --> B", fence.body)
        self.assertIsNone(fence.after)

    def test_neighbour_paragraphs(self):
        text = ("# Title\n\nIntro line one\nintro line two\n\n```mermaid\nflowchart TB\n```\n"
                "- legend a\n- legend b\n\nNext.\n")
        fence = mm.extract_fences(text)[0]
        self.assertEqual((fence.before.start, fence.before.end), (3, 4))
        self.assertEqual(fence.after.text, "- legend a\n- legend b")

    def test_no_neighbour_across_two_blank_lines_a_heading_a_comment_or_a_fence(self):
        cases = [
            "Caption.\n\n\n```mermaid\nflowchart TB\n```\n",
            "## Heading\n```mermaid\nflowchart TB\n```\n",
            "Caption.\n<!-- note -->\n```mermaid\nflowchart TB\n```\n",
            "```text\nx\n```\n```mermaid\nflowchart TB\n```\n",
            "Setext heading\n---\n```mermaid\nflowchart TB\n```\n",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertIsNone(mm.extract_fences(text)[-1].before)

    def test_setext_heading_below_is_not_a_legend(self):
        fence = mm.extract_fences("```mermaid\nflowchart TB\n```\nNext section\n============\n")[0]
        self.assertIsNone(fence.after)


class TestSettings(unittest.TestCase):
    def figure(self, body):
        return mm.parse_figure(mm.figure_from_mmd(body))

    def test_directive_single_quotes_and_position(self):
        fig = self.figure("flowchart TB\n%%{init: {'look': 'classic'}}%%\n  A --> B")
        self.assertEqual(fig.settings.config, {"look": "classic"})
        self.assertEqual(fig.settings.line, 2)
        self.assertEqual(fig.kind, "flowchart")

    def test_multiline_directive(self):
        fig = self.figure('%%{init: {\n  "look": "classic"\n}}%%\nflowchart TB\n  A --> B')
        self.assertEqual(fig.settings.config, {"look": "classic"})
        self.assertEqual(len(fig.flowchart.edges), 1)

    def test_malformed_directive(self):
        fig = self.figure('%%{init: {"look": "classic",}}%%\nflowchart TB\n  A --> B')
        self.assertIsNone(fig.settings.config)
        self.assertIn("JSON", fig.settings.error)

    def test_frontmatter_config_and_directive_wins(self):
        fig = self.figure('---\ntitle: T\nconfig:\n  look: classic\n  themeVariables:\n    primaryColor: "#ff0000"\n---\n'
                          'flowchart TB\n  A --> B')
        self.assertEqual(fig.settings.form, "frontmatter")
        self.assertEqual(fig.settings.config["themeVariables"]["primaryColor"], "#ff0000")
        both = self.figure('---\nconfig:\n  look: neo\n---\n%%{init: {"look": "classic"}}%%\nflowchart TB\n  A --> B')
        self.assertEqual(both.settings.form, "directive")
        self.assertEqual(len(both.settings_blocks), 2)

    def test_yaml_errors(self):
        bad = ["config:\n  theme: base\n    look: classic", "config:\n\tlook: classic",
               "config:\n  look: classic\n  look: neo", 'config:\n  theme: "base', "config:\n  theme base",
               "config:\n  look: %x", "config:\n  look:classic",
               "config:\n  themeVariables:\n    primaryColor: #E8F0FB"]
        for yaml in bad:
            with self.subTest(yaml=yaml):
                fig = self.figure(f"---\n{yaml}\n---\nflowchart TB\n  A --> B")
                self.assertTrue(fig.settings_blocks[0].error, yaml)

    def test_yaml_subset(self):
        data = mm.parse_yaml('a: 1\nb: true\nc: "x: y"\nd: {k: v, n: [1, 2]}\ne:\n  - one\n  - two: 2\n'
                             "f: plain words # comment\ng: |\n  line one\n  line two")
        self.assertEqual(data, {"a": 1, "b": True, "c": "x: y", "d": {"k": "v", "n": [1, 2]},
                                "e": ["one", {"two": 2}], "f": "plain words", "g": "line one\nline two"})

    def test_yaml_that_js_yaml_accepts(self):
        good = ["config:\n  look: &l classic\n  flowchart:\n    curve: basis",
                'config:\n  themeVariables: {\n    lineColor: "#546E7A"\n  }',
                'title: "a long\n  title"\nconfig:\n  look: classic']
        for yaml in good:
            with self.subTest(yaml=yaml):
                fig = self.figure(f"---\n{yaml}\n---\nflowchart TB\n  A --> B")
                self.assertIsNone(fig.settings_blocks[0].error, yaml)
                self.assertIsInstance(fig.settings.config, dict)

    def test_unclosed_frontmatter(self):
        fig = self.figure("---\nconfig:\n  look: classic\nflowchart TB\n  A --> B")
        self.assertIn("closing", fig.settings_blocks[0].error)


class TestKindsAndLabels(unittest.TestCase):
    def test_detect_kind(self):
        cases = {
            "graph TD;\n  A-->B": ("flowchart", "graph"),
            "%% c\n%%{init: {}}%%\n---\nx\n": ("unknown", "---"),
            "---\ntitle: x\n---\n%% note\nstateDiagram-v2\n  a --> b": ("state", "stateDiagram-v2"),
            "stateDiagram\n  a --> b": ("state", "stateDiagram"),
            "sequenceDiagram": ("sequence", "sequenceDiagram"),
            "mindmap\n  root": ("mindmap", "mindmap"),
            "foobar": ("unknown", "foobar"),
            "": ("unknown", ""),
        }
        for body, expected in cases.items():
            with self.subTest(body=body):
                self.assertEqual(mm.detect_kind(body), expected)

    def test_label_lines(self):
        self.assertEqual(mm.label_lines("Name<br/><small>role · tech</small>"), ["Name", "role · tech"])
        self.assertEqual(mm.label_lines("a<br>b\\nc"), ["a", "b", "c"])
        self.assertEqual(mm.label_lines("say #quot;hi#quot; #35;1"), ['say "hi" #1'])
        self.assertEqual(mm.label_lines("`**bold** text`"), ["bold text"])
        self.assertEqual(mm.label_lines(""), [])

    def test_counts(self):
        self.assertEqual(mm.word_count("один два  три"), 3)
        self.assertEqual(mm.char_count("Ёлка"), 4)
        self.assertEqual(mm.display_width("名前ab"), 6)


class TestParsers(unittest.TestCase):
    def fig(self, body):
        return mm.parse_figure(mm.figure_from_mmd(body))

    def test_flowchart_structure(self):
        fig = self.fig('flowchart LR\n  subgraph O["Outer"]\n    X(["x"])\n    subgraph I [Inner]\n      Y[(y)] --> Z{{z}}\n'
                       '    end\n    X --> Y\n  end\n  W & V --> X:::c\n  X -.->|lbl| W ==> V ~~~ W\n'
                       "  A <--> B\n  classDef c fill:#FFFFFF,color:#263238\n  style W fill:#FFFFFF\n  linkStyle 0 stroke:#546E7A")
        fc = fig.flowchart
        self.assertEqual(fc.direction, "LR")
        self.assertEqual(fc.subgraphs["I"].members, ["Y", "Z"])
        self.assertEqual(fc.subgraphs["I"].parent, "O")
        self.assertEqual(fc.subgraphs["O"].members, ["X", "I"])
        self.assertEqual(fc.nodes["X"].shape, "stadium")
        self.assertEqual(fc.nodes["Y"].shape, "cylinder")
        self.assertEqual(fc.nodes["Z"].shape, "hexagon")
        self.assertEqual(fc.nodes["X"].classes, ["c"])
        self.assertEqual(fc.nodes["Y"].parent, "I")
        pairs = [(e.src, e.dst, e.style, e.arrow, e.label) for e in fc.edges]
        self.assertIn(("W", "X", "solid", "->", ""), pairs)
        self.assertIn(("V", "X", "solid", "->", ""), pairs)
        self.assertIn(("X", "W", "dotted", "->", "lbl"), pairs)
        self.assertIn(("W", "V", "thick", "->", ""), pairs)
        self.assertIn(("V", "W", "invisible", "none", ""), pairs)
        self.assertIn(("A", "B", "solid", "<->", ""), pairs)
        self.assertEqual(fc.styles[0]["target"], "W")
        self.assertEqual(fc.link_styles[0]["index"], "0")
        self.assertEqual(fig.parse_errors, [])

    def test_flowchart_text_link_forms(self):
        fc = self.fig("flowchart TB\n  A -- calls --> B\n  B == main ==> C\n  C -. nudge .-> D\n  D --- E\n  E --o F").flowchart
        self.assertEqual([(e.label, e.style, e.arrow) for e in fc.edges],
                         [("calls", "solid", "->"), ("main", "thick", "->"), ("nudge", "dotted", "->"),
                          ("", "solid", "none"), ("", "solid", "->")])

    def test_quoted_pipe_label_may_hold_a_bar_and_quoted_labels_may_span_lines(self):
        fig = self.fig('flowchart LR\n  D -->|"|delta| <= sigma"| N["one\ntwo (x)"]\n  A["first line\nsecond (y)"] ~~~ B')
        self.assertEqual([(e.src, e.dst, e.label) for e in fig.flowchart.edges],
                         [("D", "N", "|delta| <= sigma"), ("A", "B", "")])
        self.assertEqual(mm.label_lines(fig.flowchart.nodes["A"].label), ["first line", "second (y)"])
        self.assertEqual((fig.hazards, fig.parse_errors), ([], []))

    def test_edge_ids(self):
        fc = self.fig("flowchart TB\n  a --> b\n  a --> b\n  a --> b").flowchart
        self.assertEqual(mm.flowchart_edge_ids(fc), ["L_a_b_0", "L_a_b_2", "L_a_b_3"])

    def test_sequence(self):
        seq = self.fig("sequenceDiagram\n  box rgba(127,127,127,0.08) Backend\n  participant A as Api\n  actor U as User\n  end\n"
                       "  autonumber\n  U->>+A: call\n  alt ok\n    A-->>-U: reply\n  else fail\n    A--xU: error\n  end\n"
                       "  Note over A,U: done\n  rect rgba(127,127,127,0.10)\n    A->>C: implicit\n  end").sequence
        self.assertEqual([(p.id, p.label, p.kind, p.box, p.declared) for p in seq.participants],
                         [("A", "Api", "participant", "Backend", True), ("U", "User", "actor", "Backend", True),
                          ("C", "", "participant", None, False)])
        self.assertTrue(seq.autonumber)
        self.assertEqual([(m.src, m.dst, m.arrow, m.activate) for m in seq.messages],
                         [("U", "A", "->>", "+"), ("A", "U", "-->>", "-"), ("A", "U", "--x", ""), ("A", "C", "->>", "")])
        self.assertEqual(sorted(b.kind for b in seq.blocks), ["alt", "box", "rect"])
        self.assertEqual(seq.notes[0].over, ["A", "U"])

    def test_state(self):
        sd = self.fig('stateDiagram-v2\n  direction LR\n  [*] --> idle\n  state "Running job" as run {\n    [*] --> a\n'
                      "    a --> b : step\n  }\n  state pick <<choice>>\n  idle --> pick\n  pick --> run : go\n"
                      "  run --> [*]\n  idle:::wait\n  classDef wait fill:#FFFFFF,color:#263238\n"
                      "  note right of idle : waits").state
        self.assertEqual(sd.direction, "LR")
        self.assertTrue(sd.states["run"].composite)
        self.assertEqual(sd.states["run"].label, "Running job")
        self.assertEqual(sd.states["a"].parent, "run")
        self.assertEqual(sd.states["pick"].kind, "choice")
        self.assertEqual(sd.states["idle"].classes, ["wait"])
        self.assertIn(("a", "b", "step"), [(t.src, t.dst, t.label) for t in sd.transitions])
        self.assertEqual(sd.notes[0].text, "waits")

    def test_gantt(self):
        g = self.fig(GANTT + "  title Plan\n  section Build\n  compile :crit, done, c1, 0, 2ms\n"
                     "  link :l1, after c1, 3ms\n  section Ship\n  ship :milestone, s1, after l1, 0ms").gantt
        self.assertEqual((g.date_format, g.axis_format, g.today_marker), ("x", "%Q", "off"))
        self.assertEqual(g.sections, ["Build", "Ship"])
        self.assertEqual([(t.id, t.tags, t.start, t.duration) for t in g.tasks],
                         [("c1", ["crit", "done"], "0", "2ms"), ("l1", [], "after c1", "3ms"),
                          ("s1", ["milestone"], "after l1", "0ms")])
        self.assertEqual(mm.gantt_refs(g.tasks[1]), ["c1"])

    def test_er(self):
        er = self.fig('erDiagram\n  CUSTOMER ||--o{ ORDER : places\n  ORDER {\n    int id PK\n  }\n'
                      '  ORDER }|..|{ LINE : "has lines"').er
        self.assertEqual(sorted(er.entities), ["CUSTOMER", "LINE", "ORDER"])
        self.assertEqual(er.entities["ORDER"].attributes, ["int id PK"])
        self.assertEqual([(r.a, r.b, r.cardinality, r.label) for r in er.relations],
                         [("CUSTOMER", "ORDER", "||--o{", "places"), ("ORDER", "LINE", "}|..|{", "has lines")])

    def test_ascii(self):
        fence = mm.Fence(lang="text", start=1, end=7,
                         body="+------+     +----+\n| api  | --> | db  |\n+------+     +----+\n\tcache 名前")
        block = mm.parse_figure(fence).ascii
        self.assertEqual(len(block.boxes), 2)
        self.assertEqual(block.boxes[1].ragged, [3])
        self.assertEqual(block.tabs, [5])
        self.assertEqual(block.wide, [5])
        self.assertEqual([t for _l, t in block.elements], ["api", "db", "cache 名前"])

    def test_bad_input_never_raises(self):
        for body in ("flowchart TB\n  A -->", "sequenceDiagram\n  ???", "stateDiagram-v2\n  }", "gantt\n  x",
                     "erDiagram\n  !!", "flowchart TB\n  subgraph S\n  A", "%%{init: }%%",
                     "classDiagram\n  }\n  }", "mindmap", "gitGraph\n  merge", "requirementDiagram\n  {{{"):
            with self.subTest(body=body):
                fig = self.fig(body)
                self.assertFalse(any(e.get("internal") for e in fig.parse_errors), fig.parse_errors)


# --------------------------------------------------------------------------- review round 1


def ascii_block(body):
    return mm.parse_figure(mm.Fence(lang="text", start=0, end=0, body=body, info=ASCII)).ascii


class TestAsciiColumns(unittest.TestCase):
    """LM-01, STI-02: ascii.md §8 reports a box side or a vertical connector that changes column
    between lines, in both character sets; correct figures stay quiet."""

    DRIFTED_BOXES = {
        "left side": "+------+\n| api  |\n | db  |\n+------+",
        "bottom corner": "+------+\n| api  |\n +------+",
        "left side, box drawing": "┌──────┐\n│ api  │\n │ db  │\n└──────┘",
        "bottom corner, box drawing": "┌──────┐\n│ api  │\n └──────┘",
        "bottom border one column left": "  +------+\n  | api  |\n +------+",
        "bottom border one column left, box drawing": "  ┌──────┐\n  │ api  │\n └──────┘",
        "bottom border one column left, two rows": "  +------+\n  | api  |\n  | db   |\n +------+",
        "two stacked boxes one column apart": "  +------+\n  | api  |\n +------+\n | db   |\n +------+",
    }
    #: A cell divider one column off the `+` of the border above it, in the first row under the
    #: top border, with the number of cells the figure holds: the cells stay apart, and the row
    #: reports its right border.
    DRIFTED_DIVIDERS = {
        "table header divider one column right": (
            "+----+-------+\n| id  | name |\n+----+-------+\n|  1 | alice |\n|  2 | bob   |\n+----+-------+", 6),
        "table header divider one column left": (
            "+-------+--------+\n| stage| status  |\n+-------+--------+\n| lint  | ok     |\n"
            "+-------+--------+", 4),
        "2x2 grid, first row": ("+----+----+\n| a   | b |\n+----+----+\n| c  | d  |\n+----+----+", 4),
        "1-row grid": ("+----+----+\n| a   | b |\n+----+----+", 2),
    }
    DRIFTED_CONNECTORS = {
        "tree": "print server\n├── spooler\n │   └── job queue\n├── renderer",
        "chain": "sensor\n  │ MQTT\n   ▼\ngateway",
        "chain, pure ASCII": "sensor\n  |\n   v\ngateway",
        "fork": ("gateway --> decoder --+--> raw store ---------+--> batch ack\n"
                 "                      |                       |\n"
                 "                       +--> threshold check ---+"),
        "fork, box drawing": ("gateway ──▶ decoder ──┬──▶ raw store ─────────┬──▶ batch ack\n"
                              "                       └──▶ threshold check ───┘"),
        "connector under a box": "┌─────┐\n│ api │\n└──┬──┘\n    │\n┌──┴──┐\n│ db  │\n└─────┘",
    }
    CORRECT = {
        "chain": "sensor ──MQTT──▶ gateway ──AMQP──▶ broker ──▶ decoder ──▶ time-series store",
        "chain down": "sensor\n  │ MQTT\n  ▼\ngateway\n  │ AMQP\n  ▼\nbroker",
        "fork": ("gateway ──▶ decoder ──┬──▶ raw store ─────────┬──▶ batch ack\n"
                 "                      └──▶ threshold check ───┘"),
        "fork, pure ASCII": ("gateway --> decoder --+--> raw store ---------+--> batch ack\n"
                             "                      |                       |\n"
                             "                      +--> threshold check ---+"),
        "tree": ("print server\n├── spooler\n│   └── job queue\n├── renderer\n└── drivers\n"
                 "    ├── laser\n    └── label"),
        "directory": ("library-app/\n├── docs/\n├── src/\n│   ├── loans/       loan rules and due dates\n"
                      "│   └── members/     member records\n└── tests/"),
        "mapping": "loan.created   ──▶ reminder service\nloan.overdue   ──▶ fines service",
        "boxes": "+------+     +----+\n| api  | --> | db |\n+------+     +----+",
        "connector under a box": "┌─────┐\n│ api │\n└──┬──┘\n   │\n┌──┴──┐\n│ db  │\n└─────┘",
        "connectors leave a pure-ASCII box": (
            "+------------+    +-----+\n| Upload API |    | CDN |\n+-----+------+    +--+--+\n"
            "      | writes       | reads\n      v              v\n+------------------------+\n"
            "|      Media bucket      |\n+------------------------+"),
        "grid": "┌────┬────┐\n│ a  │ b  │\n├────┼────┤\n│ c  │ d  │\n└────┴────┘",
        "pure-ASCII grid": "+----+----+\n| a  | b  |\n+----+----+\n| c  | d  |\n+----+----+",
        "pure-ASCII table": ("+----+-------+\n| id | name  |\n+----+-------+\n|  1 | alice |\n|  2 | bob   |\n"
                             "+----+-------+"),
        "pure-ASCII table, three columns": ("+------+------+------+\n| id   | name | note |\n"
                                            "+------+------+------+\n| 1    | a    | x    |\n+------+------+------+"),
        "boxes that share a corner": ("+------+------+\n| api  | db   |\n+------+------+\n       |\n       v\n"
                                      "    +------+\n    | log  |\n    +------+"),
        "a connector into the corner of a grid": "     |\n+----+----+\n| a  | b  |\n+----+----+",
        "a box on a wider box": "+------+\n| api  |\n+---------+\n| plat    |\n+---------+",
        "a box on a box one column wider on each side": " +------+\n | api  |\n+--------+\n| plat   |\n+--------+",
        "a fork and a join down the page": (
            "build site\n  |\n  +------------------+\n  |                  |\n  v                  v\n"
            "link check     accessibility check\n  |                  |\n  +------------------+\n  |\n  v\n"
            "deploy preview"),
        "a fork and a join down the page, stem in the middle": (
            "     build site\n          |\n +--------+--------+\n |                 |\n v                 v\n"
            "link check   accessibility check\n |                 |\n +--------+--------+\n          |\n"
            "          v\n    deploy preview"),
    }
    ASCII_RULES = ("MA-ASCII-04", "MA-ASCII-07")

    def ascii_findings(self, body):
        return [f for f in run(doc(body, ASCII)) if f.rule in self.ASCII_RULES]

    def test_drifted_box_borders(self):
        for name, body in self.DRIFTED_BOXES.items():
            with self.subTest(case=name):
                found = self.ascii_findings(body)
                self.assertEqual(ids(found), ["MA-ASCII-04"])
                self.assertIn("left side or bottom corner", found[0].message)
        box = ascii_block(self.DRIFTED_BOXES["left side"]).boxes[0]
        self.assertEqual((box.bottom, box.shifted, box.ragged), (4, [3], []))

    def test_drifted_connectors(self):
        for name, body in self.DRIFTED_CONNECTORS.items():
            with self.subTest(case=name):
                self.assertEqual(ids(self.ascii_findings(body)), ["MA-ASCII-07"])
        self.assertEqual(ascii_block(self.DRIFTED_CONNECTORS["chain"]).drift, [(2, 3)])

    def test_correct_figures_stay_quiet(self):
        for name, body in self.CORRECT.items():
            with self.subTest(case=name):
                self.assertEqual(self.ascii_findings(body), [])

    def test_the_figures_of_ascii_md_stay_quiet(self):
        text = (mm.SKILL_DIR / "references" / "ascii.md").read_text(encoding="utf-8")
        figures = [f for f in mm.parse_document(text) if f.kind == "ascii"]
        self.assertGreaterEqual(len(figures), 7)
        found = [f for f in lm.lint_text(text, "ascii.md", notation=NOTATION) if f.rule.startswith("MA-ASCII")]
        self.assertEqual(found, [])

    def test_a_right_border_still_reports_its_lines(self):
        found = self.ascii_findings("+------+\n| api |\n| db   |\n+------+")
        self.assertEqual(ids(found), ["MA-ASCII-04"])
        self.assertIn("right border", found[0].message)

    def test_a_drifted_cell_divider_is_reported(self):
        """A divider one column off the `+` above it ends the cell all the same: the cells stay
        apart, and the cell reports its right border (wave 1b verification, Q16)."""
        for name, (body, cells) in self.DRIFTED_DIVIDERS.items():
            with self.subTest(case=name):
                found = self.ascii_findings(body)
                self.assertEqual(ids(found), ["MA-ASCII-04"])
                self.assertIn("right border", found[0].message)
                self.assertEqual(len(ascii_block(body).elements), cells)
        header = ascii_block(self.DRIFTED_DIVIDERS["table header divider one column right"][0])
        self.assertEqual([t for _l, t in header.elements][:2], ["id", "name"])

    def test_a_cell_right_of_a_drifted_divider_keeps_its_first_letter(self):
        """A divider one column left of its `+` leaves the next cell whole in `elements` and in
        `--inventory`; the row still reports its right border (wave 1c verification)."""
        cases = {
            "table header divider one column left": (
                self.DRIFTED_DIVIDERS["table header divider one column left"][0],
                ["stage", "status", "lint", "ok"]),
            "id table, divider one column left": (
                "+----+-------+\n| id| name   |\n+----+-------+\n|  1 | alice |\n|  2 | bob   |\n"
                "+----+-------+", ["id", "name", "1", "alice", "2", "bob"]),
            "table header divider one column right": (
                self.DRIFTED_DIVIDERS["table header divider one column right"][0],
                ["id", "name", "1", "alice", "2", "bob"]),
        }
        for name, (body, cells) in cases.items():
            with self.subTest(case=name):
                self.assertEqual([t for _l, t in ascii_block(body).elements], cells)
                self.assertEqual(ids(self.ascii_findings(body)), ["MA-ASCII-04"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "table.md"
            path.write_text(doc(cases["table header divider one column left"][0], ASCII), encoding="utf-8")
            code, out, err = call_main(["--inventory", str(path)])
            self.assertEqual(code, lm.EXIT_OK, out + err)
            self.assertIn("status", out.split())
            self.assertNotIn("tatus", out.split())

    def test_a_pure_ascii_table_keeps_one_element_per_cell(self):
        """R1: a `+` between two cells is the corner of each, not a junction the border runs past."""
        table = ascii_block(self.CORRECT["pure-ASCII table"])
        self.assertEqual([t for _l, t in table.elements], ["id", "name", "1", "alice", "2", "bob"])
        self.assertEqual([(b.left, b.right, b.ragged) for b in table.boxes], [(0, 5, [])])
        corner = ascii_block(self.CORRECT["a connector into the corner of a grid"])
        self.assertEqual([t for _l, t in corner.elements], ["a", "b"])
        self.assertEqual(run(doc(self.CORRECT["pure-ASCII table"], "text"), langs=("text",)), [])

    def test_a_junction_without_a_side_under_it_is_passed(self):
        """A pure-ASCII `+` with no cell side next to it is a junction, with or without a connector."""
        for bottom in ("+-----+------+", "+-----+-+----+"):
            with self.subTest(bottom=bottom):
                box = ascii_block("+------------+\n| Upload API |\n" + bottom).boxes[0]
                self.assertEqual((box.right, box.ragged, box.bottom), (13, [], 3))

    def test_a_fork_drawn_down_the_page_is_no_box(self):
        """Its sides reach no bottom border, so its `v` heads are arrowheads, not elements."""
        for name in ("a fork and a join down the page", "a fork and a join down the page, stem in the middle"):
            with self.subTest(case=name):
                block = ascii_block(self.CORRECT[name])
                self.assertEqual(block.boxes, [])
                self.assertEqual([t for _l, t in block.elements],
                                 ["build site", "link check", "accessibility check", "deploy preview"])


class TestAsciiElements(unittest.TestCase):
    """LM-02, LM-03, STI-15: an arrowhead is no element; over 12 elements is an error."""

    def test_a_pure_ascii_down_arrowhead_is_no_element(self):
        chain = "sensor\n  |\n  v\ngateway\n  |\n  v\nbroker\n  |\n  v\ndecoder\n  |\n  v\nstore"
        block = ascii_block(chain)
        self.assertEqual([t for _l, t in block.elements], ["sensor", "gateway", "broker", "decoder", "store"])
        self.assertEqual(run(doc(chain, ASCII), "MA-ASCII-05"), [])
        same = ascii_block(chain.replace("|", "│").replace("v", "▼"))
        self.assertEqual(len(same.elements), len(block.elements))
        self.assertEqual([t for _l, t in ascii_block("v2 api\nv").elements], ["v2 api", "v"])

    def test_geometric_arrowheads_split_runs(self):
        self.assertEqual([t for _l, t in ascii_block("a ▶ b ▶ c").elements], ["a", "b", "c"])
        figure_1 = "sensor ──MQTT──▶ gateway ──AMQP──▶ broker ──▶ decoder ──▶ time-series store"
        self.assertEqual([t for _l, t in ascii_block(figure_1).elements],
                         ["sensor", "MQTT", "gateway", "AMQP", "broker", "decoder", "time-series store"])

    def test_hard_budget_is_an_error(self):
        soft, hard = BUDGETS["ascii"]["elements"]
        self.assertEqual((soft, hard), (8, 12))  # TASK D14

        def chain(n):
            return doc(" -> ".join(f"s{k}" for k in range(1, n + 1)), ASCII)
        over = run(chain(hard + 1))
        self.assertEqual([(f.rule, f.severity) for f in over if f.rule in ("MA-ASCII-05", "MA-ASCII-06")],
                         [("MA-ASCII-06", "error")])
        within = run(chain(hard))
        self.assertEqual([(f.rule, f.severity) for f in within if f.rule in ("MA-ASCII-05", "MA-ASCII-06")],
                         [("MA-ASCII-05", "warn")])
        self.assertEqual([f for f in run(chain(soft)) if f.rule in ("MA-ASCII-05", "MA-ASCII-06")], [])
        self.assertEqual(lm.counts(over)["error"], 1)

    def test_each_layer_of_a_stack_is_an_element(self):
        """R2: `├────┤` ends a layer as `+----+` does, so both character sets count each layer."""
        names = [f"layer {k}" for k in range(1, 15)]
        width = 24

        def stack(top, left, right, side, bottom):
            rows = [top[0] + "─" * width + top[1]]
            for k, name in enumerate(names):
                rows.append(side + " " + name.ljust(width - 1) + side)
                last = k == len(names) - 1
                rows.append((bottom[0] if last else left) + "─" * width + (bottom[1] if last else right))
            return "\n".join(rows)
        drawn = stack("┌┐", "├", "┤", "│", "└┘")
        pure = stack("++", "+", "+", "|", "++").replace("─", "-")
        for body in (drawn, pure):
            with self.subTest(body=body[:30]):
                self.assertEqual([t for _l, t in ascii_block(body).elements], names)
                self.assertEqual(ids(run(doc(body, ASCII), "MA-ASCII-06")), ["MA-ASCII-06"])
        three = "┌──────┐\n│ web  │\n├──────┤\n│ api  │\n├──────┤\n│ db   │\n└──────┘"
        self.assertEqual([t for _l, t in ascii_block(three).elements], ["web", "api", "db"])
        side = "┌──────┐\n│ api  ├──▶ db\n└──────┘"
        self.assertEqual([t for _l, t in ascii_block(side).elements], ["api", "db"])
        self.assertEqual(run(doc(side, ASCII), "MA-ASCII-04"), [])

    def test_each_box_inside_a_box_is_an_element(self):
        """R2-08: a box drawn inside a box is an element of its own, at any depth, so a grid in
        a container box meets the budget as a flat grid does."""
        def container(n, pure):
            h, v, tl, tr, bl, br = ("-", "|", "+", "+", "+", "+") if pure else ("─", "│", "┌", "┐", "└", "┘")
            rows = []
            for r in range(0, n, 4):
                cells = [f"S{k:02d}" for k in range(r, min(r + 4, n))]
                rows += [" ".join(tl + h * 6 + tr for _ in cells), " ".join(f"{v} {c}  {v}" for c in cells),
                         " ".join(bl + h * 6 + br for _ in cells)]
            width = max(len(x) for x in rows) + 2
            return "\n".join([tl + h * width + tr, v + " Cluster".ljust(width) + v]
                             + [v + " " + x.ljust(width - 1) + v for x in rows] + [bl + h * width + br])
        for pure in (False, True):
            with self.subTest(pure=pure):
                block = ascii_block(container(16, pure))
                self.assertEqual([t for _l, t in block.elements], ["Cluster"] + [f"S{k:02d}" for k in range(16)])
                self.assertEqual(ids(run(doc(container(16, pure), ASCII), "MA-ASCII-06")), ["MA-ASCII-06"])
                self.assertEqual(len(ascii_block(container(2, pure)).elements), 3)
        unlabelled = ("┌──────────────────────┐\n│ ┌──────┐   ┌──────┐  │\n│ │ api  │──▶│ db   │  │\n"
                      "│ └──────┘   └──────┘  │\n│  note: replicated    │\n└──────────────────────┘")
        self.assertEqual([t for _l, t in ascii_block(unlabelled).elements], ["note: replicated", "api", "db"])
        deep = ("+--------------------+\n| outer              |\n| +----------------+ |\n| | middle         | |\n"
                "| | +------+       | |\n| | | core |       | |\n| | +------+       | |\n| +----------------+ |\n"
                "+--------------------+")
        self.assertEqual([t for _l, t in ascii_block(deep).elements], ["outer", "middle", "core"])
        drifted = ("┌──────────────┐\n│ host         │\n│ ┌──────┐     │\n│ │ api  │     │\n│  └──────┘    │\n"
                   "└──────────────┘")
        self.assertEqual([(f.rule, f.line) for f in run(doc(drifted, ASCII), "MA-ASCII-04")], [("MA-ASCII-04", 8)])


class TestAsciiWidth(unittest.TestCase):
    """LM-24, LM-25: an emoji in emoji presentation takes two columns; a mapping's arrow column
    makes its lines aligned."""

    def test_vs16_emoji_is_double_width(self):
        warning = "\u26a0\ufe0f"  # U+26A0 is East Asian Width N; VS16 asks for the emoji
        self.assertEqual(mm.display_width(warning), 2)
        self.assertEqual(mm.display_width("\u26a0"), 1)
        self.assertEqual(mm.char_widths("a" + warning + "b"), [1, 1, 1, 1])
        body = "+--------+\n| " + warning + " api  |\n+--------+"
        self.assertEqual(ids([f for f in run(doc(body, ASCII)) if f.rule.startswith("MA-ASCII")]),
                         ["MA-ASCII-02", "MA-ASCII-04"])

    def test_a_cjk_label_in_a_pure_ascii_mapping(self):
        for body in ("注文作成      -> reminder service\nloan.overdue  -> fines service",
                     "注文作成          -> reminder service\nloan.overdue  -> fines service"):
            with self.subTest(body=body):
                self.assertTrue(run(doc(body, ASCII), "MA-ASCII-02"))
        self.assertEqual(run(doc("注文作成 is a label", ASCII), "MA-ASCII-02"), [])


class TestAsciiLegend(unittest.TestCase):
    """LM-16, STI-39: a fork and a join are the second encoding of an ASCII figure."""

    FORK = ("gateway ──▶ decoder ──┬──▶ raw store ─────────┬──▶ batch ack\n"
            "                      └──▶ threshold check ───┘")

    def test_fork_and_join_need_a_legend(self):
        no_legend = f"**Figure 3.** Decoded readings.\n\n```{ASCII}\n{self.FORK}\n```\n\n## Next\n"
        self.assertEqual(ids(run(no_legend, "MA-DOC-02")), ["MA-DOC-02"])
        self.assertEqual(run(doc(self.FORK, ASCII), "MA-DOC-02"), [])
        pure = self.FORK.replace("──▶", "-->").replace("─", "-").replace("┬", "+")
        self.assertEqual(ascii_block(pure.replace("└", "+").replace("┘", "+")).forks, [1])
        self.assertEqual(ascii_block(self.FORK).joins, [2])
        self.assertEqual(ascii_block(pure.replace("└", "+").replace("┘", "+")).joins, [2])

    #: Joins that are not the `───┘` of §5.2, by form: the flow goes on along the lower path, in
    #: either character set, or down from a `┤`.
    JOINS = {
        "join on the upper path": ("checkout ──┬──▶ unit tests ───────┐\n"
                                   "           └──▶ integration ──────┴──▶ deploy"),
        "join on the upper path, pure ASCII": ("checkout --+--> unit tests ------+\n"
                                               "           |                     |\n"
                                               "           +--> integration -----+--> deploy"),
        "join in a side junction": ("build ──┬──▶ lint ──┐\n        │           │\n"
                                    "        └──▶ test ──┤\n                    ▼\n                 deploy"),
    }

    def test_every_form_of_a_join_needs_a_legend(self):
        """Wave 1b verification: each join form, after a fork, is the pair of §5.2."""
        for name, body in self.JOINS.items():
            with self.subTest(case=name):
                block = ascii_block(body)
                self.assertEqual((block.forks, len(block.joins)), ([1], 1))
                no_legend = f"**Figure 4.** Checks before deploy.\n\n```{ASCII}\n{body}\n```\n\n## Next\n"
                self.assertEqual(ids(run(no_legend, "MA-DOC-02")), ["MA-DOC-02"])
                self.assertEqual(run(doc(body, ASCII), "MA-DOC-02"), [])

    #: A `┤` with a stroke above it and, below it, a row that ends before its column or a blank
    #: row (wave 1c verification). The drifted table reports its drift, as before wave 1c.
    SHORT_ROW_BELOW = {
        "a box-drawing table row one column short": (
            "┌────┬────┐\n│ a  │ b  │\n├────┼────┤\n│ c  │ d │\n└────┴────┘", ["MA-ASCII-07"]),
        "a fan-in bus over a shorter name": ("api ──────┐\nworker ───┤\ncron", []),
        "a join in a side junction, then a blank row": (
            "build ──┬──▶ lint ──┐\n        │           │\n        └──▶ test ──┤\n\ndeploy", []),
        "lifelines over a shorter last row": (
            "client          server\n  │                │\n  ├──── GET ──────▶│\n"
            "  │◀──── 200 ──────┤\n  │                │\ndone", []),
    }

    def test_a_side_junction_over_a_shorter_row_is_read(self):
        """A missing cell under a `┤` is no arrowhead: the parser reads the figure, and the lint
        exits 0 or 1, never 2 (wave 1c verification, BLOCKING)."""
        for name, (body, drift) in self.SHORT_ROW_BELOW.items():
            with self.subTest(case=name):
                fig = mm.parse_figure(mm.Fence(lang="text", start=0, end=0, body=body, info=ASCII))
                self.assertEqual(fig.parse_errors, [])
                found = run(f"**Figure 4.** Checks.\n\n```{ASCII}\n{body}\n```\n\nLegend: parallel.\n")
                self.assertEqual([r for r in ids(found) if r in ("MA-ASCII-04", "MA-ASCII-07")], drift)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bus.md"
            body = self.SHORT_ROW_BELOW["a fan-in bus over a shorter name"][0]
            path.write_text(f"**Figure 4.** Sources.\n\n```{ASCII}\n{body}\n```\n\nLegend: x.\n",
                            encoding="utf-8")
            code, out, err = call_main([str(path)])
            self.assertEqual(code, lm.EXIT_OK, out + err)

    def test_a_grid_closes_a_frame_and_joins_nothing(self):
        """The `┘` of a box-drawing grid's bottom border is no join, so a fan-out drawn next to
        a grid needs no legend; a bypass that closes under two forks is still a join."""
        grid = "┌────┬────┐\n│ a  │ b  │\n├────┼────┤\n│ c  │ d  │\n└────┴────┘"
        self.assertEqual(ascii_block(grid).joins, [])
        fan_and_grid = "client ──▶ gateway ──┬──▶ auth\n                     └──▶ orders\n\n" + grid
        self.assertEqual(run(f"**F.** x\n\n```{ASCII}\n{fan_and_grid}\n```\n\n## Next\n", "MA-DOC-02"), [])
        for bypass in ("a ──┬──▶ b ──┬──▶ c\n    └────────┘", "a ──┬──▶ b ──┬──▶ c\n    │        │\n    └────────┘"):
            with self.subTest(bypass=bypass):
                self.assertEqual(len(ascii_block(bypass).joins), 1)

    def test_a_fan_out_without_a_join_needs_none(self):
        """R6: only the pair of §5.2 is a second encoding; a fan-out's branches end in elements."""
        for body in ("client ──▶ gateway ──┬──▶ auth\n                     ├──▶ catalog\n"
                     "                     └──▶ orders",
                     "client --> gateway --+--> auth\n                     |\n                     +--> catalog"):
            with self.subTest(body=body):
                block = ascii_block(body)
                self.assertEqual((len(block.forks), block.joins), (1, []))
                self.assertEqual(run(f"**F.** x\n\n```{ASCII}\n{body}\n```\n\n## Next\n", "MA-DOC-02"), [])

    #: A fan-out whose trunk runs into the middle branch: the trunk's junction starts the
    #: branches above and below it (wave 1c verification).
    MIDDLE_TRUNK = {
        "pure ASCII": ("                     +--> auth\n                     |\n"
                       "client --> gateway --+--> orders\n                     |\n"
                       "                     +--> billing"),
        "box drawing": ("                     ┌──▶ auth\n                     │\n"
                        "client ──▶ gateway ──┼──▶ orders\n                     │\n"
                        "                     └──▶ billing"),
    }

    def test_a_trunk_that_starts_the_branches_is_no_join(self):
        """A pure-ASCII `+` with a stroke below it starts branches, as `┼` does in box drawing,
        so a middle-trunk fan-out needs no legend in either character set. The three join forms
        still count, and so does a three-way join whose middle `+` goes on down."""
        for name, body in self.MIDDLE_TRUNK.items():
            with self.subTest(case=name):
                self.assertEqual(ascii_block(body).joins, [])
                self.assertEqual(run(f"**F.** x\n\n```{ASCII}\n{body}\n```\n\n## Next\n", "MA-DOC-02"), [])
        self.assertEqual(ascii_block(self.MIDDLE_TRUNK["pure ASCII"]).forks, [3])
        for name, body in self.JOINS.items():
            with self.subTest(join=name):
                self.assertEqual(len(ascii_block(body).joins), 1)
        three = ("build --+--> lint ---+\n        |            |\n        +--> test ---+--> deploy\n"
                 "        |            |\n        +--> docs ---+")
        self.assertEqual(ascii_block(three).joins, [5])
        self.assertEqual(ids(run(f"**F.** x\n\n```{ASCII}\n{three}\n```\n\n## Next\n", "MA-DOC-02")),
                         ["MA-DOC-02"])

    def test_a_tree_or_a_chain_needs_none(self):
        for body in ("root\n├── a\n└── b", "a ──▶ b ──▶ c", "+--+--+\n|a |b |\n+--+--+",
                     "┌────┬────┐\n│ a  │ b  │\n└────┴────┘"):
            with self.subTest(body=body):
                self.assertEqual(ascii_block(body).forks, [])
                self.assertEqual(run(f"**F.** x\n\n```{ASCII}\n{body}\n```\n\n## Next\n", "MA-DOC-02"), [])


class TestLegendEncodings(unittest.TestCase):
    """LM-16: call and reply arrows, rect and box fills, and linkStyle strokes are encodings."""

    def legend(self, body):
        return run(f"**Figure 1.** Calls.\n\n```mermaid\n{body}\n```\n\n## Next\n", "MA-DOC-02")

    def test_sequence_arrow_kinds(self):
        both = "sequenceDiagram\n  participant A\n  participant B\n  A->>B: call\n  B-->>A: reply"
        self.assertEqual(ids(self.legend(both)), ["MA-DOC-02"])
        self.assertIn("2 edge styles", self.legend(both)[0].message)
        self.assertEqual(self.legend("sequenceDiagram\n  participant A\n  participant B\n  A->>B: one\n  A->>B: two"), [])
        self.assertEqual(run(doc(both), "MA-DOC-02"), [])

    def test_rect_and_box_fills(self):
        body = ("sequenceDiagram\n  box rgba(127,127,127,0.08) Backend\n    participant A\n    participant B\n"
                "  end\n  rect rgba(127,127,127,0.10)\n    A->>B: call\n  end")
        self.assertEqual(ids(self.legend(body)), ["MA-DOC-02"])

    def test_link_style_strokes(self):
        body = "flowchart TB\n  A --> B\n  B --> C\n  linkStyle 0 stroke:#C62828\n  linkStyle 1 stroke:#2E7D32"
        self.assertEqual(ids(self.legend(body)), ["MA-DOC-02"])
        self.assertEqual(self.legend("flowchart TB\n  A --> B\n  linkStyle default stroke:#546E7A"), [])

    def test_the_grader_view_is_unchanged(self):
        fig = mm.parse_figure(mm.figure_from_mmd("sequenceDiagram\n  A->>B: call\n  B-->>A: reply"))
        self.assertEqual(lm._encodings(fig), (set(), set(), set()))
        self.assertEqual(lm._legend_encodings(fig)[1], {"->>", "-->>"})


class TestFlowchartHeaderAndHazards(unittest.TestCase):
    """LM-06, LM-09, LM-10, LM-13, LM-14, LM-33, STI-35."""

    def fig(self, body):
        return mm.parse_figure(mm.figure_from_mmd(body))

    def test_statement_on_the_header_line(self):
        for body in ("flowchart TB A-->B", "graph TD A-->B", "flowchart TB A --> B --> C"):
            with self.subTest(body=body):
                fig = self.fig(body)
                self.assertEqual([h.code for h in fig.hazards], ["header-line"])
                self.assertTrue(fig.flowchart.edges)
                self.assertEqual(ids(run(doc(body), "MA-PARSE-17")), ["MA-PARSE-17"])

    def test_unknown_direction(self):
        for body in ("flowchart A-->B", "flowchart td\n  A --> B", "graph lr"):
            with self.subTest(body=body):
                self.assertEqual(ids(run(doc(body), "MA-PARSE-17")), ["MA-PARSE-17"])
                self.assertEqual(run(doc(body), "MA-MODEL-01"), [])
        self.assertEqual(len(self.fig("flowchart A-->B").flowchart.edges), 1)
        self.assertEqual(sorted(self.fig("flowchart td\n  A --> B").flowchart.nodes), ["A", "B"])

    def test_valid_headers(self):
        for body in ("flowchart TB; A-->B", "graph TD;\n  A-->B", "flowchart\n  A --> B", "flowchart LR\n  A --> B",
                     "flowchart v\n  A --> B", "flowchart-elk TB\n  A --> B"):
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-PARSE-17"), [])

    def test_double_percent_inside_a_label(self):
        for body in ("flowchart TB\n  A[100%% done] --> B", "flowchart TB\n  A -->|100%% sure| B",
                     'flowchart TB\n  A["50%% off"] --> B'):
            with self.subTest(body=body):
                fig = self.fig(body)
                self.assertEqual((fig.hazards, fig.parse_errors), ([], []))
                self.assertEqual([(e.src, e.dst) for e in fig.flowchart.edges], [("A", "B")])
        self.assertTrue(run(doc("flowchart TB\n  A --> B %% trailing"), "MA-PARSE-14"))
        self.assertTrue(run(doc("flowchart TB\n  A[x] --> B %% trailing"), "MA-PARSE-14"))

    def test_glued_arrowheads(self):
        for body in ("flowchart TB\n  A--xBeta", "flowchart TB\n  C--oDelta", "flowchart TB\n  A==xB"):
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-PARSE-10"), [])
        self.assertEqual(sorted(self.fig("flowchart TB\n  A--xBeta").flowchart.nodes), ["A", "Beta"])
        for body in ("flowchart TB\n  A---ops", "flowchart TB\n  C---xray", "flowchart TB\n  A===oB",
                     "flowchart TB\n  A-.-oB"):
            with self.subTest(body=body):
                self.assertTrue(run(doc(body), "MA-PARSE-10"))

    def test_class_before_its_node(self):
        fig = self.fig("flowchart TB\n  class A hot\n  A --> B\n  classDef hot fill:#C62828,color:#FFFFFF")
        self.assertEqual(fig.flowchart.nodes["A"].classes, [])
        self.assertEqual([h.code for h in fig.hazards], ["class-before-node"])
        body = "flowchart TB\n  class A hot\n  A --> B\n  classDef hot fill:#C62828,color:#FFFFFF"
        found = run(doc(body))
        self.assertIn(("MA-CLASS-06", "error"), {(f.rule, f.severity) for f in found})
        self.assertIn("MA-CLASS-03", ids(found))
        after = self.fig("flowchart TB\n  A --> B\n  class A hot\n  classDef hot fill:#C62828,color:#FFFFFF")
        self.assertEqual((after.flowchart.nodes["A"].classes, after.hazards), (["hot"], []))
        grouped = self.fig('flowchart TB\n  subgraph S["Grp"]\n    A\n    B\n  end\n  class S hot\n  classDef hot fill:#C62828,color:#FFFFFF')
        self.assertEqual((grouped.flowchart.subgraph_classes, grouped.hazards), ({"S": ["hot"]}, []))

    def test_the_node_set_matches_the_render(self):
        fig = self.fig("flowchart TB\n  A --> B\n  class GHOST hot\n  style PHANTOM fill:#C62828,color:#FFFFFF")
        self.assertEqual(sorted(fig.flowchart.nodes), ["A", "B", "PHANTOM"])
        self.assertEqual(sorted(h.code for h in fig.hazards), ["class-before-node", "style-node"])
        early = self.fig("flowchart TB\n  style A fill:#FFFFFF,color:#263238\n  A --> B")
        self.assertEqual((sorted(early.flowchart.nodes), early.hazards), (["A", "B"], []))
        self.assertEqual(early.flowchart.nodes["A"].line, 3)
        grouped = self.fig('flowchart TB\n  subgraph S["Grp"]\n    A\n    B\n  end\n  style S fill:#7F7F7F0D')
        self.assertEqual((sorted(grouped.flowchart.nodes), grouped.hazards), (["A", "B"], []))
        found = run(doc("flowchart TB\n  A --> B\n  style PHANTOM fill:#C62828,color:#FFFFFF"))
        self.assertEqual([(f.rule, f.severity) for f in found if f.rule == "MA-FLOW-07"], [("MA-FLOW-07", "warn")])

    def test_constructs_the_references_forbid(self):
        cases = {
            "MA-FLOW-08": ["flowchart TB\n  A --> B\n  linkStyle 0 stroke:#C62828",
                           "flowchart TB\n  A --> B\n  linkStyle default stroke:#546E7A"],
            "MA-FLOW-09": ['flowchart TB\n  subgraph G["Grp"]\n    direction LR\n    A --> B\n  end'],
            "MA-CLASS-07": ["classDiagram\n  class Animal:::hot", "classDiagram\n  class Dog\n  style Dog fill:#FFF4E0",
                            'classDiagram\n  class Dog\n  cssClass "Dog" hot', "mindmap\n  root((R))\n    A\n    :::urgent",
                            "timeline\n  2024 : a\n  classDef hot fill:#FFF4E0"],
        }
        for rule_id, bodies in cases.items():
            for body in bodies:
                with self.subTest(rule=rule_id, body=body):
                    self.assertTrue(run(doc(body), rule_id))
        quiet = {"MA-FLOW-09": ["stateDiagram-v2\n  state W {\n    direction LR\n    a --> b\n  }"],
                 "MA-CLASS-07": ["erDiagram\n  A ||--o{ B : has\n  classDef hot fill:#FFF4E0",
                                 "classDiagram\n  class Dog\n  classDef hot fill:#FFF4E0", "classDiagram\n  class Dog"]}
        for rule_id, bodies in quiet.items():
            for body in bodies:
                with self.subTest(rule=rule_id, body=body):
                    self.assertEqual(run(doc(body), rule_id), [])
        self.assertTrue(run(doc("classDiagram\n  class Dog\n  classDef hot fill:#FFF4E0"), "MA-SYN-08"))

    def test_a_styling_word_in_a_kind_without_styling_is_content(self):
        """R5: the mindmap, timeline and journey grammars of 11.17.2 hold no `style` or `classDef`
        statement, so such a word starts a node, a period or a task; a full statement still fires."""
        content = ["mindmap\n  root((Docs))\n    style guide", "mindmap\n  root((Docs))\n    classDef notes and drafts",
                   "timeline\n  style update : new colours", "journey\n  section Work\n    style review: 3: Me",
                   "mindmap\n  root((Docs))\n    guide:::wide", "quadrantChart\n  style: [0.3, 0.6]"]
        for body in content:
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-CLASS-07"), [])
        styling = ["mindmap\n  root((Docs))\n    style root fill:#FFF4E0",
                   "quadrantChart\n  Point A:::hot: [0.3, 0.6]\n  classDef hot color: #109060",
                   "journey\n  section Work\n    Make tea: 5: Me\n  classDef hot fill:#FFF4E0"]
        for body in styling:
            with self.subTest(body=body):
                self.assertTrue(run(doc(body), "MA-CLASS-07"))

    def test_character_codes_in_flowchart_labels(self):
        for body in ('flowchart TB\n  A("step #1; done") --> B', 'flowchart TB\n  A -->|"retry #3; then fail"| B',
                     "flowchart TB\n  A[step #2; x] --> B", 'flowchart TB\n  subgraph S["zone #1; a"]\n    A\n    B\n  end',
                     'flowchart TB\n  A -- "wait #9; x" --> B'):
            with self.subTest(body=body):
                self.assertTrue(run(doc(body), "MA-PARSE-18"))
        for body in ('flowchart TB\n  A["step #35;1#59; done"] --> B', 'flowchart TB\n  A["say #quot;hi#quot;"] --> B',
                     'flowchart TB\n  A["renew item\\nfor a week"] --> B', 'flowchart TB\n  A["issue #42"] --> B'):
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-PARSE-18"), [])


class TestKeywordsAndSettings(unittest.TestCase):
    """LM-04, LM-05, LM-07, LM-08."""

    def test_a_fence_without_a_diagram_is_an_error(self):
        for body in ("", "%% only a comment", "---\nconfig:\n  look: classic\n---",
                     '%%{init: {"look": "classic"}}%%', "\n\n"):
            with self.subTest(body=body):
                found = run(doc(body))
                self.assertIn(("MA-SYN-07", "error"), {(f.rule, f.severity) for f in found})
                self.assertNotIn("MA-MODEL-01", ids(found))

    def test_frontmatter_must_open_the_fence(self):
        good = "---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B"
        self.assertEqual(run(doc(good), "MA-SET-02"), [])
        for body in ("\n" + good, "  ---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B"):
            with self.subTest(body=body):
                found = run(doc(body), "MA-SET-02")
                self.assertEqual(len(found), 1)
                self.assertIn("first line", found[0].message)
                fig = mm.parse_figure(mm.figure_from_mmd(body))
                self.assertEqual((fig.kind, fig.settings.config), ("flowchart", {"look": "classic"}))

    def test_keywords_no_pinned_renderer_reads(self):
        for body in ("flowchart-v2 TB\n  A --> B", "requirement\n  element e1 {\n    type: x\n  }", "zenuml\n  A->B: x"):
            with self.subTest(body=body):
                self.assertEqual([(f.rule, f.severity) for f in run(doc(body), "MA-SYN-07")], [("MA-SYN-07", "error")])
        for body in ("requirementDiagram\n  element e1 {\n    type: x\n  }", "flowchart-elk TB\n  A --> B"):
            with self.subTest(body=body):
                self.assertEqual(run(doc(body), "MA-SYN-07"), [])

    def test_git_graph_colon_form(self):
        for body in ("gitGraph:\n  commit\n  commit", "gitGraph LR:\n  commit", "gitGraph\n  commit"):
            with self.subTest(body=body):
                self.assertEqual(mm.detect_kind(body), ("gitGraph", "gitGraph"))
                self.assertEqual(run(doc(body), "MA-SYN-07"), [])
        self.assertEqual(mm.detect_kind("sequenceDiagram:\n  A->>B: x"), ("unknown", "sequenceDiagram:"))


class TestSequenceParticipants(unittest.TestCase):
    """LM-17, LM-31."""

    def test_a_late_alias_names_the_participant(self):
        long = "W" * 28
        late = f"sequenceDiagram\n  participant A\n  A->>B: hi\n  participant B as {long}"
        seq = mm.parse_figure(mm.figure_from_mmd(late)).sequence
        self.assertEqual([(p.id, p.label, p.declared) for p in seq.participants],
                         [("A", "", True), ("B", long, True)])
        self.assertTrue(run(doc(late), "MA-LABEL-10"))
        actor = mm.parse_figure(mm.figure_from_mmd("sequenceDiagram\n  A->>U: x\n  actor U as User")).sequence
        self.assertEqual((actor.participants[1].kind, actor.participants[1].label), ("actor", "User"))
        first = doc(f"sequenceDiagram\n  participant B as {long}\n  B->>B: x")
        self.assertEqual(run(doc(late) + "\n" + first, "MA-DOC-04"), [])

    def test_a_line_of_arrows_without_a_colon_is_linear(self):
        body = "sequenceDiagram\n  A" + "->>" * 20000
        start = time.perf_counter()
        fig = mm.parse_figure(mm.figure_from_mmd(body))
        self.assertLess(time.perf_counter() - start, 0.5)
        self.assertEqual(fig.sequence.messages, [])
        self.assertTrue(fig.parse_errors)
        colon = mm.parse_figure(mm.figure_from_mmd("sequenceDiagram\n  A" + "->>" * 20000 + ": x"))
        self.assertEqual(len(colon.sequence.messages), 1)


class TestLabelLimitsOfTitlesAndEntities(unittest.TestCase):
    """LM-26: subgraph titles and ER box names hold at most `node_line1_chars_max` characters."""

    def test_subgraph_title(self):
        n = LABELS["node_line1_chars_max"]
        body = 'flowchart TB\n  subgraph S["{}"]\n    A\n    B\n  end'
        found = run(doc(body.format("t" * (n + 1))), "MA-LABEL-01")
        self.assertEqual(len(found), 1)
        self.assertIn("`S`", found[0].message)
        self.assertEqual(run(doc(body.format("t" * n)), "MA-LABEL-01"), [])

    def test_er_entity_name_and_alias(self):
        n = LABELS["node_line1_chars_max"]
        self.assertTrue(run(doc(f"erDiagram\n  {'E' * (n + 1)} ||--o{{ B : has"), "MA-LABEL-01"))
        self.assertEqual(run(doc(f"erDiagram\n  {'E' * n} ||--o{{ B : has"), "MA-LABEL-01"), [])
        self.assertTrue(run(doc(f'erDiagram\n  C["{"a" * (n + 1)}"] {{\n    int id\n  }}'), "MA-LABEL-01"))
        self.assertEqual(run(doc(f'erDiagram\n  {"L" * (n + 5)}["Short"] {{\n    int id\n  }}'), "MA-LABEL-01"), [])


class TestLiteralLimits(unittest.TestCase):
    """LM-27: TASK D14 and D25 pinned literally, so moving a limit in notation.json and the prose
    together still fails here."""

    D14 = {"flowchart": {"nodes": [12, 18], "edges": [12, 18]},
           "sequence": {"participants": [6, 6], "messages": [18, 24], "phase_blocks": [3, 4]},
           "state": {"states": [12, 16]}, "gantt": {"bars": [40, 60]}, "er": {"entities": [8, 10]},
           "ascii": {"elements": [8, 12]}}
    #: Hard budgets set to the largest count that passes legibility in a 900 px column, measured
    #: with render_check.py on 2026-10-03 in 10.9.8, 11.17.2 and its dark render: one more
    #: participant, period or task takes the text under 10 px. A `gitGraph` drawn `TB` passed at
    #: 30 commits, so its hard budget stays above the 15 commits a left-to-right graph holds.
    MEASURED = {"sequence": {"participants": [6, 6]}, "timeline": {"periods": [5, 5]},
                "journey": {"tasks": [4, 5]}, "gitgraph": {"commits": [15, 20]}}
    D25 = {"node_line1_chars_max": 32, "node_second_line_chars_max": 40, "edge_label_chars_max": 24,
           "sequence_message_chars_max": 24, "participant_chars_max": 18, "note_chars_max": 48,
           "node_label_lines_max": 2, "edge_label_lines_max": 2, "sequence_message_lines_max": 2,
           "participant_lines_max": 1, "note_lines_max": 3}

    def test_d14_budgets(self):
        for kind, metrics in self.D14.items():
            for metric, pair in metrics.items():
                with self.subTest(kind=kind, metric=metric):
                    self.assertEqual(NOTATION["budgets"][kind][metric], pair)

    def test_measured_budgets(self):
        for kind, metrics in self.MEASURED.items():
            for metric, pair in metrics.items():
                with self.subTest(kind=kind, metric=metric):
                    self.assertEqual(NOTATION["budgets"][kind][metric], pair)
        self.assertTrue(run(doc(participants(7)), "MA-BUDGET-02"))
        self.assertEqual(run(doc(participants(6)), "MA-BUDGET-02"), [])
        periods = "timeline\n" + "\n".join(f"  {2016 + k} : v{k}" for k in range(6))
        self.assertTrue(run(doc(periods), "MA-BUDGET-02"))
        tasks = "journey\n  section S\n" + "\n".join(f"    task {k}: 3: Me" for k in range(6))
        self.assertTrue(run(doc(tasks), "MA-BUDGET-02"))
        self.assertEqual(run(doc(tasks.rsplit("\n", 1)[0]), "MA-BUDGET-02"), [])

    def test_d25_labels(self):
        for key, value in self.D25.items():
            with self.subTest(key=key):
                self.assertEqual(NOTATION["labels"][key], value)
        self.assertEqual(NOTATION["structure"]["lr_max_nodes"], 6)  # TASK R3.4
        self.assertEqual(NOTATION["contrast_min"], 4.5)  # TASK R4.4

    def test_literal_oversized_inputs(self):
        self.assertTrue(run(doc('flowchart TB\n  A -->|"' + "e" * 25 + '"| B'), "MA-LABEL-03"))
        self.assertEqual(run(doc('flowchart TB\n  A -->|"' + "e" * 24 + '"| B'), "MA-LABEL-03"), [])
        self.assertTrue(run(doc('flowchart TB\n  A["' + "n" * 33 + '"] --> B'), "MA-LABEL-01"))
        self.assertEqual(run(doc('flowchart TB\n  A["' + "n" * 32 + '"] --> B'), "MA-LABEL-01"), [])
        self.assertTrue(run(doc(" -> ".join(f"e{k}" for k in range(13)), ASCII), "MA-ASCII-06"))
        self.assertEqual(run(doc(" -> ".join(f"e{k}" for k in range(12)), ASCII), "MA-ASCII-06"), [])
        self.assertTrue(run(doc(chain(19)), "MA-BUDGET-02"))
        self.assertEqual(run(doc(chain(18)), "MA-BUDGET-02"), [])
        self.assertTrue(run(doc(chain(7, "LR")), "MA-FLOW-06"))
        self.assertEqual(run(doc(chain(6, "LR")), "MA-FLOW-06"), [])

    def test_bottom_to_top_counts_as_not_top_to_bottom(self):
        """LM-30: TASK R3.4 lays out a flowchart of more than 6 nodes top to bottom."""
        for direction in ("BT", "LR", "RL"):
            with self.subTest(direction=direction):
                self.assertTrue(run(doc(chain(7, direction)), "MA-FLOW-06"))
        for direction in ("TB", "TD"):
            with self.subTest(direction=direction):
                self.assertEqual(run(doc(chain(10, direction)), "MA-FLOW-06"), [])


#: Documents and the fenced blocks CommonMark reads in them, as (opening line, info string,
#: body). Each expected list is what markdown-it-py 4.2.0 (preset `commonmark`) and micromark
#: 3.2.0 both return for the document (R2-01, R2-16).
COMMONMARK_FENCES = (
    # a fence opens on a list marker line, in each order of containers
    ("1. ```mermaid\n   flowchart TB\n     A --> B\n   ```\n", [(1, "mermaid", "flowchart TB\n  A --> B")]),
    ("- ```mermaid\n  flowchart TB\n  ```\n", [(1, "mermaid", "flowchart TB")]),
    ("-   ```mermaid\n    flowchart TB\n    ```\n", [(1, "mermaid", "flowchart TB")]),
    ("2) ~~~mermaid\n   flowchart TB\n   ~~~\n", [(1, "mermaid", "flowchart TB")]),
    ("- - ```mermaid\n    flowchart TB\n    ```\n", [(1, "mermaid", "flowchart TB")]),
    ("- > ```mermaid\n  > flowchart TB\n  > ```\n", [(1, "mermaid", "flowchart TB")]),
    ("> - ```mermaid\n>   flowchart TB\n>   ```\n", [(1, "mermaid", "flowchart TB")]),
    ("1.  > ```mermaid\n    > flowchart TB\n    > ```\n", [(1, "mermaid", "flowchart TB")]),
    ("- ```mermaid\n  flowchart TB\n\n  A --> B\n  ```\n", [(1, "mermaid", "flowchart TB\n\nA --> B")]),
    ("- ```text figure\n  a\n    \n  b\n  ```\n", [(1, "text figure", "a\n  \nb")]),
    ("Text\n1. ```mermaid\n   flowchart TB\n   ```\n", [(2, "mermaid", "flowchart TB")]),
    ("Text\n2. ```mermaid\nflowchart TB\n```\n", [(4, "", "")]),
    # a line indented less than the item ends the item and its fence
    ("- ```mermaid\n  flowchart TB\n```\n  A --> B\n```\n",
     [(1, "mermaid", "flowchart TB"), (3, "", "  A --> B")]),
    ("1. Step\n\n   ```mermaid\n   flowchart TB\n  ```\n", [(3, "mermaid", "flowchart TB"), (5, "", "")]),
    # a block at column 0 ends the list, so a 4-column opener below it is indented code
    ("- item\n\n```text\nlog\n```\n\n    ```mermaid\n    flowchart TB\n      A --> B --> A\n    ```\n",
     [(3, "text", "log")]),
    ("- item\n```text\nlog\n```\n    ```mermaid\n    flowchart TB\n    ```\n", [(2, "text", "log")]),
    ("- item\n\n<!--\nnote\n-->\n\n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("- item\n\n# Heading\n\n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("- item\n\n***\n\n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("- item\n\nParagraph.\n\n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("- item\n\n    ```mermaid\n    flowchart TB\n    ```\n", [(3, "mermaid", "flowchart TB")]),
    ("-\n    \n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("> text\n    ```mermaid\n    flowchart TB\n    ```\n", []),
    ("> ```mermaid\n> flowchart TB\nlazy\n```\n", [(1, "mermaid", "flowchart TB"), (4, "", "")]),
    # a closing fence is indented 3 columns at most
    ("```markdown\nExample:\n    ```\nstill inside\n```\n", [(1, "markdown", "Example:\n    ```\nstill inside")]),
    # a fence inside an HTML block is text; a blank line ends a block such as <details>
    ("<details>\n```mermaid\nflowchart TB\n```\n</details>\n", []),
    ("<details>\n<summary>Figure</summary>\n\n```mermaid\nflowchart TB\n```\n\n</details>\n",
     [(4, "mermaid", "flowchart TB")]),
    ("<Before>\n```markdown\nx\n```\n</Before>\n", []),
    ("Text\n<Before>\n```mermaid\nflowchart TB\n```\n", [(3, "mermaid", "flowchart TB")]),
    ("<!-->\n```mermaid\nflowchart TB\n```\n", [(2, "mermaid", "flowchart TB")]),
    # a tab that the item's indent splits leaves its other columns as spaces
    ("- item\n\n  ```text figure\n\t  x\n  ```\n", [(3, "text figure", "    x")]),
    ("- item\n\n    ```text figure\n  \tx\n    ```\n", [(3, "text figure", "x")]),
)


class TestFenceContainers(unittest.TestCase):
    """LM-11, LM-12, LM-21, LM-22, LM-23, R2-01, R2-16."""

    def test_fences_are_read_as_commonmark_reads_them(self):
        for text, expected in COMMONMARK_FENCES:
            with self.subTest(text=text):
                found = mm.extract_fences(text, ("mermaid", "text", "markdown", ""))
                self.assertEqual([(f.start, f.info, f.body) for f in found], expected)

    def test_a_figure_on_a_list_marker_line_hides_no_figure_below(self):
        """R2-01: the closing line of a fence opened on a list marker line opens no fence, so
        the broken figure below it is linted, and the lint fails."""
        text = ("# Steps\n\n1. ```mermaid\n   flowchart TB\n     A --> B\n   ```\n\nSome text.\n\n"
                "```mermaid\nflowchart TB\n  X[API (gateway)] --> Y\n  Y --> end\n```\n\n"
                "**Figure 2.** Broken.\n")
        self.assertEqual([(f.start, f.end, f.body) for f in mm.extract_fences(text)],
                         [(3, 6, "flowchart TB\n  A --> B"),
                          (10, 14, "flowchart TB\n  X[API (gateway)] --> Y\n  Y --> end")])
        found = {(f.rule, f.line) for f in counted(run(text))}
        self.assertLessEqual({("MA-PARSE-01", 12), ("MA-PARSE-05", 13)}, found)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "steps.md")
            path.write_text(text, encoding="utf-8")
            self.assertEqual(call_main([str(path)])[0], lm.EXIT_FINDINGS)

    def test_a_block_at_column_0_ends_the_list_above_it(self):
        """R2-16: after a fence or a multi-line comment at column 0, a 4-column opener is an
        indented code block, shown as text. Inside the item it still opens a figure."""
        shown = "    ```mermaid\n    flowchart TB\n      A[x (y)] --> B\n    ```\n"
        for above in ("- item\n\n```text\nlog\n```\n\n", "- item\n```text\nlog\n```\n\n",
                      "- item\n\n<!--\nnote\n-->\n\n"):
            with self.subTest(above=above):
                self.assertEqual(mm.extract_fences(above + shown), [])
                self.assertEqual(run(above + shown), [])
        self.assertEqual(ids(run("- item\n\n" + shown, "MA-PARSE-01")), ["MA-PARSE-01"])

    def test_a_line_of_nested_list_markers_scans_in_linear_time(self):
        """Each list marker of the line opens an item, and each item would test the rest of the
        line for a thematic break; the line is read for it once."""
        for text in ("- " * 20000 + "*", "1. " * 10000 + "- -"):
            with self.subTest(first=text[:6], length=len(text)):
                start = time.perf_counter()
                self.assertEqual(mm.extract_fences(text), [])
                elapsed = time.perf_counter() - start
                self.assertLess(elapsed, 2.0, f"{elapsed:.2f} s")

    def test_fence_spans_give_the_column_of_the_opening_fence(self):
        lines = ["1. ```mermaid", "   flowchart TB", "   ```", "", "> ```text", "> x"]
        self.assertEqual(mm._fence_spans(lines), [(0, 2, "mermaid", 3), (4, 6, "text", 2)])

    def test_blockquote_and_alert(self):
        quoted = "> **Figure 1.** Quoted.\n>\n> ```mermaid\n> flowchart TB\n>   A[x (y)] --> B\n> ```\n>\n> Legend.\n"
        fence = mm.extract_fences(quoted)[0]
        self.assertEqual((fence.start, fence.end, fence.body), (3, 6, "flowchart TB\n  A[x (y)] --> B"))
        self.assertEqual((fence.before.text, fence.after.text), ("**Figure 1.** Quoted.", "Legend."))
        self.assertEqual(ids(run(quoted, "MA-PARSE-01")), ["MA-PARSE-01"])
        alert = "> [!NOTE]\n> ```mermaid\n> flowchart TB\n>   A --> B\n> ```\n"
        self.assertEqual(mm.extract_fences(alert)[0].body, "flowchart TB\n  A --> B")
        nested = "> > ```mermaid\n> > flowchart TB\n> >   A --> end\n> > ```\n"
        self.assertEqual(ids(run(nested, "MA-PARSE-05")), ["MA-PARSE-05"])

    def test_the_end_of_a_blockquote_closes_its_fence(self):
        text = "> ```mermaid\n> flowchart TB\n>   A --> B\nNext paragraph.\n"
        fence = mm.extract_fences(text)[0]
        self.assertEqual((fence.body, fence.end, fence.after.text), ("flowchart TB\n  A --> B", 3, "Next paragraph."))

    def test_a_top_level_fence_keeps_its_quote_lines(self):
        fence = mm.extract_fences("```text figure\n> quoted line\na -> b\n```\n")[0]
        self.assertEqual(fence.body, "> quoted line\na -> b")

    def test_an_indented_code_block_is_no_fence(self):
        shown = "Example source:\n\n    ```mermaid\n    flowchart TB\n      A[x (y)] --> B\n    ```\n"
        self.assertEqual(mm.extract_fences(shown), [])
        self.assertEqual(run(shown), [])
        lazy = "Text\n    ```mermaid\n    flowchart TB\n    ```\n"
        self.assertEqual(mm.extract_fences(lazy), [])
        for listed in ("- item\n\n    ```mermaid\n    flowchart TB\n      A --> B\n    ```\n",
                       "1. Step\n\n   More text.\n\n    ```mermaid\n    flowchart TB\n      A --> B\n    ```\n",
                       "- item text\ncontinued lazily\n\n    ```mermaid\n    flowchart TB\n      A --> B\n    ```\n"):
            with self.subTest(text=listed):
                fence = mm.extract_fences(listed)[0]
                self.assertEqual(fence.body, "flowchart TB\n  A --> B")
        ended = "- item\n\nParagraph at the top level.\n\n    ```mermaid\n    flowchart TB\n    ```\n"
        self.assertEqual(mm.extract_fences(ended), [])

    def test_indented_openers_scan_in_linear_time(self):
        """R4, TASK R6.8: the list context is kept while scanning, never searched back per opener."""
        for text in ("\n".join(["    ```mermaid"] * 8000),
                     "\n".join(["    text", "    ```mermaid", "    flowchart TB", "    ```"] * 2000)):
            with self.subTest(lines=text.count("\n") + 1, first=text[:12]):
                start = time.perf_counter()
                self.assertEqual(mm.extract_fences(text), [])
                elapsed = time.perf_counter() - start
                self.assertLess(elapsed, 2.0, f"{elapsed:.2f} s")
        nested = ("- a\n  - b\n    - c\n\n      ```mermaid\n      flowchart TB\n      ```\n\n"
                  "  ```mermaid\n  flowchart TB\n  ```\n")
        self.assertEqual([f.start for f in mm.extract_fences(nested)], [5, 9])
        deeper = "- a\n\n        ```mermaid\n        flowchart TB\n        ```\n"
        self.assertEqual(mm.extract_fences(deeper), [])

    def test_a_tab_indent_is_stripped_by_columns(self):
        text = ("- item\n\n\t```mermaid\n\t---\n\tconfig:\n\t  look: classic\n\t---\n\tflowchart TB\n\t  A --> B\n"
                "\t```\n")
        fence = mm.extract_fences(text)[0]
        self.assertEqual(fence.body, "---\nconfig:\n  look: classic\n---\nflowchart TB\n  A --> B")
        self.assertEqual(run(text, "MA-SET-02"), [])
        # a tab that the item's indent splits leaves its other columns as spaces
        split = mm.extract_fences("- item\n\n  ```text figure\n\t  x\n  ```\n")[0]
        self.assertEqual(split.body, "    x")
        whole = mm.extract_fences("- item\n\n    ```text figure\n  \tx\n    ```\n")[0]
        self.assertEqual(whole.body, "x")

    def test_a_multi_line_comment_is_no_caption_and_no_legend(self):
        above = "## Section\n\n<!--\n  generated by a tool\n-->\n```mermaid\nflowchart TB\n  A --> B\n```\n"
        self.assertIsNone(mm.extract_fences(above)[0].before)
        self.assertEqual(ids(run(above, "MA-DOC-01")), ["MA-DOC-01"])
        spaced = "## Section\n\n<!--\n  generated by a tool\n-->\n\n```mermaid\nflowchart TB\n  A --> B\n```\n"
        self.assertIsNone(mm.extract_fences(spaced)[0].before)
        body = ("flowchart TB\n  A:::x --> B:::y\n  classDef x fill:#FFFFFF,color:#263238\n"
                "  classDef y fill:#E8F0FB,color:#0F2A47")
        below = f"**Figure 1.** Two classes.\n\n```mermaid\n{body}\n```\n<!--\nhidden note\n-->\n"
        self.assertIsNone(mm.extract_fences(below)[0].after)
        self.assertEqual(ids(run(below, "MA-DOC-02")), ["MA-DOC-02"])

    def test_a_rule_after_a_list_legend(self):
        listed = "```mermaid\nflowchart TB\n```\n- white = external\n- blue = owned\n---\n"
        self.assertEqual(mm.extract_fences(listed)[0].after.text, "- white = external\n- blue = owned")
        table = "```mermaid\nflowchart TB\n```\n| a | b |\n| - | - |\n---\n"
        self.assertIsNotNone(mm.extract_fences(table)[0].after)
        self.assertIsNone(mm.extract_fences("```mermaid\nflowchart TB\n```\nA heading\n---\n")[0].after)


class TestInventoryOfEveryKind(unittest.TestCase):
    """LM-18, LM-19: the inventory lists the elements of every kind it reads and names the kinds
    it does not read; a parser failure is exit 2."""

    def rows(self, body):
        return lm.inventory(mm.parse_figure(mm.figure_from_mmd(body)))

    def test_class_diagram(self):
        rows = self.rows('classDiagram\n  class Order {\n    +int id\n    +place() bool\n  }\n'
                         '  Customer "1" --> "*" Order : placed by 2\n  note for Order "kept 7 years"')
        texts = {(r["kind"], r["text"]) for r in rows}
        self.assertTrue({("node", "Order"), ("node", "Customer"), ("label", "+int id"), ("label", "+place() bool"),
                         ("edge", "Customer --> Order"), ("label", "placed by 2"), ("number", "1"),
                         ("number", "2"), ("note", "kept 7 years"), ("number", "7")} <= texts, texts)

    def test_chart_kinds(self):
        cases = {
            "mindmap\n  root((Guide))\n    Forms\n    id1[Tables]\n    ::icon(fa fa-book)":
                {("node", "Guide"), ("node", "Forms"), ("node", "Tables")},
            "timeline\n  title T\n  section Early\n  2002 : LinkedIn\n  2004 : Facebook\n       : Google":
                {("group", "Early"), ("node", "2002"), ("label", "LinkedIn"), ("label", "Google"),
                 ("number", "2004")},
            'pie title Pets\n  "Dogs" : 386\n  "Cats" : 85':
                {("node", "Dogs"), ("number", "386"), ("node", "Cats"), ("number", "85")},
            "journey\n  title Day\n  section Work\n    Make tea: 5: Me, Cat":
                {("group", "Work"), ("task", "Make tea"), ("number", "5"), ("label", "Me, Cat")},
            'gitGraph\n  commit id: "Alpha"\n  branch develop\n  checkout develop\n  commit tag: "v1.0"\n'
            '  checkout main\n  merge develop':
                {("node", "Alpha"), ("group", "develop"), ("label", "v1.0"), ("edge", "merge develop")},
        }
        for body, wanted in cases.items():
            with self.subTest(kind=body.split()[0]):
                texts = {(r["kind"], r["text"]) for r in self.rows(body)}
                self.assertTrue(wanted <= texts, texts)
                self.assertTrue(lm.inventoried(mm.parse_figure(mm.figure_from_mmd(body))))

    def test_er_attributes(self):
        rows = self.rows("erDiagram\n  CUSTOMER ||--o{ ORDER : places\n  ORDER {\n    int id PK\n    string note\n  }")
        attrs = [(r["id"], r["text"], r["line"]) for r in rows if r["kind"] == "label" and r["id"] == "ORDER"]
        self.assertEqual(attrs, [("ORDER", "int id PK", 4), ("ORDER", "string note", 5)])

    def test_a_kind_without_an_inventory_says_so(self):
        text = doc("quadrantChart\n  title Reach\n  A: [0.3, 0.6]")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "q.md")
            path.write_text(text, encoding="utf-8")
            code, out, _ = call_main(["--inventory", str(path)])
            self.assertEqual(code, lm.EXIT_OK)
            self.assertIn("not inventoried: quadrantChart", out)
            self.assertNotIn("0 rows", out)
            code, out, _ = call_main(["--inventory", "--json", str(path)])
            block = json.loads(out)["figures"][0]
            self.assertEqual((block["inventoried"], block["rows"]), (False, []))

    def test_a_parser_failure_is_exit_2(self):
        original = mm._parse_er

        def broken(rows, fig):
            if any("ZZZ" in text for _line, text in rows):
                raise RuntimeError("ZZZ")
            return original(rows, fig)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "er2.md")
            path.write_text(doc("erDiagram\n  ZZZ ||--o{ B : has"), encoding="utf-8")
            mm._parse_er = broken
            try:
                for argv in (["--inventory", str(path)], ["--inventory", "--json", str(path)], [str(path)]):
                    with self.subTest(argv=argv):
                        code, _out, err = call_main(argv)
                        self.assertEqual(code, lm.EXIT_INTERNAL)
                        self.assertIn("ZZZ", err)
            finally:
                mm._parse_er = original


if __name__ == "__main__":
    unittest.main()
