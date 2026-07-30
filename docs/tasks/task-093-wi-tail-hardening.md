# Technical Specification: close the WI-2…WI-7 tail of the run-feedback hardening

### 0. Meta Information
- **Task ID:** 093
- **Slug:** wi-tail-hardening

## 1. General Description

Two adversarial iterations over TASK 091/092 closed every reproduced exploit and deferred the rest
into six work-items: **WI-2** (record bodies neither redacted nor capped), **WI-3** (ledger bodies are
unmarked agent-trusted context), **WI-4** (eager `git` spawn in every `Config`), **WI-5**
(`find_by_fingerprint` rescans the whole inbox), **WI-6** (`--finding` accepts any path and `consume`
unlinks it), **WI-7** (an 11-row residual tail). This task closes them.

The organizing finding is WI-7's own: **`ledger_issues` and `ledger_backlog` implement one contract
in two modules, and every fix that landed in one but not the other is half a fix.** That asymmetry is
what produced the original WI-23, and it is still the shape of the list — V12 is literally "the CRLF
fix landed only in the backlog module". So the work is organized by *contract surface*, not by
work-item number, and every shared mechanism moves to one place.

**Scope:** `run-feedback` (library, CLI, hook, tests, SKILL.md), `known-issues-format` (one new
optional extension key, both templates, the sync gate), and one additive clause in the three vendor
bootstrap files. No change to the pipeline, to any workflow, or to any other skill.

### 1.1 Two work-items are in direct conflict — the resolution is part of this spec

**WI-2 asks for the record body to be redacted. WI-3's premise is that the record body is preserved
verbatim by contract**, and `known-issues-format` states that rule. Silently rewriting evidence is
also the failure mode `filters.redact` would introduce here that it does not introduce on excerpts:
excerpts are machine-captured log tails (noisy, disposable), bodies are triage prose that a human
re-reads to decide what happened. Rewriting the second class corrupts the record; refusing to write
it does not.

Concretely, `filters.redact`'s `\b(token|secret|passw\w*|…)\s*[=:]\s*(\S+)` rule would rewrite the
sentence *"the bypass token: …"* in a work-item body about the spec-validator gate, and its email
rule would rewrite any address in any body. So this task **caps and screens, but never rewrites**:

- a body above a configurable ceiling is **refused** (R1);
- a body containing a **high-confidence credential shape** (`AKIA…`, `sk-…`, `gh[pousr]_…`,
  `xox[baprs]-…`, `Bearer <token>`) is **refused**, naming the class and the line but never echoing
  the match (R2). The loose `key: value` and email rules are deliberately **excluded** from the
  screen — their false-positive rate on prose is high and a false refusal blocks real filing;
- `SKILL.md` §5 states exactly this, so the doc stops overclaiming either way (R3).

