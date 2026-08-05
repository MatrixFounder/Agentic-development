#!/usr/bin/env python3
import sys
import argparse
import re
import os

# The RTM heading, matched against the shapes the repo ACTUALLY ships. A survey of
# docs/tasks/ finds the section written at least six ways — h2 AND h3, with/without a
# section number, with a trailing "(RTM)", and the current form `### N. Requirements (RTM)`
# which drops the word "Traceability" entirely. The old `## Requirements Traceability`
# literal (and its `$`-anchored relaxation) matched NONE of them, so this gate had never
# once passed on a shipped artifact and Step-1 validation was, in practice, skipped. A gate
# that cannot pass on the artifacts it governs is not a gate.
#
# Rule: an h2..h4 heading, an optional "N."/"N)" section number, then a lookahead requiring
# the line to name the RTM — either "Requirements Traceability[ Matrix]" or a bare "(RTM)"
# token. Kept zero-width / non-capturing so RTM_HEADER.split() stays clean. The table checks
# below (non-empty, columns ID + Requirement) are UNCHANGED.
RTM_HEADER = re.compile(
    r'^#{2,4}\s+(?:\d+[.)]\s*)?(?=.*(?:Requirements\s+Traceability|\bRTM\b)).*$',
    re.MULTILINE | re.IGNORECASE)

# --- Structural anchor (TASK 095 / WI-30) ------------------------------------
#
# Everything above addresses the RTM through the document's own PROSE, and so
# only works for documents written in English. Three independent places did it:
# this heading regex, the ['ID','Requirement'] column-name check in
# validate_task, and a second r['ID'] lookup in validate_plan — which fails even
# after the first two are fixed, so a project that patched only the reported one
# still had a dead --mode plan gate.
#
# `documentation-standards` §4.3 states the rule this implements: a human may
# address a section by its heading; a MACHINE addresses it by anchor. A gate
# matching heading words or column names asserts that the document is written in
# a particular language — an assertion nobody made and the gate cannot check.
#
# The anchor is OPTIONAL and WINS when present. When it is absent every matcher
# below behaves exactly as before, which is what keeps the whole shipped corpus
# (and every downstream project) passing unchanged — see tests/test_corpus.py.
# Deliberately a SEPARATE pattern rather than an alternation inside RTM_HEADER:
# RTM_HEADER.split() is pinned to exactly two parts by test_validate, and the
# corpus pins that it is never narrowed. Additive, in both senses.
ANCHOR_NAME = "contract:rtm"
ANCHOR_RTM = re.compile(
    r'^[ \t]*<!--[ \t]*' + re.escape(ANCHOR_NAME) + r'[ \t]*-->[ \t]*$',
    re.MULTILINE)

#: cut the located section at the next h2, matching the pre-existing fallback
#: behaviour exactly — an `### Details by ID` subsection stays inside the block,
#: and the table parser stops at the first non-table line anyway.
_SECTION_END = re.compile(r'^## ', re.MULTILINE)


def _anchor_block(content):
    """Slice the RTM section addressed by the anchor.

    Returns ``(block, error)`` — ``(None, None)`` when there is no anchor at
    all, so the caller falls back to the heading matcher.

    A duplicated anchor is an ERROR, never "first one wins": an ambiguous
    address is a document defect, and quietly picking one hides it (the same
    reasoning `known-issues-format` applies to its ledger anchors).
    """
    matches = list(ANCHOR_RTM.finditer(content))
    if not matches:
        return None, None
    if len(matches) > 1:
        return None, (
            "Error: the '<!-- %s -->' anchor appears %d times in TASK.md; "
            "it must appear exactly once." % (ANCHOR_NAME, len(matches)))

    # The anchor sits directly ABOVE the heading it names, so the heading line
    # itself must be stepped over before cutting at the next h2 — otherwise the
    # section terminator fires on the very heading the anchor introduced and
    # the block comes back empty.
    rest = content[matches[0].end():].split('\n')
    i = 0
    while i < len(rest) and not rest[i].strip():
        i += 1
    if i < len(rest) and re.match(r'#{1,6}\s', rest[i]):
        i += 1
    return _SECTION_END.split('\n'.join(rest[i:]).strip())[0], None


