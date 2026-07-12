from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import Tender
from .seed_loader import load_tender
from .source_registry import TenderSource, get_first_adapter_candidate, source_allows


class TenderImportAdapter(Protocol):
    source: TenderSource

    def import_notice(self, notice_id: str) -> "TenderImportResult":
        ...


@dataclass(frozen=True)
class TenderImportResult:
    tender: Tender
    source_id: str
    notice_id: str
    mode: str
    external_request_performed: bool
    allowed_actions: list[str]
    forbidden_actions: list[str]
    warnings: list[str]


class BekanntmachungsserviceMockAdapter:
    """MVP adapter stub for the German central notice service.

    This deliberately loads the Golden Flow tender fixture instead of calling a
    live endpoint. The interface is shaped like a future source adapter, while
    keeping Stage 2 safe from brittle scraping or unauthorized portal actions.
    """

    def __init__(self, source: TenderSource | None = None) -> None:
        self.source = source or get_first_adapter_candidate()

    def import_notice(self, notice_id: str) -> TenderImportResult:
        if not source_allows(self.source, "retrieve_notices"):
            raise PermissionError(f"Source {self.source.id} does not allow notice retrieval in the MVP")

        tender = load_tender()
        return TenderImportResult(
            tender=tender,
            source_id=self.source.id,
            notice_id=notice_id,
            mode="fixture_only",
            external_request_performed=False,
            allowed_actions=self.source.mvp_allowed_actions,
            forbidden_actions=self.source.mvp_forbidden_actions,
            warnings=[
                "Adapter is a Stage 2 stub and performs no live HTTP request.",
                "Do not submit bids or download restricted documents through this adapter.",
            ],
        )


def get_default_import_adapter() -> TenderImportAdapter:
    return BekanntmachungsserviceMockAdapter()
