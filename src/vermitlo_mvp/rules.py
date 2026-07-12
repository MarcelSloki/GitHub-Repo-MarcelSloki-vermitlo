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

    for requirement in tender.requirements:
        score = 0
        explanations: list[str] = []

        if requirement.required_certification:
            if requirement.required_certification in company.certifications:
                score += 100
                explanations.append(f"Certification present: {requirement.required_certification}")
            else:
                reason = f"Missing mandatory certification: {requirement.required_certification}"
                explanations.append(reason)
                if requirement.mandatory:
                    ko_reasons.append(reason)

        if requirement.min_contract_value_eur:
            if company.max_contract_value_eur >= requirement.min_contract_value_eur:
                score += 100
                explanations.append("Company contract capacity covers minimum value")
            else:
                reason = "Contract value exceeds stated company delivery capacity"
                explanations.append(reason)
                if requirement.mandatory:
                    ko_reasons.append(reason)

        keyword_hits = sorted(set(requirement.keywords) & set(company.capabilities))
        if keyword_hits:
            score += min(100, 30 * len(keyword_hits))
            explanations.append("Capability match: " + ", ".join(keyword_hits))
        elif requirement.mandatory and not requirement.required_certification and not requirement.min_contract_value_eur:
            reason = f"No evidence for mandatory requirement: {requirement.text}"
            explanations.append(reason)
            ko_reasons.append(reason)

        normalized_score = min(100, score)
        status = "met" if normalized_score >= 70 else "partial" if normalized_score > 0 else "missing"
        assessments.append(
            RequirementAssessment(
                requirement_id=requirement.id,
                status=status,
                score=normalized_score,
                explanation="; ".join(explanations) or "No matching evidence found",
            )
        )

    score = round(sum(item.score for item in assessments) / max(len(assessments), 1))
    if ko_reasons:
        decision = Decision.NO_BID
    elif score >= 75:
        decision = Decision.BID
    elif score >= 55:
        decision = Decision.REVIEW
    else:
        decision = Decision.NO_BID

    return MatchResult(score=score, decision=decision, ko_reasons=ko_reasons, assessments=assessments)


def prepare_pricing(tender: Tender, match: MatchResult) -> PricingPlan:
    contingency_rate = 0.12 if match.decision == Decision.BID else 0.18
    base_price = round(tender.estimated_value_eur * 0.82)
    contingency = round(base_price * contingency_rate)
    return PricingPlan(
        base_price_eur=base_price,
        contingency_eur=contingency,
        total_price_eur=base_price + contingency,
        assumptions=[
            "Synthetic MVP pricing based on estimated tender value",
            "Final commercial offer requires human validation and source-backed calculation",
        ],
    )


def select_references(company: CompanyProfile, tender: Tender, limit: int = 2) -> list[str]:
    tender_keywords = {
        keyword
        for requirement in tender.requirements
        for keyword in requirement.keywords
    }
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
    selected_references = [] if match.decision == Decision.NO_BID else select_references(company, tender)
    missing_information: list[str] = []
    if not selected_references and match.decision != Decision.NO_BID:
        missing_information.append("No source-backed reference project matches the tender capabilities")
    if match.ko_reasons:
        missing_information.extend(match.ko_reasons)

    return OfferDossier(
        tender_id=tender.id,
        company_id=company.id,
        decision=match.decision,
        match_score=match.score,
        ko_reasons=match.ko_reasons,
        selected_reference_ids=selected_references,
        pricing=None if match.decision == Decision.NO_BID else prepare_pricing(tender, match),
        approval_required=True,
        missing_information=missing_information,
        source_attribution=[tender.source_url],
    )


def simulate_submission(dossier: OfferDossier, approval: Approval) -> SubmissionResult:
    if not approval.approved:
        return SubmissionResult(
            status=SubmissionStatus.BLOCKED_PENDING_APPROVAL,
            portal="mock-public-procurement-portal",
            message="Submission blocked: explicit human approval is required.",
        )
    if dossier.decision == Decision.NO_BID:
        return SubmissionResult(
            status=SubmissionStatus.BLOCKED_PENDING_APPROVAL,
            portal="mock-public-procurement-portal",
            message="Submission blocked: bid/no-bid decision is no_bid.",
        )
    return SubmissionResult(
        status=SubmissionStatus.SIMULATED_SUBMITTED,
        portal="mock-public-procurement-portal",
        message=f"Submission simulated for approver {approval.approver}.",
    )


def simulate_outcome(submission: SubmissionResult, dossier: OfferDossier) -> OutcomeResult:
    awarded = submission.status == SubmissionStatus.SIMULATED_SUBMITTED and dossier.match_score >= 75
    award_value = dossier.pricing.total_price_eur if awarded and dossier.pricing else 0
    return OutcomeResult(
        awarded=awarded,
        award_value_eur=award_value,
        reason="High match score in demo simulation" if awarded else "Not awarded in demo simulation",
    )


def calculate_billing(outcome: OutcomeResult, commission_rate: float = 0.025) -> BillingResult:
    commission = round(outcome.award_value_eur * commission_rate) if outcome.awarded else 0
    return BillingResult(
        commission_rate=commission_rate,
        commission_eur=commission,
        invoice_status="test_invoice_created" if commission else "not_billable",
        payment_status="test_payment_succeeded" if commission else "not_started",
    )


def record_learning(tender: Tender, match: MatchResult, outcome: OutcomeResult) -> LearningEvent:
    notes = [
        f"Decision={match.decision.value}",
        f"Match score={match.score}",
        f"Awarded={outcome.awarded}",
    ]
    if match.ko_reasons:
        notes.extend(match.ko_reasons)
    return LearningEvent(tender_id=tender.id, signal="demo_outcome_recorded", notes=notes)
