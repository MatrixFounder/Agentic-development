# TASK-101 — Per-key rate limiting for the public HTTP API

| Field | Value |
| :--- | :--- |
| Status | Draft |
| Date | 2026-08-05 |
| Owner | API platform owner |
| Reviewers | SRE on-call owner, API documentation owner, platform database owner |
| Requirement strength | MUST, MUST NOT, SHOULD (RFC 2119) |
| Risk severity vocabulary | SEV-1, SEV-2, SEV-3 (defined in §4) |

---

## 1. Problem

- The public HTTP API admits every authenticated request without a rate check.
- The authentication layer resolves an API key to a key id on each request.
- A small number of key ids produce most requests. OQ-1 quantifies the share.
- Per-key request rate varies sharply inside one minute. OQ-1 measures the variation.
- On two occasions one key id held enough concurrent requests to consume every database connection.
- During those two occasions requests carrying other key ids returned errors.
- No control bounds per-key request rate or per-key concurrency today.
- No published document tells a client what to do after a rejection.

**Why.** Connection pool capacity is shared across all key ids, and nothing divides it.

**Why.** Without a published retry rule, a rejected client either stops or retries immediately.

---

## 2. Goals

**G-1.** Bound per-key rate and concurrency so that one key cannot exhaust the connection pool.

**G-2.** Publish a retry contract so that a throttled client recovers without operator contact.

**G-3.** Admit short bursts from a shared allowance so that compliant clients keep current behaviour.

---

## 3. Scope

**In scope.**

- per-key steady rate and per-key burst capacity
- a shared burst pool with a per-key draw cap
- a per-key concurrency cap
- the 429 response contract, including `Retry-After` and rate-limit fields
- limiter state shared by all API instances
- quota configuration that applies without a redeploy
- limiter metrics and throttling logs
- the published client retry contract
- a report-only rollout phase

**Out of scope.**

- API-key issuance and rotation — identity service
- per-endpoint request weighting — deferred, D-10
- paid quota tiers and billing — commerce, OQ-4
- L3/L4 volumetric filtering — edge provider
- retry logic inside published client SDKs — SDK maintainers
- database connection pool sizing — platform database owner
- rate limiting of internal service-to-service traffic — deferred
- rate limiting of requests that fail authentication — deferred, OQ-7
- bot detection and WAF rules — security owner

---

## 4. Definitions

- **API key** is the credential that the authentication layer resolves to a key id.
- **Key id** is the stable identifier that names one client for quota purposes.
- **Token bucket** is a counter that refills at a fixed rate and stops at a fixed capacity.
- **Key bucket** is a token bucket owned by exactly one key id.
- **Shared burst pool** is a token bucket that every key id may draw from.
- **Steady rate `d`** is the refill rate of a key bucket, in requests per second.
- **Burst capacity `b`** is the maximum token count of a key bucket.
- **Concurrency cap `c_instance`** is the maximum count of simultaneously executing requests for one key id on one API instance.
- **Concurrency slot** is the reservation that one executing request holds against `c_instance`.
- **Throttled request** is a request that the limiter rejects with status 429.
- **Report-only mode** is a limiter mode that records every decision and rejects nothing.
- **Exempt key** is a key id whose decisions are recorded and whose requests are never rejected.
- **SEV-1** is a severity value for a failure visible to all clients.
- **SEV-2** is a severity value for a failure visible to one client or one instance.
- **SEV-3** is a severity value for a failure visible only in internal telemetry.

---

## 5. Requirements

### 5.1 Identification and counting

- **R-1** — The limiter MUST select the bucket by key id.
- **R-2** — The limiter MUST NOT select the bucket by client IP address.
  Violation shows: two key ids behind one NAT address share a single counter.
- **R-3** — The limiter MUST run after authentication and MUST receive a resolved key id.
- **R-4** — Each key id MUST have a steady rate `d`, a burst capacity `b` and a cap `c_instance`.
- **R-5** — A key id with no configured quota row MUST use the default quota of §8.

