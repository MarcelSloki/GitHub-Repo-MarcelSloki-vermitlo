# Technical Architecture and Data Model Plan

Status: 2026-07-12
Current baseline: dependency-free Python MVP core with local demo runner, tiny HTTP server, synthetic seed data, rule-based match logic, submission simulation, billing simulation, and unittest coverage.

## Zielarchitektur

Start with a modular monolith. This keeps the MVP locally runnable and easy to test while making later service extraction possible.

## Runtime Layers

- Interface layer: CLI demo and minimal HTTP API first; later React or server-rendered operational UI.
- Application layer: workflow orchestration for tender import, requirement analysis, match, dossier, approval, submission simulation, outcome, billing, and learning.
- Domain layer: company profile, tender, requirement, assessment, dossier, approval, outcome, billing, audit event.
- Adapter layer: source import, document storage, dossier rendering, payment provider, and submission provider.
- Persistence layer: JSON seeds now; PostgreSQL in the next backend increment.

## Adapter Boundaries

- `TenderSourceAdapter`: Bekanntmachungsservice/TED/OCDS/eForms/CSV/demo seeds.
- `DocumentAdapter`: customer-uploaded documents with hash, source, access basis, and extraction status.
- `DossierRenderer`: Markdown/JSON now; DOCX/PDF later.
- `SubmissionProvider`: mock checklist now; assisted/manual integration later.
- `BillingProvider`: test invoice now; Stripe sandbox or EN 16931-compatible invoice path later.
- `AuditLogger`: append-only log for source, rule, decision, approval, and billing events.

## Datenmodell-Grundgeruest

### organizations

Customer tenant and legal entity.

Fields: `id`, `legal_name`, `country`, `industry_focus`, `created_at`.

### company_profiles

Tender-fit profile for a tenant.

Fields: `id`, `organization_id`, `capabilities`, `certifications`, `regions`, `max_contract_value_eur`, `min_margin_percent`, `hard_no_go_rules`, `updated_at`.

### references

Source-backed reference projects.

Fields: `id`, `organization_id`, `title`, `industries`, `capabilities`, `contract_value_eur`, `evidence_source`, `verified`, `approved_for_reuse`.

### tenders

Normalized notice record.

Fields: `id`, `source`, `source_url`, `title`, `buyer`, `country`, `region`, `cpv_codes`, `estimated_value_eur`, `deadline`, `raw_payload_json`, `created_at`.

### tender_documents

Documents and parsed artifacts.

Fields: `id`, `tender_id`, `filename`, `source_url`, `content_hash`, `storage_uri`, `processing_status`, `access_basis`.

### requirements

Machine-readable requirements with evidence.

Fields: `id`, `tender_id`, `text`, `category`, `mandatory`, `keywords`, `required_certification`, `min_contract_value_eur`, `evidence_locator`, `confidence`.

### match_scores

Decision support output.

Fields: `id`, `tender_id`, `company_profile_id`, `score`, `decision`, `ko_reasons`, `rule_version`, `created_at`.

### dossiers

Offer preparation artifact.

Fields: `id`, `tender_id`, `company_profile_id`, `match_score_id`, `pricing_case_id`, `status`, `missing_information`, `source_attribution`, `created_at`.

### approvals

Human approval gate.

Fields: `id`, `dossier_id`, `approved`, `approver`, `note`, `approved_at`.

### submissions

Simulation or assisted submission state.

Fields: `id`, `dossier_id`, `provider`, `status`, `message`, `submitted_at`.

### outcomes

Award/loss tracking.

Fields: `id`, `tender_id`, `status`, `award_value_eur`, `reason`, `recorded_at`.

### commission_events

Success-fee calculation basis.

Fields: `id`, `outcome_id`, `rate`, `commission_eur`, `billable`, `reason`, `created_at`.

### invoices

Test invoice now, production invoice later.

Fields: `id`, `commission_event_id`, `status`, `invoice_number`, `amount_eur`, `provider`, `created_at`.

### audit_events

Append-only compliance history.

Fields: `id`, `tenant_id`, `actor`, `action`, `subject_type`, `subject_id`, `payload_json`, `created_at`.

## Immediate Refactor Direction

1. Keep the current domain objects and rules as the executable core.
2. Add an `AuditEvent` model and write events during `run_demo`.
3. Split seed loading into a generic source adapter interface.
4. Add a second tender seed that demonstrates a K.O.-blocked no-bid flow.
5. Add persistence after the audit model is stable.
