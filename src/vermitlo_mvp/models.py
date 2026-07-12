from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Decision(StrEnum):
    BID = "bid"
    REVIEW = "review"
    NO_BID = "no_bid"


class SubmissionStatus(StrEnum):
    BLOCKED_PENDING_APPROVAL = "blocked_pending_approval"
    SIMULATED_SUBMITTED = "simulated_submitted"


@dataclass(frozen=True)
class Evidence:
    source: str
    quality: str
    note: str


@dataclass(frozen=True)
class ReferenceProject:
    id: str
    title: str
    industries: list[str]
    capabilities: list[str]
    contract_value_eur: int
    evidence: Evidence


@dataclass(frozen=True)
class PricingDefaults:
    person_days: int
    day_rate_eur: int
    contingency_pct: float
    success_fee_pct: float


@dataclass(frozen=True)
class CompanyProfile:
    id: str
    legal_name: str
    country: str
    location: str
    company_size: str
    industries: list[str]
    capabilities: list[str]
    certifications: list[str]
    max_contract_value_eur: int
    pricing_defaults: PricingDefaults
    references: list[ReferenceProject] = field(default_factory=list)


@dataclass(frozen=True)
class TenderRequirement:
    id: str
    text: str
    category: str
    mandatory: bool
    keywords: list[str]
    required_certification: str | None = None
    min_contract_value_eur: int | None = None
    min_references: int | None = None


@dataclass(frozen=True)
class KnockoutCriterion:
    id: str
    text: str
    severity: str
    status: str
    note: str | None = None


@dataclass(frozen=True)
class Tender:
    id: str
    title: str
    buyer: str
    country: str
    delivery_location: str
    estimated_value_eur: int
    source_type: str
    source_url: str
    deadline: str
    documents: list[str]
    requirements: list[TenderRequirement]
    knockout_criteria: list[KnockoutCriterion]


@dataclass(frozen=True)
class RequirementAssessment:
    requirement_id: str
    status: str
    score: int
    explanation: str


@dataclass(frozen=True)
class MatchResult:
    score: int
    decision: Decision
    recommendation: str
    ko_reasons: list[str]
    warnings: list[str]
    assessments: list[RequirementAssessment]


@dataclass(frozen=True)
class PricingPlan:
    person_days: int
    day_rate_eur: int
    base_price_eur: int
    contingency_eur: int
    total_price_eur: int
    assumptions: list[str]


@dataclass(frozen=True)
class OfferDossier:
    id: str
    tender_id: str
    company_id: str
    decision: Decision
    recommendation: str
    match_score: int
    ko_reasons: list[str]
    warnings: list[str]
    selected_reference_ids: list[str]
    pricing: PricingPlan
    approval_required: bool
    missing_information: list[str]
    source_attribution: list[str]
    sections: list[str]


@dataclass(frozen=True)
class Approval:
    approved: bool
    approver: str | None
    note: str


@dataclass(frozen=True)
class SubmissionResult:
    status: SubmissionStatus
    portal: str
    message: str
    external_portal_called: bool


@dataclass(frozen=True)
class OutcomeResult:
    awarded: bool
    award_value_eur: int
    reason: str


@dataclass(frozen=True)
class BillingResult:
    commission_rate: float
    commission_eur: int
    invoice_id: str | None
    invoice_status: str
    payment_status: str
    real_charge_created: bool


@dataclass(frozen=True)
class LearningEvent:
    tender_id: str
    signal: str
    notes: list[str]


def asdict_without_none(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: asdict_without_none(getattr(value, key))
            for key in value.__dataclass_fields__
            if getattr(value, key) is not None
        }
    if isinstance(value, list):
        return [asdict_without_none(item) for item in value]
    if isinstance(value, dict):
        return {key: asdict_without_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, StrEnum):
        return value.value
    return value
