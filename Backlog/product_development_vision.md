# Product Development Vision

> **Status:** VDD-Reviewed Vision Document
> **Created:** 2026-01-21
> **Purpose:** Target architecture for enterprise product development extension

---

## Table of Contents

- [Vision Statement](#vision-statement)
  - [Goals](#goals)
  - [Non-Goals](#non-goals)
- [Core Principles](#core-principles)
  - [1. Artifact-Centric Architecture](#1-artifact-centric-architecture)
  - [2. Sequential Sessions (Not Parallel Agents)](#2-sequential-sessions-not-parallel-agents)
  - [3. VDD at Every Level](#3-vdd-at-every-level)
  - [4. Token Budget Awareness](#4-token-budget-awareness)
- [Target Architecture](#target-architecture)
  - [Phase Model](#phase-model)
  - [Isolation & Handoff Strategy](#isolation--handoff-strategy)
  - [Artifact Flow](#artifact-flow)
- [Agent Model](#agent-model)
  - [New Agents (Minimal Set)](#new-agents-minimal-set)
  - [Rejected Agents](#rejected-agents)
- [Skills & Workflows](#skills-workflows)
  - [New Skills](#new-skills)
  - [New Workflows](#new-workflows)
- [Folder Structure](#folder-structure)
- [Detailed Implementation Plan](#detailed-implementation-plan)
  - [Prerequisites](#prerequisites)
  - [Phase 0: Product Bootstrap & Tools](#phase-0-product-bootstrap--tools-week-1)
  - [Phase 1: The Refinement Loop](#phase-1-the-refinement-loop-week-2)
  - [Phase 2: Standalone Mode](#phase-2-standalone-mode-startupsrfp-week-3)
  - [Phase 3: Technical Integration](#phase-3-technical-integration-week-4)
- [VDD Review](#vdd-review)
  - [Challenge 1: Business Metrics](#challenge-1-business-metrics-are-hard-to-verify)
  - [Challenge 3: Complexity](#challenge-3-another-layer-more-complexity)
  - [Challenge 4: Token Budget](#challenge-4-token-budget-will-be-exceeded)
- [Open Questions](#open-questions)
  - [Resolved](#resolved-by-this-document)
  - [Still Open](#still-open)
- [Future Initiatives (Phase 3+)](#future-initiatives-phase-3)
- [Changelog](#changelog)

---

## Vision Statement

Расширить фреймворк Agentic-Development для поддержки **бизнес-ориентированного планирования продуктов** с минимальным overhead и максимальной устойчивостью к галлюцинациям.

### Goals

1. **Business Layer Integration** — добавить Product Analysis фазу перед техническим pipeline
2. **Artifact-Centric Communication** — агенты общаются через файлы, не через "оркестрацию"
3. **Near-Zero Hallucinations** — VDD на каждом уровне, включая бизнес-артефакты

### Non-Goals

- ❌ SAFe-style иерархия (PO → Orchestrator → Coordinator)
- ❌ Real-time параллелизм агентов (невозможен в текущих IDE)
- ❌ External integrations (API, market data) — Phase 3+
- ❌ Замена текущего фреймворка — extension, не rewrite

---

## Core Principles

### 1. Artifact-Centric Architecture

> **Ключевой инсайт:** Агенты не общаются напрямую. Они общаются через артефакты.

```
User Request
     │
     ▼
┌─────────────────┐
│ PRODUCT_VISION  │ ◄── Created by Product Analyst (Session 1)
│      .md        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PRODUCT_BACKLOG │ ◄── Created by Product Analyst (Session 1)
│      .md        │     Reviewed by Product Reviewer (Session 2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ APPROVED_BACKLOG│ ◄── Output of VDD Review
│      .md        │
└────────┬────────┘
         │
         ▼
   ┌─────┴─────┐
   │           │
   ▼           ▼
Domain 1    Domain 2    ◄── Standard Agentic Pipeline per domain
TASK.md     TASK.md
```

### 2. Sequential Sessions (Not Parallel Agents)

**Reality Check:**
- Cursor/Antigravity/VSCode = 1 LLM session at a time
- "Orchestrator" — это prompt, не процесс
- "Parallel pipelines" возможны только через:
  - Разные IDE instances
  - Человек переключается между доменами
  - Artifact-based async handoff

### 3. VDD at Every Level

```
User Input ─────┐
                │
                ▼
        ┌───────────────┐
        │ Product       │──────▶ VDD: "Is this achievable?"
        │ Analyst       │               "ROI realistic?"
        └───────────────┘               "Market validated?"
                │
                ▼
        ┌───────────────┐
        │ Product       │──────▶ VDD: "WSJF correct?"
        │ Reviewer      │               "Dependencies considered?"
        └───────────────┘               "Edge cases?"
                │
                ▼
        [ Standard Technical Pipeline with existing VDD ]
```

### 4. Token Budget Awareness

> [!IMPORTANT]
> Product Development phase adds overhead, but recent optimizations (O1-O4) have created room.
>
> **Revised Budget (v3.7+ Baseline):**
> - Standard Framework Overhead: ~12,000 tokens (down from 16k)
> - `p01_product_analyst.md`: MAX 2,500 tokens (Standardized)
> - `p02_product_reviewer.md`: MAX 2,000 tokens (Standardized)
> - `skill-product-analysis`: MAX 1,000 tokens (TIER 2 - Lazy Load)
> - `skill-backlog-prioritization`: MAX 500 tokens (Script-First approach)
>
> **Total Product Phase overhead: ~6,000 tokens (Optimized)**

---

## Target Architecture

### Phase Model

| Phase | Session | Agent | Input | Output |
|-------|---------|-------|-------|--------|
| 1. Vision Cycle | 1 | p01_Analyst + p02_Reviewer | User request | `APPROVED_VISION.md` |
| 2. Backlog Cycle | 2 | p01_Analyst + p02_Reviewer | Approved Vision | `APPROVED_BACKLOG.md` |
| **STOP** | **—** | **HUMAN** | **Approved Backlog** | **GO/NO-GO Decision** |
| 3. Planning| — | **HUMAN** | Decisions | Scope for Tech Implementation |
| 4. Handoff | 3 | Orchestrator | Human Scope | Domain `TASK.md` files |
| 5. Dev | 4+ | Standard Pipeline | `TASK.md` | Code |

### Isolation & Handoff Strategy

> [!IMPORTANT]
> **The "Air Gap" Principle**: Product Agents never call Development Agents directly.

```mermaid
graph TD
    subgraph "Stage 1: Vision Refinement"
        A[User Request] --> B(p01 Analyst)
        B -- Draft --> C[PRODUCT_VISION]
        C -- Review --> D(p02 Reviewer)
        D -- Feedback --> B
    end

    subgraph "Stage 2: Backlog Generation"
        D -- Approve --> E[APPROVED_VISION]
        E --> F(p01 Analyst)
        F -- Create --> G[PRODUCT_BACKLOG]
        G -- Review --> H(p02 Reviewer)
        H -- Feedback --> F
        H -- Approve --> I[APPROVED_BACKLOG]
    end

    I --> J{HUMAN GATE<br/>Strategic Decision}

    subgraph "Transition"
        J -- Approved --> K[HUMAN PLANNING<br/>Select Scope for Sprint]
        K -- Create Task --> L[Orchestrator Input]
    end

    subgraph "Agentic Development"
        L --> M(Standard Pipeline)
    end
```

### Artifact Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARTIFACT FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  docs/                                                                      │
│  ├── PRODUCT_VISION.md        # High-level vision (created Phase 1)        │
│  │   └── Sections:                                                          │
│  │       ├── Problem Statement                                              │
│  │       ├── Target Users                                                   │
│  │       ├── Success Metrics                                                │
│  │       └── Constraints                                                    │
│  │                                                                          │
│  ├── PRODUCT_BACKLOG.md       # Prioritized backlog (created Phase 2)      │
│  │   └── Sections:                                                          │
│  │       ├── Epics (WSJF-prioritized)                                       │
│  │       ├── Stories (INVEST-compliant)                                     │
│  │                                                                          │
│  ├── APPROVED_BACKLOG.md      # Starting point for Implementation           │
│  │   └── (Same structure as Backlog, but signed off)                        │
│  │                                                                          │
│  ├── TASK.md                  # Technical Scope (Manual Creation for now)   │
│  │   └── Derived from Approved Epics                                        │
│  │                                                                          │
│  └── domains/                 # (Future: Multi-domain split)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Model

### New Agents (Minimal Set)

#### p01_product_analyst.md

```markdown
# Product Analyst

## ROLE
Analyze user product requests and create structured backlog.

## ACTIVE SKILLS
- skill-product-analysis (REQUIRED)
- skill-backlog-prioritization (REQUIRED)
- TIER 0 SKILLS (MANDATORY):
  - core-principles
  - safe-commands
  - artifact-management
  - skill-session-state (O7)

## INPUT
- User product request
- PRODUCT_VISION.md (if exists, for updates)

## OUTPUT
1. PRODUCT_VISION.md — Vision document
2. PRODUCT_BACKLOG.md — Prioritized backlog

## PROCESS
1. **BOOTSTRAP**: Restore Session State (skill-session-state)
2. Read user request
3. IF PRODUCT_VISION.md exists → determine if UPDATE or NEW
4. Extract: Problem, Users, Metrics, Constraints
5. Create/Update PRODUCT_VISION.md
6. Breakdown vision into Epics → Stories
7. Prioritize using WSJF (`prioritize.py`)
8. Assign domains to stories
9. Create PRODUCT_BACKLOG.md
10. **UPDATE STATE**: Save session context

## TOKEN BUDGET: < 2,500 tokens
```

#### p02_product_reviewer.md

```markdown
## ROLE
Challenge product artifacts using adversarial analysis.

## ACTIVE SKILLS
- vdd-adversarial (REQUIRED)
- skill-backlog-prioritization (for verification)
- TIER 0 SKILLS (MANDATORY):
  - core-principles
  - safe-commands
  - artifact-management
  - skill-session-state

## INPUT
- PRODUCT_BACKLOG.md
- PRODUCT_VISION.md

## OUTPUT
- Review comments OR approval

## VDD CHECKLIST
1. [ ] Vision clear and achievable?
2. [ ] ROI/metrics measurable?
3. [ ] Epics properly decomposed?
4. [ ] Stories meet INVEST criteria?
5. [ ] WSJF priorities justified?
6. [ ] Domain assignments logical?
7. [ ] Dependencies identified?
8. [ ] Edge cases / risks documented?

## TONE
Use `vdd-sarcastic` approach:
- "So you expect 100x growth in 3 months? With what team?"
- "ROI based on 'market trends'? Which trends exactly?"

## TOKEN BUDGET: < 2,000 tokens
```

### Rejected Agents

| Original Proposal | Rejection Reason |
|-------------------|------------------|
| `p00_product_development.md` | Meta-prompt unnecessary — GEMINI.md handles bootstrap |
| `p01_product_orchestrator.md` | Orchestration via artifacts, not dedicated agent |
| `p04_product_architect.md` | Use existing `04_architect_prompt.md` with domain context |
| `p05_product_architecture_review.md` | Use existing `05_architecture_reviewer_prompt.md` |
| `01_module_coordinator.md` | Function covered by artifact structure |

---

## Skills & Workflows

### New Skills

> [!NOTE]
> All new skills must comply with **O5 Skill Tiers** (likely TIER 2) and **O6 Script-First** standards.

#### skill-product-analysis (TIER 2, MAX 1,000 tokens)

```markdown
# Product Analysis

## Vision Document Structure
- Problem Statement (50-100 words)
- Target Users (personas)
- Success Metrics (SMART)
- Constraints (time, budget, tech)

## Epic Breakdown
For each epic:
- Clear business goal
- Measurable outcome
- Rough scope estimate (T-shirt size: S/M/L/XL)

## Story Extraction
Apply INVEST:
- Independent
- Negotiable
- Valuable
- Estimable
- Small
- Testable
```

#### skill-backlog-prioritization (TIER 2, MAX 500 tokens)

```markdown
# Backlog Prioritization

## SCRIPT-FIRST STRATEGY
Instead of teaching LLM arithmetic, use `scripts/calculate_wsjf.py`.

## Usage
`python3 scripts/calculate_wsjf.py --file PRODUCT_BACKLOG.md`

## WSJF Logic (Implemented in script)
1. Parse table from markdown
2. Calculate WSJF = (BV + TC + RR) / JobSize
3. Sort items descending
4. Rewrite table in-place
```

```

### New Workflows

#### product-vision.md

```yaml
---
description: Create or update Product Vision and Backlog
---
1. Read docs/PRODUCT_VISION.md (if exists)
2. Load skill: skill-product-analysis
3. Execute p01_product_analyst
4. Create/Update docs/PRODUCT_VISION.md
5. Load skill: skill-backlog-prioritization
6. Create docs/PRODUCT_BACKLOG.md
7. Tool: `calculate_wsjf.py` (Auto-prioritize)
8. Notify user: "Vision and Backlog ready for review"
```

#### product-review.md

```yaml
---
description: VDD Review of Product Backlog
---
1. Read docs/PRODUCT_BACKLOG.md
2. Read docs/PRODUCT_VISION.md
3. Load skill: vdd-adversarial
4. Execute p02_product_reviewer
5. IF issues found:
   - Create review comments
   - Return to product-vision workflow
6. IF approved:
   - Rename to docs/APPROVED_BACKLOG.md
   - Proceed to domain-start workflow
```

```

---

## Folder Structure

```
project-root/
├── .gemini/GEMINI.md                    # Extended with product phase
├── .agent/
│   ├── skills/
│   │   ├── skill-product-analysis/       # NEW
│   │   ├── skill-backlog-prioritization/ # NEW
│   │   ├── skill-domain-decomposition/   # NEW
│   │   └── ... (existing skills)
│   └── workflows/
│       ├── product-vision.md             # NEW
│       ├── product-review.md             # NEW
│       ├── domain-start.md               # NEW
│       └── ... (existing workflows)
├── System/
│   └── Agents/
│       ├── p01_product_analyst.md        # NEW
│       ├── p02_product_reviewer.md       # NEW
│       └── ... (existing agents)
├── docs/
│   ├── PRODUCT_VISION.md                 # NEW: High-level vision
│   ├── PRODUCT_BACKLOG.md                # NEW: Prioritized backlog
│   ├── APPROVED_BACKLOG.md               # NEW: After VDD review
│   │
│   └── domains/                  # Future (See Phase 3+)
│       └── ...
```

---

## Integration Strategy

## Detailed Implementation Plan

### Prerequisites
- [ ] **O1-O7 Optimizations Complete**: System must be stable (v3.7+)
- [ ] **Script-First Infrastructure**: `scripts/` directory must be ready for new Product tools
- [ ] **Standalone Mode Support**: Ability to run agents without full project scaffolding (for RFPs/Startups)

### Phase 0: Product Bootstrap & Tools (Week 1)
**Goal**: Create infrastructure for generating `PRODUCT_VISION.md` and `PRODUCT_BACKLOG.md` from zero.

1. **Bootstrap Tools (Script-First)**:
   - `scripts/init_product.py`: Interactive CLI to scaffold `PRODUCT_VISION.md`.
     - Prompts user for: Problem, Persona, Goals, Constraints.
     - Generates markdown template with placeholders.
   - `scripts/calculate_wsjf.py`: Already defined (for Backlog).

2. **Skills Implementation**:
   - `skill-product-analysis`: TIER 2 skill, loaded only for product workflows.
   - `skill-backlog-prioritization`: Wrapper around `calculate_wsjf.py`.

3. **Agent Implementation (Standalone-Capable)**:
   - `p01_product_analyst.md`: Capable of running on empty folder (Greenfield).
   - `p02_product_reviewer.md`: Strict VDD logic.

### Phase 1: The Cascading Refinement Loop (Week 2)
**Goal**: Implement "Fail Fast" quality gates.

> [!TIP]
> **Efficiency**: Reviewing Vision *before* generating Backlog saves tokens. Don't write 50 stories for a flawed concept.

**Workflow: `/product-refine`**
```yaml
description: Two-Stage Refinement (Vision -> Backlog)
steps:
  1. Boot: Restore Session Context
  
  # STAGE 1: VISION
  2. Analyst: Generate `PRODUCT_VISION.md`
  3. LOOP (Vision):
     a. Reviewer: Check Vision (Goal/metrics/feasibility)
     b. If Reject -> Analyst fixes -> Retry
     c. If Approve -> Save `APPROVED_VISION.md` -> BREAK

  # STAGE 2: BACKLOG
  4. Analyst: Generate `PRODUCT_BACKLOG.md` from `APPROVED_VISION.md`
  5. Tool: Auto-calculate WSJF
  6. LOOP (Backlog):
     a. Reviewer: Check Epics/Stories (INVEST/WSJF)
     b. If Reject -> Analyst fixes -> Retry
     c. If Approve -> Save `APPROVED_BACKLOG.md` -> BREAK

  7. Summary: Ready for Human Gate
```

### Phase 2: Standalone Mode (Startups/RFP) (Week 3)
**Goal**: Use agents for analysis WITHOUT triggering development.

- **Use Case**: Evaluating incoming RFPs or brainstorming startup ideas.
- **Workflow**:
  - Run `/product-refine`
  - Output: `APPROVED_BACKLOG.md` + `PRODUCT_VISION.md`
  - **STOP**. Do not convert to `TASK.md`.
  - User decision point: "Archive" (Idea stored) or "Proceed" (Generate domains).

### Phase 3: Technical Integration (Week 4)
**Goal**: Connect Approved Backlog to `01_orchestrator`.

- Only when user explicitly proceeds.
- Map `APPROVED_BACKLOG.md` Epics -> `domains/{domain}/TASK.md`.

---

## VDD Review

> **Sarcasmotron Mode** 🎭

### Challenge 1: "Business metrics are hard to verify"

**Issue:** Unlike code (tests pass/fail), business metrics (ROI, WSJF) are subjective.

**Risk:** LLM hallucinates business justifications that sound plausible but are wrong.

**Mitigation:**
1. WSJF requires explicit scoring (1-10) with rationale
2. Product Reviewer enforces "Show your work" — no scores without explanation
3. User is ALWAYS in the loop for business decisions

**VDD Verdict:** PASS with human oversight mandatory

---

---

### Challenge 3: "Another layer = more complexity"

**Issue:** Adding product phase increases pipeline length.

**Risk:** More phases = more potential failures = longer feedback loop

**Mitigation:**
1. Product phase is OPTIONAL — technical-only projects skip it
2. Product phase happens ONCE per major initiative, not per task
3. Output is reusable across multiple development cycles

**VDD Verdict:** PASS — complexity justified for enterprise scale

---

### Challenge 4: "Token budget will be exceeded"

**Issue:** New skills + agents = more tokens

**Calculation (Revised after O1-O4):**
```
Existing: ~38,000 tokens (Optimized Standard Pipeline)
Product Phase:
  + p01_product_analyst: ~2,500
  + p02_product_reviewer: ~2,000
  + skill-product-analysis: ~1,000 (TIER 2)
  + skill-backlog-prioritization: ~500 (Script)
  = ~6,000 tokens additional

Total with Product: ~44,000 tokens (Well within limits)
```

**VDD Verdict:** PASS — O1-O4 optimizations successfully created room.

---

## Open Questions

### Resolved (by this document)

| Question | Resolution |
|----------|------------|
| "How to handle hallucinations in PO?" | VDD-review mandatory via p02_product_reviewer |
| "Need parallel agents?" | No — artifact-based handoff instead |
| "Separate PM framework?" | No — start as extension, extract if needed |

### Still Open

| Question | Owner | Blocker For |
|----------|-------|-------------|
| "How to persist context between sessions?" | **RESOLVED (O7)**: `skill-session-state` + `latest.yaml` | Multi-session pipeline |
| "Token Budget limit?" | **RESOLVED (O1-O4)**: Optimization freed up ~5k tokens | Feasibility |
| "How to validate business metrics?" | Human oversight | Full automation |
| "IDE support for domain switching?" | IDE vendor | Seamless UX |

---

## Implementation Timeline

```
Week 1: Phase 0
├── Create skill-product-analysis
├── Create skill-backlog-prioritization
├── Create p01_product_analyst
└── Create p02_product_reviewer

Week 2: Phase 1
├── Create product workflows
├── Test workflows in isolation
└── Document usage examples

Week 3: Phase 2
├── Create domain folder structure
├── Update Orchestrator
└── Test multi-domain scenario

Week 4+: Validation
├── Test on real project (Trading Platform example)
├── Measure token usage
├── Iterate based on feedback
```

---

## Future Initiatives (Phase 3+)

### 1. Domain Isolation Strategy
> [!NOTE]
> Deferred to allow Product Agents to stabilize first.

**Goal**: Support multi-domain enterprise projects where Epics are automatically routed to domain-specific queues.

#### Proposed Skill: `skill-domain-decomposition`
```markdown
# Domain Decomposition

## Bounded Context Rules
1. Each domain has clear ownership
2. Minimal dependencies between domains
3. Shared kernel explicitly documented

## Domain → Folder Mapping
Epic "User Authentication" → domain: auth
Epic "Trading Bots" → domain: trading
```

#### Proposed Workflow: `domain-start.md`
1. Read `APPROVED_BACKLOG.md`
2. Load `skill-domain-decomposition`
3. Split Epics into `docs/domains/{domain}/TASK.md`

### 2. Challenge: "Domain assignment is non-trivial"
**Issue:** Deciding which epic belongs to which domain requires deep understanding.
**Mitigation:** Architecture phase must validate domain boundaries before any code is written.

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-21 | Adversarial Architect | Initial vision with VDD review |
