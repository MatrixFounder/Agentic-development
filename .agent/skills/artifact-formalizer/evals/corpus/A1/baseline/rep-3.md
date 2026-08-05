# TASK-RL-01 — Per-Key Rate Limiting for the Public HTTP API

| Field | Value |
|---|---|
| Status | Draft — for review |
| Date | 2026-08-05 |
| Component | Public HTTP API (ingress / auth middleware), shared counter store |
| Related incidents | Connection-pool exhaustion, 2 occurrences (see OQ-9 for exact refs) |

---

## 1. Problem

The public HTTP API applies no rate limiting. Every authenticated request is admitted and executed
to completion regardless of how many requests the calling key has in flight or has issued recently.

Three properties of current traffic make this untenable:

1. **Load is concentrated.** A small number of API keys account for most requests. Capacity planning
   based on aggregate averages does not describe what any single key can do to the system.
2. **Load is bursty.** Sustained-average headroom is not headroom during a burst. Provisioning for
   peak-of-peaks across all keys simultaneously is not economical.
3. **One client has twice exhausted the database connection pool.** In both incidents a single key
   held enough concurrent in-flight requests that all pool connections were checked out. The blast
   radius was *every* client, not the misbehaving one: unrelated keys received timeouts and 5xx.

The second point deserves emphasis because it shapes the design. **Connection-pool exhaustion is a
concurrency failure, not a request-rate failure.** A key issuing 5 requests per second, each holding
a connection for 20 seconds, sits at 100 concurrent checkouts while never breaching a 10 rps quota.
A request-rate limiter alone would not have prevented either incident. This specification therefore
requires two independent admission controls — a rate limit and a concurrency limit — and treats the
concurrency limit as the direct remediation for the incidents.

Secondary problems:

- Clients have no way to know they are near a limit, and no documented contract telling them what to
  do when refused. Without one, throttled clients retry immediately and tightly, converting a
  throttling event into a retry storm.
- Operations has no per-key visibility. Identifying the offending key during both incidents was
  manual and slow.

### Goals

- Bound the damage any single key can do to shared resources, especially the database connection pool.
- Preserve the ability of well-behaved clients to burst, by way of a per-key allowance plus a shared
  pool, rather than flat-lining everyone at a conservative constant.
- Publish a retry contract precise enough that a client can implement it correctly without support
  contact, and machine-readable enough that generated SDKs can honour it.
- Give operators per-key observability and a same-shift lever to raise, lower, or suspend a key's limits.

### Non-goals

Monetization, quota sales, and abuse *detection* (as opposed to abuse *containment*). See §8.

---

## 2. Requirements

Priority follows RFC 2119: **MUST** is required for release; **SHOULD** is expected unless there is a
recorded reason to omit it; **MAY** is optional.

### 2.1 Functional — admission control