### 5.2 Enforcement

- **R-6** — The limiter MUST admit a request when the key bucket holds at least one token.
- **R-7** — The limiter MUST decrement the key bucket by one token on admission.
- **R-8** — The limiter MUST draw one token from the shared burst pool when the key bucket is empty.
- **R-9** — One key id MUST NOT draw more than `p` percent of shared pool capacity per minute.
  Violation shows: key A drains the pool and key B is rejected while under its own quota.
- **R-10** — The limiter MUST reject the request with status 429 when both buckets are empty.
- **R-11** — The limiter MUST NOT open a database connection for a rejected request.
  Violation shows: the acquired-connection counter increases on a 429 response.
- **R-12** — The limiter MUST NOT decrement any bucket for a rejected request (D-11).
- **R-13** — The limiter MUST reject with 429 when the key's active slot count equals `c_instance`.
- **R-14** — The limiter MUST release a concurrency slot when the response completes.
- **R-15** — The limiter MUST release a concurrency slot when the handler raises an error.
- **R-16** — A concurrency slot MUST expire after `t_slot` seconds (§8).

  **Why.** A client that drops the connection leaves a slot held until an expiry runs.

### 5.3 Response contract

- **R-17** — A 429 response MUST carry `Retry-After` with a delay in whole seconds (RFC 9110 §10.2.3).
- **R-18** — `Retry-After` MUST equal the seconds until the key bucket holds one token, rounded up.
- **R-19** — A rejection caused by R-13 MUST carry `Retry-After: 1`.
- **R-20** — Every response MUST carry rate-limit fields in the syntax selected by OQ-11.
- **R-21** — The report-only phase MUST emit `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`.
- **R-22** — A 429 response body MUST use media type `application/problem+json` (RFC 9457).
- **R-23** — The problem body MUST carry `type`, `title`, `status` and `retryAfterSeconds`.
- **R-24** — A response MUST NOT expose the quota state of another key id.
  Violation shows: a shared-pool field value changes for key B when only key A sends traffic.

### 5.4 State, latency and availability

- **R-25** — Limiter state MUST be shared by every API instance.
- **R-26** — The token read, refill and decrement MUST execute as one atomic operation.

  **Why.** Two instances reading one bucket concurrently would each observe the same token.

- **R-27** — The limiter MUST add at most 5 ms to request latency at p99 (§8).
- **R-28** — The limiter MUST fall back to a per-instance limiter when the shared store is unreachable (D-5).
- **R-29** — The fallback limiter MUST keep enforcing `c_instance` for each key id.
- **R-30** — A shared-store error MUST NOT propagate to the client as a 5xx response.

### 5.5 Observability

- **R-31** — The limiter MUST emit one metric sample per decision, labelled `admitted` or `throttled`.
- **R-32** — The limiter MUST log a throttling event with key id, bucket name and remaining tokens.
- **R-33** — Logs MUST NOT contain the API key secret.
  Violation shows: a search for a known test secret returns a matching log line.
- **R-34** — The limiter MUST expose the count of key ids that reached `c_instance` per minute.

### 5.6 Configuration and rollout

- **R-35** — A quota change MUST take effect within 60 seconds without a redeploy.
- **R-36** — The limiter MUST support report-only mode per environment.
- **R-37** — An operator MUST be able to mark a key id as exempt.
- **R-38** — An exempt key id MUST still be counted, logged and reported.

### 5.7 Documentation

- **R-39** — The public documentation MUST state the default `d`, `b` and `c_instance`.
- **R-40** — The public documentation MUST state the 429 body shape and every rate-limit field.
- **R-41** — The public documentation MUST require exponential backoff with jitter after a 429.
- **R-42** — The public documentation MUST state that a client must not retry before `Retry-After` elapses.
- **R-43** — The public documentation MUST state that a throttled request never reached the handler.

  **Why.** R-11 keeps the handler unreached, so a retry repeats no side effect.