def _table_columns(block):
    """Header cells of the first markdown table in *block*, in order.

    `parse_markdown_table` returns dicts, and a dict cannot answer "which
    column came first" once two columns share a name. Positional reading is
    the whole point of the anchor path, so the order is read from the raw
    header row instead of recovered from the rows.
    """
    for line in block.split('\n'):
        stripped = line.strip()
        if stripped.startswith('|'):
            cells = re.split(r'(?<!\\)\|', stripped.strip('|'))
            return [c.strip() for c in cells]
    return []


# --- Multi-table RTM sections (RF-6) -----------------------------------------
#
# `parse_markdown_table` stops at the first non-table line, so the located
# block could only ever yield its FIRST table -- and said `Success` about it.
# A TASK carrying 23 requirements in five per-epic tables reported
# `Found 9 requirements`, exit 0, no warning that 61% of the document went
# unread; `validate_plan` shares this locator, so the planning gate would have
# reported full coverage of the nine it could see. A gate that reports success
# over part of its subject is worse than no gate: the exit code reads as reach.
#
# The obvious repair -- "parse every table in the block" -- is WRONG, and the
# corpus says so. `_SECTION_END` cuts at the next h2, so an `### N.N Details by
# ID` subsection stays INSIDE the block by design, and three shipped tasks put
# non-RTM tables there: `task-096` (a corpus-measurement table and a
# rejected-candidates table), `task-085` (a prefix legend and an issue index),
# `task-101` (a derivation table). Reading those as requirements invents ids
# like `Bold density`; refusing on "more than one table" fails all three. Both
# variants break a gate on the artifacts it governs.
#
# What separates a continuation from a foreign table is its HEADER ROW. An RTM
# split by epic repeats its columns per epic (`skill-planning-format` encourages
# the grouping); a `Details by ID` table has different columns because it
# tabulates something else. So: the first table fixes the shape, every later
# table with an IDENTICAL header row is the same RTM continued, and anything
# else is skipped -- BY NAME, never silently, which is the half of RF-6 that
# refusing would also have satisfied and staying quiet would not.
#
# Measured on the corpus at the time of the fix: 3 files carry more than one
# table in the RTM block, and in all 3 every later table has a different header
# -- so this rule reads the corpus exactly as before (0 changed counts) while
# the five-epic case now reports all 23. Scanning continues past a foreign
# table rather than stopping at it: `RTM-E1 / Details / RTM-E2` must not lose
# E2 to a subsection someone filed in the middle.
def _split_tables(block):
    """Contiguous markdown-table chunks of *block*, in document order.

    Splitting here keeps `parse_markdown_table` untouched -- its stop-at-first-
    non-table-line behaviour is correct FOR ONE TABLE and is pinned by tests.
    """
    chunks, current = [], []
    for line in block.split('\n'):
        if line.strip().startswith('|'):
            current.append(line)
        elif current:
            chunks.append('\n'.join(current))
            current = []
    if current:
        chunks.append('\n'.join(current))
    return chunks


