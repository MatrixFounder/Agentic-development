---
id: FW-1
type: known-issue
status: fixed
opened_at: 2026-07-20
category: validation
severity: SEV-4
slug: validator-bypass-substring
component: skill-spec-validator
fingerprint: 823677cffc508f6b
finding_ref: fnd-20260720-193131-823677cf
resolved_at: 2026-10-29
resolved_by: TASK 136
---

# FW-1 — Spec-validator bypass token matches anywhere in content

> **Resolved 2026-10-29 by TASK 136.** `validate.py` reads the token only in the first h1 outside
> a fenced block, in both modes, through `bypass_requested()`. A token in prose, in a fenced line,
> in a later h1 or in an h2 leaves both checks running; an h1 below `<!-- contract:meta -->` still
> bypasses. This record's reproduction now exits 1 with `section missing`. `TestBypass` in
> `scripts/tests/test_validate.py` pins each placement, and `SKILL.md` §3 states the rule. The
> script reads each file as UTF-8, so a BOM is dropped on every platform (`TestEncoding`).

## Summary
`validate.py` treats `[BYPASS_VALIDATION]` as a plain substring (`if "[BYPASS_VALIDATION]" in content`). Any TASK.md that merely *mentions* the token — e.g. a requirement documenting the bypass, or an acceptance criterion about it — silently disables ALL RTM validation and exits 0.

## Reproduce
Add a line containing `[BYPASS_VALIDATION]` anywhere in TASK.md body (not the title), then run `validate.py --mode task TASK.md`. It prints "Validation bypassed" and exits 0 even with no RTM table. Hit live during TASK 090 (a requirement quoting the token self-bypassed).

## Expected
Bypass should be recognised only as an explicit marker in the TITLE/H1 (per SKILL.md §3 "add `[BYPASS_VALIDATION]` to the Title"), not anywhere in content.

## Fix sketch
Match the token on the H1/title line only, or require a dedicated `<!-- BYPASS_VALIDATION -->` HTML-comment marker.
