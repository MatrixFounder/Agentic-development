# TASK — Per-key rate limiting for the public HTTP API

**Status:** draft. **Date:** 2026-08-05. **Owner:** API platform lead.
**Severity vocabulary used in §10:** `Critical`, `Major`, `Minor`.

---

## 1. Goal

Enforce a per-key quota at the gateway so that upstream request rate stays under 3000 req/s.

---

## 2. Problem

- The public API applies no request limit today.
- Every admitted request checks out one connection from the database pool.
- The pool reached 120 of 120 connections on 2026-05-14 and on 2026-07-02.
- During those two windows the API returned status 500 to all clients for 6 and 11 minutes.
- In the 2026-07-02 window one API key sent 1900 req/s for 4.2 s.
- Three keys produced 78% of requests over the 30 days to 2026-07-31.
- The published documentation states no client behaviour for a rejected request.

### 2.1 Measured inputs

Every number in §6 derives from this table. A number without a row here is an Open Question.

| id | value | source |
| :--- | :--- | :--- |
| M-1 | pool size: 120 connections | pool configuration, 2026-07-31 |
| M-2 | mean connection hold time: 40 ms | query log, 30 days to 2026-07-31 |
| M-3 | active keys per 5-minute window, p95: 42 | gateway access log, same window |
| M-4 | 3 keys produce 78% of requests | gateway access log, same window |
| M-5 | peak single-key rate: 1900 req/s for 4.2 s | incident record 2026-07-02 |
| M-6 | pool exhaustion events: 2 | incident records 2026-05-14, 2026-07-02 |
| M-7 | client burst length, p99: 1.8 s | gateway access log, same window |
| M-8 | response latency p99: 180 ms | gateway metrics, same window |
| M-9 | counter store restart duration: 40 s | store runbook |

---

## 3. Scope

**In scope.**

- one token bucket per API key at the gateway
- one shared burst bucket across all keys
- the 429 response contract and its headers
- the retry rule published in client documentation
- per-key limit override by an operator
- rejection metrics, alerts and logs
- shadow mode for rollout

**Out of scope.**

- API-key issuance, rotation and authentication — identity service
- per-endpoint request weighting — deferred, D-6, OQ-3
- paid quota tiers and billing — commerce team
- L3/L4 volumetric filtering — edge provider
- per-IP limits on unauthenticated traffic — edge provider
- retry code inside the published SDKs — SDK maintainers
- rate limiting of internal service-to-service traffic — OQ-4
- resizing the database connection pool — database owner

---

## 4. Definitions

**Quota subject** is the identity the gateway counts requests against. In this document it is one API key (D-9).

**Token bucket** is a counter that refills at a fixed rate and stops at a fixed capacity.

**Per-key bucket** is a token bucket whose quota subject is one API key.

**Shared burst bucket** is a token bucket that any key draws from after its per-key bucket reaches zero.

**Throttled request** is a request the gateway rejects with status 429.

**Key fingerprint** is the first 8 hexadecimal characters of the SHA-256 digest of an API key.

**Shadow mode** is a gateway mode that records every limit decision and admits every request.

**Counter store** is the shared datastore that holds bucket state for all gateway instances.

---

## 5. Decisions

**D-1**, 2026-08-05, API platform lead: one token bucket per key plus one shared burst bucket. Rejected: fixed-window counter — admits 2 × limit across a window boundary. Rejected: sliding-window log — stores one entry per request, 1900 entries/s for one key (M-5).

**D-2**, 2026-08-05, API platform lead: evaluate the quota in the gateway, before upstream routing. Rejected: per-service middleware — each service counts independently and the pool receives the sum.

**D-3**, 2026-08-05, platform architect: hold bucket state in a shared counter store. Rejected: per-instance memory — the effective limit multiplies by the instance count, 400 req/s per key at 8 instances.

**D-4**, 2026-08-05, API platform lead: reject with status 429 and a `Retry-After` header. Rejected: 503 — the published SDKs retry 503 without reading `Retry-After` (OQ-5).

**D-5**, 2026-08-05, platform architect: on counter store failure, each instance applies a local limit. Rejected: admitting every request — reproduces M-6. Rejected: rejecting every request — a 40 s restart (M-9) rejects all traffic for 40 s.

