# Vermitlo MVP Baseline

This document describes the first runnable Vermitlo MVP scaffold.

## Core Flow

The baseline makes this flow executable with synthetic demo data:

1. Load a company profile
2. Import a tender
3. Analyse requirements
4. Check match and K.O. criteria
5. Prepare pricing
6. Select verified references
7. Generate a bid dossier
8. Require human approval
9. Simulate submission
10. Simulate award outcome
11. Calculate commission trigger
12. Create test invoice and test payment status
13. Record learning signals

## Run Locally

```bash
python -m vermitlo_mvp.cli run-demo
python -m unittest discover -s tests
```

Optional local API:

```bash
python -m vermitlo_mvp.api
```

Endpoints:

- `GET /health`
- `GET /demo/run`

## Safety Boundaries

- No legally binding offer without explicit human approval.
- No invented references, certificates, revenue, employees, prices, or project experience.
- Missing or uncertain data must remain visible as missing, low-confidence, or assumed.
- Portal submission is simulated and flagged for manual or authorized adapter handling.
- Billing and payment are test/mock flows only.
- Customer data must remain separated and must not be reused for competitors.

## First Beachhead Assumption

The demo assumes a German mid-market IT and software services provider. The model is kept sector-neutral enough to support other B2B service providers later.

## Current Implementation

- `vermitlo_mvp/models.py`: domain objects
- `vermitlo_mvp/seeds.py`: synthetic demo company and tender
- `vermitlo_mvp/pipeline.py`: rule-based bid workflow
- `vermitlo_mvp/cli.py`: CLI demo runner
- `vermitlo_mvp/api.py`: tiny local HTTP API
- `tests/test_pipeline.py`: workflow safety tests
- `.github/workflows/ci.yml`: GitHub Actions test workflow

## Known Gaps

- Public tender source adapters are not implemented yet.
- Real submission portals are not automated.
- Pricing uses demo heuristics, not source-backed costing.
- Human approval is represented as a workflow state, not yet a UI/task system.
- Billing and payment are simulated only.

## Next Scaffold Step

Add persistence and auditability:

- SQLite schema or lightweight repository layer
- stable IDs for company, tender, dossier, approval, submission, outcome, invoice, and payment records
- event log for each workflow transition
- seed command that creates a complete demo workspace
