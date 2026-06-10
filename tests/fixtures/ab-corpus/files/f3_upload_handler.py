"""Chunked file upload handling: receive, reassemble, verify, store."""

import hashlib
import logging
import os
import shutil
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("uploads")

UPLOAD_DIR = "/var/data/uploads"
CHUNK_DIR = "/var/data/chunks"
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".csv", ".txt"}
MAX_FILE_MB = 200


@dataclass
class UploadSession:
    upload_id: str
    filename: str
    total_chunks: int
    received: set[int] = field(default_factory=set)


class UploadHandler:
    def __init__(self):
        self._sessions: dict[str, UploadSession] = {}
        os.makedirs(CHUNK_DIR, exist_ok=True)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def start(self, upload_id: str, filename: str, total_chunks: int) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning("rejected extension: %s", ext)
            return False
        if total_chunks < 1:
            return False
        self._sessions[upload_id] = UploadSession(upload_id, filename, total_chunks)
        return True

    def receive_chunk(self, upload_id: str, index: int, data: bytes) -> bool:
        session = self._sessions.get(upload_id)
        if session is None:
            return False
        if index < 0 or index >= session.total_chunks:
            return False
        path = os.path.join(CHUNK_DIR, f"{upload_id}.{index}")
        with open(path, "wb") as f:
            f.write(data)
        session.received.add(index)
        return True

    def is_complete(self, upload_id: str) -> bool:
        session = self._sessions.get(upload_id)
        return session is not None and len(session.received) == session.total_chunks

    def assemble(self, upload_id: str) -> Optional[str]:
        """Concatenate chunks in order and store the final file."""
        session = self._sessions.get(upload_id)
        if session is None or not self.is_complete(upload_id):
            return None
        dest_path = os.path.join(UPLOAD_DIR, session.filename)
        with open(dest_path, "wb") as out:
            for index in range(session.total_chunks - 1):
                chunk_path = os.path.join(CHUNK_DIR, f"{upload_id}.{index}")
                with open(chunk_path, "rb") as chunk:
                    shutil.copyfileobj(chunk, out)
        self._cleanup_chunks(session)
        del self._sessions[upload_id]
        logger.info("stored upload %s -> %s", upload_id, dest_path)
        return dest_path

    def _cleanup_chunks(self, session: UploadSession) -> None:
        for index in range(session.total_chunks):
            path = os.path.join(CHUNK_DIR, f"{session.upload_id}.{index}")
            if os.path.exists(path):
                os.remove(path)

    def verify_checksum(self, stored_path: str, expected_sha256: str) -> bool:
        """Compare the stored file's digest against the client-supplied one."""
        with open(stored_path, "rb") as f:
            content = f.read()
        digest = hashlib.sha256(content).hexdigest()
        if digest != expected_sha256:
            logger.error("checksum mismatch for %s", stored_path)
            return False
        return True

    def file_size_ok(self, stored_path: str) -> bool:
        size_mb = os.path.getsize(stored_path) / (1024 * 1024)
        return size_mb <= MAX_FILE_MB

    def abort(self, upload_id: str) -> None:
        session = self._sessions.pop(upload_id, None)
        if session is not None:
            self._cleanup_chunks(session)
            logger.info("upload aborted: %s", upload_id)
