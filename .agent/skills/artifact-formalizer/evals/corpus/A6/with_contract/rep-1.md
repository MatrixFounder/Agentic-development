# Development plan — split one build into `web` and `worker` over `shared-lib`

Status: draft for approval. Date: 2026-08-05.

## 1. Goal

Split the build into two artifacts so that each deploys independently.

## 2. Definitions

- `monolith` is the current deployable artifact that contains web and batch code.
- `shared-lib` is a versioned package that contains modules imported by both sides.
- `web` is a deployable artifact that serves HTTP requests.
- `worker` is a deployable artifact that runs batch jobs.
- A `stage` is a group of steps that ends at one gate.
- A `gate` is the verification set that a stage passes before the next stage starts.
- `M-shared`, `M-web`, `M-worker`, `M-conflict` are module lists produced in S1.

## 3. Scope

In scope: module inventory, `shared-lib` extraction, package publication, build split, deploy split, replica-scaling split, monolith pipeline removal.

Out of scope: behaviour changes to batch jobs, database schema changes, queue technology changes, HTTP route ownership, registry provisioning (platform owner carries these).

## 4. Severity vocabulary

| Value | Meaning | Effect on the stage |
| :--- | :--- | :--- |
| `blocker` | a gate verification reported a failure | stage does not close; fix or revert |
| `warn` | a recorded deviation with a named owner | stage closes; item enters the follow-up list |
| `note` | an observation with no obligation | none |

## 5. Ordering rule

**OR-1 (the ordering rule).** A step runs only after every input it consumes has passed its gate.

**Why.** `shared-lib` is the input of both artifact builds ⇒ the extraction precedes both builds. A gate that has not run produces no evidence ⇒ a consumer of that output cannot be checked.

Three clauses follow from OR-1 and are checked separately.

- **OR-2.** `shared-lib` reaches a published version before either artifact is built from it.
- **OR-3.** The monolith build target stays buildable until the S5 gate reports `pass`.
- **OR-4.** Each stage records its revert steps before its first step runs.

Prohibitions:

- **P-1.** A stage must not start while the previous gate holds a `blocker` finding. The violation shows in the gate log for the previous stage.
- **P-2.** `shared-lib` must not import a `M-web` or `M-worker` module. The violation shows in the import graph of `shared-lib`.
- **P-3.** `web` and `worker` must not import each other. The violation shows in the resolved dependency list of each artifact.
- **P-4.** A stage must not hand partial output to the next stage. The violation shows as a stage closed with an unrun verification id.

## 6. Stages

### S0 — Baseline

Steps.

1. Tag the current commit `baseline-monolith`. Postcondition: the tag resolves to one commit.
2. Record the monolith build command and output path. Postcondition: `docs/baseline.md` lists both.
3. Record deploy duration and replica counts. Postcondition: both values carry today's date.
4. Record batch queue depth and job latency for one full day. Postcondition: a range is stored.
5. Run the full test suite on the tag. Postcondition: the run reports zero failures.
6. Store the artifact checksum. Postcondition: the checksum file names the tag.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S0.1 | `baseline-monolith` → resolves to one commit | documentation check |
| V-S0.2 | test suite on the tag → zero failures | fails on a commit with a seeded defect |
| V-S0.3 | `docs/baseline.md` → lists command, path, replicas, queue range | documentation check |

Revert. S0 changes no build input. Revert deletes the record files and the tag.

### S1 — Boundary inventory

Steps.

1. Generate the import graph of the monolith. Postcondition: the graph file covers every source module.
2. List modules reachable from both entrypoints. Postcondition: `M-shared` exists.
3. List modules reachable from one entrypoint. Postcondition: `M-web` and `M-worker` exist.
4. Mark `M-shared` entries that import a one-side module. Postcondition: `M-conflict` exists.
5. Assign each `M-conflict` entry one of: move, duplicate, invert. Postcondition: each entry has an assignment and an owner.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S1.1 | union of the three lists → equals the monolith module set | fails when one module is dropped |
| V-S1.2 | `M-conflict` → every entry carries one assignment | documentation check |
| V-S1.3 | `M-shared` → every entry has an importer on each side | fails when a one-side module is added |

Revert. Delete the four lists. No build input changed.

### S2 — In-place extraction

The monolith stays one artifact through this stage.

Steps.

1. Create the `shared-lib` package inside the repository. Postcondition: a package manifest exists.
2. Move `M-shared` modules into `shared-lib` under unchanged public names. Postcondition: monolith imports resolve through `shared-lib`.
3. Apply the `M-conflict` assignments from S1. Postcondition: `shared-lib` imports no one-side module.
4. Declare `shared-lib` as a path dependency of the monolith. Postcondition: the build resolves it from the working tree.
5. Build the monolith. Postcondition: the build exits 0 and produces one artifact.
6. Run the full test suite. Postcondition: the run reports zero failures.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S2.1 | `shared-lib` import graph → no `M-web` or `M-worker` entry | fails when a worker import is added |
| V-S2.2 | monolith build → exits 0, one artifact | fails when a moved module keeps its old path |
| V-S2.3 | test suite → zero failures | fails when a moved module's public name changes |
| V-S2.4 | artifact count → equals 1 | fails when a second target is defined |

