# Vermitlo MVP

Vermitlo is a B2B SaaS MVP for tender discovery, qualification, offer dossier preparation, human approval, submission simulation, outcome tracking, commission billing, and learning from results.

This repository starts with a small executable core that makes the end-to-end flow visible with synthetic demo data:

1. Load a company profile.
2. Import a public-tender-style opportunity.
3. Analyze requirements and hard K.O. criteria.
4. Calculate a transparent match score.
5. Prepare pricing.
6. Select eligible references.
7. Generate an offer dossier.
8. Require human approval before submission.
9. Simulate submission and award outcome.
10. Calculate success-based commission.
11. Simulate invoice and test payment.
12. Record a learning event from the outcome.

## Repository structure

- `src/vermitlo_mvp`: canonical Python MVP core for workflow, rules, models, seeds, and the tiny HTTP server.
- `apps/web`: first Next.js product shell around the existing core.
- `docker-compose.yml`: shared local runtime for the web shell and Python core server.
- `tests`: focused unit tests for workflow and runtime boundaries.

## Run locally

Python demo mode:

```bash
PYTHONPATH=src python -m vermitlo_mvp.demo
```

Python server mode:

```bash
PYTHONPATH=src python -m vermitlo_mvp.server
```

Then open `http://127.0.0.1:8000/health`, `http://127.0.0.1:8000/demo/overview`, or post to `http://127.0.0.1:8000/demo/run`.

Shared UI and backend mode:

```bash
docker compose up --build
```

Then open:

- Web shell: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- Backend overview: `http://localhost:8000/demo/overview`

The compose setup keeps `src/vermitlo_mvp` as the backend source of truth. It only adds a visible product shell and shared local startup path around the existing executable core.

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
- The web app is an early Stage 2 product shell, not the final marketing website.

## Default assumptions

- Target customers: small, medium-sized, and larger companies in Germany with recurring tender or bid work.
- Tender source: public/open data style import with source attribution.
- Matching: explainable rule-based scoring before any AI-assisted layer.
- Billing: success-based commission simulation with auditable calculation inputs.
- Live portal submissions, production payments, authentication, tenancy, migrations, and broader source ingestion come in later slices.
