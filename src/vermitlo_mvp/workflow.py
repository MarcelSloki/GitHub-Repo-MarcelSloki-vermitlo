from __future__ import annotations

from .models import Approval, asdict_without_none
from .rules import (
    analyze_match,
    build_dossier,
    calculate_billing,
    record_learning,
    simulate_outcome,
    simulate_submission,
)
from .seed_loader import load_company_profile, load_tender
from .storage import WorkflowStore


def run_demo(approved: bool = True) -> dict:
    company = load_company_profile()
    tender = load_tender()
    match = analyze_match(company, tender)
    dossier = build_dossier(company, tender, match)
    approval = Approval(
        approved=approved,
        approver="Demo Approver" if approved else None,
        note="Synthetic approval for local MVP demo" if approved else "Approval intentionally withheld",
    )
    submission = simulate_submission(dossier, approval)
    outcome = simulate_outcome(submission, dossier)
    billing = calculate_billing(outcome)
    learning = record_learning(tender, match, outcome)

    return asdict_without_none(
        {
            "company": company,
            "tender": tender,
            "match": match,
            "dossier": dossier,
            "approval": approval,
            "submission": submission,
            "outcome": outcome,
            "billing": billing,
            "learning": learning,
        }
    )


def run_and_persist_demo(approved: bool = True, db_path: str | None = None) -> dict:
    result = run_demo(approved=approved)
    store = WorkflowStore(db_path) if db_path else WorkflowStore()
    run_id = store.save_workflow_run(result)
    return {"run_id": run_id, **result}
