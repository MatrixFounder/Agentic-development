# Solution Blueprint: [Product Name]

## 1. User Requirements (The "What")
- List top 5–10 user stories with acceptance criteria.

### User Story Example
- **Persona:** [Name] (Role/Demographic)
- **User Story:** As a [Persona], I want [Action] so that [Benefit].
- **Acceptance Criteria:**
    - [ ] Criterion 1
    - [ ] Criterion 2

## 2. Text-Based UX Flows (The "Skeleton")
- Numbered steps for core flows + error paths.

### Flow 1: [User Story Name]
- **Size:** M (60h) | **LLM Friendly:** 0.8
1. User [Action] on [Page/Component].
   - *System:* [Validates/Checks/Loads].
   - *Error Path:* If [Condition], show [Error Message].
2. User sees [Result].
3. User clicks [Button].
   - *System:* Calls API `POST /api/v1/resource`.

### Flow 2: [Another Story]
- **Size:** S (20h) | **LLM Friendly:** 0.5
1. ...

## 3. Non-Functional Requirements (NFRs)
- **Security:** [e.g. Zero-Knowledge, OAuth2]
- **Performance:** [e.g. Latency < 200ms]
- **Scalability:** [e.g. Support 10k concurrent users]

## 4. Business Case (ROI)
- Development Effort (granular story sizing if advanced mode)
- ROI Summary (use calculate_roi.py outputs)
<!-- Paste output from calculate_roi.py here -->
```text
(Paste script output)
```
- Unit Economics: ARPU, LTV, CAC, LTV/CAC ratio, Payback Period
- Verdict: Strong Go / Consider / No-Go


## 5. Risk Register
| Risk ID | Risk Description | Impact (1-5) | Likelihood (1-5) | Mitigation |
|---------|------------------|--------------|------------------|------------|
| R01     | [Description]    | 5            | 3                | [Mitigation] |