Revert.

1. Revert the S2 merge commit on the default branch. Postcondition: the tree matches the `baseline-monolith` layout.
2. Rebuild the monolith. Postcondition: the build exits 0.
3. Run the test suite. Postcondition: the run reports zero failures.
4. Redeploy the rebuilt artifact. Postcondition: one artifact serves HTTP and batch jobs.

### S3 — Publish `shared-lib` as a versioned package

Steps.

1. Set the `shared-lib` version to `0.1.0`. Postcondition: the manifest carries an exact version.
2. Publish `0.1.0` to the internal registry. Postcondition: the registry serves the version.
3. Replace the monolith path dependency with the exact pin `0.1.0`. Postcondition: no path dependency remains.
4. Build the monolith from an empty dependency cache. Postcondition: the build resolves `0.1.0` from the registry.
5. Run the full test suite. Postcondition: the run reports zero failures.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S3.1 | clean-cache build → resolves exactly `shared-lib 0.1.0` | fails when the pin is a range |
| V-S3.2 | republish of `0.1.0` → registry rejects the upload | fails when the registry allows overwrite |
| V-S3.3 | test suite → zero failures | fails when the pin names a missing version |

Revert.

1. Pin the monolith back to the path dependency. Postcondition: the build resolves from the working tree.
2. Rebuild and run the test suite. Postcondition: the run reports zero failures.
3. Leave `0.1.0` published. Postcondition: registry state is unchanged.

**Why.** A consumer that already resolved `0.1.0` keeps resolving it ⇒ removal of the version breaks that consumer's build.

### S4 — Two build targets

Steps.

1. Add the build target `web` with the HTTP entrypoint. Postcondition: the target produces one artifact.
2. Add the build target `worker` with the batch entrypoint. Postcondition: the target produces one artifact.
3. Point both targets at the `shared-lib` pin from S3. Postcondition: both lock files name `0.1.0`.
4. Exclude the batch entrypoint from `web` and the HTTP entrypoint from `worker`. Postcondition: neither artifact contains both entrypoints.
5. Keep the monolith target in the build configuration. Postcondition: three targets build in one run.
6. Start both new artifacts in a test environment. Postcondition: each reports ready.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S4.1 | file list of `web` → no batch entrypoint | fails when the batch entrypoint is added back |
| V-S4.2 | file list of `worker` → no HTTP entrypoint | fails when the HTTP entrypoint is added back |
| V-S4.3 | both artifacts started → each reports ready | fails when the `shared-lib` pin names a missing version |
| V-S4.4 | monolith target → builds and produces one artifact | fails when the target is deleted |
| V-S4.5 | lock files of both targets → name the same `shared-lib` version | fails when one target is repinned |

Revert.

1. Delete the `web` and `worker` targets. Postcondition: the build configuration lists one target.
2. Rebuild the monolith. Postcondition: the build exits 0.
3. Leave the deployment untouched. Postcondition: the monolith continues to serve.

**Why.** S4 publishes no deployment ⇒ its revert changes build configuration only.

### S5 — Independent deploy and scaling

Steps.

1. Deploy `web` alongside the running monolith. Postcondition: `web` instances report ready.
2. Move the HTTP route to `web`. Postcondition: the monolith receives no HTTP request.
3. Scale the monolith to zero replicas. Postcondition: no monolith instance consumes the queue.
4. Deploy `worker` with its own replica setting. Postcondition: `worker` instances consume the queue.
5. Record the elapsed time between steps 3 and 4. Postcondition: the value is stored with the queue depth.
6. Raise then lower the `worker` replica count. Postcondition: `web` instance ids are unchanged.
7. Deploy a worker-only commit. Postcondition: the `web` revision id is unchanged.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S5.1 | worker-only commit deployed → `web` revision id unchanged | fails when one deploy job covers both targets |
| V-S5.2 | `worker` replica change → `web` instance ids unchanged | fails when a shared restart policy is applied |
| V-S5.3 | queue depth one hour after step 4 → inside the S0 range | fails when `worker` consumes no job |
| V-S5.4 | job completion count for one hour → no duplicate job id | fails when the monolith runs during step 4 |
| V-S5.5 | HTTP error rate for one hour → inside the S0 range | fails when `web` starts without the `shared-lib` pin |

Revert.

1. Scale `worker` to zero replicas. Postcondition: no `worker` instance consumes the queue.
2. Deploy the monolith artifact from the retained S4 target. Postcondition: monolith instances report ready.
3. Move the HTTP route to the monolith deployment. Postcondition: `web` receives no HTTP request.
4. Scale `web` to zero replicas. Postcondition: only the monolith runs.
5. Record the failing verification id with severity `blocker`. Postcondition: the gate log names the id.

