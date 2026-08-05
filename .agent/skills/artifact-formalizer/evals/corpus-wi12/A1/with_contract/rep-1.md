# TASK — Per-key rate limiting for the public HTTP API

| field | value |
| :--- | :--- |
| id | assigned on merge |
| status | Draft |
| owner | api-platform |
| date | 2026-08-05 |
| severity vocabulary | `Critical`, `Major`, `Minor` |

---

## 1. Problem

The public HTTP API enforces no request limit today. Clients authenticate with an API key on every request. Request volume is uneven across keys. A small number of keys produces most requests.

One client exhausted the backend database connection pool twice. During each exhaustion, requests from other keys failed. The gateway has no control that rejects a request before it reaches a handler. Operators have no per-key consumption metric. Clients have no documented rule for retrying a rejected request.

The two incident records are cited in Q-9.

## 2. Goal

Bound per-key request rate and concurrency at the gateway so that one key cannot exhaust the database connection pool.

## 3. Scope

**In scope.**

- per-key token-bucket quotas evaluated in the gateway
- a shared burst pool that any key may draw from
- a per-key concurrency cap and a gateway-wide concurrency cap
- the `429` response contract, including headers and body
- the client retry contract, published in the API reference
- quota configuration in the control plane
- metrics, logs and alerts for throttle decisions
- shadow mode and the staged rollout

**Out of scope.**

- authentication and API-key issuance — identity service
- per-IP limiting of unauthenticated traffic — edge provider (D-8)
- L3/L4 volumetric filtering — edge provider
- paid quota tiers and billing — commerce
- rate limiting of internal service-to-service traffic — platform networking (Q-7)
- retry logic inside published client SDKs — SDK maintainers (this document specifies the contract only, R-29)
- database connection pool sizing — backend service team
- per-endpoint request weighting — deferred (D-9)

## 4. Definitions

| term | definition |
| :--- | :--- |
| limiter | the gateway middleware that admits or rejects a request before routing |
| counter store | the Redis deployment that holds token buckets shared across gateway instances |
| per-key quota | the sustained request rate one API key may consume |
| burst capacity | the token count one key accumulates while idle |
| shared burst pool | a token bucket that serves any key whose own bucket is empty |
| concurrency cap | the maximum number of requests one key may have open at once |
| throttled request | a request the limiter rejects before any handler runs |
| degraded decision | an allow decision taken while the counter store is unreachable |
| shadow mode | a limiter setting that records decisions and rejects nothing |
| full jitter | a retry delay drawn uniformly from `[0, backoff]` |

## 5. Capacity inputs

Each input is an assumption until its open question closes.

| id | input | value | confirmed by |
| :--- | :--- | :--- | :--- |
| A-1 | database connection pool size | 100 connections | Q-1 |
| A-2 | mean connection hold time | 25 ms | Q-1 |
| A-3 | gateway instances, steady | 6 | Q-2 |
| A-4 | gateway instances, autoscaling maximum | 12 | Q-2 |
| A-5 | active API keys | 400, of which 10 are high tier | Q-3 |
| A-6 | backend request timeout | 30 s | confirmed |

## 6. Derived numbers

Every value below is provisional until the shadow period closes Q-3 (D-7).

- `pool_capacity = 4000 req/s` = A-1 (100) / A-2 (0.025 s); measured: pending Q-1; applied 4000; the applied value is a ceiling.
- `default_quota_rps = 5 req/s`; derivation: 390 default keys × 5 = 1950 req/s; measured: pending Q-3; applied 5; the applied value is a per-key ceiling.
- `default_burst_tokens = 50` = `default_quota_rps` × 10 s idle; measured: pending Q-3; applied 50; the applied value is a ceiling.
- `high_quota_rps = 50 req/s`; derivation: 10 high keys × 50 = 500 req/s; measured: pending Q-3; applied 50; the applied value is a per-key ceiling.
- `shared_rps = 500 req/s` = 12.5 % of `pool_capacity`; measured: pending Q-3; applied 500; the applied value is a ceiling.
- `shared_tokens = 1000` = `shared_rps` × 2 s; measured: pending Q-3; applied 1000; the applied value is a ceiling.
- `shared_key_max = 200` = 20 % of `shared_tokens` per 10 s window; measured: pending Q-3; applied 200; the applied value is a ceiling.
- `global_conc = 80` = 80 % of A-1 (100), reserving 20 connections for background work; measured: pending Q-1; applied 80; the applied value is a ceiling.
- `slot_ttl = 35 s` = A-6 (30 s) + 5 s; applied 35; the applied value is a ceiling.
- `limiter_latency_p99 = 3 ms` = one counter-store round trip (2 ms) + local evaluation (1 ms); measured: pending AC-12; applied 3; the applied value is a ceiling.
- `config_propagation = 60 s` = tier cache TTL (30 s) × 2; applied 60; the applied value is a ceiling.

