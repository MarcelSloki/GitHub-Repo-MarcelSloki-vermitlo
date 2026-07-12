# Initial Domain Model

This document describes the first migration-ready relational baseline for the Vermitlo Stage 2 MVP.

## Scope

The baseline supports one auditable golden path:

1. Tenant exists as the customer data boundary.
2. Company profile stores capabilities, certifications, delivery capacity, and approved reference evidence.
3. Tender stores source-attributed opportunity data and requirements.
4. Match decision stores explainable scoring, K.O. reasons, and requirement assessments.
5. Proposal dossier stores selected references, pricing assumptions, missing information, and source attribution.
6. Approval records explicit human decision before any submission simulation.
7. Submission, outcome, and billing remain simulations.
8. Audit events provide a future append-only trace for important workflow actions.

## Design choices

- The first SQL file is SQLite-compatible so local MVP development can start without a managed database.
- Multi-value fields are stored as JSON text in the baseline to keep the first schema small and reversible.
- `tenant_id` appears on workflow tables to preserve customer-data separation from the first persistence step.
- Submission, outcome, invoice, and payment are represented as simulation tables, not production integrations.
- Approval is modeled separately from dossiers so a dossier cannot imply permission by existing.

## Safety boundaries

- No table represents a legally binding submission to a real tender portal.
- Reference evidence is stored as source/quality/note metadata and must come from approved company input.
- Billing events require an outcome simulation in this MVP baseline; real payment execution remains out of scope.
- Audit metadata must not be used to mix data across tenants.

## Next implementation step

Add a small SQLite repository layer and seed loader that maps the existing `data/company_profile.json` and `data/tender.json` into this schema. Then expose read-only API endpoints for the golden demo objects before adding write workflows.
