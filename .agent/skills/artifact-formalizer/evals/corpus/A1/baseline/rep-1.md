# TASK-081 — Per-Key Rate Limiting, Shared Burst Allowance, and Client Retry Contract

| Field | Value |
| --- | --- |
| Document type | Technical specification (TASK) |
| Status | Draft — for review |
| Version | 0.1 |
| Date | 2026-08-05 |
| Owner | API Platform |
| Reviewers | Backend, SRE, Developer Relations, Support |
| Related | Incidents INC-2041, INC-2098 (connection pool exhaustion) |

---

## 1. Problem

The public HTTP API has no rate limiting of any kind. Every authenticated request is admitted and
runs to completion regardless of who sent it, how many are already in flight, or how expensive the
work is.

Three properties of the current traffic make this untenable:

1. **Load is concentrated.** A small number of API keys generate the majority of requests. There is
   no mechanism to bound any single key's consumption, so the service's availability is a function
   of the best-behaved client's discipline rather than of anything we control.
2. **Load is bursty.** Aggregate traffic is not smooth; clients batch work and fire it in short,
   dense bursts. A limiter tuned to average throughput would reject legitimate traffic, and a
   limiter tuned to peak throughput would provide no protection.
3. **A single client has twice caused a full outage.** On both occasions one misbehaving key opened
   enough concurrent long-running requests to exhaust the shared database connection pool. Every
   other client — including clients making trivial requests — then failed, because connection
   checkout blocked. Recovery required manually revoking the key.

The second point deserves emphasis for design purposes: **the outages were caused by concurrency,
not by request rate.** A key issuing 20 requests per second that each hold a database connection for
5 seconds occupies 100 connections in steady state. A request-rate limit alone does not bound
in-flight work when latency rises, and rising latency is precisely the condition under which the
pool is scarce. Any solution that only counts requests per second would not have prevented either
incident.

There is also no contract with clients about what to do when they are refused. Today a refusal
looks like a timeout or a 500, so well-behaved clients retry immediately and aggressively, which
amplifies the original overload. We need clients to back off correctly, which means we need to tell
them how — in the response, and in the documentation.

### 1.1 Goals

- Bound the load any single API key can place on the service, in both rate and concurrency.
- Absorb legitimate short bursts without rejecting well-behaved clients.
- Protect the database connection pool as a first-class, explicitly reserved resource.
- Give throttled clients a machine-readable, documented, unambiguous retry contract.
- Make limiter behaviour observable, tunable per key, and reversible without a deploy.

### 1.2 Non-goals

See §8 (Out of scope).

---

## 2. Assumptions

These are the assumptions the design rests on. Any that turn out to be false will change the
requirements they support; each is either confirmed before implementation or converted into an open
question in §7.

| ID | Assumption |
| --- | --- |
| A-01 | Every request to the public API carries an API key and is authenticated before any limiting decision is made. Unauthenticated traffic is handled elsewhere (see §8, OOS-05). |
| A-02 | An API key maps to exactly one customer account and exactly one service tier. |
| A-03 | The API is served by multiple stateless instances behind a load balancer; limiting must therefore be coordinated across instances, not per-process. |
| A-04 | A Redis (or API-compatible) instance is available to the API tier with sub-millisecond p99 round-trip latency, and is already an operational dependency or may become one. |
| A-05 | The database connection pool is shared by all request-handling instances and its total size is a known, fixed number (assumed 100 for the sizing in §4.4). |
| A-06 | Request cost is unequal across endpoints and can be approximated by a static per-route weight. |
| A-07 | We can identify the current top-consuming keys and their owners well enough to notify them before enforcement begins. |

---

## 3. Glossary

| Term | Meaning |
| --- | --- |
| **Key** | An API key; the unit of identity, quota, and accounting. |
| **Tier** | A named policy bundle (rate, burst, concurrency) assigned to a key. |
| **Token bucket** | A bucket of capacity *B* refilled at *R* tokens/second; a request consumes tokens equal to its cost and is admitted only if enough remain. |
| **Sustained rate** | The bucket refill rate *R* — the throughput a key may hold indefinitely. |
| **Burst capacity** | The bucket size *B* — how far above the sustained rate a key may go after an idle period. |
| **Shared burst pool** | A single global token bucket that keys may draw from *after* exhausting their own bucket, bounded per key. |
| **Cost** | The number of tokens a request consumes, derived from its route weight. |
| **Concurrency slot** | Permission to hold one database connection; bounded per key and globally. |
| **Throttled** | Rejected by the limiter with 429 or 503, as opposed to failing for any other reason. |

---

## 4. Design overview

### 4.1 Enforcement point and order

Limiting is implemented as middleware in the API request pipeline, positioned **after**
authentication (so the key and tier are known) and **before** routing to the handler (so no
handler-side resource — most importantly a database connection — is acquired for a request that
will be refused).

Each request passes through the following gates in order. The first gate that refuses the request
terminates it; no later gate is consulted.

1. **Resolve policy.** Look up the key's tier and any per-key overrides. Missing or invalid key →
   the existing 401 path; the limiter records nothing and makes no decision.
