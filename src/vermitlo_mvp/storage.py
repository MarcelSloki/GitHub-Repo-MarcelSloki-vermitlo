from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


DEFAULT_DB_PATH = Path("var/vermitlo_mvp.sqlite3")


SCHEMA = """
CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    tender_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    match_score INTEGER NOT NULL,
    submission_status TEXT NOT NULL,
    awarded INTEGER NOT NULL,
    commission_eur INTEGER NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES workflow_runs(id)
);
"""


class WorkflowStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_workflow_run(self, result: dict[str, Any]) -> str:
        run_id = str(uuid4())
        created_at = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO workflow_runs (
                    id, created_at, tender_id, company_id, decision, match_score,
                    submission_status, awarded, commission_eur, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    created_at,
                    result["tender"]["id"],
                    result["company"]["id"],
                    result["match"]["decision"],
                    result["match"]["score"],
                    result["submission"]["status"],
                    int(result["outcome"]["awarded"]),
                    result["billing"]["commission_eur"],
                    json.dumps(result, ensure_ascii=False, sort_keys=True),
                ),
            )
            for event_type, actor, summary, payload in _audit_events_for(result):
                connection.execute(
                    """
                    INSERT INTO audit_events (
                        run_id, created_at, event_type, actor, summary, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        created_at,
                        event_type,
                        actor,
                        summary,
                        json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    ),
                )
        return run_id

    def get_workflow_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM workflow_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                return None
            events = connection.execute(
                "SELECT event_type, actor, summary, payload_json FROM audit_events WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "tender_id": row["tender_id"],
            "company_id": row["company_id"],
            "decision": row["decision"],
            "match_score": row["match_score"],
            "submission_status": row["submission_status"],
            "awarded": bool(row["awarded"]),
            "commission_eur": row["commission_eur"],
            "payload": json.loads(row["payload_json"]),
            "audit_events": [
                {
                    "event_type": event["event_type"],
                    "actor": event["actor"],
                    "summary": event["summary"],
                    "payload": json.loads(event["payload_json"]),
                }
                for event in events
            ],
        }

    def list_workflow_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, tender_id, company_id, decision, match_score,
                       submission_status, awarded, commission_eur
                FROM workflow_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "tender_id": row["tender_id"],
                "company_id": row["company_id"],
                "decision": row["decision"],
                "match_score": row["match_score"],
                "submission_status": row["submission_status"],
                "awarded": bool(row["awarded"]),
                "commission_eur": row["commission_eur"],
            }
            for row in rows
        ]

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection


def _audit_events_for(result: dict[str, Any]) -> list[tuple[str, str, str, dict[str, Any]]]:
    return [
        (
            "tender_imported",
            "system",
            f"Imported tender {result['tender']['id']} from attributed source.",
            {"source_url": result["tender"]["source_url"]},
        ),
        (
            "requirements_scored",
            "rules-engine",
            f"Calculated match score {result['match']['score']} with decision {result['match']['decision']}.",
            {"assessments": result["match"]["assessments"], "ko_reasons": result["match"]["ko_reasons"]},
        ),
        (
            "dossier_prepared",
            "system",
            "Prepared non-binding offer dossier for human review.",
            {"approval_required": result["dossier"]["approval_required"]},
        ),
        (
            "approval_recorded",
            result["approval"].get("approver") or "human-approval-missing",
            "Recorded approval status before submission simulation.",
            result["approval"],
        ),
        (
            "submission_simulated",
            "mock-submission-adapter",
            result["submission"]["message"],
            result["submission"],
        ),
        (
            "billing_simulated",
            "mock-billing-adapter",
            f"Commission result: {result['billing']['commission_eur']} EUR.",
            result["billing"],
        ),
        (
            "learning_recorded",
            "system",
            "Stored outcome learning signal.",
            result["learning"],
        ),
    ]


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
