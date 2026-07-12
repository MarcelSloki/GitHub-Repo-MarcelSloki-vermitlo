from __future__ import annotations

import os
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vermitlo_mvp.persistence import (
    DEFAULT_TENANT_ID,
    apply_migrations,
    get_company_profile_snapshot,
    get_latest_dossier_snapshot,
    get_tenant_overview,
    get_tender_snapshot,
    persist_demo_run,
)
from vermitlo_mvp.workflow import run_demo


class DemoRunRequest(BaseModel):
    approved: bool = True


app = FastAPI(title="Vermitlo API", version="0.1.0")


def _db_path() -> Path:
    return Path(os.environ.get("VERMITLO_DB_PATH", ROOT / "var" / "vermitlo.sqlite3"))


def _ensure_demo_database(approved: bool = True) -> None:
    db_path = _db_path()
    apply_migrations(db_path)
    persist_demo_run(db_path, approved=approved)


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(error))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "vermitlo-api"}


@app.post("/demo/run")
def run_demo_flow(request: DemoRunRequest | None = None) -> dict:
    approved = True if request is None else request.approved
    return run_demo(approved=approved)


@app.post("/demo/persist")
def persist_demo_flow(request: DemoRunRequest | None = None) -> dict:
    approved = True if request is None else request.approved
    _ensure_demo_database(approved=approved)
    return get_latest_dossier_snapshot(_db_path())


@app.get("/tenants/{tenant_id}")
def tenant_overview(tenant_id: str) -> dict:
    _ensure_demo_database()
    try:
        return get_tenant_overview(_db_path(), tenant_id=tenant_id)
    except LookupError as error:
        raise _not_found(error) from error


@app.get("/company-profile")
def company_profile() -> dict:
    _ensure_demo_database()
    try:
        return get_company_profile_snapshot(_db_path(), tenant_id=DEFAULT_TENANT_ID)
    except LookupError as error:
        raise _not_found(error) from error


@app.get("/tender")
def tender() -> dict:
    _ensure_demo_database()
    try:
        return get_tender_snapshot(_db_path(), tenant_id=DEFAULT_TENANT_ID)
    except LookupError as error:
        raise _not_found(error) from error


@app.get("/dossier/latest")
def latest_dossier() -> dict:
    _ensure_demo_database()
    try:
        return get_latest_dossier_snapshot(_db_path(), tenant_id=DEFAULT_TENANT_ID)
    except LookupError as error:
        raise _not_found(error) from error
