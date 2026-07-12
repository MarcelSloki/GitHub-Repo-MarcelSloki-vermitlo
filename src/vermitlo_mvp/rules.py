from __future__ import annotations

from .models import (
    Approval,
    BillingResult,
    CompanyProfile,
    Decision,
    LearningEvent,
    MatchResult,
    OfferDossier,
    OutcomeResult,
    PricingPlan,
    RequirementAssessment,
    SubmissionResult,
    SubmissionStatus,
    Tender,
)


def analyze_match(company: CompanyProfile, tender: Tender) -> MatchResult:
    assessments: list[RequirementAssessment] = []
    ko_reasons: list[str] = []
    warnings: list[str] = []

    for requirement in tender.requirements:
        score, status, explanation = assess_requirement(company, requirement)
        if requirement.mandatory and status == "missing":
            ko_reasons.append(f"No evidence for mandatory requirement: {requirement.text}")
        if status == "needs_clarification":
            warnings.append(explanation)
        assessments.append(
            RequirementAssessment(
                requirement_id=requirement.id,
                status=status,
                score=score,
                explanation=explanation,
            )
        )

    score = round(sum(item.score for item in assessments) / max(len(assessments), 1))
    if ko_reasons:
        decision = Decision.NO_BID
        recommendation = "no_bid"
    elif warnings:
        decision = Decision.BID
        recommendation = "bid_with_conditions"
    elif score >= 75:
        decision = Decision.BID
        recommendation = "bid"
    elif score >= 55:
        decision = Decision.REVIEW
        recommendation = "review"
    else:
        decision = Decision.NO_BID
        recommendation = "no_bid"

    return MatchResult(
        score=score,
        decision=decision,
        recommendation=recommendation,
        ko_reasons=ko_reasons,
        warnings=warnings,
        assessments=assessments,
    )


def assess_requirement(company: CompanyProfile, requirement) -> tuple[int, str, str]:
    if requirement.required_certification:
        if requirement.required_certification in company.certifications:
            return 100, "met", f"Certification present: {requirement.required_certification}"
        if requirement.mandatory:
            return 0, "missing", f"Missing mandatory certification: {requirement.required_certification}"
        return 40, "needs_clarification", (
            f"{requirement.required_certification} missing; clarify whether it is mandatory."
        )

    if requirement.min_references:
        matching_references = select_references(company, keywords=requirement.keywords, limit=requirement.min_references)
        if len(matching_references) >= requirement.min_references:
            return 100, "met", f"{len(matching_references)} matching source-backed references available"
        return 0, "missing", "Not enough source-backed matching references available"

    keyword_hits = sorted(set(requirement.keywords) & set(company.capabilities))
    if keyword_hits:
        if requirement.category == "delivery":
            return 80, "met", "Delivery capability match: " + ", ".join(keyword_hits)
        if requirement.category == "commercial":
            return 70, "draft_ready", "Pricing draft can be prepared from company defaults"
        return 100, "met", "Capability match: " + ", ".join(keyword_hits)

    if requirement.min_contract_value_eur:
        if company.max_contract_value_eur >= requirement.min_contract_value_eur:
            return 80, "met", "Company delivery capacity covers minimum value"
        return 0, "missing", "Contract value exceeds stated company delivery capacity"

    return 0, "missing", "No matching evidence found"


def prepare_pricing(company: CompanyProfile) -> PricingPlan:
    defaults = company.pricing_defaults
    base_price = defaults.person_days * defaults.day_rate_eur
    contingency = round(base_price * defaults.contingency_pct)
    return PricingPlan(
        person_days=defaults.person_days,
        day_rate_eur=defaults.day_rate_eur,
        base_price_eur=base_price,
        contingency_eur=contingency,
        total_price_eur=base_price + contingency,
        assumptions=[
            "Synthetic MVP pricing based on company demo defaults",
            "Final commercial offer requires human validation and source-backed calculation",
        ],
    )


