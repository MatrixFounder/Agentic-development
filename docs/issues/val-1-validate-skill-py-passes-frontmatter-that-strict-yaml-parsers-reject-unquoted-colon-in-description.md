---
id: VAL-1
type: known-issue
status: fixed
opened_at: 2026-07-13
resolved_at: 2026-07-13
resolved_by: heal-issues run 2026-07-13 (branch fix/val-1-validator-strict-yaml)
category: validation
severity: SEV-4
slug: val-1-validate-skill-py-passes-frontmatter-that-strict-yaml-parsers-reject-unquoted-colon-in-description
component: skill-creator
fingerprint: f15a6a3f1351475f
auto_fixable: true
finding_ref: fnd-20260713-134248-f15a6a3f
---

# VAL-1 — validate_skill.py passes frontmatter that strict YAML parsers reject (unquoted colon in description)

> Discovered when the shipped `run-feedback` SKILL.md rendered "Failed to parse frontmatter:
> Nested mappings are not allowed in compact mappings" in Obsidian/IDE preview — its
> description carried an unquoted `Triggers: "..."` clause. The file had passed
> `validate_skill.py`. The instance was fixed (quoted, commit `0518fe1`) and a one-off strict
> sweep of all 91 framework + 21 Universal-skills frontmatters came back clean — but the GATE
> is still blind, so the class will recur with the next colon-bearing description.

**Symptom.** `validate_skill.py` parses frontmatter with a lenient hand-rolled reader: a
`description:` (or any value) containing `: ` as a plain scalar validates green, while strict
YAML 1.1/1.2 parsers (Obsidian preview, VSCode markdown preview, js-yaml, PyYAML) reject the
whole frontmatter — the skill card renders as an error for every preview consumer.

**Reproduction.**

```sh
cd "$(git rev-parse --show-toplevel)"
T=$(mktemp -d)
cp -RL .agent/skills/run-feedback "$T/run-feedback"
sed -i '' '3s|.*|description: Use when previewing breaks: strict YAML parsers reject this "unquoted" colon scalar.|' "$T/run-feedback/SKILL.md"
! python3 .agent/skills/skill-creator/scripts/validate_skill.py "$T/run-feedback"
```

(macOS `sed -i ''`; on Linux use `sed -i`.) Red today: the validator exits 0 on the broken
frontmatter, so the negated call exits 1. Green after the fix: the validator must FAIL it.

**Workaround.** Quote any colon-bearing description manually; sweep with
`python3 -c "import yaml, ..."` over `*/SKILL.md` (the one-off sweep script from commit
`0518fe1`'s verification).

**Fix path.** In `validate_skill.py`'s frontmatter step: `try: import yaml` — when PyYAML is
importable, `yaml.safe_load` the frontmatter block and FAIL with the parser message on
`YAMLError`; when PyYAML is absent, fall back to a heuristic (flag unquoted values that
contain `: `) as a WARNING. Add a regression test with a colon-bearing description fixture.

**Related.** Commit `0518fe1` (the fixed instance + sweep); `run-feedback` SKILL.md;
`System/Docs/skill-writing.md` (authoring guidance should mention quoting).

**Do-not.** Do not make PyYAML a hard dependency — the validator must stay runnable in a bare
stdlib environment (strict check is soft-optional, heuristic is the floor).

> **Resolution — 2026-07-13, `heal-issues` run (branch `fix/val-1-validator-strict-yaml`).**
> `validate_skill.py` gained `check_frontmatter_strict()`, wired into the frontmatter step
> ahead of `VanillaYamlParser`: with PyYAML importable it `safe_load`s the block and FAILS with
> the parser's own message; without PyYAML it falls back to `_heuristic_unquoted_colon_warnings()`,
> which only WARNS on plain scalars holding `': '` — PyYAML stays soft-optional per the Do-not.
> Regression test `scripts/tests/test_frontmatter_strict.py` (5 cases, incl. the reproduction at
> unit scope) also materializes the `scripts/tests/` directory the configured `skill-creator`
> unit gate had been pointing at while it did not exist.
> **Gates:** reproduction now green (validator exits 1 on the broken frontmatter, with the
> `mapping values are not allowed here` detail); `unittest discover` 5/5 OK; validator on
> `run-feedback` PASSED; strict sweep of all 45 framework `SKILL.md` frontmatters — 0 failures,
> so no existing skill regresses.
