from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    CompanyProfile,
    Evidence,
    KnockoutCriterion,
    PricingDefaults,
    ReferenceProject,
    Tender,
    TenderRequirement,
)


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_company_profile(path: Path | None = None) -> CompanyProfile:
    payload = _read_json(path or DATA_DIR / "company_profile.json")
    references = [
        ReferenceProject(
            evidence=Evidence(**item["evidence"]),
            **{key: value for key, value in item.items() if key != "evidence"},
        )
        for item in payload.get("references", [])
    ]
    return CompanyProfile(
        references=references,
        pricing_defaults=PricingDefaults(**payload["pricing_defaults"]),
        **{key: value for key, value in payload.items() if key not in {"references", "pricing_defaults"}},
    )


def load_tender(path: Path | None = None) -> Tender:
    payload = _read_json(path or DATA_DIR / "tender.json")
    requirements = [TenderRequirement(**item) for item in payload["requirements"]]
    knockout_criteria = [KnockoutCriterion(**item) for item in payload["knockout_criteria"]]
    return Tender(
        requirements=requirements,
        knockout_criteria=knockout_criteria,
        **{key: value for key, value in payload.items() if key not in {"requirements", "knockout_criteria"}},
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
