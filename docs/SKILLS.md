# System Skills Catalog

The Agentic System v3.0 relies on a modular **Skills System**. Skills are reusable packages of instructions that extend agent capabilities.

## 📁 Library Layout
Skills are located in `.agent/skills/`.

## ⚙️ How it Works

The Skills System separates **"Who"** (Agent Persona) from **"What"** (Capabilities).
- **Persona (`System/Agents/`)**: Defines the role, tone, and high-level responsibilities (e.g., "You are an Architect").
- **Skill (`.agent/skills/`)**: Defines specific procedures, checklists, or technical standards (e.g., "How to design a DB").

### Principles
1.  **Dynamic Loading**: Agents load only the skills they need for a specific task.
2.  **Modularity**: Improvements to `skill-tdd-stub-first` automatically benefit all agents using it.
3.  **Cross-Platform**: The same skill definitions work in both Cursor and Antigravity.

### 🔗 Documentation
- **For Cursor**: [Cursor Skills Documentation](https://cursor.com/ru/docs/context/skills)
- **For Antigravity**: [Antigravity Skills Documentation](https://antigravity.google/docs/skills)

## 📚 Available Skills

### Core & Process
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`core-principles`** | Fundamental principles: Atomicity, Traceability, Stub-First, Minimizing Hallucinations. | All (`01-03`, `vdd-*`) | All Agents |
| **`artifact-management`** | Rules for managing `.AGENTS.md` (local memory) and global artifacts (`TZ.md`, `ARCHITECTURE.md`). | All Workflows | All Agents |
| **`planning-decision-tree`** | Decision logic for breaking down tasks and prioritizing work (Stub-First & E2E). | `02-plan-implementation`, `vdd-02-plan` | Planner, Architect |
| **`requirements-analysis`** | Process for gathering and refining requirements into a structured Technical Specification (TZ). | `01-start-feature`, `vdd-01-start-feature` | Analyst, TZ Reviewer |

### Engineering Standards
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`architecture-design`** | Guidelines for designing scalable and modular system architecture and data models. | `01-start-feature`, `/base-stub-first` | Architect, Arch Reviewer |
| **`tdd-stub-first`** | Test-Driven Development strategy: "Structure & Stubs" first, then "Implementation". | `03-develop-task`, `vdd-enhanced` | Planner, Developer |
| **`developer-guidelines`** | Behavioral rules for Developers: adherence to tasks, "Documentation First", Anti-Loop Protocol. | `03-develop-task`, `/base-stub-first` | Developer |
| **`documentation-standards`** | Standards for docstrings (Google/JSDoc) and "The Why" comments. | All Development Workflows | Developer, Code Reviewer |
| **`testing-best-practices`** | Best practices: E2E/Unit hierarchy, no LLM mocking, realism. | `03-develop-task`, `vdd-03-develop` | Developer, Code Reviewer |

### Review & Quality Assurance
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`checklists/*`** | Specialized checklists for each review stage: | All relevant stages | Reviewers (TZ, Arch, Plan, Code) |
| - `tz-review-checklist` | For checking Technical Specifications. | `01-start-feature` | TZ Reviewer |
| - `architecture-review-checklist` | For checking System Architecture. | `01-start-feature` | Arch Reviewer |
| - `plan-review-checklist` | For checking Development Plans. | `02-plan-implementation` | Plan Reviewer |
| - `code-review-checklist` | For checking Code implementation. | `03-develop-task` | Code Reviewer |
| **`security-audit`** | Vulnerability assessment (OWASP, secrets) and reporting. | `/security-audit`, `/full-robust` | Security Auditor |

### Verification Driven Development (VDD)
| Skill | Description | Used By in Workflows | Used By Agents |
|-------|-------------|----------------------|----------------|
| **`vdd-adversarial`** | Adversarial verification: challenging assumptions and finding weak spots. <br> **[Read Full Role Description](docs/VDD.md#core-philosophy)** | `vdd-03-develop`, `/vdd-adversarial` | **Virtual Persona** <br> (Adversarial Agent) |
| **`vdd-sarcastic`** | Adversarial verification with a sarcastic/provocative tone. (Variant of `vdd-adversarial`) | `/vdd-sarcastic` | **Virtual Persona** <br> (Adversarial Agent) |
