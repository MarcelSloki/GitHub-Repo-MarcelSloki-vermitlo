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

## Run locally

### Python demo mode

Use this to execute the synthetic workflow directly:

```bash
PYTHONPATH=src python -m vermitlo_mvp.demo
```

### Python server mode

Use this to run the current lightweight HTTP server around the MVP core:

```bash
PYTHONPATH=src python -m vermitlo_mvp.server
```

Then open `http://127.0.0.1:8000/health` or post to `http://127.0.0.1:8000/demo/run`.

### Shared local UI + backend mode

Use this mode when you want to run the first visible product shell together with the current executable MVP core:

```bash
docker compose up
```

Then open:

- `http://127.0.0.1:3000` for the web shell
- `http://127.0.0.1:8000/health` for the backend health endpoint
- `http://127.0.0.1:8000/demo/run` for the current demo server path

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
- The web shell is an early product shell, not the final marketing website.
- Schema, migrations, and deeper app structure come later.

## Default assumptions

- Target customer: tender-active small, medium-sized, and larger companies in Germany, including organizations with recurring public-tender work or an internal bid/tender team.
- Example segments can include IT and software service providers, manufacturers, industrial suppliers, business service firms, specialist contractors, and other tender-active B2B organizations.
- Tender source: public/open data style import with source attribution.
- Matching: explainable rule-based scoring before any AI-assisted layer.
- Billing: success-based commission simulation with auditable calculation inputs.