2. **Compute cost.** Look up the route's weight (§4.3).
3. **Per-key rate gate.** Attempt to consume `cost` tokens from the key's own bucket.
4. **Shared burst gate.** If the key's bucket is short, attempt to consume the shortfall from the
   shared burst pool, subject to the key's per-window draw cap.
5. **Per-key concurrency gate.** Acquire a concurrency slot for the key. If none is free, wait up to
   a short bounded interval, then refuse.
6. **Global admission gate.** If total in-flight database-bound work exceeds the reserved ceiling,
   shed load starting with the lowest tier.
7. **Admit.** Dispatch to the handler; release the concurrency slot when the response completes,
   including on error, timeout, and client disconnect.

### 4.2 Why a token bucket

A token bucket expresses "sustained rate" and "burst tolerance" as two independent parameters,
which is exactly the shape of the problem: we want to permit short dense bursts while bounding
long-run throughput. Fixed windows permit a 2× burst across a window boundary and produce
synchronized retry storms at window reset; sliding-window counters are more storage-expensive and
still express burst tolerance only implicitly. See D-01.

### 4.3 Request cost

Cost is a static per-route weight, resolved from configuration, defaulting to 1.

| Route pattern | Weight | Rationale |
| --- | --- | --- |
| `GET /v1/health`, `GET /v1/status` | 0 | Must never be throttled; used by client monitoring. |
| Default (all other routes) | 1 | Baseline. |
| `GET /v1/search` | 5 | Fan-out query, disproportionate database time. |
| `POST /v1/reports/*` | 10 | Long-running aggregation; the dominant contributor to both incidents. |

Weights are configuration, not code, and are changeable without a deploy (FR-19).

### 4.4 Proposed initial policy

These values are a starting proposal derived from current traffic percentiles and a 100-connection
pool; they are subject to OQ-01 and are configuration, not contract.

| Tier | Sustained rate (tokens/s) | Burst capacity (tokens) | Max concurrent DB-bound requests | Shared-pool draw cap |
| --- | --- | --- | --- | --- |
| `free` | 5 | 25 | 4 | 10 tokens / minute |
| `standard` | 50 | 200 | 16 | 120 tokens / minute |
| `partner` | 200 | 800 | 48 | 480 tokens / minute |
| `internal` | not rate-limited (observed only) | — | 64 | n/a |

**Shared burst pool:** capacity 2,000 tokens, refill 500 tokens/second, global across all keys and
instances.

**Global reservation:** at most 80 of the 100 database connections may be held by request handlers;
the remaining 20 are reserved as headroom for background jobs, migrations, and operator access. The
sum of per-key concurrency caps deliberately exceeds 80 — the global gate, not the per-key caps, is
what enforces the pool ceiling. Per-key caps exist to ensure no single key can reach it alone.

### 4.5 State and coordination

Limiter state lives in Redis and is manipulated by a single Lua script per decision, making the
read-modify-write of the per-key bucket, the shared pool, and the draw cap atomic. Time comes from
Redis `TIME`, not from instance clocks, so instance clock drift cannot skew refill (D-04).

- Bucket key: `rl:v1:{sha256(api_key)[:16]}` — the raw key is never used as a Redis key, logged, or
  emitted in metrics (FR-22).
- Concurrency slots: a Redis-backed counter per key with a TTL-based lease, so a crashed instance
  cannot leak slots permanently. Lease TTL is the request timeout plus a small margin.
- All limiter state is ephemeral. Loss of the store loses accounting, not durable data.

### 4.6 Degradation

If Redis is unavailable or exceeds a latency budget, the limiter does **not** fail open. Each
instance falls back to a local in-process token bucket provisioned with `tier_rate / instance_count`
(instance count from service discovery, floored at 1). This is less accurate than the coordinated
limiter and will over-restrict a key whose traffic is unevenly balanced across instances, but it
preserves the property that motivated the work: no single key can exhaust the pool. The fallback is
announced in metrics and alerts. See D-05.

The per-key and global concurrency gates are enforced locally in every instance regardless of Redis
availability, since the local in-flight count is always known.

---

## 5. Requirements

Priority uses RFC 2119 keywords: **MUST** = required for launch, **SHOULD** = required unless a
stated reason prevents it, **MAY** = optional.

### 5.1 Functional — per-key quotas

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | The system MUST enforce a per-key token bucket with independently configurable sustained rate and burst capacity. | MUST |
| FR-02 | The bucket MUST be shared across all API instances, so that a key's limit is a property of the key and not of the number of instances or of load-balancer routing. | MUST |
| FR-03 | Each request MUST consume tokens equal to its route's configured cost weight; routes with weight 0 MUST never be rate-limited. | MUST |
| FR-04 | Policy MUST be resolved per key from a named tier, with support for per-key overrides of any tier parameter. | MUST |
| FR-05 | Per-key overrides MUST take effect within 60 seconds of being changed, without a deploy or restart. | MUST |
| FR-06 | The system MUST support an `internal` (or equivalent) tier that is observed and metered but not enforced. | MUST |
| FR-07 | Rate-limit decisions MUST be made after authentication and before any database connection is acquired for the request. | MUST |
| FR-08 | The limiter MUST add no more than 5 ms to p99 request latency for admitted requests. | MUST |

