---
id: REG-5
type: known-issue
status: open
opened_at: 2026-08-04
category: register
severity: SEV-3
slug: reg-5-dequote-has-no-regression-pin-for-the-defect-its-own-docstring-says-it-exists-to-fix-a-table-inside-a
provenance: machine
component: '.agent/skills/artifact-formalizer/scripts/scan_register.py'
fingerprint: 01663dd3389c1650
finding_ref: fnd-20260804-152823-01663dd3
---

# REG-5 — `dequote()` has no regression pin for the defect its own docstring says it exists to fix (a table inside a `> …

> Filed by `run-feedback` from capture `fnd-20260804-152823-01663dd3`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

**Component:** `.agent/skills/artifact-formalizer/scripts/scan_register.py:529`

## Symptom

`dequote()` has no regression pin for the defect its own docstring says it exists to fix (a table inside a `> [!IMPORTANT]` callout being invisible to `table_lines`); the single blockquote case in the battery does not discriminate, so breaking `dequote` loses real findings with both gates green.

## Reproduction

Replace the body of `dequote` with `return list(lines)`. Verified: `selftest_scan.py` → `128/128 passed` exit 0, `--probe` → exit 0. Scanning the file `> [!IMPORTANT]\n> | Field | Meaning |\n> | --- | --- |\n> | xxx…(150 chars) | ok |` goes from `{'warn': 1}` with `('cell_width', '150 chars')` to `{'warn': 0}`. The only blockquote case, TC-ADV-15 at selftest_scan.py:772-776, uses `"> [!TIP]\n> " + "word " * 40 + "ends."`; with the `>` left in place the line is still 42 words and still exceeds the 35-word limit, so the case passes either way and proves nothing about dequoting.

## Evidence

scan_register.py:521-530 — docstring `"Stripping \`>\` only inside \`prose_blocks\` meant a table written inside a \`> [!IMPORTANT]\` callout was invisible to \`table_lines\`"` / `return [QUOTE_PREFIX.sub("", l) if QUOTE_PREFIX.match(l) else l for l in lines]`; selftest_scan.py:772-776 `doc = tmpfile("> [!TIP]\n> " + "word " * 40 + "ends.\n")` … `check("TC-ADV-15 blockquote prose reaches rule 1", …)`.

## Verification

Confirmed by an independent adversarial verifier that reproduced it against the committed tree:

Reproduced. scan_register.py:521-529 carries the quoted docstring (`Stripping \`>\` only inside \`prose_blocks\` meant a table written inside a \`> [!IMPORTANT]\` callout was invisible to \`table_lines\``) and the quoted return. Replacing the body with `return list(lines)`: `selftest_scan.py` → `128/128 passed` exit 0, `--probe` exit 0, and the fixture `> [!IMPORTANT]` + a quoted table with a 150-char cell went from `[('cell_width', '150 chars')]` to `[]`. TC-ADV-15 at selftest_scan.py:772-776 is exactly `tmpfile("> [!TIP]\n> " + "word " * 40 + "ends.\n")` asserting `sentence_length`, which passes with dequote neutered — it does not discriminate. Medium is right for a documented past defect with no regression pin.

## Provenance

Found by the 7-dimension review of commit `992b3ef` (dimension `selftest-honesty`), 2026-08-04. Survived adversarial verification; 7 sibling findings were refuted and are not filed.
