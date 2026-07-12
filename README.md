# Vermitlo MVP

Vermitlo is a B2B SaaS MVP for tender discovery, qualification, offer dossier preparation, human approval, submission simulation, outcome tracking, commission billing, and learning from results.

This repository contains a small executable core that makes the end-to-end flow visible with synthetic demo data:

1. Load a company profile.
2. Import a public-tender-style opportunity.
3. Analyze requirements and hard K.O. criteria.
4. Calculate a transparent match score.
5. Stop blocked tenders before pricing, dossier finalization, submission, billing, or payment.
6. Prepare pricing only for viable bids.
7. Select eligible references from provided evidence.
8. Generate an offer dossier.
9. Require human approval before submission.
10. Simulate submission and award outcome.
11. Calculate success-based commission.
12. Simulate invoice and test payment.
13. Record a learning event from the outcome.

## Run locally

```bash
PYTHONPATH=src python -m vermitlo_mvp.demo
PYTHONPATH=src python -m vermitlo_mvp.demo --no-approval
PYTHONPATH=src python -m vermitlo_mvp.demo --no-go
PYTHONPATH=src python -m vermitlo_mvp.demo --no-go --db ./.local/vermitlo-demo.sqlite
```

For a tiny local HTTP API:

```bash
PYTHONPATH=src python -m vermitlo_mvp.server
```

Then call:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/demo/run -d '{"approved": true}' -H 'content-type: application/json'
curl -X POST http://127.0.0.1:8000/demo/run -d '{"approved": true, "no_go": true}' -H 'content-type: application/json'
curl -X POST http://127.0.0.1:8000/demo/run -d '{"approved": true, "no_go": true, "db_path": "./.local/vermitlo-demo.sqlite"}' -H 'content-type: application/json'
```

## Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## MVP boundaries

- No legally binding offer is submitted without explicit human approval.
- Real tender portal submission is intentionally represented as a mock adapter.
- Payment is a test simulation and never charges a real customer.
- Missing company evidence is surfaced as missing, not invented.
- Reference projects are only selected from the provided company profile.
- Hard K.O. criteria stop the flow before pricing, submission, billing, and payment.
- Optional SQLite persistence records demo runs and audit events locally.

## Default assumptions

- Beachhead market: German mid-market IT and software service providers.
- Tender source: public/open data style import with source attribution.
- Matching: explainable rule-based scoring before any AI-assisted layer.
- Billing: success-based commission simulation with auditable calculation inputs.
