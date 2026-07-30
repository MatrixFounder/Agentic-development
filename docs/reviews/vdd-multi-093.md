# VDD Multi-Adversarial Report — TASK 093, iteration 3

**Date:** 2026-07-30
**Target:** `git diff 4b2a65e..HEAD` — the six work-items WI-2…WI-7 closed by TASK 093
**Critics:** `critic-logic`, `critic-security`, `critic-performance` (Layer-A parallel spawn)
**Overlap tag:** `corroborated` — all three critics ran on the same base model, so same-location
agreement is persona/prompt variation, **not** independent confirmation (R3a; no severity escalation).

## Summary

- **Findings:** 25 logic + 23 security (4 High, 6 Medium, 13 Low) + 8 performance = **56 raw**
- **Reproduced as working exploits before fixing: 5** — `H-01` arbitrary file write, `H-04`
  out-of-tree delete, `H-02` case-variant denylist bypass, `L-1` CRLF corruption, `L-2` insertion
  inside a code fence
- **Convergence:** logic `issues-found` · security `issues-found` · performance `issues-found`
- **Verdict:** the iteration is **not converged**; every confirmed finding is fixed and pinned, but
  three critics independently finding real defects means a fourth round is warranted, not optional.
- **Gates after fixes:** 286 unit tests (265 → 286, zero skips), E2E PASS, spec-validator 38 PASS,
  contract-sync 0, 45/45 skills, `doctor ready: true`.

## The finding that matters most

**TASK 093 did not apply its own organizing lesson to itself.** The task existed to close WI-7,
whose stated generalization is *"a fix that lands on one of two symmetric code paths is half a
fix."* Iteration 3 found **six more instances of exactly that**, in the code written to close it:

| # | The guard | Present on | Missing on |
|---|-----------|-----------|-----------|
| L-1 | CRLF fidelity | the existing-category branch | the **new-category** branch — the one a freshly seeded index always takes, so the *first defect ever filed* corrupted line endings |
| L-2 | fence awareness | `ledger_backlog` | `ledger_issues` — a pointer line landed **inside** a documented code example (F3, one registry over, a whole task later) |
| L-4 | `except BaseException` rollback | `file_work_item` | `file_defect` — whose docstring made the same no-half-state promise |
| L-5 | the WI-2 body cap + screen | the CLI | **neither writer** — so any library caller bypassed it, and my docstring argued the inverse |
| L-6 | id-uniqueness | `file_work_item` | `file_defect` — no id guard at all |
| H-04 | path containment | `resolve`'s verbatim branch | `resolve`'s **suffix-appending** branch — the one a ref without `.json` *necessarily* takes, so WI-6's own exploit still deleted a file outside the repo |

Vigilance was the wrong remedy and produced the same class a third time. The structural answer
now shipped: `feedback_lib/markdown.py` holds **one** fence scanner both ledgers consume,
`ids.assert_id_free` is **one** id guard both writers call, `atomic.read_verbatim` is **one** read
primitive, `body.guard_config_body` runs **inside both writers**, and every test covering a shared
guard is parameterized over both registries so "fixed on one path" cannot pass again.

## Security findings (4 High — all reproduced, all fixed)

**H-01 · arbitrary file write via unvalidated `finding_id` (CWE-22/73).** `finding.save` built its
target as `directory / (record["finding_id"] + ".json")`, and `pathlib` discards the left operand
when the right is absolute — the identical root cause `_contained` exists to fix. An inbox record
carrying `"finding_id": "/Users/…/.claude/settings"` wrote the attacker's whole JSON object to that
path; `write_atomic` creates missing parents and **replaces** an existing file. Reachable via
`file --as noise`, the one path needing no title, body or category. *Reproduced: wrote
`/tmp/h01/PWNED_BY_FINDING_ID.json`, exit 0.* WI-6 reasoned carefully about containing the file
this tool **deletes** and left the file it **writes** uncontained.
**Fixed** with two independent controls — an id-grammar validator at `load`/`save`, and a
containment assert on the computed path — each pinned by its own test (a single test could not
attribute which fired, which is the V-22 lesson).

**H-04 · out-of-tree delete through the unguarded `resolve` branch.** WI-6 added `_within` to the
branch that tests the ref verbatim. A ref *without* a `.json` suffix necessarily falls to the second
branch, which had no containment — so `--finding ../../../victim` read a foreign JSON and `consume`
**unlinked it**. *Reproduced: `/tmp/h01/victim.json` was deleted.* **Fixed** — both branches now go
through one `contained()` helper.