**Why.** Two queue consumers run the same job twice ⇒ `worker` stops before the monolith starts.

### S6 — Decommission the monolith pipeline

S6 starts only after the S5 gate reports `pass` on every verification id.

Steps.

1. Delete the monolith build target. Postcondition: the build configuration lists two targets.
2. Delete the monolith deploy job. Postcondition: no deploy job names the monolith.
3. Record the revert path from `baseline-monolith` in `docs/baseline.md`. Postcondition: the file names the tag and the build command.
4. Rebuild the monolith from the tag in a scratch environment. Postcondition: the build produces a runnable artifact.

Verification.

| Id | Input → asserted outcome | Mutation |
| :--- | :--- | :--- |
| V-S6.1 | build configuration → exactly two targets | fails when a third target is added |
| V-S6.2 | deploy configuration searched for the monolith name → zero matches | fails when the job is restored |
| V-S6.3 | build from `baseline-monolith` in a scratch environment → runnable artifact | fails when the tag is deleted |

Revert. Revert after S6 rebuilds the monolith from `baseline-monolith`. That tree excludes every commit merged after S0. S6 is the last stage with a cheap revert path; its gate is therefore the decision point.

## 7. Stage gate summary

| Stage | Output | Gate ids | Revert cost |
| :--- | :--- | :--- | :--- |
| S0 | baseline record, tag | V-S0.1–V-S0.3 | delete records |
| S1 | four module lists | V-S1.1–V-S1.3 | delete lists |
| S2 | `shared-lib` in repository | V-S2.1–V-S2.4 | revert one merge commit |
| S3 | `shared-lib 0.1.0` published | V-S3.1–V-S3.3 | repin to path dependency |
| S4 | three build targets | V-S4.1–V-S4.5 | delete two targets |
| S5 | two deployments, split scaling | V-S5.1–V-S5.5 | redeploy monolith from S4 target |
| S6 | monolith pipeline removed | V-S6.1–V-S6.3 | rebuild from `baseline-monolith` |

## 8. Risks

- **R-1** — `shared-lib` retains a one-side import → `web` ships batch code (detected by V-S2.1).
- **R-2** — monolith and `worker` consume the queue together → a job runs twice (detected by V-S5.4).
- **R-3** — the dependency is pinned as a range → the two artifacts build against different library code (detected by V-S3.1 and V-S4.5).
- **R-4** — the monolith target is deleted before the S5 gate → revert requires a rebuild from the tag (detected by V-S4.4).
- **R-5** — the S5 step 3–4 pause runs long → queue depth exceeds the S0 range (detected by V-S5.3).
- **R-6** — a moved module changes its public name → an importer fails to resolve (detected by V-S2.3).
- **R-7** — the registry accepts a republished version → two builds resolve different code under one version (detected by V-S3.2).

## 9. Decisions

- **D-1, 2026-08-05, build owner:** extract `shared-lib` before splitting the artifacts. Rejected: split first and extract later — each artifact then carries a private copy, and no verification compares the copies.
- **D-2, 2026-08-05, build owner:** both artifacts consume `shared-lib` by exact version pin. Rejected: a version range — V-S4.5 cannot assert one resolved version.
- **D-3, 2026-08-05, platform owner:** the monolith target stays buildable until the S5 gate passes. Rejected: deletion at S4 — revert then costs a rebuild from `baseline-monolith`.
- **D-4, 2026-08-05, platform owner:** a published version is never deleted; revert repins the consumer. Rejected: unpublish — a consumer with a cached resolution keeps the deleted version.
- **D-5, 2026-08-05, batch owner:** `worker` starts only after the monolith reaches zero replicas. Rejected: overlap — V-S5.4 cannot separate duplicate jobs from retries.

## 10. Derived numbers

- Deployable artifacts after S5: `2 = web + worker`; measured 1 at S0; applied as an exact count.
- Build targets during S4 and S5: `3 = web + worker + monolith`; measured 1 at S0; applied as a ceiling, falling to 2 at S6.
- `shared-lib` versions consumed per build: `1`; applied as a ceiling; asserted by V-S4.5.

## 11. Open questions

- **OQ-1** — is the monolith build reproducible byte-for-byte? Blocks: whether S2 verification compares checksums against V-S0.3. Owner: build owner.
- **OQ-2** — what batch pause is acceptable between S5 steps 3 and 4? Blocks: the S5 step order and the V-S5.3 threshold. Owner: batch owner.
- **OQ-3** — does the target registry reject republished versions? Blocks: V-S3.2. Owner: platform owner.
- **OQ-4** — does any batch job require exactly-once processing? Blocks: the S5 revert step order. Owner: batch owner.
- **OQ-5** — who approves `shared-lib` version releases after S6? Blocks: closing S6. Owner: engineering manager.
- **OQ-6** — do `web` and `worker` share one deploy pipeline definition today? Blocks: V-S5.1. Owner: platform owner.