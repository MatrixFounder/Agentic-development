# Task 129-03: The renderer lockfiles

## Use Case Connection

- UC-2: The operator installs the renderers

<!-- contract:goal -->

## Task Goal

Write the three renderer lockfiles again with the overrides of TASK R3, so that `npm audit`
reports no critical and no high advisory and each render keeps its base status and metrics.

<!-- contract:changes -->

## Changes Description

`M/` stands for `.agent/skills/mermaid-authoring-guidelines/`, and `R/` for
`M/assets/renderers/`. `<scratch>` and `<logs>` are the directories that PLAN 129, Base evidence,
names.

### Changes in Existing Files

#### Files: `R/v10/package.json`, `R/v11/package.json`, `R/v12/package.json`

- `overrides` gains `"dompurify": "3.4.17"` and `"katex": "0.18.10"`; its keys are sorted (R3.1).
- v10: the override `puppeteer` becomes `25.16.0`. v11 and v12: the dependency `puppeteer`
  becomes `25.16.0` (R3.2).
- v10: `description` names puppeteer 25.16.0 in place of 25.12.0, and the overrides of
  `dompurify` and `katex` (R6.3).

#### Files: `R/v10/package-lock.json`, `R/v11/package-lock.json`, `R/v12/package-lock.json`

- In each renderer directory,
  `npm_config_cache=<scratch>/npm-cache npm install --package-lock-only --ignore-scripts --no-audit --no-fund`
  writes the lockfile (R3.3).

#### File: `M/scripts/setup_renderers.sh`

- The header paragraph that starts at this line names puppeteer 25.16.0 in place of 25.12.0:
  `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:43@2a7d11c` `# The v10 lockfile overrides the puppeteer 19.11.1 of mermaid-cli 10.9.1 with 25.12.0, the`
- The paragraph also names the overrides of `dompurify` 3.4.17 and `katex` 0.18.10, and the
  result of `npm audit` of this task with its date (R6.3).
- The paragraph names each copy of DOMPurify and KaTeX that the render page runs, by tag and
  package, with its version (R6.5, TASK D9).
- The claim at this line stays when R7.2 confirms it:
  `.agent/skills/mermaid-authoring-guidelines/scripts/setup_renderers.sh:13@2a7d11c` `The only install script in the three lockfiles is puppeteer's`
- No line of code changes.

### Procedure

1. Edit the three manifests.
2. Write the three lockfiles, each from the lockfile of the base revision, with the final manifest:
   `git show 2a7d11c:<path>` over the lockfile, then the command above. The review brief lists the
   difference against the base.

   **Why.** Written from an intermediate lockfile, npm nested `katex` under its dependents
   (measured, 2026-10-27). Written from the base, each lockfile holds one `katex` at the top.
3. In each renderer directory,
   `npm_config_cache=<scratch>/npm-cache npm audit --package-lock-only --json` writes its output
   to a file under `<logs>` → no critical and no high advisory (A3).
4. TC-L1 and the v10 test of Task 129.1 → pass (A4).
5. `MERMAID_RENDER_HOME=<scratch>/render-new bash M/scripts/setup_renderers.sh --forward` → exit 0
   (R3.4). The log names the cached chrome-headless-shell 150.0.7871.24, accepted by its recorded
   tree hash, and a passed smoke render for each install.
6. From `M/`, `MERMAID_RENDER_HOME=<scratch>/render-new python3 -B scripts/render_check.py --forward --json`
   runs over the nine files of the base evidence, then over the KaTeX probe figure. Each output
   goes to a file under `<logs>`.
7. `<scratch>/tools-128/compare_renders.py --base <the two base files> --new <the two new files>`,
   without `--ignore`, compares the renders (R3.5, D8).
8. A difference → PLAN 129, Failure paths.
9. Edit the setup header and the v10 description.
10. Spawn the code reviewer and the security auditor in one message (R7).

<!-- contract:tests -->

## Test Cases

### End-to-end Tests

1. **TC-E5** — `setup_renderers.sh --forward` in a temporary home → exit 0, and a passed smoke
   render for each of the three installs (A5).
2. **TC-E6** — `compare_renders.py` without `--ignore`, over the 52 figures → no difference (A5).

### Unit Tests

1. **TC-L1** and the v10 test of Task 129.1 → pass (A4).
2. **TC-C1** — `compare_renders.py` on the base evidence against itself → no difference.
3. **TC-C2** — `compare_renders.py` against a copy with one metric changed by 1 px → one
   difference that names the figure, the render and the metric.

### Regression Tests

- The tests of the skill under `M/scripts/tests/` → pass (A9).
- Every `run:` step of `.github/workflows/framework-gates.yml`, run locally → each passes.

<!-- contract:acceptance -->

## Acceptance Criteria

- [ ] A3, A4 and A5 hold, or A4 holds in the form of the katex branch of R3.7.
- [ ] A9: the tests of the skill pass.
- [ ] A10: the security review finds no finding of MEDIUM or above.
- [ ] The code review approves.

## Notes

- **The security review (R7).** The brief carries, as files:
  - the diff of the three manifests and the three lockfiles;
  - the output of `npm audit` for each lockfile;
  - each added or removed package, each `hasInstallScript`, each `resolved` host and each
    `integrity` algorithm.

  The auditor checks the claim at line 13 of the setup script again (R7.2).
- **The base installs** under `<scratch>/render-base` stay until the comparison ends. Once the
  lockfiles change, `render_check.py` of the work tree refuses them: their lockfile stamps are
  stale. The `render_check.py` of a worktree at `2a7d11c` still accepts them, so the fallback of
  PLAN 129 can render the base with them.
- **The browser.** puppeteer 25.16.0 pins chrome-headless-shell 156.0.8078.47. That build is not in
  the puppeteer cache, so the setup offers the cached 150.0.7871.24. `browsers.json` and
  `BROWSER_MIN_BUILD` stay unchanged (R3.4).
- **`compare_renders.py`** pairs each figure of the base with its new render by the normalised
  source path and the figure index (code review of Task 129.3, MINOR 7). It reports:
  - each figure or render present in one set only;
  - each field of a figure or of a render whose value differs, the paths `svg`, `png` and
    `measure` aside;
  - each metric whose value differs.

  Exit 0 no difference; 1 a difference; 2 usage.
- **The KaTeX probe figure**, the text of `<scratch>/probe-katex/katex-probe.md` below its title:

```text
flowchart LR
  A["$$x^2 + y^2 = z^2$$"] --> B["$$\sqrt{a + b}$$"]
  B --> C["plain label"]
```
