from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from app.models import DailyResearchReport


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    benchmark TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def save_report(self, report: DailyResearchReport) -> int:
        payload = json.dumps(report.to_dict())
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO reports (created_at, benchmark, payload_json) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), report.benchmark, payload),
            )
            return int(cur.lastrowid)
