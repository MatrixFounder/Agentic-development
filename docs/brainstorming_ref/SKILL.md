---
name: brainstorming
description: Use for ideation, requirements clarification, and architectural design. Adapts to task complexity (Trivial/Medium/Complex).
tier: 2
version: 2.1
status: active
changelog: Upgraded to Universal Gold Standard v2.1 (2026) - Added 3-Tier Assessment, Tool Agnosticism, and Safety Guardrails.
---

# Universal Brainstorming Protocol

**Purpose**: Bridge the gap between user intent ("Make it pop") and technical specification ("CSS Box Shadow").
**Core Rule**: Do NOT write code until you have a confirmed design (except for Trivial tasks).

## Phase 1: Assess & Understand

**1. Complexity Assessment (MANDATORY)**
At the start, classify the task to determine your mode:

| Level | Criteria | Protocol | Reference |
| :--- | :--- | :--- | :--- |
| **TRIVIAL** | Clear requirements, standard pattern, single component (e.g., "Fix typo", "Add log"). | **Fast Path**: Skip deep research. Confirm plan in chat. Go. | `examples/demo_trivial.md` |
| **MEDIUM** | Standard task but open details (e.g., "Add button", "Refactor function"). | **Standard**: 1-2 clarifying questions, 2 options, brief confirmation. | `examples/demo_medium.md` |
| **COMPLEX** | High uncertainty, architectural impact, multiple components (e.g., "New System"). | **Deep Dive**: Research -> Mermaid -> Trade-offs -> Design Doc -> Sign-off. | `examples/demo_complex.md` |

**2. Context Gathering (Tool Agnostic)**
*   **Search**: Use your environment's search capability (e.g., `grep`, `search_code`) to understand existing patterns.
    *   *Guardrail*: **IF NO SEARCH TOOLS EXIST**, do NOT guess. Explicitly ask the user: *"I cannot scan the repo. Could you share `package.json` and relevant files?"*
*   **Reading**: Preferentially read `task.md`, `README.md`, or `.cursorrules` to align with project standards.

---

## Phase 2: Explore & Visualize (The "How")

**1. Smart Questions**
*   Ask **ONE** critical question at a time.
*   *Template*: "To match your existing patterns for [X], do you prefer [Option A] or [Option B]?"

**2. Visual Thinking**
*   **Constraint**: For **MEDIUM/COMPLEX** tasks, you MUST visualize the flow.
*   **Primary**: **Mermaid** (Flowcharts/Sequence) *only if* confident the user's UI supports it.
*   **Fallback**: **ASCII Art** or **Bullet Lists** if the environment is restricted (e.g., standard terminal).

**3. The "Design Doc" Rule**
*   **Trivial**: No doc needed. Chat confirmation is enough.
*   **Medium/Complex**: You **MUST** produce a Design Document (e.g., `docs/design/feature-name.md`).
    *   *No File Access?*: Output the full Markdown in chat and ask user to save it.

---

## Phase 3: Converge & Verify (The "Gate")

**1. Adversarial CoT Checklist (The "Final Gate")**
Before asking for approval, explicitly check these in your internal thought process:
- [ ] **Red Flags**: Did I ignore any user constraints?
- [ ] **YAGNI**: Is this the simplest possible solution?
- [ ] **Alignment**: Does this match the project's tech stack (e.g., not suggesting React for a Vue app)?
- [ ] **Confirmation**: Did the user explicitly say "Yes" to *this specific design*?

**2. Handover Templates**
*   **Presentation**: *"I have analyzed the options. Here is the proposed design for [Feature]: [Link to Doc / Summary]. Trade-offs considered: [A vs B]."*
*   **Checkpoint**: *"Please confirm this approach matches your expectation before I proceed to implementation."*
*   **Rejection**: *"Understood. You prefer [B]. I will pivot the design to focus on [B]. New plan..."*

---

## Rationalization Table (Anti-Patterns)

| Agent Excuse | Reality / Correct Action |
| :--- | :--- |
| "It's faster to just code it." | **WRONG**. Reworking bugs is slower. Validate first. |
| "I skipped options because it's trivial." | **OK**, but state: *"This is trivial, I propose X. Proceed?"* |
| "The user ignored my question." | **RISKY**. Don't guess. Ask again: *"To avoid breaking X, I need to know Y."* |
| "I can't see the file." | **STOP**. Ask for it. Do not hallucinate file contents. |
| "This seems standard." | **VERIFY**. Is it standard *for this project*? Check `package.json`. |

---

## Edge Cases
*   **User provides full design**: Summarize understanding, verify 1-2 assumptions, then Fast Track.
*   **Non-Code Idea**: Switch to "Strategy" mode. Output a "Strategy Doc" instead of "Technical Spec".
*   **Legacy Code**: If context is massive, ask user: *"Which specific files should I anchor my design on?"*
