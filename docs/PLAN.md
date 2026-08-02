# Development Plan — TASK 095: Structural anchors and gate honesty

**TASK:** [docs/TASK.md](TASK.md) · **Spec audit:** [framework-audit-095-spec.md](reviews/framework-audit-095-spec.md)
**Methodology:** Stub-First. Every code change lands its failing test before its logic.

---

## 0. Rollback

Before Stage 1, back up every file this plan edits:

```bash
mkdir -p .agent/archive/095
for f in \
  .agent/skills/documentation-standards/SKILL.md \
  .agent/skills/known-issues-format/SKILL.md \
  .agent/skills/developer-guidelines/SKILL.md \
  .agent/skills/skill-spec-validator/SKILL.md \
  .agent/skills/skill-spec-validator/scripts/validate.py \
  .agent/skills/skill-planning-format/assets/templates/plan_md_template.md \
  .agent/skills/skill-planning-format/assets/templates/task_md_template.md \
  .agent/skills/skill-product-backlog-prioritization/scripts/calculate_wsjf.py \
  .agent/tools/task_id_tool.py .agent/tools/archive_protocol.py \
  .agent/workflows/vdd-enhanced.md .agent/workflows/vdd-adversarial.md \
  System/Agents/02_analyst_prompt.md System/Docs/SKILLS.md System/Docs/WORKFLOWS.md \
  docs/design/095_workflow_loop_contract.md ; do
  [ -f "$f" ] || continue
  mkdir -p ".agent/archive/095/$(dirname "$f")" && cp "$f" ".agent/archive/095/$f"
done
echo "backed up: $(find .agent/archive/095 -type f | wc -l | tr -d ' ') files"   # expect 16
```

> The trailing count is not decoration. The first version of this block used `install -D`, which
> GNU coreutils has and BSD/macOS `install` does not: every copy failed, `&&` swallowed it, and the
> loop exited 0. The count printed `0` and the step was caught immediately. This is `T-095-05`'s
> third rule — *a zero exit is not evidence of work* — demonstrated on this plan's own first command.

Restore: `cp -R .agent/archive/095/. .` — no migration, no data format change, so restore is
sufficient at any point. `core-principles` and `skill-safe-commands` are not in the list because
this plan does not touch them (TASK A5).

<!-- contract:sequence -->

## 1. Task Execution Sequence

### Stage 1: Contract — declare before anyone reads it

- [ ] **T-095-01 — Anchor doctrine and registry** — covers `R1`, and the registry half of `R4`.
      [docs/tasks/task-095-01-anchor-doctrine.md](tasks/task-095-01-anchor-doctrine.md)
      Adds the third rung and the reserved-anchor registry to `documentation-standards` (§4.3/§4.4),
      with a pointer from `known-issues-format` to its two rows there.
      No script reads anything new yet — this is the declaration Stage 2
      implements against. `docs/ARCHITECTURE.md` §7.2 (already written) is its architectural anchor.

### Stage 2: Structure and stubs `[STUB CREATION]`

- [ ] **T-095-02 Phase 1 — Validator: failing tests first** — covers `R2`, `R3`, `R6` (Red).
      [docs/tasks/task-095-02-validator-anchor.md](tasks/task-095-02-validator-anchor.md)
      New `_slice_rtm_block()` helper as a stub returning the current behaviour verbatim, so the 38
      existing tests stay green; new tests for the non-English fixture in **both** modes, which must
      FAIL. Explicit check: the anchor is a separate branch, never an alternation inside
      `RTM_HEADER` — `test_validate.py:70-77` pins that split at exactly two parts.

### Stage 3: Core functionality implementation

- [ ] **T-095-02 Phase 2 — Validator: anchor lookup and positional columns** — covers `R2`, `R3` (Green).
      Anchor-first lookup in both `validate_task` and `validate_plan`; the ID column resolved by
      position with the `['ID','Requirement']` name check kept as the fallback for anchorless
      documents. Both hard-fail sites (`:105` and `:145`) close in one commit — a half-applied fix
      here would reproduce WI-32 inside the fix for WI-30.

- [ ] **T-095-03 — Templates and prompts emit anchors** — covers `R4`, `R5`.
      [docs/tasks/task-095-03-templates-emit-anchors.md](tasks/task-095-03-templates-emit-anchors.md)
      `plan_md_template.md`, `task_md_template.md`, and the RTM clause of `02_analyst_prompt.md`.
      Emission only; nothing is required to read these anchors yet, which is what keeps `R6` true.

