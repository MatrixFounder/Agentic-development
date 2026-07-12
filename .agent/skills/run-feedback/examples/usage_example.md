# Example: capture → triage → file (one real defect, one duplicate, one noise)

Scenario: during a `/develop` run the transcript-fetcher gate failed twice with exit 7, and one
`curl` call died on a transient DNS error.

## 1. Collect (retro step, after claiming ownership)

```sh
RF="python3 .agent/skills/run-feedback/scripts/run_feedback.py"
$RF claim --run-id develop-task-042            # exit 0 → we own the retro
$RF collect --source workflow --kind gate-failure --component transcript-fetcher \
  --message "fetch.py exit 7: ffmpeg missing on HLS ASR path" \
  --command "scripts/.venv/bin/python scripts/fetch.py <url>" --exit-code 7 \
  --workflow develop --task-id task-042
$RF collect --source workflow --kind tool-error --component session \
  --message "curl: (6) could not resolve host example.com" --exit-code 6
```

## 2. Triage

```sh
$RF triage
```

```
| finding | src | kind | component | failure | ×N | message | dup candidates |
|---|---|---|---|---|---|---|---|
| fnd-…-a1b2c3d4 | workflow | gate-failure | transcript-fetcher | exit:7 | 2 | fetch.py exit 7: ffmpeg… | issue TF-X-3 (title overlap: ffmpeg, path) |
| fnd-…-9f8e7d6c | workflow | tool-error | session | exit:6 | 1 | curl: (6) could not resolve… | - |
```

Judgement: open `docs/issues/tf-x-3-….md` → it is about MacWhisper, NOT ffmpeg → not a dup, file
as defect. The curl failure is transient DNS → noise.

## 3. File

Author the body from `assets/templates/issue_body_template.md` (Symptom / **runnable fenced-sh
Reproduction** / Workaround / Fix path / Related / Do-not) into `/tmp/body.md`, then:

```sh
$RF file --finding fnd-…-a1b2c3d4 --as defect --title "ffmpeg gap not flow-blocking in doctor" \
  --category robustness --severity SEV-3 --auto-fixable --body-file /tmp/body.md --dry-run
# review the printed ID + index line, then re-run without --dry-run

$RF file --finding fnd-…-9f8e7d6c --as noise --reason "transient DNS, not reproducible"
$RF release --run-id develop-task-042
```

Result: `docs/issues/tf-x-8-ffmpeg-gap-not-flow-blocking-in-doctor.md` + one index line under
`## robustness`, the noise finding in `dismissed/`, everything journaled in
`.agent/feedback/journal/2026-07.md`.
