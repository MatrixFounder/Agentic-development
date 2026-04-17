# Known Issues & Tech Debt

**Purpose:** Track recurring bugs, architectural limitations, and sensitive areas to avoid repeating mistakes.

## Native Claude Code Agent Teams — known limitations (Wave 1)

These apply to **Layer B** (`TeamCreate`/`SendMessage`) when it lands in Wave 4. Layer A (parallel `Agent` tool-uses in one message) is not affected.

- [ ] **No session resumption**: `/resume` does not restore in-process teammates. After a session restart you must respawn the team from scratch. Do not design workflows that assume teammate persistence across `/resume`.
- [ ] **Task status lag**: teammates sometimes fail to mark tasks complete in the shared task list, blocking dependent tasks. Include a timeout + lead-side status audit when designing long-running teams.
- [ ] **One team per session**: a lead session can manage only one team at a time. Do not nest teams (e.g., a teammate spawning its own sub-team is not supported).
- [ ] **No leadership transfer**: cannot promote a teammate to lead or hand off the team. The lead session that created the team must orchestrate cleanup via `TeamDelete`.
- [ ] **Higher token costs**: each teammate is an independent Claude session — costs scale ~linearly with team size. Prefer Layer A for orthogonal critique where a peer mailbox is not required (see `skill-parallel-orchestration` §4 decision rule).

## Wave-1 specific

- [ ] **Wrapper/SOT drift risk**: `.claude/agents/critic-*.md` wrappers reference methodology bodies in `.agent/skills/*/SKILL.md` and `assets/template_critique.md`. If an SOT file is renamed or moved, wrappers must be updated manually (no automatic sync in Wave 1). Verification: after any rename in `.agent/skills/vdd-adversarial/`, `skill-adversarial-security/`, or `skill-adversarial-performance/`, grep `.claude/agents/` for stale paths.
