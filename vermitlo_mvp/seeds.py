from __future__ import annotations

from .models import CompanyProfile, Reference, Tender


def demo_company() -> CompanyProfile:
    return CompanyProfile(
        name="DemoSoft Mittelstand GmbH",
        industries=["IT services", "software development"],
        capabilities=[
            "requirements_analysis",
            "web_application_development",
            "api_integration",
            "accessibility_testing",
            "cloud_operations",
        ],
        certifications=["ISO 27001"],
        references=[
            Reference(
                title="Citizen portal modernization",
                sector="public_sector",
                capabilities=["web_application_development", "accessibility_testing"],
                evidence_status="verified",
            ),
            Reference(
                title="API integration for regional utility",
                sector="utilities",
                capabilities=["api_integration", "cloud_operations"],
                evidence_status="verified",
            ),
            Reference(
                title="Unverified CRM relaunch",
                sector="private_sector",
                capabilities=["web_application_development"],
                evidence_status="missing_evidence",
            ),
        ],
        max_contract_value_eur=850_000,
        min_margin_percent=15.0,
    )


def demo_tender() -> Tender:
    return Tender(
        title="Relaunch kommunales Serviceportal",
        buyer="Stadt Beispielheim",
        source_url="https://example.invalid/tenders/kommunales-serviceportal",
        contract_value_eur=420_000,
        required_capabilities=[
            "requirements_analysis",
            "web_application_development",
            "accessibility_testing",
            "api_integration",
        ],
        knockout_criteria=[
            "ISO 27001 or equivalent information security management",
            "At least one verified public-sector reference",
        ],
        required_certifications=["ISO 27001"],
        submission_mode="portal",
    )
