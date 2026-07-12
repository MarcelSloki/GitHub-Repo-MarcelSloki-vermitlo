from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_REGISTRY_PATH = ROOT / "data" / "source_registry.json"


@dataclass(frozen=True)
class TenderSource:
    id: str
    name: str
    operator: str
    jurisdiction: str
    scope: str
    status: str
    access_url: str
    documentation_url: str
    adapter_status: str
    mvp_allowed_actions: list[str]
    mvp_forbidden_actions: list[str]
    notes: list[str]


def load_source_registry(path: Path | None = None) -> list[TenderSource]:
    payload = _read_json(path or SOURCE_REGISTRY_PATH)
    return [TenderSource(**item) for item in payload]


def get_first_adapter_candidate() -> TenderSource:
    registry = load_source_registry()
    for source in registry:
        if source.id == "doe-bekanntmachungsservice":
            return source
    raise LookupError("First German source adapter candidate is missing")


def source_allows(source: TenderSource, action: str) -> bool:
    return action in source.mvp_allowed_actions and action not in source.mvp_forbidden_actions


def _read_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
