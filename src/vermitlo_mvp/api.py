from __future__ import annotations

from .adapters import get_default_import_adapter
from .dossier_export import submission_package_payload
from .models import asdict_without_none
from .rules import analyze_match, build_dossier
from .seed_loader import load_company_profile
from .source_registry import get_first_adapter_candidate, load_source_registry
from .workflow import run_demo


def health_payload() -> dict:
    return {"status": "ok", "service": "vermitlo-mvp"}


def golden_flow_payload(approved: bool = True) -> dict:
    return run_demo(approved=approved)


def source_registry_payload() -> dict:
    return {
        "sources": asdict_without_none(load_source_registry()),
        "first_adapter_candidate": asdict_without_none(get_first_adapter_candidate()),
    }


def demo_import_payload(notice_id: str = "tender-demo-essen-2026-001") -> dict:
    result = get_default_import_adapter().import_notice(notice_id)
    return {"import": asdict_without_none(result)}


def demo_submission_package_payload() -> dict:
    imported = get_default_import_adapter().import_notice("tender-demo-essen-2026-001")
    company = load_company_profile()
    match = analyze_match(company, imported.tender)
    dossier = build_dossier(company, imported.tender, match)
    return {"submission_package": submission_package_payload(dossier)}
