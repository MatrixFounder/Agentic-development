---
id: VAL-2
type: known-issue
status: fixed
opened_at: 2026-07-13
category: validation
severity: SEV-3
slug: val-2-run-eval-py-trigger-probe-false-negatives-name-competition-with-installed-skill-and-first-call-strictness
component: skill-creator
fingerprint: 68607ca1c9e4aca2
finding_ref: fnd-20260713-220152-68607ca1
resolved_at: 2026-07-30
resolved_by: TASK 096
---

# VAL-2 — run_eval.py trigger probe false-negatives: name competition with installed skill and first-call strictness

> **✅ FIXED 2026-07-30 (TASK 096).** Both reported mechanisms, plus three the record
> does not name — found by reproducing it rather than reading it.
>
> **Verified live before any code changed.** A fake `claude` on PATH replaying canned
> stream-json reproduced every reported behaviour at zero token cost:
> `Skill(run-feedback)` → False, `Read(.../run-feedback/SKILL.md)` → False,
> `Bash` → then probe → False, unrelated skill → False (correctly).
>
> **Fix path (a) and (b) both taken, and the "Do-not" was the hard part.** Widening to
> the canonical name while leaving matching loose would have made precision WORSE: the
> old `clean_name in accumulated_json` test already scored
> `Skill(skill="brainstorming", args="…<clone>…")` as a trigger — a **different** skill
> counted, which is exactly what the Do-not forbids — and
> `Read("docs/backlog/rf-1-<clone>-notes.md")` too. The probing repo really does contain
> substring pairs (`wiki-query` ⊂ `wiki-query-synthesis`); `run-feedback` is a substring
> of nothing, which is why the original repro never exposed it. So the fix **widens and
> tightens together**: exact match against `{probe_clone, real_name}` after normalising
> `plugin:skill` / `apps/web:deploy` / `.md` forms, `Skill.skill` only (never `args`),
> and a `Read` counts only when it loads `SKILL.md` or the probe command file.
>
> **Three additional mechanisms, all fixed:**
> 1. `message_stop` fires once per assistant MESSAGE, not per turn — recorded from a real
>    stream (2 × `message_stop`, 1 × `result`). So a model that ran `Bash` in message 1 and
>    the skill in message 2, after the tool result, scored not-triggered. The scan now ends
>    only on `result`, EOF, timeout, or the tool budget.
> 2. The EOF path appended the final read to the buffer and then `break`ed out **before**
>    the parse loop, discarding every event in it.
> 3. A `thinking` block always precedes the tool call, so any detector keying on "the
>    first content block" is wrong.
>
> **First-call strictness** is now a budget (`MAX_TOOL_CALLS_SCANNED = 8`) rather than
> "the first call decides", with every non-Skill/Read tool NEUTRAL — not a trigger and not
> a reason to abort.
>
> **Instrument failure is now distinguishable from a real non-trigger.** The scan reports
> a reason (`matched` / `clean-no-trigger` / `budget-exhausted` / `timeout` /
> `child-error`), reports **which** name matched (`canonical_matches` per query, because a
> canonical hit may have been caused by the INSTALLED description rather than the
> candidate under test), and prints a loud warning when zero queries trigger across the
> whole set. Collapsing all of those into one `False` is precisely how "0/69" read as a
> description failure for three weeks.
>
> **A defect of my own, caught mid-fix:** the first version killed a child that was
> exiting cleanly and then classified it `child-error`, which made every negative pass for
> the wrong reason. Our kill is now distinguished from the child's own failure.
>
> **Verification:** `scripts/tests/test_trigger_detection.py` — 32 tests in two layers
> (pure helpers with no subprocess; 13 end-to-end scenarios against a fake `claude`,
> zero tokens, no API key). Three mutations confirm the guards bite: dropping the
> canonical name → 4 failures, substring-instead-of-exact → 5, `message_stop` terminating
> → 4. Suite 26 → 58.
>
> **Portability, raised during review:** `run_eval.py` is Claude-Code-only and was before
> this fix. The detector is now SPLIT along that line — `normalize_skill_ref`,
> `match_skill_ref`, `match_read_path`, `classify_tool_use` are vendor-neutral pure
> functions and only `TriggerScanner.feed` knows the wire format, so another harness needs
> one adapter plus one fixture, not a rewrite. Recorded as WI-10.

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