### 5.2 Functional — shared burst allowance

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-09 | The system MUST provide a single global burst pool that a key MAY draw from only after its own bucket is exhausted. | MUST |
| FR-10 | Each key's draw from the shared pool MUST be capped per rolling window, so that one key cannot consume the pool alone. | MUST |
| FR-11 | Shared-pool draws MUST be atomic with respect to concurrent requests from all keys and all instances; the pool MUST NOT be over-drawn under concurrency. | MUST |
| FR-12 | Shared-pool capacity, refill rate, and per-tier draw caps MUST be runtime-configurable (FR-19). | MUST |
| FR-13 | The system SHOULD prefer serving a shared-pool draw to a higher tier over a lower tier when the pool is contended. | SHOULD |

### 5.3 Functional — concurrency and pool protection

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-14 | The system MUST enforce a per-key ceiling on concurrently in-flight database-bound requests, independent of request rate. | MUST |
| FR-15 | The system MUST enforce a global ceiling on concurrently in-flight database-bound requests, set strictly below the database connection pool size, leaving a configured reserve for non-request workloads. | MUST |
| FR-16 | A request that cannot acquire a concurrency slot MUST wait no longer than a configured bounded interval (default 50 ms) before being refused. | MUST |
| FR-17 | Concurrency slots MUST be released on every terminal outcome — success, handler error, timeout, and client disconnect — and MUST NOT be leakable by an instance crash. | MUST |
| FR-18 | When the global ceiling is reached, the system MUST shed load in ascending tier order (lowest tier first) rather than uniformly. | MUST |

### 5.4 Functional — operability

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-19 | All limiter parameters (tier values, weights, pool settings, ceilings) MUST be runtime configuration, changeable without a deploy and effective within 60 seconds. | MUST |
| FR-20 | The limiter MUST support an **observe-only mode**, globally and per tier, in which decisions are computed, headers emitted, and metrics recorded, but no request is refused. | MUST |
| FR-21 | A global kill switch MUST disable enforcement within 60 seconds without a deploy. | MUST |
| FR-22 | Raw API keys MUST NOT appear in logs, metrics labels, traces, or limiter storage keys; a stable non-reversible key identifier MUST be used instead. | MUST |
| FR-23 | The system MUST emit per-decision metrics labelled by tier, route, decision (`allowed`, `allowed_from_shared_pool`, `throttled_rate`, `throttled_concurrency`, `shed_global`), and key identifier. | MUST |
| FR-24 | The system MUST emit gauges for shared-pool fill level, global in-flight count, and database pool utilisation. | MUST |
| FR-25 | The system MUST alert when: a key is throttled continuously for more than 5 minutes; the shared pool is empty for more than 1% of any 5-minute interval; the limiter enters degraded (local-fallback) mode; or global shedding occurs at all. | MUST |
| FR-26 | Per-key consumption MUST be queryable by support staff for at least 30 days, to answer "why was I throttled" tickets. | SHOULD |

### 5.5 Functional — client-facing contract

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-27 | Every response to an authenticated request, throttled or not, MUST include `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` describing the key's own bucket. | MUST |
| FR-28 | A request refused for exceeding a rate or concurrency limit MUST return HTTP **429**. | MUST |
| FR-29 | A request refused by global load shedding MUST return HTTP **503**. | MUST |
| FR-30 | Every 429 and every 503 emitted by the limiter MUST include a `Retry-After` header as an integer number of seconds, with a value of at least 1. | MUST |
| FR-31 | The `Retry-After` value for a rate refusal MUST be the time until the key's bucket holds enough tokens for the refused request, rounded up to the next whole second. | MUST |
| FR-32 | Throttled responses MUST carry an `application/problem+json` body (RFC 9457) with a stable `type` URI, a human-readable `detail`, and the limit that was hit. | MUST |
| FR-33 | Throttled responses MUST distinguish which limit was hit (per-key rate, shared pool exhausted, per-key concurrency, global shed) via a machine-readable field in the problem body. | MUST |
| FR-34 | The 429 body MUST NOT disclose other keys' consumption, the shared pool's absolute size, or global in-flight counts. | MUST |
| FR-35 | The retry contract (§5.6) MUST be published in the public API documentation before enforcement begins. | MUST |
| FR-36 | Throttled requests MUST NOT be counted against the customer's billable usage. | SHOULD |

### 5.6 The retry contract

This is the normative statement to be published to clients (FR-35) and the behaviour the server
commits to.

**The server commits to:**

- Returning 429 when a client-attributable limit is exceeded, and 503 when the service is shedding
  load globally.
- Including `Retry-After`, in integer seconds, on every such response.
- Making `Retry-After` a sufficient wait: a client that waits exactly that long and retries a
  request of the same cost will not be refused for the same reason, absent new traffic from that
  key.
- Never returning 429 for `GET /v1/health` or `GET /v1/status`.
- Never using 429 or 503 to signal a malformed, unauthorized, or otherwise permanently failing
  request.

