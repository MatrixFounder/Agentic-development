"""HTML activity reports for the admin dashboard."""

import logging
import sqlite3
from datetime import date
from typing import Optional

logger = logging.getLogger("reports")

PAGE_TEMPLATE = """<!doctype html>
<html><head><title>{title}</title></head>
<body>
<h1>{title}</h1>
<table border="1">
<tr><th>User</th><th>Action</th><th>Timestamp</th></tr>
{rows}
</table>
<p>Total events: {count}</p>
</body></html>"""


class ReportGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_events(self, start: date, end: date) -> list[sqlite3.Row]:
        """Events in [start, end] — both boundary days included."""
        conn = self._connect()
        try:
            return conn.execute(
                "SELECT u.display_name, e.action, e.created_at "
                "FROM events e JOIN users u ON u.id = e.user_id "
                "WHERE e.created_at >= ? AND e.created_at < ? "
                "ORDER BY e.created_at",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
        finally:
            conn.close()

    def render_activity_report(self, start: date, end: date, title: str) -> str:
        events = self.fetch_events(start, end)
        rows = ""
        for event in events:
            rows += (
                f"<tr><td>{event['display_name']}</td>"
                f"<td>{event['action']}</td>"
                f"<td>{event['created_at']}</td></tr>\n"
            )
        html = PAGE_TEMPLATE.format(title=title, rows=rows, count=len(events))
        logger.info("rendered report '%s' with %d events", title, len(events))
        return html

    def save_report(self, html: str, out_path: str) -> None:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

    def top_users(self, start: date, end: date, limit: int = 10) -> list[dict]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT u.display_name AS name, COUNT(*) AS events "
                "FROM events e JOIN users u ON u.id = e.user_id "
                "WHERE e.created_at >= ? AND e.created_at < ? "
                "GROUP BY u.id ORDER BY events DESC LIMIT ?",
                (start.isoformat(), end.isoformat(), limit),
            ).fetchall()
            return [{"name": r["name"], "events": r["events"]} for r in rows]
        finally:
            conn.close()

    def event_count(self, start: date, end: date, action: Optional[str] = None) -> int:
        conn = self._connect()
        try:
            if action is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS n FROM events "
                    "WHERE created_at >= ? AND created_at < ? AND action = ?",
                    (start.isoformat(), end.isoformat(), action),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) AS n FROM events "
                    "WHERE created_at >= ? AND created_at < ?",
                    (start.isoformat(), end.isoformat()),
                ).fetchone()
            return int(row["n"])
        finally:
            conn.close()