def locate_rtm(content, artifact="TASK.md"):
    """Locate the RTM and extract ``(rows, ids, errors, notes)``.

    Shared by both modes so that the two cannot drift apart again — they held
    two copies of this logic, and only one of them got fixed each time.

    Anchor present -> the table is read POSITIONALLY: the first column holds
    the requirement id, whatever it is called. Column names are prose.
    Anchor absent  -> the pre-existing English column-name contract, unchanged.

    ``notes`` are non-fatal lines the caller MUST print: they say how much of
    the section was read (RF-6). A gate is allowed to read part of a document;
    it is not allowed to do so quietly.
    """
    block, err = _anchor_block(content)
    via_anchor = block is not None
    if err:
        return None, None, [err], []

    if not via_anchor:
        if not RTM_HEADER.search(content):
            return None, None, [
                "Error: '## Requirements Traceability' section missing in %s." % artifact,
                "Please add the RTM table (a section number and a trailing "
                "'Matrix' are both fine), or mark it with the "
                "'<!-- %s -->' anchor — the anchor works in any language." % ANCHOR_NAME], []
        block = _SECTION_END.split(RTM_HEADER.split(content)[1].strip())[0]

    chunks = _split_tables(block)
    rows = parse_markdown_table(chunks[0]) if chunks else []
    if not rows:
        if via_anchor:
            return None, None, [
                "Error: no requirements table found under the '<!-- %s -->' "
                "anchor in %s." % (ANCHOR_NAME, artifact)], []
        return None, None, [
            "Error: Requirements Traceability Matrix table is empty or invalid."], []

    if via_anchor:
        columns = _table_columns(chunks[0])
        if len(columns) < 2:
            return None, None, [
                "Error: the table under '<!-- %s -->' has %d column(s); an RTM "
                "needs at least an id column and one more."
                % (ANCHOR_NAME, len(columns))], []
        id_column = columns[0]
    else:
        expected_cols = ['ID', 'Requirement']
        if not all(col in rows[0] for col in expected_cols):
            return None, None, [
                "Error: RTM table must contain columns: %s" % expected_cols,
                "Or mark the table with the '<!-- %s -->' anchor, which reads "
                "the first column as the id and needs no English column names."
                % ANCHOR_NAME], []
        id_column = 'ID'

    # An RTM split by epic repeats its header per epic; a `Details by ID`
    # subsection tabulates something else and does not. Same header -> same
    # RTM, continued. See the commentary above `_split_tables`.
    header = _table_columns(chunks[0])
    read_tables, skipped = 1, []
    for chunk in chunks[1:]:
        if _table_columns(chunk) == header:
            rows.extend(parse_markdown_table(chunk))
            read_tables += 1
        else:
            skipped.append(' | '.join(_table_columns(chunk)))

    notes = []
    if read_tables > 1:
        notes.append(
            "Note: the RTM in %s spans %d tables with identical columns; all "
            "%d were read." % (artifact, read_tables, read_tables))
    if skipped:
        notes.append(
            "Note: %d further table(s) in the RTM section of %s were NOT read "
            "as requirements — their columns differ from the RTM's (%s). "
            "Repeat the RTM's exact header to have a table read as a "
            "continuation." % (len(skipped), artifact,
                               '; '.join(repr(s) for s in skipped)))

    ids = [r[id_column] for r in rows if id_column in r]
    return rows, ids, None, notes


def parse_markdown_table(content):
    """
    Parses a markdown table into a list of dictionaries.
    Assumes the first row is the header, and the second row is the separator.
    """
    lines = content.split('\n')
    table_data = []
    headers = []
    
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            if in_table:
                break # End of table
            continue
            
        # It's a table row
        # Remove leading/trailing pipes and split using regex to handle escaped pipes \|
        # split by pipe that is NOT preceded by backslash
        cells = re.split(r'(?<!\\)\|', stripped.strip('|'))
        cells = [c.strip() for c in cells]
        
        if not in_table:
            # First row = Headers
            headers = cells
            in_table = True
        elif '---' in cells[0]:
            # Separator row
            continue
        else:
            # Data row
            if len(cells) != len(headers):
                # Handle mismatched columns if necessary, or skip
                continue
            
            row_dict = dict(zip(headers, cells))
            table_data.append(row_dict)
            
    return table_data

def validate_task(task_path):
    """
    Validates TASK.md for Requirements Traceability Matrix.
    """
    if not os.path.exists(task_path):
        print(f"Error: File '{task_path}' not found.")
        sys.exit(1)
        
    with open(task_path, 'r') as f:
        content = f.read()
        
    # check for bypass
    if "[BYPASS_VALIDATION]" in content:
         print("Validation bypassed via [BYPASS_VALIDATION] flag.")
         sys.exit(0)

    # Locating the RTM and reading its id column is ONE decision, made in
    # locate_rtm() and shared with validate_plan below. It used to be two
    # copies, and each fix landed in only one of them — which is precisely the
    # half-applied-fix defect this task also closes elsewhere.
    rows, _ids, errors, notes = locate_rtm(content, artifact="TASK.md")
    if errors:
        for line in errors:
            print(line)
        sys.exit(1)

    # Printed BEFORE the verdict: how much of the section was read qualifies
    # the count that follows, and a qualifier after the word `Success` is read
    # by nobody (RF-6).
    for line in notes:
        print(line)
    print(f"Success: Found {len(rows)} requirements in TASK.md.")
    sys.exit(0)

