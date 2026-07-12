from __future__ import annotations

from .models import (
    BidDossier,
    CompanyProfile,
    PricingDraft,
    Reference,
    RequirementAnalysis,
    Tender,
    WorkflowResult,
)
from .seeds import demo_company, demo_tender


def analyse_requirements(company: CompanyProfile, tender: Tender) -> RequirementAnalysis:
    company_caps = set(company.capabilities)
    company_certs = set(company.certifications)
    required_caps = set(tender.required_capabilities)
    required_certs = set(tender.required_certifications)

    missing_capabilities = sorted(required_caps - company_caps)
    missing_certifications = sorted(required_certs - company_certs)
    knockout_failures = []

    if tender.contract_value_eur > company.max_contract_value_eur:
        knockout_failures.append("contract_value_above_company_limit")
    if missing_certifications:
        knockout_failures.append("missing_required_certification")

    return RequirementAnalysis(
        matched_capabilities=sorted(required_caps & company_caps),
        missing_capabilities=missing_capabilities,
        met_certifications=sorted(required_certs & company_certs),
        missing_certifications=missing_certifications,
        knockout_failures=knockout_failures,
    )


def prepare_pricing(company: CompanyProfile, tender: Tender, analysis: RequirementAnalysis) -> PricingDraft:
    complexity_factor = 1 + (0.08 * len(tender.required_capabilities))
    risk_factor = 1 + (0.12 * len(analysis.missing_capabilities))
    base_price = round(tender.contract_value_eur * 0.72 * complexity_factor * risk_factor)
    estimated_margin = max(company.min_margin_percent, 18.0 - (4.0 * len(analysis.missing_capabilities)))

    return PricingDraft(
        base_price_eur=base_price,
        estimated_margin_percent=estimated_margin,
        confidence="medium" if not analysis.knockout_failures else "low",
        assumptions=[
            "Demo pricing only; no legally binding offer.",
            "Final price requires human validation and source-backed cost inputs.",
        ],
    )


def select_references(company: CompanyProfile, tender: Tender) -> list[Reference]:
    required_caps = set(tender.required_capabilities)
    eligible = [
        ref
        for ref in company.references
        if ref.evidence_status == "verified" and required_caps.intersection(ref.capabilities)
    ]
    return eligible[:3]


def build_dossier(company: CompanyProfile, tender: Tender) -> BidDossier:
    analysis = analyse_requirements(company, tender)
    pricing = prepare_pricing(company, tender, analysis)
    references = select_references(company, tender)
    risk_flags = []

    if analysis.knockout_failures:
        risk_flags.append("hard_exclusion_criteria_detected")
    if not references:
        risk_flags.append("no_verified_reference_available")
    if tender.submission_mode == "portal":
        risk_flags.append("portal_submission_requires_manual_or_authorized_adapter")

    if analysis.knockout_failures:
        recommendation = "no_bid"
    elif risk_flags or analysis.missing_capabilities:
        recommendation = "needs_review"
    else:
        recommendation = "bid"

    return BidDossier(
        tender_title=tender.title,
        company_name=company.name,
        bid_recommendation=recommendation,
        analysis=analysis,
        pricing=pricing,
        selected_references=references,
        risk_flags=risk_flags,
    )


def run_workflow(company: CompanyProfile, tender: Tender) -> WorkflowResult:
    dossier = build_dossier(company, tender)
    approved = dossier.bid_recommendation in {"bid", "needs_review"} and not dossier.analysis.knockout_failures

    approval_status = "approved_for_simulation" if approved else "blocked"
    submission_status = "simulated" if approved else "not_submitted"
    outcome_status = "simulated_awarded" if approved else "not_available"
    invoice_status = "test_invoice_created" if outcome_status == "simulated_awarded" else "not_billable"
    payment_status = "test_payment_succeeded" if invoice_status == "test_invoice_created" else "not_started"

    learning_log = [
        f"recommendation={dossier.bid_recommendation}",
        f"matched_capabilities={len(dossier.analysis.matched_capabilities)}",
        f"missing_capabilities={len(dossier.analysis.missing_capabilities)}",
        f"risk_flags={len(dossier.risk_flags)}",
    ]

    return WorkflowResult(
        dossier=dossier,
        approval_status=approval_status,
        submission_status=submission_status,
        outcome_status=outcome_status,
        commission_invoice_status=invoice_status,
        payment_status=payment_status,
        learning_log=learning_log,
    )


def run_demo() -> WorkflowResult:
    return run_workflow(demo_company(), demo_tender())
