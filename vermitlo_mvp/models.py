from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class CompanyProfile:
    name: str
    industries: list[str]
    capabilities: list[str]
    certifications: list[str]
    references: list["Reference"]
    max_contract_value_eur: int
    min_margin_percent: float


@dataclass(frozen=True)
class Reference:
    title: str
    sector: str
    capabilities: list[str]
    evidence_status: Literal["verified", "missing_evidence"]


@dataclass(frozen=True)
class Tender:
    title: str
    buyer: str
    source_url: str
    contract_value_eur: int
    required_capabilities: list[str]
    knockout_criteria: list[str]
    required_certifications: list[str]
    submission_mode: Literal["portal", "email", "mock"]


@dataclass(frozen=True)
class RequirementAnalysis:
    matched_capabilities: list[str]
    missing_capabilities: list[str]
    met_certifications: list[str]
    missing_certifications: list[str]
    knockout_failures: list[str]


@dataclass(frozen=True)
class PricingDraft:
    base_price_eur: int
    estimated_margin_percent: float
    confidence: Literal["low", "medium", "high"]
    assumptions: list[str]


@dataclass(frozen=True)
class BidDossier:
    tender_title: str
    company_name: str
    bid_recommendation: Literal["bid", "no_bid", "needs_review"]
    analysis: RequirementAnalysis
    pricing: PricingDraft
    selected_references: list[Reference]
    risk_flags: list[str]
    approval_required: bool = True


@dataclass(frozen=True)
class WorkflowResult:
    dossier: BidDossier
    approval_status: Literal["approved_for_simulation", "blocked"]
    submission_status: Literal["simulated", "not_submitted"]
    outcome_status: Literal["simulated_awarded", "simulated_lost", "not_available"]
    commission_invoice_status: Literal["test_invoice_created", "not_billable"]
    payment_status: Literal["test_payment_succeeded", "not_started"]
    learning_log: list[str] = field(default_factory=list)
