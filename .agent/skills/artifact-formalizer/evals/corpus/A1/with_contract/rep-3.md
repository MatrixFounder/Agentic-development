# TASK-114 — Per-key rate limiting for the public HTTP API

| Field | Value |
| :--- | :--- |
| Status | Draft |
| Owner | API platform lead |
| Date | 2026-08-05 |
| Severity vocabulary | `SEV-1`, `SEV-2`, `SEV-3` |
| Modal keywords | MUST, MUST NOT, SHOULD (RFC 2119) |

---

## 1. Goal

Limit requests per API key so that no single key exhausts the database connection pool.

---

## 2. Problem

### 2.1 Observations

| id | Observation | Source |
| :--- | :--- | :--- |
| OB-1 | The public HTTP API enforces no request rate limit. | project brief, 2026-08-05 |
| OB-2 | Every client authenticates with an API key. | project brief, 2026-08-05 |
| OB-3 | A small subset of keys produces most of the request volume. | project brief, 2026-08-05 |
| OB-4 | One client exhausted the database connection pool on two occasions. | project brief, 2026-08-05 |
| OB-5 | No published contract tells a client how to retry after rejection. | project brief, 2026-08-05 |

The per-key rate distribution behind OB-3 is not measured. OQ-1 carries that measurement.

### 2.2 Failure modes

| id | Condition → observable outcome | Detected by | Severity |
| :--- | :--- | :--- | :--- |
| RK-1 | One key opens unbounded concurrent requests → the pool holds no free connection and unrelated keys receive errors | AC-9 | `SEV-1` |
| RK-2 | The rejection path checks out a connection → throttling leaves the pool unprotected | AC-3 | `SEV-1` |
| RK-3 | Each gateway instance counts separately → the effective limit equals `R_key` × instance count | AC-6 | `SEV-2` |
| RK-4 | Clients retry a 429 without delay → retry traffic sustains the overload | AC-4, AC-13 | `SEV-2` |
| RK-5 | The shared burst bucket has no per-key cap → one key drains it and RK-1 recurs | AC-7 | `SEV-2` |
| RK-6 | The limiter store is unreachable and the gateway passes all traffic → RK-1 recurs | AC-12 | `SEV-2` |

---

## 3. Definitions

- **Key identifier** is the non-secret part of an API key that names the calling client.
- **Token bucket** is a rate-limiting structure that holds up to `Cap` tokens and refills at `R` tokens per second.
- **Key bucket** is a token bucket bound to one key identifier.
- **Shared burst bucket** is a token bucket that all key identifiers draw from when their key bucket is empty.
- **Throttled request** is a request that the gateway answers with status 429 and no handler execution.
- **Observe mode** is a per-key setting under which the gateway counts a throttled request and answers it normally.
- **`SEV-1`** is a defect class that makes the API unavailable to keys other than the offending one.
- **`SEV-2`** is a defect class that degrades enforcement without causing an outage.
- **`SEV-3`** is a defect class confined to reporting or documentation.

---

## 4. Scope

In scope: per-key token buckets, one shared burst bucket, per-key concurrency ceilings, the throttled response format, the published client retry contract, limiter configuration reload, and throttle metrics.

Out of scope: monetised quota plans and billing (billing team); network-layer volumetric attack filtering (network team); authentication and key issuance changes (identity team); per-endpoint cost weighting (deferred, not scheduled); client SDK changes (client SDK owners); connection pool sizing (platform team); limits on internal service-to-service traffic (platform team).

---

## 5. Requirements

### 5.1 Enforcement point

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-1 | The gateway MUST resolve the key identifier before limit evaluation. | AC-16 |
| R-2 | The gateway MUST evaluate the limit before the request reaches a handler. | AC-3 |
| R-3 | A throttled request MUST NOT check out a database connection. | AC-3 |

**Why.** OB-4 shows connection exhaustion ⇒ a limit evaluated after checkout leaves RK-2 open.