- [ ] **T-095-04 — Sibling defects of the same class** — covers `R7`.
      [docs/tasks/task-095-04-sibling-defects.md](tasks/task-095-04-sibling-defects.md)
      `calculate_wsjf.py` column-name check; `task_id_tool.py` + `archive_protocol.py` silent
      `"untitled"` collision. Each lands its failing test first.

- [ ] **T-095-05 — Gate-verification rules** — covers `R8`.
      [docs/tasks/task-095-05-gate-verification-rules.md](tasks/task-095-05-gate-verification-rules.md)
      One qualifying clause in `developer-guidelines` §5.1 (write-scope vs verdict-scope) and a new
      §6.3. TIER 1 only — `core-principles` line count is pinned unchanged by acceptance A5.

- [ ] **T-095-06 — Adversarial cycle: find-all-sites and a real brief** — covers `R9`, `R10`.
      [docs/tasks/task-095-06-adversarial-cycle.md](tasks/task-095-06-adversarial-cycle.md)
      New `vdd-enhanced.md` §4 item **appended as item 6**; brief promoted to a named input block in
      `vdd-adversarial.md` step 2a on the `.agent/workflows/vdd-multi.md:110-124` pattern.

### Stage 4: Testing

- [ ] **T-095-07 — Full regression and corpus re-measurement** — verifies `R2`, `R3`, `R6`, `R7`.
      Run every gate the way CI runs it (this plan's own subject matter — see T-095-05):
      ```bash
      bash .agent/skills/skill-spec-validator/scripts/tests/run_tests.sh
      PYTHONPATH=. pytest -p no:cacheprovider tests/test_tool_runner.py \
        tests/test_tool_runner_security_contract.py tests/test_spec_validator.py \
        tests/test_inline_efficiency.py tests/test_positional_refs.py tests/test_scratch_hygiene.py -q
      python System/scripts/validate_skills.py --root . --quiet
      python System/scripts/check_prompt_references.py --root .
      python System/scripts/security_lint.py --root .
      python System/scripts/smoke_workflows.py --root .
      ```
      Then re-run the §1.1 R2 corpus measurement in **both** repositories and record the before/after
      pass counts. A count that did not rise, or fell, is a failure, not a footnote.

### Stage 5: Documentation and closure

- [ ] **T-095-08 — Spec 095 evidence and independent review** — covers `R11`, `R12`.
      [docs/tasks/task-095-08-spec-095-evidence.md](tasks/task-095-08-spec-095-evidence.md)
      Field evidence appended to `docs/design/095_workflow_loop_contract.md` §7.1; the critics'
      report filed under `docs/reviews/`. **No `run_stack.py` is created by this task** (TASK §5).

- [ ] **T-095-09 — System/Docs, CHANGELOG, ledgers** — covers `R13`.
      [docs/tasks/task-095-09-docs-and-ledgers.md](tasks/task-095-09-docs-and-ledgers.md)
      `SKILLS.md` rows, `WORKFLOWS.md` VDD row, `CHANGELOG.md` (+ `.ru`), and closing WI-30/31/32 in
      the reporting project's ledger — where "closed" means verified against the landed diff, per
      `known-issues-format`: *"sent for review is not closed"*.

- [ ] **T-095-10 — Positional references, verified LAST** — covers `R9` acceptance A6.
      `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py`
      Run **after** every artifact edit above is final — this is `documentation-standards` §4.1
      applied to this plan's own change, and running it earlier is the exact failure that rule names.

<!-- contract:coverage -->

## 2. Use Case Coverage

| Use Case | Covered by |
| :--- | :--- |
| UC-1 Non-English project runs the first gate | T-095-02 (both phases), T-095-07 |
| UC-1 Alt A — anchorless legacy document | T-095-02 Phase 1 (the 38 existing tests are the assertion), T-095-07 corpus floors |
| UC-1 Alt B — anchor with no table | T-095-02 Phase 2 |
| UC-2 Author writes a new TASK | T-095-01, T-095-03 |
| UC-3 Orchestrator fixes an assertion mid-cycle | T-095-06 |

## 3. Ordering constraints

1. **T-095-01 before T-095-02.** The anchor's spelling is a contract; implementing a reader before
   the registry names it is how the second one-off gets created.
2. **T-095-02 Phase 1 strictly before Phase 2.** The non-English test must be observed FAILING. A
   test written after the fix proves the test, not the fix.
3. **T-095-10 last, unconditionally.** Ordinals shift as §4 gains an item.
4. **T-095-09 after T-095-07.** A ledger entry that claims a fix before the regression ran is the
   defect WI-31 is about.
