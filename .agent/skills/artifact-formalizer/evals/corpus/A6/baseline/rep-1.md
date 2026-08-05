# Development Plan: Splitting the Combined Build into `web` and `workers` over a Shared `core` Library

## 1. Outcome

| Before | After |
|---|---|
| One build → one deployable artifact containing front end + batch workers | Three build units: `core` (library), `web` (deployable), `workers` (deployable) |
| Any change redeploys everything | A change to `web` redeploys `web` only; a change to `workers` redeploys `workers` only |
| Workers scale with the front end | Workers scale independently |

`core` is a **library**, not a deployable. It is consumed by version, never by source path.

## 2. Preconditions

- [ ] Current combined artifact builds reproducibly from a tagged commit.
- [ ] A package registry (or equivalent) exists that can host a versioned `core` artifact.
- [ ] The current deploy can be rolled back to the previous artifact version by operators without a rebuild.
- [ ] Existing test suite passes on the tagged baseline; its pass rate is recorded as the comparison baseline.

## 3. The Ordering Rule

> **`core` must be extracted, versioned, and published before either `web` or `workers` is built from it. No artifact may be split off while any code it shares with the other artifact still lives inside an artifact.**

Three constraints follow, and they fix the stage order:

1. **Extraction precedes split.** Splitting first would fork the shared code into two copies that immediately drift. Stage 2 (extract) therefore precedes Stage 3 (split) with no overlap.
2. **Dependency direction is one-way.** `web → core` and `workers → core`. `core` must not import from `web` or `workers`. Any code that would require a back-edge is not shared code — it stays in the artifact that needs it, duplicated if genuinely needed by both in different forms.
3. **Every stage ends deployable.** No stage may end with the system un-shippable. Until Stage 4 completes, the combined artifact remains the production deployable and remains buildable.

**Stage gate:** a stage is complete only when its verification passes *in production*, not only in CI. The next stage does not begin before that.

## 4. Stage Overview

| Stage | Produces | Production deployable at stage end |
|---|---|---|
| 0 | Baseline + rollback path | combined artifact (unchanged) |
| 1 | Boundary map, no code moved | combined artifact (unchanged) |
| 2 | `core` published; monolith consumes it | combined artifact (now depends on `core`) |
| 3 | `web` and `workers` built separately | combined artifact (still authoritative) |
| 4 | Two pipelines, two deploys | `web` + `workers` |
| 5 | Independent scaling; combined path removed | `web` + `workers` |

---

## Stage 0 — Baseline and Rollback Path

**Steps**

- [ ] Tag the current commit `pre-split-baseline`.
- [ ] Build the combined artifact from that tag; record its version, checksum, and build inputs.
- [ ] Record the full test result set (pass/fail per suite) as `baseline-tests`.
- [ ] Record production behavioural baselines: front-end p95 latency and error rate; worker job throughput, queue depth, and job failure rate — each over a full representative cycle (at minimum one weekday and one weekend day).
- [ ] Confirm with operators that redeploying the baseline artifact version is a one-command action, and rehearse it once in a non-production environment.

**Verification**

- [ ] The baseline artifact rebuilds from the tag to an identical checksum.
- [ ] The rehearsed rollback restored the prior version without a rebuild, and the environment was healthy afterwards.

**Revert:** nothing to revert; Stage 0 changes no shipped code.

---

## Stage 1 — Map the Boundary (no code moves)

**Steps**

- [ ] Enumerate every module in the build and classify each as `web-only`, `workers-only`, `shared`, or `undecided`.
- [ ] Generate the module dependency graph and mark every edge that crosses a classification boundary.
- [ ] For each `shared` module, list its consumers on both sides. A module with a consumer on only one side is not shared — reclassify it.
- [ ] Resolve every `undecided` module. Record the decision and its reason.
- [ ] Identify cycles that cross the boundary. For each, choose and record a break strategy: move the module wholly to one side, split it, or invert the dependency behind an interface owned by `core`.
- [ ] List shared non-code assets — config schemas, migrations, generated clients, fixtures — and assign each an owner.
- [ ] Publish the map for review; get sign-off from the owners of both the front end and the batch workers.

**Verification**

- [ ] Every module carries exactly one classification; the `undecided` set is empty.
- [ ] The graph restricted to `shared` modules is acyclic and has no edge pointing into `web-only` or `workers-only`.
- [ ] Each recorded cycle-break strategy names a specific module and a specific action.
- [ ] Sign-off recorded from both owners.

**Revert:** discard the map. No shipped artifact is affected. A failure here means the boundary is not yet understood — do not proceed to Stage 2 with an unresolved `undecided` set or an unbroken cycle.

---

## Stage 2 — Extract `core` (the gating stage)

Nothing in this stage changes what the combined artifact *does*. It changes only where the shared code lives.

**Steps**

- [ ] Create the `core` build unit with its own manifest, version, and test suite.
- [ ] Apply the cycle-break strategies from Stage 1 **first**, while the code is still in one place and refactoring is cheap.
- [ ] Move `shared` modules into `core` in dependency order — leaves first, so `core` compiles after each move.
- [ ] Move shared non-code assets into `core` per their assigned owner.
- [ ] Move the tests that cover the moved code into `core`'s suite.
- [ ] Replace in-tree references to the moved code with imports of `core`.
- [ ] Publish `core` version `1.0.0` to the registry.
- [ ] Change the combined build to consume `core` from the registry at a pinned version — not from a local path, not as a source include.
- [ ] Add a CI check that fails the build if `core` imports from `web` or `workers` code.

**Verification**

