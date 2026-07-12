from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = ROOT / "migrations" / "0001_initial.sql"

CORE_TABLES = [
    "tenants",
    "company_profiles",
    "company_capabilities",
    "company_certifications",
    "company_references",
    "tenders",
    "tender_documents",
    "tender_requirements",
    "knockout_criteria",
    "match_evaluations",
    "requirement_assessments",
    "pricing_drafts",
    "proposal_dossiers",
    "approval_tasks",
    "submission_simulations",
    "outcome_simulations",
    "billing_events",
    "invoices",
    "payment_simulations",
    "audit_log_entries",
]


def load_initial_migration() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")