**The client is required to:**

1. **Honour `Retry-After`.** Do not retry before it elapses. A retry that arrives earlier is
   refused again and consumes nothing but the client's own quota headroom.
2. **Add exponential backoff with full jitter on top.** For attempt *n* (0-indexed), wait
   `Retry-After + random_uniform(0, min(60, 1 × 2ⁿ))` seconds. The jitter is mandatory: without it,
   all clients throttled by the same event retry in the same instant and reproduce the burst.
3. **Cap retries.** At most 5 attempts per logical operation, and at most 60 seconds of computed
   backoff per attempt. After exhausting retries, surface the failure; do not loop indefinitely.
4. **Retry only what is retryable.** 429 and 503 are retryable. 400, 401, 403, 404, 409, and 422 are
   not, and retrying them is treated as abuse.
5. **Send `Idempotency-Key` on retried non-idempotent requests** (`POST`, `PATCH`), reusing the same
   value across all attempts of one logical operation, so a retry after an ambiguous timeout cannot
   duplicate an effect.
6. **Use `RateLimit-Remaining` proactively.** Clients running batch work should pace themselves from
   the headers on successful responses rather than driving to 429 and recovering.

**Worked example.** A `standard`-tier key exhausts its bucket at *t*=0 and is refused with
`Retry-After: 3`. First retry at *t* ≈ 3 + U(0,1); if refused again with `Retry-After: 2`, second
retry at *t* ≈ 5 + U(0,2); and so on, to a maximum of five attempts.

### 5.7 Non-functional

| ID | Requirement | Priority |
| --- | --- | --- |
| NFR-01 | Limiter overhead MUST NOT exceed 5 ms at p99 for admitted requests (restates FR-08 as a measured budget). | MUST |
| NFR-02 | The limiter MUST sustain the service's peak request rate plus 100% headroom without becoming the bottleneck. | MUST |
| NFR-03 | Unavailability of the limiter's coordination store MUST NOT make the API unavailable; behaviour degrades per §4.6. | MUST |
| NFR-04 | The limiter MUST NOT fail open on the concurrency gates under any failure mode, including store unavailability. | MUST |
| NFR-05 | Decisions MUST be consistent across instances to within one refill interval; a key MUST NOT observe materially different limits from different instances. | MUST |
| NFR-06 | The limiter MUST be deployable and enable-able independently of any client change, and revertible via FR-21 within 60 seconds. | MUST |
| NFR-07 | Limiter storage MUST hold no personal data and no raw credentials (see FR-22). | MUST |
| NFR-08 | Configuration changes to limits MUST be audit-logged with actor, timestamp, previous and new value. | SHOULD |

---

## 6. Use cases

### UC-01 — Well-behaved client under its limit

**Actor:** Client with a `standard` key.
**Precondition:** Key is issuing 20 req/s against a 50 token/s sustained limit.
**Flow:** Every request is admitted. Each response carries `RateLimit-Limit: 50`, a `RateLimit-Remaining`
that stays comfortably positive, and `RateLimit-Reset`.
**Postcondition:** No behavioural change from today; latency increased by no more than the limiter
budget (NFR-01).
**Covers:** FR-01, FR-27, FR-08.

### UC-02 — Legitimate short burst absorbed by the key's own bucket

**Actor:** Client running a nightly sync.
**Precondition:** Key idle for several minutes; bucket full at 200 tokens.
**Flow:** Client fires 180 requests in under a second. All are admitted from accumulated burst
capacity. `RateLimit-Remaining` falls to near zero; the client's own pacing logic slows to the
sustained rate.
**Postcondition:** No 429 is returned; the burst is absorbed as designed.
**Covers:** FR-01, FR-27.

### UC-03 — Burst exceeding the key's bucket, served by the shared pool

**Actor:** Client whose burst slightly exceeds its own capacity.
**Precondition:** Key's bucket is empty; the shared pool has tokens; the key has not exhausted its
per-window draw cap.
**Flow:** The shortfall is drawn from the shared pool and the request is admitted. Metrics record
the decision as `allowed_from_shared_pool`.
**Postcondition:** The client sees success; operators can see, per key, how much of the shared pool
is being consumed and by whom.
**Covers:** FR-09, FR-10, FR-11, FR-23.

### UC-04 — Key exceeds its rate limit and is throttled

**Actor:** Client running an unpaced backfill.
**Precondition:** Key's bucket is empty and its shared-pool draw cap is exhausted.
**Flow:** The request is refused with 429, `Retry-After: 3`, `RateLimit-Remaining: 0`, and a
`problem+json` body identifying the per-key rate limit as the cause. The client's SDK waits
3 seconds plus jitter and retries; the retry succeeds.
**Postcondition:** The customer's backfill completes more slowly; no other customer is affected.
**Covers:** FR-28, FR-30, FR-31, FR-32, FR-33, §5.6.

### UC-05 — The incident case: one key attempts to monopolise the connection pool

