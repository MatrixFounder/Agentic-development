# TASK-XXXX — Rate limiting for the public HTTP API

| Field | Value |
| --- | --- |
| Status | Draft — for review |
| Author | TBD |
| Reviewers | API team, SRE, Support (client-facing contract) |
| Target component | Public HTTP API edge / gateway middleware |
| Related | (link the two connection-pool exhaustion incidents here) |
| Last updated | 2026-08-05 |

---

## 1. Problem

The public HTTP API has no rate limiting of any kind. Every authenticated request is admitted and
proceeds to the application tier, where it may acquire a database connection.

Observed characteristics of the traffic:

- **Concentration.** A small number of API keys account for the majority of requests. The load
  distribution is heavy-tailed, not uniform; average-rate provisioning does not describe it.
- **Burstiness.** Load arrives in short spikes rather than a steady stream. Any control that only
  bounds a long-window average will either throttle legitimate spikes or fail to contain them.
- **Demonstrated blast radius.** One misbehaving client has twice exhausted the database connection
  pool. Because the pool is a shared, fixed-size resource, a single key degraded or halted service
  for every other client. Both incidents were mitigated manually.

Consequences today:

1. There is no mechanism to contain a runaway client other than manual intervention (revoking a key,
   or a network-level block). Time-to-mitigate is bounded by human response time.
2. There is no defined contract telling clients what to do when the service is under pressure. The
   API returns connection errors, timeouts, or 5xx, all of which encourage immediate client retries
   and amplify the incident.
3. Capacity planning has no enforcement counterpart: quotas exist, at best, as expectations in
   commercial agreements rather than as behaviour of the system.

**A note on the failure mode.** Pool exhaustion was caused by *concurrency*, not by request rate
alone. A client issuing 10 requests per second that each hold a connection for 20 seconds occupies
~200 connections while staying under any plausible per-second rate limit. Request-rate limiting is
therefore necessary but **not sufficient** to prevent a recurrence of the two incidents; a bound on
in-flight, database-bound requests per key is also required. This specification covers both.

### 1.1 What the team wants

- Per-key quotas.
- A shared burst allowance, so that spare capacity can absorb legitimate spikes instead of being
  stranded inside per-key ceilings.
- A documented retry contract for throttled clients.

---

## 2. Goals and non-goals

**Goals**

- G-1 — No single API key can consume enough of the database connection pool to degrade other
  clients.
- G-2 — Each key has an enforced, configurable request budget.
- G-3 — Short spikes from well-behaved clients succeed when the system has headroom.
- G-4 — Throttled clients receive a machine-readable, unambiguous instruction on when to retry, and
  the documented behaviour is followed by the official SDKs.
- G-5 — Operators can change a key's limits, or exempt a key, without a deploy.
- G-6 — Rollout is observable and reversible before it is enforcing.

**Non-goals** (see also §10, Out of scope)

- Not a fairness scheduler or a QoS system with priority classes.
- Not a defence against distributed abuse across many keys, or against credential-stuffing and
  similar attacks on the authentication path.
- Not a replacement for capacity planning, autoscaling, or connection-pool sizing.

---

## 3. Decisions taken

These are settled and constrain the requirements below. Alternatives considered are recorded so the
decisions can be revisited if their premises change.