- [ ] `core` builds and its tests pass standalone, with no checkout of the rest of the repository.
- [ ] The combined artifact builds against published `core@1.0.0`.
- [ ] `baseline-tests` results are reproduced with no new failures.
- [ ] The combined artifact contains exactly one copy of each shared module — no vendored duplicate alongside the dependency.
- [ ] The import-direction CI check is active and fails on a deliberately introduced back-edge.
- [ ] The combined artifact is deployed to production and the Stage 0 behavioural baselines hold over a full representative cycle.

**Revert**

1. Redeploy the baseline artifact version (no rebuild).
2. Revert the commit range that switched the combined build to the `core` dependency; the build returns to in-tree shared code.
3. Leave `core@1.0.0` published and unreferenced — yanking it is unnecessary and breaks nothing.
4. Record which module or check failed. Re-entry to Stage 2 requires the Stage 1 map updated for that module.

---

## Stage 3 — Split the Build into Two Artifacts

The combined artifact remains the production deployable throughout this stage. The two new artifacts are built and validated but not yet serving.

**Steps**

- [ ] Create the `web` build unit: `web-only` modules plus a dependency on pinned `core`.
- [ ] Create the `workers` build unit: `workers-only` modules plus a dependency on pinned `core`.
- [ ] Give each artifact its own entry point, config surface, and health/readiness check.
- [ ] Split the runtime configuration: each artifact declares only the settings it reads. Settings both read come from `core`'s schema.
- [ ] Move each test suite to the build unit that owns the code it covers.
- [ ] Build both artifacts in CI on every commit, alongside the combined artifact.
- [ ] Deploy both artifacts to a staging environment and run the full test suite plus a worker job replay against them.

**Verification**

- [ ] Both artifacts build from a clean checkout against published `core`.
- [ ] `web` contains no `workers-only` module and `workers` contains no `web-only` module; verify by inspecting the built artifacts' contents, not the source tree.
- [ ] `core` appears in each artifact as a resolved dependency at the same pinned version.
- [ ] Union of the two artifacts' test suites covers everything `baseline-tests` covered; no test was dropped in the move.
- [ ] In staging, `web` serves traffic and `workers` drains a replayed job queue, each with the other's artifact absent from its own deployment.
- [ ] The combined artifact still builds and still deploys.

**Revert**

1. Stop building the two artifacts in CI; the combined artifact is untouched and continues to ship.
2. Revert the build-unit split commits. `core` and the Stage 2 dependency stay in place — Stage 3 failure does not invalidate Stage 2.
3. Re-entry point is Stage 3 step 1, with the misplaced modules reclassified in the Stage 1 map.

---

## Stage 4 — Split the Deployment

**Steps**

- [ ] Create a deployment pipeline per artifact, each with independent versioning and its own rollback target.
- [ ] Deploy `workers` first, alongside the running combined artifact, with the combined artifact's worker component disabled or drained.
- [ ] Confirm workers-side baselines hold, then deploy `web` and cut front-end traffic to it.
- [ ] Keep the combined artifact deployable and its last-known-good version pinned and reachable for the full soak period.
- [ ] Soak for one full representative cycle with both artifacts serving.

**Verification**

- [ ] A commit touching only `web` triggers a `web` deploy and no `workers` deploy — confirm from pipeline history, not from configuration intent.
- [ ] The same holds in reverse for `workers`.
- [ ] A `core` version bump requires an explicit dependency update in each consumer; neither picks it up automatically.
- [ ] Stage 0 behavioural baselines hold for both artifacts across the soak period.
- [ ] Each pipeline's rollback has been exercised once against the live environment.

**Revert**

1. Cut front-end traffic back to the combined artifact and redeploy its last-known-good version.
2. Re-enable the combined artifact's worker component; scale the standalone `workers` deployment to zero.
3. Leave both pipelines in place but disabled — they are correct build definitions even if the cutover failed.
4. Re-entry requires the specific cutover failure to be reproduced in staging first.

---

## Stage 5 — Independent Scaling and Decommission

This stage removes the rollback path. Do not begin it until Stage 4 has soaked without incident.

**Steps**

- [ ] Set an independent scaling policy for `workers` — driven by queue depth or job backlog, not by front-end traffic.
- [ ] Set an independent scaling policy for `web` — driven by request load.
- [ ] Verify each policy under load in staging before enabling it in production.
- [ ] Announce the decommission date for the combined artifact.
- [ ] After the announced date: remove the combined build definition, retire its pipeline, and delete the `web-only`/`workers-only` merge points from the repository.
- [ ] Archive the baseline artifact and its build inputs in cold storage per the retention policy.

**Verification**

- [ ] Load applied to workers alone scales `workers` and leaves `web` replica count unchanged; the reverse also holds.
- [ ] A full deploy cycle of each artifact completes with the combined pipeline removed.
- [ ] No build definition, script, or runbook still references the combined artifact — verify by searching the repository and the operations runbooks.

**Revert:** the combined artifact no longer exists as a rollback target. Reverting a bad change now means rolling back the affected artifact through its own pipeline, which Stage 4 verified. Rebuilding the combined artifact from the archive is a recovery project, not a revert — treat this stage as the point of no return.

---

## 5. Rollback Ladder

Each rung is independently reachable; failing at rung *n* does not force a return past rung *n−1*.

| Failure at | Fall back to | Rebuild required |
|---|---|---|
| Stage 5 | Roll back the affected artifact via its own pipeline | No |
| Stage 4 | Combined artifact, last-known-good version | No |
| Stage 3 | Combined artifact consuming `core` (Stage 2 state) | No |
| Stage 2 | Baseline artifact, in-tree shared code | No |

**Standing rule:** every stage before 5 keeps a deployable predecessor that requires no rebuild to restore. If a proposed step would break that property, split the step until it no longer does.