**H-02 · case-variant denylist bypass (CWE-178).** `_FORBIDDEN_ROOTS` was compared with exact
string equality, `Path.resolve()` does not canonicalize case, and macOS/APFS is case-insensitive —
so `".Claude/commands"` reached the real `.claude/commands/` and would write an attacker-influenced
record body as a **new slash command**. That is the V-11 exploit reachable by changing one letter's
case. *Reproduced: `issues_dir: ".Claude/commands"` was accepted.* **Fixed** — NFC-normalized,
casefolded comparison against **every** path component, not just the first.

**H-03 · denylist over an unbounded space.** Eight forbidden dirs and five basenames is not a
containment policy: `.cursorrules`, `.envrc` (where the generated index line's backticks are
command substitution to bash), `.github/copilot-instructions.md` and any `@`-imported doc were all
legal ledger targets, and `insert_index_line` needs no anchor so it appends to *any* text file.
**Fixed structurally** — no path component may start with `.`, and a ledger *file* key must be
`.md`. Both live consumer configs already satisfy both rules (verified), and the rules kill the
class rather than enumerating it.

**M-01 · the credential screen missed the exploit it was written for.** `body.py`'s motivating
example is `--body-file ./.env`, and the first version excluded every `key=value` rule to avoid
prose false positives — so `.env` content passed, as did PEM private keys (`~/.ssh/id_rsa` is ~2 KB,
nowhere near the ceiling), `github_pat_`, `glpat-`, `AIza`, JWTs, and inline-credential URLs.
**Fixed** — 10 more pattern families plus one **narrow** env-assignment rule (uppercase env-style
name, `=` not `:`, ≥20-char token charset) that still lets *"the bypass token: [PLACEHOLDER]"* and
*"password: see the vault entry"* through, both pinned as positive tests.

**M-02 · `_MASKED_RE` laundered a partially masked secret.** The exemption was a substring `search`
over the whole match, so `ghp_xxxxxxxx0123456789abcdefgh` — masking only the middle, which is what
the error message's own "remove **or mask**" invites — passed with a live tail. **Fixed** — the mask
must now *dominate* (≥50% of the span after discounting the fixed prefix). `sk-[REDACTED]` still
files; a partially masked real token does not.

**M-03 · injection into the provenance banner** — closed as a side effect of H-01: `finding_ref`
derives from `finding_id`, which is now validated at `load`, so the trust marker cannot be forged.

**M-04 / perf-High · unbounded work on a synchronous path (CWE-1333/400).** `clip` redacted **then**
sliced, so `excerpt_max_chars` bounded the output but not the cost — 100 MB scanned to produce
2 000 characters — and the email rule backtracked O(n²) on a long run with no `@`. **Fixed** —
slice-before-redact with a 4× margin, bounded repetition in the email rule, and `clip(text, 1)` no
longer returns the whole string (`text[-(limit-1):]` is `text[-0:]`).

**M-05 / M-06 · unescaped config values.** Only the link *text* was escaped, so a `)` in a config
path closed the markdown link and the remainder became an attacker-controlled link inside an
agent-read index; control characters forged lines in `doctor` output and `hint:` lines, which the
orchestrator reads as fact. **Fixed** — ledger config paths reject `()[]<>|` `` ` `` `'"` and any
non-printable character.

## Logic findings (25; the six asymmetries above plus)

**Fixed:** L-3 (the WI-7 regression test was **vacuous in both assertions** — `assertIs(x, x)` after
an always-False `hasattr`, and an `assertIn` that the *docstring* satisfied, so deleting the actual
call left it green; now behavioural and mutation-verified) · L-8 (a ≥4-space-indented anchor counted
as live, so `doctor` could report `ready: true` for an anchor that renders inside a code block) ·
L-9 (= M-02) · L-10/L-14 (`doctor` still aborted on a bad `feedback_dir`; a foreign inbox file
crashed `triage` with `KeyError`) · L-11 (a non-UTF-8 `--body-file` produced a raw traceback;
refused cleanly now, **not** `errors="replace"`, because mangling a verbatim body is worse) · L-13
(`assert_id_free` collapses the id before comparing, so the guard can recognize its own output) ·
L-15 (`_rejoin` collapsed a human's trailing blank lines on every insertion) · L-21 (only one
credential per line was reported, so an operator masked them one refusal at a time) · L-23 (a NUL in
a config path escaped as a bare `ValueError`) · L-25 (an unguarded `.group(1)`).

