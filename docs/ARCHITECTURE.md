# Architecture: Agentic Development System

## Table of Contents
- [1. Core Concept](#1-core-concept)
- [2. Directory Structure](#2-directory-structure)
- [3. Workflow Logic (v3.1)](#3-workflow-logic-v31)
- [4. Tool Execution Subsystem [NEW]](#4-tool-execution-subsystem-new)
- [5. Parallel Execution Model (POC) [SUPERSEDED]](#5-parallel-execution-model-poc-superseded)
- [5.1 Two-Layer Teams Model (Wave 1)](#51-two-layer-teams-model-wave-1)
- [6. Key Principles](#6-key-principles)
- [7. Localization Strategy](#7-localization-strategy)
- [8. Skill Architecture & Optimization Standards](#8-skill-architecture--optimization-standards)
- [9. Framework Installer Subsystem](#9-framework-installer-subsystem)

## 1. Core Concept
The system is built on a "Multi-Agent" architecture where different "Agents" (Personas defined by System Prompts) collaborate to solve tasks.
The Source of Truth for these agents is located in `System/Agents`.

## 2. Directory Structure
```text
project-root/
├── install.sh                     # [NEW v3.15] Framework installer (bash wrapper)
├── GEMINI.md                    # Orchestrator + core-principles
├── .cursor/rules/                 # Cursor Rules
├── AGENTS.md                      # References to rules + reading .AGENTS.md
├── .agent/
│   ├── skills/                  # Skills Library (Source of Capabilities)
│   │   ├── ...
│   │   └── skill-product-*      # [NEW] Product Skills (Strategy, Vision, Handoff)
│   └── tools/                   # Executable Tools Schemas (schemas.py)
├── .cursor/skills/                # [Symlink] Mirrors .agent/skills for Cursor
├── System/
│   ├── Agents/                  # Lightweight System Prompts (Personas)
│   │   ├── 00_agent_development.md
│   │   ├── 01_orchestrator.md
│   │   ├── ...
│   │   ├── p00_product_orchestrator.md #[NEW] Product Phase Agents
│   │   └── p04_solution_architect.md
│   ├── Docs/                    # Framework Documentation & Guides
│   │   ├── SKILLS.md            # Skills Catalog
│   │   ├── ORCHESTRATOR.md      # Tools Guide
│   │   ├── PRODUCT_DEVELOPMENT.md #[NEW] Product Playbook
│   │   └── ...
│   └── scripts/                 # [NEW] Framework Utilities (Tool Dispatcher)
│       ├── tool_runner.py
│       ├── install.py           # [NEW v3.15] Installer entry-point
│       ├── vendors.yaml         # [NEW v3.15] Vendor profiles config
│       └── installer/           # [NEW v3.15] Installer module (see §9)
├── Translations/                # Localizations (RU)
├── src/                         # Project Code
│   ├── services/
│   │   └── .AGENTS.md           # Local Context Artifact (Per-directory)
│   └── ...
├── docs/                        # Project Artifacts
│   ├── product/                 # [NEW] Product Artifacts (Strategy, Vision, BRD)
│   ├── TASK.md                  # Current Technical Task
│   ├── ARCHITECTURE.md          # System Architecture (This file)
│   └── ...
├── tests/                       # Tests & Test Reports
│   ├── tests-{ID}/              # Test Reports per Task (e.g. tests-016/)
│   └── ...
└── archives/
```

## 3. Workflow Logic (v3.1)
1. **Orchestrator** receives the user task and manages the **Tool Execution Loop**.
    - If the Model supports **Native Tool Calling**, the Orchestrator executes tools directly (structured) and feeds results back.
    - If not, it falls back to text-based parsing.
2. **Agent** (any role) starts by reading relevant local `.AGENTS.md` files...
3. **Agent** activates **Skills** (dynamically loaded from `.agent/skills`).
   - *Example:* Analyst loads `skill-requirements-analysis`.
4. **Analyst** (Agent 02) creates/updates a Technical Specification (TASK) in `docs/TASK.md`.
    - *Verification:* **Task Reviewer** (Agent 03) validates the TASK.
5. **Architect** (Agent 04) validates/updates Architecture in `docs/ARCHITECTURE.md`.
    - *Verification:* **Architecture Reviewer** (Agent 05) checks the design.
6. **Planner** (Agent 06) creates a Task Plan in `docs/PLAN.md` and detailed tasks.
    - *Verification:* **Plan Reviewer** (Agent 07) validates the plan.
7. **Developer** (Agent 08) executes the plan using Stub-First methodology.
    - **Crucial Step**: Updates code AND local `.AGENTS.md` (Documentation First).
    - *Verification:* **Code Reviewer** (Agent 09) checks the code.
8. **Security Auditor** (Agent 10) performs vulnerability analysis.

## 4. Tool Execution Subsystem [NEW]
The orchestration layer now supports **Structured Tool Calling**:
- **Definition**: Tools are defined in `.agent/tools/schemas.py` as `TOOLS_SCHEMAS`.
- **Execution**: The Orchestrator loads these schemas and passes them to the LLM.
- **Dispatch**: When the LLM requests a tool call, the Orchestrator intercepts it, executes the corresponding Python function (via `System/scripts/tool_runner.py`), and returns the result as a `tool` role message.
- **Security Check**: All tool arguments are validated; file operations are restricted to the project root (Anti-Path-Traversal).

### Available Tools
| Tool | Description |
|------|-------------|
| `run_tests` | Run pytest with custom commands |
| `read_file` | Read file contents |
| `write_file` | Create/overwrite files |
| `list_directory` | List directory contents |
| `git_status`, `git_add`, `git_commit` | Git operations |
| `generate_task_archive_filename` | Generate unique sequential ID for task archival |


## 5. Parallel Execution Model (POC) [SUPERSEDED]

> **SUPERSEDED by §5.1 — Wave 1 (2026-04-17).** The mock-agent POC below is retained only for historical context. Native Claude Code `Agent` tool + `.claude/agents/` subagents replaced `spawn_agent_mock.py`. See [docs/archives/POC_PARALLEL_AGENTS.md](archives/POC_PARALLEL_AGENTS.md) for the original POC doc.

The system formerly supported a **Parallel Orchestration Protocol** via mock agents:
- **Orchestrator Role**: Decomposes tasks and spawns sub-agents.
- **Shared State**: Uses `fcntl` file locking on `.agent/sessions/latest.yaml` to ensure safe concurrent updates. *(This locking mechanism is retained and still in use under §5.1.)*
- **Agent Runner** *(DEPRECATED)*: `spawn_agent_mock.py` script simulated sub-agent behavior.
- **Protocol** *(DEPRECATED)*:
  1. Orchestrator splits `TASK.md` -> `subtask-A.md`, `subtask-B.md`.
  2. Orchestrator calls `spawn_agent_mock.py` for each subtask.
  3. Sub-agents run in background processes, updating shared state.
  4. Orchestrator merges results.

## 5.1 Two-Layer Teams Model (Wave 1)

Wave 1 replaces the mock POC with a concrete two-layer teams model based on Claude Code native capabilities. Role-switching (Stage Cycle, §3) remains the **primary** orchestration mode; teams are a **parallel path** for specific scenarios.

### Layers

```text
 ┌─────────────────────────────────────────────────────────────────┐
 │   Orchestrator (main session — role-switching primary)          │
 └───────────────┬─────────────────────────────┬───────────────────┘
                 │                             │
     ┌───────────▼─────────────┐   ┌──────────▼────────────────┐
     │  Layer A: Agent tool     │   │  Layer B: Native Teams   │
     │  (parallel subagents)    │   │  (TeamCreate/SendMessage)│
     │  ✅ Wave 1 — implemented │   │  ⏸ Wave 4 — stub only    │
     └───────────┬──────────────┘   └──────────────────────────┘
                 │
   ┌─────────────┼─────────────┐
   ▼             ▼             ▼
┌──────┐    ┌──────────┐   ┌──────────────┐
│logic │    │ security │   │ performance  │  ← .claude/agents/critic-*.md
└──────┘    └──────────┘   └──────────────┘
```

### Layer A — Framework-Agent (Wave 1 + Wave 2, implemented)

- **Mechanism**: built-in `Agent` tool. Orchestrator issues N parallel tool-uses in **one message**.
- **Subagent definitions**: `.claude/agents/<name>.md` — thin Claude-frontmatter wrappers that point (body) at source-of-truth in `.agent/skills/*/SKILL.md` or `System/Agents/*.md`.
- **Use cases**: orthogonal parallel critique (`/vdd-multi`), parallel exploration/research, independent atomic units with clear artifact contracts, dev-pipeline role invocation.
- **Communication**: no inter-teammate messaging. Merge happens in the orchestrator after all teammates return.

**Wave 1 — critics** (read-only, return text reports):
- `critic-logic`, `critic-security`, `critic-performance` — parallel critics used by `/vdd-multi`.

**Wave 2 — dev pipeline** (12 total wrappers with Wave 1):

| Wrapper | SOT | Tools | Model | Role |
|---|---|---|---|---|
| `analyst` | `System/Agents/02_analyst_prompt.md` | Read, Write, Edit, Grep, Glob | sonnet | Produces `docs/TASK.md` with RTM |
| `task-reviewer` | `System/Agents/03_task_reviewer_prompt.md` | Read, Grep, Glob | **opus** | Returns review report; gates Analysis→Architecture |
| `architect` | `System/Agents/04_architect_prompt.md` | Read, Write, Edit, Grep, Glob | sonnet | Produces `docs/ARCHITECTURE.md` |
| `architecture-reviewer` | `System/Agents/05_architecture_reviewer_prompt.md` | Read, Grep, Glob | **opus** | Returns review report; gates Architecture→Planning |
| `planner` | `System/Agents/06_planner_prompt.md` | Read, Write, Edit, Grep, Glob, Bash | **opus** | Produces `docs/PLAN.md` + `docs/tasks/*.md` (uses `task_id_tool.py`) |
| `plan-reviewer` | `System/Agents/07_plan_reviewer_prompt.md` | Read, Grep, Glob | **opus** | Returns review report; gates Planning→Execution |
| `developer` | `System/Agents/08_developer_prompt.md` | Read, Write, Edit, Grep, Glob, Bash | sonnet | Implements atomic task under Stub-First |
| `code-reviewer` | `System/Agents/09_code_reviewer_prompt.md` | Read, Grep, Glob, Bash | **opus** | Returns review report; gates Execution→Merge (uses `git diff` to scope) |
| `security-auditor` | `System/Agents/10_security_auditor.md` | Read, Grep, Glob, Bash | **opus** | Returns full OWASP audit report (uses `run_audit.py`) |

**Wave 3 — product pipeline** (4 wrappers; 16 total after Wave 3):

| Wrapper | SOT | Tools | Model | Role |
|---|---|---|---|---|
| `strategic-analyst` | `System/Agents/p01_strategic_analyst_prompt.md` | Read, Write, Edit, Grep, Glob | sonnet | Produces `docs/product/MARKET_STRATEGY.md` (TAM/SAM/SOM, competition, pre-mortem) |
| `product-analyst` | `System/Agents/p02_product_analyst_prompt.md` | Read, Write, Edit, Grep, Glob | sonnet | Produces `docs/product/PRODUCT_VISION.md` (INVEST stories, SMART KPIs, viability score) |
| `product-director` | `System/Agents/p03_product_director_prompt.md` | Read, Write, Edit, Grep, Glob, Bash | **opus** | Adversarial-VDD gatekeeper; produces `docs/product/APPROVED_BACKLOG.md` (WSJF + APPROVAL_HASH) or `REVIEW_COMMENTS.md` |
| `solution-architect` | `System/Agents/p04_solution_architect_prompt.md` | Read, Write, Edit, Grep, Glob | sonnet | Produces `docs/product/SOLUTION_BLUEPRINT.md` (requires valid APPROVAL_HASH from product-director) |

Tools note: simple tool names only; Bash sub-command restrictions live in project-level [.claude/settings.json](../.claude/settings.json) `permissions.allow` allow-list (governs auto-approve vs prompt), not in subagent frontmatter. Reviewers/critics without `Bash` in tools cannot invoke any shell command — no pattern needed.

**Model policy** (v3.11.2 + Wave 3):
- **Verifiers and rigor-heavy roles → Opus** (10 wrappers): all 4 dev-pipeline reviewers (`task-reviewer`, `architecture-reviewer`, `plan-reviewer`, `code-reviewer`), 3 adversarial critics (`critic-logic`, `critic-security`, `critic-performance`), `security-auditor`, `planner` (plan decomposition has verifier-like rigor), and `product-director` (Adversarial-VDD gatekeeper of the Product→Technical handoff). Verification is a quality gate — false negatives (missed bugs, vulnerabilities, approved broken architecture, poorly decomposed plans, weak product-market fit judgment) are orders of magnitude more expensive than the extra token cost.
- **Builders → Sonnet** (6 wrappers): `analyst`, `architect`, `developer`, `strategic-analyst`, `product-analyst`, `solution-architect`. Creation tasks are template-driven (follow SOT structure); Sonnet produces equivalent artifact quality at ~5× lower cost and lower latency.
- **Cost impact**: at `/vdd-multi` smoke, three Opus critics vs three Sonnet critics is ~3–5× token cost per run, but a single missed security or logic bug in production easily exceeds that by orders of magnitude.

**Wrapper design convention** (Option D — thin adapters):
- Frontmatter = Claude Code subagent spec (`name`, `description`, `tools`, `model`).
- Body ≤ ~15 lines: SOT link + subagent-specific adaptations only (what differs from SOT when running as subagent vs main-agent role — primarily "return text report instead of writing docs/reviews/").
- Methodology, skill loads, guardrails, Prime Directives all live in SOT (`System/Agents/*.md` or `.agent/skills/*/SKILL.md`). Wrappers do NOT duplicate — on SOT changes, behavior updates automatically.
- Reviewers and critics (read-only tools): return text reports to the orchestrator; the orchestrator persists to `docs/reviews/` or `docs/audit/` if needed. This mirrors the Wave 1 critic pattern.
- Builders (`analyst`, `architect`, `planner`, `developer`) have Write/Edit to produce their primary artifact directly.

### Layer B — Native Teams (Wave 4, stub)

- **Mechanism**: `TeamCreate` + `SendMessage` + `Agent(team_name=…)`. Each teammate is a **separate session** with its own context window and mailbox.
- **Gate**: experimental feature enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in [.claude/settings.json](../.claude/settings.json).
- **Use cases** (not implemented in Wave 1): peer-debate between critics, parallel feature development with mid-flight schema negotiation, multi-hour research with teammates exchanging findings.
- **Decision rule**: use Layer B **iff** teammates need to exchange messages with each other during work (not just with the lead). Otherwise Layer A.
- **Known gotchas**: see [docs/KNOWN_ISSUES.md](KNOWN_ISSUES.md).

### Shared infrastructure (both layers)

- **Session state**: `.agent/sessions/latest.yaml` with `fcntl`-locking (via `skill-session-state`). Safe for concurrent writes from parallel teammates.
- **Source of truth**: methodology lives in `.agent/skills/*/SKILL.md` (critics) and `System/Agents/*.md` (pipeline roles). Wrapper files in `.claude/agents/` are thin adapters, not duplicated content.
- **Vendor portability**: `.claude/agents/` is Claude Code specific. On other vendors (Codex, Antigravity), workflows fall back to sequential role-switching — see each workflow's `## Fallback` section.

## 6. Key Principles
- **Modular Skills**: Logic is decoupled from Personas. Agents load `skills` to perform specific tasks.
- **Local Artifacts**: `.AGENTS.md` provide distributed long-term memory per directory.
- **Session State**: `latest.yaml` provides volatile short-term memory (GPS coordinates).
- **Single Writer**: Only the Developer agent writes code and updates `.AGENTS.md` to prevent conflicts.
- **Stub-First**: Always create stubs/interfaces before implementation.
- **One Giant Column**: Keep context constraints in mind.
- **Source of Truth**: Documentation (`docs/`), `System/Agents`, `.agent/skills`, and `latest.yaml`.

## 7. Localization Strategy
- **Default**: English (`System/Agents`).
- **Alternative**: Russian (`System/Agents_ru` -> `Translations/RU`).
- Switching is done by swapping the source directory in the orchestrator config.

## 8. Skill Architecture & Optimization Standards

> **Critical Requirement:** All new skills MUST adhere to the **O6/O6a Optimization Standards** defined in [System/Docs/SKILLS.md](../System/Docs/SKILLS.md).

The system relies on a modular **Skills System** ([System/Docs/SKILLS.md](../System/Docs/SKILLS.md)) that separates "Who" (Agent) from "What" (Capabilities). To maintain performance and context limits, strict rules apply:

### Rule 1: Script-First Approach (O6a)
**Do NOT write complex logic in natural language.**
If a skill requires analyzing project structure, calculating metrics, or validating files:
- ❌ **Bad:** "Look at the file, count the lines, then if X..." (Bloats prompt, unreliable).
- ✅ **Good:** "Run `scripts/analyze_metrics.py`." (Zero-hallucination, deterministic).

### Rule 2: Example Separation (O6a)
**Do NOT inline large templates or examples.**
- ❌ **Bad:** Embedding 50 lines of JSON example in `SKILL.md`.
- ✅ **Good:** "Refer to `examples/template.json`."
*Why?* Skills are loaded into the context window. Static text wastes tokens.

### Rule 3: Tiered Loading Protocol (O5)
Every skill must be assigned a **TIER** in its YAML frontmatter to support Lazy Loading.
- **TIER 0 (System):** Always loaded (e.g., `safe-commands`). **Restriction:** Must be <500 tokens.
- **TIER 1 (Phase):** Loaded on phase entry (e.g., `requirements-analysis`).
- **TIER 2 (Extended):** Loaded only on demand (e.g., `adversarial-security`).

### Rule 4: Skill Creator Standard
All new skills must be generated using `skill-creator`.
- **Reason:** Enforces directory structure (`scripts/`, `examples/`, `tests/`) and runs validation checks (`validate_skill.py`).

**[>> Read Full Skills Documentation <<](../System/Docs/SKILLS.md)**

## 9. Framework Installer Subsystem

> **Added in v3.15** (see [docs/TASK.md](TASK.md) — Task 063). Bootstrap-time tool, **not** part of the runtime agent pipeline.

### 9.1 Purpose

The installer deploys the agentic-development framework into a clean **target project** (separate from this repository) under a chosen vendor profile (Claude Code / Antigravity / Codex / Cursor / Gemini CLI). It is invoked from the framework root (this repo) but operates exclusively on the target project. Reference example of a manually-installed project: [/Users/sergey/dev-projects/Universal-skills](/Users/sergey/dev-projects/Universal-skills).

### 9.2 Components

```text
agentic-development/                              # framework repo (source-of-truth)
├── install.sh                                    # Bash wrapper (minimal: BASH_VERSION guard + exec python3)
└── System/scripts/
    ├── install.py                                # argparse entry-point (subcommands: install/switch/update/uninstall/doctor)
    ├── vendors.yaml                              # Vendor profile config (5 profiles + defaults)
    └── installer/                                # Python module (stdlib + PyYAML)
        ├── cli.py                                # Subcommand dispatch
        ├── vendors.py                            # vendors.yaml loader + per-action schema validator
        ├── state.py                              # <target>/.agentic-installer-state.json
        ├── framework_root.py                     # Creates/validates target/.agentic-development/ (symlink|copy)
        ├── symlinks.py                           # link_one, link_per_item + reachability check
        ├── copy.py                               # shutil.copytree wrapper with ignore-list
        ├── managed_block.py                      # Marker block + sha256 hash (shared by gitignore + bootstrap)
        ├── bootstrap.py                          # at_import + marker_block strategies
        ├── gitignore.py                          # managed_block + !-exception scanner
        ├── backup.py                             # Timestamped snapshots + retention
        ├── platform.py                           # Windows detection, symlink probe
        └── errors.py                             # InstallerError hierarchy + exit codes
```

After install, `target/.agentic-development/install.sh` is also available — re-runs don't require the original framework path.

### 9.3 Data Model

**`vendors.yaml`** (config-as-data; new vendor added without Python changes):

```yaml
version: 1
defaults:
  agent_components: [{path, action: link_per_item|link_folder|copy|mkdir, source?, optional?, if_missing?}]
  root_components:  [{path, action, source}]
vendors:
  <vendor_name>:
    bootstrap_strategy: at_import | marker_block | none
    bootstrap_file:    str | null
    bootstrap_aliases: [str]                      # extra bootstrap files beyond bootstrap_file (none of the shipped vendors use this)
    bootstrap_source:  str                        # framework file whose content fills managed-block
    vendor_dir:        str | null
    git_root_required: bool                       # Codex only
    components:        [<component-action-spec>]
```

**`<target>/.agentic-installer-state.json`** (lives at target project root, not inside `.agent/` — survives switch/uninstall):

```json
{
  "version": 1,
  "vendor": "claude",
  "mode": "symlink",
  "framework_path": "/path/to/agentic-development",
  "agentic_development_is_symlink": true,
  "installed_at": "ISO-8601 UTC",
  "gitignore_block_hash": "sha256:...",
  "bootstrap_blocks_hash": {"AGENTS.md": "sha256:...", "GEMINI.md": "sha256:..."},
  "managed_paths": [".agent/skills/foo", ".claude/agents/bar.md", ...],
  "skipped_components": ["System"]                 // user-conflict bypasses; single source of truth for any skipped path
                                                   // (no separate boolean flags like `system_link_skipped` — the plan's wording was
                                                   //  illustrative; the array carries the same information).
}
```

**`doctor --json` output schema** (read-only diagnostic):

```json
{
  "ok": true,                                       // overall health
  "vendor": "claude",
  "errors": [                                       // hard failures (exit 1)
    {"code": "BROKEN_SYMLINK", "path": ".agent/skills/foo", "detail": "..."},
    {"code": "HASH_MISMATCH",  "path": ".gitignore",        "detail": "..."},
    {"code": "STATE_CORRUPT",  "path": ".agentic-installer-state.json", "detail": "..."}
  ],
  "warnings": [                                     // soft issues (exit 0)
    {"code": "SKIPPED_COMPONENT", "path": "System", "reason": "user-owned at install time"},
    {"code": "FOREIGN_FILE",      "path": ".claude/skills/my-local", "reason": "project-local — OK"}
  ]
}
```

### 9.4 Target Project Layout (after install)

```text
myapp/                                                  ← target project root
├── .agentic-development/                              ← symlink|copy of framework (gitignored)
├── .agent/{skills,workflows,agents}/<name>            ← per-item relative symlinks (../../.agentic-development/...)
├── .agent/{tools,rules}                               ← folder symlinks
├── .agent/sessions/                                   ← local runtime state (.gitkeep)
├── .claude/ | .gemini/ | .codex/ | .cursor/           ← per-vendor (only the chosen one is populated)
│   ├── settings.json                                  ← copy (if_missing — protects user customization)
│   ├── hooks/                                         ← copy
│   └── {skills,commands,agents}/<name>                ← per-item symlinks
├── System → .agentic-development/System               ← folder symlink (skipped if user-owned)
├── CLAUDE.md / AGENTS.md / GEMINI.md                  ← project-owned (NEVER overwritten)
├── CLAUDE.local.md, CLAUDE.agentic.md                 ← Claude only (bridge files, gitignored)
├── .agentic-installer-state.json                      ← installer state (gitignored)
└── .gitignore                                         ← contains managed marker-block (hash-protected)
```

### 9.5 Key Invariants

- **Anti-clobber:** Managed-blocks (gitignore + bootstrap) are SHA-256-hashed; on hash mismatch installer aborts with diff. `--force` saves the old version to `.agent/backups/` before overwriting.
- **Don't-overwrite list:** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` are NEVER overwritten, even with `--force` — installer only touches managed-blocks inside them.
- **Pre-flight conflict scan:** Every path is classified `safe | our | hard_conflict | soft_conflict` BEFORE any FS operation. Conflicts default to skip + warning; `--force` enables overwrite (except the don't-overwrite list).
- **Idempotency:** Re-running `install` with no source changes → `0 created, N already linked`.
- **State outside `.agent/`:** `.agentic-installer-state.json` lives at target root so it survives `switch`/`uninstall` operations on `.agent/`.
- **Vendor-aware bootstrap:** Claude uses Claude-native `@import` (3-file pattern); Antigravity/Codex/Gemini-CLI use marker-block injection (their bootstrap formats don't support `@import`).

### 9.6 Security & Safety

- No network access; no `git clone`; no shell execution of vendor content. Pure file operations.
- No PyPI installs beyond the user-explicit `pip install pyyaml` (wrapper prints hint, doesn't install).
- All destructive operations (overwrite, delete) require an explicit `--force` or `--purge` flag and are preceded by timestamped backup with retention (`--max-backups N`, default 5).
- **Reachability check** (`os.stat(follow_symlinks=True)`) after each symlink creation guards against cross-FS dangling links.
- **Canonical-path validation** (architecture-review fix): immediately after creating any symlink inside `target/`, installer asserts `Path(link).resolve().is_relative_to(framework_root.resolve())`. Symlinks whose resolved target escapes `framework_root` (e.g. crafted source name `../../../etc/passwd`) are deleted and a `ConflictError` is raised. Defends against malicious source-name traversal even though installer source paths come from a trusted `vendors.yaml`.
- **TOCTOU between pre-flight scan and write**: pre-flight classifies each path at time `t0`. For the `link_folder` action (the only one that conditionally overwrites a single target), the path is re-verified via `reclassify_before_write()` at write-time `t1` before any FS mutation. `link_per_item` does not re-classify the whole component; instead each individual symlink is created by `link_one()`, which independently refuses to overwrite a foreign real file (`ConflictError`) and confines every link to the framework root (canonical-path guard). `copy` components are copy-if-absent (never overwrite). Net effect: no action silently clobbers user content under a TOCTOU window, though only `link_folder` performs an explicit second classification.
- **Don't-overwrite enforcement**: `is_protected(filename)` returns True for `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` regardless of `--force`. The flag only modifies overwrite policy for managed-blocks inside protected files, never the files themselves.

### 9.7 Out-of-Scope (post-MVP)

- Git clone / submodule population strategies.
- Migration to plural `.agents/` (currently fixed at singular `.agent/`).
- MD→MDC transformer for Cursor `.cursor/rules/`.
- `System/` rename in framework to remove the high-risk collision.

See [docs/TASK.md §5](TASK.md) for full open-question list.
