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


def initialize_demo_database(db_path: str | Path, approved: bool = True) -> dict[str, str | int]:
    apply_migrations(db_path)
    return persist_demo_run(db_path, approved=approved)


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


def get_tenant_overview(db_path: str | Path, tenant_id: str = DEFAULT_TENANT_ID) -> dict[str, Any]:
    with connect(db_path) as connection:
        tenant = connection.execute(
            "SELECT id, name, created_at FROM tenants WHERE id = ?",
            (tenant_id,),
        ).fetchone()
        if tenant is None:
            raise LookupError(f"Tenant not found: {tenant_id}")
        counts = {
            table: _count_for_tenant(connection, table, tenant_id)
            for table in (
                "company_profiles",
                "tenders",
                "match_decisions",
                "proposal_dossiers",
                "approvals",
                "submission_simulations",
                "billing_events",
                "audit_events",
            )
        }
    return {"id": tenant["id"], "name": tenant["name"], "created_at": tenant["created_at"], "counts": counts}


def get_company_profile_snapshot(db_path: str | Path, tenant_id: str = DEFAULT_TENANT_ID) -> dict[str, Any]:
    with connect(db_path) as connection:
        company = connection.execute(
            """
            SELECT * FROM company_profiles
            WHERE tenant_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()
        if company is None:
            raise LookupError(f"Company profile not found for tenant: {tenant_id}")
        references = connection.execute(
            """
            SELECT * FROM reference_projects
            WHERE company_profile_id = ?
            ORDER BY id
            """,
            (company["id"],),
        ).fetchall()
    return {
        "id": company["id"],
        "tenant_id": company["tenant_id"],
        "legal_name": company["legal_name"],
        "country": company["country"],
        "industries": _loads(company["industries_json"]),
        "capabilities": _loads(company["capabilities_json"]),
        "certifications": _loads(company["certifications_json"]),
        "max_contract_value_eur": company["max_contract_value_eur"],
        "references": [
            {
                "id": reference["id"],
                "title": reference["title"],
                "industries": _loads(reference["industries_json"]),
                "capabilities": _loads(reference["capabilities_json"]),
                "contract_value_eur": reference["contract_value_eur"],
                "evidence": {
                    "source": reference["evidence_source"],
                    "quality": reference["evidence_quality"],
                    "note": reference["evidence_note"],
                },
            }
            for reference in references
        ],
    }


def get_tender_snapshot(db_path: str | Path, tenant_id: str = DEFAULT_TENANT_ID) -> dict[str, Any]:
    with connect(db_path) as connection:
        tender = connection.execute(
            """
            SELECT * FROM tenders
            WHERE tenant_id = ?
            ORDER BY imported_at DESC
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()
        if tender is None:
            raise LookupError(f"Tender not found for tenant: {tenant_id}")
        requirements = connection.execute(
            """
            SELECT * FROM tender_requirements
            WHERE tender_id = ?
            ORDER BY id
            """,
            (tender["id"],),
        ).fetchall()
    return {
        "id": tender["id"],
        "tenant_id": tender["tenant_id"],
        "title": tender["title"],
        "buyer": tender["buyer"],
        "country": tender["country"],
        "estimated_value_eur": tender["estimated_value_eur"],
        "source_url": tender["source_url"],
        "deadline": tender["deadline"],
        "requirements": [
            {
                "id": requirement["id"],
                "text": requirement["requirement_text"],
                "category": requirement["category"],
                "mandatory": bool(requirement["mandatory"]),
                "keywords": _loads(requirement["keywords_json"]),
                "required_certification": requirement["required_certification"],
                "min_contract_value_eur": requirement["min_contract_value_eur"],
            }
            for requirement in requirements
        ],
    }


def get_latest_dossier_snapshot(db_path: str | Path, tenant_id: str = DEFAULT_TENANT_ID) -> dict[str, Any]:
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
              pd.id AS dossier_id,
              pd.status AS dossier_status,
              pd.selected_reference_ids_json,
              pd.pricing_json,
              pd.missing_information_json,
              pd.source_attribution_json,
              md.id AS match_decision_id,
              md.score,
              md.decision,
              md.ko_reasons_json,
              md.assessments_json,
              ss.status AS submission_status,
              ss.portal AS submission_portal,
              ss.message AS submission_message,
              os.awarded,
              os.award_value_eur,
              os.reason AS outcome_reason,
              be.commission_rate,
              be.commission_eur,
              be.invoice_status,
              be.payment_status
            FROM proposal_dossiers pd
            JOIN match_decisions md ON md.id = pd.match_decision_id
            LEFT JOIN submission_simulations ss ON ss.proposal_dossier_id = pd.id
            LEFT JOIN outcome_simulations os ON os.submission_simulation_id = ss.id
            LEFT JOIN billing_events be ON be.outcome_simulation_id = os.id
            WHERE pd.tenant_id = ?
            ORDER BY pd.created_at DESC
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()
        if row is None:
            raise LookupError(f"Proposal dossier not found for tenant: {tenant_id}")
    return {
        "id": row["dossier_id"],
        "status": row["dossier_status"],
        "match": {
            "id": row["match_decision_id"],
            "score": row["score"],
            "decision": row["decision"],
            "ko_reasons": _loads(row["ko_reasons_json"]),
            "assessments": _loads(row["assessments_json"]),
        },
        "selected_reference_ids": _loads(row["selected_reference_ids_json"]),
        "pricing": _loads(row["pricing_json"]),
        "missing_information": _loads(row["missing_information_json"]),
        "source_attribution": _loads(row["source_attribution_json"]),
        "submission": {
            "status": row["submission_status"],
            "portal": row["submission_portal"],
            "message": row["submission_message"],
        },
        "outcome": {
            "awarded": bool(row["awarded"]),
            "award_value_eur": row["award_value_eur"],
            "reason": row["outcome_reason"],
        },
        "billing": {
            "commission_rate": row["commission_rate"],
            "commission_eur": row["commission_eur"],
            "invoice_status": row["invoice_status"],
            "payment_status": row["payment_status"],
        },
    }


def table_count(db_path: str | Path, table: str) -> int:
    if not table.replace("_", "").isalnum():
        raise ValueError("Invalid table name")
    with connect(db_path) as connection:
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    return int(row["count"])


def _count_for_tenant(connection: sqlite3.Connection, table: str, tenant_id: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) AS count FROM {table} WHERE tenant_id = ?", (tenant_id,)).fetchone()
    return int(row["count"])


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None) -> Any:
    if value is None:
        return None
    return json.loads(value)
