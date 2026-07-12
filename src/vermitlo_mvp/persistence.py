from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .seed_loader import load_company_profile, load_tender
from .workflow import run_demo


ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "migrations"
DEFAULT_TENANT_ID = "tenant-demo-it-001"
DEFAULT_TENANT_NAME = "Demo IT Services Tenant"


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def apply_migrations(db_path: str | Path, migrations_dir: Path = MIGRATIONS_DIR) -> None:
    with connect(db_path) as connection:
        for migration in sorted(migrations_dir.glob("*.sql")):
            connection.executescript(migration.read_text(encoding="utf-8"))


def seed_demo_data(
    db_path: str | Path,
    tenant_id: str = DEFAULT_TENANT_ID,
    tenant_name: str = DEFAULT_TENANT_NAME,
) -> dict[str, int | str]:
    company = load_company_profile()
    tender = load_tender()

    with connect(db_path) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO tenants (id, name) VALUES (?, ?)",
            (tenant_id, tenant_name),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO company_profiles (
              id, tenant_id, legal_name, country, industries_json,
              capabilities_json, certifications_json, max_contract_value_eur
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company.id,
                tenant_id,
                company.legal_name,
                company.country,
                _json(company.industries),
                _json(company.capabilities),
                _json(company.certifications),
                company.max_contract_value_eur,
            ),
        )
        connection.execute(
            "DELETE FROM reference_projects WHERE company_profile_id = ?",
            (company.id,),
        )
        connection.executemany(
            """
            INSERT INTO reference_projects (
              id, company_profile_id, title, industries_json, capabilities_json,
              contract_value_eur, evidence_source, evidence_quality, evidence_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    reference.id,
                    company.id,
                    reference.title,
                    _json(reference.industries),
                    _json(reference.capabilities),
                    reference.contract_value_eur,
                    reference.evidence.source,
                    reference.evidence.quality,
                    reference.evidence.note,
                )
                for reference in company.references
            ],
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO tenders (
              id, tenant_id, title, buyer, country, estimated_value_eur,
              source_url, deadline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tender.id,
                tenant_id,
                tender.title,
                tender.buyer,
                tender.country,
                tender.estimated_value_eur,
                tender.source_url,
                tender.deadline,
            ),
        )
        connection.execute("DELETE FROM tender_requirements WHERE tender_id = ?", (tender.id,))
        connection.executemany(
            """
            INSERT INTO tender_requirements (
              id, tender_id, requirement_text, category, mandatory, keywords_json,
              required_certification, min_contract_value_eur
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    requirement.id,
                    tender.id,
                    requirement.text,
                    requirement.category,
                    int(requirement.mandatory),
                    _json(requirement.keywords),
                    requirement.required_certification,
                    requirement.min_contract_value_eur,
                )
                for requirement in tender.requirements
            ],
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO audit_events (
              id, tenant_id, actor, action, entity_type, entity_id, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "audit-demo-seed-001",
                tenant_id,
                "system",
                "seed_demo_data",
                "tenant",
                tenant_id,
                _json({"company_id": company.id, "tender_id": tender.id}),
            ),
        )

    return {
        "tenant_id": tenant_id,
        "company_profiles": 1,
        "reference_projects": len(company.references),
        "tenders": 1,
        "tender_requirements": len(tender.requirements),
    }


def persist_demo_run(
    db_path: str | Path,
    approved: bool = True,
    tenant_id: str = DEFAULT_TENANT_ID,
) -> dict[str, str | int]:
    seed_demo_data(db_path, tenant_id=tenant_id)
    result = run_demo(approved=approved)

    company_id = result["company"]["id"]
    tender_id = result["tender"]["id"]
    match_id = f"match-{company_id}-{tender_id}"
    dossier_id = f"dossier-{company_id}-{tender_id}"
    approval_id = f"approval-{dossier_id}"
    submission_id = f"submission-{dossier_id}"
    outcome_id = f"outcome-{submission_id}"
    billing_id = f"billing-{outcome_id}"

    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO match_decisions (
              id, tenant_id, company_profile_id, tender_id, score, decision,
              ko_reasons_json, assessments_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                tenant_id,
                company_id,
                tender_id,
                result["match"]["score"],
                result["match"]["decision"],
                _json(result["match"].get("ko_reasons", [])),
                _json(result["match"].get("assessments", [])),
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO proposal_dossiers (
              id, tenant_id, match_decision_id, tender_id, company_profile_id,
              selected_reference_ids_json, pricing_json, missing_information_json,
              source_attribution_json, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dossier_id,
                tenant_id,
                match_id,
                tender_id,
                company_id,
                _json(result["dossier"].get("selected_reference_ids", [])),
                _json(result["dossier"]["pricing"]),
                _json(result["dossier"].get("missing_information", [])),
                _json(result["dossier"].get("source_attribution", [])),
                "approved" if approved else "approval_pending",
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO approvals (
              id, tenant_id, proposal_dossier_id, approved, approver, note
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                approval_id,
                tenant_id,
                dossier_id,
                int(result["approval"]["approved"]),
                result["approval"].get("approver"),
                result["approval"]["note"],
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO submission_simulations (
              id, tenant_id, proposal_dossier_id, approval_id, status, portal, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission_id,
                tenant_id,
                dossier_id,
                approval_id,
                result["submission"]["status"],
                result["submission"]["portal"],
                result["submission"]["message"],
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO outcome_simulations (
              id, tenant_id, submission_simulation_id, awarded, award_value_eur, reason
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                outcome_id,
                tenant_id,
                submission_id,
                int(result["outcome"]["awarded"]),
                result["outcome"]["award_value_eur"],
                result["outcome"]["reason"],
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO billing_events (
              id, tenant_id, outcome_simulation_id, commission_rate, commission_eur,
              invoice_status, payment_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                billing_id,
                tenant_id,
                outcome_id,
                result["billing"]["commission_rate"],
                result["billing"]["commission_eur"],
                result["billing"]["invoice_status"],
                result["billing"]["payment_status"],
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO audit_events (
              id, tenant_id, actor, action, entity_type, entity_id, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "audit-demo-run-001" if approved else "audit-demo-run-blocked-001",
                tenant_id,
                "system",
                "persist_demo_run",
                "proposal_dossier",
                dossier_id,
                _json({"approved": approved, "decision": result["match"]["decision"]}),
            ),
        )

    return {
        "tenant_id": tenant_id,
        "match_decision_id": match_id,
        "proposal_dossier_id": dossier_id,
        "submission_status": result["submission"]["status"],
        "commission_eur": result["billing"]["commission_eur"],
    }


def table_count(db_path: str | Path, table: str) -> int:
    if not table.replace("_", "").isalnum():
        raise ValueError("Invalid table name")
    with connect(db_path) as connection:
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