def validate_plan(plan_path, task_path):
    """
    Validates PLAN.md against TASK.md RTM.
    """
    if not os.path.exists(plan_path):
        print(f"Error: File '{plan_path}' not found.")
        sys.exit(1)
    if not os.path.exists(task_path):
        print(f"Error: File '{task_path}' not found.")
        sys.exit(1)

    with open(task_path, 'r') as f:
        task_content = f.read()
    
    # check for bypass
    if "[BYPASS_VALIDATION]" in task_content:
         print("Validation bypassed via [BYPASS_VALIDATION] flag.")
         sys.exit(0)

    # Same locator as validate_task. The old code here re-derived the ids with
    # `r['ID']` — a dict lookup on the AUTHORED header text — which is a second,
    # independent language coupling: it kept --mode plan dead on a non-English
    # document even after the column-name check in validate_task was fixed.
    _rows, rtm_ids, errors, notes = locate_rtm(task_content, artifact="TASK.md")
    if errors:
        for line in errors:
            print(line)
        sys.exit(1)

    # Same reason as validate_task: the coverage verdict below is a claim about
    # the ids that were READ, so what was read is stated first (RF-6).
    for line in notes:
        print(line)

    if not rtm_ids:
        print("Error: No IDs found in RTM table.")
        sys.exit(1)

    # Check PLAN for IDs
    with open(plan_path, 'r') as f:
        plan_content = f.read()

    # The contract is "every RTM item is referenced somewhere in the PLAN". Enforce THAT,
    # not a literal `[**R-1**]` token — which is what the original version demanded and why
    # the gate never passed on a shipped plan.
    #
    # IDs are referenced wherever the plan tracks them: the corpus splits between `- [ ]`
    # checklist bullets and `## Step N — ... (R1, R2)` step headings (some plans use prose),
    # so restricting to checklist lines would fail the majority. Search the WHOLE plan body,
    # but as a WHOLE TOKEN — `R1` must not be satisfied by `R10`, and the token charset
    # includes `-` for hyphenated namespaces (`R-065-1`, `TF-X-7`). IDs are normalised of
    # markdown emphasis / brackets / backticks first. A genuinely un-referenced ID (e.g. a
    # plan that omits R10, or tracks findings under a different `F#` scheme) is a real
    # traceability gap — reporting it is the gate doing its job, not a false negative.
    missing_ids = []
    for rid in rtm_ids:
        bare = rid.strip().strip("*`[] ")
        if not bare:
            continue
        token = re.compile(r'(?<![\w-])' + re.escape(bare) + r'(?![\w-])')
        if not token.search(plan_content):
            missing_ids.append(bare)

    if missing_ids:
        print(f"Error: The following Requirement IDs are NOT covered in PLAN.md: {missing_ids}")
        print("Please reference every RTM ID somewhere in PLAN.md "
              "(a step heading like '## Step 1 — ... (R1)' or a '- [ ] R1 ...' bullet).")
        sys.exit(1)
        
    print(f"Success: All {len(rtm_ids)} requirements covered in PLAN.md.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Validate artifacts for VDD-Enhanced workflow.")
    parser.add_argument("--mode", required=True, choices=['task', 'plan'], help="Validation mode")
    parser.add_argument("files", nargs='+', help="Input files. mode=task: [task.md], mode=plan: [plan.md task.md]")
    
    args = parser.parse_args()
    
    if args.mode == 'task':
        if len(args.files) < 1:
            print("Error: mode=task requires [task_path]")
            sys.exit(1)
        validate_task(args.files[0])
        
    elif args.mode == 'plan':
        if len(args.files) < 2:
            print("Error: mode=plan requires [plan_path] [task_path]")
            sys.exit(1)
        validate_plan(args.files[0], args.files[1])

if __name__ == "__main__":
    main()
