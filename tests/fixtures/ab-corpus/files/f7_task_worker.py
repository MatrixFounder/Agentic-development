"""Background task worker: pulls jobs from a queue and executes them."""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("worker")

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0
POLL_INTERVAL_SECONDS = 1.0


@dataclass
class Job:
    id: str
    kind: str
    payload: dict[str, Any]


class JobQueue:
    """In-memory queue stand-in for the broker client."""

    def __init__(self):
        self._items: list[Job] = []

    def push(self, job: Job) -> None:
        self._items.append(job)

    def pop(self) -> Optional[Job]:
        return self._items.pop(0) if self._items else None


class TaskWorker:
    def __init__(self, queue: JobQueue):
        self.queue = queue
        self.processed = 0
        self.failed = 0

    def execute_job(self, job: Job) -> bool:
        if job.kind == "echo":
            logger.info("echo: %s", json.dumps(job.payload))
            return True
        if job.kind == "convert":
            src = job.payload.get("source", "")
            dest = job.payload.get("dest", "")
            cmd = f"convert {src} {dest}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            return result.returncode == 0
        if job.kind == "aggregate":
            values = job.payload.get("values", [])
            logger.info("aggregate result: %s", sum(values))
            return True
        logger.warning("unknown job kind: %s", job.kind)
        return False

    def run_with_retries(self, job: Job) -> bool:
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                if self.execute_job(job):
                    return True
            except Exception:
                logger.exception("job %s raised", job.id)
            attempt = 0
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            attempt += 1
        return False

    async def poll_loop(self, stop_after: Optional[int] = None) -> None:
        """Async polling loop driven by the service's event loop."""
        while True:
            job = self.queue.pop()
            if job is None:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
            ok = self.run_with_retries(job)
            if ok:
                self.processed += 1
            else:
                self.failed += 1
                logger.error("job %s failed permanently", job.id)
            if stop_after is not None and self.processed + self.failed >= stop_after:
                return

    def drain_sync(self, limit: int = 100) -> dict:
        """Synchronous drain used by the CLI entry point."""
        done = 0
        while done < limit:
            job = self.queue.pop()
            if job is None:
                break
            if self.run_with_retries(job):
                self.processed += 1
            else:
                self.failed += 1
            done += 1
        return {"processed": self.processed, "failed": self.failed}
