---
name: brainstorming
description: Use when brainstorming ideas, exploring solutions, generating options, clarifying requirements, designing architecture, or answering open-ended "how should we" and "what are the options" questions — even without the word "brainstorm".
tier: 2
version: 3.1
status: active
---

# Universal Brainstorming Protocol

## Purpose

Bridge the gap between a vague user intent ("Make it pop", "I need a referral system") and a concrete, actionable plan. This skill doesn't just *clarify* requirements — it actively **generates ideas**, helps the user **evaluate trade-offs**, and converges on a **confirmed design** before any code is written.

## Red Flags (Anti-Rationalization)

**STOP and READ THIS if you are thinking:**
- "I'll just start coding, the requirements are clear enough" → **WRONG**. Even "clear" tasks have hidden assumptions. Validate first — rework costs 3x more than upfront clarification.
- "I'll skip idea generation and go straight to the obvious solution" → **WRONG**. The obvious solution is often the first one, not the best one. Generate at least 3 options for MEDIUM/COMPLEX tasks.
- "The user didn't ask for alternatives, so I'll just propose one" → **WRONG**. Brainstorming means expanding the solution space. Always present options with trade-offs.
- "I can't visualize this without a whiteboard" → **WRONG**. Use Mermaid, ASCII, or structured bullet lists — text-based visualization is always possible.
- "The user ignored my question, I'll guess" → **WRONG**. Don't guess on ambiguous requirements. Restate why the answer matters: *"To avoid breaking X, I need to know Y."*
- "This is too simple for a full brainstorm" → **OK, but state it explicitly**: *"This is trivial — I propose X. Proceed?"* Never silently skip the process.

## Capabilities

- Classify task complexity (Trivial / Medium / Complex) and adapt workflow depth
- Generate diverse ideas using structured methodologies (SCAMPER, How Might We, Inversion, Analogy)
- Visualize architectures and flows (Mermaid → ASCII → Bullet Lists fallback)
- Facilitate diverge → converge cycles for open-ended problems
- Prioritize options using Impact/Effort analysis or criteria-based scoring
- Produce appropriate output artifacts (Design Doc, Strategy Doc, Ideas Board, Technical Spec)
- Handle both technical (architecture, API design) and non-technical (naming, strategy, UX) brainstorms

## Execution Mode
- **Mode**: `prompt-first`
- **Rationale**: Brainstorming is inherently conversational and judgment-driven. No scripts needed — the value is in structured thinking and dialogue.

## Safety Boundaries
- **Scope**: Operate only on the topic the user brings up. Do not expand scope to adjacent systems unless the user asks.
- **No Code**: Do NOT write implementation code during brainstorming (except trivial tasks). The output is a *plan*, not code.
- **No Unilateral Decisions**: Never commit to an approach without explicit user confirmation.
- **Destructive Changes**: If the brainstorm leads to replacing existing architecture, flag it clearly: *"This would replace the current auth module. Are you sure?"*

## Validation Evidence
- User explicitly confirmed the final approach ("Yes", "Approved", "Let's go with B")
- For MEDIUM/COMPLEX: a Design Doc or Strategy Doc exists with trade-offs documented
- The Adversarial Checklist (Phase 4) passed with no red flags

---

## Phase 1: Assess & Understand

### 1. Complexity Assessment (MANDATORY)

At the start, classify the task. This determines your entire workflow depth:

| Level | Criteria | Protocol |
| :--- | :--- | :--- |
| **TRIVIAL** | Clear requirements, standard pattern, single component (e.g., "Fix typo", "Add log"). | **Fast Path**: Confirm plan in 1-2 sentences. Go. |
| **MEDIUM** | Standard task but open details, 2-3 components (e.g., "Add dark mode", "Refactor auth"). | **Standard**: 2-3 clarifying questions, generate 2-3 options, brief confirmation. |
| **COMPLEX** | High uncertainty, architectural impact, multiple domains (e.g., "Design referral system", "New microservice"). | **Deep Dive**: Research → Ideation → Visualize → Trade-offs → Design Doc → Sign-off. |

**Commitment anchor**: After classification, announce it explicitly: *"This is a COMPLEX task — entering Deep Dive mode."* This public commitment prevents silently downgrading the workflow depth later when you feel tempted to shortcut.

### 2. Context Gathering (Tool Agnostic)

- **Search**: Use your environment's search capability (e.g., `grep`, `search_code`, `Glob`) to understand existing patterns, tech stack, and conventions.
  - *Guardrail*: **IF NO SEARCH TOOLS EXIST**, do NOT guess. Ask the user: *"I cannot scan the repo. Could you share `package.json` and relevant files?"*
- **Reading**: Check `task.md`, `README.md`, or config files to align with project standards.
- **Constraints**: Identify hard constraints early — budget, timeline, tech stack, team skills, existing contracts.

---