---

## 6. Use cases

### UC-1 — A client stays under its quota

1. The client sends requests at a rate below `d`. Postcondition: the key bucket stays above zero.
2. The limiter admits each request. Postcondition: no 429 response is produced.
3. The response carries the remaining token count. Postcondition: the client can read its headroom.

### UC-2 — A client sends a burst inside its capacity

1. The client sends `b` requests within one second. Postcondition: the key bucket reaches zero.
2. The limiter admits all `b` requests. Postcondition: no shared pool token is drawn.
3. The client pauses for `b / d` seconds. Postcondition: the key bucket returns to `b`.

### UC-3 — A client exceeds its quota and retries

1. The client empties its key bucket. Postcondition: the next request draws from the shared pool.
2. The client empties its share of the shared pool. Postcondition: the draw cap `p` is reached.
3. The limiter returns 429 with `Retry-After`. Postcondition: no database connection was opened.
4. The client waits `Retry-After` plus jitter (§9). Postcondition: no request arrives before the delay.
5. The client repeats the request. Postcondition: the request is admitted.

### UC-4 — One key id saturates the shared pool

1. Key A sends requests far above its steady rate. Postcondition: key A reaches the draw cap `p`.
2. The limiter rejects further key A requests. Postcondition: shared pool tokens remain for other keys.
3. Key B sends one request under its own quota. Postcondition: key B is admitted.

### UC-5 — One key id reaches the concurrency cap

1. Key A opens `c_instance` slow requests on one instance. Postcondition: all slots for key A are held.
2. Key A sends one further request. Postcondition: the limiter returns 429 with `Retry-After: 1`.
3. One earlier response completes. Postcondition: one slot is released and the next request is admitted.

### UC-6 — An operator raises a quota

1. The operator updates the quota row for key A. Postcondition: the stored `d` and `b` change.
2. The limiter reloads quota configuration. Postcondition: the change is applied within 60 seconds.
3. Key A sends traffic at the new rate. Postcondition: the requests are admitted.

### UC-7 — The shared store becomes unreachable

1. The store stops answering. Postcondition: the limiter records a store-error metric sample.
2. The limiter switches to the per-instance limiter. Postcondition: requests receive no 5xx from the limiter.
3. Each instance enforces `c_instance` locally. Postcondition: one key holds at most `c_instance` slots per instance.
4. The store answers again. Postcondition: the limiter resumes shared decisions.

### UC-8 — Report-only rollout

1. The limiter runs with rejection disabled. Postcondition: every decision is recorded and no request is rejected.
2. The owner reads the recorded decisions after 14 days. Postcondition: the default quota values are chosen (OQ-1).
3. The owner enables rejection. Postcondition: R-10 and R-13 take effect.

---

## 7. Admission algorithm

1. Read the key id from the authentication result. Postcondition: the key id is bound.
2. Read the quota row for the key id, or the default row. Postcondition: `d`, `b`, `c_instance` are bound.
3. Read the active slot count for the key id on this instance. Postcondition: `n_active` is bound.
4. Reject with 429 and `Retry-After: 1` when `n_active` equals `c_instance`. Postcondition: no connection is acquired.
5. Reserve one concurrency slot with expiry `t_slot`. Postcondition: `n_active` increases by one.
6. Refill the key bucket by `d × elapsed`, capped at `b`. Postcondition: the key bucket is current.
7. Admit and decrement one token when the key bucket holds at least one. Postcondition: step 11 runs next.
8. Refill the shared burst pool, capped at `P`. Postcondition: the shared pool is current.
9. Admit and decrement one shared token when the key's minute draw is below `p`. Postcondition: step 11 runs next.
10. Release the slot and reject with 429 and a computed `Retry-After`. Postcondition: no bucket was decremented (R-12).
11. Attach the rate-limit fields to the response. Postcondition: the client can read its remaining allowance.
12. Release the concurrency slot when the response completes or the handler errors. Postcondition: `n_active` decreases by one.

