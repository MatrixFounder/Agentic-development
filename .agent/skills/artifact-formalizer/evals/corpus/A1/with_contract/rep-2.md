# TASK 041 — Per-key rate limiting for the public HTTP API

| Field | Value |
| :--- | :--- |
| Status | Draft |
| Date | 2026-08-05 |
| Owner | API platform team |
| Severity vocabulary | `Critical`, `Major`, `Minor` |
| Requirement prefix | `R-` |
| Cited standards | RFC 6585 §4, RFC 9110 §10.2.3, `draft-ietf-httpapi-ratelimit-headers` |

---

## 1. Goal

Enforce a per-key request quota so that no single API key drives the database connection pool to zero free connections.

---

## 2. Scope

**In scope:** per-key quota enforcement, a shared burst pool, the `429` response contract, rate-limit response headers, the client retry contract, limiter metrics, per-key quota configuration, shadow-mode rollout.

**Out of scope:** authentication and API-key issuance (owned by the identity service), per-endpoint request weighting (deferred, see D-8), paid quota tiers and billing (owned by commerce), L3/L4 volumetric filtering (owned by the edge provider), retry logic inside published client SDKs (owned by SDK maintainers), rate limiting of internal service-to-service traffic (see OQ-7).

---

## 3. Definitions

- **API key** is the credential presented on each request that the identity service resolves to one client.
- **Quota** is a token-bucket allowance that refills at a fixed rate and holds a fixed capacity.
- **Steady rate** is the token refill rate of one key's bucket, in requests per second.
- **Shared burst pool** is a token bucket that all keys draw from after their own bucket is empty.
- **Throttled request** is a request the limiter rejects with status `429` before the route handler runs.
- **Decision store** is the process that holds bucket state for all API instances.
- **Shadow mode** is a limiter configuration that records a decision and admits the request regardless.

**Why.** `token bucket`, `429` and `Retry-After` resolve against RFC 6585 and RFC 9110, so no local coinage is introduced.

---

## 4. Problem

**P-1** — the API applies no request limit; every authenticated request reaches the connection pool.

**P-2** — a small set of API keys produces most of the request volume. The share per key is not yet measured (OQ-2).

**P-3** — the connection pool reached zero free connections twice. Both events coincided with load from a single API key.

**P-4** — a throttled client has no documented retry behaviour, so client retry timing is unconstrained.

Observed failure mode, stated as a condition:

- One key raises its request rate → pool free connections reach zero → every other key receives errors (detected by the pool-saturation alarm).

---

## 5. Requirements

### 5.1 Enforcement

**R-1** — the limiter must evaluate every request that carries an API key.

**R-2** — the limiter must reject a throttled request before the route handler runs.

**Why.** A rejection that precedes the handler produces no side effect, which makes retry of any HTTP method safe (see R-16).

**R-3** — the limiter must hold one token bucket per API key.

**R-4** — the limiter must charge exactly one token per request in this release.

**R-5** — the limiter must apply the default tier to a key that has no configured tier.

**R-6** — the limiter must not charge a token for a request it rejects.

**R-7** — the limiter must reject a request that presents no API key with status `401`, before quota evaluation.

### 5.2 Quota values

**R-8** — the default steady rate is `50 req/s = 20 pool connections × 0.5 target utilisation ÷ 0.2 s mean hold time`; measured: none of the three inputs is measured (OQ-1); applied: 50 req/s, as a ceiling.

**R-9** — the per-key bucket capacity must equal one second of the steady rate.

**R-10** — an operator must be able to set a steady rate per key.

**R-11** — a quota change must take effect within 60 seconds without a redeploy.

### 5.3 Shared burst pool

**R-12** — a key whose own bucket is empty must draw from the shared burst pool.

**R-13** — one key must not hold more than 25% of the shared burst pool. The violation shows on a single key sending a sustained rate above its steady rate.

**R-14** — the shared burst pool must refill at a rate the operator configures.

**R-15** — the limiter must reject a request when both the key bucket and the shared pool are empty.

### 5.4 Response contract

**R-16** — a throttled response must carry status `429` (RFC 6585 §4).

**R-17** — a throttled response must carry `Retry-After` in delta-seconds (RFC 9110 §10.2.3).

**R-18** — every response to a key-carrying request must carry `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`.

**R-19** — the response body of a `429` must carry an error code of `quota_exceeded` or `burst_exhausted`.

**R-20** — the limiter must not return `503` for a throttling decision.

**R-21** — `Retry-After` must not exceed 60 seconds.

### 5.5 Client retry contract

The published API documentation must state R-22 through R-26 as client obligations.

**R-22** — a client must treat `429` as retryable for every HTTP method.

**R-23** — a client must not resend before the `Retry-After` interval has elapsed.

**R-24** — a client must add a random delay drawn uniformly from `[0, Retry-After × 0.2]`.

**R-25** — a client must stop after 5 consecutive throttled attempts and surface the error.