**D-6**, 2026-08-05, API platform lead: charge one token per request, with no per-endpoint weight. Rejected: per-endpoint weights — no per-endpoint hold-time measurement exists (OQ-3).

**D-7**, 2026-08-05, API platform lead: run 14 days in shadow mode before enforcement. Rejected: immediate enforcement — 3 keys (M-4) exceed the new limit today.

**D-8**, 2026-08-05, API platform lead: emit `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`. Rejected: `X-RateLimit-*` — RFC 6648 deprecates the `X-` prefix.

**D-9**, 2026-08-05, platform architect: the quota subject is the API key. Rejected: account-level quota — the mapping costs one identity-service call per request.

---

## 6. Derived numbers

**N-1** — 3000 req/s = 120 connections ÷ 0.040 s; measured M-1 and M-2; applied 2100 req/s as the sustained budget. 3000 req/s is the ceiling; 2100 req/s is the applied value.

**N-2** — 50 tokens/s = 2100 req/s ÷ 42 keys; measured M-3; applied 50 tokens/s per key. The applied value is a ceiling per key.

**N-3** — 100 tokens = 2 s × 50 tokens/s; measured burst length p99 of 1.8 s (M-7); applied 100 tokens as per-key bucket capacity. The applied value is a ceiling.

**N-4** — 900 tokens/s = 3000 − 2100; capacity 4500 tokens = 5 s × 900 tokens/s; measured longest single-key burst 4.2 s (M-5); applied 4500 tokens. The applied value is a ceiling.

**N-5** — 1500 tokens = 4500 ÷ 3; measured 3 keys at 78% of load (M-4); applied 1500 tokens as the per-key draw from the shared bucket. The applied value is a ceiling.

**N-6** — 5 ms = 2.8% of 180 ms; measured response latency p99 of 180 ms (M-8); applied 5 ms as the added latency budget. The applied value is a ceiling.

---

## 7. Requirements

### 7.1 Enforcement point

**R-1** — The gateway must evaluate the quota before it routes a request upstream.

> **Why.** Both events in M-6 began after the request reached the service and checked out a connection.

**R-2** — The gateway must not charge a token for a request that authentication rejects.
Violation input: a request carrying a revoked key returns 401 and the key's token count drops.

**R-3** — The gateway must hold quota state in the shared counter store (D-3).

### 7.2 Per-key bucket

**R-4** — The gateway must hold one token bucket per API key.

**R-5** — Each per-key bucket must refill at 50 tokens per second (N-2).

**R-6** — Each per-key bucket must stop refilling at 100 tokens (N-3).

**R-7** — The gateway must charge one token per admitted request (D-6).

### 7.3 Shared burst bucket

**R-8** — The gateway must draw from the shared bucket when the per-key bucket holds no token.

**R-9** — The shared bucket must refill at 900 tokens per second and stop at 4500 tokens (N-4).

**R-10** — The gateway must not grant one key more than 1500 shared tokens per rolling 5 seconds (N-5).
Violation input: one key at 2000 req/s for 5 s receives 1501 shared grants.

### 7.4 Rejection response

**R-11** — The gateway must reject a request with status 429 when both buckets hold no token.

**R-12** — The gateway must not answer a quota rejection with status 503 (D-4).
Violation input: a key over quota receives 503 with an empty `Retry-After`.

**R-13** — A 429 response must carry `Retry-After` as a whole number of seconds (RFC 9110 §10.2.3).

**R-14** — `Retry-After` must equal the seconds until the per-key bucket holds one token, rounded up, minimum 1.

**R-15** — The gateway must not emit `Retry-After` in HTTP-date form.
Violation input: a 429 response carrying `Retry-After: Wed, 05 Aug 2026 10:00:00 GMT`.

**R-16** — A 429 body must use `application/problem+json` (RFC 9457) with `type`, `title`, `status` and `retry_after`.

**R-17** — Every response must carry `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` (D-8).

### 7.5 Retry contract

**R-18** — The public API documentation must publish the procedure in §8 as the retry rule.

**R-19** — The documentation must state that a 429 retry repeats no side effect.

> **Why.** R-1 places the rejection before the service, so the rejected request changed no state.

**R-20** — The documented rule must cap the wait at 60 seconds and the attempts at 6.

### 7.6 Operations

**R-21** — An operator must be able to set a per-key limit override without a deployment.

**R-22** — An override must take effect on every gateway instance within 30 seconds.

