# TASK-101 — Per-key rate limiting for the public HTTP API

| Field | Value |
| :--- | :--- |
| Status | Draft |
| Date | 2026-08-05 |
| Owner | API Platform lead |
| Reviewers | SRE on-call lead, Developer Relations lead |
| Modal verbs | `MUST`, `MUST NOT`, `SHOULD` per RFC 2119 |
| Severity values | `Critical`, `Major`, `Minor` |

---

## 1. Problem

Observable facts about the current system.

- **P-1** — The public HTTP API applies no request-rate limit. Evidence: the gateway configuration holds no limiter rule.
- **P-2** — The gateway authenticates each request by API key. Evidence: the gateway returns 401 without a key.
- **P-3** — A small subset of keys produces most requests. Evidence: access-log aggregation; the share is unmeasured (OQ-3).
- **P-4** — The database connection pool reached exhaustion twice under load from one key. Evidence: two incident records (OQ-1).
- **P-5** — Pool exhaustion blocks requests from every key, not only the key that caused it. Evidence: every request path acquires from the same pool.
- **P-6** — No response carries the client's remaining quota. Follows from P-1.
- **P-7** — The public API documentation states no client behaviour for a throttled response. Evidence: the errors page.

**Why.** No component bounds one key's resource consumption ⇒ one key's request pattern sets availability for all keys.

---

## 2. Goals

- **G-1** — Limit each key's request rate and concurrency so that no key exhausts the connection pool.
- **G-2** — Publish a retry contract so that a throttled client resumes without operator contact.

---

## 3. Scope

**In scope:** rate limiting at the API gateway, a per-key concurrency limit in the API service, the shared burst pool, the throttled response format, the published client retry contract, limiter metrics and alerts, the observe-then-enforce rollout.

**Out of scope:**

- Billing or paid quota tiers — carried by the Product owner as a separate task.
- Per-endpoint authorization scopes — carried by the Security lead.
- API key issuance, rotation, and revocation — carried by the Identity team, unchanged by this task.
- Connection pool resizing and query optimisation — carried by the Platform DBA.
- Denial-of-service filtering at the network edge — carried by the SRE team on the CDN layer.
- Client SDK changes that implement the retry contract — carried by Developer Relations after R-21 lands.

---

## 4. Definitions

- **API key** is a bearer credential that identifies one client of the public API.
- **Counter key** is the identifier under which the limiter stores one client's token state.
- **Tier** is a named set of limiter parameters assigned to a counter key.
- **Sustained rate** is the token count a counter key receives per second.
- **Bucket capacity** is the maximum token count a counter key holds.
- **Shared burst pool** is a token bucket that any counter key draws from after its own bucket empties.
- **Draw cap** is the maximum token count one counter key takes from the shared burst pool per 60 seconds.
- **Endpoint class** is a group of routes that share one token cost.
- **Throttled response** is an HTTP response with status 429 produced by the limiter.
- **Concurrency cap** is the maximum count of one counter key's requests executing simultaneously in one service instance.
- **Limiter store** is the external key-value store holding token state across gateway instances.
- **Observe mode** is a configuration in which the limiter computes decisions and rejects nothing.

---

## 5. Requirements

### 5.1 Enforcement

- **R-1** — The gateway MUST evaluate the limiter decision before routing the request upstream.
- **R-2** — The limiter MUST use the SHA-256 digest of the API key as the counter key.
  **Why.** The digest keeps the credential out of the store, the logs, and the metrics.
- **R-3** — Requests carrying no valid API key MUST count against a counter key derived from the source IP address.
  **Why.** A 401 response consumes gateway capacity ⇒ an unauthenticated flood stays unbounded without R-3.
- **R-4** — The gateway MUST read each counter key's tier from configuration, not from the request.

### 5.2 Quota algorithm

- **R-5** — The limiter MUST hold one token bucket per counter key.
- **R-6** — Each bucket MUST refill at its tier's sustained rate.
- **R-7** — A bucket MUST NOT hold more tokens than its tier's capacity.
- **R-8** — A request MUST consume the token count assigned to its endpoint class, defaulting to 1.
- **R-9** — The limiter MUST draw from the shared burst pool only after the counter key's own bucket empties.
- **R-10** — A counter key MUST NOT exceed its tier's draw cap within any 60-second period.
  **Why.** An uncapped draw lets one key consume the whole shared pool, which reproduces P-4.
