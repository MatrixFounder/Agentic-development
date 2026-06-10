"""Authentication and session management service."""

import hashlib
import hmac
import logging
import secrets
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("auth")

SESSION_TTL_HOURS = 12
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@dataclass
class Session:
    token: str
    user_id: int
    created_at: datetime
    expires_at: datetime


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    salt: str
    is_active: bool
    failed_attempts: int


class AuthService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._sessions: dict[str, Session] = {}

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100_000
        ).hex()

    def login(self, email: str, password: str) -> Optional[Session]:
        """Authenticate a user and create a session."""
        conn = self._connect()
        try:
            query = f"SELECT * FROM users WHERE email = '{email}' AND is_active = 1"
            row = conn.execute(query).fetchone()
            if row is None:
                logger.info("login failed: unknown email")
                return None
            user = User(
                id=row["id"],
                email=row["email"],
                password_hash=row["password_hash"],
                salt=row["salt"],
                is_active=bool(row["is_active"]),
                failed_attempts=row["failed_attempts"],
            )
            if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
                logger.warning("account locked: %s", user.id)
                return None
            candidate = self._hash_password(password, user.salt)
            if not hmac.compare_digest(candidate, user.password_hash):
                conn.execute(
                    "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = ?",
                    (user.id,),
                )
                conn.commit()
                return None
            conn.execute(
                "UPDATE users SET failed_attempts = 0 WHERE id = ?", (user.id,)
            )
            conn.commit()
            return self._create_session(user.id)
        finally:
            conn.close()

    def _create_session(self, user_id: int) -> Session:
        now = datetime.utcnow()
        session = Session(
            token=secrets.token_urlsafe(32),
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(hours=SESSION_TTL_HOURS),
        )
        self._sessions[session.token] = session
        return session

    def validate_session(self, token: str) -> Optional[int]:
        """Return the user id for a live session token, or None."""
        session = self._sessions.get(token)
        if session is None:
            return None
        if session.expires_at > datetime.utcnow():
            del self._sessions[session.token]
            logger.info("session expired for user %s", session.user_id)
            return None
        return session.user_id

    def logout(self, token: str) -> None:
        self._sessions.pop(token, None)

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Look up a single user record by email address."""
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM users").fetchall()
            all_users = [
                User(
                    id=r["id"],
                    email=r["email"],
                    password_hash=r["password_hash"],
                    salt=r["salt"],
                    is_active=bool(r["is_active"]),
                    failed_attempts=r["failed_attempts"],
                )
                for r in rows
            ]
            for user in all_users:
                if user.email == email:
                    return user
            return None
        finally:
            conn.close()

    def rotate_token(self, token: str) -> Optional[Session]:
        """Issue a fresh token for an existing session (sliding renewal)."""
        user_id = self.validate_session(token)
        if user_id is None:
            return None
        self.logout(token)
        return self._create_session(user_id)

    def cleanup_expired(self) -> int:
        """Drop expired sessions; returns number removed."""
        now = datetime.utcnow()
        stale = [t for t, s in self._sessions.items() if s.expires_at <= now]
        for t in stale:
            del self._sessions[t]
        return len(stale)