| ID | Decision | Rationale | Rejected alternative |
| --- | --- | --- | --- |
| D-1 | Enforce **two independent controls**: a request-rate limit and a per-key cap on concurrent in-flight database-bound requests. Both must pass for a request to be admitted. | Rate alone does not bound pool occupancy (§1). Concurrency alone does not bound cost or protect non-DB resources. | Rate limiting only — does not address the incidents that motivated the work. |
| D-2 | Rate control uses a **token bucket** per key: sustained refill rate `r` tokens/sec, bucket capacity `b` tokens (the per-key burst allowance). | Naturally expresses "sustained rate plus burst" in two parameters; no boundary effect at window edges. | Fixed window (allows 2× the limit across a boundary); sliding-window log (higher memory and CPU cost per request). |
| D-3 | A key that has emptied its own bucket may borrow from a **shared burst pool** — a single global token bucket, refilled at a fixed rate, from which any key may draw, subject to a per-key borrowing cap. | Delivers the requested "shared burst allowance": stranded headroom is lent out, but no key can drain the pool alone. | Per-key burst only (no sharing — spikes fail while the system is idle); unlimited borrowing (reproduces the original failure mode). |
| D-4 | State is held in **Redis**, mutated by a single Lua script per decision (atomic check-and-consume). | Already operated by the team; a Lua script gives atomicity across API nodes in one round trip. | In-process counters per node (limits become node-count-dependent and wrong under uneven load balancing); the primary database (adds load to the resource being protected — self-defeating). |
| D-5 | On Redis unavailability the limiter **fails open** to a per-node local limiter sized at `global_budget / expected_node_count`, and raises an alert. | A limiter outage must not become an API outage. The local fallback still bounds the blast radius, approximately. | Fail closed (converts a dependency blip into a full outage); fail open with no fallback (removes all protection exactly when the system is unhealthy). |
| D-6 | Throttled requests receive **HTTP 429** with a `Retry-After` header and an RFC 9457 problem-details body. Concurrency rejections also use 429, distinguished by the `code` field. | One status code, one retry contract for clients; the distinction is available to those who want it. | 503 for concurrency (implies server fault and invites different, often more aggressive, retry behaviour). |
| D-7 | Rate-limit state is exposed on **every** response (not only 429s) via `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`. | Lets well-behaved clients pace themselves *before* being throttled, which is the cheapest possible enforcement. | Headers on 429 only (clients can only react after failing). |
| D-8 | Rejected requests **do not consume tokens**, but repeated rejection **lengthens** the advertised `Retry-After` for that key, up to a cap. | Avoids a spiral where a hammering client can never recover; still increases the cost of ignoring the contract. | Charging rejected requests (a client stuck in a retry loop can never drain its way out). |
| D-9 | The shared pool's remaining capacity is **not** exposed to clients. | It is a global signal; exposing it invites clients to race for it and leaks aggregate load information. | Advertising pool state per response. |
| D-10 | The feature ships behind a per-environment mode switch with three states: `off`, `observe` (evaluate and record, admit everything), `enforce`. | Makes the rollout reversible and lets limits be tuned against real traffic before anyone is throttled. | Enforcing rollout with a config-only rollback (no way to validate limits against production traffic first). |
| D-11 | Keys are identified in limiter state and logs by a **salted hash**, never in plaintext. | The limiter's storage and telemetry must not become a secondary place credentials leak from. | Storing raw keys in Redis / log lines. |

---

## 4. Requirements

Priority: **M** = must have for launch, **S** = should have, **C** = could have (later increment).

### 4.1 Functional — identification and configuration

| ID | Pri | Requirement |
| --- | --- | --- |
| FR-1 | M | The limiter SHALL identify the subject of a limit as the API key presented on the request, using a salted hash of the key as the state and log identifier (D-11). |
| FR-2 | M | Requests with a missing, malformed, or unrecognised API key SHALL be limited by source IP under a separate, lower policy, and SHALL be rejected before any database access occurs. |
| FR-3 | M | Each key SHALL be assigned a **policy** defining: sustained rate `r` (requests/sec), per-key burst capacity `b` (tokens), per-key concurrency cap `c` (in-flight DB-bound requests), and shared-pool borrowing cap `s` (tokens per borrowing interval). |
| FR-4 | M | Policies SHALL be assignable by **tier** (a named default set) and overridable **per key**. A per-key override takes precedence over its tier. |
| FR-5 | M | Policy and tier configuration SHALL be changeable at runtime and take effect within 60 seconds across all API nodes, without a deploy or restart (G-5). |
| FR-6 | S | An operator SHALL be able to place a key on an **exemption list** (no rate limit, concurrency cap still applies) with a mandatory expiry timestamp. Concurrency remains enforced because it is the pool-safety control. |
| FR-7 | M | Every configuration change (tier edit, per-key override, exemption, mode switch) SHALL be recorded in an audit log with actor, timestamp, previous value, and new value. |

### 4.2 Functional — rate limiting

