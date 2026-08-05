# DEFECT: Nightly reporting job runs twice on the autumn DST transition and duplicates every row it writes

| Field | Value |
|---|---|
| ID | *(assign on filing)* |
| Reported | 2026-08-05 |
| Reported by | Maintainer, on-call rotation — via support ticket escalation |
| Component | Nightly reporting job / scheduler configuration |
| Type | Data corruption (silent) |
| Severity | **S2 — High** (see [Severity](#severity)) |
| Priority | **P1** — a fix must land before the next backward transition (2026-10-25 EU, 2026-11-01 US) |
| Status | Open, unassigned, not reproduced in a controlled environment |
| First observed | On a night the local clock moved backwards; detected ~7 days later |
| Regression? | Unknown — likely present since the job was first scheduled |

---

## Summary

The nightly reporting job is scheduled with a cron expression interpreted in a local time zone that observes daylight saving time. On the night the clock moves backwards, the scheduled local wall-clock time occurs twice, and the job fires twice. The job is not idempotent: the second run repeats the full write for the same logical reporting period, producing a complete duplicate set of rows.

Because the rows are inserted with freshly generated primary keys, no uniqueness constraint rejects them and no error is raised. Both runs report success. The corruption is silent and was only discovered a week later, when a customer filed a support ticket about an invoice total that was exactly double the expected amount.

## Symptom

- On the DST fall-back night, the job's execution log contains **two** successful runs for the same logical reporting date, roughly one hour apart in real time and at the *same* local wall-clock time.
- Every row written by the first run has a twin written by the second: identical business content (period, account, line item, amount), different surrogate primary key, different insert timestamp.
- No constraint violation, no error, no alert. Both runs exit zero.
- Downstream aggregates that sum these rows — invoice totals, usage summaries, any report built on `SUM`/`COUNT` over the affected table — are inflated, roughly ×2 for the affected period.
- The defect is invisible in the job's own monitoring: "ran successfully" is true twice.

## Environment

Fill in observed values before assigning; the entries below are what the reporter could confirm.

| Item | Observed | Notes |
|---|---|---|
| Scheduler | *TBD* — cron / systemd timer / Kubernetes CronJob / cloud scheduler / Quartz | **Critical to establish**: each has different backward-transition semantics |
| Schedule expression | Nightly, single fixed time inside the repeated hour (e.g. `30 1 * * *`) | Confirm exact expression |
| Time zone used to interpret the schedule | Host/container local time, DST-observing | Confirm `TZ` env var, `/etc/localtime`, and any scheduler-level `timeZone` field |
| Job runtime time zone | *TBD* | May differ from the scheduler's — confirm separately |
| Database / target table | Reporting store, surrogate PK (auto-increment or UUID) | No natural-key uniqueness constraint on the business columns |
| Job entry point | *TBD* | Confirm how the reporting period is derived (see [Suspected cause](#suspected-cause)) |

## Reproduction

The bug reproduces only when the schedule's local wall-clock time falls inside the hour that is repeated by a backward transition.

### Preconditions

1. The scheduler interprets the cron expression in a zone with an autumn DST transition (e.g. `America/New_York`, `Europe/Berlin`).
2. The scheduled time falls inside the repeated local hour — for `America/New_York`, any time in `01:00–01:59`.
3. The job's target table has a surrogate primary key and no uniqueness constraint over the business columns.

### Steps — real-clock reproduction (slow, highest fidelity)

1. Deploy the job to a staging host configured with a DST-observing local zone; schedule it inside the repeated hour.
2. Set the host clock so that the transition occurs shortly after start-up. Worked example, `America/New_York`, schedule `30 1 * * *`:
   - `01:30:00 EDT` = `05:30 UTC` — **run 1**
   - `02:00 EDT` → clock steps back to `01:00 EST`
   - `01:30:00 EST` = `06:30 UTC` — **run 2**
3. Let both runs complete.
4. Query the target table for the affected reporting period.

### Steps — fast reproduction (preferred for a regression test)

1. Invoke the job twice in immediate succession with the *same* logical reporting period, without resetting state between invocations.
2. Query the target table.

This shortcut isolates the actual defect — non-idempotent writes — from the scheduler behaviour that triggers it. Both should be covered: one test for idempotency, one for the schedule.

### Detection query

```sql
SELECT <business_key_columns>, COUNT(*) AS copies
FROM   <report_table>
WHERE  <period_column> = :affected_period
GROUP  BY <business_key_columns>
HAVING COUNT(*) > 1;
```

### Expected vs. actual

- **Expected:** the reporting period is written exactly once; a second invocation for the same period is either refused, or replaces the prior output, or is a no-op.
- **Actual:** the second invocation appends a full duplicate set. Row count for the period is 2×; every aggregate over it is inflated accordingly.

## Impact

**Data.** One full duplicate set of rows for one reporting period, per affected DST-fall-back night. Because the duplicates carry distinct primary keys and valid content, they are indistinguishable from legitimate rows by schema alone; separating them requires the insert timestamp or the run identifier, if either was recorded.

**Customer-visible.** At least one incorrect invoice reached a customer with a doubled total. Any customer whose billing draws on the affected period is potentially affected — the reported ticket is a sample, not necessarily the full set. Billing errors carry direct financial and trust cost, and possibly correction/refund obligations.

**Downstream.** Anything that read the table between the corruption and its discovery may have propagated the error: derived aggregates, exports, dashboards, warehouse loads, forecasts, and anything already sent to a customer or an external system. Fixing the source table does not retroactively fix copies that have already left it.

**Detection gap.** Seven days between corruption and discovery, and the discovery path was a customer complaint rather than any internal control. This is the most concerning part of the report: the same failure would have gone unnoticed indefinitely on data no customer inspects.

**Blast radius over time.** One backward transition per year per DST-observing zone; if the system runs jobs in several such zones, each contributes its own event. Prior years' data should be assumed affected until checked.

## Severity

**S2 — High.**

Rationale for the rating:
- Corrupts persisted data rather than merely failing (an outright failure would have been louder and cheaper).
- Silent: no error, no constraint violation, no alert; both runs self-report success.
- Escapes to customers as incorrect financial figures.
- Discovered externally, after a week — the detection latency is itself part of the defect.

Rationale for *not* rating it S1: it is time-boxed to one night a year per zone, does not affect availability, and the corruption is in principle repairable from the surviving insert metadata.

**Priority is P1 regardless of severity**: the next backward transitions are known dates (2026-10-25 for EU zones, 2026-11-01 for US zones) and the defect will recur on them by default.

## Suspected cause

Two independent faults compound. Both need addressing; fixing either alone leaves a hazard.

1. **The schedule is ambiguous.** A local wall-clock time inside the repeated hour does not identify a unique instant on a fall-back night — it names two. A scheduler that resolves the expression against local time therefore has two legitimate matches and fires for both. This is the trigger.

2. **The job is not idempotent, and probably derives its reporting period from the wall clock.** The likely mechanism: the job computes "yesterday" (or "the last 24 hours") from the local clock at start-up. On both runs that resolves to the same period, so the second run recomputes the identical result set and appends it, because writes are unconditional inserts with generated keys and there is no run-level guard, no natural-key constraint, and no "already produced for this period" check. This is the reason the trigger causes damage rather than a harmless repeat.

Fault 2 is the more serious of the two: any duplicate invocation — a manual re-run, a retry after a false-negative timeout, an operator running the job by hand — produces the same corruption on any night of the year. The DST transition is how the bug was found, not the only way it can fire.

## Contributing factors

- No uniqueness constraint expressing the business rule "one row per (period, account, line item)" — the database was not in a position to catch this.
- No reconciliation or row-count sanity check between the job and its consumers.
- Success monitoring is per-run, not per-period, so "ran twice for one period" is not an observable anomaly.

## Open questions / unknowns

These block a confident fix; the assignee should resolve them early.

1. **Which scheduler, and what are its documented backward-transition semantics?** Behaviour differs materially — some implementations deliberately suppress the repeat for fixed-time entries, others fire for every real-time match, others depend on the interval between the transition and the schedule. Until the actual scheduler and its version are confirmed, the trigger is inferred, not established.
2. **How does the job derive its reporting period?** From the wall clock at start-up, from a watermark/cursor, or from an argument? The remedy differs completely by case, and the mechanism in [Suspected cause](#suspected-cause) item 2 is currently a hypothesis.
3. **Is there a run identifier or insert timestamp on the affected rows** sufficient to distinguish the second run's output from the first? If not, cleanup is much harder and may need reconstruction from source data.
4. **Full extent of the corruption.** How many periods, how many rows, how many customers, how many prior years? Only one ticket has surfaced. The affected set has not been enumerated.
5. **How far did it propagate?** Which downstream systems, exports, and customer-facing documents consumed the affected period before discovery? Which of those are already corrected, and which are not?
6. **The symmetric spring-forward case.** When the clock jumps *forwards*, a schedule inside the skipped hour may not fire at all — producing a silently *missing* reporting period, which no aggregate anomaly would reveal. Has that already happened? It has not been checked, and it would look like nothing at all.
7. **Are there other jobs on the same schedule pattern?** The scheduler configuration has not been audited for sibling jobs with the same exposure.
8. **Concurrency.** If the two runs could ever overlap (long-running job, short transition gap), is there any interleaving hazard beyond duplication? Not investigated.

## Suggested directions (not decided)

Recorded as leads for whoever picks this up, not as a chosen design.

- Make the job idempotent for a given reporting period — the highest-value fix, and the one that also covers manual re-runs and retries. Options include a natural-key uniqueness constraint, a delete-then-insert or upsert per period, or a run ledger keyed by period.
- Express the schedule in UTC, or move it outside the hours affected by any transition, so the wall-clock time is unambiguous.
- Pass the reporting period to the job explicitly rather than deriving it from the clock at start-up.
- Add a per-period row-count/total reconciliation check that would have caught this within a day rather than a week.

## Immediate containment (before a fix lands)

1. Enumerate affected periods with the detection query; scope the customer impact.
2. Correct the affected data and reissue anything already sent, per the billing team's process.
3. Until the fix ships, treat the next backward-transition night as a manual watch: verify row counts for that period the following morning.