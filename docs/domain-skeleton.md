# Vermitlo domain skeleton

This is the first migration-ready persistence backbone for Stage 2. It extends the executable Python MVP core without replacing it.

## Scope

The migration in `migrations/0001_domain_skeleton.sql` defines five durable workflow entities:

1. `tenants`
2. `company_profiles`
3. `tenders`
4. `proposal_dossiers`
5. `approval_tasks`

These tables support the first believable product path:

`tenant -> company profile -> tender -> proposal dossier -> human approval`

Submission simulation, outcome simulation, and billing simulation remain downstream MVP logic. They are not persisted as production-grade events in this slice.

## Design choices

- Top-level workflow entities are normalized.
- Nested capabilities, references, evidence, requirements, generated sections, and source documents stay in JSONB for the first migration.
- Status values use text with check constraints, not database enums, so early iteration stays reversible.
- Every product artifact is tenant-scoped.
- The approval gate is explicit before submission simulation or later outcome work.

## Golden fixture

`fixtures/golden_path.json` contains one synthetic tenant, company profile, tender, proposal dossier, and approval task. It is designed to align with the existing demo workflow while making the future persisted path concrete.

## Deferred models

Do not add these until the five-table backbone is landed and exercised:

- `match_assessments`
- `outcome_events`
- `billing_events`

They should attach to `proposal_dossiers` later rather than changing the identity of company profiles or tenders.
