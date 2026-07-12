# Vermitlo MVP

Vermitlo is a B2B SaaS MVP for tender discovery, qualification, offer dossier preparation, human approval, submission simulation, outcome tracking, commission billing, and learning from results.

This repository contains the first synthetic **Golden Demo Flow** for a German mid-market IT service provider:

1. Load the RheinMain Digital GmbH company profile.
2. Import a mock public tender from Stadt Essen.
3. Analyze requirements and hard K.O. criteria.
4. Calculate an explainable match score of `78/100`.
5. Prepare pricing from demo company defaults.
6. Select two eligible references.
7. Generate an offer dossier.
8. Require human approval before submission.
9. Simulate submission and award outcome.
10. Calculate a 3 percent success-based commission.
11. Simulate invoice and sandbox payment.
12. Record a learning event from the outcome.

## Run locally

```bash
PYTHONPATH=src python -m vermitlo_mvp.demo
```

For a tiny local HTTP API:

```bash
PYTHONPATH=src python -m vermitlo_mvp.server
```

Then open `http://127.0.0.1:8000/health`, `http://127.0.0.1:8000/demo/golden-flow`, or post to `http://127.0.0.1:8000/demo/run`.

## Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Persistence baseline

The first migration-ready schema is in `migrations/0001_initial.sql`.
It covers tenants, company profiles, tenders, requirements, K.O. criteria,
match evaluations, pricing drafts, dossiers, approvals, submission simulations,
outcome simulations, billing, invoices, payment simulations, and audit log
entries.

## Source registry

The first official-source registry is in `data/source_registry.json`.
It marks TED API and Germany's Datenservice Oeffentlicher Einkauf /
Bekanntmachungsservice as candidate discovery sources, while keeping bid
submission, notice publication, restricted document access, and portal-rule
bypass explicitly forbidden for the MVP.

The first adapter stub is `BekanntmachungsserviceMockAdapter`. It uses the
German Bekanntmachungsservice registry entry but deliberately imports the local
Golden Flow tender fixture only. It performs no live HTTP request and exposes
its allowed and forbidden actions for tests and UI badges.

## MVP boundaries

- No legally binding offer is submitted without explicit human approval.
- Real tender portal submission is intentionally represented as a mock adapter.
- Payment is a sandbox simulation and never charges a real customer.
- Missing company evidence is surfaced as missing, not invented.
- Reference projects are only selected from the provided company profile.
- ISO 27001 is intentionally missing in the demo company profile and remains a visible clarification point.

## Default assumptions

- Beachhead market: German mid-market IT and software service providers.
- Tender source: public/open-data-style import with source attribution.
- Matching: explainable rule-based scoring before any AI-assisted layer.
- Billing: success-based commission simulation with auditable calculation inputs.