### 5.2 Per-key quota

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-4 | The gateway MUST hold one key bucket per key identifier. | AC-1 |
| R-5 | Each key bucket MUST refill at `R_key` tokens per second. | AC-1 |
| R-6 | Each key bucket MUST hold at most `Cap_key` tokens. | AC-1 |
| R-7 | An accepted request MUST consume exactly one token. | AC-1 |
| R-8 | A throttled request MUST consume no token. | AC-5 |
| R-9 | `R_key` and `Cap_key` MUST be configurable per key identifier. | AC-8 |
| R-10 | A key identifier with no explicit configuration MUST use the default tier values. | AC-16 |

**Why.** R-8 keeps a throttled client from extending its own lockout window.

### 5.3 Shared burst allowance

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-11 | The gateway MUST hold one shared burst bucket for all key identifiers. | AC-2 |
| R-12 | A request MUST draw from the shared burst bucket only when its key bucket holds no token. | AC-2 |
| R-13 | The gateway MUST cap one key identifier's draw at `S_key` tokens per 60 seconds. | AC-7 |
| R-14 | The shared bucket refill rate MUST NOT depend on the number of registered keys. | AC-7 |

**Why.** OB-4 records one client exhausting a shared resource ⇒ an uncapped shared bucket reproduces that outcome.

### 5.4 Concurrency ceiling

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-15 | The gateway MUST limit concurrent requests per key identifier to `C_key`. | AC-9 |
| R-16 | A request above `C_key` MUST receive status 429. | AC-9 |

**Why.** A rate limit bounds requests per second, not requests held open at once. Slow handlers hold connections, so RK-1 survives a rate limit alone.

### 5.5 Throttled response

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-17 | A throttled response MUST carry status 429 (RFC 6585 §4). | AC-3 |
| R-18 | A throttled response MUST carry `Retry-After` in delta-seconds (RFC 9110 §10.2.3). | AC-4 |
| R-19 | The `Retry-After` value MUST equal the whole seconds until the key bucket holds one token, rounded up. | AC-4 |
| R-20 | Every response MUST carry the rate-limit fields pinned in D-4. | AC-15 |
| R-21 | A throttled response body MUST use `application/problem+json` (RFC 9457) with a stable `type` URI. | AC-10 |
| R-22 | A response body or log record MUST NOT contain the API key secret. | AC-14 |

R-22 shows a violation on a request whose secret is `sk_live_0000`: that literal appears in the response body or in a log line.

### 5.6 Published client retry contract

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-23 | The public documentation MUST state that a client waits at least `Retry-After` seconds. | AC-13 |
| R-24 | The documentation MUST state that a client adds a random delay of 0 to 1000 ms to that wait. | AC-13 |
| R-25 | The documentation MUST state that a client retries a throttled request at most 5 times. | AC-13 |
| R-26 | The documentation MUST state that the retry contract covers status 429 only. | AC-13 |
| R-27 | The documentation MUST publish the `type` URI of R-21 and each body field. | AC-13 |

**Why.** RK-4 needs a published delay rule. Synchronised retries without jitter re-create the original burst.

### 5.7 Operability

| id | Requirement | Verified by |
| :--- | :--- | :--- |
| R-28 | The gateway MUST export a throttle counter labelled by key identifier and by rejection reason. | AC-11 |
| R-29 | The gateway MUST apply a limit configuration change within 30 seconds and without a restart. | AC-8 |
| R-30 | Each key identifier MUST carry mode `observe` or mode `enforce`. | AC-11 |
| R-31 | In mode `observe` the gateway MUST answer normally and MUST increment the throttle counter. | AC-11 |
| R-32 | Limiter state MUST be shared across all gateway instances. | AC-6 |
| R-33 | The gateway MUST take one documented, deterministic action when the limiter store is unavailable. | AC-12 |

R-33 is blocked by OQ-3, which selects that action.

### 5.8 Derived numbers

- N-1 — `R_key` default = 2 × the p95 per-key request rate; measured: pending OQ-1; applied: pending OQ-1. `R_key` is a ceiling on sustained rate.
- N-2 — `C_key` = floor(0.25 × connection pool size); measured: pending OQ-2; applied: pending OQ-2. `C_key` is a ceiling on concurrent requests per key.
- N-3 — `S_key` = 0.25 × the shared bucket capacity; measured: not applicable, this value is chosen; applied: pending OQ-1. `S_key` is a ceiling on one key's shared draw.
- N-4 — `Retry-After` granularity = 1 second, the delta-seconds unit of RFC 9110 §10.2.3; measured: not applicable; applied: 1 second.

