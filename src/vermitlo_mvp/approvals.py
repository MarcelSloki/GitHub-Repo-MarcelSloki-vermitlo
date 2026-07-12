from __future__ import annotations

from dataclasses import dataclass

from .models import Approval, OfferDossier, asdict_without_none


@dataclass(frozen=True)
class ApprovalDecision:
    id: str
    dossier_id: str
    role: str
    decision: str
    approver: str | None
    conditions: list[str]
    blockers: list[str]
    legal_submission_allowed: bool
    audit_event: str


def decide_approval(dossier: OfferDossier, approved: bool = True) -> ApprovalDecision:
    conditions = list(dossier.warnings)
    blockers: list[str] = []
    if not approved:
        blockers.append("Human approval was intentionally withheld.")
    if dossier.ko_reasons:
        blockers.extend(dossier.ko_reasons)

    decision = "approved_with_conditions" if approved and not blockers else "blocked"
    return ApprovalDecision(
        id="approval-demo-001",
        dossier_id=dossier.id,
        role="commercial_approver",
        decision=decision,
        approver="Demo Approver" if approved else None,
        conditions=conditions,
        blockers=blockers,
        legal_submission_allowed=False,
        audit_event="approval.completed" if approved else "approval.blocked",
    )


def approval_to_submission_input(approval: ApprovalDecision) -> Approval:
    return Approval(
        approved=approval.decision == "approved_with_conditions",
        approver=approval.approver,
        note=(
            "; ".join(approval.conditions)
            if approval.conditions
            else "Approved for sandbox submission simulation"
        )
        if approval.decision == "approved_with_conditions"
        else "; ".join(approval.blockers),
    )


def approval_payload(approval: ApprovalDecision) -> dict:
    return asdict_without_none(approval)
