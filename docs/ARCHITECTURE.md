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
- [10. Figure Authoring Subsystem](#10-figure-authoring-subsystem)

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
│   ├── tasks/                    # Archived TASK.md (task-NNN-slug.md) + planner sub-tasks (task-NNN-SubID-slug.md)
│   ├── plans/                    # [NEW v3.16] Archived PLAN.md (plan-NNN-slug.md) — lockstep with tasks/
│   ├── architectures/            # [NEW v3.16] ARCHITECTURE.md section chunks (Index-Mode, size-driven split only)
│   ├── TASK.md                  # Current Technical Task
│   ├── PLAN.md                  # Current Development Plan
│   ├── ARCHITECTURE.md          # System Architecture (This file) — LIVING doc / index, never per-task archived
│   └── ...
├── tests/                       # Tests & Test Reports
│   ├── tests-{ID}/              # Test Reports per Task (e.g. tests-016/)
│   └── ...
└── archives/
```

**Artifact rotation.** `docs/TASK.md` and `docs/PLAN.md` rotate **in lockstep** on each
new task — `skill-archive-task` archives them to `docs/tasks/task-NNN-slug.md` and
`docs/plans/plan-NNN-slug.md`, sharing the same ID and slug. `docs/ARCHITECTURE.md` is a
single **living document**, updated in place and **never per-task archived**; it is only
restructured into `docs/architectures/` section chunks (with a short index) when it
exceeds 1500 lines. See `artifact-management`, `skill-archive-task`, and
`architecture-format-core` ("Living Document & Index-Mode") for the protocols.

## 3. Workflow Logic (v3.1)
1. **Orchestrator** receives the user task and manages the **Tool Execution Loop**.
    - If the Model supports **Native Tool Calling**, the Orchestrator executes tools directly (structured) and feeds results back.
    - If not, it falls back to text-based parsing.
2. **Agent** (any role) starts by reading relevant local `.AGENTS.md` files...
3. **Agent** activates **Skills** (dynamically loaded from `.agent/skills`).
   - *Example:* Analyst loads `requirements-analysis`.
4. **Analyst** (Agent 02) creates/updates a Technical Specification (TASK) in `docs/TASK.md`.
    - *Verification:* **Task Reviewer** (Agent 03) validates the TASK.
5. **Architect** (Agent 04) validates/updates Architecture in `docs/ARCHITECTURE.md`.
    - *Verification:* **Architecture Reviewer** (Agent 05) checks the design.
6. **Planner** (Agent 06) creates a Task Plan in `docs/PLAN.md` and detailed tasks.
    - *Verification:* **Plan Reviewer** (Agent 07) validates the plan.
7. **Developer** (Agent 08) executes the plan using Stub-First methodology.
    - **Required step**: Updates code AND local `.AGENTS.md` (Documentation First).
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
| `run_tests` | Run one of seven whole test commands, with no other option (TASK 112 R5.3) |
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
| `planner` | `System/Agents/06_planner_prompt.md` | Read, Write, Edit, Grep, Glob, Bash | **opus** | Produces `docs/PLAN.md` + `docs/tasks/*.md` (reuses the TASK Meta ID; generates none) |
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

The committed `settings.json` holds framework permissions only (TASK 111 R2). An operator's own rules live in the ignored `.claude/settings.local.json`, which the installer does not copy. A Bash allow rule matches command text only, so a relative-path rule still approves that path in a nested checkout. A PreToolUse hook to make such a command ask is deferred to WI-34.

Archiving runs through `.agent/tools/archive_move.py`, which one allow rule names (TASK 112). A rule's `*` matches any text, so the script guards its own operands: it moves `docs/TASK.md` into `docs/tasks/` and `docs/PLAN.md` into `docs/plans/`, and refuses every other operand, a link and an existing file. `rebase_links.py` and `init_skill.py`, which allow rules also name, write only to paths inside the working directory and outside `.git/`, compared by path without resolving links. `rebase_links.py --inbound` (TASK 115, `skill-archive-task` Step 8) rewrites the slot links an archived task wrote, in files it finds by scanning the working tree. It writes no symbolic link, no file with a second hard link and no file whose directory resolves outside the working directory, and it runs no `git diff`.

**Model policy** (v3.11.2 + Wave 3):
- **Verifiers and rigor-heavy roles → Opus** (10 wrappers): all 4 dev-pipeline reviewers (`task-reviewer`, `architecture-reviewer`, `plan-reviewer`, `code-reviewer`), 3 adversarial critics (`critic-logic`, `critic-security`, `critic-performance`), `security-auditor`, `planner`, and `product-director`.

  **Why.** Verification is a quality gate, and a false negative there costs more than the extra tokens. The false negatives are missed bugs, missed vulnerabilities, approved broken architecture, poorly decomposed plans and weak product-market judgement. `planner` sits here because plan decomposition carries verifier-like rigor; `product-director` because it gates the Product to Technical handoff.
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
- **Vendor portability**: `.claude/agents/` is Claude Code specific. Other vendors resolve their own native parallel adapter via `skill-parallel-orchestration` §1.1. Codex, Cursor and Antigravity each have a documented parallel primitive, none of them validated end to end. Sequential role-switching is the last resort for a runtime with no primitive, documented per workflow under its vendor-dispatch section.

## 6. Key Principles
- **Modular Skills**: Logic is decoupled from Personas. Agents load `skills` to perform specific tasks.
- **Local Artifacts**: `.AGENTS.md` provide distributed long-term memory per directory.
- **Session State**: `latest.yaml` provides volatile short-term memory (GPS coordinates).
- **Single Writer**: Only the Developer agent writes code and updates `.AGENTS.md` to prevent conflicts.
- **Stub-First**: Always create stubs/interfaces before implementation.
- **One Giant Column**: Keep context constraints in mind.
- **Source of Truth**: Documentation (`docs/`), `System/Agents`, `.agent/skills`, and `latest.yaml`.

## 7. Localization Strategy

### 7.1 Framework language
- **Default**: English (`System/Agents`).
- **Alternative**: Russian (`System/Agents_ru` -> `Translations/RU`).
- Switching is done by swapping the source directory in the orchestrator config.

### 7.2 Project language ≠ framework language

The framework is installed into projects that write **their own** artifacts — `docs/TASK.md`,
`docs/PLAN.md`, task files, ledgers — in whatever language the team uses. Swapping the agent-prompt
directory (§7.1) does not address this: the prompts are the framework's, the artifacts are the
project's, and only the second kind is read back by a gate.

**Invariant (L1): a machine gate never depends on the natural language of the document it judges.**

A gate that matches an English heading or an English column name has two failure modes, and the
quiet one is worse:

| Mode | Example | Consequence |
| :--- | :--- | :--- |
| Loud | `validate.py --mode task` exits 1 on a non-English RTM | The author rewrites in a language they do not use, or stops running the step |
| Silent | a non-latin slug degrades to `"untitled"` | Two different documents resolve to one filename, and nothing reports it |

**Why the loud mode is still a failure.** A step the author stopped running is indistinguishable
from a step that passed.

**Addressing ladder.** [`documentation-standards` §4.1](../.agent/skills/documentation-standards/SKILL.md)
already distinguishes *positional* from *nominal* references. L1 adds the missing third rung: a
reference can be nominal and still break, because it names its target **in a language**.

| Rung | Form | Survives renumbering | Survives retitling | Survives translation |
| :--- | :--- | :--- | :--- | :--- |
| Positional | `§4.5`, `line 112` | ✗ | ✗ | ✗ |
| **Positional + referent** | `` `registry.ts:1083@e95b909`, `if (deadlineHit …) {` `` | ✓ — repaired | n/a | ✓ |
| Nominal-by-prose | `## Requirements Traceability`, `\| Requirement \|` | ✓ | ✗ | ✗ |
| **Nominal-by-anchor** | `<!-- contract:rtm -->` | ✓ | ✓ | ✓ |

**The second rung is not a fourth kind of name — it is a positional reference carrying the
observation that falsifies it** (TASK 103). The number stays positional and stays fragile; what
changes is that its falsity becomes observable, and a machine can recompute the number from the
referent rather than a human re-measuring it. It survives translation for the same reason the anchor
rung does and by a different route: the referent is a substring of the **cited artifact** — code, a
test id, a symbol — so matching it never reads the natural language of the citing document. **L1
holds by construction, not by care.**

Two rungs, two objects, and the names are kept apart deliberately: an **anchor** addresses a section
of a document, a **referent** identifies what a coordinate claims to point at.

**Humans address at any rung; machines address at the anchor rung.** Prose headings stay exactly as
they are — the anchor sits beside them and carries the machine contract, so the two audiences stop
competing for one string.

**Anchor namespace.** `<!-- contract:<name> -->`, reusing the namespace already in service for the
two ledgers. The reserved set and each anchor's consumer are registered in
[`documentation-standards` §4.4](../.agent/skills/documentation-standards/SKILL.md), alongside the
rule itself. **No gate may key on an unregistered anchor.** The converse is deliberately allowed:
an anchor may be registered and emitted before any reader exists, so that the next gate is
language-independent by construction rather than by remembering the rule.

**Compatibility rule.** Anchors are **emitted on write, optional on read**: a template and a prompt
produce them, and every gate keeps its pre-existing prose matcher as a fallback. Documents written
before an anchor existed — including archived artifacts, which are immutable by doctrine, and every
downstream project's corpus — behave exactly as before.

### 7.3 Register is language-independent; its rules are per-language

L1 (§7.2) removes a gate's dependence on the document's language. It says nothing about how the
document reads. Measurement across two independently authored corpora (TASK 096 §1.1) found the
same drift in both: sentences lengthening, and evaluative markers multiplying in a document whose
purpose is to state checkable requirements.

**Invariant (L2): the framework constrains how an artifact reads, never which language it is
written in.**

Two consequences follow, and they pull in opposite directions:

| Check kind | Example | Language handling |
| :--- | :--- | :--- |
| Structural | sentence length, cell width, emoji as severity marker | One implementation, all languages |
| Lexical | evaluative and rhetorical markers | One data file per language |

A language with no rule file is not an error. Structural checks still run, lexical checks report
zero, and the scanner says which language it resolved and that no lexicon backed it. The alternative
— refusing to scan — would make the tool useless in the projects that most need it.

**Advisory by construction.** Register checks report and never fail a phase. §4 of
[`documentation-standards`](../.agent/skills/documentation-standards/SKILL.md) already records why:
a gate that fails on correct documents is how gates get switched off.
Register rules are heuristic, so a false positive is expected rather than exceptional.

**Where the rules live.** One place per artefact class, so the copies cannot drift:

| Artefact | Holds |
| :--- | :--- |
| `documentation-standards` §5.5 | the normative short form and the detector-coverage table |
| `artifact-formalizer/references/authoring-contract.md` | the six per-sentence tests and the licensed statement forms |
| `artifact-formalizer/references/formalization-guide.md` | the rewrite pass and the worked example |
| `artifact-formalizer/data/`, `scripts/` | the per-language lexicons and the scanner |

The three authoring prompts (Analyst, Architect, Planner) and the artefact templates **point at the
contract and do not restate it**. An earlier revision carried the rules inline in each surface;
that produced five copies of one rule set, which is five places for it to drift.

`docs/ARCHITECTURE.md` is also what `--terms` reads when deciding whether a noun is a term or a
coined metaphor, so a metaphor introduced here legitimises itself in every artefact downstream.

### 7.4 What the scanner masks, and how it reports an input it cannot classify

The scanner measures prose. Fenced blocks, HTML comments, link targets and code spans are blanked
before any rule runs. That boundary is the measurement's precondition, not a convenience.

**Invariant (L3): masking never changes the classification of text that follows a masked
construct.**

The scanner makes one left-to-right pass. At each position it opens at most one construct and
consumes it whole. A construct therefore cannot begin inside another.

An earlier implementation applied four regular expressions in sequence, each over the whole text.
TASK 097 §1 records what that produced. A comment boundary landing inside a code span removed one
backtick, and the code/prose classification inverted to the end of the file.

**A code span ends at a blank line**, per CommonMark. The bound also limits how far a residual
mispairing can travel.

**Exit codes, and what each one claims.**

| Code | Claim | Example |
| :--- | :--- | :--- |
| 0 | The scan is a measurement | findings reported, or an input defect named |
| 2 | The instrument is broken | a detector matched nothing under `--probe` |
| 3 | The invocation is wrong | an unreadable path |

**An input defect exits 0.** An unterminated comment and an unpaired backtick are facts about the
document. Naming them stops a zero finding count from reading as a clean document. Failing on them
would break the advisory rule stated above in §7.3.

### 7.5 What the scanner's own gates may compare against

**Invariant (L4): a gate over the scanner compares the artefact under test against a value declared
outside it.**

The two CI gates are the acceptance battery and the detector roster. Both once read their expected
value out of the data they judged, so an edit moved both sides of the comparison at once. Two
measurements. Deleting every rule-6 entry of one language printed `17/17 detectors live` at exit 0.
Replacing a rule-3 pattern together with its declared example left the battery at `174/174` and the
roster at `18/18`, with a real finding lost.

The invariant applies to three kinds of declared value, in order of strength:

| Declared value | Catches | Misses |
| :--- | :--- | :--- |
| A count of what ships | an entry deleted | an entry replaced in place |
| The identity of what ships | an entry replaced in place | a detector blinded outside the data |
| A fixture the mutation must break | a detector blinded in code | a class the fixture does not reach |

**Why all three.** TASK 099 added the counts, and TASK 100 records five mutations that survived
them. A pattern set, a threshold set and a glyph set are pinned by identity. `SKIP_LINE` and the
case flag are held by fixtures the roster runs, because neither is a value a document declares.

A fixture derived from the value it tests is not a declared value. `_structural_probes` builds its
sentence from the active `sentence_max_words`, so that fixture measures the detector and never the
threshold; the threshold is pinned separately.

### 7.6 What measures the half of the register skill that is a prompt

§7.5 covers the scanner. The scanner is Mode B, and it is the half of `artifact-formalizer` that a
declared literal can pin. Mode A is an authoring contract read by a model, and §5 of that skill
assigns the residue of rules 3, 4 and 6 to a reading pass. Neither is a function, so neither has a
value to declare.

**Invariant (L5): a claim about what a model produces is measured by two runs differing in one
input; a claim about what a reading pass finds is measured against a key written before the run.**

| Claim | Reference value | Instrument |
| :--- | :--- | :--- |
| The contract changes what a model writes | the other arm of the same case | `evals/run_authoring.py` + `evals/grade_run.py` |
| The reading pass finds what the detectors do not | a planted answer key | `evals/` fixtures + `evals/grade_run.py` |

**Why the other arm and not a threshold.** A register figure has no absolute pass mark. §5.1 of
`documentation-standards` and the corpus table in `measurement-baseline.md` §1 both report ranges
across corpora. A difference between two arms of one prompt is attributable; a single arm against a
constant is not.

**Why the key is written first.** A key derived after reading the run is the authoring bias L4
excludes for the scanner, applied one level up.

**A recall-gap fixture is valid only while the scanner stays silent on it.** The fixture exists to
measure what the detectors do not reach, so a lexicon entry added later can convert it into a
detector test without touching the fixture. That condition is asserted by
`evals/selftest_evals.py`, not assumed.

**The grader calls the scanner.** It derives no threshold and no finding of its own, per §2 of
`skill-creator/references/advanced-eval-patterns.md`. A reimplementation drifts from the production
rule and keeps reporting against the old one.

## 8. Skill Architecture & Optimization Standards

> **Critical Requirement:** All new skills MUST adhere to the **O6/O6a Optimization Standards** defined in [System/Docs/SKILLS.md](../System/Docs/SKILLS.md).

The system relies on a modular **Skills System** ([System/Docs/SKILLS.md](../System/Docs/SKILLS.md)) that separates "Who" (Agent) from "What" (Capabilities). To maintain performance and context limits, strict rules apply:

### Rule 1: Script-First Approach (O6a)
**Do NOT write complex logic in natural language.**
If a skill requires analyzing project structure, calculating metrics, or validating files:
- **Rejected:** "Look at the file, count the lines, then if X..." — bloats the prompt, and the
  result varies per run.
- **Required:** "Run `scripts/analyze_metrics.py`." — deterministic, and no value is invented.

### Rule 2: Example Separation (O6a)
**Do NOT inline large templates or examples.**
- **Rejected:** Embedding 50 lines of JSON example in `SKILL.md`.
- **Required:** "Refer to `examples/template.json`."
*Why?* Skills are loaded into the context window. Static text wastes tokens.
*Enforcement:* `validate_skill.py` applies a two-tier inline-block check — a fenced block over 20 lines warns, over 60 lines fails (`mermaid` exempt; `text`/`console`/`output` warn-only). Thresholds are config-driven via `validation.quality_checks.max_inline_lines_warn`/`_fail`.

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
├── install.sh                                    # Bash wrapper: checks bash, python3, the minimum Python (README §3) and PyYAML, then exec python3
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
│   ├── hooks/                                         ← copy (Claude: validate_skill_hook.sh)
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

## 10. Figure Authoring Subsystem

TASK 108. The skill `mermaid-authoring-guidelines` (tier 2) governs every figure an agent writes into
an output. It is loaded before the first figure of any output, in any phase; a generated plan chart
needs no load.

### 10.1 Components

| Component | Kind | Role | Runs in CI |
| :--- | :--- | :--- | :--- |
| `SKILL.md` | prompt | Step 0 form choice, the authoring contract, the process, the routing table | — |
| `references/*.md` | prompt | notation per kind, renderer facts, layout, ASCII, paired examples, review | — |
| `assets/notation.json` | data | budgets, thresholds, settings lines, palette, allowed and avoided kinds | read by tests |
| `scripts/mermaid_model.py` | library | fence extraction; parsers for flowchart, sequence, state, gantt, ASCII | unit tests |
| `scripts/lint_mermaid.py` | CLI | static rules with probe pairs; `--inventory` worksheet | yes |
| `scripts/planarity.py` | library | exact planarity test of a flowchart's simple graph | unit tests |
| `scripts/svg_geometry.py` | library | crossings, edges through nodes and titles, overlaps, size, from an SVG | fixture tests |
| `scripts/render_check.py` | CLI | renders with pinned installs, measures text, calls `svg_geometry` | no |
| `scripts/setup_renderers.sh` | CLI | installs the pinned renderers into a cache outside the repository | no |
| `assets/renderers/<tag>/` | data | `package.json` and lockfile per pinned renderer, installed with `npm ci` | — |
| `assets/renderers/browsers.json` | data | tree sha256 of each browser build the setup accepts without the operator's hash | read by tests |
| `scripts/plan_gantt.py` | CLI | schedule from a task list; writes or checks the plan chart block | yes |
| `evals/` | instruments | the A/B evaluation of the skill (§10.4) | selftest only |

**Why one data file.** The lint, the render check and the eval grader read every threshold from
`assets/notation.json`. A test pins that the references quote the same values. A threshold held in
two places drifts in one of them.

### 10.2 Authoring flow

1. Step 0 picks the form: no figure, list or table, ASCII, Mermaid, image. The first sufficient
   form is used.
2. For Mermaid, the agent writes the figure to a scratch file outside the repository.
3. `lint_mermaid.py` reports static findings. Postcondition: 0 `error`.
4. `render_check.py` renders in mermaid 11.17.2 and 10.9.8, plus a dark 11.17.2 render.
   Postcondition: exit 0, or exit 2 with `not rendered: <reason>` stated in the hand-off.
5. `lint_mermaid.py --inventory` lists every element; the agent cites a supporting line for each.
6. The agent inserts caption, fence and legend, and runs the lint on the document.

### 10.3 Interfaces

Exit codes follow §7.4: 0 measured and clean, 1 a defect found, 2 the instrument is broken or
absent, 3 the invocation is wrong (TASK 108 D20).

| Command | 0 | 1 | 2 | 3 |
| :--- | :--- | :--- | :--- | :--- |
| `lint_mermaid.py <file.md\|file.mmd> [--json] [--inventory] [--probe]` | no error | error found | internal failure or dead rule | usage |
| `render_check.py <file> [--no-dark] [--forward] [--versions TAGS] [--json] [--out DIR] [--fixture FILE]` | pass | a figure fails or does not parse; a broken negative fence, or one that fails a render check its marker does not name | not rendered: a required render left out, no mermaid fence, or output that cannot be written | usage, including a `--fixture` that is not a render-evidence fixture |
| `plan_gantt.py <plan> [--write DOC\|--check DOC] [--stages ...] [--strict]` | ok | stale block or invalid plan | internal failure | usage |

`setup_renderers.sh [--forward] [--dry-run]` exits 0 when installed, 1 with the failing step
named, 3 on usage. `plan_gantt.py` reads a JSON schedule, or the JSON block under
`<!-- contract:schedule -->` of a plan; it never parses the plan's prose (L1). A chart split with
`--stages` stores its stage groups in the region's first line, `<!-- plan-gantt-groups: ... -->`,
which a later `--write` or `--check` reuses.

A fence whose last body line is `%% negative: <names>` shows a defect on purpose (TASK 108 R9.4).
The marker counts only in the skill's `references/` and `scripts/tests/fixtures/`. There, the
findings of the rules and families it names are `expected` and set no exit code; every other
finding counts. Elsewhere the lint reports the marker (MA-NEG-03), and the render check grades the
fence as an ordinary figure. A parse or render error in 11.17.2 or 10.9.8 fails a negative fence
unless its marker names a parse rule. The render check calls the fence broken, exit 1, when it
names render checks and none of them fails, or when a render check it does not name fails. A
marker that names no render check has its renders graded as a positive figure. The lint and the
render check read the marker and its scope through one definition in `mermaid_model.py`. A figure of a kind whose geometry the check does not
model passes as `pass, geometry not checked`; the PNG answers for its crossings and overlaps.
`--fixture FILE` merges hash-bound evidence into `FILE`: the sha256 of the fence lines, the
renderer versions, the browser build, and the metrics of each render. The unit tests read it
without node (R9.5).

### 10.4 Evaluation

`evals/` measures the skill under invariant L5 (§7.6). The arms differ in one input: the skill
bundle that `SKILL.md`'s routing table names for the case's figure kind. Keys are written before
any run. The grader imports `lint_mermaid` and `svg_geometry` and restates no threshold. Rendering
happens once, in `render_corpus.py`, so the grader is a function of committed files and its pin
runs in CI. The decision rule is TASK 108 D8.

### 10.5 Invariant

**Invariant (L6): a figure check states the renderer versions it ran; a check that did not render
reports `not rendered: <reason>` and exits 2, never 0.**

**Why.** Renderers differ in layout, wrapping and syntax support between 10.9, 11.17 and 12.1. A
pass without a version names no observable state, and exit 0 from a check that never ran is the
failure `developer-guidelines` §6.3 describes.

L1 (§7.2) applies to the lint. Caption and legend are found by their position next to the fence.
Label limits count characters per line; the lowercase rule for edge labels applies to cased
scripts only.

### 10.6 Integration points

| Surface | What it states |
| :--- | :--- |
| `architecture-format-core` §2.2, §3.3; `architecture-format-extended` | load the skill; the figure block skeleton; ER subset or table |
| `documentation-standards` §5.6 | caption and legend positions; the form ladder; fences are exempt from §5.1 |
| `04_architect_prompt.md`, `06_planner_prompt.md` | load before the first figure; plan chart at 8 or more tasks |
| `05_architecture_reviewer_prompt.md`, `07_plan_reviewer_prompt.md` and four review checklists | figure items over caller-supplied lint and render output; the plan reviewer also gets `plan_gantt.py --check` output |
| workflows `01-start-feature.md`, `vdd-01-start-feature.md`, `02-plan-implementation.md`, `vdd-02-plan.md` | the caller runs the figure lint, and `plan_gantt.py --check` for a plan, before the reviewer's brief |
| plan template and `PLAN_EXAMPLE.md` of `skill-planning-format` | the schedule block, `not-started` per task, and the generated region |
| workflows `03-develop-single-task.md`, `vdd-03-develop.md`, `vdd-05-run-full-task.md` | set a task `in-progress` and `done` and run `plan_gantt.py --write` (`skill-planning-format` §2.2) |
| `.claude/agents/architect.md` | the architect may run the lint and the render check |
| `.claude/settings.json` | the lint and `plan_gantt.py --check` run without approval; the render check asks |
| `skill-phase-context`, `SKILL_TIERS.md`, bootstrap files | the conditional load |
| `brainstorming`, `security-audit` DFD, `skill-reverse-engineering`, `skill-planning-format` | figures follow the skill |

### 10.7 Security and safety

- `setup_renderers.sh` installs exact versions with `npm ci --ignore-scripts` from committed
  lockfiles, never globally, into `${MERMAID_RENDER_HOME:-~/.cache/mermaid-authoring-guidelines}`,
  with the npm cache beside the installs. The v10 lockfile overrides puppeteer with the version of
  v11; `npm audit` reports no high advisory for any lockfile (TASK 110).
- The setup accepts a browser only when the tree hash of its directory is in
  `assets/renderers/browsers.json` or equals `MERMAID_RENDER_BROWSER_SHA256`, set by the operator,
  and when that directory and the one above it are private. It resolves every symbolic link of
  the browser path once and writes that path into `puppeteer.json` and into the stamp. The hash
  covers the directory of the executable only, so `MERMAID_RENDER_CHROME` names the browser binary
  in a directory that holds that browser only.
- `render_check.py` refuses an install in seven cases (TASK 110 R7.3, R7.7):
  - its lockfile stamp is stale;
  - its browser stamp is missing, or holds no tree hash or no stat digest;
  - the stamp names another browser than `puppeteer.json`;
  - the browser path no longer resolves to itself;
  - another user may write the executable;
  - another user may change the browser directory or the one above it;
  - the stat digest of the browser directory differs from the stamped one.

  It does not hash the browser again. It compares the stat digest: the inode, size, mtime and
  ctime of every entry, read with `lstat` at every render. A change of metadata alone, such as an
  extended attribute or a remount, also refuses the install until the setup runs again.
- The browser resolves no host name, localhost included, uses no proxy, and talks to puppeteer
  over a pipe; `render_check.py` refuses a config that lacks these arguments.
- Every node process runs inside its install directory, which holds an empty `.puppeteerrc.json`.
  A configuration file in the caller's directory or its parents is never read, so it cannot run
  code in a render.
- The install home, each install and the render output directory are private to the user. A
  directory others may write to is refused.
- The browser runs with its sandbox. `--no-sandbox` is passed only when
  `MERMAID_RENDER_NO_SANDBOX=1` is set.
- Renders and PNGs are written outside the repository, so a review round's tree fingerprint does
  not change.
- `run_evals.py` spends tokens and stays off the safe-command list, like `run_authoring.py`.

### 10.8 Out of scope

- The ELK layout. GitHub does not register it, and every settings line pins `dagre`.
- Consumer projects and Universal-skills, which receive the skill after `install.py update`.