---

## 6. Use cases

### UC-1 — Request within the key quota

Actor: API client. Precondition: the key bucket holds at least one token.

1. The gateway resolves the key identifier. Postcondition: the key configuration is loaded.
2. The gateway removes one token from the key bucket. Postcondition: the key bucket count drops by one.
3. The handler runs and the gateway returns the handler response. Postcondition: the response carries the R-20 fields.

### UC-2 — Burst absorbed by the shared bucket

Actor: API client. Precondition: the key bucket is empty and the shared bucket holds tokens.

1. The gateway finds the key bucket empty. Postcondition: the shared-draw path is selected.
2. The gateway checks the key's draw against `S_key`. Postcondition: the draw is below `S_key`.
3. The gateway removes one token from the shared bucket. Postcondition: the shared bucket count drops by one.
4. The handler runs and the gateway returns the handler response. Postcondition: `RateLimit-Remaining` reports `0` for the key bucket.

### UC-3 — Key exceeds both allowances

Actor: API client. Precondition: the key bucket is empty and the key reached `S_key`.

1. The gateway rejects the request before handler dispatch. Postcondition: no connection is checked out.
2. The gateway computes the seconds until the next key token. Postcondition: the value is a whole number of seconds.
3. The gateway returns 429 with `Retry-After` and the R-21 body. Postcondition: the throttle counter increments by one.

### UC-4 — Client retries after a throttled response

Actor: API client. Precondition: the client holds a 429 response with `Retry-After: 4`.

1. The client waits 4 seconds. Postcondition: the key bucket refill has run.
2. The client waits an additional random delay of 0 to 1000 ms. Postcondition: two clients that were throttled together resume at different instants.
3. The client repeats the request. Postcondition: the attempt counter for this request increments.
4. The client stops after 5 throttled attempts. Postcondition: the client surfaces the failure to its caller.

### UC-5 — Operator raises a key's quota

Actor: operator. Precondition: the key identifier exists in the limiter configuration.

1. The operator writes a new `R_key` value to the configuration. Postcondition: the configuration store holds the new value.
2. The gateway reloads the configuration. Postcondition: the new value applies within 30 seconds.
3. The operator reads the throttle counter for that key. Postcondition: the counter stops increasing for that key.

### UC-6 — Rollout in observe mode

Actor: operator. Precondition: a key identifier carries mode `observe`.

1. The gateway evaluates the limit on every request. Postcondition: the throttle counter records every request that would be rejected.
2. The gateway answers each request normally. Postcondition: no client receives 429 for that key.
3. The operator compares the counter against the key's traffic. Postcondition: the operator holds evidence for switching the key to `enforce`.

### UC-7 — Limiter store unavailable

Actor: gateway. Precondition: the limiter store returns errors for every operation.

1. The gateway detects the store error. Postcondition: the metric `limiter_store_unavailable` increments.
2. The gateway applies the action selected by OQ-3. Postcondition: the action matches the published documentation.

---

## 7. Acceptance criteria

Each entry is a test obligation. The mutation clause names the change that must turn the test red.