**Actor:** The misbehaving client from INC-2041 / INC-2098.
**Precondition:** Client opens 200 concurrent `POST /v1/reports/*` requests, each holding a database
connection for seconds.
**Flow:** The first 16 (the `standard` per-key concurrency cap) acquire slots and proceed. The
remainder wait up to 50 ms, fail to acquire a slot, and are refused with 429 and a body identifying
the concurrency limit. As earlier requests complete, slots free and later retries are admitted.
**Postcondition:** The key's database usage is bounded at 16 connections out of 100. Other
customers are unaffected. No manual key revocation is required.
**Rationale:** This is the case a rate-only limiter would not have caught (§1).
**Covers:** FR-14, FR-16, FR-17, FR-28, FR-33.

### UC-06 — Aggregate overload with no single guilty key

**Actor:** Many keys, each individually within its limits.
**Precondition:** Global in-flight database-bound requests reach the reserved ceiling of 80.
**Flow:** New requests are shed lowest-tier-first with 503 and `Retry-After`. `partner` and
`internal` traffic continues. An alert fires (FR-25). The reserve of 20 connections remains
available for background jobs and operator access.
**Postcondition:** The service degrades in a controlled, prioritised way instead of failing
uniformly.
**Covers:** FR-15, FR-18, FR-29, FR-30.

### UC-07 — Coordination store outage

**Actor:** Operator; Redis becomes unavailable.
**Precondition:** Enforcement is on.
**Flow:** Instances detect the failure within the latency budget and fall back to local per-instance
buckets at `tier_rate / instance_count`. Concurrency gates continue to be enforced locally at full
strength. A degradation alert fires.
**Postcondition:** The API remains available; limits become approximate and somewhat stricter; the
pool remains protected.
**Covers:** NFR-03, NFR-04, §4.6, FR-25.

### UC-08 — Support investigates a throttling complaint

**Actor:** Support engineer.
**Precondition:** A customer reports unexpected 429s over the past week.
**Flow:** Support looks up the key's identifier (never the raw key), reviews per-key decision
history and which limit was hit, and either explains the client's burst pattern or raises a
per-key override.
**Postcondition:** The question is answerable from data; an override, if granted, takes effect in
under a minute without a deploy.
**Covers:** FR-05, FR-22, FR-23, FR-26.

### UC-09 — Operator rolls out enforcement, then rolls it back

**Actor:** Operator.
**Precondition:** Limiter deployed in observe-only mode.
**Flow:** Operator reviews a week of would-have-throttled metrics, adjusts tier values, then enables
enforcement for the `free` tier only. An unexpected surge of legitimate 429s appears; the operator
returns that tier to observe-only within a minute.
**Postcondition:** Enforcement can be introduced and withdrawn per tier without a deploy and without
client-visible instability.
**Covers:** FR-19, FR-20, FR-21, NFR-06.

---

## 7. Acceptance criteria

Each criterion is independently verifiable. Method: **U** unit, **I** integration, **L** load test,
**M** manual/operational drill.

