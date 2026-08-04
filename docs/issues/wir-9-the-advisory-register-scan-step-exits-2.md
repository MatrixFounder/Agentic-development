---
id: WIR-9
type: known-issue
status: fixed
opened_at: 2026-08-04
category: wiring
severity: SEV-2
slug: wir-9-the-advisory-register-scan-step-exits-2
provenance: machine
component: '.github/workflows/framework-gates.yml'
fingerprint: 627cd22d61e6ed5e
finding_ref: fnd-20260804-152826-627cd22d
---

# WIR-9 — The "advisory" register-scan step exits 2

> Filed by `run-feedback` from capture `fnd-20260804-152826-627cd22d`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

**Component:** `.github/workflows/framework-gates.yml:56`

## Symptom

The "advisory" register-scan step exits 2 — and fails CI — whenever docs/TASK.md or docs/PLAN.md is absent, which is the framework's own documented state after `/start-feature` archives them. The step comment asserts this cannot happen.

## Reproduction

Run `/start-feature` (`.agent/workflows/01-start-feature.md:22` archives `docs/TASK.md` → `docs/tasks/` and `docs/PLAN.md` → `docs/plans/` in lockstep; PLAN.md is only recreated later by `/plan`). Commit and push that phase-boundary state. `scan_register.py` hits `FileNotFoundError` (an `OSError`) on the first missing path and returns 2 — the same code reserved for "broken instrument / dead detector". Verified live in this very checkout, where a concurrent archive had just moved both files: `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/TASK.md docs/PLAN.md docs/ARCHITECTURE.md --sections --terms docs/ARCHITECTURE.md` → `exit=2`, stderr `{"ok": false, "error": "docs/TASK.md: [Errno 2] No such file or directory"}`. CI goes red on an ordinary doc-pipeline commit, and the exit code tells the operator to go hunt a dead detector. The same class fires on a non-UTF-8 byte in any of the three files (UnicodeDecodeError is a ValueError, caught by the same handler) and on a missing `--terms` source (`scan_register.py:1154-1156`).

## Evidence

.github/workflows/framework-gates.yml:53-55 — "# Advisory sweep of the living artifacts. The scanner exits 0 on any / # number of findings, so this step fails ONLY on a broken instrument. / # Deliberately no `|| true`" contradicted by .agent/skills/artifact-formalizer/scripts/scan_register.py:1192-1194 — "except (OSError, ValueError) as exc: / _fail(args.json, {"ok": False, "error": f"{fp}: {exc}"}) / return 2"

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Independently reproduced in a clean worktree at 992b3ef. Ran the CI command verbatim with docs/PLAN.md moved aside: `{"ok": false, "error": "docs/PLAN.md: [Errno 2] No such file or directory: 'docs/PLAN.md'"}` / `exit=2`. The cited lines are exact: framework-gates.yml:53-55 says "The scanner exits 0 on any / number of findings, so this step fails ONLY on a broken instrument. / Deliberately no `|| true`", and scan_register.py:1192-1194 is `except (OSError, ValueError) as exc: _fail(...); return 2`. The step has no `continue-on-error` and no `|| true`. The absent-PLAN.md state is not hypothetical: skill-archive-task/SKILL.md:251 states `ASSERT NOT exists("docs/PLAN.md")` as the post-condition of Step 7, and /start-feature (01-start-feature.md:22) recreates only TASK.md, never PLAN.md — PLAN.md returns at /plan. I enumerated history: 10 of the last 30 first-parent commits on main have no docs/PLAN.md (f89cdc3, 8011cbd, cf13d8e, 31db854, f116252, a5afe1b, d2053e6, f768d2c, 4b2a65e, 4281c96), and 20 of the last 40 across all ancestry. So the gate would go red on roughly a third of ordinary commits, with exit 2 — the code the same file reserves for a dead detector. This is exactly the failure mode documentation-standards §4 names ("a gate that fails on correct documents is how gates get switched off"). Severity high stands.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `gate-honesty-and-regressions`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