Sum of granted sustained rates: 1950 + 500 + 500 = 2950 req/s, about 74 % of `pool_capacity`.

### 6.1 Tiers

| tier | `quota_rps` | `burst_tokens` | `key_conc` | degraded per-instance cap |
| :--- | :--- | :--- | :--- | :--- |
| `default` | 5 | 50 | 10 | 1 |
| `high` | 50 | 500 | 25 | 3 |

The degraded per-instance cap is `ceil(key_conc / A-4)`.

## 7. Requirements

### 7.1 Enforcement and keying

**R-1** — The limiter must reject a throttled request before any handler runs.

**Why.** A request that reaches a handler holds a pool connection ⇒ rejecting after routing does not protect the pool.

**R-2** — The gateway must authenticate the request before the limiter evaluates it.

**R-3** — The limiter must key every decision on the authenticated API key identifier.

**R-4** — A request that fails authentication must not consume tokens from any bucket.

### 7.2 Quota algorithm

**R-5** — Each key must have a token bucket that refills at `quota_rps` and caps at `burst_tokens`.

**R-6** — Each admitted request must cost one token, on every endpoint (D-9).

**R-7** — When a key bucket holds no token, the limiter must attempt one token from the shared pool.

**R-8** — The shared pool must be a token bucket that refills at `shared_rps` and caps at `shared_tokens`.

**R-9** — One key must not draw more than `shared_key_max` tokens from the shared pool per 10 s window.

**Why.** Without the per-key cap, one key consumes the whole shared pool ⇒ every other key falls back to its sustained rate. This is the observed incident pattern.

**R-10** — Token buckets must live in the counter store and must be shared across gateway instances.

**R-11** — The quota decision must complete in one round trip to the counter store.

### 7.3 Concurrency

**R-12** — The limiter must cap concurrent requests per key at `key_conc`, counted in the counter store.

**R-13** — Each concurrency slot must carry a TTL of `slot_ttl`.

**R-14** — The gateway must release the slot after the response is written, including on error and on client disconnect.

**Why.** A slot that leaks on disconnect throttles the key until an operator intervenes.

**R-15** — Slot release must not add latency to the response path.

**R-16** — The gateway must cap total concurrent backend requests at `global_conc`.

**R-17** — While the counter store is unreachable, each instance must cap per-key concurrency at `ceil(key_conc / A-4)`.

### 7.4 Response contract

**R-18** — Every throttled response must carry status `429`.

**R-19** — Every `429` must carry `Retry-After` as an integer number of seconds, minimum 1.

**R-20** — `Retry-After` must equal `ceil(tokens_needed / refill_rate)`, with a floor of 1.

**R-21** — Every response must carry `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset` (D-6).

**R-22** — The `429` body must be a problem detail per RFC 9457.

**R-23** — The problem detail must carry a `scope` member with one of `key`, `shared`, `concurrency`, `capacity`.

**R-24** — The response must not expose shared pool totals or the state of any other key.

**Why.** Shared pool state describes the aggregate traffic of other tenants.

**R-25** — A `429` must leave no side effect on server state.

### 7.5 Retry contract for clients

**R-26** — The API reference must state that a `429` leaves no side effect.

**Why.** No handler runs (R-1, R-25) ⇒ a retry is safe for every method, including `POST`.

**R-27** — A client must not send the retry before `Retry-After` seconds elapse.

**R-28** — A client must compute the delay as `Retry-After + uniform(0, min(30 s, 1 s × 2^(attempt−1)))`.

**Why.** A fixed delay makes every throttled client retry at the same instant.

**R-29** — A client must stop after 5 attempts and must surface the failure to its caller.

**R-30** — The retry contract must be published in the API reference and in the SDK documentation.

### 7.6 Configuration

**R-31** — Quotas must be stored per key in the control plane and must be editable without a deploy.

**R-32** — A quota change must take effect on every instance within `config_propagation`.

**R-33** — A key with no explicit tier must receive the `default` tier.

**R-34** — Each tier change must record the operator identifier and the previous value.

### 7.7 Observability

**R-35** — The limiter must emit a decision counter with labels `tier`, `scope`, `outcome`.

**R-36** — The key identifier must not appear as a metric label.

**Why.** Metric label cardinality grows with the key population, which A-5 puts at 400 and rising.

**R-37** — The gateway must write one structured log record per throttled request, with key id, scope and `Retry-After`.

**R-38** — The dashboard must show the top 20 keys by request count and the top 20 by throttle count.

**R-39** — An alert of severity `Major` must fire when the shared pool stays empty for more than 60 s.

**R-40** — An alert of severity `Major` must fire when degraded decisions exceed 1 % of requests over 5 min.