| ID | Criterion | Verifies | Method |
| --- | --- | --- | --- |
| AC-01 | Given a key with sustained 50/s and burst 200, when 200 requests of cost 1 arrive within 100 ms after an idle period, then all 200 are admitted and the 201st within the same second is refused with 429. | FR-01, FR-03 | I |
| AC-02 | Given the same key, when requests arrive at a steady 50/s for 10 minutes, then zero are refused and `RateLimit-Remaining` never reaches 0 for more than one consecutive second. | FR-01 | L |
| AC-03 | Given traffic for one key balanced across 4 instances, when it exceeds the key's limit, then the total admitted rate is within ±5% of the configured single-key limit — i.e. the limit does not scale with instance count. | FR-02, NFR-05 | L |
| AC-04 | Given a request to `GET /v1/search` (weight 5), when it is admitted, then exactly 5 tokens are deducted; given `GET /v1/health` (weight 0), then it is admitted and no tokens are deducted even when the bucket is empty. | FR-03 | U |
| AC-05 | Given a per-key override raising a key's sustained rate, when the override is written, then the new limit is observed in production within 60 seconds with no deploy or restart. | FR-04, FR-05, FR-19 | I, M |
| AC-06 | Given a key on the `internal` tier exceeding every configured limit, then no request is refused and metrics record the would-be decisions. | FR-06, FR-20 | I |
| AC-07 | Given a request that will be refused, then no database connection is checked out for it, verified by pool checkout instrumentation showing zero checkouts attributable to refused requests. | FR-07 | I |
| AC-08 | Given production-representative load, then limiter overhead measured as p99 latency delta against a control build is ≤ 5 ms. | FR-08, NFR-01 | L |
| AC-09 | Given a key whose own bucket is empty and whose draw cap is unexhausted, when the shared pool has tokens, then the request is admitted and reported as `allowed_from_shared_pool`. | FR-09, FR-23 | I |
| AC-10 | Given one key attempting to draw continuously from the shared pool, then its draws stop at its per-window cap and other keys can still draw from the pool in the same window. | FR-10 | I |
| AC-11 | Given 500 concurrent requests from 50 keys all drawing on a 2,000-token shared pool, then the total tokens dispensed never exceeds the pool's capacity plus refill for the interval — no over-draw under concurrency. | FR-11 | L |
| AC-12 | Given a `standard` key with a concurrency cap of 16, when it opens 200 concurrent long-running requests, then at most 16 hold database connections at any instant, the remainder receive 429 identifying the concurrency limit, and the total pool utilisation attributable to that key never exceeds 16. | FR-14, FR-16, FR-33 | L |
| AC-13 | Given the scenario of AC-12 running against a full production-shaped workload, then requests from all other keys continue to succeed with p99 latency within 20% of baseline — i.e. INC-2041/INC-2098 does not reproduce. | FR-14, FR-15 | L |
| AC-14 | Given a request that is admitted and then times out, errors, or whose client disconnects, then its concurrency slot is released within the request timeout plus lease margin. | FR-17 | I |
| AC-15 | Given an instance killed with slots held, then those slots become available within the lease TTL without operator action. | FR-17 | I, M |
| AC-16 | Given global in-flight work at the ceiling, when new requests arrive from `free` and `partner` keys, then `free` is shed with 503 first and `partner` continues to be admitted; global in-flight never exceeds the configured ceiling, and the connection reserve is never consumed by request handlers. | FR-15, FR-18, FR-29 | L |
| AC-17 | Given the kill switch is set, then enforcement stops within 60 seconds across all instances with no deploy, and every request that would have been refused is admitted. | FR-21, NFR-06 | I, M |
| AC-18 | Given any log line, metric series, trace, or limiter storage key produced by the limiter, then no raw API key appears in any of them, verified by an automated scan over a full test run. | FR-22, NFR-07 | I |
| AC-19 | Given any authenticated response, including 2xx, 429, and 503, then `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` are present and internally consistent. | FR-27 | I |
| AC-20 | Given a 429 or a limiter-issued 503, then `Retry-After` is present, is an integer, and is ≥ 1. | FR-30 | I |
| AC-21 | Given a 429 with `Retry-After: N`, when the client waits exactly N seconds and retries an identical request with no other traffic on that key, then the retry is admitted. | FR-31, §5.6 | I |
| AC-22 | Given any throttled response, then its body is `application/problem+json`, validates against the published schema, carries a stable `type` URI, and names which of the four limits was hit. | FR-32, FR-33 | I |
| AC-23 | Given any throttled response body, then it contains no other key's consumption, no absolute shared-pool size, and no global in-flight count. | FR-34 | I |
| AC-24 | Given the public documentation at enforcement go-live, then it states the retry contract of §5.6 in full, including the jitter formula, the retry cap, the retryable status list, and the idempotency requirement. | FR-35 | M |
| AC-25 | Given a throttled request, then it does not appear in the customer's billable usage records. | FR-36 | I |
| AC-26 | Given the coordination store is made unavailable, then the API continues to serve requests, per-key rate limiting degrades to local buckets rather than failing open, concurrency gates remain fully enforced, and a degradation alert fires within 60 seconds. | NFR-03, NFR-04, FR-25 | I, M |
| AC-27 | Given a key throttled continuously for 5 minutes, or the shared pool empty for >1% of a 5-minute interval, or any global shedding, then the corresponding alert fires. | FR-25 | M |
| AC-28 | Given a support engineer with a key identifier, then per-key decision history for the last 30 days is retrievable, including which limit was hit. | FR-26 | M |
| AC-29 | Given limits are changed in configuration, then an audit record exists with actor, timestamp, and previous and new values. | NFR-08 | I |

**Launch gate.** Enforcement is not enabled in production until AC-01 through AC-24 and AC-26 pass,
and one week of observe-only data (§9, Phase 1) shows the proposed limits would throttle no more
than the agreed share of currently-legitimate traffic (threshold set under OQ-01).

---

## 8. Out of scope

| ID | Excluded | Note |
| --- | --- | --- |
| OOS-01 | Billing, metering, and paid quota upgrades. | The limiter emits usage signals; monetising them is separate work. |
| OOS-02 | Per-user, per-IP, or per-organisation limiting. | The key is the only unit of identity in this task. IP-based limiting is a different control with different failure modes (NAT, proxies). |
| OOS-03 | Abuse detection, anomaly scoring, and automatic key suspension. | The limiter bounds damage; it does not judge intent. |
| OOS-04 | WAF, DDoS mitigation, and volumetric attack defence at the network edge. | Handled by infrastructure upstream of the application. |
| OOS-05 | Limiting of unauthenticated endpoints, including login and key issuance. | Depends on a different identity signal; tracked separately. |
| OOS-06 | Fair-queueing or priority scheduling of admitted requests. | Admitted requests are served first-come-first-served; only *admission* is prioritised (FR-18). |
| OOS-07 | Client SDK changes implementing the retry contract. | This task defines and documents the contract; SDK adoption is a follow-up per language. |
| OOS-08 | Response caching or deduplication to reduce load. | Complementary, but an independent piece of work. |
| OOS-09 | Resizing the database connection pool, adding read replicas, or query optimisation. | The reserve in FR-15 assumes the pool as it is today. |
| OOS-10 | Retroactive enforcement or credit for past overage. | Enforcement is forward-looking from go-live. |
| OOS-11 | Cross-region coordination of the shared burst pool. | Deferred; see OQ-04. |

