# ASCII figures, lists and tables

Load this file when Step 0 of `SKILL.md` picks a numbered list, a table or ASCII. Load it also
before any figure in a medium that does not render Mermaid. It covers:

- the choice between a list, a table and ASCII;
- what an ASCII figure may draw, in which characters, with which caption;
- five ASCII patterns, each with an example;
- tables for many-to-many relations;
- output media that do not render Mermaid;
- the checks the lint runs on a `text figure` fence.

## 1. Choose the form

Take the first row that carries the information. The rows restate Step 0 of `SKILL.md`.

| Information | Form |
| :--- | :--- |
| up to 7 steps in a fixed order, no branches | numbered list |
| a many-to-many relation, attribute sets, a full schema, a status matrix | table, except in a log (§7) |
| a chain or a tree of at most 8 elements, link labels and comments included | ASCII in a `text figure` fence |
| any figure, in a medium that does not render Mermaid | list or ASCII, a table outside a log; never Mermaid |
| structure, interaction in time, lifecycle, plan, a small ER model | Mermaid, in Markdown on GitHub or in an IDE |
| a screenshot or a visual design | image |

- A step is an action. A numbered list carries steps.
- An element is a box, or a run of text outside a box: a name (a component, a stage, a directory,
  a value), a link label or a comment. An ASCII figure links its named elements.
- A section gets no figure by default.

**Why.** A numbered list keeps its order in every medium, a screen reader included. A table holds
a relation of any density without a crossing. ASCII shows a short branch or a nesting that a list
flattens.

## 2. What ASCII may draw

An ASCII figure draws one of the five patterns of §5:

1. a chain;
2. a chain with one parallel pair;
3. a tree;
4. a directory tree;
5. a two-column mapping.

Rules:

1. Write the figure in a fence whose info string is `text figure`. An ASCII figure has no
   settings line.
2. A fence whose info string is `text` alone is a listing: command output, a log, file contents.
   No figure rule applies to it, and the lint skips it.
3. The budget is 8 elements soft and 12 hard (`budgets.ascii.elements`), counted as §1 defines
   them: names, link labels and comments alike. A `v` under a vertical line is its arrowhead, not
   an element.
4. Over 8 elements, aggregate or split. Over 12, write a numbered list, a nested list or a table.
5. Never draw a 2-D graph of boxes with crossing arrows. Draw it in Mermaid where the medium
   renders Mermaid; otherwise write a table or a list.

**Why.** Models misalign columns: a box side or a vertical arrow drifts by one column on some
line. A font that lacks a box-drawing or arrow glyph borrows it from another font, and the
borrowed glyph can be wider than one column. A terminal wraps a long line and breaks the figure.
The five patterns keep each relation on one line or in one column. The token `figure` in the info
string separates a figure from a listing without reading the text around the fence.

## 3. Character set

Pick one set per figure: pure ASCII or box drawing.

| Role | Pure ASCII | Box drawing |
| :--- | :--- | :--- |
| vertical line | `\|` | `│` U+2502 |
| horizontal line | `-` | `─` U+2500 |
| branch of a tree | `+` | `├` U+251C |
| last branch of a tree | `+` | `└` U+2514 |
| fork | `+` | `┬` U+252C |
| join | `+` | `┘` U+2518 |
| arrowhead, right | `>` | `▶` U+25B6 |
| arrowhead, down | `v` | `▼` U+25BC |
| short arrow, right | `->` | `→` U+2192 |

1. Use one set in one figure. Two sets give one role two glyphs, such as `|` and `│` for a
   vertical line.
2. Write no tab character. Indent with spaces.
3. Write no emoji and no CJK character in a figure.
4. Cyrillic letters take one column outside a CJK locale, so a Russian label aligns like a Latin
   one.
5. Every line holds at most 100 columns (`ascii.max_columns`).
6. Use pure ASCII in a log, and in a terminal whose locale may be Chinese, Japanese or Korean.