| ID | Pri | Requirement |
| --- | --- | --- |
| FR-8 | M | For each request, the limiter SHALL atomically attempt to consume the request's cost in tokens from the key's bucket, refilled continuously at rate `r` up to capacity `b` (D-2, D-4). |
| FR-9 | M | If the key's bucket has insufficient tokens, the limiter SHALL attempt to consume the shortfall from the **shared burst pool** (D-3), subject to FR-10 and FR-11. |
| FR-10 | M | A single key SHALL NOT borrow more than `s` tokens from the shared pool within any rolling 60-second interval. |
| FR-11 | M | Borrowing from the shared pool SHALL be permitted only while the pool's fill level is at or above a configured floor (default 20% of capacity), so that the pool cannot be fully drained and a reserve remains for newly arriving spikes. |
| FR-12 | M | If neither source can satisfy the request, the limiter SHALL reject it per FR-16. The rejected request SHALL NOT consume tokens from either bucket (D-8). |
| FR-13 | S | Request **cost** SHALL be configurable per route, defaulting to 1 token. Routes known to be expensive (bulk export, search, report generation) SHALL be assigned a higher cost. The cost table is part of runtime configuration (FR-5). |
| FR-14 | M | Limit decisions SHALL be evaluated at the API edge, before authentication of the request body, business logic, or any database access, so that a rejection is cheap. |

### 4.3 Functional — concurrency protection

| ID | Pri | Requirement |
| --- | --- | --- |
| FR-15 | M | The system SHALL maintain a count of in-flight **database-bound** requests per key across all API nodes, and SHALL reject a request whose admission would exceed that key's cap `c` (D-1). |
| FR-16 | M | The system SHALL maintain a **global** in-flight budget, sized as a fraction of the database connection pool, and SHALL reject requests that would exceed it regardless of per-key state. |
| FR-17 | M | In-flight counts SHALL be released on request completion **and** on timeout, disconnect, or panic. A leaked slot must not permanently reduce a key's capacity. Slots SHALL additionally carry a TTL exceeding the maximum request timeout as a backstop. |
| FR-18 | S | The per-key cap `c` SHALL default such that no single key can occupy more than 15% of the global in-flight budget. |

### 4.4 Functional — throttle response and retry contract

| ID | Pri | Requirement |
| --- | --- | --- |
| FR-19 | M | A throttled request SHALL receive **HTTP 429 Too Many Requests** (D-6). |
| FR-20 | M | Every 429 SHALL include a `Retry-After` header containing an integer number of seconds, value ≥ 1, computed as the time until enough tokens exist to satisfy a cost-1 request (rate rejection) or a fixed backoff (concurrency rejection). |
| FR-21 | M | Every 429 SHALL include an `application/problem+json` body (RFC 9457) with at least: `type`, `title`, `status`, `detail`, `code`, `retry_after_seconds`. `code` SHALL be one of `rate_limit_exceeded`, `concurrency_limit_exceeded`, `global_capacity_exceeded`. |
| FR-22 | M | **All** responses to key-authenticated requests, including 2xx and non-429 errors, SHALL carry `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` (delta-seconds) describing the key's own bucket (D-7). |
| FR-23 | S | Responses SHALL carry a `RateLimit-Policy` header naming the applied policy and its parameters, so that support can diagnose from a single response capture. |
| FR-24 | M | Responses SHALL NOT expose the shared pool's fill level or the borrowing decision (D-9). |
| FR-25 | M | The `Retry-After` value for a key that continues to be rejected SHALL increase (default: doubling per consecutive rejection interval, capped at 60 seconds) and SHALL reset to the computed value once the key is admitted again (D-8). |
| FR-26 | M | 429 responses SHALL be safe to cache never: `Cache-Control: no-store`. |
| FR-27 | M | The retry contract SHALL be published in the public API documentation, stating: honour `Retry-After`; on repeated 429 use exponential backoff with full jitter, base = `Retry-After`, cap 60 s; retry automatically only for idempotent methods, or non-idempotent methods carrying an idempotency key; give up after a documented attempt limit and surface the error. |
| FR-28 | S | The official client SDKs SHALL implement FR-27 as their default behaviour. |

### 4.5 Functional — modes, observability, operations

