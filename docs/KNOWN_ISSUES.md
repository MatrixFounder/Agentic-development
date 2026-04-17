# Known Issues & Tech Debt

**Purpose:** Track recurring bugs, architectural limitations, and sensitive areas to avoid repeating mistakes.

## Native Claude Code Agent Teams — known limitations (Layer B)

These apply to **Layer B** (`TeamCreate`/`SendMessage`). Layer A (parallel `Agent` tool-uses in one message) is not affected.

- [ ] **No session resumption**: `/resume` does not restore in-process teammates. After a session restart you must respawn the team from scratch. Do not design workflows that assume teammate persistence across `/resume`.
- [ ] **Task status lag**: teammates sometimes fail to mark tasks complete in the shared task list, blocking dependent tasks. Include a timeout + lead-side status audit when designing long-running teams.
- [ ] **One team per session**: a lead session can manage only one team at a time. Do not nest teams (e.g., a teammate spawning its own sub-team is not supported).
- [ ] **No leadership transfer**: cannot promote a teammate to lead or hand off the team. The lead session that created the team must orchestrate cleanup via `TeamDelete`.
- [ ] **Higher token costs**: each teammate is an independent Claude session — costs scale ~linearly with team size. Prefer Layer A for orthogonal critique where a peer mailbox is not required (see `skill-parallel-orchestration` §4 decision rule).
- [ ] **`TeamDelete` does NOT clean up after protocol shutdown** (verified Wave-4 probe, 2026-04-17): the shutdown round-trip works (`SendMessage({type: "shutdown_request"})` → teammate replies `shutdown_approved`), but `config.json` members array is NOT updated. `TeamDelete` then fails with `Cannot cleanup team with N active member(s)`. The error references `requestShutdown` which is not an available tool. **Workaround**: manual `rm -rf ~/.claude/teams/<name>/ ~/.claude/tasks/<name>/`. This blocks any workflow that expects idempotent team lifecycle via `TeamDelete`.
- [ ] **Async spawn ≠ sync return**: `Agent(team_name, name, ...)` returns `"Spawned successfully. agent_id: ..."` immediately; teammate runs in background. Lead must poll the inbox file (`~/.claude/teams/<name>/inboxes/<recipient>.json`) or await an auto-delivered message turn. Different contract from Layer A where `Agent` returns the subagent's result synchronously.
- [ ] **Model inheritance inconsistent across agent types**: spawning `subagent_type: "Explore"` as a teammate defaults to `model: "haiku"` regardless of lead's model. If Opus is required for a teammate, pass `model` explicitly at spawn time.
- [ ] **Runtime sends structured JSON despite docs**: docs say "Do NOT send structured JSON status messages like `{type: idle,...}`"; the runtime itself auto-delivers `{"type":"idle_notification", ...}` and `{"type":"shutdown_approved", ...}` into the lead's inbox. Parsers must handle both plain text and structured JSON.

## Wave-1/2 specific

- [ ] **Wrapper/SOT drift risk** (reduced after v3.11.1 thin refactor): each of the 12 `.claude/agents/*.md` wrappers references exactly one SOT path (its primary `System/Agents/XX_*.md` or `.agent/skills/*/SKILL.md`). Two critic wrappers also reference the `template_critique.md` / `sarcastic.md` asset paths. If an SOT file is renamed or moved, wrappers must be updated manually — no automatic sync. Verification after any rename in `System/Agents/` or `.agent/skills/{vdd-adversarial,skill-adversarial-*}/`: `grep -l '<old-path>' .claude/agents/` → should return no stale references.
