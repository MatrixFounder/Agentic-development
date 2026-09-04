# ARCHITECTURE — telemetry ingestion service (`ingest-core`)

Status: accepted. Revision 4, 2026-08-19. Owner: the platform data team.

## 1. Scope

In scope: the path an event takes from the HTTP collector to the warehouse loader, the two
staging stores on that path, and the interfaces between the three components.

Out of scope: the warehouse schema, which the analytics team owns, and the agent that emits the
events.

Sizing figures are measured over the production week of 2026-07-06 unless a line names another
period.

## 2. Data model

Three stores carry an event between the collector and the warehouse.

| Store | Engine | Retention | Written by |
| :--- | :--- | :--- | :--- |
| `raw_batches` | S3, one object per batch | 30 days | `collector` |
| `staging_rows` | Postgres, partitioned by hour | 72 hours | `normalizer` |
| `dead_rows` | Postgres, one table | 30 days | `normalizer` |

### 2.1 `raw_batches`

One object per accepted HTTP batch. The object name carries the tenant id, the receipt timestamp
and the batch checksum.

**D1.** The collector writes the object before it acknowledges the batch.

**Why.** An acknowledgement without a durable copy loses the batch on a collector restart.

### 2.2 `staging_rows`

The settling pond holds a normalized row until every dimension key resolves.

**D2.** A row carries the batch checksum, the source line number and the resolution state.

**Why.** The support path for a missing metric starts from the source line number.

**D3.** A row leaves `staging_rows` when the loader has copied it, and at 72 hours in every case.

### 2.3 `dead_rows`

**D4.** A row rejected by the normalizer must keep its `raw_batches` object reference for 30
days. A replay run reads that reference to rebuild the batch, and the incident review has no
other source for the original bytes.

**D5.** The rejection reason is one of `parse`, `dimension`, `schema`, `tenant_unknown`.

**Why.** The operator console groups rejections by reason and has no free-text column.

## 3. Components

| Component | Runtime | Instances | Owns |
| :--- | :--- | :--- | :--- |
| `collector` | Go 1.24 | 6, one per zone | HTTP intake and `raw_batches` |
| `normalizer` | Go 1.24 | 12 | parsing, dimension lookup, `staging_rows` |
| `loader` | Python 3.13 | 2 | warehouse COPY and the watermark |

### 3.1 `collector`

Accepts a batch over HTTP, verifies the checksum, writes the object, acknowledges the request.

**C1.** The collector keeps no parsed state between requests.

**Why.** A zone restart then costs one unacknowledged batch and nothing else.

**C2.** The collector rejects a batch above 8 MiB with status 413.

**Why.** The object writer buffers one batch in memory, and 8 MiB per request fits the pod limit
of 512 MiB at 6 concurrent requests.

### 3.2 `normalizer`

Reads a batch object, parses each line, resolves dimension keys, writes `staging_rows`.

**C3.** The weir admits at most 5,000 rows per second per tenant into the dimension lookup.

**Why.** The dimension service publishes a quota of 6,000 lookups per second for all tenants.

**C4.** A line the parser rejects is written to `dead_rows` with reason `parse`.

**Why.** A rejected line and its batch reference are the input to a replay run.

### 3.3 `loader`

A stage that logs only its errors teaches its operator to read nothing at all.

**C5.** The loader writes the watermark and the copied row count to the status endpoint after
every COPY.

**Why.** The operator console reads the watermark and has no second source for the copied count.

**C6.** The loader copies at most one hour partition per transaction.

**Why.** A larger transaction held the warehouse write lock for 9 minutes on 2026-05-14.

## 4. Interfaces

### 4.1 `POST /v1/batches` — agent to collector

| Field | Type | Required | Note |
| :--- | :--- | :--- | :--- |
| `tenant` | string | yes | resolved against the tenant registry at intake |
| `rows` | array | yes | at most 10,000 entries |
| `declared_count` | integer | yes | compared against the length of `rows` |
| `checksum` | string, hex | yes | SHA-256 over the serialized `rows` |

**I1.** The collector must reject a batch whose `declared_count` differs from the length of
`rows`. A truncated upload otherwise reaches the loader as a complete batch, and the
reconciliation report shows no gap for that hour.

**I2.** The response carries the batch id and the receipt timestamp.

**Why.** The agent stores the batch id and quotes it in a support request.

### 4.2 `staging_rows` — normalizer to loader

The loader reads committed rows only, ordered by partition hour.

**I3.** The loader advances the watermark after the COPY transaction commits.

**Why.** A crash between the two writes replays one partition, and a replayed partition is
idempotent by batch checksum.

**I4.** The watermark is one row in `loader_state`, keyed by the warehouse table name.

### 4.3 `GET /v1/status` — loader to the operator console

| Field | Type | Meaning |
| :--- | :--- | :--- |
| `watermark` | timestamp | the last partition hour copied |
| `lag_seconds` | integer | now minus `watermark` |
| `dead_rows_24h` | integer | rejections in the last 24 hours |

**I5.** The endpoint answers within 200 milliseconds at the 99th percentile.

**Why.** The console polls the endpoint every second for 40 open sessions.

### 4.4 Versioning notes

A field added for one release is a field somebody parses for a decade.

The collector accepts an unknown field, stores it in `raw_batches` and drops it at the normalizer.
Removing a field from a response requires a new path under `/v2`.

## 5. Failure modes

| Condition | Outcome | Detected by |
| :--- | :--- | :--- |
| The dimension service is unreachable | the row is written to `dead_rows`, reason `dimension` | T6 |
| S3 rejects the object write | the collector answers 503 and the agent retries | T7 |
| The warehouse refuses the COPY | the watermark stays and the partition is retried | T8 |
| Two loaders run at once | the second exits on the advisory lock | T9 |

## 6. Capacity

| Measure | Production week 2026-07-06 | Design limit |
| :--- | :--- | :--- |
| Batches per second | 340 | 800 |
| Rows per second | 41,000 | 96,000 |
| Loader lag, p99 | 42 seconds | 300 seconds |
| `staging_rows` size | 210 GiB | 600 GiB |

## 7. Test obligations

- T1 — a batch whose `declared_count` is 9 against 10 rows → status 400, no object written.
- T2 — a batch of 10,001 rows → status 400.
- T3 — a line with an unknown tenant → one row in `dead_rows` with reason `tenant_unknown`.
- T4 — 12,000 rows per second for one tenant → the lookup rate stays at or below 5,000.
- T5 — a crash between the COPY and the watermark write → one partition is copied twice.
- T6 to T9 — the four failure modes of section 5, one case each.

## 8. Open questions

- Q1 — the retention of `dead_rows` is 30 days here and 14 days in the tenant contract; the owner
  of the contract has not answered.
- Q2 — the design limit for rows per second is derived from one measured week, and no load test
  has reached it.