| ID | Pri | Requirement |
| --- | --- | --- |
| FR-29 | M | The limiter SHALL support modes `off`, `observe`, `enforce` per environment (D-10). In `observe`, decisions are computed and recorded, headers are emitted, and no request is rejected. |
| FR-30 | M | The system SHALL emit metrics, labelled by tier and outcome (and by key hash only at a bounded cardinality — see OQ-6): requests evaluated, admitted, rejected by reason; tokens borrowed from the shared pool; shared-pool fill level; in-flight count per key (p50/p99) and globally; limiter decision latency; limiter backend errors and fallback activations. |
| FR-31 | M | Each rejection SHALL be logged once with key hash, policy, reason code, and advertised `Retry-After`; rejection logging SHALL be rate-limited per key so that a runaway client cannot flood the logging pipeline. |
| FR-32 | M | Alerts SHALL fire on: limiter backend unavailability / fallback active; global in-flight budget above a threshold; a key sustaining rejections for longer than a configured period (a signal for Support to reach out). |
| FR-33 | S | A read-only operator endpoint or dashboard SHALL show, for a given key hash, its effective policy, current bucket level, in-flight count, and recent rejection counts. |

### 4.6 Non-functional

| ID | Pri | Requirement |
| --- | --- | --- |
| NFR-1 | M | Limiter overhead SHALL add no more than **2 ms at p99** and 1 ms at p50 to request latency, measured at the edge. |
| NFR-2 | M | A limit decision SHALL require at most **one** round trip to the limiter backend. |
| NFR-3 | M | The limiter SHALL NOT read from or write to the primary application database on the request path (D-4). |
| NFR-4 | M | Enforcement SHALL be correct across all API nodes concurrently; measured admission over any 60-second window SHALL not exceed the configured rate by more than **5%**. |
| NFR-5 | M | Limiter backend unavailability SHALL NOT cause API unavailability (D-5); the fallback path SHALL engage within 1 second of detection and SHALL be exercised by a test. |
| NFR-6 | M | Limiter state SHALL expire automatically (TTL) so that dormant keys consume no storage. Storage growth SHALL be O(active keys), not O(issued keys). |
| NFR-7 | M | Plaintext API keys SHALL NOT appear in limiter state, logs, metric labels, traces, or error messages (D-11). |
| NFR-8 | S | Enabling `enforce` mode and rolling back to `observe` SHALL each take effect within 60 seconds and require no deploy. |

---

## 5. Use cases

**UC-1 — Client operating within its quota.**
A client on the `standard` tier sends requests below its sustained rate. Every request is admitted.
Each response carries `RateLimit-Remaining`, which the client's SDK uses to pace itself.
*Covers: FR-8, FR-22.*

**UC-2 — Legitimate spike inside the key's own burst allowance.**
A client's nightly job fires 80 requests in two seconds against a policy of `r=10/s, b=100`. The
bucket absorbs the spike; all requests are admitted; the bucket refills over the following seconds.
*Covers: FR-8.*

**UC-3 — Spike exceeding the key's burst, shared pool has headroom.**
The same job fires 150 requests. The key's bucket covers 100; the remaining 50 are drawn from the
shared burst pool, which is above its floor and within the key's borrowing cap. All requests
succeed. The borrowing is visible in metrics but not in the responses.
*Covers: FR-9, FR-10, FR-11, FR-24, FR-30.*

**UC-4 — Spike exceeding both allowances.**
Several large clients spike simultaneously. The shared pool falls to its floor. Further borrowing is
refused; requests beyond each key's own bucket receive 429 with a `Retry-After` derived from that
key's refill rate. Clients that stay within their own buckets are unaffected — the pool's floor is
what preserves that property.
*Covers: FR-11, FR-12, FR-19, FR-20.*

**UC-5 — Runaway client, the incident that motivated this work.**
A client opens a large number of concurrent long-running queries. Its request *rate* stays within
policy, so the rate limiter admits it, but its in-flight count reaches cap `c`. Every further request
from that key is rejected with `concurrency_limit_exceeded` until slots free. The key can occupy at
most 15% of the global in-flight budget, so the connection pool is never exhausted and other clients
see no degradation. An alert fires (FR-32) and Support is notified.
*Covers: FR-15, FR-16, FR-17, FR-18, FR-21, FR-32.*

