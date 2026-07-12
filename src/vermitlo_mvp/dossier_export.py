from __future__ import annotations

from dataclasses import dataclass

from .models import OfferDossier, asdict_without_none


@dataclass(frozen=True)
class SubmissionPackage:
    id: str
    dossier_id: str
    status: str
    files: list[str]
    checks: list[str]
    open_questions: list[str]
    external_portal_called: bool
    legal_submission_allowed: bool


def build_submission_package(dossier: OfferDossier) -> SubmissionPackage:
    files = [
        "Angebotsdossier.pdf",
        "Preisblatt.xlsx",
        "Referenzanhang.pdf",
        "Eigenerklaerung-DSGVO-TOM.pdf",
        "Klaerfragenprotokoll.pdf",
    ]
    checks = [
        "Human approval is required before any real submission.",
        "Price draft is present but not legally binding.",
        "Selected references come from the company profile only.",
        "Payment and commission remain sandbox-only until a verified billing event exists.",
    ]
    return SubmissionPackage(
        id="submission-package-demo-001",
        dossier_id=dossier.id,
        status="draft_export_simulated",
        files=files,
        checks=checks,
        open_questions=dossier.missing_information,
        external_portal_called=False,
        legal_submission_allowed=False,
    )


def submission_package_payload(dossier: OfferDossier) -> dict:
    return asdict_without_none(build_submission_package(dossier))
