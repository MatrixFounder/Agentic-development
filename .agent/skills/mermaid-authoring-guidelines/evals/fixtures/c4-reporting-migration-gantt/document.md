## 2. Schedule

Halcyon Analytics moves its reporting warehouse to the new cluster.
Work starts on Monday 2 November 2026. Durations are working days; nobody works on weekends.
A task starts on the first working day after every task it waits for has ended.

### 2.1 Tasks

Each task belongs to one team: Platform, Data, QA or Release.

| ID | Task | Team | Duration | Waits for |
| :--- | :--- | :--- | :--- | :--- |
| P1 | Provision the new cluster | Platform | 4 d | — |
| P2 | Configure replication | Platform | 3 d | P1 |
| D1 | Backfill dimension tables | Data | 2 d | P2 |
| D2 | Backfill fact tables (2019–2025) | Data | 6 d | P2 |
| Q1 | Reconcile row counts | QA | 2 d | D1, D2 |
| R1 | Write freeze | Release | 1 d | Q1 |
| R2 | Switch dashboards | Release | milestone | R1 |

D1 and D2 run in parallel; neither waits for the other. Q1 starts after both backfills have ended.
R2 takes no time: the dashboards switch to the new cluster when the write freeze ends.

### 2.2 Critical path

The critical path is P1, P2, D2, Q1, R1 and R2, 16 working days in total.
D1 can end up to 4 working days late without moving R2.

### 2.3 Acceptance and rollback

- Q1 accepts a row-count difference of at most 0.1 % between the old and the new warehouse.
- After R2, the old warehouse stays ready for a rollback for 3 days.

### 2.4 Out of scope

Decommission the old warehouse — not before 30 days after R2; tracked in TASK-512.
This plan does not schedule it.
