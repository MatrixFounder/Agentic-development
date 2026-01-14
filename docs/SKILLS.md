# System Skills Catalog

The Agentic System v3.0 relies on a modular **Skills System**. Skills are reusable packages of instructions that extend agent capabilities.

## 📁 Library Layout
Skills are located in `.agent/skills/`.

## 📚 Available Skills

### Core & Process
| Skill | Description | Used By |
|-------|-------------|---------|
| **`core-principles`** | Fundamental principles: Atomicity, Traceability, Stub-First, Minimizing Hallucinations. | All Agents |
| **`artifact-management`** | Rules for managing `.AGENTS.md` (local memory) and global artifacts (`TZ.md`, `ARCHITECTURE.md`). | All Agents |
| **`planning-decision-tree`** | Decision logic for breaking down tasks and prioritizing work (Stub-First & E2E). | Planner, Architect |
| **`requirements-analysis`** | Process for gathering and refining requirements into a structured Technical Specification (TZ). | Analyst, TZ Reviewer |

### Engineering Standards
| Skill | Description | Used By |
|-------|-------------|---------|
| **`architecture-design`** | Guidelines for designing scalable and modular system architecture and data models. | Architect, Arch Reviewer |
| **`tdd-stub-first`** | Test-Driven Development strategy: "Structure & Stubs" first, then "Implementation". | Planner, Developer |
| **`developer-guidelines`** | Behavioral rules for Developers: adherence to tasks, "Documentation First", Anti-Loop Protocol. | Developer |
| **`documentation-standards`** | Standards for docstrings (Google/JSDoc) and "The Why" comments. | Developer, Code Reviewer |
| **`testing-best-practices`** | Best practices: E2E/Unit hierarchy, no LLM mocking, realism. | Developer, Code Reviewer |

### Review & Quality Assurance
| Skill | Description | Used By |
|-------|-------------|---------|
| **`checklists/*`** | Specialized checklists for each review stage: | Reviewers |
| - `tz-review-checklist` | For checking Technical Specifications. | TZ Reviewer |
| - `architecture-review-checklist` | For checking System Architecture. | Arch Reviewer |
| - `plan-review-checklist` | For checking Development Plans. | Plan Reviewer |
| - `code-review-checklist` | For checking Code implementation. | Code Reviewer |
| **`security-audit`** | Vulnerability assessment (OWASP, secrets) and reporting. | Security Auditor |

### Verification Driven Development (VDD)
| Skill | Description | Used By |
|-------|-------------|---------|
| **`vdd-adversarial`** | Adversarial verification: challenging assumptions and finding weak spots. | Sarcasmotron |
| **`vdd-sarcastic`** | Adversarial verification with a sarcastic/provocative tone. | Sarcasmotron |