- **R-11** — The limiter MUST perform read, deduct, and write as one atomic operation per counter key.
  **Why.** Read-then-write across N gateway instances overshoots the quota by up to N requests.
- **R-12** — The limiter MUST compute refill from the limiter store's clock, not from the gateway instance clock.
  **Why.** Instance clock skew changes the refill amount for the same elapsed time.

Provisional tier values.

| Tier | Sustained req/s | Capacity | Draw cap / 60 s | Status |
| :--- | :--- | :--- | :--- | :--- |
| `anon` | 1 | 5 | 0 | provisional (OQ-8) |
| `standard` | 10 | 50 | 100 | provisional (OQ-3) |
| `partner` | 50 | 250 | 300 | provisional (OQ-3) |
| `internal` | unlimited | n/a | n/a | provisional (OQ-6) |

Shared burst pool: capacity 500 tokens, refill 250 tokens/s, both provisional under OQ-3.

### 5.3 Connection-pool protection

- **R-13** — Each API service instance MUST limit one counter key's simultaneously executing requests to C.
- **R-14** — `C = floor(P × 0.25); P measured per service instance (OQ-2); applied per instance and counter key.` C is a ceiling, not a target.
- **R-15** — A tier exempt from R-5 through R-10 MUST still obey R-13.
  **Why.** P-4 came from concurrent connection holding ⇒ a rate exemption that also exempts R-13 restores the incident condition.
- **R-16** — The service MUST hold the R-13 counter in process memory, not in the limiter store.
  **Why.** A limiter store outage would otherwise remove the protection that P-4 requires.

### 5.4 Throttled response

- **R-17** — The gateway MUST return status 429 for a rate rejection and for a concurrency rejection (RFC 6585).
- **R-18** — A throttled response MUST carry `Retry-After` as delta-seconds with an integer value of 1 or greater (RFC 9110 §10.2.3).
- **R-19** — A throttled response MUST carry the counter key's limit, remaining tokens, and reset instant. Field syntax follows OQ-4.
- **R-20** — Every response to a limited route SHOULD carry the fields named in R-19.
  **Why.** A client that reads remaining tokens paces itself before reaching zero.
- **R-21** — A throttled response body MUST be JSON carrying `error.code`, `error.message`, `error.retry_after_seconds`, and `error.request_id`.
- **R-22** — `error.code` MUST take one of `rate_limit_exceeded`, `concurrency_limit_exceeded`, or `quota_unavailable`.
- **R-23** — A throttled request MUST NOT reach the upstream service.
  **Why.** No side effect occurs ⇒ a client may retry a non-idempotent method safely.

### 5.5 Client retry contract

The published contract states the following obligations for a client.

- **R-24** — The API documentation MUST publish this contract at least 14 days before enforcement starts.
- **R-25** — A client MUST wait at least the `Retry-After` value before repeating the request.
- **R-26** — A client MUST add random jitter between 0 and 1000 milliseconds to that wait.
  **Why.** Synchronised retries from many clients arrive as one burst at reset.
- **R-27** — A client SHOULD stop after 4 total attempts and surface the error.
- **R-28** — A client MAY repeat a non-idempotent request after 429, under the guarantee in R-23.
- **R-29** — The gateway MUST NOT extend a counter key's wait when the client retries early.
  **Why.** An escalating penalty turns a client-side defect into an outage longer than the quota window.

### 5.6 Degradation

- **R-30** — The gateway MUST bound each limiter store call to 5 milliseconds.
- **R-31** — The gateway MUST NOT repeat a limiter store call within one request.
- **R-32** — The gateway MUST allow the request when the limiter store returns no answer within R-30.
  **Why.** Rejecting on store failure returns 429 for 100% of traffic; R-13 still bounds pool usage.
- **R-33** — The gateway MUST apply a changed tier value within 60 seconds without a redeploy.

### 5.7 Observability

- **R-34** — The gateway MUST emit a decision counter labelled by tier and by outcome.
- **R-35** — Outcome values MUST be `allow`, `throttle`, `would_throttle`, and `fallback_allow`.
- **R-36** — Metric labels MUST NOT carry the counter key.
  **Why.** Key-valued labels grow the time-series count with the client count.
