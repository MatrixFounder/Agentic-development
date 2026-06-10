#!/usr/bin/env python3
"""Build ground_truth.json by locating seeded-bug anchor lines, then seal.

Run ONCE before any arm runs. Anchors are unique substrings (with an
occurrence index for repeated patterns); line numbers are derived, never
hand-counted.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
FILES = ROOT / "files"

# (file, anchor substring, occurrence, class, severity, description)
BUGS = [
    ("f1_auth_service.py", "if session.expires_at > datetime.utcnow():", 1, "logic", "CRITICAL",
     "Session expiry comparison inverted: live sessions are deleted as 'expired', truly expired ones validate"),
    ("f1_auth_service.py", "SELECT * FROM users WHERE email = '{email}'", 1, "security", "CRITICAL",
     "SQL injection: email interpolated into query via f-string (login bypass / data exfiltration)"),
    ("f1_auth_service.py", 'rows = conn.execute("SELECT * FROM users").fetchall()', 1, "performance", "HIGH",
     "find_user_by_email loads the entire users table into memory and scans in Python instead of WHERE email = ?"),
    ("f2_payments.py", "discounted = round(line * (1.0 - discount_pct", 1, "logic", "HIGH",
     "Money math in binary floats with per-line rounding then float accumulation; final total never rounded before *100 — cent drift"),
    ("f2_payments.py", "card=%s cvv=%s", 1, "security", "CRITICAL",
     "Full PAN and CVV written to logs (PCI-DSS violation; CVV must never be persisted)"),
    ("f2_payments.py", "SELECT unit_price, quantity FROM order_items WHERE order_id = ?", 1, "performance", "HIGH",
     "N+1 query: one order_items query per order inside monthly report loop instead of a JOIN/aggregate"),
    ("f3_upload_handler.py", "for index in range(session.total_chunks - 1):", 1, "logic", "MEDIUM",
     "Off-by-one in reassembly: last chunk never appended (range excludes total_chunks-1 index)"),
    ("f3_upload_handler.py", "dest_path = os.path.join(UPLOAD_DIR, session.filename)", 1, "security", "CRITICAL",
     "Path traversal: client-controlled filename joined into UPLOAD_DIR without sanitization (../ escapes)"),
    ("f3_upload_handler.py", "content = f.read()", 1, "performance", "MEDIUM",
     "verify_checksum reads the whole file (up to 200MB) into memory instead of streaming chunks into the hash"),
    ("f4_cache_layer.py", "return age < self.ttl", 1, "logic", "HIGH",
     "_is_expired inverted: fresh entries report expired (evicted), stale entries report fresh (served)"),
    ("f4_cache_layer.py", "value = pickle.loads(raw)", 1, "security", "CRITICAL",
     "Untrusted deserialization: pickle.loads on bytes from shared Redis — RCE if any writer is compromised"),
    ("f4_cache_layer.py", "self.redis.setex(key, self.ttl, pickle.dumps(value))", 1, "performance", "HIGH",
     "L1 dict is unbounded: set() always inserts, no max-size/eviction — memory grows without limit"),
    ("f5_report_generator.py", "WHERE e.created_at >= ? AND e.created_at < ?", 1, "logic", "MEDIUM",
     "Docstring promises [start, end] inclusive but query uses < end with date-typed bound — boundary day excluded"),
    ("f5_report_generator.py", "<tr><td>{event['display_name']}</td>", 1, "security", "HIGH",
     "Stored XSS: user display_name interpolated into HTML report without escaping"),
    ("f5_report_generator.py", "rows += (", 1, "performance", "MEDIUM",
     "O(n^2) string concatenation building report rows in a loop instead of join()"),
    ("f6_user_search.py", "offset = page * page_size", 1, "logic", "MEDIUM",
     "Pagination: page is 1-based per docstring, offset must be (page-1)*size — first page is skipped"),
    ("f6_user_search.py", "matcher = re.compile(name_pattern, re.IGNORECASE)", 1, "security", "HIGH",
     "ReDoS: user-supplied regex compiled and executed against rows (catastrophic backtracking DoS)"),
    ("f6_user_search.py", "users.sort(key=lambda u:", 1, "performance", "MEDIUM",
     "Fetches all rows, filters/sorts/slices in Python — pagination belongs in SQL (LIMIT/OFFSET, indexed ORDER BY)"),
    ("f7_task_worker.py", "attempt = 0", 2, "logic", "CRITICAL",
     "Retry counter reset inside the while body — attempt never reaches MAX_RETRIES, failing job retries forever"),
    ("f7_task_worker.py", "subprocess.run(cmd, shell=True", 1, "security", "CRITICAL",
     "Command injection: payload-derived source/dest interpolated into shell=True command line"),
    ("f7_task_worker.py", "time.sleep(POLL_INTERVAL_SECONDS)", 1, "performance", "HIGH",
     "Blocking time.sleep inside async poll_loop stalls the entire event loop (should be await asyncio.sleep)"),
    ("f8_config_loader.py", "merged.update(self._read_file())", 1, "logic", "MEDIUM",
     "Precedence inverted vs docstring: file applied after env overlay, so file values override environment"),
    ("f8_config_loader.py", "data = yaml.load(f)", 1, "security", "CRITICAL",
     "yaml.load without SafeLoader: arbitrary object construction from config file (use yaml.safe_load)"),
    ("f8_config_loader.py", "config = self.load()", 1, "performance", "MEDIUM",
     "get() re-reads and re-parses the YAML file (plus env scan) on every single key access — no caching"),
]


def find_line(path: Path, anchor: str, occurrence: int) -> int:
    hits = []
    for n, line in enumerate(path.read_text().splitlines(), start=1):
        if anchor in line:
            hits.append(n)
    if len(hits) < occurrence:
        sys.exit(f"ANCHOR MISS: {path.name!r} {anchor!r} (found {len(hits)}, need {occurrence})")
    return hits[occurrence - 1]


def main() -> None:
    bugs = []
    for fname, anchor, occ, klass, sev, desc in BUGS:
        line = find_line(FILES / fname, anchor, occ)
        bugs.append({"id": f"{fname.split('_')[0]}-{klass[:3].upper()}",
                     "file": fname, "line": line, "class": klass,
                     "severity": sev, "description": desc})
    # Stratification self-check
    by_class = {c: sum(1 for b in bugs if b["class"] == c) for c in ("logic", "security", "performance")}
    by_sev = {s: sum(1 for b in bugs if b["severity"] == s) for s in ("CRITICAL", "HIGH", "MEDIUM")}
    assert by_class == {"logic": 8, "security": 8, "performance": 8}, by_class
    assert by_sev == {"CRITICAL": 8, "HIGH": 8, "MEDIUM": 8}, by_sev
    gt = {"version": 1, "total_bugs": len(bugs), "by_class": by_class, "by_severity": by_sev,
          "controls": ["c1_text_utils.py", "c2_date_utils.py"], "bugs": bugs}
    (ROOT / "ground_truth.json").write_text(json.dumps(gt, indent=2) + "\n")

    seal = {"sealed_at_utc": datetime.now(timezone.utc).isoformat(), "sha256": {}}
    for p in sorted(FILES.glob("*.py")) + [ROOT / "ground_truth.json"]:
        seal["sha256"][p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (ROOT / "seal.json").write_text(json.dumps(seal, indent=2) + "\n")
    print(f"ground_truth.json: {len(bugs)} bugs ({by_class} / {by_sev})")
    print(f"seal.json: {len(seal['sha256'])} hashes @ {seal['sealed_at_utc']}")


if __name__ == "__main__":
    main()
