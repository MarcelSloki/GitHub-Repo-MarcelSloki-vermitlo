from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "fixtures" / "golden_path.json"


class DomainFixtureError(ValueError):
    """Raised when a domain fixture does not satisfy the Stage 2 backbone."""


@dataclass(frozen=True)
class DomainFixture:
    tenant: dict[str, Any]
    company_profile: dict[str, Any]
    tender: dict[str, Any]
    proposal_dossier: dict[str, Any]
    approval_task: dict[str, Any]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "DomainFixture":
        required = ["tenant", "company_profile", "tender", "proposal_dossier", "approval_task"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise DomainFixtureError("Fixture missing required sections: " + ", ".join(missing))

        fixture = cls(
            tenant=payload["tenant"],
            company_profile=payload["company_profile"],
            tender=payload["tender"],
            proposal_dossier=payload["proposal_dossier"],
            approval_task=payload["approval_task"],
        )
        fixture.validate()
        return fixture

    def validate(self) -> None:
        tenant_id = self._require_id(self.tenant, "tenant")
        company_id = self._require_id(self.company_profile, "company_profile")
        tender_id = self._require_id(self.tender, "tender")
        dossier_id = self._require_id(self.proposal_dossier, "proposal_dossier")

        self._require_equal(self.company_profile, "tenant_id", tenant_id, "company_profile")
        self._require_equal(self.tender, "tenant_id", tenant_id, "tender")
        self._require_equal(self.proposal_dossier, "tenant_id", tenant_id, "proposal_dossier")
        self._require_equal(self.proposal_dossier, "company_profile_id", company_id, "proposal_dossier")
        self._require_equal(self.proposal_dossier, "tender_id", tender_id, "proposal_dossier")
        self._require_equal(self.approval_task, "tenant_id", tenant_id, "approval_task")
        self._require_equal(self.approval_task, "dossier_id", dossier_id, "approval_task")

        self._require_status(
            self.tenant,
            "workspace_status",
            {"active", "inactive", "archived"},
            "tenant",
        )
        self._require_status(
            self.company_profile,
            "profile_status",
            {"draft", "active", "archived"},
            "company_profile",
        )
        self._require_status(
            self.tender,
            "tender_status",
            {"imported", "reviewing", "qualified", "dossier_in_progress", "approval_pending", "closed"},
            "tender",
        )
        self._require_status(
            self.proposal_dossier,
            "dossier_status",
            {"draft", "review_ready", "awaiting_approval", "approved", "rework_required", "submission_simulated"},
            "proposal_dossier",
        )
        self._require_status(
            self.approval_task,
            "approval_status",
            {"pending", "approved", "rejected", "cancelled"},
            "approval_task",
        )

        self._validate_approval_decision()
        self._validate_non_binding_fixture()

    def as_records(self) -> dict[str, dict[str, Any]]:
        return {
            "tenant": self.tenant,
            "company_profile": self.company_profile,
            "tender": self.tender,
            "proposal_dossier": self.proposal_dossier,
            "approval_task": self.approval_task,
        }

    @staticmethod
    def _require_id(record: dict[str, Any], label: str) -> str:
        value = record.get("id")
        if not isinstance(value, str) or not value:
            raise DomainFixtureError(f"{label} must include a non-empty id")
        return value

    @staticmethod
    def _require_equal(record: dict[str, Any], key: str, expected: str, label: str) -> None:
        actual = record.get(key)
        if actual != expected:
            raise DomainFixtureError(f"{label}.{key} expected {expected!r}, got {actual!r}")

    @staticmethod
    def _require_status(record: dict[str, Any], key: str, allowed: set[str], label: str) -> None:
        actual = record.get(key)
        if actual not in allowed:
            raise DomainFixtureError(f"{label}.{key} has unsupported status {actual!r}")

    def _validate_approval_decision(self) -> None:
        status = self.approval_task["approval_status"]
        decided_at = self.approval_task.get("decided_at")
        if status == "pending" and decided_at is not None:
            raise DomainFixtureError("approval_task.decided_at must be empty while approval is pending")
        if status != "pending" and not decided_at:
            raise DomainFixtureError("approval_task.decided_at is required once approval is decided")

    def _validate_non_binding_fixture(self) -> None:
        serialized = json.dumps(self.as_records()).lower()
        if "synthetic" not in serialized:
            raise DomainFixtureError("fixture must clearly mark synthetic/demo content")
        export_notes = self.proposal_dossier.get("export_notes_json", [])
        joined_notes = " ".join(str(note) for note in export_notes).lower()
        if "no legally binding submission" not in joined_notes:
            raise DomainFixtureError("fixture must state that it creates no legally binding submission")


def load_domain_fixture(path: Path | str = DEFAULT_FIXTURE) -> DomainFixture:
    fixture_path = Path(path)
    with fixture_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return DomainFixture.from_mapping(payload)