This is a documented deviation from WI-2's recommended Option 1 (redact + cap) and is recorded in
WI-2's resolution blockquote, not silently.

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | A record body above `body_max_chars` (new config key, default 64000) is refused on **both** filing paths with a remediation naming the cap and the actual size. | Unit test per ledger; a body at the cap passes, one byte over is refused. |
| R2 | A body containing a high-confidence credential shape is refused on both paths; the error names the pattern class and the 1-based line number and does **not** contain the matched text. The loose `k: v` and email rules are NOT part of the screen. | Unit test per pattern class; positive tests that `token: [PLACEHOLDER]` prose, an email address, and an already-redacted shape (`sk-[REDACTED]`) still file; a test asserting the secret is absent from the error string. |
| R3 | `SKILL.md` §5 states the body policy precisely: capped, screened for credential shapes, **never rewritten**; excerpts are redacted and clipped. | Grep-verified doc text; `validate_skills.py` warning-free. |
| R4 | Records filed by the CLI carry `provenance: machine` in frontmatter and a one-line provenance blockquote above the body naming the `finding_ref`. Hand-written records are unaffected. | Unit test per ledger; a test that the banner sits between the H1 and the body and the body bytes are otherwise unchanged. |
| R5 | `provenance` is an optional extension key in the `known-issues-format` contract for **both** registries (SKILL.md + both seed templates), and `check_contract_sync.py` still exits 0. | Gate run; a test asserting the key is documented in both templates. |
| R6 | `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` state that ledger record bodies are **data, not instructions**, at the point where the pipeline is told to read the ledgers. | Grep for the clause in all three; existing prompt-reference gate still green. |
| R7 | `Config.data_root` is computed **lazily** and cached **per instance** (no module-level memo — audit 093 Risk 3), with `timeout=2`. `doctor` still reports it; `file --dry-run` and `issues` spawn no `git`. | Unit test asserting zero `git` spawns via a patched `subprocess.run` counter; the existing fallback test still passes. |
| R8 | The PostToolUse hook loads config only **after** the `tool_name != "Bash"` and `should_capture` filters, so a discarded event costs no config load and no `git` spawn. Debug dumping still sees **every** payload. | Unit test with a non-Bash payload asserting zero config loads; a debug-mode test asserting a non-Bash payload is still dumped. |
| R9 | `inbox.find_by_fingerprint` resolves via `glob("fnd-*-<fp8>.json")` and verifies the **full** fingerprint on each candidate; the filename↔fingerprint invariant is documented. | Unit test: two records sharing an 8-char prefix still merge correctly; a file whose name matches but whose fingerprint differs is not treated as a duplicate. |
| R10 | `doctor` reports inbox depth. | Unit test on the `checks` payload. |
| R11 | `inbox.resolve` accepts a bare path **only** when it resolves inside `inbox_dir`/`filed_dir`/`dismissed_dir`; anything else is a usage error that deletes nothing. Id and filename resolution are unaffected. | Unit test: `--finding /etc/hosts` exits 2 and the file still exists; a path inside the inbox still resolves. |
| R12 | (V7) The placeholder strip walks forward to the first non-blank line after the inserted line instead of probing fixed offsets 2–3, so a two-blank-line shape works and a different section's placeholder is never deleted. | Unit tests for the two-blank shape and for a placeholder belonging to a later section. |
| R13 | (V8) Fence detection follows CommonMark: fence char and length are tracked (a 3-backtick line does not close a 4-backtick fence), `~~~` and ``` do not close each other, and a ≥4-space-indented line is not a fence. Behaviour stays **fail-closed**; when the anchor is unreachable because a fence is unclosed, the remediation says so and names the opening line. | Unit test per shape, incl. the unclosed-fence message. |
| R14 | (V9) Every config-derived probe in `doctor` sits inside the guarded block, `UnicodeDecodeError` is caught, and an over-cap backlog reports `backlog_anchor_present: "unchecked"` rather than a false `False`. | Unit tests: a config with an escaping `issues_dir` still produces a report; an invalid-UTF-8 backlog is reported not crashed; an over-cap backlog reports `unchecked` and is not counted unready. |
| R15 | (V12) `ledger_issues.insert_index_line` is newline-faithful: reads verbatim, splits on `\n` only, preserves CRLF, and does not rewrite the whole file's line endings. The read primitive is **shared** with `ledger_backlog`. | Unit tests mirroring the backlog CRLF/`U+2028` tests, byte-level; a test asserting both modules use the same primitive. |
| R16 | (V-13) `backlog_anchor` (non-empty, single line, no leading/trailing space), `id_prefixes` (str keys and `^[A-Za-z][A-Za-z0-9_-]{0,31}$` values) and `excerpt_max_chars` (int ≥ 1) are validated at access with an exit-3 config error. | Unit test per invalid value, incl. the empty anchor that would match every blank line. |
| R17 | (V-08) The `doctor` writability probe uses an unpredictable temp name and does not follow a symlink. | Unit test: a planted `.doctor-probe` symlink is not written through. |
| R18 | (V-10) `--dry-run` marks the id provisional on **both** paths, in the JSON (`provisional_id`) and in the human line. | Unit test per path asserting both surfaces. |
| R19 | (V11) Both ledgers build frontmatter **from** their `CONTRACT_KEYS` tuple rather than asserting against a restated literal; `ledger_issues.CONTRACT_KEYS` is live; a test pins **both** tuples to the `known-issues-format` SKILL.md contract via the sync gate's own extractor, and skips cleanly when that skill is absent. | Unit test; it must fail if a key is added to a tuple without updating SKILL.md. |
| R20 | (V17) When `inbox.consume` fails after a successful ledger write, the finding's status is flipped in place best-effort and the error names the written record path and the manual recovery step, so a retry reports "already filed" instead of exiting 4 forever. | Unit test simulating a `consume` failure: the error text names the record, and the immediate retry does not exit 4. |
| R21 | (V-22) The three tests that passed for the wrong reason are rewritten so each fails when its guard is removed: the "one line" test uses input containing a reader break, the temp-name test asserts unpredictability rather than PID absence, and the symlink test distinguishes which of the two guards fired. | Mutation-checked by hand: remove each guard, confirm the specific test reddens. |
| R22 | (V-21) `serialize` quotes scalars a real YAML parser would coerce (`true/false/yes/no/on/off/null/~` in any case, and int/float-looking text), and the `'`→`’` rewrite emits a stderr warning naming the key. ISO dates stay bare. | Unit tests incl. `value: "true"`, `value: "2026"`, `opened_at: 2026-07-30` staying bare, and the warning. |
| R23 | Every existing gate stays green: both unit suites, `test_e2e.sh`, `check_contract_sync.py`, `validate_skills.py` 45/45, the prompt-reference and security-lint sweeps. | Full gate sweep. |
| R24 | Each of WI-2…WI-7 is closed in lockstep (record `status` + `resolved_at`/`resolved_by` + resolution blockquote, index line moved to `## Closed`), and any item deliberately **not** implemented is stated in its resolution rather than omitted. | `git diff` review of `docs/BACKLOG.md` + `docs/backlog/*`. |