**R-26** — a client must not open additional connections while it holds a throttled request.

### 5.6 Degraded operation

**R-27** — the limiter must fall back to per-instance local buckets when the decision store is unreachable.

**R-28** — a local fallback bucket must use `configured rate ÷ instance count` as its rate.

**R-29** — the limiter must emit a `limiter_degraded` metric while the fallback is active.

**R-30** — the limiter must not admit an unlimited request rate while the decision store is unreachable.

### 5.7 Observability

**R-31** — the limiter must emit a counter of admitted and rejected requests, labelled by key and error code.

**R-32** — the limiter must emit the remaining shared-pool tokens as a gauge.

**R-33** — the limiter must log every rejection with the key identifier and the bucket that was empty.

**R-34** — the metrics must distinguish shadow-mode decisions from enforced decisions.

### 5.8 Rollout

**R-35** — the limiter must support shadow mode per key and globally.

**R-36** — an operator must be able to disable enforcement without a redeploy.

---

## 6. Use cases

### UC-1 — a high-volume key stays inside its quota

Actor: an API client. Precondition: the key's request rate is below its steady rate.

1. The client sends a request. Postcondition: the limiter charges one token.
2. The limiter admits the request. Postcondition: the handler runs.
3. The API responds. Postcondition: the response carries `RateLimit-Remaining`.

### UC-2 — a key exceeds its steady rate and draws from the shared pool

Precondition: the key bucket is empty; the shared pool holds tokens.

1. The client sends a request. Postcondition: the key bucket has no token.
2. The limiter draws one token from the shared pool. Postcondition: the pool gauge falls by one.
3. The limiter admits the request. Postcondition: the handler runs.

### UC-3 — the shared pool is empty

Precondition: the key bucket is empty; the shared pool is empty.

1. The client sends a request. Postcondition: no token is available.
2. The limiter rejects the request. Postcondition: status is `429`, error code is `burst_exhausted`.
3. The limiter sets `Retry-After`. Postcondition: the value is the pool refill interval, capped at 60 s.

### UC-4 — one key raises its rate far above its quota

Precondition: one key sends 10× its steady rate.

1. The key bucket empties. Postcondition: the key draws from the shared pool.
2. The key reaches the 25% share cap of R-13. Postcondition: further draws are refused.
3. The limiter rejects the excess. Postcondition: other keys still obtain shared-pool tokens.
4. The pool free-connection count stays above zero. Postcondition: no saturation alarm fires.

### UC-5 — a throttled client retries

1. The client receives `429` with `Retry-After: 2`. Postcondition: the request was not processed.
2. The client waits 2 s plus a jitter from `[0, 0.4 s]`. Postcondition: the wait satisfies R-23 and R-24.
3. The client resends. Postcondition: attempt count increments.
4. After 5 throttled attempts the client stops. Postcondition: the error reaches the caller.

### UC-6 — the decision store is unreachable

1. The decision store stops answering. Postcondition: the limiter records the failure.
2. The limiter switches to local buckets at `rate ÷ instance count`. Postcondition: R-28 holds.
3. The limiter emits `limiter_degraded`. Postcondition: the alert fires.
4. The store returns. Postcondition: the limiter resumes shared state within 60 s.

### UC-7 — an operator raises one key's quota

1. The operator sets a new steady rate for the key. Postcondition: the configuration records the value.
2. The limiter reloads the value. Postcondition: the new rate applies within 60 s (R-11).
3. The next response carries the new `RateLimit-Limit`. Postcondition: the client observes the change.

### UC-8 — shadow-mode rollout

1. The operator enables shadow mode globally. Postcondition: no request is rejected.
2. The limiter records would-reject decisions. Postcondition: metrics carry the shadow label.
3. The team reads the would-reject count per key. Postcondition: the quota values of R-8 are re-derived.
4. The operator enables enforcement. Postcondition: rejections return `429`.

---

## 7. Acceptance criteria

**AC-1** — 200 requests at 2× the steady rate from one key → at least 100 responses carry `429`; fails when the rate check in the limiter is removed.

**AC-2** — a rejected request → the handler records no invocation; fails when the limiter is moved after the handler in the middleware chain.

**AC-3** — a rejected request → the response carries `Retry-After` with an integer value in `[1, 60]`; fails when the `Retry-After` cap of R-21 is removed.

**AC-4** — any admitted request with a key → the response carries all three `RateLimit-*` fields; fails when one header write is deleted.

**AC-5** — one key sending 10× its steady rate for 60 s, with nine other keys at half their steady rate → every other key receives zero `429` responses; fails when the 25% share cap of R-13 is removed.

**AC-6** — the same scenario as AC-5 → the pool free-connection gauge stays above zero for the full 60 s; fails when the limiter is disabled.

**AC-7** — a rejection caused by the shared pool → the body error code is `burst_exhausted`; fails when both rejection paths return one code.

**AC-8** — a rejection caused by the key bucket → the body error code is `quota_exceeded`; fails when both rejection paths return one code.

