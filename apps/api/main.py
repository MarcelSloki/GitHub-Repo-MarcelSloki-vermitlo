from __future__ import annotations

from pathlib import Path
import sys

from fastapi import FastAPI
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vermitlo_mvp.workflow import run_demo


class DemoRunRequest(BaseModel):
    approved: bool = True


app = FastAPI(title="Vermitlo API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "vermitlo-api"}


@app.post("/demo/run")
def run_demo_flow(request: DemoRunRequest | None = None) -> dict:
    approved = True if request is None else request.approved
    return run_demo(approved=approved)