- AC-1 — 10 requests at 5 req/s against `R_key` = 10 → every response is 200; fails when a request consumes two tokens.
- AC-2 — empty key bucket, non-empty shared bucket → response is 200 and `RateLimit-Remaining` is `0`; fails when the shared-draw path is removed.
- AC-3 — empty key bucket, exhausted `S_key` → response is 429 and the driver reports zero new connections; fails when limit evaluation moves after connection checkout.
- AC-4 — throttled response → `Retry-After` equals the rounded-up seconds to the next key token; fails when the value becomes a constant.
- AC-5 — throttled request → the key bucket token count is unchanged; fails when the rejection path consumes a token.
- AC-6 — two gateway instances, `R_key` = 10, client sends 20 req/s → accepted rate is 10 ± 1 req/s; fails when counters become per-instance.
- AC-7 — key A draws above `S_key`, key B is idle → key A receives 429 and key B receives 200; fails when the `S_key` cap is removed.
- AC-8 — configuration sets a new `R_key` → the new rate applies within 30 s with no restart; fails when the value is read once at startup.
- AC-9 — one key sends 10 × `R_key` with `C_key` concurrency for 5 minutes → free pool connections stay above zero for the whole run; fails when R-15 is reverted.
- AC-10 — throttled response → `Content-Type` is `application/problem+json` and `type` matches the published URI; fails when the body becomes `text/plain`.
- AC-11 — key in mode `observe` above quota → every response is 200 and the throttle counter increments; fails when mode `observe` rejects.
- AC-12 — limiter store returns errors → the gateway applies the OQ-3 action and increments `limiter_store_unavailable`; fails when requests pass without limit evaluation.
- AC-13 — the published documentation states R-23 through R-27 (documentation check).
- AC-14 — a request with secret `sk_live_0000` → that literal appears in no response body and no log record; fails when the secret is added to the log context.
- AC-15 — accepted response → the R-20 fields are present; fails when the fields are emitted only on 429.
- AC-16 — unconfigured key identifier → the default tier limit applies; fails when an unconfigured key receives unlimited service.

---

## 8. Decisions

- D-1, 2026-07-22, API platform lead: per-key token bucket plus one shared burst bucket. Rejected: fixed-window counter — a request pair straddling a window boundary passes 2 × the configured rate within one second.
- D-2, 2026-07-22, API platform lead: limit evaluation runs at the gateway, before handler dispatch and before connection checkout. Rejected: in-handler middleware — a rejected request has already checked out a connection, which leaves RK-1 open.
- D-3, 2026-07-29, platform team: limiter state lives in a shared store, mutated by one atomic script per request. Rejected: per-instance in-memory counters — with N instances the effective limit is N × `R_key` (RK-3).
- D-4, 2026-07-29, API platform lead: the throttled response uses status 429, `Retry-After`, and the `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` field triple; the field specification version is pinned in OQ-4. Rejected: status 503 — 503 reports server state, so a client applies its retry policy to unaffected endpoints as well.
- D-5, 2026-07-31, API platform lead: quotas key on the key identifier, not on the client IP address. Rejected: per-IP quotas — one NAT egress address maps to many customers, so a quota would bind unrelated clients together.
- D-6, 2026-08-03, API platform lead: every key starts in mode `observe` and moves to mode `enforce` per key. Rejected: direct enforcement for all keys — no measured per-key distribution exists yet (OQ-1), so the default tier would be a guess.
- D-7, 2026-08-03, API platform lead: `Retry-After` reports the key bucket recovery time, not the shared bucket recovery time. Rejected: reporting the shared value — the shared value depends on other clients, so the same key receives different delays for the same state.

---

## 9. Open questions

- OQ-1 — What is the per-key request rate distribution over the last 30 days, at p50, p95 and max? Blocks: N-1, N-3, the default tier values in R-10. Owner: SRE on-call.
- OQ-2 — What is the database connection pool size per API instance, and how many instances run? Blocks: N-2, the `C_key` value in R-15. Owner: platform team.
- OQ-3 — When the limiter store is unavailable, does the gateway pass the request or reject it? Blocks: R-33, AC-12, UC-7 step 2. Owner: API platform lead with the security reviewer.
- OQ-4 — Which version of the `RateLimit` header field specification does the gateway implement, and has that specification been published as an RFC? Blocks: D-4, R-20, AC-15. Owner: API platform lead.
- OQ-5 — Do the two pool-exhaustion events in OB-4 have incident records, and what request pattern do those records show? Blocks: the load profile of AC-9. Owner: SRE on-call.
- OQ-6 — Does the shared burst bucket serve write endpoints, or read endpoints only? Blocks: R-11, R-12, UC-2. Owner: API platform lead.
- OQ-7 — Which keys, if any, hold a contractual rate commitment that the default tier would breach? Blocks: the mode `enforce` rollout in D-6. Owner: account management.
- OQ-8 — How long does a key stay in mode `observe` before the switch to mode `enforce`? Blocks: D-6 execution. Owner: API platform lead.