---

## 9. Decisions taken

| ID | Decision | Rationale | Consequence |
| --- | --- | --- | --- |
| D-01 | Use a **token bucket** per key, not a fixed or sliding window. | Expresses sustained rate and burst tolerance as independent parameters, which is exactly what bursty traffic requires. Fixed windows allow a 2× boundary burst and cause synchronized retry storms at reset. | Two parameters per tier to tune instead of one; `RateLimit-Reset` is computed from refill rather than read off a window edge. |
| D-02 | Enforce a **per-key concurrency cap in addition to** the rate limit. | Both incidents were caused by concurrent long-lived requests holding connections, not by request rate; a rate limit alone would not have prevented them. | A second gate and a second class of 429, both of which must be documented and observable. |
| D-03 | Coordinate state in **Redis with an atomic Lua script**, not in-process. | The limit must be a property of the key, not of instance count or routing (FR-02); the bucket, shared pool, and draw cap must be updated atomically or the pool can be over-drawn. | Adds an operational dependency in the request path, mitigated by D-05. |
| D-04 | Take time from **Redis `TIME`**, not from instance clocks. | Instance clock drift would otherwise cause inconsistent refill and reproducible over-admission. | One extra value returned by the script; no NTP assumptions. |
| D-05 | **Do not fail open.** On store unavailability, degrade to local per-instance buckets at `tier_rate / instance_count`; keep concurrency gates at full strength. | Failing open reintroduces exactly the outage this work exists to prevent, and does so at the moment the system is least healthy. | Limits become approximate and somewhat stricter during a store outage; this is explicitly accepted (NFR-04). |
| D-06 | The shared burst pool is **global and drawn only after the key's own bucket is exhausted**, with a per-key per-window draw cap. | A pool that keys draw from first would be trivially monopolised by the heaviest key and would provide no protection. | Requires per-key draw accounting in addition to pool accounting. |
| D-07 | Use **429 for client-attributable refusals and 503 for global shedding.** | The two carry different meanings for the client: 429 means "you are over your allowance"; 503 means "we are over ours". Conflating them makes client behaviour and our own dashboards ambiguous. | Two documented paths in the retry contract; both carry `Retry-After`. |
| D-08 | **`Retry-After` is mandatory on every throttled response** and must be a sufficient wait. | Without it, clients guess, and guessing produces the retry storms that amplify overload. Making it *sufficient* is what allows the client contract to require honouring it. | The limiter must compute time-to-sufficient-tokens, not emit a constant. |
| D-09 | Require **exponential backoff with full jitter on top of `Retry-After`**, not `Retry-After` alone. | All clients throttled by a single event receive similar `Retry-After` values and would otherwise retry in the same instant, reproducing the burst. | The published contract is slightly more demanding of clients; the jitter formula is stated explicitly (§5.6). |
| D-10 | Use the widely-deployed **`RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset`** header triple. | Already understood by existing client libraries and tooling; the newer structured-field form is not yet broadly supported. | Revisit under OQ-05; if we later adopt the structured form, both may be emitted during a transition. |
| D-11 | Throttled responses use **`application/problem+json` (RFC 9457)** with a stable `type` URI. | Gives clients a machine-readable reason and gives us a documentation anchor per limit type, rather than a free-text string clients will end up parsing. | A published problem-type registry that must be kept stable. |
| D-12 | **Never log or store raw API keys**; use a truncated SHA-256 identifier everywhere, including storage keys. | The limiter touches every request; a key leak through logs or metrics would be a credential incident of the widest possible scope. | Support tooling resolves identifiers to accounts through the existing key store, not through limiter data. |
| D-13 | Ship in **observe-only mode first**, enforce per tier, and keep a kill switch. | We do not yet know how much currently-legitimate traffic the proposed limits would refuse; guessing wrong and enforcing immediately converts a reliability fix into an outage. | Enforcement is gated on a week of observe-only data (§7, launch gate). |
| D-14 | **Reserve database connections** for non-request work rather than letting handlers consume the whole pool. | Both incidents removed operator and background-job access precisely when it was needed to recover. | Nominal request throughput ceiling is 80% of the pool. |
| D-15 | Weight requests by **static per-route cost**, not by measured cost. | Static weights are predictable for clients and cannot be gamed by a request that turns out cheap; dynamic costing cannot be known before admission, which is when the decision must be made (FR-07). | Weights need periodic review as endpoint behaviour changes; they are configuration (FR-19). |

---

## 10. Open questions