**R-23** — The gateway must keep answering requests while the counter store is unavailable (D-5).

**R-24** — While the counter store is unavailable, each instance must apply a local limit of 50 ÷ instance count tokens per second.

**R-25** — Added latency p99 from quota evaluation must stay at or below 5 ms (N-6).

### 7.7 Observability

**R-26** — The gateway must emit a rejection counter labelled by key fingerprint and by bucket.

**R-27** — A rejection log line must record the key fingerprint, both bucket counts and the decision.

**R-28** — Logs and metrics must not contain the API key.
Violation input: a rejection log line containing the literal key value.

**R-29** — The gateway must expose per-key utilisation as admitted rate divided by refill rate.

**R-30** — An alert must fire when one key holds utilisation above 0.8 for 5 minutes.

### 7.8 Rollout

**R-31** — The gateway must support shadow mode.

**R-32** — Shadow mode must produce the same decision record as enforcement mode.

---

## 8. Retry procedure (published to clients)

1. Read `Retry-After` from the 429 response. Postcondition: the client holds a delay in whole seconds.
2. Wait that delay plus a uniform random value in [0, 1) seconds. Postcondition: the client has waited at least `Retry-After` seconds.
3. Send the same request once. Postcondition: the client holds a new status code.
4. On a further 429, double the previous delay, up to 60 seconds. Postcondition: the next delay is at most 60 seconds.
5. Repeat steps 2 to 4 while attempts remain. Postcondition: the client has sent at most 6 requests.
6. After the sixth rejection, return the error to the caller. Postcondition: the client sends no further retry for this request.

---

## 9. Use cases

### UC-1 — A client stays inside its quota

- **Actor:** API client with a valid key.
- **Precondition:** the key sends 40 req/s.
- **Steps:** 1. The gateway charges one token per request. 2. The per-key bucket refills at 50 tokens/s.
- **Outcome:** the gateway admits every request and sets `RateLimit-Remaining` above 0.

### UC-2 — A client bursts above its quota

- **Actor:** API client with a valid key.
- **Precondition:** the shared bucket holds 4500 tokens; the key sends 300 req/s for 3 s.
- **Steps:** 1. The per-key bucket reaches zero. 2. The gateway draws the remainder from the shared bucket.
- **Outcome:** the gateway admits the burst and the shared bucket count drops.

### UC-3 — One key sends the incident traffic

- **Actor:** API client sending 1900 req/s (M-5).
- **Precondition:** the per-key bucket is full and the shared bucket is full.
- **Steps:** 1. The per-key bucket empties within 1 s. 2. The gateway grants at most 1500 shared tokens over 5 s (R-10). 3. The gateway rejects the remaining requests with 429.
- **Outcome:** upstream rate stays under 3000 req/s and other keys keep receiving 2xx.

### UC-4 — A throttled client retries

- **Actor:** API client holding a 429 response.
- **Precondition:** `Retry-After: 1`.
- **Steps:** 1. The client waits 1 s plus jitter (§8 step 2). 2. The client repeats the request.
- **Outcome:** the per-key bucket holds a token and the gateway admits the request.

### UC-5 — An operator raises a partner's limit

- **Actor:** operator.
- **Precondition:** the partner key runs at utilisation 0.95 and the alert of R-30 has fired.
- **Steps:** 1. The operator sets an override of 200 tokens/s. 2. Every gateway instance reads the override within 30 s.
- **Outcome:** the partner key runs at 200 req/s with no deployment.

### UC-6 — The counter store becomes unavailable

- **Actor:** gateway instance.
- **Precondition:** the counter store is restarting for 40 s (M-9).
- **Steps:** 1. The instance stops reaching the store. 2. The instance applies a local limit of 50 ÷ instance count.
- **Outcome:** the gateway keeps answering, and upstream rate stays under 3000 req/s.

### UC-7 — Rollout in shadow mode

- **Actor:** API platform lead.
- **Precondition:** the gateway runs in shadow mode for 14 days (D-7).
- **Steps:** 1. The gateway records each decision and admits every request. 2. The lead reads the count of would-be rejections per key. 3. The lead notifies each key above the limit.
- **Outcome:** the enforcement date is set and every affected key holds notice.

---

## 10. Risks

**RK-1** — `Critical` — Quota evaluated after connection checkout → the pool reaches 120 connections again (detected by AC-1).

