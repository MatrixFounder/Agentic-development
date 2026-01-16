---
name: architecture-review-checklist
description: Detailed checklist for verifying System Architecture and Data Models.
version: 1.0
---
# Architecture Review Checklist

## 1. TASK Compliance
- [ ] **Coverage:** All Use Cases mapped to components?
- [ ] **Constraints:** All non-functional requirements met?

## 2. Data Model (CRITICAL)
- [ ] **Completeness:** All entities, attributes, relationships defined?
- [ ] **Types:** Correct data types chosen? (e.g., TIMESTAMP vs VARCHAR)
- [ ] **Indexes:** Defined for frequent queries?
- [ ] **Migrations:** Plan for existing data exists?
- [ ] **Business Rules:** Constraints enforced (UNIQUE, NOT NULL)?

## 3. System Design
- [ ] **Simplicity:** Least moving parts? (No overengineering).
- [ ] **Style:** Pattern matches problem (Monolith vs Microservices).
- [ ] **Boundaries:** Clear segregation of duties (SRP).

## 4. Security
- [ ] **Auth:** Authentication & Authorization defined?
- [ ] **Protection:** OWASP Top 10 considered?
- [ ] **Secrets:** No hardcoded keys?

## 5. Scalability & Reliability
- [ ] **Scaling:** Horizontal/Vertical strategy?
- [ ] **Faults:** Error handling, retries, backups?

## Criticality Protocol
- 🔴 **BLOCKING:** Data Model error, Security hole, Unmet TASK requirement.
- 🟡 **MAJOR:** Missing index, Questionable tech choice, Vague interface.
- 🟢 **MINOR:** Description clarity, typos.
