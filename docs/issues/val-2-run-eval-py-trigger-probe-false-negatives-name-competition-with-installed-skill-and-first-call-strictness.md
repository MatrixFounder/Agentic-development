---
id: VAL-2
type: known-issue
status: open
opened_at: 2026-07-13
category: validation
severity: SEV-3
slug: val-2-run-eval-py-trigger-probe-false-negatives-name-competition-with-installed-skill-and-first-call-strictness
component: skill-creator
fingerprint: 68607ca1c9e4aca2
finding_ref: fnd-20260713-220152-68607ca1
---

# VAL-2 — run_eval.py trigger probe false-negatives: name competition with installed skill and first-call strictness

**Symptom.** `run_eval.py` (skill-creator) reported 0 triggers across 69 runs for a description whose verbatim trigger phrase fires instantly when probed manually. Two mechanisms: (1) the probe registers a uuid-suffixed clone (`<skill>-skill-<uuid8>`) — when the real skill is already installed in the repo, the model rationally invokes the canonical name and the probe scores "not triggered"; (2) the detector returns False unless the FIRST tool call is Skill/Read naming the probe — in a neutral repo the model's natural first move (look around via Bash) also scores "not triggered". Negative queries then pass vacuously, so the summary looks half-plausible instead of obviously broken.

**Reproduction.**

```sh
cd "$(git rev-parse --show-toplevel)"
cat > /tmp/probe_set.json <<'JSON'
[{"query": "собери фидбек по прогону — /full упал на security-критике", "should_trigger": true}]
JSON
python3 .agent/skills/skill-creator/scripts/run_eval.py \
  --eval-set /tmp/probe_set.json --skill-path .agent/skills/run-feedback \
  --num-workers 1 --timeout 60 --runs-per-query 2 --model claude-opus-4-8 --verbose
# observed: 0/2 triggers. Manual claude -p with the same phrase invokes Skill(run-feedback) as its FIRST tool call.
```

**Workaround.** Measure trigger accuracy only for skills NOT yet registered in the probing repo, and treat 0-trigger-everywhere results as instrument failure, never as description failure.

**Fix path.** In `run_eval.py`: (a) when the skill under test is already installed, count an invocation of the REAL skill name as a trigger (detect both names); (b) relax first-call strictness — scan the first N tool calls (or the whole turn) for a Skill/Read of either name instead of failing on the first unrelated tool call. `run_loop.py` inherits both fixes via `run_eval.run_eval`.

**Related.** finding_ref: fnd-20260713-220152-68607ca1 · sibling gate defect [VAL-1](val-1-validate-skill-py-passes-frontmatter-that-strict-yaml-parsers-reject-unquoted-colon-in-description.md) (validator blind spot; same "gate lies green" class).

**Do-not.** Do not "fix" by deleting the CLAUDECODE-env guard removal or by widening detection to ANY Skill call — near-miss negative queries legitimately trigger OTHER skills and must still count as non-triggers for this one.
