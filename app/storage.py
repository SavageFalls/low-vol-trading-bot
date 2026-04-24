from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterable


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_ts TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    score REAL NOT NULL,
                    thesis TEXT NOT NULL,
                    report_path TEXT NOT NULL
                )
                """
            )

    def save_ideas(self, run_ts: str, ideas: Iterable[Dict], report_path: str):
        with self._conn() as conn:
            conn.executemany(
                """
                INSERT INTO ideas (run_ts, ticker, rating, confidence, score, thesis, report_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_ts,
                        idea["ticker"],
                        idea["rating"],
                        idea["confidence"],
                        idea["score"],
                        idea["thesis"],
                        report_path,
                    )
                    for idea in ideas
                ],
            )
