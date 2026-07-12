from __future__ import annotations

from .models import Approval, asdict_without_none
from .adapters import get_default_import_adapter
from .rules import (
    analyze_match,
    build_dossier,
    calculate_billing,
    record_learning,
    simulate_outcome,
    simulate_submission,
)
from .seed_loader import load_company_profile


def run_demo(approved: bool = True) -> dict:
    company = load_company_profile()
    imported = get_default_import_adapter().import_notice("tender-demo-essen-2026-001")
    tender = imported.tender
    match = analyze_match(company, tender)
    dossier = build_dossier(company, tender, match)
    approval = Approval(
        approved=approved,
        approver="Demo Approver" if approved else None,
        note=(
            "Approved with condition: clarify ISO 27001 before real submission"
            if approved
            else "Approval intentionally withheld"
        ),
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
            "import": imported,
            "audit_log": [
                "company_profile.created",
                "tender.imported",
                "tender.requirements_analyzed",
                "match.evaluated",
                "pricing.draft_created",
                "references.selected",
                "dossier.generated",
                "approval.completed",
                "submission.simulated",
                "outcome.simulated",
                "billing.success_fee_calculated",
                "payment.sandbox_completed",
                "learning.event_recorded",
            ],
            "boundaries": {
                "source": "synthetic_golden_demo",
                "submission": "sandbox_only",
                "payment": "sandbox_only",
                "legal_submission_allowed": False,
            },
        }
    )