| ID | Priority | Requirement |
|---|---|---|
| FR-1 | MUST | Every authenticated request is evaluated against a **per-key token bucket** with a sustained refill rate `R_key` (tokens/second) and a capacity `B_key` (tokens). A request consumes `w` tokens; if fewer than `w` tokens are available across all applicable buckets, the request is refused. |
| FR-2 | MUST | Request cost `w` is configurable per route, defaulting to `1`. Routes with known-heavy cost profiles MAY be assigned a higher weight without a code change. |
| FR-3 | MUST | A **shared burst pool** exists as a single global token bucket with rate `R_shared` and capacity `B_shared`. A key whose own bucket is empty may draw the shortfall from the shared pool. |
| FR-4 | MUST | A single key's draw from the shared pool is capped at `S_key` tokens per rolling window `W_s`. Without this cap the shared pool is simply a larger bucket for whichever key polls fastest, and it reproduces the incident. |
| FR-5 | MUST | The shared pool MUST NOT be drawn below a reserve fraction `F_reserve` of its capacity by any key already over its own sustained rate. The reserve is available only to keys within their sustained rate, so a key that is merely spiky is never starved by a key that is persistently over. |
| FR-6 | MUST | Every authenticated request is evaluated against a **per-key in-flight concurrency limit** `C_key`. A request that would exceed `C_key` is refused immediately; it is not queued. |
| FR-7 | MUST | A **global in-flight limit** `C_global` is enforced across all keys, sized so that worst-case simultaneous database checkouts remain strictly below the connection-pool size. See OQ-1 for the sizing input. |
| FR-8 | MUST | Concurrency slots are released on response completion **including** on client disconnect, timeout, and panic/unhandled-error paths. A leaked slot is permanently lost capacity. |
| FR-9 | MUST | Limits are resolved from a **tier** attached to the key (e.g. `default`, `partner`, `internal`), with optional per-key overrides that take precedence over the tier. |
| FR-10 | MUST | Tier definitions, per-key overrides, and the global kill switch are changeable **without a deploy** and take effect within `T_config` seconds across all instances. |
| FR-11 | MUST | A per-key **exemption** may be set with a mandatory expiry timestamp. Exemptions bypass FR-1/FR-3 but never bypass FR-6/FR-7 — the concurrency limit protects a shared, finite resource and has no legitimate bypass. |
| FR-12 | MUST | A **shadow (observe-only) mode** exists, per tier and per key, in which all decisions are computed, counted, and logged but no request is refused. |
| FR-13 | SHOULD | Requests that fail authentication (absent, malformed, unknown, or revoked key) are rate-limited by source IP before any key lookup. Otherwise the limiter itself is bypassable by simply not authenticating. |
| FR-14 | MAY | Limits MAY be applied at account granularity in addition to key granularity, for accounts holding many keys. Deferred — see OQ-5. |

### 2.2 Functional — client-facing contract

| ID | Priority | Requirement |
|---|---|---|
| FR-15 | MUST | A refused request returns HTTP **429 Too Many Requests**. |
| FR-16 | MUST | Every 429 carries a **`Retry-After`** header, integer seconds, ≥ 1, representing the earliest time at which the same request could succeed given current state. It is a lower bound and an estimate, not a promise. |
| FR-17 | MUST | Every response — throttled or not — to an authenticated request carries `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` describing the key's own bucket (FR-1). Shared-pool state is deliberately **not** exposed: it is a global quantity a client cannot act on, and publishing it invites racing for it. |
| FR-18 | MUST | The 429 body is JSON with a stable machine-readable discriminator: `error.type = "rate_limit_exceeded"` and an `error.code` distinguishing at minimum `per_key_rate`, `shared_pool_exhausted`, `concurrency_limit`, and `unauthenticated_rate`. The four have materially different client remedies. |
| FR-19 | MUST | The 429 body includes the `request_id` so a client can cite a specific refusal in a support request. |
| FR-20 | MUST | The published **retry contract** (§4) states: honour `Retry-After`; apply exponential backoff with full jitter on repeated refusals; cap total attempts; retry automatically only for idempotent requests or requests carrying an idempotency key. |
| FR-21 | MUST | 429 responses MUST NOT consume a token or a concurrency slot themselves, beyond the fixed cost of the limiter check. Charging for refusals makes a throttled client's recovery slower the harder it retries, which is punitive and hard to reason about. |
| FR-22 | SHOULD | The `Retry-After` value for a `concurrency_limit` refusal is short (1 s) — concurrency clears on the order of a request duration, not a refill window — while a `per_key_rate` refusal reports the true refill time. |

### 2.3 Non-functional