**UC-6 — Throttled client retries correctly.**
A client receives 429 with `Retry-After: 3`. The SDK waits a jittered interval of at least 3 seconds,
retries the idempotent request, and succeeds. Total requests sent during the throttle period are
bounded.
*Covers: FR-20, FR-27, FR-28.*

**UC-7 — Throttled client ignores the contract.**
A client retries immediately in a tight loop. Rejections cost it no tokens, so it is not driven
further into debt, but its advertised `Retry-After` escalates towards the 60-second cap. Rejections
are served at the edge without touching the database, and the rejection log for that key is
rate-limited.
*Covers: FR-12, FR-14, FR-25, FR-31.*

**UC-8 — Limiter backend outage.**
Redis becomes unreachable. The limiter fails open to per-node local buckets sized at
`global_budget / expected_node_count`, emits `limiter_fallback_active`, and alerts. The API keeps
serving; enforcement is approximate until the backend recovers, at which point the shared state
resumes.
*Covers: FR-30 (fallback metric), NFR-5, D-5.*

**UC-9 — Operator raises a customer's limit.**
Support receives a request for a temporary increase. An operator edits the per-key override; the new
policy is effective on all nodes within 60 seconds; the change is captured in the audit log with
actor and previous value. No deploy occurs.
*Covers: FR-4, FR-5, FR-7.*

**UC-10 — Unauthenticated or invalid key.**
A request arrives with no key or an unknown key. It is limited by source IP under the anonymous
policy and rejected at the edge, before any database access — so a flood of invalid keys cannot
consume connections.
*Covers: FR-2, FR-14.*

**UC-11 — Rollout in observe mode.**
The limiter is enabled in `observe` for two weeks. Metrics show which keys *would* have been
throttled and how often. Two tier defaults are adjusted, three keys receive overrides, affected
customers are notified, and only then is `enforce` switched on.
*Covers: FR-29, D-10, §8.*

---

## 6. Acceptance criteria

Each criterion is a test that must pass before the feature is enabled in `enforce` mode in
production. Load-based criteria are run against a staging environment sized comparably to
production.

| ID | Criterion | Verifies |
| --- | --- | --- |
| AC-1 | A key with policy `r=10/s, b=20` driven at 50 req/s for 60 s receives no more than 630 admitted responses (600 sustained + 20 burst, +5% tolerance) and the remainder 429; verified with traffic split across at least 3 API nodes. | FR-8, NFR-4 |
| AC-2 | With the shared pool at full and a key's own bucket empty, a burst is admitted up to the key's borrowing cap `s` and rejected beyond it. Repeating within the same 60-second interval yields no further borrowing. | FR-9, FR-10 |
| AC-3 | With the shared pool driven to its floor by other keys, a key that stays within its own bucket experiences **zero** rejections. | FR-11 |
| AC-4 | With `c=12`, a key issuing 100 concurrent requests that each hold a connection for 10 s never has more than 12 in flight; the remainder receive 429 with `code=concurrency_limit_exceeded`. | FR-15, FR-21 |
| AC-5 | Under the reproduction of the original incident (single key, high concurrency, slow queries), database connection pool utilisation stays below 80% and the p99 latency of a second, well-behaved key increases by less than 10% versus baseline. | G-1, FR-15, FR-16, FR-18 |
| AC-6 | Killing a request mid-flight (client disconnect), and separately a request that times out, each release the in-flight slot within 1 s; after 1 000 such events the key's in-flight count returns to 0. | FR-17 |
| AC-7 | Every 429 carries `Retry-After` (integer ≥ 1), `Cache-Control: no-store`, and a problem-details body validating against the published schema, with `code` from the defined set. | FR-19, FR-21, FR-26 |
| AC-8 | Waiting exactly `Retry-After` seconds after a rate-limit 429 and retrying results in a 2xx, for each tier. | FR-20 |
| AC-9 | 2xx, 4xx, and 5xx responses to key-authenticated requests all carry `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`; no response carries shared-pool state. | FR-22, FR-24 |
| AC-10 | A client retrying with zero delay sees `Retry-After` escalate towards 60 s and, on backing off and succeeding, sees it reset. Rejections are served without a database query (verified by query-count instrumentation) and rejection log volume per key stays below the configured ceiling. | FR-25, FR-14, FR-31 |
| AC-11 | With the limiter backend stopped: the API continues to serve, the fallback limiter engages within 1 s, the fallback metric and alert fire, and no request returns 5xx attributable to the limiter. On restart, shared enforcement resumes without operator action. | NFR-5, D-5 |
| AC-12 | A tier change and a per-key override each take effect on all nodes within 60 s of being saved, with no restart; both appear in the audit log with actor, timestamp, old and new values. | FR-5, FR-7 |
| AC-13 | An exemption removes rate limiting for the key while the concurrency cap still rejects at `c`; the exemption expires automatically at its stated time. | FR-6 |
| AC-14 | In `observe` mode, a key driven far above its policy receives zero 429s, while metrics report the would-be rejections. Switching to `enforce` and back to `observe` each take effect within 60 s. | FR-29, NFR-8 |
| AC-15 | Limiter overhead measured at the edge under production-like load is ≤ 2 ms at p99 and ≤ 1 ms at p50, with exactly one backend round trip per decision. | NFR-1, NFR-2 |
| AC-16 | A grep of limiter state, application logs, metric labels, and traces produced during the full test suite finds zero plaintext API keys. | NFR-7, D-11 |
| AC-17 | Requests with a missing or unknown key are rejected at the edge and produce zero database queries. | FR-2, FR-14 |
| AC-18 | Limiter state for a key idle beyond the TTL is absent from the backend; total key count in the backend tracks active keys, not issued keys. | NFR-6 |
| AC-19 | The public documentation page describing the retry contract is published, and the official SDKs' default retry behaviour matches it (verified by an SDK integration test against a server forced to 429). | FR-27, FR-28 |