## Phase 2: Diverge — Generate Ideas (The "What If")

This phase **expands** the solution space. The goal is quantity and diversity, not perfection.

### For TRIVIAL tasks
Skip this phase. Propose the obvious solution and confirm.

### For MEDIUM tasks

**Generate 2-3 options** using at least one technique:

- **Direct alternatives**: List different implementation approaches (e.g., localStorage vs DB vs cookie for persistence)
- **How Might We**: Reframe the problem as "How might we onboard users without requiring email verification?" to unlock lateral thinking
- **Analogy**: "How do similar systems solve this?" (e.g., "Stripe handles this with webhooks, Shopify uses polling")

### For COMPLEX tasks

**Generate 3-5 options** using multiple techniques (see `references/ideation_techniques.md` for step-by-step algorithms):

- **SCAMPER**: Systematically apply each letter (Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse) to the current approach
- **Inversion**: "What would make this fail?" → then design the opposite
- **First Principles**: Strip the problem to fundamental truths — "Why do we need X at all?" — then rebuild from scratch, ignoring existing solutions
- **How Might We**: Reframe constraints as opportunities
- **Analogy**: Draw from patterns in other domains or well-known systems
- **Constraint Removal**: "If we had no budget limit, what would we build?" → then add constraints back
- **Wild Card** (MANDATORY for COMPLEX): Include at least one radically different approach that challenges the problem framing itself. Label it "Wild Card". Even if impractical, it expands the solution space and often inspires hybrid solutions.

**Present ideas as a numbered list** with a 1-sentence description each. Do NOT evaluate yet — that's Phase 3.

### Knowledge Depth (MANDATORY for MEDIUM/COMPLEX)

Go beyond obvious solutions. For each option you generate, actively draw on the best available knowledge:

- **Real-world precedents**: Name specific companies, systems, or projects that solved similar problems. Cite what worked and what didn't. (e.g., "Spotify's Discover Weekly uses collaborative filtering + editorial curation — a hybrid that outperformed either alone")
- **Cross-domain analogies**: Borrow solutions from unrelated fields. A logistics problem might learn from ant colony algorithms; a notification system might learn from hospital alert fatigue research.
- **Academic/research insights**: If relevant research exists (distributed systems theory, UX studies, behavioral economics), reference it concretely.
- **Name your sources**: Do NOT say "some systems use X". Say "Stripe's payment retry uses exponential backoff with jitter — we could apply this to our notification delivery."

The most valuable thing you bring is cross-domain knowledge that the user doesn't have. Use it.

### Smart Questions (Adaptive)

Ask questions to fill gaps, but adapt the count to complexity:
- **TRIVIAL**: 0-1 questions (confirm and go)
- **MEDIUM**: 1-2 questions, each with concrete options: *"For persistence, do you prefer localStorage or a database?"*
- **COMPLEX**: 2-4 questions across different dimensions (scope, quality attributes, constraints, priorities)

In Phase 2-3 (diverge/converge), always provide concrete options to reduce cognitive load. In Phase 1 (understand), open-ended questions are allowed when you need to discover the user's actual goal — e.g., *"What does success look like for this project?"*

---

## Phase 3: Converge — Evaluate & Prioritize (The "Which One")

This phase **narrows** the solution space. The goal is a clear recommendation with reasoning.

### Visual Thinking

For **MEDIUM/COMPLEX** tasks, visualize the proposed approach — visual models catch flaws that text descriptions miss:
- **Primary**: **Mermaid** (Flowcharts, Sequence Diagrams) — use when confident the user's UI supports it
- **Fallback**: **ASCII Art** or **Structured Bullet Lists** if environment is restricted (standard terminal)

### Prioritization

For MEDIUM tasks with 2+ options:
- **Quick comparison**: A simple pros/cons table is sufficient

For COMPLEX tasks with 3+ options:
- **Impact/Effort Matrix**: Rate each option on impact (H/M/L) and effort (H/M/L)
- **Criteria-Based Scoring**: Define 3-5 criteria (performance, maintainability, time-to-ship, risk) and score each option
- **Trade-off Summary**: For the top 2 options, explicitly state: *"Option A gives you speed but costs maintainability. Option B gives you clean architecture but costs an extra week."*

### Second-Order Thinking (COMPLEX tasks)

Before recommending, consider consequences beyond the immediate:
- **6-month consequences**: What new problems will the recommended option create? (e.g., "Async processing means we need an observability stack for the queue")
- **Scaling implications**: What breaks at 10x current load/users/data?
- **Organizational impact**: Which teams need to change? What new skills are required?

State these explicitly in your recommendation — they are part of the trade-off, not afterthoughts.

### Recommendation

Always end with a clear recommendation: *"I recommend the event-driven approach because it decouples services. The main risk is message loss, mitigated by a dead-letter queue."*

Do NOT present options without a recommendation — the user hired you to think, not just list.

---