| ID | Priority | Requirement |
|---|---|---|
| NFR-1 | MUST | Added latency at p99 for the full admission check (rate + concurrency) ≤ **2 ms** at expected peak. |
| NFR-2 | MUST | The limiter is correct across all API instances — decisions use shared state, not per-instance counters. Per-instance counters divide the effective limit by an instance count that changes under autoscaling. |
| NFR-3 | MUST | If the shared counter store is unavailable, the API **fails open on the distributed rate limit** and **fails closed to a conservative local limit**: each instance falls back to an in-process limiter at `R_key / expected_instances` and continues enforcing FR-6/FR-7 locally, which need no shared state. Availability of the API is preferred over exactness of the quota; total loss of protection is not acceptable, because the incident this document exists to prevent could recur during the outage. |
| NFR-4 | MUST | Limiter state is ephemeral. Loss of the store resets buckets to full; it MUST NOT lose or corrupt any request data, and MUST NOT prevent the API from serving. |
| NFR-5 | MUST | Bucket updates are atomic — check-and-consume happens in one round trip, no read-modify-write race. |
| NFR-6 | SHOULD | Limiter overhead adds no more than one network round trip per request to the shared store. |
| NFR-7 | SHOULD | The design admits a future move to per-region shared pools without a client-visible contract change. |

### 2.4 Security

| ID | Priority | Requirement |
|---|---|---|
| SEC-1 | MUST | Raw API keys MUST NOT appear in limiter keys, logs, metrics labels, traces, or error bodies. Use the key's opaque ID, or a truncated salted hash where no ID exists. |
| SEC-2 | MUST | Limiter decisions MUST NOT leak the existence or validity of a key: an unknown key and a revoked key produce indistinguishable throttling behaviour. |
| SEC-3 | MUST | Metrics cardinality is bounded. Per-key metrics are emitted for the top-N keys plus an aggregate bucket, never one unbounded series per key seen. |
| SEC-4 | SHOULD | Client-supplied headers that could influence limiter identity (e.g. forwarded-for chains used by FR-13) are trusted only from the known ingress hop. |

### 2.5 Observability and operations

| ID | Priority | Requirement |
|---|---|---|
| OBS-1 | MUST | Counters for admitted, throttled-by-rate, throttled-by-shared-pool, and throttled-by-concurrency, dimensioned by tier and by top-N key. |
| OBS-2 | MUST | A gauge of current global in-flight requests and of database connections checked out, on the same dashboard, so the relationship in FR-7 is verifiable at a glance during an incident. |
| OBS-3 | MUST | An operator can answer "which key is causing this?" within **60 seconds** from a single dashboard, without ad-hoc log queries. |
| OBS-4 | MUST | Alert when any single key exceeds a configured share of global in-flight capacity, or when global in-flight exceeds `F_alert` of `C_global`. |
| OBS-5 | SHOULD | Alert when a key's throttle rate crosses a threshold for a sustained period — this is the signal that a legitimate client's limits are set wrong, distinct from OBS-4 which signals abuse. |
| OBS-6 | SHOULD | Shadow-mode counters are recorded separately from enforcement counters, so pre-enforcement analysis (UC-9) is a query, not an inference. |
| OBS-7 | MUST | A runbook documents: raising a key's limits, granting a timed exemption, and the global kill switch, each with the expected propagation delay from FR-10. |

---

## 3. Use cases

**UC-1 — Compliant client, steady traffic.**
A key issues requests below `R_key`. All are admitted. Each response carries `RateLimit-*` headers
showing remaining tokens. The client never sees a 429. *(FR-1, FR-17)*

**UC-2 — Compliant client, short burst.**
A batch job issues a burst above `R_key` but shorter than `B_key` tokens. The burst is fully absorbed
by the key's own bucket. `RateLimit-Remaining` falls toward zero and refills at `R_key`. No 429.
*(FR-1)*

**UC-3 — Large burst, absorbed by the shared pool.**
A key's own bucket is exhausted mid-burst while the shared pool has tokens above the reserve. The
shortfall is drawn from the shared pool, up to `S_key` per window. The client completes its burst
successfully. This is the case the shared allowance exists for: aggregate capacity is available, one
key temporarily needs more than its own share, and no one else is being harmed. *(FR-3, FR-4, FR-5)*