---

## 7. Traceability

| Goal | Requirements | Use cases | Acceptance |
| --- | --- | --- | --- |
| G-1 pool safety | FR-15…FR-18, FR-16 | UC-5 | AC-4, AC-5, AC-6 |
| G-2 per-key quotas | FR-1, FR-3, FR-4, FR-8, FR-13 | UC-1, UC-10 | AC-1, AC-17 |
| G-3 spikes absorbed | FR-9…FR-11 | UC-2, UC-3, UC-4 | AC-2, AC-3 |
| G-4 retry contract | FR-19…FR-28 | UC-6, UC-7 | AC-7, AC-8, AC-9, AC-10, AC-19 |
| G-5 runtime operation | FR-5, FR-6, FR-7, FR-33 | UC-9 | AC-12, AC-13 |
| G-6 safe rollout | FR-29, FR-30, FR-32, NFR-5, NFR-8 | UC-8, UC-11 | AC-11, AC-14 |

---

## 8. Rollout

1. **Ship dark.** Deploy in `off`. Confirm no latency or error-rate change.
2. **Observe (≥ 2 weeks, covering at least one monthly peak).** Switch to `observe`. Collect
   would-be-rejection rates per key and per tier. Set tier defaults so that fewer than 1% of
   currently well-behaved keys would be throttled at their normal peak.
3. **Publish.** Release the retry-contract documentation (FR-27) and updated SDKs (FR-28). Notify,
   individually, every key that `observe` shows would be throttled, with its measured numbers and a
   date.
4. **Enforce concurrency first.** Enable `enforce` for the concurrency caps only. This is the control
   that addresses the incidents and affects the fewest clients.
5. **Enforce rate limiting**, one tier at a time, lowest-traffic tier first.
6. **Steady state.** Review rejection metrics weekly for the first month; treat a sustained rejection
   rate on a paying key as a support signal (FR-32), not merely as correct behaviour.

Rollback at any step is a mode switch back to `observe` (NFR-8).

---

## 9. Open questions

