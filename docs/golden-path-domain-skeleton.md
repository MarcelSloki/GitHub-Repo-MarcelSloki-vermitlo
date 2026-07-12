# Golden Path Domain Skeleton

## Purpose

This document defines the corrected Stage 2 post-shell domain skeleton for Vermitlo.

It supersedes the earlier five-table backbone direction. The first migration-ready skeleton now includes the full Golden Path from tenant setup through simulated billing, while preserving explicit simulation boundaries.

## Stage fit

Active stage: Stage 2 - build one believable product path.

The existing Python core in `src/vermitlo_mvp` remains the canonical product core. This skeleton adds the persistence and workflow-state backbone around it.

## Golden Path

Company profile -> tender -> requirement analysis -> match and exclusion check -> dossier preparation -> human approval -> submission simulation -> outcome simulation -> billing/payment simulation -> audit trail.

## Entities

The first migration-ready skeleton includes exactly these eight entities:

1. `tenants`
2. `company_profiles`
3. `tenders`
4. `match_assessments`
5. `proposal_dossiers`
6. `approval_tasks`
7. `outcome_events`
8. `billing_events`

## Capability truth

### Real in this slice

- Domain entities and relationships
- Synthetic company profile and tender fixtures
- Rule-based match and exclusion representation
- Dossier structure using available evidence
- Human approval state
- Audit/status fields that separate real outputs from simulations

### Simulated in this slice

- Submission
- Award outcome
- Success-fee calculation
- Test invoice
- Test payment

### Mocked in this slice

- Tender source ingestion when no real source adapter is connected
- External portal behavior
- Payment provider behavior
- Any customer-specific documents or private evidence

### Later, not now

- Live portal submission
- Digital signature or authorization workflows
- Real payment collection
- Production invoicing
- Multi-source live ingestion at scale
- Advanced user roles and enterprise permissions
- Production legal/compliance assurances

## Guardrails

- No legally binding submission is modeled.
- `outcome_events.simulated` must remain true in this slice.
- `billing_events.simulated` must remain true in this slice.
- Missing evidence remains visible and must not be converted into invented evidence.
- K.O. criteria remain separate from ordinary scoring.
- Billing events are test records only and do not create real invoices or charges.

## Fixtures

This slice includes two fixture paths:

- `fixtures/golden_path_it_services_demo.json`: successful guided demo path.
- `fixtures/blocked_missing_evidence_demo.json`: negative guardrail path that blocks downstream simulation.

## Tests

The minimum tests verify:

- all eight tables are present in the migration
- the Golden Path fixture links from tenant through billing event
- OutcomeEvent and BillingEvent are forced to simulated/test status
- the blocked fixture does not create outcome or billing records
- missing evidence remains explicit