**UC-4 — Shared pool depleted.**
Several keys burst simultaneously and the shared pool falls to its reserve. A key over its sustained
rate is refused with `code: shared_pool_exhausted` and a `Retry-After` derived from the shared refill
rate. A key *within* its sustained rate is still served from the reserve. *(FR-3, FR-5, FR-15, FR-16)*

**UC-5 — Connection-pool protection (the incident case).**
A misbehaving client opens a large number of concurrent long-running requests. Its request *rate* may
be modest. On reaching `C_key` in-flight, further requests are refused immediately with
`code: concurrency_limit` and `Retry-After: 1`. Global in-flight stays below `C_global`; database
checkouts stay below pool size; **other keys are unaffected**. This is the acceptance-critical
scenario. *(FR-6, FR-7, FR-8, OBS-2)*

**UC-6 — Unauthenticated flood.**
A source floods the API with absent or invalid keys. Requests are refused by the IP limiter before
key lookup, so the flood consumes neither authentication work nor database connections. Valid and
invalid keys are refused identically. *(FR-13, SEC-2)*

**UC-7 — Shared counter store unavailable.**
The store becomes unreachable. Distributed rate limiting degrades to per-instance local limiting at a
divided rate; concurrency limiting continues unimpaired because it needs no shared state. The API
keeps serving. An alert fires. Quotas are approximate for the duration. *(NFR-3, NFR-4)*

**UC-8 — Operator raises a limit under pressure.**
A partner's legitimate migration job is being throttled. An operator applies a per-key override, or a
timed exemption with a mandatory expiry. It takes effect within `T_config` seconds with no deploy. The
exemption cannot lift the concurrency cap. *(FR-9, FR-10, FR-11, OBS-7)*

**UC-9 — Rollout in shadow mode.**
Limits are enabled in observe-only mode. For each candidate limit set, operators query how many
requests *would* have been refused, per key, and adjust before enforcing. Keys that would be heavily
affected are contacted before enforcement. *(FR-12, OBS-6)*

**UC-10 — Client recovers correctly from throttling.**
A client receives a 429 with `Retry-After: 3`. It waits at least 3 seconds, retries with jitter, and
succeeds. On repeated refusals it backs off exponentially and gives up after the documented attempt
cap rather than retrying indefinitely. Its retry traffic does not amplify the throttling. *(FR-16, FR-20)*

**UC-11 — Non-idempotent request is throttled.**
A `POST` without an idempotency key is refused with 429. The documented contract instructs the client
**not** to retry automatically unless it carries an idempotency key, since a 429 is a guaranteed
non-execution but an SDK cannot in general prove that for a request it retries after other failures.
*(FR-20)*

---

## 4. Retry contract (client-facing, to be published in the API documentation)

When a request is refused, the API responds:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3
RateLimit-Limit: 10
RateLimit-Remaining: 0
RateLimit-Reset: 3
Content-Type: application/json