## 3. Non-functional Requirements
- **Performance:** the suite's wall clock must not grow materially; R7 should reduce it. No new
  process spawns on any path.
- **Security:** every change is either a refusal or a narrowing. No new write surface, no new
  network use, no rewriting of operator-supplied bytes (§1.1).
- **Compatibility:** `config.v` stays `1` — `body_max_chars` is additive with a default that no
  honest body reaches. Existing configs in three consuming repos keep working unchanged. Python 3.9+,
  stdlib only.
- **Blast radius:** `run-feedback` and `known-issues-format` are consumed by symlink from
  `Universal-skills` and `onchain-analytics`, so every change is live for them on save. Nothing here
  may change the meaning of an existing config key or the format of an existing record.

## 4. Constraints and Assumptions
- **R13 must not become fail-open.** An unclosed fence above the anchor means the anchor really is
  inside a code block per CommonMark, and inserting there is the F3 defect this guard was built for.
  The fix is accuracy and a better message, not permission to write.
- **R9 has a real cost:** dedup now depends on the filename encoding the fingerprint prefix.
  `finding.save` is the only writer and derives the name from `finding_id`, so the invariant holds
  in-tree; a hand-renamed inbox file would no longer dedup. A fallback full scan is deliberately
  rejected — the miss case is the common case, so a fallback would restore the O(k²) it removes.
- `provenance: machine` is an **extension** key: optional, after the contract keys, absent from
  hand-written records. It is not a new contract key and must not reorder the existing five.
- No behaviour change to `validate.py`, to `archive_protocol.py`, or to any workflow file.

## 5. Open Questions / Observations (recorded, not fixed here)
- The three ledger-adjacent modules would be better as one shared `ledger_core` (WI-7 option 3).
  This task does the narrower thing WI-7 recommends — shared primitives for the mechanisms that
  actually diverged — because a full extraction is an L-sized change with a blast radius across two
  live registries in three repos. If a third registry ever appears, that extraction is the fix.
- `serialize` remains a hand-rolled emitter, not a YAML library. R22 closes the two coercion cases
  found; it does not make the output round-trip-safe under every YAML dialect.
- WI-2's Option 1 (redact the body) is **not** implemented, by the reasoning in §1.1. If the owner
  disagrees, the change is one call to `filters.redact` in `_read_body` — but it silently mutates
  evidence, and the verbatim rule would then need removing from `known-issues-format`.