| ID | Question | Blocks | Owner / needed by |
| --- | --- | --- | --- |
| OQ-1 | What is the actual database connection pool size, per node and in total, and what fraction may the API safely commit as the global in-flight budget (FR-16)? All concurrency defaults derive from this number. | FR-16, FR-18, AC-5 | SRE — before implementation of §4.3 |
| OQ-2 | What are the concrete tier definitions (`r`, `b`, `c`, `s`) and which existing customers map to which tier? Proposed starting point, to be validated in `observe`: free `r=1/s, b=20, c=4, s=20`; standard `r=10/s, b=100, c=12, s=100`; partner `r=100/s, b=500, c=25, s=300`. | FR-3, FR-4 | Product + SRE — before step 2 of §8 |
| OQ-3 | Are quotas contractually committed anywhere (existing agreements, published documentation, sales commitments)? Enforcement must not violate a commitment already made. | FR-4, §8 step 3 | Commercial / Legal — before `enforce` |
| OQ-4 | Should limits be scoped to the API key, or to the account/organisation that owns it? A customer holding ten keys can currently multiply any per-key limit by ten. | FR-1, FR-3 | Product — before implementation |
| OQ-5 | Header naming: emit the widely deployed `RateLimit-Limit` / `-Remaining` / `-Reset` triple, or align with the IETF `draft-ietf-httpapi-ratelimit-headers` structured-field form (`RateLimit`, `RateLimit-Policy`)? Emitting both during a transition is possible but doubles the surface we must keep correct. | FR-22, FR-23 | API team — before step 3 of §8 |
| OQ-6 | What per-key metric cardinality is acceptable? Per-key labels are the most useful diagnostic signal and the easiest way to overwhelm the metrics backend. Proposal: per-key series only for the top N keys by volume plus any key currently being rejected. | FR-30 | SRE |
| OQ-7 | Does the API support idempotency keys today? FR-27's guidance on retrying non-idempotent requests depends on the answer; if not, the contract must say "do not retry automatically" for those methods. | FR-27, FR-28 | API team — before documentation is published |
| OQ-8 | Which endpoints warrant a cost above 1, and what are the costs (FR-13)? Requires per-endpoint latency and database-time data. | FR-13 | API team — may follow launch |
| OQ-9 | How is "database-bound request" determined for the in-flight count — every request, or only routes known to acquire a connection? Counting every request is simpler and safer; counting only DB routes is more precise and needs a per-route classification that must be kept current. | FR-15 | API team — before implementation |
| OQ-10 | Is a dedicated Redis instance required for the limiter, or is the existing shared instance acceptable? The limiter is on the request path of every call; sharing an instance couples API availability to whatever else uses it. | D-4, NFR-1, NFR-5 | SRE |
| OQ-11 | Are there internal or first-party clients that must never be throttled, and are they distinguishable from public traffic? If they share the public key space, the exemption list (FR-6) is the mechanism; if not, they may need a separate ingress. | FR-6 | API team |

---

## 10. Out of scope

The following are explicitly **not** part of this task. Each is listed with the reason, so that
excluding it is a decision rather than an omission.

- **Billing, metering, and overage charging.** The limiter counts requests, but revenue-grade
  metering has different accuracy and durability requirements than an approximate,
  TTL-expiring, fail-open control. Separate work.
- **Per-user, per-endpoint, or per-tenant sub-quotas.** Only per-key (or per-account, pending OQ-4)
  limits are in scope. Finer granularity is a later increment.
- **Priority classes and fair-share scheduling.** Rejected requests are rejected, not queued or
  reordered. No admitted request is preferred over another.
- **Request queueing or deferred execution.** The API stays synchronous; there is no "accepted, will
  run later" path.
- **WAF-class abuse detection**: distributed abuse across many keys, credential stuffing, bot
  detection, IP reputation. The anonymous-traffic limit (FR-2) is a crude backstop, not a security
  control.
- **Automatic key suspension or revocation.** Sustained abuse raises an alert (FR-32) for a human to
  act on. Automated revocation of a paying customer's credential is not a decision to hand to a
  heuristic.
- **Bandwidth, payload-size, and response-size limits.** Only request rate and concurrency are
  bounded here.
- **Connection-pool resizing, query optimisation, autoscaling, and read-replica routing.** These
  raise capacity; this task bounds consumption. They are complementary and tracked separately.
- **Rate limiting of internal service-to-service traffic** that does not transit the public edge.
- **A self-service customer portal for viewing quota usage.** FR-33 provides an internal operator
  view only; a customer-facing view is separate work.
- **Retrofitting the retry contract into third-party client libraries** the team does not own. Only
  the official SDKs are in scope (FR-28).