**Why.** The width of a tab depends on the tab stop of the viewer. A monospace font draws a
character of East Asian Width `W` or `F` two columns wide; emoji and CJK characters are such
characters. Box-drawing characters, `▶`, `▼`, `→` and Cyrillic letters are East Asian Width `A`,
ambiguous: a terminal set to draw ambiguous characters wide gives them two columns. A terminal
wraps a line longer than its width, and GitHub scrolls it out of view in a code block.

An aligned line is a line that shares a column position with the line above or below it: a tree
row, a fork, a box side, a comment column.

## 4. Caption and legend

- The caption is the paragraph directly above the fence, as for every figure: a bold label and a
  title, then one sentence that states what the figure shows. The label follows the document's
  language. A medium that renders no Markdown gets a plain label (§7).
- A legend is the paragraph directly below the fence. It is required when the figure uses two or
  more encodings. The fork and join of §5.2 are the second encoding in these patterns.
- Every figure in §5 carries its caption in this form.

## 5. Patterns

### 5.1 A chain

Elements linked one after another. A label on a link names the relation the text states.

**Figure 1.** Reading path — a reading travels from the sensor to the time-series store.

```text figure
sensor ──MQTT──▶ gateway ──AMQP──▶ broker ──▶ decoder ──▶ time-series store
```

A chain that does not fit in 100 columns runs top to bottom, one element per line.

**Figure 2.** Reading path, top to bottom — the first three elements of Figure 1.

```text figure
sensor
  │ MQTT
  ▼
gateway
  │ AMQP
  ▼
broker
```

### 5.2 A chain with a parallel pair

One fork and one join. Two paths run between them in parallel. A figure with a second fork is a
Mermaid flowchart, or a list that names each parallel pair.

**Figure 3.** Decoded readings — the raw store and the threshold check run in parallel, then the
batch is acknowledged.

```text figure
gateway ──▶ decoder ──┬──▶ raw store ─────────┬──▶ batch ack
                      └──▶ threshold check ───┘
```

Legend: the two paths between the fork and the join run in parallel.

The same figure in pure ASCII:

**Figure 4.** Decoded readings — Figure 3 drawn with pure ASCII characters.

```text figure
gateway --> decoder --+--> raw store ---------+--> batch ack
                      |                       |
                      +--> threshold check ---+
```

Legend: the two paths between the fork and the join run in parallel.

In Figures 3 and 4, counting from 1, the fork sits in column 23 and the join in column 47 on
every line.

The lint counts a join in four forms. Forms 1, 2 and 4 have a spelling in either character set;
form 3 exists in box drawing only:

1. the lower path ends under the stroke, `───┘` or `---+`, and the flow goes on along the upper
   path;
2. the stroke meets the path in `┴` or `+`, and the path goes on to an arrowhead, `──┴──▶` or
   `--+-->`;
3. the path ends in `┤`, and the stroke goes on down to an arrowhead below;
4. the stroke meets the path in `┴` or `+`, and the path goes on to a corner that turns down to an
   arrowhead, `──┴──┐` or `--+--+` over a stroke to `▼` or `v`.

### 5.3 A tree

A hierarchy: each element has one parent. `│` continues a parent past a nested branch.

**Figure 5.** Print server — its parts and the drivers it holds.

```text figure
print server
├── spooler
│   └── job queue
├── renderer
└── drivers
    ├── laser
    └── label
```

### 5.4 A directory tree

1. A directory name ends with `/`.
2. Draw only the entries the text discusses. Write `...` for entries left out.
3. A comment column starts at the same column on every line that carries a comment.
4. A comment counts as an element (§2), so comment only the entries the text explains.

**Figure 6.** Library app — the directories the text names, with the role of its two packages.

```text figure
library-app/
├── docs/
├── src/
│   ├── loans/       loan rules and due dates
│   └── members/     member records
└── tests/
```

### 5.5 A two-column mapping

