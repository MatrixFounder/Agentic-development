# Import service — currency validation

## 1. Scope

In scope: the row-level validation of the nightly import. Out of scope: the ledger's own rate
table, which the accounting service owns.

## 2. Requirements

| ID | Requirement | MVP? |
| :--- | :--- | :--- |
| R1 | The importer rejects a row whose currency code is not in the active set | Y |
| R2 | A rejected row is written to the quarantine table with its source line number | Y |
| R3 | The run reports the count of rejected rows before it commits | Y |

### 2.1 Detail

**R1.** The importer must reject a row whose currency code is absent from the active set. Otherwise
a stale rate reaches the ledger and the month closes on a figure nobody can reproduce.

**R2.** The quarantine row carries the source file name, the line number and the rejected code.

**Why.** The support team resolves a rejection by reading the source file at that offset.

**R3.** The run must print the rejected count to the job log before the commit. The operator
decides whether to accept a partial import, and that decision needs the number in front of it.

## 3. Failure modes

| Condition | Outcome | Detected by |
| :--- | :--- | :--- |
| The active set is empty | the run aborts before the first row | T4 |
| The quarantine table is unreachable | the run aborts and commits nothing | T5 |

## 4. Test obligations

- T1 — a row with code `XYZ` and an active set of `USD, EUR` → the row is quarantined.
- T2 — a row with code `EUR` and the same active set → the row is imported.
- T3 — 40 rows, 3 rejected → the log holds the value 3; fails when the counter is reset per batch.
