# Security Review: TASK 129 R7 — the renderer lockfiles

- **Auditor:** `security-auditor` (subagent), with `security-audit` and its §6.1 disclosure rule.
- **Scope:** the diff of the three renderer lockfiles and manifests, the claim at
  `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:13@2a7d11c`, and the
  statements written about the bundled copies (TASK D9).
- **Kept by:** the orchestrator, from the auditor's hand-back. WI-30 and RF-21 are named by ID only.

## Round 1 — 2026-10-26, at tree fingerprint `0a8d25c3fc5a`

**Verdict: PASS for A10. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW, 3 INFO.** The auditor recomputed the
fingerprint at its start and at its end. It wrote nothing in the repository.

**Scan.** `run_audit.py . --scan-type all`: exit 0, `scan_complete: true`, `not_run: []`. The
critical and high hits of the regular expressions lie in fixtures, seeded corpora and tests that
this task does not change. On copies of the 11 files of the change: no critical or high hit,
`npm audit` 0, gitleaks nothing.

**R7.1.**

- Added packages: none. Removed: `node_modules/katex/node_modules/commander` 8.3.0 in v12.
- Version changes: 11 per lockfile, 10 in v12, as the summary of the brief lists them.
- `hasInstallScript`: on `node_modules/puppeteer` only.
- Every `resolved` is on `https://registry.npmjs.org`; every entry has a sha512 `integrity`, and
  each changed hash matches the `dist.integrity` of the registry.
- `npm audit signatures` after a fresh `npm ci --ignore-scripts`: 134, 190 and 193 packages
  verified, none invalid or missing.
- No new `bin`, `os`, `cpu` or `libc`; no license change.

**R7.2.** The claim at line 13 holds: of 134, 190 and 193 installed manifests, only puppeteer runs
a script at install time, `postinstall: node install.mjs`, and no package has a `binding.gyp`.

### LOW

| ID | Finding | Answer |
| :--- | :--- | :--- |
| L-1 | DOMPurify 3.3.1 in `@mermaid-js/mermaid-zenuml` 0.2.3 and 1.0.1 runs on the page of v11 and v12 with a `zenuml` figure; D9 and the records did not name it | TASK D9 names every copy; the operator confirmed it (2026-10-27) |
| L-2 | "The advisories of §1 cover each of them" is wrong for the critical advisory and 3.4.2 | TASK §8 names the advisories of each copy |
| L-3 | The override pins `katex` 0.18.11, which its publisher deprecates | `katex` 0.18.10 (TASK D4) |

### INFO

- **I-1.** `chromium-bidi` 157.0.8090-0 is published without provenance; its registry signature is
  valid, and puppeteer-core 25.16.0, which has provenance, pins it. It loads only with
  `protocol: 'webDriverBiDi'`, which `puppeteer.json` never sets.
- **I-2.** `zod` 4.6.7 serves only `chromium-bidi` 157; `commander` 15.0.0 serves only the command
  line of `katex`. `npm audit` is clean for both.
- **I-3.** The accepted browser is still build 150.0.7871.24; puppeteer 25.16.0 pins 156. This
  task does not change it.

**D9 on its own merits: LOW.** mermaid calls the sanitizer with default options or with
`FORBID_TAGS`, and its directive handling strips the options that a figure sets. The page resolves
no host, uses no proxy, talks over a pipe and keeps its sandbox. The figures come from the operator
and from agents.

**Controls.** The change weakens none: `npm ci --ignore-scripts`, the cache location, the browser
hash and stamp, the browser arguments and `puppeteer.json` are unchanged.

## Round 2 — 2026-10-27, at tree fingerprint `dbdcf6571d95`

**Verdict: PASS for A10. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 1 LOW, 3 INFO.** A second auditor reviewed the
delta: the operator moved `katex` to 0.18.10 (TASK D4), and each lockfile was written again.

- **R7.1 on the delta.** Each final lockfile differs from round 1 only in `node_modules/katex`:
  version, `resolved`, `integrity`, and no `deprecated` field. For 0.18.10: `resolved` on
  registry.npmjs.org; `integrity` equal to the registry's `dist.integrity` and to the sha512 of the
  tarball; the same publisher, maintainers, `bin`, license and `commander ^15.0.0` as 0.18.11; its
  only lifecycle script is `prepare`, which a registry install does not run. `npm audit signatures`
  verified 134, 190 and 193 packages, none invalid or missing.
- **R7.2** holds: puppeteer 25.16.0 is the only package with an install hook.
- **The copies.** The tables of the setup header and of TASK D9 are accurate and complete: the
  auditor followed the module imports from each page entry. No page file imports the packages
  `dompurify` or `katex`.
- **Round 1.** L-1, L-2 and L-3 are answered.

| ID | Severity | Finding | Answer |
| :--- | :--- | :--- | :--- |
| L-1 | LOW | `docs/ARCHITECTURE.md` §10.7 still named `katex` 0.18.11 and no copy | Task 129.4 |
| I-1 | INFO | D9 said "default options"; `sanitizeText` passes `FORBID_TAGS`, and a figure cannot set `dompurifyConfig` | TASK revision 6 |
| I-2 | INFO | `@mermaid-js/layout-tidy-tree` loads on every render and holds no copy | none needed |
| I-3 | INFO | semgrep `ifs-tampering` at the `local IFS=.` of `version_ge`, before the task; the IFS is local to the function | a false positive |
