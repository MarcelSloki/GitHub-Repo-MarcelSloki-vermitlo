from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


class AuditStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS demo_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    tender_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    match_score INTEGER NOT NULL,
                    approved INTEGER NOT NULL,
                    submission_status TEXT NOT NULL,
                    awarded INTEGER NOT NULL,
                    invoice_status TEXT NOT NULL,
                    payment_status TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    sequence INTEGER NOT NULL,
                    step TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES demo_runs(id)
                )
                """
            )
            connection.execute(
                "INSERT OR REPLACE INTO schema_meta(key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )

    def save_demo_run(self, result: dict[str, Any]) -> int:
        self.initialize()
        created_at = datetime.now(UTC).isoformat(timespec="seconds")
        tender = result["tender"]
        match = result["match"]
        approval = result["approval"]
        submission = result["submission"]
        outcome = result["outcome"]
        billing = result["billing"]

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO demo_runs (
                    created_at,
                    tender_id,
                    decision,
                    match_score,
                    approved,
                    submission_status,
                    awarded,
                    invoice_status,
                    payment_status,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    tender["id"],
                    match["decision"],
                    int(match["score"]),
                    int(bool(approval["approved"])),
                    submission["status"],
                    int(bool(outcome["awarded"])),
                    billing["invoice_status"],
                    billing["payment_status"],
                    json.dumps(result, ensure_ascii=False, sort_keys=True),
                ),
            )
            run_id = int(cursor.lastrowid)
            self._insert_audit_events(connection, run_id, result)
            return run_id

    def list_runs(self) -> list[dict[str, Any]]:
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    created_at,
                    tender_id,
                    decision,
                    match_score,
                    approved,
                    submission_status,
                    awarded,
                    invoice_status,
                    payment_status
                FROM demo_runs
                ORDER BY id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_run(self, run_id: int) -> dict[str, Any] | None:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM demo_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["payload_json"])

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _insert_audit_events(
        self,
        connection: sqlite3.Connection,
        run_id: int,
        result: dict[str, Any],
    ) -> None:
        events = [
            ("tender_import", "ok", f"Loaded tender {result['tender']['id']}"),
            (
                "match",
                result["match"]["decision"],
                f"Score {result['match']['score']} with {len(result['match']['ko_reasons'])} K.O. reason(s)",
            ),
            (
                "dossier",
                "prepared" if result["dossier"].get("pricing") else "blocked_no_pricing",
                "Draft dossier state persisted with source attribution",
            ),
            (
                "approval",
                "approved" if result["approval"]["approved"] else "blocked",
                result["approval"]["note"],
            ),
            (
                "submission",
                result["submission"]["status"],
                result["submission"]["message"],
            ),
            (
                "billing",
                result["billing"]["invoice_status"],
                f"Payment status {result['billing']['payment_status']}",
            ),
            (
                "learning",
                result["learning"]["signal"],
                "; ".join(result["learning"]["notes"]),
            ),
        ]
        connection.executemany(
            """
            INSERT INTO audit_events(run_id, sequence, step, status, detail)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (run_id, sequence, step, status, detail)
                for sequence, (step, status, detail) in enumerate(events, start=1)
            ],
        )
