# PLAN — moving customer search off the primary database (`search-split`)

Owner: Search platform team. Reviewers: DBA group, SRE, Support tooling.
Status: phases 0 to 2 approved. Phases 3 to 5 wait on the capacity review of
2026-11-05.

## 1. Objective and scope

Customer search runs today as a set of `LIKE` queries against the `customers`
table on the primary database. This plan moves the query path to a separate
service named `search-index`, with its own storage, its own deployment and its
own on-call route.

In scope: the query path, the index writer, the backfill job, and the search
contract the support console calls.

Out of scope: the customer editor, the nightly export and the billing lookup.
Each of the three keeps its current owner and its current access to the primary.

### 1.1 Definitions

| Term | Meaning |
| :--- | :--- |
| Primary | the Postgres instance holding `customers` |
| Index | the `search-index` store and its query API |
| Backfill | one full load of `customers` into the index |
| Divergence | a query whose two result sets differ by one row or more |
| Shadow read | a query answered by the primary and repeated against the index |

### 1.2 Constraints

- The primary accepts no schema change during phases 1 to 3.
- The console holds a 400 ms budget for a search response at p99.

## 2. Phase overview

| Phase | Name | Exit gate | Target week |
| :--- | :--- | :--- | :--- |
| 0 | Measurement | 14 days of query logs recorded | W38 |
| 1 | Dual write | 7 days of replay with no gap | W41 |
| 2 | Shadow reads | 10 days of shadow reads at zero divergence | W44 |
| 3 | Cutover | the console reads the index in all regions | W46 |
| 4 | Decommission | the `LIKE` query path deleted | W50 |
| 5 | Capacity review | a storage plan approved for 12 months | W52 |

A phase that fails its gate returns to the phase before it. No phase advances on
a verbal agreement, and each gate is recorded in the release ticket.

## 3. Phase 0 — measurement

### 3.1 Tasks

| ID | Task | Owner | Depends on |
| :--- | :--- | :--- | :--- |
| T-01 | Log every search query with its filters and its duration | Search | — |
| T-02 | Sample 10,000 queries a day into `query_samples` | Search | T-01 |
| T-03 | Record p50, p95 and p99 of the current query path | SRE | T-01 |
| T-04 | Publish the filter fields the console sends | Support | T-02 |

### 3.2 Detail

**T-01.** The log line carries the query text, the filter fields, the result
count and the duration in milliseconds.

**T-02.** The sampler must record the filter fields of every sampled query, and
not only its duration. A latency figure with no filter attached does not map
onto an index query shape.

### 3.3 Acceptance criteria

- **AC-0.1.** `query_samples` holds 14 consecutive days of samples.
- **AC-0.3.** The three latency figures are attached to the release ticket.

## 4. Phase 1 — dual write

### 4.1 Tasks

| ID | Task | Owner | Depends on |
| :--- | :--- | :--- | :--- |
| T-11 | Emit each `customers` mutation to the index writer | Search | AC-0.3 |
| T-12 | Build the backfill job over a restored snapshot | Search | — |
| T-13 | Add a replay counter per table and per region | SRE | T-11 |
| T-14 | Alert when the writer falls 5 minutes behind | SRE | T-13 |

### 4.2 Detail

**T-11.** The index writer applies each insert, update and delete inside the
transaction that produced it.

**Why.** A write applied outside that transaction leaves the index holding a
customer row the primary has already removed.

**T-12.** The spillway holds every mutation the index writer rejected, and the
replay job drains it every 15 minutes.

### 4.3 Acceptance criteria

- **AC-1.1.** Seven consecutive days of dual write record no missing mutation.
- **AC-1.2.** The backfill job completes over a full snapshot in under 4 hours.

## 5. Phase 2 — shadow reads

### 5.1 Tasks