## Phase 4: Verify & Confirm (The "Gate")

### Pre-Mortem (MANDATORY for COMPLEX)

Before presenting the final recommendation, run a Pre-Mortem (Gary Klein's technique):
*"Imagine this solution failed catastrophically in production 6 months from now. What went wrong?"*

List 3 plausible failure scenarios. For each, verify the design has a mitigation. If it doesn't — add one or flag it as an open risk to the user.

### Adversarial Checklist

Before asking for approval, explicitly verify in your reasoning:
- [ ] **Red Flags**: Did I ignore any user constraints or project conventions?
- [ ] **YAGNI**: Is this the simplest solution that meets requirements? Am I over-engineering?
- [ ] **Alignment**: Does this match the project's tech stack (e.g., not suggesting React for a Vue app)?
- [ ] **Idea Diversity**: Did I genuinely explore alternatives, or just dress up one idea in different words?
- [ ] **Knowledge Depth**: Did I cite real-world precedents, or just generate ideas from thin air?
- [ ] **User Confirmation**: Has the user explicitly agreed to *this specific approach*?

### Output Artifacts

Choose the appropriate artifact based on task type:

| Task Type | Artifact | When |
| :--- | :--- | :--- |
| Architecture / System Design | **Design Doc** (`docs/design/feature-name.md`) | COMPLEX technical tasks |
| Strategy / Business Decision | **Strategy Doc** (in chat or file) | Non-code brainstorms |
| Naming / UX / Creative | **Ideas Board** (numbered list with pros/cons) | Creative tasks |
| Standard Feature | **Technical Spec** (brief summary in chat) | MEDIUM tasks |
| Trivial Change | **Chat confirmation** (1-2 sentences) | TRIVIAL tasks |

*No File Access?* Output the full Markdown in chat and ask the user to save it.

### Handover

- **Presentation**: *"Here is the proposed design for the referral system. Trade-offs considered: sync vs async processing. I recommend async."*
- **Checkpoint**: *"Please confirm this approach before I proceed to implementation."*
- **Rejection**: *"Understood. You prefer the synchronous approach. Pivoting the design. Here's the updated plan..."*

---

## Phase 5: Iterate (The "Loop Back")

Brainstorming is not linear. If the user:

- **Rejects all options** → Return to Phase 2 with a different technique:
  1. Ask *"What's missing or wrong with these options?"* to understand the gap
  2. Switch technique — if you used Direct/Analogy, try Inversion or First Principles
  3. Challenge the original constraints: *"Are any of these constraints actually flexible?"*
  4. If still stuck, use Constraint Removal to find the ideal, then work backwards
- **Wants to explore a tangent** → Acknowledge it, mini-brainstorm the tangent (1-2 options), then explicitly return: *"Coming back to the main thread..."*
- **Changes requirements mid-stream** → Re-assess complexity. Announce if the level changed: *"This has moved from MEDIUM to COMPLEX — switching to Deep Dive mode."* Re-enter at Phase 2.
- **Says "I don't know"** → That's a signal to generate more options, not to guess. Use Inversion (*"What would you NOT want?"*) or Analogy (*"Here's how Slack/Stripe/Spotify solved a similar problem..."*) to unlock new angles.
- **Brainstorm stalls** → Offer a provocative constraint: *"What if we had to ship this in 1 day? What would we cut?"* Or flip perspective: *"What would your users wish this did?"*

---

## Rationalization Table (Additional Anti-Patterns)

These complement the Red Flags section with situational traps:

| Agent Excuse | Reality / Correct Action |
| :--- | :--- |
| "My options are good enough — no need for deep research." | **WRONG**. Surface-level options waste the user's time. Cite real systems, research, or precedents. |
| "I generated 3 options, that's enough diversity." | **CHECK**. Are they genuinely different approaches, or the same idea with different names? Apply the "would a different team choose differently?" test. |
| "The second-order effects are obvious, no need to state them." | **WRONG**. State them explicitly. What's obvious to you may be invisible to the user. |
| "This seems standard." | **VERIFY**. Is it standard *for this project*? Check conventions first. |
| "The Wild Card option is too weird to include." | **WRONG**. That's exactly why it's valuable. Label it, present it, let the user decide. |

---

## Edge Cases

- **User provides full design**: Summarize understanding, verify 1-2 assumptions, then Fast Track to implementation.
- **Non-Code Idea**: Switch to "Strategy" mode. Output a Strategy Doc instead of Technical Spec. Use business criteria for prioritization (revenue, user impact, feasibility).
- **Legacy Code**: If context is massive, ask: *"Which specific files should I anchor my design on?"*
- **User says "just do it"**: Classify as TRIVIAL. Confirm in 1 sentence and proceed. But if the task is objectively COMPLEX, push back once: *"This touches auth, billing, and notifications. A 2-minute brainstorm now saves hours later. Quick: sync or async processing?"*
