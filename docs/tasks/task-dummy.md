# Task DUMMY — Smoke fixture for /vdd-multi parallel critics

**Purpose**: minimal deterministic fixture to verify Wave 1 teams-mode integration.
**Not a real task** — do not link from roadmap or execute as development work.

## How to use

Run `/vdd-multi` against the code below. Expected behaviour:

1. In a single assistant message, orchestrator issues **three parallel `Agent` tool-uses**: `subagent_type: critic-logic`, `critic-security`, `critic-performance`.
2. Each critic returns a structured report per its teammate contract.
3. Orchestrator merges reports, dedupes by (file, line), escalates severity on cross-category overlaps.

Each critic should find at least its own category's seeded flaw (see "Expected findings" below). If a critic misses its seeded flaw or invents issues, investigate the wrapper or SOT references.

## Fixture code (`users_api.py` — do not deploy)

```python
import sqlite3
import subprocess
import json

API_KEY = "sk-prod-7f3a9b2e1d4c6f8a0b5c7d9e1f3a5b7c"  # (1) hardcoded secret

def get_user_orders(db_path: str, email: str) -> list[dict]:
    """Return all orders for a given user email."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # (2) SQL injection: email interpolated directly into query
    cur.execute(f"SELECT id FROM users WHERE email = '{email}'")
    user_row = cur.fetchone()
    user_id = user_row[0]  # (3) no None-check — crashes if user missing

    # (4) N+1 query pattern — one SELECT per order id
    cur.execute("SELECT id FROM orders WHERE user_id = ?", (user_id,))
    order_ids = [r[0] for r in cur.fetchall()]

    orders = []
    for oid in order_ids:
        cur.execute(f"SELECT * FROM order_items WHERE order_id = {oid}")  # (5) interpolation + N+1
        orders.append({"order_id": oid, "items": cur.fetchall()})

    return orders


def export_report(user_email: str, out_path: str) -> None:
    """Run the reporting CLI and save its stdout to out_path."""
    # (6) shell=True + unsanitized input → command injection
    result = subprocess.run(
        f"/usr/local/bin/report-tool --user {user_email}",
        shell=True,
        capture_output=True,
        text=True,
    )
    # (7) load entire stdout into memory even for huge reports
    with open(out_path, "w") as f:
        f.write(result.stdout)


def rank_users(users: list[dict]) -> list[dict]:
    """Rank users by number of mutual friends (pairwise)."""
    ranked = []
    for u in users:
        score = 0
        for v in users:  # (8) O(n²) nested loop, unbounded for large `users`
            if u["id"] != v["id"]:
                score += len(set(u["friends"]) & set(v["friends"]))
        ranked.append({"id": u["id"], "score": score})
    return ranked


def load_config(path: str) -> dict:
    f = open(path)  # (9) file handle leaked — never closed
    return json.loads(f.read())
```

## Expected findings (sanity check for critics)

### critic-logic should flag
- **(3)** `user_row[0]` with no `None` check — happy-path assumption; crashes on unknown email.
- **(9)** leaked file handle in `load_config` (resource-mismanagement → correctness adjacent).

### critic-security should flag
- **(1)** hardcoded API key in source.
- **(2)** SQL injection via f-string in `get_user_orders`.
- **(5)** SQL injection in order-items loop.
- **(6)** `shell=True` with unsanitized `user_email` — command injection.

### critic-performance should flag
- **(4)+(5)** N+1 query pattern in order fetching — one query per order.
- **(7)** load-entire-stdout into memory, then write — should stream.
- **(8)** O(n²) `rank_users` with nested loop over all users.
- **(9)** resource leak (also perf at scale).

### Cross-category overlaps (orchestrator should escalate severity)
- **(5)**: security (SQLi) + perf (N+1) on the same line — severity should escalate.
- **(9)**: logic (correctness) + perf (leak at scale) on same line.

## Pass/fail criteria

- **Pass**: each critic finds its own category flaws (at least 2 of 3 seeded per category). Merged report contains an "Overlaps" section with (5) and ideally (9).
- **Fail**: critic misses all of its category's flaws → investigate wrapper body or SOT reference. Critic hallucinates issues not in the fixture → expected signal for SKILL.md convergence logic (should self-terminate).
- **Regression check**: the fixture is intentionally NOT fixed after the run. Leave the file intact for repeatable smoke tests.