**AC-9** — the decision store is stopped, then 200 requests arrive at 2× the steady rate → rejections continue and `limiter_degraded` is non-zero; fails when the fallback branch returns "admit".

**AC-10** — a quota change written to configuration → a response reflects the new `RateLimit-Limit` within 60 s; fails when the reload interval is raised past 60 s.

**AC-11** — a request with no API key → the response is `401` and no token is charged; fails when the key check is moved after quota evaluation.

**AC-12** — shadow mode enabled, then 200 requests at 2× the steady rate → zero `429` responses and a non-zero shadow-reject counter; fails when the shadow branch calls the reject path.

**AC-13** — the public API documentation states R-22 through R-26 as client obligations.

**AC-14** — the published error reference lists `quota_exceeded` and `burst_exhausted` with their `Retry-After` semantics.

---

## 8. Risks

| Id | Risk | Severity | Detected by |
| :--- | :--- | :--- | :--- |
| RISK-1 | Quota set below real demand → legitimate clients receive `429` | `Major` | Shadow-mode would-reject count per key (UC-8) |
| RISK-2 | Per-instance counters only → effective limit is `N ×` configured | `Critical` | AC-5 run against a multi-instance deployment |
| RISK-3 | Decision store adds latency to every request → p99 rises | `Major` | Latency comparison across the shadow-mode window |
| RISK-4 | Synchronised client retries after a shared-pool reset → a rate spike at the reset instant | `Major` | AC-5 with jitter disabled in the test client |
| RISK-5 | Store outage with a fail-open branch → the P-3 condition returns | `Critical` | AC-9 |
| RISK-6 | Uniform default tier → one large key consumes the shared pool alone | `Major` | AC-5 |

---

## 9. Decisions

**D-1, 2026-08-05, API platform lead:** the limiter uses a token bucket per key. Rejected: a fixed window counter — a fixed window admits 2× the configured rate across a window boundary.

**D-2, 2026-08-05, API platform lead:** enforcement runs in API middleware before the route handler. Rejected: per-client limits inside the database — the pool carries no key attribution, and no `429` can be produced there.

**D-3, 2026-08-05, API platform lead:** bucket state lives in a shared decision store. Rejected: per-instance counters only — with `N` instances the effective limit is `N ×` the configured value (RISK-2).

**D-4, 2026-08-05, API platform lead:** a throttled request returns `429` with `Retry-After`. Rejected: `503` — `503` triggers client failover and gateway-level retries, which raises the arrival rate.

**D-5, 2026-08-05, API platform lead:** a store outage degrades to local buckets at `rate ÷ instance count`. Rejected: fail-open — fail-open reproduces the P-3 condition during the outage.

**D-6, 2026-08-05, API platform lead:** quotas are configured per key and hot-reloaded within 60 s. Rejected: quotas in the deployment manifest — a quota change would then wait for the next release.

**D-7, 2026-08-05, API platform lead:** the limiter ships in shadow mode for 7 days before enforcement. Rejected: direct enforcement — the quota inputs of R-8 carry no measurement (OQ-1).

**D-8, 2026-08-05, API platform lead:** every request costs one token in this release. Rejected: per-endpoint weights — endpoint cost is unmeasured, and a wrong weight is not distinguishable from a wrong quota.

**D-9, 2026-08-05, API platform lead:** one key may hold at most 25% of the shared pool. Rejected: an unrestricted shared pool — one key then drains the pool, which is the P-3 condition.

---

## 10. Open questions

**OQ-1** — what are the connection pool size, the target utilisation and the mean pool hold time per request? Blocks: the derived value in R-8. Owner: API platform team.

**OQ-2** — what request share does each key percentile carry over a 7-day window? Blocks: the tier boundaries behind R-5 and R-10. Owner: API platform team.

**OQ-3** — which revision of `draft-ietf-httpapi-ratelimit-headers` do the response headers conform to? Blocks: R-18. Owner: API platform lead.

**OQ-4** — does a rejected request count toward any per-key accounting other than the quota? Blocks: R-6 and the metrics of R-31. Owner: API platform team.

**OQ-5** — is the shared burst pool global, or one pool per endpoint group? Blocks: R-12, R-13, R-14. Owner: API platform lead.

**OQ-6** — what steady rate does the default tier carry for a key with no configuration? Blocks: R-5. Owner: API platform lead.

**OQ-7** — are internal service-to-service keys exempt from the quota? Blocks: the scope statement in §2. Owner: API platform lead.

**OQ-8** — which incident records correspond to the two pool exhaustions in P-3? Blocks: the evidence citation in §4. Owner: on-call rotation.

**OQ-9** — which decision store is used, and what latency does it add at p99? Blocks: RISK-3 and R-27. Owner: API platform team.

**OQ-10** — is a throttled request allowed to consume a client's concurrent-connection allowance? Blocks: R-26. Owner: API platform lead.