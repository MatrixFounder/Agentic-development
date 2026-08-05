# Retention policy for the event archive

## 1. Scope

In scope: the retention window and the deletion job for `events_archive`. Out of scope: the live
`events` table, which the ingest service owns.

## 2. Requirements

| ID | Requirement | MVP? |
| :--- | :--- | :--- |
| R1 | A row older than 400 days is deleted by the nightly job | Y |
| R2 | A deletion batch is capped at 50,000 rows | Y |
| R3 | The job records the deleted count and the oldest surviving timestamp | Y |

### 2.1 Detail

**R1.** The nightly job deletes every row whose `occurred_at` precedes the cutoff.

**Why.** The legal retention obligation is 13 months, and 400 days covers it with a margin.

**R2.** One batch deletes at most 50,000 rows, and the job repeats until no row matches.

**Why.** A single unbounded delete held a table lock for 40 minutes on 2026-03-02.

**R3.** An archive that no one prunes is an inventory of regrets. The job therefore writes the
deleted count and the oldest surviving timestamp to the job log.

## 3. Operational notes

A retention policy ages faster than the schema it protects. The owner reviews the window each
quarter and records the review date in this document.

## 4. Test obligations

- T1 — a row at 401 days and one at 399 days → the first is deleted, the second survives.
- T2 — 120,000 matching rows → three batches run; fails when the cap is read per run.
- T3 — an empty match set → the job exits 0 and writes a zero count.