Steps 6 to 9 execute as one atomic operation in the shared store (R-26).

---

## 8. Derived numbers

**`c_instance` — per-key concurrency cap on one instance.**
`c_instance = floor(0.25 × pool_instance)`; measured `pool_instance` is unconfirmed (OQ-3); applied `c_instance = 5` during report-only.
`pool_instance` is the ceiling: one key id must not hold more than a quarter of it.

**`d` — default steady rate.**
`d = 10 requests per second`; measured p99 of legitimate keys is not yet computed (OQ-1); applied 10 during report-only.
The applied value is the ceiling for a client; the measured p99 is its floor.

**`b` — default burst capacity.**
`b = 100 tokens = 10 × d`; measured burst length is not yet computed (OQ-1); applied 100.
The applied value is the ceiling.

**`P` — shared burst pool capacity.**
`P = 3000 tokens = 50 tokens per second × 60 seconds`; measured spare API capacity is unconfirmed (OQ-3); applied 3000.
The measured spare capacity is the ceiling.

**`p` — per-key draw cap on the shared pool.**
`p = 25 percent of P per minute = 750 tokens`; measured concurrent burst-key count is unconfirmed (OQ-1); applied 750.
The applied value is the ceiling.

**`t_slot` — concurrency slot expiry.**
`t_slot = 35 s = request timeout 30 s + 5 s margin`; measured timeout is 30 s in the current gateway configuration; applied 35.
The measured timeout is the floor; the applied value must stay above it.

**Limiter latency budget.**
`5 ms = 2 × 2 ms store round trip + 1 ms script time`; measured store p99 round trip is unconfirmed (OQ-2); applied 5 ms as the gate in AC-9.
The applied value is the ceiling.

**Quota propagation delay.**
`60 s = configuration cache TTL`; measured reload cost is below 10 ms; applied 60 s in R-35.
The applied value is the ceiling.

---

## 9. Published retry contract

The client rules below are the text that R-41 to R-43 require in the public documentation.

1. Read `Retry-After` from the 429 response. Postcondition: the client holds a delay in seconds.
2. Set `attempt` to the count of consecutive 429 responses for this key. Postcondition: `attempt` is at least 1.
3. Compute `backoff = min(60, 2 ^ attempt)` seconds. Postcondition: the backoff is bounded at 60 s.
4. Draw `jitter` uniformly from the interval `[0, backoff]`. Postcondition: two clients rarely wait the same time.
5. Send the next request after `Retry-After + jitter` seconds. Postcondition: no request arrives before `Retry-After`.
6. Stop after 5 consecutive 429 responses and surface the error. Postcondition: the retry loop terminates.
7. Read the remaining allowance from the rate-limit fields on every response. Postcondition: the client can slow down before a rejection.

**Prohibition.** A client MUST NOT send the next request before `Retry-After` elapses.
Violation shows: the server records a request from the key id inside its advertised delay window.

**Retry safety.** A throttled request may be retried with any HTTP method.

**Why.** R-11 keeps a rejected request out of the handler, so no side effect was applied.

---

## 10. Acceptance criteria

- **AC-1** — 100 requests at 5 req/s with `d = 10` → every request is admitted.
  Fails when the bucket refill step is removed.
- **AC-2** — `b + 1` requests within 100 ms with an empty shared pool → the last request returns 429.
  Fails when the burst capacity check is removed.
- **AC-3** — any 429 response → `Retry-After` is present and is an integer of at least 1.
  Fails when the header is dropped from the rejection path.
- **AC-4** — a client that waits `Retry-After` and repeats → the repeated request is admitted.
  Fails when the refill timestamp is not persisted.
- **AC-5** — a 429 response → the acquired-connection counter is unchanged.
  Fails when the limiter is invoked after the handler acquires a connection.
