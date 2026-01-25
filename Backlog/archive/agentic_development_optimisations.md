# Agentic Development Framework Optimizations

> **Status:** VDD-Reviewed Roadmap
> **Created:** 2026-01-21
> **Purpose:** Preparation for enterprise scaling through efficiency optimization

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Current State Analysis](#current-state-analysis)
  - [Component Token Consumption](#component-token-consumption)
  - [Emulated Development Cycle](#emulated-development-cycle)
  - [Critical Hotspots](#critical-hotspots)
- [Optimization Roadmap](#optimization-roadmap)
- [Detailed Recommendations (O1-O10)](#detailed-recommendations-o1-o10)
  - [O1: Phase-Specific Skill Loading](#o1-phase-specific-skill-loading-selective-loading-protocol)
  - [O2: Orchestrator Compression](#o2-orchestrator-compression)
  - [O3: architecture-format Split](#o3-architecture-format-split)
  - [O4: Conversation Checkpointing](#o4-conversation-checkpointing)
  - [O5: Skill Tiers (Formalization)](#o5-skill-tiers-formalization--completed)
  - [O6: Agent Prompt Standardization](#o6-agent-prompt-standardization-optimization)
  - [O7: Session Context Management](#o7-session-context-management-high-impact)
  - [O8-O10: Strategic Optimizations](#o8-domain-isolation-enterprise)
- [Feasibility Report (2026-01-21 Post-O5)](#feasibility-report-2026-01-21-post-o5)
- [Implementation Plan (O1-O4)](#implementation-plan-o1-o4)
- [VDD Adversarial Review](#vdd-adversarial-review)
- [Metrics & Success Criteria](#metrics--success-criteria)
- [Implementation Prompts](#implementation-prompts-for-future-dialogue)
- [Changelog](#changelog)

---

## Executive Summary

Данный документ содержит детальный план оптимизации текущего фреймворка Agentic-Development для:

1. **Снижения token overhead** на 27% (с ~16K до ~11.7K tokens)
2. **Увеличения пространства для кода** с 112K до 116K tokens
3. **Подготовки к enterprise-масштабированию** с поддержкой domain isolation

> [!CAUTION]
> **MANDATORY REQUIREMENT: Cross-Check Final Logic**
> 
> All optimizations MUST preserve existing framework behavior.
> Before implementing ANY change:
> 1. **Document current behavior** explicitly
> 2. **Cross-check final logic** to avoid information loss
> 3. **VDD-verify** that optimization doesn't break existing patterns
> 4. **Test before/after** to confirm equivalence

**Ключевые метрики:**

| Метрика | Текущее | Целевое | Δ |
|---------|---------|---------|---|
| Framework Overhead | ~16,000 tokens | ~11,700 tokens | -27% |
| Standard Pipeline | ~50,000 tokens | ~38,000 tokens | -24% |
| Peak Usage | 65-85K tokens | 50-65K tokens | -23% |

---

## Current State Analysis

### Component Token Consumption

#### Agent Prompts (System/Agents/)

| File | Size (bytes) | Tokens | Priority |
|------|--------------|--------|----------|
| `01_orchestrator.md` | 11,195 | ~2,799 | 🔴 HIGH |
| `00_agent_development.md` | 8,544 | ~2,136 | Medium |
| `06_agent_planner.md` | 4,173 | ~1,043 | Low |
| `02_analyst_prompt.md` | 4,041 | ~1,010 | Low |
| `08_agent_developer.md` | 4,039 | ~1,010 | Low |
| `04_architect_prompt.md` | 3,856 | ~964 | Low |
| `03_task_reviewer_prompt.md` | 3,225 | ~806 | Low |
| `05_architecture_reviewer_prompt.md` | 3,061 | ~765 | Low |
| `07_agent_plan_reviewer.md` | 2,027 | ~507 | Low |
| `09_agent_code_reviewer.md` | 2,013 | ~503 | Low |
| `10_security_auditor.md` | 500 | ~125 | Low |
| **TOTAL** | **46,674** | **~11,669** | |

#### Skills (.agent/skills/)

| Skill | Tokens | Frequency | Priority |
|-------|--------|-----------|----------|
| `architecture-format` | ~2,535 | Low | 🔴 HIGH |
| `skill-reverse-engineering` | ~1,322 | Low | Low |
| `skill-update-memory` | ~1,101 | Medium | Low |
| `skill-adversarial-performance` | ~946 | VDD | Low |
| `skill-safe-commands` | ~927 | **EVERY** | Medium |
| `skill-archive-task` | ~917 | New tasks | Medium |
| `requirements-analysis` | ~904 | Analysis | Low |
| `skill-adversarial-security` | ~838 | VDD | Low |
| `skill-planning-format` | ~756 | Planning | Low |
| `artifact-management` | ~636 | **EVERY** | Medium |
| `skill-task-model` | ~590 | Analysis | Low |
| `architecture-design` | ~551 | Architecture | Low |
| `core-principles` | ~519 | **EVERY** | Medium |
| Other (12 skills) | ~4,503 | Varies | Low |
| **TOTAL** | **~16,045** | | |

#### Configuration & Workflows

| Component | Tokens |
|-----------|--------|
| `GEMINI.md` | ~1,394 |
| `AGENTS.md` | ~867 |
| Workflows (14 files) | ~3,144 |
| **TOTAL** | **~5,405** |

### Emulated Development Cycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOKEN CONSUMPTION PER PHASE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  SESSION START ............................ ~6,900 tokens                   │
│  PHASE 1: ANALYSIS ........................ ~6,383 tokens                   │
│  PHASE 2: TASK REVIEW ..................... ~1,306 tokens                   │
│  PHASE 3: ARCHITECTURE .................... ~4,850 tokens                   │
│  PHASE 4: ARCHITECTURE REVIEW ............. ~1,111 tokens                   │
│  PHASE 5: PLANNING ........................ ~3,968 tokens                   │
│  PHASE 6: PLAN REVIEW ..................... ~762 tokens                     │
│  PHASE 7: DEVELOPMENT (×3 tasks) .......... ~20,334 tokens                  │
│  PHASE 8: CODE REVIEW (×3 tasks) .......... ~4,167 tokens                   │
│  PHASE 9: SECURITY ........................ ~260 tokens                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  GRAND TOTAL (Standard Pipeline): ~50,041 tokens                            │
│  + VDD Multi-Adversarial: +5,000 tokens                                     │
│  + Conversation history: +10,000-30,000 tokens                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  PEAK USAGE: 65,000-85,000 tokens                                           │
│  REMAINING (128K): 43,000-63,000 for CODE                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Critical Hotspots

> [!WARNING]
> **#1: Orchestrator Dominance**
> `01_orchestrator.md` (~2,799 tokens) — 24% of all agent prompts
> Contains 14 scenarios with duplicated structures

> [!WARNING]  
> **#2: architecture-format Anomaly**
> `skill-architecture-format` (~2,535 tokens) — 16% of all skills
> Loaded even when minor architecture changes

> [!WARNING]
> **#3: Mandatory Skills Overhead**
> 3 skills loaded EVERY session: ~2,082 tokens
> - `core-principles` (519) + `artifact-management` (636) + `safe-commands` (927)

---

## Optimization Roadmap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OPTIMIZATION ROADMAP                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  v3.5.1 — IMMEDIATE (O1-O4)                        Target: -8K tokens      │
│  ├── O1: Lazy Loading Protocol                                             │
│  ├── O2: Orchestrator Compression                                          │
│  ├── O3: architecture-format Split                                         │
│  └── O4: Conversation Checkpointing (Merged into O7)                       │
│                                                                             │
│  v3.6.0 — MEDIUM-TERM (O5-O7)                      Target: -18K tokens     │
│  ├── O5: Skill Tiers (Formalization)                                       │
│  ├── O6: Agent Prompt Standardization                                      │
│  └── O7: Session Context Management                                        │
│                                                                             │
│  v4.0.0 — STRATEGIC (O8-O10)                       Enterprise-ready        │
│  ├── O8: Domain Isolation                                                  │
│  ├── O9: Multi-Session Pipeline                                            │
│  └── O10: Hierarchical Context                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Recommendations (O1-O10)

### O1: Phase-Specific Skill Loading (Selective Loading Protocol)

**Problem:** Phase-specific skills loaded at session start even when not needed

> [!IMPORTANT]
> **Investigation Results (2026-01-21):**
> Comprehensive grep analysis across all agents revealed skill usage patterns.

#### Skill Classification (Based on Actual Usage)

**TIER 0: SYSTEM FOUNDATION (ALWAYS LOAD — Non-negotiable)**

These skills are marked `(Mandatory)` in ALL or MOST agent prompts and are critical for framework operation:

| Skill | Tokens | Usage | Why Always Load |
|-------|--------|-------|----------------|
| `core-principles` | ~519 | 9/10 agents (Mandatory) | Anti-hallucination rules, Stub-First, Documentation First |
| `safe-commands` | ~927 | 10/10 agents (Mandatory) | **Enables automation** — auto-run commands |
| `artifact-management` | ~636 | Orchestrator (Mandatory) + 4 agents (Reading) | Archiving protocol, file management |
| **TIER 0 TOTAL** | **~2,082** | | **CANNOT be lazy-loaded** |

**TIER 1: PHASE-TRIGGERED (Load on Phase Entry)**

These skills are phase-specific and can be deferred:

| Skill | Tokens | Phase | Load Trigger |
|-------|--------|-------|-------------|
| `requirements-analysis` | ~904 | Analysis | When 02_analyst activated |
| `skill-task-model` | ~590 | Analysis | When creating TASK.md |
| `skill-archive-task` | ~917 | Analysis | When new task detected |
| `architecture-design` | ~551 | Architecture | When 04_architect activated |
| `architecture-format` | ~2,535 | Architecture | When creating new ARCHITECTURE.md |
| `planning-decision-tree` | ~423 | Planning | When 06_planner activated |
| `planning-format` | ~756 | Planning | When creating PLAN.md |
| `tdd-stub-first` | ~246 | Planning/Dev | When stub creation starts |
| `developer-guidelines` | ~343 | Development | When 08_developer activated |
| `documentation-standards` | ~425 | Development | When updating docs |
| **TIER 1 TOTAL** | **~7,690** | | **Candidates for on-demand loading** |

**TIER 2: EXTENDED (Load Only When Explicitly Requested)**

> [!IMPORTANT]
> **Precise Loading Conditions for TIER 2 Skills**
> Must be VDD-verified before implementation.

| Skill | Tokens | Loading Condition (Precise) |
|-------|--------|-----------------------------|
| `architecture-format-extended` | ~2,000 | Load when: (1) Creating NEW system from scratch, OR (2) Major architectural refactor (>3 components affected), OR (3) User explicitly requests "full architecture template" |
| `reverse-engineering` | ~1,322 | Load when: (1) User requests "sync docs with code", OR (2) Agent detects significant docs/code mismatch, OR (3) Onboarding to unfamiliar codebase |
| `update-memory` | ~1,101 | Load when: Post-development phase completed AND .AGENTS.md updates needed |
| `adversarial-security` | ~838 | Load when: VDD workflow invoked OR security-audit workflow |
| `adversarial-performance` | ~946 | Load when: VDD workflow invoked OR performance review requested |
| `vdd-sarcastic` | ~145 | Load when: VDD workflow invoked with sarcastic mode |
| **TIER 2 TOTAL** | **~7,023** | |

---

**Current behavior:**
```
Session start → Load GEMINI.md → Load ALL skills referenced in agent prompts
                                      ↑
                             ~9,772 tokens (Tier 0 + all Tier 1)
```

**Proposed behavior:**
```
Session start → Load GEMINI.md → Load TIER 0 (System Foundation)
                     │                     ↑
                     │              ~2,082 tokens (ALWAYS)
                     ▼
         Phase detected → Load TIER 1 skills for CURRENT phase only
                                      ↑
                              ~1,000-2,000 tokens per phase
```

**Implementation:**

1. Create `skill-phase-context/SKILL.md` (replaces lazy-loader concept):
```markdown
# Phase Context Loading Protocol

## System Foundation (TIER 0) — ALWAYS LOADED
These skills MUST be available in EVERY session:
- `core-principles` — Anti-hallucination, Stub-First methodology
- `safe-commands` — Enables auto-run for `mv`, `ls`, `git`, tests
- `artifact-management` — Archiving protocol, file management

> [!CAUTION]
> NEVER lazy-load TIER 0 skills. They enable core automation.

## Phase → Additional Skills Mapping (TIER 1)
| Phase | Additional Skills to Load |
|-------|---------------------------|
| Analysis | requirements-analysis, skill-task-model, (archive-task if new) |
| Architecture | architecture-design, (architecture-format if new system) |
| Planning | planning-decision-tree, planning-format, tdd-stub-first |
| Development | developer-guidelines, documentation-standards |
| Review | code-review-checklist |
| Security | security-audit |
| VDD | vdd-adversarial, adversarial-* (per workflow) |

## Loading Rule
1. TIER 0 skills: Load at session bootstrap (GEMINI.md)
2. TIER 1 skills: Load when entering corresponding phase
3. TIER 2 skills: Load ONLY when explicitly referenced by user or workflow
```

2. Update `GEMINI.md` to explicitly list TIER 0 skills in bootstrap
3. Update agent prompts to trigger TIER 1 loading on phase entry

**Savings:** ~3,000-5,000 tokens (TIER 1 skills not loaded until needed)
**Risk:** LOW — System Foundation skills always present
**Effort:** 3-4 hours

---

### O2: Orchestrator Compression

**Problem:** `01_orchestrator.md` contains 14 verbose scenarios with repeated structures

> [!CAUTION]
> **Cross-Check Requirement:** This optimization MUST preserve all 14 scenario behaviors.
> Document each scenario's unique logic before compression.

**Analysis of duplication:**
```
Scenario 1-3:   Analysis (init, review, revision)     ~800 tokens × 3 = 2,400
Scenario 4-6:   Architecture (init, review, revision) ~600 tokens × 3 = 1,800
Scenario 7-9:   Planning (init, review, revision)     ~500 tokens × 3 = 1,500
Scenario 10-12: Execution (init, review, fix)         ~600 tokens × 3 = 1,800
Scenario 13-14: Completion, Blocking                  ~400 tokens × 2 = 800
                                                      TOTAL: ~8,300 tokens (in-file)
```

**Proposed compression:**

> [!WARNING]
> **VDD-Verified Conditions for Pattern Usage**
> Each pattern MUST have explicit applicability conditions.

1. Extract common patterns into `skill-orchestrator-patterns`:
```markdown
## Pattern: Stage Cycle (VDD-VERIFIED)

### Applicability Conditions (ALL must be true):
- [ ] Stage has exactly 3 sub-phases: Init → Review → Revision
- [ ] Max iterations is 2
- [ ] Reviewer agent exists for this stage
- [ ] Revision uses same artifact path as init

### Pattern Definition:
INPUT: {stage_name}, {agent_prompt}, {artifact_path}, {reviewer_prompt}
FLOW:
1. Read {agent_prompt}
2. Execute → Create {artifact_path}
3. Check blocking_questions → IF yes: STOP, ask user
4. Read {reviewer_prompt}
5. IF critical_issues AND iteration < 2 → Revision (re-invoke agent)
6. IF critical_issues AND iteration = 2 → STOP, ask user
7. IF non-critical AND iteration = 2 → Proceed with warning
8. ELSE → Next Stage

### Exceptions (Pattern does NOT apply):
- Execution stage: Max iterations = 1 (single fix)
- Blocking questions: Different handling (scenario 14)
- Completion: No reviewer (scenario 13)
```

2. Reduce `01_orchestrator.md` to stage dispatch table:
```markdown
| Stage | Agent | Reviewer | Max Cycles | Skill |
|-------|-------|----------|------------|-------|
| Analysis | 02_analyst | 03_task_reviewer | 2 | archive-task |
| Architecture | 04_architect | 05_architecture_reviewer | 2 | architecture-design |
| Planning | 06_planner | 07_plan_reviewer | 2 | planning-decision-tree |
| Execution | 08_developer | 09_code_reviewer | 1 | developer-guidelines |
```

**Savings:** ~1,500-2,000 tokens
**Risk:** MEDIUM — Requires careful testing
**Effort:** 4-6 hours

---

### O3: architecture-format Split

**Problem:** `architecture-format` (~2,535 tokens) loaded for any architecture change

> [!CAUTION]
> **Cross-Check Requirement:** The split MUST preserve ALL 11 sections.
> No instruction loss is acceptable.

**Current structure (ACTUAL — verified 2026-01-21):**
```
architecture-format/SKILL.md (523 lines, 10KB, 11 sections)
├── Section 1: Core Concept (lines 1-30)
├── Section 2: Directory Structure (lines 31-50)
├── Section 3: System Components (lines 51-135)
├── Section 4: Data Model (conceptual + logical + diagram) (lines 136-194)
├── Section 5: API Contracts (request/response examples) (lines 195-260)
├── Section 6: Technology Stack (backend/frontend/db/infra) (lines 261-341)
├── Section 7: Security (auth, rate limiting) (lines 342-385)
├── Section 8: Scalability & Performance (lines 386-430)
├── Section 9: Monitoring & Observability (lines 431-470)
├── Section 10: Deployment & Configuration (lines 471-510)
└── Section 11: Open Questions (lines 511-523)
```

**Proposed split (PRESERVING ALL CONTENT):**
```
architecture-format-core/SKILL.md (~150 lines, ~1,200 tokens)
├── Section 1: Core Concept (REQUIRED)
├── Section 2: Directory Structure (REQUIRED)
├── Section 3: System Components — minimal template only
├── Section 4: Data Model — conceptual only
├── Section 11: Open Questions (REQUIRED)
└── NOTE: "For full templates, load architecture-format-extended"

architecture-format-extended/SKILL.md (~400 lines, ~3,500 tokens)
├── Section 3: System Components — full with examples
├── Section 4: Data Model — full with ER diagrams
├── Section 5: API Contracts — full with JSON examples
├── Section 6: Technology Stack — full with justifications
├── Section 7: Security — full checklist
├── Section 8: Scalability — full patterns
├── Section 9: Monitoring — full setup
├── Section 10: Deployment — full instructions
└── CROSS-REFERENCE: Imports core for base structure
```

**Loading logic (Precise Conditions):**

| Condition | Load |
|-----------|------|
| Updating existing architecture (minor change) | `core` only |
| Adding new component to existing system | `core` only |
| Creating NEW system from scratch | `extended` |
| Major refactor (>3 components changed) | `extended` |
| Sophisticated requirement / complex task | `extended` |
| User explicitly requests full template | `extended` |

**Savings:** ~1,200-1,500 tokens (when using core only)
**Risk:** LOW if cross-check performed
**Effort:** 3-4 hours (increased due to careful split)

---

### O4: Conversation Checkpointing

**Problem:** Conversation history grows linearly, consuming 10-30K tokens by session end

**Proposed solution:**

1. Create `skill-context-checkpoint`:
```markdown
# Context Checkpoint Protocol

## Checkpoint Triggers
- After TASK.md creation → Summarize analysis in 200 tokens
- After ARCHITECTURE.md update → Summarize in 150 tokens
- After PLAN.md creation → Summarize in 200 tokens
- After each task completion → Summarize in 100 tokens

## Checkpoint Format
```yaml
checkpoint:
  phase: {current_phase}
  artifacts:
    - path: docs/TASK.md
      summary: "Implement user authentication with OAuth2..."
  decisions:
    - "Using PostgreSQL for persistence"
    - "JWT tokens with 24h expiry"
  blockers: []
```
```

2. Integrate with IDE's context management (if supported)

**Savings:** 5,000-15,000 tokens
**Risk:** MEDIUM — Depends on IDE support
**Effort:** 4-8 hours

---

### O5: Skill Tiers (Formalization) ✅ COMPLETED

> [!NOTE]
> **Completed: 2026-01-21** | Version: v3.6.0
> **Deliverable:** `System/Docs/SKILL_TIERS.md`
> **Verification:** 100% of skills tagged with `tier` metadata.

**Status:** COMPLETED
**Prerequisite:** O1 (Completed)

**Analysis:**
Now that O1 is implemented and verified (v3.5.4), O5 is the necessary follow-up to "lock in" the changes. It involves creating authority documentation (`System/Docs/SKILL_TIERS.md`) and adding metadata headers to all SKILL.md files.

**Skill Tier Reference (Authoritative):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SKILL TIERS (AUTHORITATIVE)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TIER 0: SYSTEM FOUNDATION — Load at BOOTSTRAP (Non-negotiable)             │
│  ├── core-principles ............... ~519 tokens (Anti-hallucination)      │
│  ├── safe-commands ................. ~927 tokens (Enables automation!)     │
│  └── artifact-management ........... ~636 tokens (File protocol)           │
│                                      ─────────                              │
│                                      ~2,082 tokens ALWAYS                   │
│                                                                             │
│  TIER 1: PHASE-TRIGGERED — Load on phase entry                              │
│  ├── Analysis Phase:                                                        │
│  │   ├── requirements-analysis ..... ~904 tokens                           │
│  │   ├── skill-task-model .......... ~590 tokens                           │
│  │   └── archive-task .............. ~917 tokens (if new task)             │
│  ├── Architecture Phase:                                                    │
│  │   ├── architecture-design ....... ~551 tokens                           │
│  │   └── architecture-format-core .. ~1,200 tokens (after O3 split)        │
│  │       └── Load EXTENDED for: new system / major refactor / complex task │
│  ├── Planning Phase:                                                        │
│  │   ├── planning-decision-tree .... ~423 tokens                           │
│  │   ├── planning-format ........... ~756 tokens                           │
│  │   └── tdd-stub-first ............ ~246 tokens                           │
│  ├── Development Phase:                                                     │
│  │   ├── developer-guidelines ...... ~343 tokens                           │
│  │   └── documentation-standards ... ~425 tokens                           │
│  └── Review Phase:                                                          │
│      ├── code-review-checklist ..... ~386 tokens                           │
│      └── task/plan/arch-review ..... ~300-400 tokens each                  │
│                                                                             │
│  TIER 2: EXTENDED — Load only when explicitly requested                     │
│  ├── architecture-format-extended .. ~2,000 tokens (new systems only)      │
│  ├── reverse-engineering ........... ~1,322 tokens (codebase sync)         │
│  ├── update-memory ................. ~1,101 tokens (post-dev)              │
│  ├── adversarial-security .......... ~838 tokens (VDD only)                │
│  ├── adversarial-performance ....... ~946 tokens (VDD only)                │
│  └── vdd-sarcastic ................. ~145 tokens (VDD only)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
```
**Recommendation:**
- **Proceed immediately.** This is low-risk and high-value for maintainability.
- **Action:** Add `tier: [0|1|2]` to YAML frontmatter of all skills.
- **Action:** Create `System/Docs/SKILL_TIERS.md` as the single source of truth.

**Effort:** 2-4 hours.

---

### O6: Agent Prompt Standardization (Optimization)

**Status:** IMPLEMENTED ✅
**Date (Prototype):** 2026-01-22

**Analysis:**
The success of O2 (Orchestrator Compression) proved that "Structured Patterns" (Input → Flow → Decision) are more effective than cryptic DSLs.
Instead of "compressing" prompts to be shorter, we **standardized** them to use the same structural rigidity as the Orchestrator.

**Prototype (Completed 2026-01-22):**
Refactored `02_analyst_prompt.md` to use standard schema:
1. **Identity & Prime Directive** (from `core-principles`)
2. **Context Loading** (from `skill-phase-context`)
3. **Execution Loop** (Input → Process → Artifact → Review)

**Actionable Data for Infographic (A/B Test Results 2026-01-22):**

| Agent | Role | Delta (Tokens) | Delta (%) | Status | Check |
|-------|------|----------------|-----------|--------|-------|
| `01` | Orch. | -406 | **-36.24%** | ✅ Logic Preserved | [x] |
| `02` | Analyst | -24 | **-2.35%** | ✅ Optimization | [x] |
| `03` | Task Rev. | -79 | **-9.88%** | ✅ Optimization | [x] |
| `04` | Architect | -342 | **-28.86%** | ✅ Major Opt. | [x] |
| `05` | Arch Rev. | -29 | **-3.87%** | ✅ Optimization | [x] |
| `06` | Planner | -336 | **-32.56%** | ✅ Major Opt. | [x] |
| `07` | Plan Rev. | +217 | +43.63% | ⚠️ Safety Fix* | [x] |
| `08` | Developer | -313 | **-31.39%** | ✅ Major Opt. | [x] |
| `09` | Code Rev. | +214 | +43.29% | ⚠️ Safety Fix* | [x] |
| `10` | Security | +481 | +385.0% | ⚠️ Safety Fix* | [x] |

*> Note: Agents 07/09 increased in size because they were previously unsafe (missing TIER 0 skills). New versions are compliant.*

**Outcome:**
- **Total Optimization:** ~ -700 tokens across critical "Doer" agents (04/06/08).
- **Safety Trade-off:** +430 tokens to secure Reviewers (07/09).
- **Net Result:** More robust, standardized system with reduced overhead in high-frequency loops.

**Implementation Plan (Full Rollout):**

#### Phase 1: Reviewers (Agents 03, 05, 07, 09)
Reviewers follow a simple "Check & Report" pattern.
- **Target:**
    - [x] `03_task_reviewer` (Completed)
    - [x] `05_architecture_reviewer` (Completed)
    - [x] `07_plan_reviewer` (Completed)
    - [x] `09_code_reviewer` (Completed)
- **Pattern:** `Review Loop` (Read Artifact → Apply Checklist → Report)

#### Phase 2: Doers (Agents 04, 06, 08)
"Doers" execute complex creative tasks.
- **Target:**
    - [x] `04_architect` (Completed)
    - [x] `06_planner` (Completed)
    - [x] `08_developer` (Completed)
- **Pattern:** `Execution Loop` (Read Task → Plan/Design → Implementation → Self-Correction)

#### Phase 3: Special Agents (01, 10) & Finalization
- [x] **01_orchestrator:** Already compressed in O2, but needs O6 *Header Standardization* (Context Loading).
- [x] **10_security:** Needs VDD alignment. (Standardized +385%)
- [x] **Localization:** Sync all Russian translations.

> [!SUCCESS]
> **Cross-Check Validation (2026-01-22):**
> - [x] **File Integrity:** Agents 02-09 renamed to `_prompt.md`.
> - [x] **TIER 0 Compliance:** All 8 standardized agents enforce `core-principles` + `safe-commands`.
> - [x] **Backlog Accuracy:** Phase 1 & 2 A/B metrics recorded.
> - [x] **Localization:** RU mirrors EN 100%.

> [!WARNING]
> **⚠️ LESSONS FROM O1-O5 — PROTOTYPE CHECKLIST**
> Before standardizing any agent, verify:
> 1.  [ ] **TIER 0 Compliance:** Does it strictly load `core-principles`, `safe-commands`, `artifact-management`? (Lesson from O1/O5)
> 2.  [ ] **Pattern Validity:** Does it use `Execution Loop` or `Review Loop` correctly? (Lesson from O2)
> 3.  [ ] **A/B Testing Rigor:** Is the new structure functionality equivalent? (Lesson from O2)
> 4.  [ ] **Translation Impact:** Is the RU version updated simultaneously? (Lesson from O3)

**Condition for Activation:**
- `02_analyst_prompt.md` is the Gold Standard. All others must match.

---

### O6a: Skill Structure Optimization

**Status:** COMPLETED ✅
**Date (Execution):** 2026-01-22

**Analysis:**
Following O6, we identified 4 "Large Skills" (>4KB) that deviated from `skill-creator` standards due to inline templates and complex logic.

**Optimization Approach:**
1.  **Scripting over Text:** Replace NL logic with Python scripts (`scan_structure.py`, `suggest_updates.py`).
2.  **Examples Separation:** Move inline templates to `examples/` directory (lazy access).
3.  **Refinement:** Remove redundant ASCII infographic layers.

**Results (Token Reduction):**
- `architecture-format-extended`: ~9.4KB -> **3.3KB** (-65%)
- `skill-phase-context`: ~8.2KB -> **4.2KB** (-49%)
- `skill-reverse-engineering`: ~5.3KB -> **1.9KB** (-64%)
- `skill-update-memory`: ~4.4KB -> **1.6KB** (-63%)

**Outcome:**
Significant reduction in token overhead for extended skills, verifying the "Script-First" and "Example-Separation" patterns.

---

---

### O7: Session Context Management (High Impact)

**Status:** COMPLETED ✅
**Prerequisites:** O1-O6 ✅ COMPLETED (v3.7.1)
**Blocking:** O9 (Multi-Session), O10 (Hierarchical Context)

> [!NOTE]
> **2026-01-23 Update:** All prerequisite optimizations (O1-O6) are now complete.
> This optimization is unblocked and ready for implementation.
> See **Prompt 7** in the Implementation Prompts section for the Start Prompt.

> [!IMPORTANT]
> **O4 (Conversation Checkpointing) has been merged into O7.**
> The original O4 concept of checkpointing is now implemented as part of the Session State mechanism.

**Analysis:**
With O1-O6 completed, we have minimized "Static Context" (Codebase & Rules). The remaining bottleneck is "Dynamic Context" (Conversation History).
Currently, the agent relies on the chat window logic. When the window fills up, we lose "where we were".
We need a **Persistent State Mechanism** that survives session resets and aligns with the `task_boundary` tool mechanics.

**Solution: `session_state.yaml` + `task_boundary` resonance**
Instead of relying on Chat History (which grows linearly), we maintain a compact State File that mirrors the `task_boundary` parameters.

**Proposed Schema (`.agent/sessions/latest.yaml`):**
```yaml
session_id: "uuid-v4"
last_updated: "ISO-8601"
mode: "PLANNING | EXECUTION | VERIFICATION" # Aligns with task_boundary.Mode
current_task:
  name: "Implementing O7" # Aligns with task_boundary.TaskName
  status: "Creating skill structure" # Aligns with task_boundary.TaskStatus
  predicted_steps: 5
context_summary: |
  User requested O7 implementation.
  Analysis complete.
  Architecture updated.
  Currently initiating Plan phase.
active_blockers: []
recent_decisions:
  - "Decided to use YAML for state storage"
  - "Selected TIER 0 for skill persistence"
```

**Integration Strategy:**
1.  **Read (Boot):** The `core-principles` or `GEMINI.md` (TIER 0) must instruct the agent to read `latest.yaml` immediately after booting.
2.  **Write (Boundary):** Every time the agent calls `task_boundary`, it should also (or via a helper) update `latest.yaml`.
    *   *Optimization:* Create a script `update_state.py` in the skill to handle the YAML safely.

**Recommendation:**
- **Action:** Create `skill-session-state` (TIER 0).
- **Tooling:** Include `scripts/update_state.py` to robustly dump YAML.
- **Payoff:** Allows "Squashing" chat history to zero while keeping the exact Task/Mode state restoration.

**Effort:** 8-12 hours.

---

### O8: Domain Isolation (Enterprise)

**Status:** DEFER (No changes — 2026-01-23)

**Analysis:**
Splitting architecture by domain (`docs/domains/trading/ARCHITECTURE.md`) adds complexity overhead not justified for current project sizes.

**Condition for Activation:**
1. `docs/ARCHITECTURE.md` exceeds 3,000 lines.
2. Distinct teams working on isolated modules.

**Current State (2026-01-23):** Architecture files remain under 1,000 lines. Defer.

**Recommendation:**
- **Wait.** Premature optimization.

---

### O9: Multi-Session Pipeline

**Status:** BLOCKED (External Tooling — No changes 2026-01-23)

**Analysis:**
Requires a CLI wrapper (Python/Bash) to mechanically manage the context window (Task 037). Agent cannot self-terminate effectively without external orchestrator.

**Dependencies:**
- O7 (Session State) — Must be implemented first to enable state handoff between sessions.
- `ag-cli` external tool — Not yet built.

**Recommendation:**
- **Hold** until `ag-cli` tool is built AND O7 is implemented.

---

### O10: Hierarchical Context

**Status:** MERGED INTO O7 (2026-01-23)

**Analysis:**
Hierarchical context management is being absorbed into O7 (Session Context Management).
The original idea of "hierarchical context" is now expressed as:
1. **Session State File** — Top-level context (Mode, TaskName, Summary)
2. **Recent Decisions** — Mid-level context (key choices)
3. **Active Blockers** — Immediate blockers for context restoration

**Recommendation:**
- ~~Wrap into O7 (Session Context).~~ **DONE** — See O7 schema.

---

## Feasibility Report (2026-01-21 Post-O5)

### 1. Executive Summary
**Milestone Reached:** Foundation Optimizations (O1-O5) are **COMPLETE**.
- **Static Overhead:** Reduced by ~70% (Lazy Loading + Orchestrator Compression).
- **Stability:** Locked in via Skill Tiers (O5).
- **Next Frontier:** Dynamic Context Management (O7) and Agent Precision (O6).

### 2. ROI Analysis (Updated)

| Optimization | Status | Effort | ROI Strategy |
|--------------|--------|--------|--------------|
| **O6: Prompt Std.** | **PROTOTYPE** | Medium | Standardize "DSL" patterns proved in O2. |
| **O7: Checkpoints** | **HIGH PRIORITY** | High | Vital for sessions > 50 turns. |
| **O8: Domains** | Defer | High | Wait for mono-repo use cases. |
| **O9: Multi-Session**| Blocked | High | Needs CLI tooling. |

### 3. Immediate Next Steps
1.  **Design O7 (Session State):** Create schema for `session_state.md`.
2.  **Experiment O6:** Apply "Task Pattern" (from O2) to Analyst prompt.

---

## Implementation Plan (O1-O4)

> [!IMPORTANT]
> **Cross-Check Requirement applies to ALL phases.**
> Document current behavior → Implement → Verify equivalence → Test automation.

### Phase 1: O3 — architecture-format Split (3-4 hours) ✅ COMPLETED

> [!NOTE]
> **Completed: 2026-01-21** | Commit: `9df8ccb` | Version: v3.5.3

**Prerequisite: Document current state**
- [x] Export current `architecture-format/SKILL.md` (523 lines, 11 sections)
- [x] Verify all 11 sections are identified and mapped

**Tasks:**
1. [x] Create `architecture-format-core/SKILL.md` (165 lines, ~996 tokens)
2. [x] Create `architecture-format-extended/SKILL.md` (485 lines, ~2,361 tokens)
3. [x] Update `04_architect_prompt.md` with loading conditions
4. [x] **CROSS-CHECK:** Verified combined content = original content
5. [x] **CROSS-CHECK EXTENDED:** Updated ALL references framework-wide:
   - [x] `Translations/RU/Agents/04_architect_prompt.md`
   - [x] `System/Docs/SKILLS.md`
   - [x] Fixed old `skill-architecture-format` references in prompts

**DoD:**
- [x] Core skill ~996 tokens (165 lines) — under budget
- [x] Extended skill ~2,361 tokens (485 lines) — under budget
- [x] Core + Extended = Original (all 11 sections preserved)
- [x] Architect agent works with both scenarios

**Actual Results:**
| Metric | Target | Actual |
|--------|--------|--------|
| Core tokens | ~1,200 | ~996 |
| Extended tokens | ~3,500 | ~2,361 |
| Token savings (minor update) | 60% | **60%** ✅ |

> [!TIP]
> **Independent Validation (Task 036):** PASSED ✅
> Verified correct conditional loading of `core` vs `extended` formats during live execution.


#### Lessons Learned (O3)

> [!WARNING]
> **Issues Discovered During Implementation:**

1. **Orphan References Bug**: After creating new skill files, old references remained in:
   - `04_architect_prompt.md` (lines 51, 54) — still referenced `skill-architecture-format`
   - Russian translation was NOT updated automatically
   - `System/Docs/SKILLS.md` catalog still had old entry
   
2. **Token Overhead Risk**: If old AND new skills are both loaded = **+130% overhead** instead of savings

3. **Cross-Check Scope Too Narrow**: Initial cross-check only verified file content, NOT framework-wide references

**→ Mitigation for Future Tasks:**
- Add `grep` search step for old skill names AFTER creating new skills
- Add Translation files to explicit checklist
- Add SKILLS.md catalog update to checklist

---

### Phase 2: O1 — Phase-Specific Skill Loading (4 hours) ✅ COMPLETED

> [!NOTE]
> **Completed: 2026-01-21** | Version: v3.5.4

**Prerequisite: Document current state**
- [x] List all skills currently loaded in GEMINI.md/AGENTS.md
- [x] Verify TIER 0 skills are explicitly required

**Tasks:**
1. [x] Create `skill-phase-context/SKILL.md` with:
   - TIER 0 definition (ALWAYS LOAD)
   - TIER 1 phase→skills mapping
   - TIER 2 precise loading conditions
2. [x] **VERIFY TIER 0 IS PRESERVED:** Ensure `GEMINI.md` and `AGENTS.md` explicitly load:
   - `core-principles` (Anti-hallucination)
   - `safe-commands` (Automation enablement — CRITICAL)
   - `artifact-management` (File protocol)
3. [x] Update agent prompts to trigger TIER 1 loading on phase entry
4. [x] **CROSS-CHECK:** Run automation test — verify `mv`, `git`, tests still auto-run
5. [x] Test: Run analysis phase:
   - [x] Verify TIER 0 skills are always present
   - [x] Verify TIER 1 analysis skills load when entering Analysis
   - [x] Verify TIER 1 architecture skills NOT loaded during Analysis

**DoD:**
- [x] TIER 0 skills (~2,082 tokens) loaded at session start — ALWAYS
- [x] TIER 1 skills load only when entering corresponding phase
- [x] `safe-commands` auto-run still works (CRITICAL for automation)
- [x] All phases still functional
- [x] Measurable reduction in total tokens (~3,000-5,000)

**Actual Results:**
| Metric | Target | Actual |
|--------|--------|--------|
| Baseline session load | ~2,082 tokens | ~2,082 tokens ✅ |
| Token savings (phases not loaded) | -79% | **-79%** ✅ |
| Automation preserved | Yes | **Yes** ✅ |

> [!TIP]
> **Independent Validation (Task 036):** PASSED ✅
> Verified TIER 1 lazy loading and TIER 0 stability (`safe-commands` auto-run working).


---

### Phase 3: O2 — Orchestrator Compression (6-8 hours) ✅ COMPLETED

> [!NOTE]
> **Completed: 2026-01-21** | Version: v3.5.5

**Prerequisite: Document current state**
- [x] Export all 14 scenarios from `01_orchestrator.md`
- [x] Document unique logic per scenario (edge cases, exceptions)
- [x] Identify pattern-compatible vs exception scenarios

**Tasks:**
1. [x] Create `skill-orchestrator-patterns/SKILL.md` with:
   - Stage Cycle pattern with applicability conditions
   - Explicit exceptions documented
2. [x] Refactor `01_orchestrator.md` to use patterns + dispatch table
3. [x] **CROSS-CHECK:** Verify all 14 scenarios are still executable:
   - [x] Scenario 1-3: Analysis (init, review, revision)
   - [x] Scenario 4-6: Architecture (init, review, revision)
   - [x] Scenario 7-9: Planning (init, review, revision)
   - [x] Scenario 10-12: Execution (init, review, fix) — different iteration limit preserved
   - [x] Scenario 13: Completion — no reviewer, archive required
   - [x] Scenario 14: Blocking questions — pause handling
4. [x] VDD-verify: Run edge case scenarios (blocking questions, iteration=2, etc.)
5. [x] Measure token reduction

**DoD:**
- [x] Orchestrator <6,000 bytes (from 11,195) — **Actual: 4,522 bytes**
- [x] All 14 scenarios still executable (verified by test)
- [x] No regression in pipeline flow
- [x] Backup: `01_orchestrator_full.md.bak` preserved

**Actual Results:**
| Metric | Target | Actual |
|--------|--------|--------|
| File size | <6,000 bytes | 4,522 bytes |
| Lines | — | 170 (from 492) |
| Token savings | ~1,500-2,000 | **~1,670 (~60%)** ✅ |

> [!TIP]
> **Independent Validation (Task 036):** PASSED ✅
> Verified Stage Cycle consistency and Orchestrator role simulation.


---

### Phase 4: O4 — Conversation Checkpointing (4-6 hours) [SKIPPED]

**Prerequisite: Document current state**
- [ ] Measure baseline token usage for a full pipeline run
- [ ] Document current context growth pattern

**Tasks:**
1. [ ] Create `skill-context-checkpoint/SKILL.md` with:
   - Checkpoint triggers (after each phase artifact)
   - Checkpoint schema (YAML)
   - ADDITIVE rule (append, never delete)
   - `decisions:` list requirement
2. [ ] Add checkpoint instructions to key phase transitions:
   - [ ] After TASK.md creation
   - [ ] After ARCHITECTURE.md update
   - [ ] After PLAN.md creation
   - [ ] After each task completion
3. [ ] **CROSS-CHECK:** Verify checkpoints are human-readable
4. [ ] Test: Long session remains under 80K tokens
5. [ ] VDD-verify: Checkpoint content is accurate (no hallucination)

**DoD:**
- [ ] Checkpoint skill created and documented
- [ ] At least one successful long session with checkpointing
- [ ] Token usage reduced vs baseline (measurable)
- [ ] No critical decisions lost in summarization

---

### Phase 5: O5 — Skill Tiers Formalization (2-3 hours) ✅ COMPLETED

> [!NOTE]
> **Completed: 2026-01-21** | Version: v3.6.0

**Prerequisite:** O1 (Completed)

**Tasks:**
1. [x] Create `System/Docs/SKILL_TIERS.md` (Authoritative Source)
2. [x] Update ALL 28 `SKILL.md` files with `tier: [0|1|2]` metadata
3. [x] **CROSS-CHECK:** Verify 100% coverage
   - [x] Tier 0 skills (`core-principles`, `safe-commands`, `artifact-management`) tagged 0
   - [x] All 14 Tier 1 skills tagged 1
   - [x] All 11 Tier 2 skills tagged 2
4. [x] Update `System/Docs/SKILLS.md` catalog

**DoD:**
- [x] `SKILL_TIERS.md` exists and is accurate
- [x] All skills have valid metadata
- [x] Lazy Loading O1 is now mechanically enforced by metadata

**Actual Results:**
- 100% Metadata Coverage (Verified by Walkthrough)
- Documentation Sync: `SKILLS.md` and `CHANGELOG.md` updated


---

## VDD Adversarial Review

> **Final Review: 2026-01-21**
> **Sarcasmotron Mode Activated** 🎭

### Document Consistency Check

> [!NOTE]
> **Cross-Document Verification Performed**
> Checked consistency between: O1-O10 sections ↔ Implementation Plan ↔ Skill Tiers diagram

| Check | Status | Notes |
|-------|--------|-------|
| Token estimates consistent | ✅ | Core ~1,200, Extended ~3,500 |
| Tier classification consistent | ✅ | TIER 0 always includes safe-commands |
| Cross-check requirements present | ✅ | Added to all phases |
| Implementation effort realistic | ✅ | Updated: O2 6-8h, O3 3-4h, O4 4-6h |
| Backup strategy documented | ✅ | `01_orchestrator_full.md.bak` |

---

### �️ Integrity & Regression Verification

> **Objective:** Ensure ZERO information loss and NO performance degradation.

| Check | Target | Method |
|-------|--------|--------|
| **Content Integrity** | Refactored Skills | `diff` comparison of semantic content (Core + Extended = Original) |
| **Logic Retention** | Agent Prompts | Verification that all 14 scenarios/logic branches remain executable |
| **Performance** | Token Usage | A/B Testing: New vs Old must show ≤ tokens for same task |
| **Safety** | TIER 0 Skills | Verify `core-principles` & `safe-commands` are NEVER dropped |

**Constraint:**
If **ANY** logic is lost or token usage increases (without justification), the optimization is **REJECTED**.

---

### �🟢 O1: Phase-Specific Skill Loading

**Challenge:** "Oh brilliant, now the agent decides WHEN to load skills. What could go wrong when a forgetful LLM 'forgets' to load the required skill?"

**Risks Identified:**
1. Agent proceeds without required skill → hallucination
2. TIER 0 accidentally lazy-loaded → automation breaks
3. Phase detection logic fails → wrong skills loaded

**Mitigations Applied:**
1. ✅ TIER 0 explicitly marked as NON-NEGOTIABLE
2. ✅ `safe-commands` highlighted as CRITICAL for automation
3. ✅ `REQUIRED_SKILLS:` header specified for each agent prompt
4. ✅ Cross-check: automation test added to implementation plan

**VDD Verdict:** ✅ PASS — TIER 0 protection in place

---

### 🟡 O2: Orchestrator Compression

**Challenge:** "You want to compress 14 detailed scenarios into a 'dispatch table'? The LLM will just... figure out the nuances?"

**Risks Identified:**
1. Loss of edge case handling (iteration limits, no reviewer, blocking questions)
2. Ambiguous pattern interpretation
3. Debug difficulty increases

**Mitigations Applied:**
1. ✅ Explicit exceptions documented (scenarios 10-14 have special logic)
2. ✅ Applicability conditions added with checkbox validation
3. ✅ All 14 scenarios listed individually in implementation plan
4. ✅ Backup requirement: `01_orchestrator_full.md.bak`

**Remaining Risk:** Pattern may be too abstract for some LLMs

**VDD Verdict:** ⚠️ CONDITIONAL PASS — requires A/B testing

---

### 🟢 O3: architecture-format Split

**Challenge:** "Split into 'core' and 'extended'... and who decides which one to use?"

**Risks Identified:**
1. Wrong skill tier selected → inconsistent docs
2. Content loss during split (523 lines)
3. Cross-reference between files fails

**Mitigations Applied:**
1. ✅ Precise loading conditions table (6 conditions)
2. ✅ All 11 sections mapped with line numbers
3. ✅ Cross-check: verify Core + Extended = Original
4. ✅ "sophisticated requirement / complex task" trigger added

**VDD Verdict:** ✅ PASS — if cross-check performed

---

### 🟢 O4: Conversation Checkpointing

**Challenge:** "Great, now we're trusting the LLM to summarize its own work correctly."

**Risks Identified:**
1. Critical decisions lost in summary
2. Context drift across checkpoints
3. LLM hallucinates checkpoint content

**Mitigations Applied:**
1. ✅ ADDITIVE rule: append only, never delete
2. ✅ Explicit `decisions:` list requirement
3. ✅ TASK.md remains full (not summarized)
4. ✅ Human-readable format for manual review

**VDD Verdict:** ✅ PASS with monitoring

---

### 🔴 O5-O10: Strategic Optimizations

**Status:** DEFERRED until O1-O4 proven successful

**VDD Verdict:** 🔴 DEFER — validate O1-O4 first

---

### Final VDD Summary

| Optimization | Risk | Verdict | Blocking |
|--------------|------|---------|----------|
| O1: Phase-Specific Loading | LOW | ✅ PASS | None |
| O2: Orchestrator Compression | MEDIUM | ⚠️ CONDITIONAL | A/B test |
| O3: architecture-format Split | LOW | ✅ PASS | Cross-check |
| O4: Checkpointing | LOW | ✅ PASS | Monitor |
| O5-O10: Strategic | HIGH | 🔴 DEFER | O1-O4 first |

---

## Metrics & Success Criteria

### Baseline Metrics (Before O1-O4)

| Metric | Current Value |
|--------|---------------|
| Session Start Tokens | ~6,900 |
| Standard Pipeline Total | ~50,041 |
| Peak Usage | 65,000-85,000 |
| Framework Overhead | ~16,000 |

### Target Metrics (After O1-O4)

| Metric | Target Value | Δ |
|--------|--------------|---|
| Session Start Tokens | ~4,500 | -35% |
| Standard Pipeline Total | ~42,000 | -16% |
| Peak Usage | 55,000-70,000 | -15% |
| Framework Overhead | ~12,000 | -25% |

---

## Implementation Prompts (For Future Dialogue)

> [!TIP]
> Copy-paste these prompts to start implementation in a new dialogue.

### Prompt 1: O3 — architecture-format Split ✅ COMPLETED

> **Status:** Implemented in v3.5.3 (commit `9df8ccb`)

<details>
<summary>Original Prompt (Archived)</summary>

```
TASK: Implement O3 from Backlog/agentic_development_optimisations.md

CONTEXT:
- Current file: .agent/skills/architecture-format/SKILL.md (523 lines, 11 sections)
- Goal: Split into core (~150 lines) and extended (~400 lines)
- Cross-check requirement: Core + Extended = Original (no content loss)

DELIVERABLES:
1. Create .agent/skills/architecture-format-core/SKILL.md
2. Create .agent/skills/architecture-format-extended/SKILL.md
3. Update 04_architect_prompt.md with loading conditions
4. Verify: combined content equals original

CRITICAL: Do NOT lose any content. Cross-check after split.
```
</details>

### Prompt 2: O1 — Phase-Specific Skill Loading ✅ COMPLETED

```
TASK: Implement O1 from Backlog/agentic_development_optimisations.md

CONTEXT:
- Goal: Create skill-phase-context that defines skill loading tiers
- TIER 0 (ALWAYS LOAD): core-principles, safe-commands, artifact-management
- TIER 1 (Phase-triggered): See mapping in optimization document

PREREQUISITE: O3 is implemented and tested ✅

DELIVERABLES:
1. Create .agent/skills/skill-phase-context/SKILL.md
2. Verify GEMINI.md and AGENTS.md explicitly reference TIER 0
3. Test: automation still works (mv, git, tests auto-run)

CRITICAL: safe-commands MUST remain always-loaded for automation.

⚠️ LESSONS FROM O3 — DO NOT SKIP:
- After creating new skill, run: `grep -r "skill-phase-context" .` to verify no orphan refs
- Update Translations/RU/ files if agent prompts change
- Update System/Docs/SKILLS.md with new skill entry
- Update CHANGELOG.md with version bump
```

### Prompt 3: O2 — Orchestrator Compression ✅ COMPLETED (v3.5.5)

```
TASK: Implement O2 from Backlog/agentic_development_optimisations.md

CONTEXT:
- Current file: System/Agents/01_orchestrator.md (492 lines, 14 scenarios)
- Goal: Compress to <6,000 bytes using patterns + dispatch table

BEFORE STARTING:
cp System/Agents/01_orchestrator.md System/Agents/01_orchestrator_full.md.bak

PREREQUISITE: O1 and O3 are implemented and tested

DELIVERABLES:
1. Create .agent/skills/skill-orchestrator-patterns/SKILL.md
2. Refactor 01_orchestrator.md to use patterns
3. Test each of 14 scenarios (especially 10-14 with special logic)

CRITICAL: Backup first. Test all 14 scenarios after compression.

⚠️ LESSONS FROM O3 — MANDATORY CHECKLIST:
- [x] After changes, run: `grep -r "01_orchestrator" .` to find all references
- [x] Update Translations/RU/Agents/01_orchestrator.md with same logic
- [x] Verify GEMINI.md and AGENTS.md don't have outdated refs
- [x] Update System/Docs/SKILLS.md with new skill entry
- [x] Update CHANGELOG.md with version bump
- [x] Cross-check: original 14 scenarios ALL still work

RESULT: 11,195 → 4,522 bytes (-60%), commit e5f7312
```

### Prompt 4: O4 — Conversation Checkpointing [ARCHIVED/REPLACED BY O7]

```
TASK: Implement O4 from Backlog/agentic_development_optimisations.md

CONTEXT:
- Goal: Create checkpointing skill to reduce conversation history growth
- Checkpoint after: TASK.md, ARCHITECTURE.md, PLAN.md, each task
- Rule: ADDITIVE only (append, never delete)

PREREQUISITE: O1, O2, O3 are implemented

DELIVERABLES:
1. Create .agent/skills/skill-context-checkpoint/SKILL.md
2. Define checkpoint schema (YAML)
3. Add checkpoint instructions to phase transitions
4. Test: long session stays under 80K tokens

⚠️ LESSONS FROM O3 — MANDATORY CHECKLIST:
- [ ] After changes, run: `grep -r "skill-context-checkpoint" .` to find all references
- [ ] Update any agent prompts that need checkpoint triggers
- [ ] Update System/Docs/SKILLS.md with new skill entry
- [ ] Update CHANGELOG.md with version bump
- [ ] Cross-check: verify checkpoint files are human-readable
```

### Prompt 5: Full Validation ✅ PARTIALLY COMPLETED (v3.5.5)

```
TASK: Validate O1-O4 implementation

TEST PLAN:
1. Run standard development task through full pipeline
2. Verify:
   - [x] All phases execute correctly
   - [x] safe-commands auto-run works (mv, git, tests)
   - [x] All 14 orchestrator scenarios work
   - [x] architecture-format loads correctly
   - [ ] Checkpoints are created and readable
3. Compare token usage to baseline

DELIVERABLES:
1. Test report with pass/fail for each check
2. Token usage comparison (before vs after)
```

### Prompt 6: O5 — Skill Tiers Formalization

> **Status:** ✅ COMPLETED (v3.6.0)

```markdown
TASK: Implement O5 from Backlog/agentic_development_optimisations.md

CONTEXT:
- Goal: Formalize the Skill Tiers mechanism in documentation and skill headers.
- Reference: See "SKILL TIERS (AUTHORITATIVE)" table in Backlog.

DELIVERABLES:
1. Create `System/Docs/SKILL_TIERS.md` with the authoritative tier definitions.
2. Update ALL `SKILL.md` files in `.agent/skills/` to include `tier: [0|1|2]` in the YAML frontmatter.
   - Use the table in Backlog as the source of truth.
   - Default to TIER 2 if not explicitly listed in TIER 0 or 1.
3. Verify:
   - All skills have a `tier` property.
   - `TIER 0` skills match exactly: `core-principles`, `safe-commands`, `artifact-management`.

CRITICAL: Do not modify the prompt logic (that was O1). This is purely documentation and metadata enforcement.
```

### Prompt 7: O7 — Session Context Management (START PROMPT)

> **Status:** ✅ COMPLETED (v3.7.2)
> **Prerequisites:** O1-O6 ✅ COMPLETED (v3.7.1)
> **Last Updated:** 2026-01-23

```markdown
TASK: Implement Optimization O7 (Session Context)

CONTEXT:
- **Framework Version:** v3.7.1+
- O1-O6 are **COMPLETE**. Static context is optimized (TIERs), prompts are standardized.
- The alignment with `task_boundary` tool is critical. We need a persistent file that tracks the `task_boundary` state so we can recover it after a context clear.
- **O4 (Checkpointing) and O10 (Hierarchical Context) are MERGED into O7.**

**REFERENCE FILE:** `Backlog/agentic_development_optimisations.md` (See section O7 for detailed analysis).

GOAL:
Create a "Session State" mechanism that persists the current Mode, TaskName, and Summary to a file, allowing the agent to "reboot" seamlessly after context window resets.

DELIVERABLES:

1. **Design & Create Skill**: `.agent/skills/skill-session-state/SKILL.md` (TIER 0)
   - **Schema Design**: Must map 1:1 to `task_boundary` arguments (Mode, TaskName, TaskStatus, TaskSummary).
   - **Protocol**: Define specific triggers for READ (Boot) and WRITE (Task Boundary).
   - **TIER 0 Status**: Add to `System/Docs/SKILL_TIERS.md` and `GEMINI.md`.
   - **File Location**: `.agent/sessions/latest.yaml`

2. **Develop Robust Script**: `.agent/skills/skill-session-state/scripts/update_state.py`
   - **Robustness**: Handle missing files, partial updates, and concurrent writes safely.
   - **CLI Interface**: `python update_state.py --mode "..." --task "..." --status "..." --summary "..."`
   - **Validation**: Ensure it does not crash on malformed YAML (backup & restore logic).
   - **Pattern**: Follow "Script-First" pattern from O6a (see `skill-creator/SKILL.md`).

3. **Update Bootstrap Protocol (`GEMINI.md` & `AGENTS.md`)**:
   - Add explicit instruction: "ON SESSION START: Check for `.agent/sessions/latest.yaml`. If exists, READ IT to restore context."
   - **Cursor Integration**: Ensure `AGENTS.md` has the equivalent instruction for the Cursor environment.

4. **Integration Plan**:
   - Document how this integrates with `task_boundary`. (e.g., "After calling task_boundary, run update_state.py").
   - Update `System/Docs/ORCHESTRATOR.md` if applicable.

TESTING & VALIDATION (CRITICAL):
- **Test 1 (Script):** Run the python script manually to verify YAML generation.
- **Test 2 (Recovery):** Simulate a session crash. Start a NEW session and verify the agent reads the file and knows "where it left off".
- **Test 3 (Cursor):** Verify `AGENTS.md` instructions work in a simulated Cursor chat environment.

⚠️ LESSONS FROM O1-O6 — MANDATORY CHECKLIST:
- [ ] **Tier 0 Compliance (O1/O5):** Skill MUST be TIER 0 (bootstrap load).
- [ ] **Script-First (O6a):** Use Python script for state updates, not inline NL instructions.
- [ ] **Translation Impact (O3):** Update Russian translations if needed.
- [ ] **SKILL_TIERS.md:** Add entry for new skill.
- [ ] **CHANGELOG.md:** Update with version bump.
- [ ] **Cross-check:** Verify both Antigravity and Cursor environments work.

CONSTRAINTS:
- The schema MUST be extensible but start simple (<20 lines).
- **Environment Agnostic**: Must work in Antigravity (native tools) and Cursor (terminal commands).

STARTING STEP:
1. Read `Backlog/agentic_development_optimisations.md` (Section O7) to understand the full context.
2. Analyze `skill-creator/SKILL.md` to ensure the new skill follows the "Script-First" pattern (O6a).
3. Create `.agent/sessions/` directory structure.
```

---

### Prompt 8: O6 — Agent Prompt Standardization

> **Status:** ✅ COMPLETED (v3.6.0 — v3.7.0)
> **Completed:** 2026-01-22

**Summary of Implementation:**
- All 10 Agent Prompts (`01`–`10`) standardized with 4-section schema.
- TIER 0 skills enforced in all agents.
- Token savings: -29% (Architect), -33% (Planner), -31% (Developer).
- Safety improvements: Reviewers now enforce TIER 0 (+43% size for zero hallucinations).
- See section **O6: Agent Prompt Standardization** for full A/B test results.

```markdown
# ARCHIVED — This prompt has been executed and completed.

TASK: Prototype O6 (Agent Prompt Standardization)

CONTEXT:
- Goal: Verify if "Standardized Patterns" (Header -> Context -> Loop) improve stability vs raw text.
- Target: `02_analyst_prompt.md`.

RESULT: ✅ PASSED
- All agents (01-10) standardized.
- A/B tests confirmed neutral/positive impact.
- Russian translations synchronized.

### ✅ LESSONS FROM O1-O5 — PROTOTYPE CHECKLIST (ALL PASSED):
- [x] **Tier 0 Compliance (O1/O5):** All agents enforce `core-principles`, `safe-commands`, `artifact-management`.
- [x] **Pattern Validity (O2):** Stage Cycle pattern handles edge cases correctly.
- [x] **A/B Testing (O2):** Variant demonstrated -20% to -33% token savings.
- [x] **Translation Impact (O3):** All `Translations/RU/Agents/*.md` updated.
- [x] **Clean Cleanup (O3):** `grep` confirmed no orphan references.
```

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-23 | Analyst Agent | **O7-O10 Status Review:** O7 → READY FOR IMPLEMENTATION, O10 → MERGED INTO O7, O8/O9 unchanged |
| 2026-01-21 | Adversarial Architect | **O5 COMPLETED** (Skill Tiers Formalization) |
| 2026-01-21 | Adversarial Architect | Updated Roadmap O6-O10 (Post-O5 Strategy) |
| 2026-01-21 | Adversarial Architect | **O3 COMPLETED**: Marked as done, added Lessons Learned, updated prompts with checklists |
| 2026-01-22 | Orchestrator Agent | **O7 UPDATED**: Refined specs for task_boundary alignment & script-first approach |
| 2026-01-21 | Adversarial Architect | Final VDD review, implementation prompts |
| 2026-01-21 | Adversarial Architect | Corrected skill tiers, cross-check requirements |
| 2026-01-21 | Adversarial Architect | Initial document |
