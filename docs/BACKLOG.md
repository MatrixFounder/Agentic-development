# Framework Backlog

Living work-item ledger for agentic-development. Defects live in
[`docs/issues/`](issues/) + [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md); this file holds
enhancement/work-item signals. Rows are appended by the `run-feedback` skill
(`file --as work-item`) or by hand; prioritize explicitly when picking work.

## Discovered Issues

<!-- feedback:discovered-issues -->
- **Add unit tests for skill-spec-validator (2026-07-20)** — skill-spec-validator ships zero unit tests. Both matchers (RTM heading + PLAN ID coverage) drifted from the real house convention and failed on 100% of artifacts across >=2 prior "fixes", undetected until a manual corpus run in TASK 090. Add tests/ with fixtures covering: the 6 RTM heading forms (h2-h4, section number, trailing (RTM), bare `Requirements (RTM)`), ID references in both `## Step N (R1)` headings and `- [ ]` bullets, the R1-vs-R10 whole-token boundary, and the empty-table / bypass paths. · Effort: S · Value: prevents silent matcher drift / dead gate