Each left value maps to one right value: an event to its consumer, a code to its meaning. The
arrows start in one column. A many-to-many mapping is a table (§6).

**Figure 7.** Loan events — the service that consumes each event.

```text figure
loan.created   ──▶ reminder service
loan.overdue   ──▶ fines service
loan.returned  ──▶ reservation service
```

The same mapping in a Russian document. The caption label follows the document's language, and
the Cyrillic labels align like Latin ones:

````markdown
**Рисунок 7.** События займа — служба, которая обрабатывает каждое событие.

```text figure
заём создан      ──▶ служба напоминаний
заём просрочен   ──▶ служба штрафов
заём возвращён   ──▶ служба резерва
```
````

## 6. Tables for many-to-many relations

1. Put the set with more members in the rows. A table grows down without limit and across only
   to the page width.
2. The first header cell names the row set. Each other header cell names one member of the
   column set.
3. Every cell holds `yes` or `no`, in the document's language. Leave no cell empty and use no
   mark glyph such as `✓`.
4. Write a sentence directly under the table. It states that the table lists every member of
   both sets, and what `no` means.

**Why.** Three elements each linked to the same three elements form `K3,3`. Every drawing of
`K3,3` has at least one crossing, and a table has none. An empty cell reads as unknown. A mark
glyph has no fixed meaning: it can mean allowed, done or tested.

Example:

| Printer | Duplex | Colour | A3 | Staple |
| :--- | :--- | :--- | :--- | :--- |
| Floor 1 laser | yes | no | no | yes |
| Floor 2 colour | yes | yes | yes | no |
| Label printer | no | no | no | no |

The table lists every printer of the print server and every option the queue routes by. A job
that needs an option goes only to a printer marked `yes` for it.

## 7. Media that do not render Mermaid

1. These media show Mermaid as source text: a terminal, a log, an MCP response, a chat surface
   without a diagram renderer.
2. Output for such a medium holds no `mermaid` fence. Write a list, a table or an ASCII figure in
   a `text figure` fence.
3. When the operator asks for Mermaid source there, give it in a `mermaid` fence. Add one
   sentence stating that this medium does not render it. Example: `This terminal shows Mermaid
   as source; paste the block into a Markdown file to see the figure.`
4. A log renders no Markdown table. Write a two-column mapping (§5.5) or a list there.
5. A medium that renders no Markdown prints `**` as typed. Write the caption label plain:
   `Figure 1.`, not `**Figure 1.**`. Keep the `text figure` fence: its lines mark where the
   figure starts and ends, and the reply pasted into a Markdown file still shows a figure.

**Why.** A reader of a terminal sees the source of a Mermaid fence, not the figure. The bootstrap
files of the framework carry this rule, so it holds before the skill loads.

## 8. What the lint checks in a `text figure` fence

`lint_mermaid.py` reads every `text figure` fence of a document as an ASCII figure. It skips a
fence whose info string is `text` alone.

| Rule | Reported when | Fix |
| :--- | :--- | :--- |
| MA-ASCII-01, error | the fence holds a tab character | indent with spaces |
| MA-ASCII-02 | an emoji or a CJK character sits on an aligned line | write the label in single-width characters |
| MA-ASCII-03 | a line is wider than 100 columns | split the figure, or run the chain top to bottom |
| MA-ASCII-04 | a box side or corner leaves the column of the box's top corners | move it to that column; pad every line to the top-right corner |
| MA-ASCII-05 | the figure counts more than 8 elements | aggregate or split |
| MA-ASCII-06, error | the figure counts more than 12 elements | write a list or a table |
| MA-ASCII-07 | a vertical stroke (`│`, `\|`, `▼`, `v`, `+`) moves by one column between lines | move it to the column of the stroke above or below |
| MA-DOC-02 | a fork and its join, drawn as in §5.2, have no legend directly below the fence | add the legend of §4 |

A rule without `error` reports a `warn`. A fan-out, a fork without a join, needs no legend.
Postcondition: the lint reports no finding on the fence.