- **R-37** — A throttle log line MUST carry the first 8 characters of the counter key digest.
- **R-38** — A log line MUST NOT carry the API key.
- **R-39** — The alert rule MUST page when `fallback_allow` exceeds 1% of decisions over 5 minutes.
- **R-40** — The alert rule MUST warn when one counter key's throttle share exceeds 50% over 10 minutes.

### 5.8 Rollout control

- **R-41** — The limiter MUST support observe mode per tier.
- **R-42** — Observe mode MUST emit the R-19 fields and the R-35 outcome `would_throttle`.
- **R-43** — Observe mode MUST NOT return status 429.
- **R-44** — Enforcement MUST be switchable per tier, independently of other tiers.

---

## 6. Use cases

### UC-1 — A key stays under its sustained rate

Actor: a `standard` client. Trigger: 8 requests per second for one minute.

1. The gateway deducts 1 token per request. Postcondition: the bucket holds tokens above zero.
2. The gateway routes each request upstream. Postcondition: no 429 is emitted.
3. The gateway attaches the R-19 fields. Postcondition: the client reads its remaining tokens.

Postcondition: every response carries status 200.

### UC-2 — A burst fits inside the key's own bucket

Actor: a `standard` client with a full bucket. Trigger: 40 requests within one second.

1. The gateway deducts 40 tokens. Postcondition: the bucket holds 10 tokens.
2. The gateway routes all 40 requests. Postcondition: the shared pool is untouched.

Postcondition: the bucket refills to capacity within 4 seconds.

### UC-3 — A burst draws from the shared pool

Actor: a `standard` client with an empty bucket. Trigger: 60 further requests within one second.

1. The gateway finds zero tokens in the key's bucket. Postcondition: R-9 permits a shared-pool draw.
2. The gateway draws 60 tokens from the shared pool. Postcondition: the key's 60-second draw total reaches 60.
3. The gateway routes all 60 requests. Postcondition: no 429 is emitted.

Postcondition: the key may draw 40 further tokens within the same 60 seconds.

### UC-4 — Both sources are exhausted

Actor: a `standard` client at its draw cap. Trigger: one further request.

1. The gateway finds zero tokens in the bucket. Postcondition: R-9 applies.
2. The gateway finds the draw cap consumed. Postcondition: R-10 blocks the draw.
3. The gateway returns 429 with `error.code = rate_limit_exceeded`. Postcondition: the request never reaches upstream.
4. The client waits `Retry-After` plus jitter and repeats. Postcondition: the repeated request receives 200.

Postcondition: no other counter key observes a changed decision.

### UC-5 — A client retries before the stated instant

Actor: a throttled client that ignores `Retry-After`. Trigger: an immediate repeat.

1. The gateway deducts nothing and returns 429. Postcondition: the counter key's state is unchanged.
2. The gateway leaves the wait value unchanged. Postcondition: R-29 holds.
3. The alert rule counts the throttle share. Postcondition: R-40 warns after 10 minutes.

Postcondition: Developer Relations contacts the key owner.

### UC-6 — One key holds long-running queries

Actor: a client under its rate quota whose queries run for 20 seconds. Trigger: C+1 simultaneous requests to one instance.

1. The service admits C requests to the semaphore. Postcondition: at most C pool connections carry this key.
2. The service rejects request C+1 with 429 and `error.code = concurrency_limit_exceeded`. Postcondition: the pool retains free connections.

Postcondition: requests from other counter keys acquire pool connections.

### UC-7 — The limiter store stops answering

Actor: the gateway. Trigger: limiter store latency above 5 milliseconds.

1. The gateway abandons the store call at 5 milliseconds. Postcondition: R-30 holds.
2. The gateway allows the request and increments `fallback_allow`. Postcondition: R-32 holds.
3. R-13 continues to bound simultaneous requests. Postcondition: the pool stays protected.
4. The alert rule pages after 5 minutes above 1%. Postcondition: on-call receives the page.

Postcondition: the API serves traffic while the store is unavailable.

### UC-8 — An operator raises a key's tier

Actor: the API Platform lead. Trigger: an approved quota increase.