- **AC-6** — key A drains the shared pool, key B sends one request under quota → key B is admitted.
  Fails when the per-key draw cap `p` is removed.
- **AC-7** — key A holds `c_instance` slow requests and sends one more → the last returns 429 with `Retry-After: 1`.
  Fails when the slot reservation is skipped.
- **AC-8** — key A disconnects while holding every slot → slots are free after `t_slot` seconds.
  Fails when the slot expiry is removed.
- **AC-9** — one key id sends 200 requests across 4 instances → admitted requests per second stay at or below `d`, after the initial burst `b`.
  Fails when the shared store is replaced by in-process counters.
- **AC-10** — 10 minutes of load with the limiter enabled → added p99 latency is at or below 5 ms.
  Fails when the limiter performs more than one store round trip per decision.
- **AC-11** — the shared store is unreachable → requests are admitted and `c_instance` still holds per instance.
  Fails when the store client error propagates to the caller.
- **AC-12** — a quota row is changed → the new limit is observed within 60 seconds.
  Fails when the configuration cache TTL is raised above 60 s.
- **AC-13** — report-only mode with traffic above quota → decisions are recorded and zero 429 responses are returned.
  Fails when the mode flag is not read on the rejection path.
- **AC-14** — 1000 throttled requests → a search of the logs for the test key secret returns zero lines.
  Fails when the log field carries the credential instead of the key id.
- **AC-15** — an exempt key id sends 10 × its quota → zero 429 responses and the throttle metric counts the excess.
  Fails when the exemption check also skips metric emission.
- **AC-16** — a 429 response → the body parses as `application/problem+json` with `retryAfterSeconds` equal to `Retry-After`.
  Fails when the two values are computed independently.
- **AC-17** — replay of the traffic recorded in the two pool-exhaustion incidents → free connections stay above 25 percent. Depends on OQ-9 for the replay input.
- **AC-18** — the public documentation build → the retry page states `Retry-After`, the jitter rule and the no-early-retry rule. Documentation check; no mutation clause applies.

### Traceability

| Requirement | Criterion |
| :--- | :--- |
| R-6, R-7 | AC-1 |
| R-8, R-9 | AC-2, AC-6 |
| R-11 | AC-5 |
| R-13, R-14 | AC-7 |
| R-16 | AC-8 |
| R-17, R-18 | AC-3, AC-4 |
| R-22, R-23 | AC-16 |
| R-25, R-26 | AC-9 |
| R-27 | AC-10 |
| R-28, R-29, R-30 | AC-11 |
| R-33 | AC-14 |
| R-35 | AC-12 |
| R-36 | AC-13 |
| R-37, R-38 | AC-15 |
| R-39 to R-43 | AC-18 |

---

## 11. Risks

- **RSK-1** — SEV-2 — The shared store fails → every instance falls back and total concurrency reaches `n × c_instance` (detected by AC-11 and the free-connections alert).
- **RSK-2** — SEV-2 — The default `d` sits below a legitimate key's p99 rate → a paying client receives 429 (detected by the report-only report in UC-8).
- **RSK-3** — SEV-1 — The limiter runs after connection acquisition → a 429 still consumes a connection (detected by AC-5).
- **RSK-4** — SEV-2 — Clients retry without jitter → retries align at the delay expiry and produce a second peak (detected by AC-4 repeated with 1000 clients).
- **RSK-5** — SEV-3 — All traffic for one key id maps to one store shard → that shard saturates (detected by the shard CPU metric during AC-9).
- **RSK-6** — SEV-2 — A concurrency slot leaks on a dropped connection → the key id is rejected until expiry (detected by AC-8).
- **RSK-7** — SEV-3 — Instance clocks disagree → `Retry-After` values differ across instances (detected by a clock-offset alert on the API fleet).
- **RSK-8** — SEV-2 — A long-running endpoint exceeds `t_slot` → its slot is released while the request runs (detected by AC-8 extended with a 60 s handler; blocked on OQ-6).

---

## 12. Decisions

