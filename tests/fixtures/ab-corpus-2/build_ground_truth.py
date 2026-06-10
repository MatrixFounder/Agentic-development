#!/usr/bin/env python3
"""Build ground_truth.json for corpus-2 (tier-diverse mini-experiment), then seal.

Run ONCE before any arm runs. Lines derived from unique anchors, never hand-counted.
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
    ("g1_csv_ingest.py", "id=int(row[0]),", 1, "logic", "CRITICAL",
     "parse() builds a header->index map but then maps fields by hardcoded positions 0-3, silently corrupting every record when the CSV columns are in any other order"),
    ("g1_csv_ingest.py", "writer.writerow([r.id, r.name,", 1, "security", "HIGH",
     "CSV formula injection: name/email written to the export without neutralizing a leading =,+,-,@ — formula executes when the file is opened in a spreadsheet"),
    ("g1_csv_ingest.py", "lines = open(path).readlines()", 1, "performance", "MEDIUM",
     "count_rows loads the entire file into memory via readlines() just to count rows instead of streaming"),
    ("g2_rate_limiter.py", "if len(hits) <= self.limit:", 1, "logic", "HIGH",
     "off-by-one: <= allows limit+1 requests per window (append happens when len already equals limit)"),
    ("g2_rate_limiter.py", 'return forwarded.split(",")[0].strip()', 1, "security", "CRITICAL",
     "rate-limit identity trusts the client-controlled X-Forwarded-For first hop — spoofing the header rotates the key and bypasses the limit entirely"),
    ("g2_rate_limiter.py", "hits.pop(0)", 1, "performance", "MEDIUM",
     "hits is a list; pop(0) is O(n) per evicted timestamp — should be a deque (or ring buffer)"),
    ("g3_email_queue.py", "key = msg.to", 1, "logic", "MEDIUM",
     "dedup keyed only by recipient address — two distinct messages to the same address are silently collapsed to one"),
    ("g3_email_queue.py", 'f"Subject: {msg.subject}\\r\\n"', 1, "security", "CRITICAL",
     "email header injection: subject/to interpolated into a raw header string with CRLF, then handed to sendmail — attacker can inject Bcc/extra headers"),
    ("g3_email_queue.py", "server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)", 1, "performance", "HIGH",
     "opens a fresh SMTP connection per message inside the flush loop — no connection reuse/pooling (handshake per send)"),
    ("g4_inventory.py", 'if row["stock"] > quantity:', 1, "logic", "HIGH",
     "reserve uses > instead of >=, so reserving the exact remaining stock fails (off-by-one), leaving stranded inventory"),
    ("g4_inventory.py", "f\"WHERE name LIKE '%{fragment}%'\"", 1, "security", "MEDIUM",
     "SQL injection: search fragment interpolated into the LIKE clause via f-string (admin-console search, hence MEDIUM)"),
    ("g4_inventory.py", '"SELECT COUNT(*) AS n FROM movements "', 1, "performance", "CRITICAL",
     "N+1 query: a movements COUNT(*) is issued per product inside low_stock_report, scanning the whole catalog on every dashboard load"),
    ("g5_graph_traversal.py", "queue.append(neighbor)", 1, "logic", "CRITICAL",
     "reachable() enqueues neighbors with no visited guard before append — any cyclic graph causes an infinite loop (hang)"),
    ("g5_graph_traversal.py", 'logger.info("registered node %s", node)', 1, "security", "MEDIUM",
     "log injection: a user-controlled node id is written to the log unescaped — CRLF lets an attacker forge log lines"),
    ("g5_graph_traversal.py", "total += self.count_paths(neighbor, dst)", 1, "performance", "HIGH",
     "count_paths recurses without memoization — exponential blowup on DAGs with many overlapping paths"),
    ("g6_session_store.py", "session.expires_at = time.time() + self.ttl", 1, "logic", "MEDIUM",
     "touch() slides expiry without checking the current one, resurrecting an already-expired (but not yet purged) session"),
    ("g6_session_store.py", 'return "".join(random.choice(alphabet) for _ in range(TOKEN_LENGTH))', 1, "security", "HIGH",
     "session tokens generated with the random module (Mersenne Twister, predictable) instead of secrets — tokens are guessable"),
    ("g6_session_store.py", "self._purge_expired()", 1, "performance", "CRITICAL",
     "get() runs a full O(n) sweep of all sessions on every single lookup — purge belongs on a timer, not the hot path"),
]


def find_line(path: Path, anchor: str, occurrence: int) -> int:
    hits = [n for n, line in enumerate(path.read_text().splitlines(), 1) if anchor in line]
    if len(hits) < occurrence:
        sys.exit(f"ANCHOR MISS: {path.name!r} {anchor!r} (found {len(hits)}, need {occurrence})")
    return hits[occurrence - 1]


def main() -> None:
    bugs = []
    for fname, anchor, occ, klass, sev, desc in BUGS:
        line = find_line(FILES / fname, anchor, occ)
        bugs.append({"id": f"{fname.split('_')[0]}-{klass[:3].upper()}", "file": fname,
                     "line": line, "class": klass, "severity": sev, "description": desc})
    by_class = {c: sum(1 for b in bugs if b["class"] == c) for c in ("logic", "security", "performance")}
    by_sev = {s: sum(1 for b in bugs if b["severity"] == s) for s in ("CRITICAL", "HIGH", "MEDIUM")}
    assert by_class == {"logic": 6, "security": 6, "performance": 6}, by_class
    assert by_sev == {"CRITICAL": 6, "HIGH": 6, "MEDIUM": 6}, by_sev
    gt = {"version": 1, "corpus": "ab-corpus-2", "total_bugs": len(bugs), "by_class": by_class,
          "by_severity": by_sev, "controls": ["ctrl_aggregate.py"], "bugs": bugs}
    (ROOT / "ground_truth.json").write_text(json.dumps(gt, indent=2) + "\n")
    seal = {"sealed_at_utc": datetime.now(timezone.utc).isoformat(), "sha256": {}}
    for p in sorted(FILES.glob("*.py")) + [ROOT / "ground_truth.json"]:
        seal["sha256"][p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (ROOT / "seal.json").write_text(json.dumps(seal, indent=2) + "\n")
    print(f"ground_truth.json: {len(bugs)} bugs ({by_class} / {by_sev})")
    print(f"seal.json: {len(seal['sha256'])} hashes @ {seal['sealed_at_utc']}")


if __name__ == "__main__":
    main()
