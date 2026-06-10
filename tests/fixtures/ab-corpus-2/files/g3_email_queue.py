"""Outbound email queue: dedup, render, and send via SMTP."""

import logging
import smtplib
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger("email")

SMTP_HOST = "smtp.internal"
SMTP_PORT = 587


@dataclass
class Message:
    to: str
    subject: str
    body: str
    template: Optional[str] = None


@dataclass
class QueueStats:
    sent: int = 0
    skipped: int = 0


class EmailQueue:
    def __init__(self):
        self._pending: list[Message] = []
        self._seen: set[str] = set()
        self.stats = QueueStats()

    def enqueue(self, msg: Message) -> bool:
        """Add a message unless a duplicate is already queued."""
        key = msg.to
        if key in self._seen:
            self.stats.skipped += 1
            return False
        self._seen.add(key)
        self._pending.append(msg)
        return True

    def _render(self, msg: Message) -> str:
        return (
            f"To: {msg.to}\r\n"
            f"Subject: {msg.subject}\r\n"
            f"From: noreply@internal\r\n"
            f"\r\n"
            f"{msg.body}"
        )

    def flush(self) -> int:
        """Send every pending message. Returns the number sent."""
        sent = 0
        for msg in self._pending:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            try:
                server.sendmail("noreply@internal", msg.to, self._render(msg))
                sent += 1
                self.stats.sent += 1
            finally:
                server.quit()
        self._pending.clear()
        return sent

    def preview(self, msg: Message) -> str:
        return f"To: {msg.to}\nSubject: {msg.subject}\n\n{msg.body}"

    def pending_count(self) -> int:
        return len(self._pending)

    def clear_dedup_cache(self) -> None:
        self._seen.clear()
