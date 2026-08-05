# DEF-318 — `nightly-report` writes every row twice on the backward DST transition

| Field | Value |
| :--- | :--- |
| Id | `DEF-318` |
| Filed | 2025-11-03 |
| Reporter | reporting-platform maintainer |
| Component | job `nightly-report`, table `report_rows` |
| Version | `reporting:2.14.0` |
| Severity | `SEV-2` |
| Status | `open`, cause unconfirmed |
| First occurrence | 2025-10-26 |
| Noticed via | `SUP-4471`, 2025-11-02 |

**Scope.** In scope: `report_rows` and its consumers for business date 2025-10-25. Out of scope: the upstream ingestion pipeline (owned by data-platform).

---

## 1. Symptom

`nightly-report` runs from the cron entry `15 2 * * *` in zone `Europe/Berlin`.

On 2025-10-26 the local time 02:15 occurred twice. The scheduler started the job at 02:15 CEST and again at 02:15 CET. Both runs wrote a complete result set for business date 2025-10-25.

Each row takes its key from the `bigserial` column `report_rows.id`. The duplicate rows differ from the originals in `id` and `created_at` only. No unique constraint rejects the second set.

Measured with:

```sql
SELECT business_date, count(*)
FROM report_rows
WHERE business_date BETWEEN '2025-10-24' AND '2025-10-26'
GROUP BY business_date;
```

| `business_date` | rows |
| :--- | :--- |
| 2025-10-24 | 41802 |
| 2025-10-25 | 83604 |
| 2025-10-26 | 41802 |

83604 = 2 × 41802.

## 2. Reproduction

Preconditions:

- image `reporting:2.14.0`;
- `TZ=Europe/Berlin`;
- `report_rows` empty;
- `libfaketime` installed in the container.

Steps:

1. Start the container with `TZ=Europe/Berlin`. Postcondition: `date` prints an offset of `+0200`.
2. Set the fake clock to `2025-10-26 01:50:00 CEST`. Postcondition: `date` prints that timestamp.
3. Install the crontab entry `15 2 * * * /usr/local/bin/nightly-report`. Postcondition: `crontab -l` lists exactly one entry.
4. Advance the fake clock at 60× until `03:10 CET`. Postcondition: the job log holds two `run started` lines, at offsets `+0200` and `+0100`.
5. Run the count query from §1. Postcondition: business date 2025-10-25 holds 83604 rows.

Reproduced on 3 of 3 attempts.

**Test obligation.** `T-DST-1` — the step sequence above → `report_rows` holds 41802 rows for 2025-10-25; fails when the deduplication guard is removed. The test is red until a fix lands.

## 3. Impact

- Every aggregate over `report_rows` for 2025-10-25 → returns twice the delivered volume (detected by the count query in §1).
- Invoice `INV-2025-10-88213` states a doubled total. The customer raised `SUP-4471`.
- The defect stayed unobserved for 7 days, from 2025-10-26 to 2025-11-02.
- No unique index and no downstream check reports the condition. Discovery depended on a customer reading an invoice.
- The count of further affected invoices is not yet established (`OQ-2`).

## 4. Severity

Severity: `SEV-2`.

Applied vocabulary: `SEV-1` (data loss or outage), `SEV-2` (incorrect data reaches a customer), `SEV-3` (incorrect data stays internal), `SEV-4` (cosmetic).

**Why.** A doubled total reached a customer invoice ⇒ `SEV-2`. Not `SEV-1`: no row was lost and the job stayed available.

## 5. Suspected cause

Two conditions are suspected. Duplication requires both.

- `C1` — the scheduler starts a wall-clock entry twice inside a repeated local hour. Evidence: two `run started` lines carry the same local time and the offsets `+0200` and `+0100`.
- `C2` — `report_rows` carries no unique index over `(business_date, entity_id, metric)`. Evidence: the DDL declares `PRIMARY KEY (id)` only, and `id` is `bigserial`.

Why both are required:

- `C1` without `C2` → the second run replaces the first result set; totals stay correct.
- `C2` without `C1` → the job writes once per business date; no duplicate appears.

Confirmation step: add the unique index in a test database, then repeat §2. The second run then fails on the constraint, and `C2` is confirmed.

Status of this section: suspected. The production scheduler is not yet identified (`OQ-3`), so `C1` rests on log evidence alone.

## 6. Workaround

Delete the later result set:

```sql
DELETE FROM report_rows
WHERE business_date = '2025-10-25'
  AND created_at >= '2025-10-26 02:00:00+01';
```

Postcondition: the count query from §1 returns 41802 for 2025-10-25.

The workaround repairs one date. The next backward transition falls on 2026-10-25 and reproduces the defect.

## 7. Open questions

- `OQ-1` — Did the backward transitions of 2023 and 2024 duplicate the same table? Blocks: the backfill range. Owner: reporting-platform maintainer.
- `OQ-2` — How many issued invoices read the duplicated rows? Blocks: the customer correction plan. Owner: billing owner.
- `OQ-3` — Which scheduler runs the entry in production, and does it suppress the repeated hour? Blocks: confirmation of `C1`. Owner: platform on-call.
- `OQ-4` — Is the fix a UTC schedule, an idempotent write, or both? Blocks: the fix design. Owner: reporting-platform maintainer.
- `OQ-5` — Does the forward transition on 2026-03-29 skip a run instead? Blocks: whether one fix covers both directions. Owner: reporting-platform maintainer.
- `OQ-6` — Does this project use the severity vocabulary quoted in §4? Blocks: the priority of `DEF-318`. Owner: reporting-platform maintainer.