# Lightweight Threat Modeling Template

> **Methodology:** STRIDE-per-Element (simplified).
> **When to use:** Before any new feature, API endpoint, or infrastructure change.
> **Time budget:** 15-30 minutes for a focused feature; 1-2 hours for a system.

## Step 1: Define Scope
```
Feature/Component: ____________________
Data Classification: [ ] Public  [ ] Internal  [ ] Confidential  [ ] Restricted
Users/Actors: ____________________
```

## Step 2: Draw Data Flow Diagram (DFD)
Identify and document:
- **External Entities**: Users, third-party APIs, external services
- **Processes**: Application logic, microservices, background jobs
- **Data Stores**: Databases, caches, file systems, vector stores
- **Data Flows**: Arrows showing data movement with protocol (HTTPS, gRPC, etc.)
- **Trust Boundaries**: Lines separating zones of trust (internet ↔ DMZ ↔ internal)

In a Markdown document, draw the DFD per `mermaid-authoring-guidelines`; load the skill first.
- **Kind**: Mermaid `flowchart`.
- **Trust boundaries**: a zone of trust with two or more elements is a subgraph with a short
  title. For a zone with one element, the zone name goes on that element's second line.
- **Data flows**: edges between elements, labelled with the data and its protocol
  (`readings · MQTT`). No edge ends on a subgraph.
- **Budget**: the skill's flowchart budget applies. Over it, Step 3 of the skill aggregates the
  DFD or splits it into several figures.
- **Legend**: directly below the figure; it names the trust-boundary notation.

In a terminal or chat reply, pick the form with Step 0 of the skill instead. If the skill is not
installed, list the flows in a table and report that the skill is absent.

## Step 3: STRIDE Analysis

For EACH element in the DFD, evaluate:

| Threat | Question | Applies? | Mitigation |
|--------|----------|----------|------------|
| **S**poofing | Can an attacker pretend to be this entity? | [ ] Yes [ ] No | Auth, mTLS, API keys |
| **T**ampering | Can data be modified in transit or at rest? | [ ] Yes [ ] No | TLS, HMAC, checksums |
| **R**epudiation | Can an actor deny performing an action? | [ ] Yes [ ] No | Audit logs, signing |
| **I**nformation Disclosure | Can sensitive data leak? | [ ] Yes [ ] No | Encryption, access control |
| **D**enial of Service | Can the resource be exhausted? | [ ] Yes [ ] No | Rate limiting, CDN, scaling |
| **E**levation of Privilege | Can a user gain higher permissions? | [ ] Yes [ ] No | RBAC, least privilege |

## Step 4: Risk Assessment (DREAD Score)

For each identified threat, score 1-10:

| Factor | Score (1-10) | Description |
|--------|-------------|-------------|
| **D**amage | __ | How severe is the impact? |
| **R**eproducibility | __ | How easy to reproduce? |
| **E**xploitability | __ | How easy to exploit? |
| **A**ffected Users | __ | How many users impacted? |
| **D**iscoverability | __ | How easy to discover? |
| **Total** | __ / 50 | **0-20**: Low, **21-35**: Medium, **36-50**: High |

## Step 5: Mitigation Tracker

| # | Threat | DREAD | Status | Owner | Mitigation |
|---|--------|-------|--------|-------|------------|
| 1 | | /50 | [ ] Open [ ] Mitigated [ ] Accepted | | |
| 2 | | /50 | [ ] Open [ ] Mitigated [ ] Accepted | | |
| 3 | | /50 | [ ] Open [ ] Mitigated [ ] Accepted | | |

## Step 6: Assumptions & Out of Scope
- **Assumptions**: (e.g., "Cloud provider infrastructure is secure", "TLS terminates at load balancer")
- **Out of Scope**: (e.g., "Physical security", "Social engineering")

## Quick Reference: Common Threats by Component

### Web Application
- SQL Injection, XSS, CSRF, Session Hijacking, IDOR

### API
- BOLA, Mass Assignment, Rate Limiting, JWT Manipulation

### AI/LLM Integration
- Prompt Injection (direct + indirect), Data Exfiltration via output, Excessive Agency

### Smart Contract
- Reentrancy, Flash Loan, Oracle Manipulation, Access Control

### Infrastructure
- SSRF, Container Escape, Privilege Escalation, Secrets Exposure