**RK-2** — `Critical` — One key drains the shared bucket → other keys receive 429 during their own burst (detected by AC-4).

**RK-3** — `Major` — The counter store adds a round trip per request → response latency p99 exceeds 185 ms (detected by AC-11).

**RK-4** — `Major` — Clients retry without jitter → the rejection rate rises after each wave of 429 (detected by the rejection counter of R-26 during the shadow period).

**RK-5** — `Major` — Active keys exceed 42 → the sum of per-key quotas exceeds 3000 req/s (detected by the utilisation alert of R-30; see OQ-2).

**RK-6** — `Minor` — The counter store restarts → every instance limits locally and the effective ceiling drops (detected by AC-9).

---

## 11. Acceptance criteria

**AC-1** — request from a key with an empty bucket → no database connection is checked out; fails when the limiter runs after upstream routing. Covers R-1.

**AC-2** — one key at 50 req/s for 60 s, shared bucket empty → 0 rejections; fails when the refill constant drops below 50 tokens/s. Covers R-5.

**AC-3** — one key at 200 req/s for 10 s, full per-key bucket, shared bucket empty → at most 600 admitted; fails when the capacity constant rises above 100 tokens. Covers R-6.

**AC-4** — one key at 2000 req/s for 5 s, full shared bucket → at most 1500 shared grants; fails when the per-key shared cap is removed. Covers R-10.

**AC-5** — a rejected request → 429 with integer `Retry-After` at or above 1 and a `problem+json` body; fails when `Retry-After` is emitted in HTTP-date form. Covers R-11, R-13, R-15, R-16.

**AC-6** — the client waits `Retry-After`, then repeats, shared bucket empty → the request is admitted; fails when `Retry-After` rounds down. Covers R-14.

**AC-7** — 5 keys at 500 req/s each for 30 s → upstream rate stays at or below 3000 req/s; fails when the shared refill rises above 900 tokens/s. Covers R-8, R-9.

**AC-8** — replay of the 2026-07-02 capture → concurrent pool checkouts stay below 120; fails when the shared bucket capacity rises above 4500 tokens. Covers R-1, R-9, R-10.

**AC-9** — counter store returns errors for 60 s → in-quota traffic keeps receiving 2xx under the local limit; fails when the gateway answers 5xx on a store error. Covers R-23, R-24.

**AC-10** — request with a revoked key → 401 and an unchanged token count; fails when the limiter runs before authentication. Covers R-2.

**AC-11** — load test at 2100 req/s → added latency p99 at or below 5 ms; fails when quota evaluation makes more than one store round trip per request. Covers R-25.

**AC-12** — operator writes an override → every instance applies it within 30 s; fails when an instance serves the previous limit past 30 s. Covers R-21, R-22.

**AC-13** — a rejection log line → holds an 8-character fingerprint and no key; fails when the log formatter prints the raw key. Covers R-27, R-28.

**AC-14** — shadow mode over a fixed capture → the decision record equals the enforcement-mode record; fails when shadow mode skips the shared bucket. Covers R-31, R-32.

**AC-15** — documentation review → the retry rule states `Retry-After`, jitter, the 60 s cap and the 6-attempt limit. Covers R-18, R-20, §8. This check is not executable, so it names no mutation.

---

## 12. Open questions

**OQ-1** — Which version of the `RateLimit` header fields does the gateway pin? Blocks: R-17, client documentation. Owner: API platform lead.

**OQ-2** — What happens to the per-key limit when active keys exceed 42 (M-3)? Blocks: N-2, RK-5. Owner: capacity owner.

**OQ-3** — Do write endpoints hold a connection long enough to need a per-endpoint weight? Blocks: D-6 revisit. Owner: database owner.

**OQ-4** — Do internal service callers present API keys, and does the gateway see their traffic? Blocks: the internal-traffic exclusion in §3. Owner: platform architect.

**OQ-5** — What retry behaviour do the published SDKs implement today for 429 and 503? Blocks: D-4 justification, R-18. Owner: SDK maintainers.

**OQ-6** — Is a paid tier planned whose quota overrides R-5? Blocks: R-21 override model. Owner: product owner.

**OQ-7** — Does a key that holds an override still draw from the shared bucket? Blocks: R-8, R-21. Owner: API platform lead.