**Recorded, not fixed** — with reasons, in `docs/backlog/`: L-16 (a 0-byte index is not seeded),
L-17 (`doctor` does not exercise the R16 validations, so it can report `ready: true` while every
`file` exits 3), L-18/L-19 (two tests under-pin what they claim), L-20 (`_PLACEHOLDER_RE` is a
wildcard that could delete legitimate prose), L-22 (`_strip_comment` truncates a value that merely
*starts* with a quote), L-24 (new-category placement assumes existing headings are sorted), sec-L-01
(duplicate frontmatter keys let a human and a tool read different values), sec-L-06/L-07/L-08/L-09/
L-10/L-11 and the remaining fd-leak and TOCTOU residue.

## Performance findings (8)

**Fixed:** the hook did **O(entire tool output)** work — a full copy, a `splitlines()` of everything,
and a full-text regex — **above** the exit-0 discard filter, i.e. on every successful Bash call,
synchronously in the user's session. WI-4 removed a bounded ~5–30 ms `git` spawn from that path and
left an unbounded allocation cost three lines higher; the response is now tail-truncated to 64 KB
before anything touches it, and the `tool_name` discard moved **above the imports**. Also: `doctor`
parsed every inbox JSON to produce an integer — the exact O(k) WI-5 had just deleted, one command
over, in the same commit — now a `scandir` count; `_dup_candidates` rebuilt a loop-invariant token
set per pair (100 000 constructions instead of 500); and `existing_ids`/`list_issues` used
`parse_file`, which joins a full record body every caller discards, twice per filing inside the
filing flock — now `parse_meta_only`.

**Recorded, not fixed:** unconditional `fsync` twice per capture (one inside the collect lock) —
inbox state is regenerable and the durability guarantee worth paying for is on the ledgers;
`_read_maybe_stdin` loads the whole file *before* the ceiling that exists to refuse it; the double
corpus scan per filing is now cheap per record but still two passes; various micro-syscall counts
the critic itself judged not worth fixing.

**Confirmed as delivered:** WI-4's laziness (one `git` spawn per `Config`, verified by a counter) and
WI-5's glob (one file read instead of *k*) both do what they claimed, and both are pinned.

## Process findings — mine, not the code's

1. **I edited the tree while the critics were reading it.** `critic-security` opened
   `ledger_issues.py` twice and got two different files, one of them mid-mutation, and correctly
   refused to certify the exit bar on those grounds (its C-0a). Its C-0b — a reverted
   `read_verbatim` — was an artifact of that window, not a real regression (verified: line 311 is
   `atomic.read_verbatim`). The lesson is procedural and unambiguous: **freeze the tree for the
   duration of a review**, or the report describes a state that never existed.
2. **Mutation testing caught a weak test of my own** — asserting the anchor *count* is 1 passes
   whether the right or the wrong anchor resolved, because a naive-toggle regression also finds
   exactly one. The fence tests now assert **which line**.
3. **Two independent controls can mask each other in a test.** Neutralizing the H-01 id validator
   left the suite green because the containment assert caught it, and vice versa. Good defence in
   depth, useless attribution — each control now has its own test, exactly as the create-only guards
   did in iteration 2.
4. **The security scanner's remaining CRITICAL hits are the credential-screen fixtures.** A test for
   a secret detector necessarily contains secret-shaped strings. Verified by reading each site; no
   live credential is committed. Noted in the skill so the output stays interpretable.

## Exit bar

Not met. Per `vdd-adversarial`'s objective bar: the full test run **was** executed and is green
(286 + 38, E2E, contract-sync, 45/45), and there are zero **unfixed** CRITICAL findings — but all
three critics returned `issues-found`, several confirmed findings are deliberately recorded rather
than fixed, and the review ran against a tree that was moving. A fourth iteration should target the
recorded residue and, on the evidence of three rounds, **the remaining `ledger_issues` /
`ledger_backlog` divergence** — which has produced a confirmed finding in every single iteration so
far and is the strongest available argument for WI-7's option 3 (extract a shared `ledger_core`).