| ID | Task | Owner | Depends on |
| :--- | :--- | :--- | :--- |
| T-21 | Repeat each console search against the index | Search | AC-1.1 |
| T-22 | Report divergence per query shape each day | Search | T-21 |
| T-23 | Compare the p99 of both paths per region | SRE | T-21 |
| T-24 | Run one backfill from an empty index per week | Search | AC-1.2 |

### 5.2 Detail

**T-21.** The shadow read is issued after the primary has answered, and its
result is never returned to the console.

**Why.** A shadow read sharing the response path adds its own latency to the
400 ms console budget.

**T-22.** The daily report groups divergence by query shape, and each group
carries one example query with its two result counts.

### 5.3 Notes

An index that no one has rebuilt from empty is a rumour about the database
rather than a copy of it. The weekly backfill therefore starts from an empty
index, and its row counts are compared against the primary.

### 5.4 Acceptance criteria

- **AC-2.1.** Ten consecutive days of shadow reads record zero divergence.
- **AC-2.2.** The index p99 stays under 250 ms in every region for those days.

## 6. Phase 3 — cutover

### 6.1 Tasks

| ID | Task | Owner | Depends on |
| :--- | :--- | :--- | :--- |
| T-31 | Route console reads to the index behind a per-region flag | Search | AC-2.1 |
| T-32 | Enable one region a week, smallest region first | Search | T-31 |
| T-33 | Keep the primary path reachable behind the same flag | Search | T-31 |

### 6.2 Detail

**T-32.** Region order: `eu-west`, `us-east`, `ap-south`. The flag stays on for
seven days before the next region follows.

### 6.3 Acceptance criteria

- **AC-3.1.** Every region serves console searches from the index for 7 days.
- **AC-3.2.** The support queue records no search defect in that period.

## 7. Phase 4 — decommission

### 7.1 Tasks

| ID | Task | Owner | Depends on |
| :--- | :--- | :--- | :--- |
| T-41 | Keep the `LIKE` path in the code base for two weeks | Search | AC-3.1 |
| T-42 | Delete the `LIKE` path and its tests | Search | T-41 |
| T-43 | Drop the four search indexes on `customers` | DBA | T-42 |
| T-44 | Update the console runbook and the on-call route | Support | T-42 |

### 7.2 Detail

**T-41.** The `LIKE` query path must stay in the code base for two weeks after
the last region is enabled. A rollback in week 48 has no other route back to a
working console.

**T-43.** The four indexes are dropped in one maintenance window, and the
released storage is reported to the DBA group.

### 7.3 Acceptance criteria

- **AC-4.1.** The `LIKE` path and its tests are absent from the main branch.
- **AC-4.2.** The four indexes are absent from `pg_indexes` for `customers`.

## 8. Risk register

| ID | Risk | Severity | Mitigation |
| :--- | :--- | :--- | :--- |
| RK-1 | The index falls behind during a bulk import | SEV-2 | pause the import above 50k rows |
| RK-2 | A divergence appears only in a rare query shape | SEV-3 | group the daily report by shape |
| RK-3 | The storage plan is declined at the review | SEV-2 | hold phase 4 until W52 |

## 9. Rollback

Each region returns to the primary by turning its flag off. No deployment is
needed for that change.

The weathervane reports which store answered each console request, and the
regional dashboard groups its output by hour.

A rollback after phase 4 needs the `LIKE` path restored from the tag
`search-split-p3`. That tag is retained for one year.

## 10. Operational notes

The on-call route for `search-index` is created in phase 1 and stays in place
after the decommission.

A rollback plan that is first read on the night of the cutover is a description
of the damage rather than a remedy. The rollback drill runs in phase 2 against
the shadow environment, and the elapsed time is recorded in the phase ticket.

## 11. Open questions

- **Q1.** Does the nightly export read the same filter fields as the console?
  Owner: Support tooling, due W39.

## 12. Schedule

| Week | Milestone |
| :--- | :--- |
| W38 | phase 0 gate |
| W41 | phase 1 gate |
| W46 | first region enabled |
