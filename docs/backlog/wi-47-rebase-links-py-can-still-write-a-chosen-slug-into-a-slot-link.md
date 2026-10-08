---
id: WI-47
type: work-item
status: open
opened_at: 2026-10-08
slug: wi-47-rebase-links-py-can-still-write-a-chosen-slug-into-a-slot-link
effort: S
value: 'the file mode of rebase_links.py writes into a link only what its author or the archive step wrote'
source: 'TASK 116 D23'
component: '.agent/tools/rebase_links.py'
---

# WI-47 — rebase_links.py can still write a chosen slug into a slot link

> Origin: stage-2 round 7 of TASK 116, the security audit's L1 and I1 and I2. TASK 116 §11 states
> each residual, and D23 files them here.

**Signal.** After TASK 116 R8, the file mode of `rebase_links.py` writes into a link of a markdown
file under `docs/` only the parts its author wrote, `..`, and the parts of a slot archive. Three
residuals remain:

- **The slug of a slot archive.** R8.1 admits any slug of the grammar of `archive_move.SLUG`.
  Measured: `--slot docs/TASK.md=docs/tasks/task-116-marker-chosen-words-here.md` on
  `[t](../TASK.md)` gave `[t](task-116-marker-chosen-words-here.md)`, exit 0, with no file on
  disk.
- **Reordered or repeated parts.** The check of path parts is a set test. Measured:
  `[a](one/two/three.md)` with `--from docs/two/one` gave `../two/one/one/two/three.md`. Each
  shape needs the target file to exist.
- **A splice of overlapping links.** Two link matches that overlap are spliced into a part that
  no single record holds: a reference definition, or an `href=` or `src=` value, that holds an
  inline link. Measured: `[r]: ](x`, where `docs/](x` and `docs/x` exist, was written as
  `[r]: ../](x../x`; `<a href="](x">`, where `docs/](x` and `docs/x">` exist, was written as
  `<a href="../](x../x">`. The base splices so too.

**Why it matters.** The script runs with no prompt under
`Bash(python3 .agent/tools/rebase_links.py *)`. An agent steered by injected text can write
lowercase words into the slot link of a document that the next phase reads.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Bind a slot archive's `<ID>-<slug>` to the operand's own name, as the archive steps pass it | S | the typo cases of ARC-6 exit 2 before `--slot-must-exist` reports them |
| 2 | Require the new parts, but `..`, to be a tail of the authored parts or of the archive's | S | measured to refuse none of 280 archive rewrites |
| 3 | Refuse when the new text's length is not the old length plus each record's change | S | catches the splice and the duplication of TASK 116 round 6 |

**Recommendation.** Options 1 to 3 together; each is a small check in `_file_mode`.

**Acceptance.** A case of `tests/test_script_guards.py` makes each of the three shapes, both
splices among them, and the file mode refuses each with exit 2 and no write.

**Related.** [WI-46](wi-46-rebase-links-py-opens-a-checked-path-again-to-write-it.md);
[ARC-6](../issues/arc-6-a-slot-map-whose-target-does-not-exist-rewrites-the-link-and-exits-0-ok-true-because-slot-resolved.md);
TASK 116 R8 and §11.