def select_references(
    company: CompanyProfile,
    tender: Tender | None = None,
    keywords: list[str] | None = None,
    limit: int = 2,
) -> list[str]:
    tender_keywords = set(keywords or [])
    if tender:
        tender_keywords.update(
            keyword
            for requirement in tender.requirements
            for keyword in requirement.keywords
        )
    ranked = sorted(
        company.references,
        key=lambda reference: len(tender_keywords & set(reference.capabilities)),
        reverse=True,
    )
    return [
        reference.id
        for reference in ranked
        if tender_keywords & set(reference.capabilities)
    ][:limit]


def build_dossier(company: CompanyProfile, tender: Tender, match: MatchResult) -> OfferDossier:
    selected_references = select_references(company, tender=tender)
    missing_information: list[str] = []
    if not selected_references:
        missing_information.append("No source-backed reference project matches the tender capabilities")
    if match.ko_reasons:
        missing_information.extend(match.ko_reasons)
    missing_information.extend(match.warnings)

    return OfferDossier(
        id="dossier-demo-001",
        tender_id=tender.id,
        company_id=company.id,
        decision=match.decision,
        recommendation=match.recommendation,
        match_score=match.score,
        ko_reasons=match.ko_reasons,
        warnings=match.warnings,
        selected_reference_ids=selected_references,
        pricing=prepare_pricing(company),
        approval_required=True,
        missing_information=missing_information,
        source_attribution=[tender.source_url],
        sections=[
            "Executive Summary",
            "Bid-or-No-Bid-Begruendung",
            "Anforderungsmatrix",
            "K.O.-Kriterienstatus",
            "Referenzzuordnung",
            "Preisvorschlag",
            "Offene Klaerfragen",
            "Submission-Checkliste",
        ],
    )


def simulate_submission(dossier: OfferDossier, approval: Approval) -> SubmissionResult:
    if not approval.approved:
        return SubmissionResult(
            status=SubmissionStatus.BLOCKED_PENDING_APPROVAL,
            portal="mock-public-procurement-portal",
            message="Submission blocked: explicit human approval is required.",
            external_portal_called=False,
        )
    if dossier.decision == Decision.NO_BID:
        return SubmissionResult(
            status=SubmissionStatus.BLOCKED_PENDING_APPROVAL,
            portal="mock-public-procurement-portal",
            message="Submission blocked: bid/no-bid decision is no_bid.",
            external_portal_called=False,
        )
    return SubmissionResult(
        status=SubmissionStatus.SIMULATED_SUBMITTED,
        portal="mock-public-procurement-portal",
        message=f"Submission simulated for approver {approval.approver}. No external portal was called.",
        external_portal_called=False,
    )


def simulate_outcome(submission: SubmissionResult, dossier: OfferDossier) -> OutcomeResult:
    awarded = submission.status == SubmissionStatus.SIMULATED_SUBMITTED and dossier.match_score >= 75
    return OutcomeResult(
        awarded=awarded,
        award_value_eur=302000 if awarded else 0,
        reason=(
            "Fachlich geeignet, Preis im erwarteten Bereich, ISO 27001 nicht als harte Pflicht gewertet."
            if awarded
            else "Not awarded in demo simulation"
        ),
    )


def calculate_billing(outcome: OutcomeResult, commission_rate: float = 0.03) -> BillingResult:
    commission = round(outcome.award_value_eur * commission_rate) if outcome.awarded else 0
    return BillingResult(
        commission_rate=commission_rate,
        commission_eur=commission,
        invoice_id="INV-DEMO-2026-0001" if commission else None,
        invoice_status="sandbox_invoice_created" if commission else "not_billable",
        payment_status="sandbox_paid" if commission else "not_started",
        real_charge_created=False,
    )


def record_learning(tender: Tender, match: MatchResult, outcome: OutcomeResult) -> LearningEvent:
    notes = [
        f"Recommendation={match.recommendation}",
        f"Match score={match.score}",
        f"Awarded={outcome.awarded}",
        "Do not reuse confidential customer data for competitors.",
    ]
    if match.warnings:
        notes.extend(match.warnings)
    if match.ko_reasons:
        notes.extend(match.ko_reasons)
    return LearningEvent(tender_id=tender.id, signal="demo_outcome_recorded", notes=notes)
