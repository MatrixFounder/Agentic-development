# PLAN 103 — A positional reference carries its referent

**TASK:** [docs/TASK.md](TASK.md) · **Covers:** R1–R11 · **Acceptance:** A1–A9

## Sequencing rule

Seven clusters. Cluster A declares every new surface as a stub and asserts the module still imports
and the existing battery still passes — Stub-First per `core-principles` §2, so a syntax or wiring
error is caught before any logic exists. Cluster B writes the tests against those stubs and leaves
them **red on purpose**: the red list is the specification the next three clusters discharge, one
at a time. Clusters C–E turn them green in dependency order. Cluster F writes the normative text
only after the behaviour it describes exists, which is `documentation-standards` §4.1 applied to
this task itself. Cluster G closes the ledger, both changelogs, and runs every gate.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | Stubs and surface | `check_positional_refs.py` | R3, R4, R5, R6 (declarations only) |
| B | Battery, red | `tests/test_positional_refs.py` | R2–R7 |
| C | Referent detection and the four outcomes | `check_positional_refs.py` | R1, R2, R3 |
| D | Fix mode | `check_positional_refs.py` | R4 |
| E | Selection and coverage | `check_positional_refs.py` | R5, R6, R7 |
| F | Normative text and registry | `SKILL.md`, `authoring-contract.md`, `System/Docs/SKILLS.md` | R1, R8, R9, R11 |
| G | Ledger, changelogs, gates | ledgers, `CHANGELOG*.md` | R10, A1–A9 |

**Baselines, measured before Cluster A** (re-derive with the same two commands):

| Gate | Value now |
| :--- | :--- |
| `python3 -m pytest tests/test_positional_refs.py -q` | 89 passed |
| `python3 System/scripts/validate_skills.py --root .` | 46/46 passed |

**Backup.** Before Cluster A: `mkdir -p .agent/archive`, then copy each file the clusters edit to
`.agent/archive/<name>.bak`. The workflow's §3.1 step backs up bootstrap files only; this task edits
none of them, so `CLAUDE.md`, `AGENTS.md` and `GEMINI.md` are copied for the fallback step and are
expected to stay byte-identical. The set to copy:

```
.agent/skills/documentation-standards/scripts/check_positional_refs.py
.agent/skills/documentation-standards/SKILL.md
.agent/skills/artifact-formalizer/references/authoring-contract.md
tests/test_positional_refs.py
System/Docs/SKILLS.md
CHANGELOG.md  CHANGELOG.ru.md
```

