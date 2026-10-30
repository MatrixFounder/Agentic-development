# Scripts and the renderer setup

The full contract of the scripts that `SKILL.md` §4 names, and the rules of the renderer setup
that `SKILL.md` §5 summarizes. `SKILL.md` keeps the commands and the rules an agent acts on;
this file holds the flags, the exit codes and the details (TASK 137).

## 1. Commands

Run from the project root as `python3 .agent/skills/mermaid-authoring-guidelines/scripts/<script>`;
`scripts/` below stands for that directory:

- `python3 scripts/lint_mermaid.py <file.md|file.mmd> [--json] [--inventory] [--probe]` — exit 0
  no error, 1 error found, 2 internal failure or dead rule, 3 usage.
- `python3 scripts/render_check.py <file> [--no-dark] [--forward] [--versions v11,v10] [--json]
  [--out DIR] [--fixture FILE]` — exit 0 pass; 1 a figure fails or does not parse; 2 not
  rendered: renderers or browser absent, a required render left out by `--no-dark` or
  `--versions`, or no mermaid fence; 3 usage. It renders 11.17.2, 10.9.8 and a dark 11.17.2 by
  default. A figure of a kind it does not model passes as `pass, geometry not checked`.
- `bash scripts/setup_renderers.sh [--forward] [--dry-run]` — installs the pinned renderers once.
- `python3 scripts/plan_gantt.py <plan.json|PLAN.md> [--write DOC | --check DOC] [--stages A,B]
  [--strict]` — exit 0 ok, 1 stale block or invalid plan, 2 internal failure, 3 usage.

## 2. Inputs, outputs and side effects

- **Inputs**: Markdown or `.mmd` files; for plans, a JSON schedule or the JSON block under
  `<!-- contract:schedule -->` in a `PLAN.md`.
- **Outputs**: findings (text or JSON). Renders go outside the repository: to `--out`, or under
  the cache, where the check keeps the newest 20 `check-*` directories.
- **Thresholds and settings**: `assets/notation.json` only.
- **Idempotency**: the lint and `--check` write nothing. `--write` rewrites the marked block,
  `--fixture` its file, and the setup script its cache.
- **Dry-run support**: `setup_renderers.sh --dry-run`.

## 3. The renderer setup

- **Network**: `setup_renderers.sh` downloads pinned npm packages once, and the current stable
  chrome-headless-shell of Chrome for Testing from
  `https://storage.googleapis.com/chrome-for-testing-public`, into
  `${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}`, never globally and never into a
  repository. Run it only when the operator allows these downloads. A render fetches nothing: no
  host resolves, no proxy, a pipe to puppeteer.
- **Browser**: the sandbox stays on. Only the operator sets `MERMAID_RENDER_NO_SANDBOX=1` or
  `MERMAID_RENDER_BROWSER_SHA256`; an agent reports a refused browser and stops.
- **Browser build**: no build number is kept. Each run of the setup installs the stable build of
  its day into `<home>/chrome`, with the `@puppeteer/browsers` that the lockfiles pin, and removes
  the older builds there; the security fixes of the browser arrive that way. `render_check.py`
  names a browser installed more than 30 days before the render, and refuses an install whose
  stamp holds no date of the install. Without the network the operator may name a browser at hand
  with `MERMAID_RENDER_CHROME` and its tree hash with `MERMAID_RENDER_BROWSER_SHA256`.
- **Windows**: `setup_renderers.sh` runs under Git Bash, with paths in the form `/c/…`. No owner
  or mode is checked there: Windows reports none that shows who may write. The install home, the
  browser in it, and `--out` must lie in `%USERPROFILE%`, whose ACL keeps other users out, and the
  default home lies in it. The browser is checked by its tree hash and its stat
  digest, which leave out the top-level file `debug.log` of one link that Chrome writes beside
  its executable there. That file grows with each render and may hold text of a figure. Limits:
  - not seen there: a browser file overwritten in place with its size and mtime restored;
  - on a ReFS volume (Dev Drive), or with a reparse point that is no link, such as a OneDrive
    placeholder, the stat digest never matches, and every render is refused;
  - a volume mounted into the profile, or a folder of it with an ACL of its own, is not private.

  The header of `setup_renderers.sh` states the same rules.
- **Optional artifacts**: absent renderers do not block authoring; they make the hand-off say
  `not rendered`.