**R-41** — An alert of severity `Critical` must fire when the `capacity` scope rejects requests for more than 60 s.

### 7.8 Rollout

**R-42** — The limiter must support shadow mode, which records the decision and rejects nothing.

**R-43** — Shadow mode must run for 7 days before enforcement starts (D-7).

**R-44** — Tier values must be re-derived from shadow data before enforcement starts.

**R-45** — The limiter must expose a runtime flag that returns it to shadow mode without a deploy.

## 8. Use cases

**UC-1 — Request within quota.**
- Actor: client on the `default` tier.
- Precondition: the key bucket holds at least one token.
- Steps: 1. the gateway authenticates the key. 2. the limiter removes one token. 3. the handler runs.
- Outcome: `200`, with `RateLimit-Remaining` lower by one.

**UC-2 — Burst absorbed by the key bucket.**
- Precondition: the key has been idle for 10 s and holds 50 tokens.
- Steps: 1. the client sends 50 requests within one second. 2. the limiter removes 50 tokens.
- Outcome: 50 responses of `200`; `RateLimit-Remaining` reaches 0.

**UC-3 — Burst served by the shared pool.**
- Precondition: the key bucket is empty and the shared pool holds tokens.
- Steps: 1. the limiter finds no key token. 2. the limiter takes one shared token.
- Outcome: `200`; the shared draw is recorded against `shared_key_max`.

**UC-4 — Shared pool empty.**
- Precondition: the key bucket is empty and the shared pool is empty.
- Steps: 1. the limiter finds no token in either bucket. 2. the limiter computes `Retry-After`.
- Outcome: `429` with `scope=shared`.

**UC-5 — Per-key concurrency cap reached.**
- Precondition: the key holds `key_conc` open requests.
- Steps: 1. the limiter fails to acquire a slot. 2. the limiter rejects the request.
- Outcome: `429` with `scope=concurrency` and `Retry-After: 1`.

**UC-6 — Gateway capacity cap reached.**
- Precondition: open backend requests equal `global_conc`.
- Steps: 1. the limiter fails to acquire a global slot. 2. the alert in R-41 arms.
- Outcome: `429` with `scope=capacity`.

**UC-7 — Throttled client retries.**
- Actor: client SDK.
- Steps: 1. the client reads `Retry-After`. 2. the client waits per R-28. 3. the client resends the request.
- Outcome: `200` once a token is available, or a surfaced error after 5 attempts.

**UC-8 — Operator raises a key's tier.**
- Actor: operator.
- Steps: 1. the operator sets the key to `high` in the control plane. 2. instances refresh the tier cache.
- Outcome: the new limit applies on every instance within `config_propagation`; the change is recorded per R-34.

**UC-9 — Counter store unreachable.**
- Steps: 1. the limiter's store call fails. 2. the limiter admits the request. 3. the limiter increments the degraded counter. 4. each instance applies the degraded per-instance concurrency cap.
- Outcome: `200`; the alert in R-40 fires above 1 %.

**UC-10 — Operator reviews consumption.**
- Actor: operator, after a latency alert.
- Steps: 1. the operator opens the dashboard from R-38. 2. the operator reads the top keys by throttle count.
- Outcome: the key driving the load is named without a log query.

## 9. Acceptance criteria

**AC-1** — 5 req/s for 60 s on a `default` key → every response is `200`.
`; fails when the refill rate is set below 5 req/s`

**AC-2** — 60 requests in one second on an idle `default` key, shared pool empty → 50 return `200` and 10 return `429` with `scope=key`.
`; fails when burst_tokens is raised above 50`

**AC-3** — 60 requests in one second on an idle `default` key, shared pool full → 60 return `200`.
`; fails when the shared pool lookup is removed`

**AC-4** — one key requesting 400 shared tokens within 10 s → at most 200 are granted.
`; fails when the shared_key_max check is removed`

**AC-5** — key A holds its full shared-pool share → key B still receives 5 req/s.
`; fails when the shared_key_max check is removed`

**AC-6** — 11 concurrent requests on a `default` key → the eleventh returns `429` with `scope=concurrency`.
`; fails when key_conc is raised above 10`

**AC-7** — 10 clients disconnect mid-request → the key's slot count returns to 0 within `slot_ttl`.
`; fails when the release path skips the disconnect case`

**AC-8** — counter store unreachable → requests return `200` and the degraded counter rises.
`; fails when the store error path returns 429`

**AC-9** — one key sends 200 concurrent requests for 5 min → the backend reports zero pool timeouts, and pool wait time for other keys stays under 50 ms.
`; fails when the global_conc cap is removed`

**AC-10** — tier change in the control plane → every instance applies the new limit within 60 s.
`; fails when the tier cache TTL exceeds 30 s`

**AC-11** — any `429` → the body is an RFC 9457 problem detail with a `scope` member, and `Retry-After` is an integer of at least 1.
`; fails when Retry-After is emitted as an HTTP-date`