**Rollback.** Every edit is to a tracked file; no cluster moves or deletes one. Reverting is
`git checkout --` on the seven paths above **plus three not in the backup set**:
`docs/ARCHITECTURE.md` (edited in the Architecture phase, §7.2's ladder), `docs/BACKLOG.md`, and the
new `docs/backlog/wi-17-*.md`, which is untracked until Cluster G and is removed with `rm`.
Reverting the code alone leaves §7.2 describing a rung that does not exist and the ledger holding a
record for work that was undone — the record-vs-reality breakage the ledger format forbids.

**One property is load-bearing across every cluster.** A reference carrying no referent must remain
*not examined* — never a finding of any severity. It is asserted first (B1), before any detection
exists, and re-asserted last (G5) against this repository's own corpus. If any cluster makes it
fail, that cluster is wrong, not the assertion: 324 references across four consumer repositories
depend on it, and the symlinked skill directory reaches them at commit time with no adoption step.

## Cluster A — stubs and surface (Stub-First)

- [x] A1. Add the three finding kinds as module constants beside the existing ones:
      `REFERENT_MOVED`, `REFERENT_AMBIGUOUS`, `REFERENT_ABSENT`. No emitter yet.
- [x] A2. Add `REFERENT_SPAN`, the regex for a code span following a reference code span, separated
      by whitespace and at most one comma. Declared next to `CODE_SPAN_REF`, unused.
- [x] A3. Add `extract_referent(line, ref_end) -> str | None` as a stub returning `None`, with the
      docstring stating the adjacency rule and the two normalizations (collapse whitespace,
      unescape `\|`).
- [x] A4. Add the CLI surface, all inert: `--fix` (store_true), `--targets-changed` (store_true).
      `--all` keeps its signature; Cluster E teaches `collect_docs()` to accept files.
- [x] A5. Extend the `Finding` / report plumbing with the referent counters R7 needs, initialized to
      zero and printed nowhere yet.
- [x] A6. Run `python3 -m pytest tests/test_positional_refs.py -q`. **Expected: 89 passed** — the
      stubs changed no behaviour. A failure here is a wiring error, isolated before any logic.

**Why stubs before tests.** `core-principles` §2 requires the structure importable before logic.
A6 is the verification checkpoint that separates "the surface is wrong" from "the logic is wrong",
which is the distinction the next cluster's red list would otherwise hide.

## Cluster B — the battery, deliberately red (R2–R7)

- [x] B1. **R2, the load-bearing case.** A document citing `path:line` with no adjacent code span
      produces **no finding of any severity**, exit 0, and is counted as not examined. Assert on the
      finding list being empty for that reference, not merely on the exit code — exit 0 is also what
      a warning produces.
- [x] B2. **R3, four cases.** Referent on the cited line → no finding. Referent unique elsewhere →
      `REFERENT_MOVED` carrying both numbers. Referent matching several lines → `REFERENT_AMBIGUOUS`
      carrying the candidates. Referent nowhere → `REFERENT_ABSENT` carrying what now sits on the
      cited line.
- [x] B3. **R3, the two normalizations.** A referent escaped as `\|` inside a table cell matches an
      unescaped pipe in the target; a referent written without indentation matches an indented target
      line. Each is a case, not a shared fixture: they fail for different reasons and a merged case
      reports only one of them.
      **Plus D9's stated cost:** a referent written *before* its reference, or wrapped across two
      document lines, is **not examined** — no finding of any severity. Asserted, because a silent
      narrowing that reads as coverage is the defect this task exists against.
- [x] B4. **R4, the fix boundary.** `--fix` on `REFERENT_MOVED` rewrites the number and leaves the
      referent byte-identical. `--fix` on `REFERENT_ABSENT` and on `REFERENT_AMBIGUOUS` writes
      nothing. A run without `--fix` writes nothing in any case.
      **Plus the whole-document assertion:** the fixed file differs from its input in exactly the
      intended character range and nowhere else. Without it, a rewrite that also normalizes line
      endings, strips trailing whitespace or drops a final newline passes every case above while
      silently editing every document it is pointed at.
- [x] B5. **R5.** A change touching only a source file selects the documents citing it. Pins the
      defect directly: today that change selects nothing.
- [x] B6. **R6.** `--all` given a file path scans that file; given a directory, it still rglobs.
- [x] B7. **R7.** The coverage line states, separately, how many references carried a referent, how
      many did not, and how many did not resolve. Assert on the three numbers summing to the total
      reported — a coverage line that does not add up is the defect this requirement exists against.
- [x] B8. Run the battery. **Expected: 89 passed, and the new cases red.** Record the count of new
      cases here at execution time; that number is the specification Clusters C–E discharge.

## Cluster C — referent detection and the four outcomes (R1–R3)

- [x] C1. Implement `extract_referent()` per its A3 docstring.
- [x] C2. Implement the four outcomes in `classify()`, after the existing path/range checks. A
      reference that fails to resolve keeps its current kind: `UNRESOLVABLE` and `AMBIGUOUS` are
      about the path and must not be masked by a referent verdict.
- [x] C3. Give `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS` severity `error`, `REFERENT_MOVED`
      severity `error` with the repair named in its detail string.
- [x] C4. Run the battery. Expected: B1, B2, B3 green; B4–B7 still red.

## Cluster D — fix mode (R4)

- [x] D1. Implement `--fix`: for `REFERENT_MOVED` only, rewrite the line number in the citing
      document, in place, leaving every other byte of the line untouched.
- [x] D2. Assert the boundary in code, not only in tests: the write path receives the new number and
      the reference span, never the referent span.
- [x] D3. Amend the module docstring's third design constraint. It reads "Read-only. The tool never
      writes to the repository" and becomes the narrowed statement — the check never writes; the
      separately-invoked `--fix` writes a line number and never a referent. **A4 fails while the old
      sentence stands.**
- [x] D4. Run the battery. Expected: B4 green.

## Cluster E — selection and coverage (R5–R7)

- [x] E1. Implement `--targets-changed`: build the target→citing-documents index while resolving,
      and select documents citing any path in `changed_files()`.
- [x] E2. Teach `collect_docs()` to accept a file argument as itself and a directory as an rglob.
- [x] E3. Extend the coverage line with the three referent counts, in the shape §4.2's existing note
      already uses for ordinals.
- [x] E4. Run the battery. **Expected: all green, 89 + new cases.**

## Cluster F — normative text and registry (R1, R8, R9, R11)

- [x] F1. `documentation-standards` §4.1 — state the referent rule: an unpinned `path:line` in a
      living corpus carries a referent; a reference without one is not examined, not an error. Name
      the two spellings. State that §4.3's anchor is a different object (TASK 103 D7).
- [x] F2. §4.2 — state the corpus distinction. The 54-of-84 measurement was taken over archived
      reviews and stays as written; the referent layer is gateable over a **named** living corpus and
      stays advisory elsewhere. Add the new finding kinds to the findings table.
- [x] F3. `artifact-formalizer/references/authoring-contract.md` — one licensed-form row, per the
      WI-16 §5.3 precedent, inside `documentation-standards` §5.1's 120-character one-clause cap.
      The row uses commas rather than `|`, which a table cell cannot carry unescaped.
- [x] F4. `System/Docs/SKILLS.md` — the `documentation-standards` row names the resolver, its
      referent layer and its fix mode (R11).
- [x] F5. Run `python3 System/scripts/validate_skills.py --root .`. **Expected: 46/46** — this task
      adds no skill, so a changed count is a defect.

**Why the text lands after the behaviour.** §4.1 itself prescribes that positional references are
verified after the artifact edits are final. F1–F4 cite the tool's kinds and flags; writing them
before Clusters C–E exist would author claims about a state that does not yet hold.

## Cluster G — ledger, changelogs, gates (R10, A1–A9)

- [x] G1. File `WI-17` — `docs/backlog/wi-17-<slug>.md` plus its index line inserted directly after
      `<!-- feedback:discovered-issues -->` in `docs/BACKLOG.md`, newest first. `provenance: human`,
      `source` naming onchain-analytics WI-43. Record and index line in the same commit.
- [x] G2. Close it in the same run (**collapsed into G1**: both land in the same commit,
      so the record was authored already carrying its resolution — four elements, not three): `status: done`, `resolved_at`, `resolved_by: TASK 103`, a
      resolution blockquote at the top of the body, and the index line moved to `## Closed`. Four
      edits, not three — flipping fewer leaves the record contradicting its index.
- [x] G3. `CHANGELOG.md` and `CHANGELOG.ru.md` — one entry each, both in the same commit (A7).
- [x] G4. Full battery: `python3 -m pytest tests/test_positional_refs.py -q`, then
      `python3 System/scripts/validate_skills.py --root .`.
- [x] G5. **A8 — run the tool on this repository's own living corpus** and record the output in this
      plan below this line. Six references exist here; the run must show them as not examined, since
      D5 puts adding referents to them out of scope. A run reporting them as findings falsifies R2
      and blocks the task.
- [x] G6. **A8, second corpus — the blast-radius evidence.** Run the shipped tool **read-only** (no
      `--fix`) against a consumer repository's living corpus and record the finding count. Six
      references here cannot distinguish "the rule holds" from "the corpus is too small to fire it";
      the property protects 324 references across four repositories reached by symlink at commit
      time. Use `Universal-skills` (36 references) at minimum, `obsidian-llm-wiki` (99) preferred.
      **Blocks the task** if any unreferenced coordinate produces a finding.
- [x] G7. Update `.agent/sessions/latest.yaml` via `update_state.py`.

### G5 result — this repository

```bash
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py \
  --all docs/ARCHITECTURE.md docs/TASK.md docs/PLAN.md
```

**First run: exit 1, four errors — all four in this task's own artifacts.** Every one was a
cross-repository coordinate (`registry.ts:1083`, three onchain-analytics paths) read as a local
reference and reported `UNRESOLVABLE`. Fixed with the mechanism §4.1 already provides and this task
did not have to invent: an `@e95b909` pin, which is *true* — those are claims about another
repository at the revision this task measured. A pinned reference is skipped before resolution.

**Second run: exit 0.** `0 error(s), 2 warning(s) across 21 reference(s) (6 path:line + 15 ordinal)
in 3 document(s)`. Both warnings are `DRIFT_SUSPECT` on `check_positional_refs.py:17` and
`System/Docs/SKILLS.md:68` — files this very change edits, which is §4.1's own case working as
designed. Both confirmed: the printed target lines are what the citing documents claim.

**A8 therefore did what it exists for.** Running the tool on real artifacts found four true defects
that no test case would have produced, in the documents of the task shipping the tool.

### G6 result — consumer corpora

Read-only, no `--fix`, over `--all docs` (a deliberately over-wide scope: it includes archives):

| Repository | REFERENT findings | `path:line` coverage line |
| :--- | :--- | :--- |
| obsidian-llm-wiki | 37 | 39 with a referent, **348 without (not examined)**, 106 unresolvable, 1 pinned |
| Universal-skills | 3 | 3 with a referent, **139 without (not examined)**, 96 unresolvable |
| onchain-analytics | 115 | 122 with a referent, **845 without (not examined)**, 223 unresolvable |

**R2 holds: not one unreferenced coordinate produced a finding** — 1332 of them across three
repositories, all reported as not examined. That is the property the whole upgrade rests on.

**What the acceptance criterion did not anticipate, stated rather than hidden.** References that
*happen* to carry a referent — a backticked token already sitting after a coordinate — are now
judged, and there are 155 of them across the three repositories. Sampled all three in
Universal-skills: **all three are true positives** (a predicate that moved 150 → 890, one that moved
264 → 283, one whose cited text no longer exists). Two of the three sit in **archived** documents,
where a stale coordinate is a correct record of a past state and not a defect — which is exactly why
§4.2 now scopes gating to a **named** living corpus and leaves everything else advisory. Nothing is
red anywhere today regardless: no workflow invokes the resolver (OQ-1).
