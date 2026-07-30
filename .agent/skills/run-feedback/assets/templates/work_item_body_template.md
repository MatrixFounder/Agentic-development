> Origin: [run / task / review that surfaced this]. Remove if none.
> For a work-item whose fix lands in a SHARED artifact (skill, agent prompt, workflow): state here
> that it is **a behaviour change for the owner's review, not a landed fix** — and keep it accurate
> until verified in that repo.

**Signal.** What was observed, one paragraph. Concrete and dated; quote the command or output
(redacted) if there was one. No fix language yet.

**Why it matters.** The cost of leaving it as-is: whose time, which workflow, how often. If the
answer is "cosmetic", say so — that is a legitimate `effort: S` item, not a reason to inflate it.
A work-item with no broken contract is not a defect; if a contract IS broken, file it as a defect
instead.

**Generalized.** Strip the language, tool, repo layout, and project name: state the rule so it holds
on every stack the framework supports. Concrete commands belong in a per-ecosystem table, never in
the rule. (Required when the resolution touches a shared artifact; skip for project-local items.)

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 |        |      |           |
| 2 |        |      |           |
| 3 | do nothing, document the constraint | — | what stays broken |

**Recommendation.** Which option and why, in one or two sentences. Name the minimum acceptable
outcome separately from the ideal one — a half-fix that is honest beats a full fix that is deferred
forever.

**Acceptance.** How anyone can tell this is done — the observable state, not the intended edit.

**Related.** Sibling work-items / issues (`[label](…)`), review findings, `finding_ref`. Say
explicitly when something looks like a duplicate but is not, and why.
