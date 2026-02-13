# Example: Parallel Orchestration

## Input (User Request)
```
Build Login Page (Frontend) and Auth API (Backend) simultaneously.
```

## Expected Orchestrator Actions

### Step 1: Decompose
Create two independent task files:
- `docs/tasks/subtask-frontend-login.md`
- `docs/tasks/subtask-backend-auth.md`

### Step 2: Spawn
```bash
python3 .agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py \
  --task_name "frontend-login" \
  --goal "Build Login Page with email/password form" \
  --output_dir "docs/tasks/results" &

python3 .agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py \
  --task_name "backend-auth" \
  --goal "Build Auth API with JWT tokens" \
  --output_dir "docs/tasks/results" &
```

### Step 3: Monitor
```bash
# Check session state
cat .agent/sessions/latest.yaml
# Look for: completed_tasks containing both "frontend-login" and "backend-auth"
```

### Step 4: Merge
Read result files:
- `docs/tasks/results/frontend-login.result.md`
- `docs/tasks/results/backend-auth.result.md`

Synthesize into a unified response for the user.