| ID | Question | Why it matters | Owner | Needed by |
| --- | --- | --- | --- | --- |
| OQ-01 | What are the actual tier values, and what share of currently-legitimate traffic may they refuse? The values in §4.4 are a proposal, not an analysis. | Sets the launch gate threshold (§7) and determines whether enforcement is safe at all. | API Platform + SRE | End of observe-only phase |
| OQ-02 | Which tier do existing keys map to by default, and who approves exceptions? | Every current customer must land somewhere; a wrong default throttles paying customers on day one. | Product + Support | Before Phase 2 |
| OQ-03 | What notice period do we owe existing clients before enforcement, and are any commercial commitments in place that guarantee unlimited throughput? | May legally or contractually block enforcement for specific accounts. | Legal + Sales | Before Phase 2 |
| OQ-04 | Is the shared burst pool global or per-region? | A global pool needs cross-region coordination in the request path, with the latency and failure-mode consequences that implies (currently OOS-11). | Architecture | Before implementation |
| OQ-05 | Do we emit the newer structured-field `RateLimit` / `RateLimit-Policy` headers alongside the legacy triple? | Affects the published contract and client library compatibility; changing it later is a breaking documentation change. | API Platform + DevRel | Before Phase 1 |
| OQ-06 | Should a concurrency refusal be 429 or 503? It is client-attributable (arguing for 429) but is also a resource-exhaustion condition (arguing for 503). Current decision is 429 per D-07. | Determines client retry behaviour for the exact case that caused both incidents. | API Platform | Before Phase 1 |
| OQ-07 | How do we treat the two keys implicated in INC-2041 and INC-2098 during rollout — enforce immediately, or give the same notice as everyone else? | They are the concrete risk the work addresses; a long notice period leaves the exposure open. | SRE + Support | Before Phase 1 |
| OQ-08 | Should throttled requests count toward any quota or billing at all (FR-36 is currently SHOULD)? | Affects revenue recognition and whether a client can be charged for being refused. | Finance + Product | Before Phase 2 |
| OQ-09 | Do internal service-to-service callers traverse this limiter, and if so, is `internal` permanently observe-only or eventually enforced? | An unbounded internal tier can exhaust the pool exactly as an external key can. | Architecture | Before Phase 2 |
| OQ-10 | Is a dedicated Redis instance provisioned for the limiter, or is an existing one shared? | A shared instance couples limiter availability to unrelated workloads and makes the degraded path (D-05) more likely. | SRE | Before implementation |
| OQ-11 | Is `Idempotency-Key` currently honoured on all non-idempotent endpoints? The retry contract (§5.6, item 5) requires it. | If not, the published contract instructs clients to send a header we ignore, and retries can duplicate effects. | Backend | Before FR-35 is published |
| OQ-12 | Do we expose a "current usage" endpoint so clients can pace themselves without driving to 429? | Would reduce throttling for large batch clients; adds public API surface not currently in scope. | Product + DevRel | Post-launch |

---

## 11. Rollout plan

| Phase | Content | Exit condition |
| --- | --- | --- |
| 0 | Implement limiter; deploy disabled. Unit and integration criteria (AC-01…AC-11, AC-14, AC-18…AC-23, AC-25, AC-29) pass in CI. | All targeted criteria green. |
| 1 | Enable **observe-only** in production for all tiers. Collect would-have-throttled data per key. Publish the retry contract (FR-35, AC-24). Notify the top consuming keys and the two incident keys (OQ-07). | One week of clean data; OQ-01, OQ-05, OQ-06 resolved. |
| 2 | Enable **enforcement of concurrency gates only**, all tiers. | AC-12, AC-13, AC-16 pass under production load; no unexpected 429 volume for 72 hours. |
| 3 | Enable **rate and shared-pool enforcement** for `free`, then `standard`, then `partner`, one tier at a time with at least 48 hours between. | Throttle rate per tier within the OQ-01 threshold; no rollback triggered. |
| 4 | Steady state: dashboards and alerts owned by SRE; tier values reviewed monthly. | — |

**Rollback.** At any phase, the kill switch (FR-21, AC-17) returns the system to observe-only within
60 seconds with no deploy. Rollback triggers: throttle rate exceeding the OQ-01 threshold for any
tier, any increase in p99 latency attributable to the limiter beyond NFR-01, or entry into degraded
mode lasting more than 15 minutes.

---

## 12. Risks

| ID | Risk | Mitigation |
| --- | --- | --- |
| RK-01 | Limits set too low refuse legitimate traffic and break customers. | Observe-only phase, per-tier rollout, per-key overrides effective in 60 s, kill switch (D-13). |
| RK-02 | The limiter becomes a new single point of failure in the request path. | Degraded local mode, concurrency gates enforced locally regardless of store state (D-05, NFR-03). |
| RK-03 | Clients ignore `Retry-After` and retry immediately, amplifying overload. | Retry-storm behaviour is bounded by the limiter itself — a non-compliant retry is refused cheaply before any connection is acquired (FR-07). Contract published and SDK follow-up tracked (OOS-07). |
| RK-04 | Static cost weights drift out of line with actual endpoint cost. | Weights are configuration (FR-19) with a monthly review in Phase 4; per-route latency dashboards make drift visible. |
| RK-05 | Concurrency slot leases leak on repeated instance churn, over-restricting a key. | TTL-based leases sized to request timeout plus margin; AC-15 covers crash recovery. |
| RK-06 | The shared pool is consumed by a handful of keys, so it provides no benefit to the clients it was intended for. | Per-key draw caps (FR-10), tier-ordered preference (FR-13), and per-key shared-pool metrics (FR-23) to detect it. |