# TASK 218 — Break-glass access grants for the operations console

Owner: platform access team. Status: draft. Target release: 2026-10.

## 1. Context

The operations console exposes one shared administrator account. Its credentials
live in the on-call vault and are rotated after each use. Nine incidents in
2026 Q2 were resolved through that account, and the audit log records the
account rather than the person who acted.

This task replaces the shared account with time-boxed grants issued to one
person for one incident. The console keeps its existing role definitions, and a
grant selects among them.

## 2. Scope

In scope: the grant request path, the approval check, the grant lifetime, the
revocation job and the audit record. Out of scope: the console role
definitions, which the platform team owns, and the retirement of the shared
credential, which TASK 219 covers.

### 2.1 Definitions

| Term | Meaning |
| :--- | :--- |
| grant | a time-boxed authorisation of one person for one role |
| approver | a person holding the `access-approver` role |
| break-glass | access taken outside the standing role assignment |

## 3. Requirements

| ID | Requirement | MVP? |
| :--- | :--- | :--- |
| R1 | A grant request names an incident identifier, a role and a reason | Y |
| R2 | A grant is issued only after approval by a second person | Y |
| R3 | A grant expires 60 minutes after issue | Y |
| R4 | An expired grant is revoked within 15 seconds of its expiry | Y |
| R5 | Each grant writes an audit record naming person, role and incident | Y |
| R6 | One person holds at most two active grants | N |
| R7 | A console action carrying no active grant is rejected | Y |

## 4. Requirement detail

### 4.1 R1 — request contents

**R1.** A grant request must carry an incident identifier, the requested role
and a reason of at most 280 characters. Otherwise the audit record names an
action and no cause, and the reviewer rebuilds the intent from chat history.

The identifier is checked against the incident tracker before the request
reaches an approver. A request naming a closed incident is rejected at that
check.

### 4.2 R2 — approval

**R2.** The approver is a person other than the requester and holds the
`access-approver` role.

**Why.** The 2026-05-18 review found four approvals copied from a previous
incident thread.

An approval older than 10 minutes is not accepted. The requester repeats the
request, and the second approval is recorded with its own timestamp.

### 4.3 R3 — grant lifetime

**R3.** A grant expires 60 minutes after it is issued, and the expiry timestamp
is written with the grant row.

**Why.** The median incident in the 2026 Q2 sample was resolved in 34 minutes.

An expiring grant is not extended in place. A second grant is requested through
the same path, with its own approval.

### 4.4 R4 — revocation

**R4.** The shutter reads the active grant table every 15 seconds and closes
each grant whose expiry has passed.

**Why.** A revocation delay above 30 seconds was measured while the job ran
once per minute.

A closed grant stays in the table for 30 days in the state `revoked`. The
retention job removes it after that window.

### 4.5 R5 — audit record

**R5.** Each issued grant writes one audit record carrying the person, the role,
the incident identifier, the approver and the issue timestamp.

**Why.** The audit export feeds the quarterly access review, which reads one row
per grant.

The record is written before the grant becomes usable. A write failure leaves
the grant unissued.

### 4.6 R6 — concurrent grants

**R6.** The console must refuse a third concurrent grant to the same person. Two
grants cover an engineer holding an incident and a maintenance window at the
same time.

R6 is deferred past the MVP. The counter is recorded from the first release and
enforced in the second.

### 4.7 R7 — action binding

**R7.** A permission that travels further than the incident that justified it
stops being a permission. The console rejects an action whose request carries no
active grant identifier.

The grant identifier travels in the request header `X-Grant-Id`. The console
resolves it against the grant table on every action.

## 5. Failure modes

| Condition | Outcome | Detected by |
| :--- | :--- | :--- |
| The incident tracker is unreachable | the request is rejected and logged | T5 |
| The approver roster is empty | no grant is issued | T6 |
| The revocation job is stopped | grants stay active past their expiry | T7 |
| The audit sink rejects a write | the grant is not issued | T8 |

## 6. Operational notes

Every emergency door becomes an ordinary door once enough people know where it
is. The owner reviews the approver roster each quarter and records the review
date in this document.

The on-call runbook names the grant path in its section 3. The runbook is
updated in the same change that ships R1 to R5.

## 7. Rollout

Each region is enabled behind its own drawbridge, and no two drawbridges open in
the same week. The order is `eu-west`, then `us-east`, then `ap-south`.

The shared account stays available for the first two weeks of each region's
rollout. It is disabled in a region after seven days with no fallback use.

## 8. Test obligations

- T1 — a request with no incident identifier → rejected at the request path.
- T2 — an approval by the requester → rejected; fails when the check compares
  roles and not people.
- T3 — a grant at 61 minutes → the console accepts no action against it.
- T4 — a grant at 59 minutes → the console accepts the action.
- T5 — the tracker returns 503 → the request is rejected and one log line is
  written.
- T6 — three concurrent requests by one person → the third is refused.
- T7 — the revocation job is paused for 60 seconds → the expired grant is closed
  on the first run after the pause.
- T8 — the audit sink returns an error → no grant row is written.

## 9. Open questions

- Q1 — does a grant survive a console deploy that restarts the session store?
- Q2 — who approves a grant during a region-wide incident that pages the whole
  approver roster?
- Q3 — which retention window applies to the audit record in the EU region?