1. The operator changes the key's tier in configuration. Postcondition: the change is recorded in version control.
2. The gateway reloads the value within 60 seconds. Postcondition: R-33 holds.
3. The next request from that key uses the new tier. Postcondition: no gateway restart occurred.

Postcondition: other counter keys keep their previous tiers.

---

## 7. Acceptance criteria

- **AC-1** — 8 requests/second for 60 seconds on a `standard` key → every response returns 200; fails when the refill rate constant is halved. Covers R-5, R-6.
- **AC-2** — shared pool drained, 60 requests in one second on a full `standard` bucket → 50 responses 200 and 10 responses 429; fails when the capacity ceiling is removed. Covers R-7, R-9.
- **AC-3** — empty bucket, shared pool at 500 tokens, draw cap already consumed → the next request returns 429; fails when the draw cap check is skipped. Covers R-10.
- **AC-4** — two gateway instances issuing 100 simultaneous requests on one counter key → allowed count equals capacity plus accrued tokens; fails when the atomic script is replaced by read-then-write. Covers R-11.
- **AC-5** — one instance clock advanced by 30 seconds → refill matches the store clock elapsed time; fails when the script reads the instance clock. Covers R-12.
- **AC-6** — C+1 simultaneous requests on one counter key against one instance → one response returns 429 with `concurrency_limit_exceeded`; fails when the semaphore is sized from the tier rate. Covers R-13, R-14.
- **AC-7** — an `internal` key issuing C+1 simultaneous requests → one response returns 429; fails when the tier exemption also bypasses the semaphore. Covers R-15.
- **AC-8** — any throttled response → `Retry-After` parses as an integer of 1 or greater; fails when the header is emitted as an HTTP-date. Covers R-18.
- **AC-9** — any throttled response → the body contains `error.code` and `error.request_id`; fails when the error body is emitted empty. Covers R-21, R-22.
- **AC-10** — a throttled request against a route with a write side effect → the upstream service records no invocation; fails when the limiter runs after routing. Covers R-1, R-23.
- **AC-11** — limiter store delayed past 5 milliseconds → the response returns 200 and `fallback_allow` increments by 1; fails when the timeout path returns 429. Covers R-30, R-32, R-35.
- **AC-12** — a throttle event → the log line contains the 8-character digest prefix and no API key; fails when the formatter writes the credential. Covers R-37, R-38.
- **AC-13** — observe mode with a counter key over quota → the response returns 200 and `would_throttle` increments; fails when observe mode returns 429. Covers R-41, R-42, R-43.
- **AC-14** — a tier value changed in configuration → the new value applies within 60 seconds without a restart; fails when the value is read once at startup. Covers R-33.
- **AC-15** — a request with no valid API key → the decision counter increments for tier `anon`; fails when unauthenticated requests bypass the limiter. Covers R-3.
- **AC-16** — the public API documentation page states 429 semantics, `Retry-After` handling, jitter, and the attempt cap. Covers R-24 through R-28.
- **AC-17** — the metric registry after 10 000 distinct keys → the decision counter holds one series per tier and outcome pair. Covers R-36.

---

## 8. Risks

