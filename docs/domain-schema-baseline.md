# Vermitlo domain schema baseline

## Purpose

This baseline turns the current in-memory Python MVP flow into a migration-ready relational model. It is scoped to the active Stage 2 goal: one believable product path from company profile and tender import through match, dossier, human approval, simulated submission, simulated outcome, billing simulation, and learning event.

## Current repository fit

The repository already contains a lightweight executable Python demo. This schema keeps that shape intact and adds the persistence boundary needed before broader UI, API, or source-adapter work.

## Primary entities

- `tenants`: customer isolation boundary for future multi-tenant operation.
- `company_profiles`: buyer-facing supplier profile used for matching and dossier generation.
- `company_industries`, `company_capabilities`, `company_certifications`: normalized profile facts with evidence status where relevant.
- `reference_projects`: approved or demo reference evidence. Dossier generation must only select from these records.
- `tenders`: source-attributed imported opportunities.
- `tender_requirements`: extracted requirements, including mandatory criteria, certifications, capacity thresholds, and keywords.
- `match_runs`: explainable bid/no-bid scoring result for one company and one tender.
- `requirement_assessments`: per-requirement scoring explanations.
- `proposal_dossiers`: prepared offer dossier draft with pricing assumptions, missing information, and source attribution.
- `approval_tasks`: human approval state. Real submission is blocked unless approval is explicit.
- `submission_simulations`: mock submission outcome, never a real portal submission.
- `outcome_simulations`: simulated award result used for demo and billing flow.
- `billing_events`: success-fee, test invoice, and test payment state.
- `learning_events`: structured outcome signal for later improvement.
- `audit_events`: tenant-scoped activity log for traceability.

## Safety boundaries represented in the schema

- Tenant-owned records are scoped by `tenant_id`.
- Submission is represented as `submission_simulations`, not real submission.
- Approval is explicit and modeled separately from dossier creation.
- Reference projects must exist before a dossier can cite them.
- Billing stores test invoice/payment state only.
- Evidence fields distinguish demo data from source-backed or verified data.

## Assumptions

- First persistence target is SQLite because the current MVP has no runtime dependencies.
- JSON fields are stored as text for now to keep the migration dependency-free.
- UUID generation is left to the application layer in this increment.
- Timestamps use database defaults and can be hardened later.
- The first official tender source adapter is still open and remains outside this migration.

## Next implementation step

Add a tiny persistence adapter that:

1. Creates an in-memory SQLite database from `migrations/0001_core_domain.sql`.
2. Loads the current synthetic company and tender fixtures into the relational schema.
3. Persists one demo run into `match_runs`, `proposal_dossiers`, `approval_tasks`, `submission_simulations`, `outcome_simulations`, `billing_events`, `learning_events`, and `audit_events`.
4. Adds a test that the demo path writes the expected records without inventing missing evidence.