**AC-12** — 2000 req/s with the limiter enabled against the same load with it disabled → added p99 latency is at most 3 ms.
`; fails when the decision makes more than one counter-store round trip`

**AC-13** — shadow mode on, request above quota → the response is `200` and the log records `decision=would_throttle`.
`; fails when shadow mode rejects a request`

**AC-14** — the API reference states the `429` semantics, the retry delay formula and the attempt limit. Documentation check, no mutation clause.

**AC-15** — the decision counter carries labels `tier`, `scope`, `outcome`.
`; fails when the key identifier is added as a label`

## 10. Risks

| id | risk | severity |
| :--- | :--- | :--- |
| RISK-1 | Sum of granted quotas exceeds `pool_capacity` → pool timeouts replace `429` (detected by AC-9) | `Major` |
| RISK-2 | Counter store outage with fail-open → per-key rate is unbounded until recovery (detected by R-40) | `Major` |
| RISK-3 | Concurrency slot leaks on disconnect → the key is throttled until the TTL expires (detected by AC-7) | `Critical` |
| RISK-4 | Clients retry without jitter → retry traffic arrives synchronised after `Retry-After` (detected by AC-9 and R-38) | `Major` |
| RISK-5 | One key drains the shared pool → other keys fall back to sustained rate (detected by AC-4, AC-5) | `Major` |
| RISK-6 | Autoscaling raises instance count → the degraded per-instance cap admits more concurrency than `key_conc` (detected by AC-9 under a store outage) | `Major` |
| RISK-7 | Key identifier used as a metric label → time-series count grows with the key population (detected by AC-15) | `Minor` |
| RISK-8 | Shadow data collected outside a peak period → tier values are set below real demand (detected by the review in R-44) | `Major` |

## 11. Decisions

**D-1**, 2026-08-05, api-platform: per-key limits use a token bucket held in the counter store. Rejected: fixed-window counters — a fixed window admits twice the quota across a window boundary.

**D-2**, 2026-08-05, api-platform: one shared burst pool serves every tier. Rejected: one pool per tier — it adds two more parameters that no measurement supports.

**D-3**, 2026-08-05, api-platform: the per-key concurrency cap is counted in the counter store. Rejected: process-local counting only — with 6 instances a global cap of 10 becomes a per-instance cap of 2, and a client routed to one instance is rejected at 3 concurrent requests.

**D-4**, 2026-08-05, sre: on counter-store failure the limiter admits the request and records a degraded decision. Rejected: reject on failure — a store outage would return `429` to 100 % of requests.

**D-5**, 2026-08-05, api-platform: all four throttle scopes return `429`. Rejected: `503` for the concurrency and capacity scopes — the platform returns `503` during deploy drain, and clients could not distinguish the two conditions.

**D-6**, 2026-08-05, api-platform: responses carry `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`. Rejected: the structured `RateLimit` field from `draft-ietf-httpapi-ratelimit-headers` — its syntax changed between draft revisions and no client SDK reads it today. Revisit under Q-6.

**D-7**, 2026-08-05, api-platform: enforcement starts after 7 days of shadow mode. Rejected: immediate enforcement — no tier value in §6 has a measurement behind it.

**D-8**, 2026-08-05, sre: the limiter applies to authenticated requests only. Rejected: per-IP limiting in the gateway — it duplicates a control the edge provider already runs.

**D-9**, 2026-08-05, api-platform: every request costs one token, on every endpoint. Rejected: per-endpoint weights — no per-endpoint cost measurement exists, so the weights would be set by guess.

## 12. Open questions

**Q-1** — What is the production pool size and the mean connection hold time? Blocks: A-1, A-2 and every number derived from them. Owner: sre.

**Q-2** — What is the gateway instance count under autoscaling, at minimum and maximum? Blocks: A-3, A-4, R-17, RISK-6. Owner: sre.

**Q-3** — What per-key request rate and concurrency does the shadow period measure at p99? Blocks: every tier value in §6.1. Owner: api-platform.

**Q-4** — Which keys are assigned the `high` tier at launch? Blocks: the launch configuration and UC-8. Owner: product.

**Q-5** — Does a `429` count against the contractual availability commitment? Blocks: the published SLA text and R-30. Owner: product.

**Q-6** — When does the `RateLimit` structured field reach RFC status? Blocks: the revisit of D-6. Owner: api-platform.

**Q-7** — Do internal service calls reach the backend through the public gateway with an API key? Blocks: the scope boundary of D-8. Owner: sre.

**Q-8** — Is the quota owned by the API key or by the account that holds several keys? Blocks: R-3 and the control plane schema. Owner: product.

**Q-9** — Which two incident records document the pool exhaustion? Blocks: the citation in §1. Owner: sre.