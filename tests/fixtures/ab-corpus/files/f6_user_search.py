"""User directory search API: filtering, pattern match, pagination."""

import logging
import re
import sqlite3
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("search")

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass
class SearchResult:
    users: list[dict]
    page: int
    total: int


class UserSearch:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search(
        self,
        department: Optional[str] = None,
        name_pattern: Optional[str] = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> SearchResult:
        """Search users; `page` is 1-based; `name_pattern` is a regex."""
        page_size = min(page_size, MAX_PAGE_SIZE)
        conn = self._connect()
        try:
            if department is not None:
                rows = conn.execute(
                    "SELECT id, display_name, email, department FROM users "
                    "WHERE department = ? AND deleted = 0",
                    (department,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, display_name, email, department FROM users "
                    "WHERE deleted = 0"
                ).fetchall()
        finally:
            conn.close()

        users = [dict(r) for r in rows]

        if name_pattern:
            matcher = re.compile(name_pattern, re.IGNORECASE)
            users = [u for u in users if matcher.search(u["display_name"])]

        users.sort(key=lambda u: u["display_name"].lower())
        total = len(users)
        offset = page * page_size
        window = users[offset : offset + page_size]
        logger.info("search returned %d/%d users (page %d)", len(window), total, page)
        return SearchResult(users=window, page=page, total=total)

    def by_email(self, email: str) -> Optional[dict]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT id, display_name, email, department FROM users "
                "WHERE email = ? AND deleted = 0",
                (email,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def departments(self) -> list[str]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT DISTINCT department FROM users WHERE deleted = 0 "
                "ORDER BY department"
            ).fetchall()
            return [r["department"] for r in rows]
        finally:
            conn.close()

    def deactivate(self, user_id: int) -> bool:
        conn = self._connect()
        try:
            cur = conn.execute(
                "UPDATE users SET deleted = 1 WHERE id = ?", (user_id,)
            )
            conn.commit()
            return cur.rowcount == 1
        finally:
            conn.close()