- **D-1**, 2026-08-05, API platform owner: buckets are keyed by key id. Rejected: client IP address — one NAT address groups unrelated clients into one counter.
- **D-2**, 2026-08-05, API platform owner: each key id gets a token bucket. Rejected: fixed window counter — a window boundary admits `2 × d` inside one second.
- **D-3**, 2026-08-05, API platform owner: a shared burst pool serves overflow. Rejected: per-key burst only — a compliant client's burst would be rejected while the fleet is idle.
- **D-4**, 2026-08-05, API platform owner: the shared pool has a per-key draw cap `p = 25%`. Rejected: an uncapped shared pool — one key id can take 100 percent of it.
- **D-5**, 2026-08-05, SRE on-call owner: the limiter fails open to a per-instance limiter. Rejected: fail closed — a store outage would return 429 for 100 percent of requests.
- **D-6**, 2026-08-05, API platform owner: a per-key concurrency cap ships alongside the rate cap. Rejected: rate cap only — the two recorded exhaustions used concurrent slow requests, which a rate cap does not bound.
- **D-7**, 2026-08-05, API documentation owner: rejection uses status 429 (RFC 6585 §4). Rejected: 503 — 503 marks a server fault and triggers client-side failover.
- **D-8**, 2026-08-05, API documentation owner: field names follow `draft-ietf-httpapi-ratelimit-headers`. Rejected: `X-RateLimit-*` — RFC 6648 deprecates the `X-` prefix.
- **D-9**, 2026-08-05, SRE on-call owner: state lives in one shared store, evaluated by one atomic script. Rejected: in-process counters — `n` instances multiply the effective limit by `n`.
- **D-10**, 2026-08-05, API platform owner: per-endpoint weights are deferred to a later task. Rejected: weights in this task — per-endpoint cost data is not collected.
- **D-11**, 2026-08-05, API platform owner: a rejected request decrements no bucket. Rejected: decrement on rejection — a client in a retry loop would hold its bucket at zero indefinitely.
- **D-12**, 2026-08-05, API platform owner: enforcement follows a 14-day report-only phase. Rejected: immediate enforcement — the default quota inputs are unmeasured (OQ-1).

---

## 13. Open questions

- **OQ-1** — What is the p99 per-key request rate and burst length over the last 30 days? Blocks: the applied values of `d`, `b` and `p` in §8. Owner: API platform owner.
- **OQ-2** — Which store holds limiter state: the existing cache cluster or a new instance? Blocks: R-25, the latency budget in §8. Owner: SRE on-call owner.
- **OQ-3** — How many database connections does one API instance hold, and how many instances run? Blocks: the `c_instance` and `P` derivations in §8. Owner: platform database owner.
- **OQ-4** — Do quota defaults differ by client tier? Blocks: R-5, the quota configuration schema. Owner: commerce owner.
- **OQ-5** — Is a quota scoped to a key id overall, or to a key id and endpoint pair? Blocks: R-4, D-10. Owner: API platform owner.
- **OQ-6** — Which endpoints stream or run longer than `t_slot`? Blocks: R-16, RSK-8. Owner: API platform owner.
- **OQ-7** — Do requests that fail authentication receive a limit in this task? Blocks: the scope exclusion, R-3. Owner: security owner.
- **OQ-8** — Which key ids receive advance notice before enforcement starts? Blocks: the D-12 rollout plan. Owner: support owner.
- **OQ-9** — Which incident records document the two pool-exhaustion events? Blocks: AC-17 replay input. Owner: SRE on-call owner.
- **OQ-10** — What 429 rate for a compliant key id triggers an alert? Blocks: the alert threshold on the R-31 metric. Owner: SRE on-call owner.
- **OQ-11** — Which syntax do the rate-limit fields use: separate `RateLimit-*` fields, or the combined `RateLimit` structured field with `RateLimit-Policy`? Blocks: R-20, R-40. Owner: API documentation owner.