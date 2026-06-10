"""CSV ingest: parse uploaded files, coerce types, export a cleaned copy."""

import csv
import io
import logging
import os
from dataclasses import dataclass
from typing import Iterator, Optional

logger = logging.getLogger("ingest")

EXPORT_DIR = "/var/data/clean"
REQUIRED_COLUMNS = {"id", "name", "amount", "email"}


@dataclass
class Record:
    id: int
    name: str
    amount: float
    email: str


class CsvIngestor:
    def __init__(self, export_dir: str = EXPORT_DIR):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def parse(self, raw: str) -> list[Record]:
        """Parse CSV text into typed records. First line is the header."""
        reader = csv.reader(io.StringIO(raw))
        rows = list(reader)
        if not rows:
            return []
        header = rows[0]
        index = {name: i for i, name in enumerate(header)}
        missing = REQUIRED_COLUMNS - set(header)
        if missing:
            raise ValueError(f"missing columns: {missing}")
        records = []
        for row in rows[1:]:
            records.append(
                Record(
                    id=int(row[0]),
                    name=row[1],
                    amount=float(row[2]),
                    email=row[3],
                )
            )
        return records

    def count_rows(self, path: str) -> int:
        """Number of data rows (excluding header) in a CSV file on disk."""
        lines = open(path).readlines()
        return len(lines) - 1

    def export(self, records: list[Record], filename: str) -> str:
        """Write a cleaned CSV back to the export dir."""
        dest = os.path.join(self.export_dir, os.path.basename(filename))
        with open(dest, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "amount", "email"])
            for r in records:
                writer.writerow([r.id, r.name, f"{r.amount:.2f}", r.email])
        logger.info("exported %d records to %s", len(records), dest)
        return dest

    def stream_valid(self, raw: str) -> Iterator[Record]:
        """Yield only records whose email contains '@' and amount >= 0."""
        for record in self.parse(raw):
            if "@" in record.email and record.amount >= 0:
                yield record

    def summarize(self, records: list[Record]) -> dict:
        total = sum(r.amount for r in records)
        return {
            "count": len(records),
            "total": round(total, 2),
            "avg": round(total / len(records), 2) if records else 0.0,
        }

    def find_by_id(self, records: list[Record], target: int) -> Optional[Record]:
        for record in records:
            if record.id == target:
                return record
        return None
