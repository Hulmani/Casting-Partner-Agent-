import json
import sqlite3
from dataclasses import asdict
from typing import Iterable
from .models import Opportunity


class OpportunityStore:
    """Fictional-data foundation; real-data encryption is not implemented."""

    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS opportunities (
                source_id TEXT NOT NULL,
                external_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (source_id, external_id)
            );
            CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY,
                source_id TEXT NOT NULL,
                external_id TEXT NOT NULL,
                payload TEXT NOT NULL
            );
        """)

    def ingest(self, opportunities: Iterable[Opportunity]):
        counts = {"created": 0, "updated": 0, "unchanged": 0}
        with self.connection:
            for opportunity in opportunities:
                payload = json.dumps(asdict(opportunity), sort_keys=True)
                key = (opportunity.source_id, opportunity.external_id)
                row = self.connection.execute(
                    "SELECT payload FROM opportunities WHERE source_id=? AND external_id=?", key
                ).fetchone()
                if row:
                    previous = json.loads(row[0])
                    current = json.loads(payload)
                    previous.pop("observed_at")
                    current.pop("observed_at")
                    if previous == current:
                        counts["unchanged"] += 1
                        continue
                counts["updated" if row else "created"] += 1
                self.connection.execute(
                    "INSERT INTO opportunities VALUES (?, ?, ?) "
                    "ON CONFLICT(source_id, external_id) DO UPDATE SET payload=excluded.payload",
                    (*key, payload),
                )
                self.connection.execute("INSERT INTO revisions(source_id, external_id, payload) VALUES (?, ?, ?)", (*key, payload))
        return counts

    def list_opportunities(self):
        rows = self.connection.execute("SELECT payload FROM opportunities ORDER BY source_id, external_id")
        return [json.loads(row[0]) for row in rows]

    def close(self):
        self.connection.close()