- **RISK-1** — Tier values ship from estimates rather than measurement → clients under normal volume receive 429 (detected by observe-mode `would_throttle` counts in step 3 of §10). Severity: `Major`.
- **RISK-2** — The limiter store evicts counter keys under memory pressure → an evicted bucket resets to full capacity (detected by the store's eviction counter). Severity: `Major`.
- **RISK-3** — An `internal` key runs long queries → pool exhaustion recurs (detected by AC-7 and the concurrency rejection counter). Severity: `Critical`.
- **RISK-4** — The limiter store call adds latency to every request → p99 latency exceeds the API service objective (detected by the store latency histogram against the 5-millisecond bound). Severity: `Minor`.
- **RISK-5** — Clients repeat requests without honouring `Retry-After` → gateway CPU stays occupied by rejected traffic (detected by R-40). Severity: `Minor`.
- **RISK-6** — Shared pool tokens are consumed by one tier at reset → other tiers observe an empty pool (detected by the shared pool depth gauge). Severity: `Minor`.

---

## 9. Decisions

- **D-1**, 2026-08-05, API Platform lead: rate enforcement runs at the API gateway before routing. Rejected: per-service middleware — each new service starts without limits until a per-service audit adds them.
- **D-2**, 2026-08-05, API Platform lead: the algorithm is a token bucket per counter key. Rejected: a fixed 60-second window — it admits twice the quota across a window boundary.
- **D-3**, 2026-08-05, API Platform lead: the shared burst pool carries a per-key draw cap. Rejected: an uncapped shared pool — one key consumes the whole pool, which is the P-4 condition.
- **D-4**, 2026-08-05, SRE on-call lead: token state lives in a limiter store, updated by one atomic script. Rejected: per-instance in-memory counters — the effective limit becomes N times the configured limit for N instances.
- **D-5**, 2026-08-05, SRE on-call lead: the gateway allows the request when the limiter store answers late. Rejected: rejecting on store failure — a store outage returns 429 for 100% of requests.
- **D-6**, 2026-08-05, API Platform lead: a per-key concurrency semaphore lives in the service process. Rejected: a shared concurrency counter in the limiter store — a store outage removes the protection that P-4 requires.
- **D-7**, 2026-08-05, API Platform lead: concurrency rejection returns 429, distinguished by `error.code`. Rejected: 503 Service Unavailable — that status counts against the service availability metric.
- **D-8**, 2026-08-05, Developer Relations lead: an early retry incurs no additional wait. Rejected: an exponential lockout — a client defect then extends recovery beyond the quota window.
- **D-9**, 2026-08-05, API Platform lead: observe mode precedes enforcement, with 14 days of client notice. Rejected: immediate enforcement — tier values have no measurement yet (OQ-3).
- **D-10**, 2026-08-05, Security lead: the counter key is the SHA-256 digest of the API key. Rejected: the raw key — it would appear in store keys and in operator dashboards.

---

## 10. Rollout

1. Deploy the limiter with every tier in observe mode. Postcondition: the decision counter reports `would_throttle` and no 429 is emitted.
2. Deploy the R-13 semaphore with C from OQ-2. Postcondition: AC-6 passes in production.
3. Collect 7 days of `would_throttle` counts per tier. Postcondition: OQ-3 closes with measured values.
4. Publish the retry contract and the tier table. Postcondition: AC-16 passes; the 14-day notice under R-24 starts.
5. Enable enforcement for tier `anon`. Postcondition: the `anon` throttle share is visible in metrics.
6. Enable enforcement for `standard`, then `partner`, one week apart. Postcondition: R-40 reports no key above 50% for 10 minutes.
7. Review the shared pool depth gauge after 14 days. Postcondition: the pool values are confirmed or amended under OQ-3.

---

## 11. Open questions

- **OQ-1** — Which incident records document the two connection-pool exhaustions? Blocks: the evidence link on P-4. Owner: SRE on-call lead.
- **OQ-2** — What is the connection pool size P per service instance, and does the 0.25 fraction in R-14 hold? Blocks: C in R-13. Owner: Platform DBA.
- **OQ-3** — Which tier and shared-pool values follow from the measured per-key request rates? Blocks: the §5.2 table status. Owner: API Platform lead.
- **OQ-4** — Which version of `draft-ietf-httpapi-ratelimit-headers` defines the field syntax for R-19? Blocks: R-19 implementation. Owner: API Platform lead.
- **OQ-5** — Which endpoint classes carry a token cost above 1? Blocks: R-8 configuration. Owner: API Platform lead.
- **OQ-6** — Does the `internal` tier stay exempt from R-5 through R-10 after step 6 of §10? Blocks: RISK-3 mitigation. Owner: API Platform lead.
- **OQ-7** — Does a quota apply per API key or per account when one account holds several keys? Blocks: R-2 and R-4. Owner: Product owner.
- **OQ-8** — What sustained rate and capacity apply to tier `anon`? Blocks: R-3. Owner: Security lead.
- **OQ-9** — Does the limiter store run as a dedicated instance or on the existing cache cluster? Blocks: RISK-2 mitigation. Owner: SRE on-call lead.
- **OQ-10** — Which response does a client receive when both R-10 and R-13 reject the same request? Blocks: the `error.code` selection in R-22. Owner: API Platform lead.