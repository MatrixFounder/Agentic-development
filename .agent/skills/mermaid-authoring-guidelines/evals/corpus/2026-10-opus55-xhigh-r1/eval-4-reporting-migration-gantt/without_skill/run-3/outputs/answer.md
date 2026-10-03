The chart below shows the schedule from §2.1 by team, with the critical path highlighted. The write freeze (R1) falls on Monday 23 November 2026, and the dashboards switch (R2) when that day ends.

```mermaid
gantt
    accTitle: Warehouse migration schedule
    accDescr: P1 2–5 Nov 2026, P2 6–10 Nov, D1 11–12 Nov, D2 11–18 Nov, Q1 19–20 Nov, R1 23 Nov, R2 at the end of 23 Nov. The critical path is P1, P2, D2, Q1, R1 and R2.
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    excludes weekends
    todayMarker off

    section Platform
    P1 Provision the new cluster        :crit, p1, 2026-11-02, 4d
    P2 Configure replication            :crit, p2, after p1, 3d

    section Data
    D1 Backfill dimension tables        :d1, after p2, 2d
    D2 Backfill fact tables (2019–2025) :crit, d2, after p2, 6d

    section QA
    Q1 Reconcile row counts             :crit, q1, after d1 d2, 2d

    section Release
    R1 Write freeze                     :crit, r1, after q1, 1d
    R2 Switch dashboards                :crit, milestone, r2, after r1, 0d
```