{
  "error": {
    "type": "rate_limit_exceeded",
    "code": "per_key_rate",
    "message": "Request rate for this API key exceeded. Retry after 3 seconds.",
    "retry_after_ms": 2400,
    "request_id": "req_01J8ZK..."
  }
}
```

Client obligations:

1. **Never retry before `Retry-After` elapses.** It is a lower bound; retrying earlier is guaranteed
   to be refused and consumes limiter capacity for no benefit.
2. **Back off exponentially with full jitter** across successive refusals:
   `delay = random(0, min(cap, base × 2^attempt))`, with `base` = `Retry-After` (or 1 s if absent) and
   `cap` = 60 s. Full jitter, not fixed backoff — synchronised clients that all wake at
   `Retry-After` exactly will collide again on the next window.
3. **Cap attempts.** Give up after 3 retries and surface the failure. A client-wide retry budget
   (retries ≤ 10 % of requests) is strongly recommended so that a broad throttling event cannot turn
   into a self-inflicted retry storm.
4. **Retry automatically only** for `GET`, `HEAD`, `PUT`, `DELETE`, or requests carrying an
   `Idempotency-Key`. Other methods should surface the 429 to the caller (UC-11).
5. **Distinguish by `error.code`.** `concurrency_limit` means "you have too many requests open right
   now" — the remedy is to lower client concurrency, not to wait longer. `per_key_rate` means "slow
   down". `shared_pool_exhausted` is transient system-wide pressure and warrants the longest backoff.
6. **Use the `RateLimit-*` headers proactively.** Clients should throttle themselves as `Remaining`
   approaches zero rather than driving into a 429.
7. A 429 means the request was **not executed**. No side effect occurred.

---

## 5. Acceptance criteria

Each criterion is objectively verifiable. "Verified by" names the method.

| ID | Criterion | Verifies | Verified by |
|---|---|---|---|
| AC-1 | A key issuing traffic at exactly `R_key` for 10 minutes receives zero 429s. | FR-1 | Load test |
| AC-2 | A key issuing a burst of `B_key` requests from an idle bucket receives zero 429s; the immediately following request over the limit receives 429. | FR-1 | Integration test |
| AC-3 | With the shared pool full, a key exceeding its own bucket by up to `S_key` in window `W_s` is admitted; the request past `S_key` is refused with `code: shared_pool_exhausted`. | FR-3, FR-4 | Integration test |
| AC-4 | With the shared pool at its reserve, a key within its sustained rate is still admitted while a key over its sustained rate is refused. | FR-5 | Integration test |
| AC-5 | **A single key opening unbounded concurrent long-running requests never causes database checkouts to reach pool size; p99 latency and error rate for a concurrently running well-behaved key stay within their normal envelope for the whole test.** | FR-6, FR-7 | Load test reproducing the incident |
| AC-6 | After a test injecting client disconnects, request timeouts, and handler errors at ≥ 5 % of traffic, the measured in-flight gauge returns to zero when traffic stops. No slot leak. | FR-8 | Load test + gauge assertion |
| AC-7 | Changing a tier limit or per-key override takes effect on all instances within `T_config` seconds, with no deploy and no restart. | FR-10 | Manual, timed, recorded in the runbook |
| AC-8 | An exemption cannot raise or bypass `C_key` or `C_global`; an attempt to configure one is rejected. | FR-11 | Unit test |
| AC-9 | In shadow mode, a key driven far past its limits receives zero 429s while the would-have-throttled counter increments correspondingly. | FR-12, OBS-6 | Integration test |
| AC-10 | Requests with absent, malformed, and revoked keys are all refused by the IP limiter with byte-identical bodies and status. | FR-13, SEC-2 | Integration test |
| AC-11 | Every 429 in a full test run carries `Retry-After` ≥ 1, a recognised `error.code`, and a `request_id`. Asserted over the whole run, not a sample. | FR-16, FR-18, FR-19 | Integration test |
| AC-12 | Every 200 response to an authenticated request carries all three `RateLimit-*` headers, and `Remaining` is monotonically non-increasing within a refill window under serial traffic. | FR-17 | Integration test |
| AC-13 | Repeatedly retrying into a 429 does not extend the reported `Retry-After` beyond what the refill rate implies. | FR-21 | Integration test |
| AC-14 | p99 added latency of the admission check ≤ 2 ms at expected peak throughput. | NFR-1 | Load test with limiter-only span measurement |
| AC-15 | With the shared store killed mid-test, the API continues serving; the local fallback limiter and both concurrency limits remain in force; an alert fires; no 5xx attributable to the limiter. | NFR-3, NFR-4 | Chaos test |
| AC-16 | With N instances running, a key's observed admitted rate matches `R_key` within ±10 %, independent of N. | NFR-2 | Load test at two instance counts |
| AC-17 | No raw API key appears in any log line, metric label, trace attribute, or response body across a full test run. | SEC-1 | Automated scan of captured output |
| AC-18 | Metric series count attributable to the limiter stays bounded when the test issues traffic from 10 000 distinct keys. | SEC-3 | Load test + series count assertion |
| AC-19 | Starting from the alert, an operator identifies the offending key in ≤ 60 s using only the dashboard. | OBS-3 | Timed game-day exercise |
| AC-20 | The published documentation states the contract in §4 in full, including the `error.code` values and the non-execution guarantee. | FR-20 | Documentation review |

---

## 6. Decisions taken

| ID | Decision | Rationale | Rejected alternative |
|---|---|---|---|
| D-1 | **Token bucket** for rate limiting. | Expresses "sustained rate plus burst" as two independent parameters, which is exactly the traffic shape described. O(1) state per key. | Fixed window — permits a 2× spike across a window boundary. Sliding-window log — exact, but O(requests) memory per key, unaffordable for the heaviest keys, which are precisely the ones that matter. |
| D-2 | **A rate limit and a concurrency limit are both required**, and the concurrency limit is the primary remediation for the incidents. | The incidents were connection-pool exhaustion by concurrent long-held work. A requests-per-second limit does not bound in-flight work when latency varies; shipping only a rate limit would leave the stated failure reproducible. | Rate limiting alone — does not close the incident. Enlarging the connection pool — moves the wall without removing it, and the next resource to exhaust would be less visible. |
| D-3 | **Refuse, do not queue or delay.** | Queuing a throttled request holds server resources on behalf of a client that is already over its share, which is the failure mode inverted. Fast refusal returns control to the client, which is the only party that can actually shed load. | Leaky-bucket shaping with server-side delay. |
| D-4 | **Enforce at a single ingress layer** (auth middleware / gateway), not per downstream service. | One implementation, one contract, one place to reason about; key identity is already resolved there. | Per-service limiters — N inconsistent implementations and no global view. |
| D-5 | **Shared state in a fast central store with atomic check-and-consume** (single scripted round trip). | Satisfies NFR-2 and NFR-5 at NFR-1 latency. Rate-limit state is ephemeral (NFR-4), so durability is not required of it. | Per-instance counters — effective limit varies with autoscaling. Consensus-backed store — latency budget does not permit it. |
| D-6 | **Bounded fail-open**: on store unavailability, degrade to a conservative per-instance local limiter and keep concurrency limits fully enforced. | Full fail-open re-exposes the exact incident during an infrastructure outage. Full fail-closed converts a limiter dependency into a total API outage — a strictly worse failure than approximate quotas. | Either pure alternative. |
| D-7 | **429 for all throttling**, never 503. | 429 attributes the condition to the caller and is unambiguous for automated clients. 503 says "the server is unwell", which is untrue for a client that exceeded its own quota, and many client libraries retry 503 more aggressively than 429. | 503 for shared-pool and concurrency refusals. |
| D-8 | **`Retry-After` plus `RateLimit-Limit` / `-Remaining` / `-Reset`.** | The widest-deployed and best-understood combination; existing client libraries already handle it. The IETF `RateLimit`/`RateLimit-Policy` structured-field work is the eventual alignment target and can be added alongside, additively, without breaking the contract in §4. | Adopting the in-progress structured-field syntax alone — poorer client-library support today. Bare `X-RateLimit-*` with no `Retry-After` — leaves clients to compute retry timing themselves, and they get it wrong. |
| D-9 | **Shared-pool state is not exposed to clients.** | A client cannot act usefully on a global number, and publishing it encourages racing to claim it. `Retry-After` conveys everything the client needs. | Exposing shared-pool remaining tokens. |
| D-10 | **Per-key shared-pool draw cap and reserve floor** (FR-4, FR-5). | Without both, the shared pool is a bigger bucket for the fastest poller, which reproduces the concentration problem it was meant to relieve. | An unrestricted shared pool. |
| D-11 | **Limits keyed on API key, with tiers and per-key overrides**; account-level limits deferred. | Key is the identity the API already authenticates and the granularity at which abuse was observed. | Account-level in v1 — requires resolving account membership on the hot path for a case not yet demonstrated. |
| D-12 | **Exemptions are time-bounded and cannot lift concurrency caps** (FR-11). | Permanent exemptions become invisible permanent risk. The concurrency cap protects a finite shared resource; an exemption from it is an exemption from the whole point of this work. | Open-ended exemptions. |
| D-13 | **Mandatory shadow-mode phase before enforcement** (FR-12, §7). | Limits set from guesses will refuse legitimate traffic. Shadow mode converts the choice of numbers from a judgement call into a measurement. | Enforcing straight away with conservative numbers and adjusting on complaints. |
| D-14 | **Refused requests are not charged** (FR-21). | Charging for refusals means a client that retries hard recovers more slowly — behaviour that is hard to document, hard to debug from the client side, and punishes clients whose retry logic is merely naive. | Charging a token per refusal as an anti-hammering measure. |
| D-15 | **IP-based limiting for unauthenticated requests only** (FR-13). | Closes the trivial bypass, without applying IP limits to authenticated traffic where NAT and shared egress make IP a poor identity. | IP limits on all traffic. |

---

## 7. Rollout

1. **Instrument.** Ship in-flight and per-key metrics (OBS-1, OBS-2, OBS-3) first. Some value lands
   immediately: the next incident becomes diagnosable in seconds even before enforcement exists.
2. **Shadow.** Enable observe-only for all tiers (FR-12). Run at least one full traffic cycle,
   including the weekly peak, before choosing numbers.
3. **Set limits from measurement.** Derive `R_key`, `B_key`, `C_key` per tier from shadow data. Resolve
   OQ-1 through OQ-4 here.
4. **Notify.** Publish §4 and give affected clients notice before enforcement. Contact by name any key
   that shadow data shows would be materially throttled.
5. **Enforce concurrency first.** `C_key` and `C_global` (FR-6, FR-7) close the actual incident and
   should not wait on rate-limit tuning.
6. **Enforce rate limits**, internal and low-traffic tiers first, then broadly.
7. **Hold the kill switch** through the enforcement window, with the runbook (OBS-7) rehearsed.

---

## 8. Out of scope

| ID | Item | Note |
|---|---|---|
| OOS-1 | Billing, metered pricing, quota purchase, overage charges. | This is a stability control. Any commercial layer is separate work that may later consume these counters. |
| OOS-2 | Abuse *detection*, anomaly scoring, automated key suspension. | Containment only. Suspension stays a human decision. |
| OOS-3 | L3/L4 DDoS mitigation, WAF rules, bot detection. | Handled at the edge, upstream of this component. |
| OOS-4 | Adaptive or load-feedback-driven limits. | Static configured limits in v1; the configuration surface (FR-10) does not preclude it later. |
| OOS-5 | Per-user or per-sub-key limits below key granularity. | See D-11 and OQ-5. |
| OOS-6 | Protocols other than HTTP request/response — WebSocket, streaming, long-poll, gRPC. | Concurrency accounting for long-lived connections needs its own model. See OQ-7. |
| OOS-7 | API key issuance, rotation, and revocation. | Existing system; this work consumes key identity and tier, and does not change them. |
| OOS-8 | Response caching or other load-reduction measures. | Complementary, separately tracked. |
| OOS-9 | Resizing or reconfiguring the database connection pool. | `C_global` is sized *against* the pool as it exists (OQ-1). Changing the pool is separate work; if it happens, `C_global` must be re-derived. |
| OOS-10 | Client SDK changes implementing §4. | The contract is specified and documented here; SDK implementation is tracked separately per language. |
| OOS-11 | Contractual SLA or rate-limit commitments to existing customers. | Commercial, not technical. Flagged in OQ-6. |

---

## 9. Open questions

Ordered by how much they block. OQ-1 through OQ-4 must be resolved before enforcement (step 5 of §7);
the rest can be resolved in parallel.

| ID | Question | Blocks | Owner |
|---|---|---|---|
| OQ-1 | What is the database connection-pool size per instance and in aggregate, and how many connections can one request hold at once? `C_global` cannot be derived without both. Are there endpoints that check out more than one connection, or hold one across an external call? | FR-7, AC-5 | Backend |
| OQ-2 | What are the actual per-key rate and concurrency distributions? Required to set `R_key`, `B_key`, `C_key` per tier from data rather than from guesses. Answered by the shadow phase (§7 step 2). | FR-1, FR-6, FR-9 | Backend / Ops |
| OQ-3 | How should the shared pool be sized (`R_shared`, `B_shared`, `S_key`, `W_s`, `F_reserve`)? Sizing it too generously reproduces the current situation with extra steps; too tightly makes it decorative. | FR-3, FR-4, FR-5 | Backend |
| OQ-4 | What tiers exist, who assigns a key to one, and where does that assignment live? Does the key record already carry a suitable field, or is a schema change needed? | FR-9, FR-10 | Backend / Product |
| OQ-5 | Do any accounts hold multiple keys in a way that would let them multiply their effective quota by minting more? If so, FR-14 stops being optional. | FR-14, D-11 | Product |
| OQ-6 | Are there existing contractual commitments, explicit or implied by past behaviour, that constrain the limits we may impose on specific customers — and what notice period is owed? | §7 step 4, OOS-11 | Commercial |
| OQ-7 | Does the API expose long-poll, streaming, chunked, or otherwise long-lived responses? Under FR-6 these occupy a concurrency slot for their full lifetime, which may be minutes. If any exist, they need a separate accounting rule. | FR-6, OOS-6 | Backend |
| OQ-8 | Which shared store will back the limiter, is an instance already available in the request path, and what is its measured p99 round-trip latency from the API? NFR-1 depends on the answer. | NFR-1, D-5 | Infrastructure |
| OQ-9 | What are the exact references, timelines, and post-mortems for the two connection-pool incidents? Needed to build AC-5 as a faithful reproduction rather than an approximation. | AC-5 | Ops |
| OQ-10 | How is `T_config` propagation implemented — polling, push, or existing config mechanism — and what value is achievable? OBS-7 and AC-7 both quote it. | FR-10, AC-7 | Infrastructure |
| OQ-11 | Should `Retry-After` ever exceed some ceiling? A long value on a depleted shared pool is honest but may be read by clients as an outage. | FR-16, FR-22 | Backend / Docs |
| OQ-12 | Is there a lower-priority class of traffic (batch, analytics, replay) that should be shed before interactive traffic when the shared pool nears its reserve? Not required for v1, but it changes FR-5 if wanted early. | FR-5 | Product |

---

## 10. Traceability

| Requirement | Use cases | Acceptance criteria |
|---|---|---|
| FR-1, FR-2 | UC-1, UC-2 | AC-1, AC-2 |
| FR-3, FR-4, FR-5 | UC-3, UC-4 | AC-3, AC-4 |
| FR-6, FR-7, FR-8 | UC-5 | AC-5, AC-6 |
| FR-9, FR-10, FR-11 | UC-8 | AC-7, AC-8 |
| FR-12 | UC-9 | AC-9 |
| FR-13 | UC-6 | AC-10 |
| FR-15 – FR-19, FR-22 | UC-4, UC-5, UC-10 | AC-11, AC-12 |
| FR-20 | UC-10, UC-11 | AC-20 |
| FR-21 | UC-10 | AC-13 |
| NFR-1 | — | AC-14 |
| NFR-2 | — | AC-16 |
| NFR-3, NFR-4 | UC-7 | AC-15 |
| SEC-1, SEC-2, SEC-3 | UC-6 | AC-10, AC-17, AC-18 |
| OBS-1 – OBS-7 | UC-5, UC-8, UC-9 | AC-9, AC-19 |