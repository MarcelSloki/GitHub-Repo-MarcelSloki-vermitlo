-- Vermitlo Stage 2 Golden Path domain skeleton
-- This migration is the first persistence baseline after the web shell.
-- Outcome and billing records are explicitly simulated/test-only in this slice.

CREATE TABLE tenants (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  country_code text NOT NULL,
  tenant_status text NOT NULL DEFAULT 'demo_active',
  demo_mode boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (tenant_status IN ('demo_active', 'pilot_candidate', 'inactive'))
);

CREATE TABLE company_profiles (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  legal_name text NOT NULL,
  display_name text NOT NULL,
  summary text,
  headquarters_country text NOT NULL,
  employee_band text,
  website_url text,
  profile_status text NOT NULL DEFAULT 'draft',
  target_markets_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  capabilities_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  certifications_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  reference_projects_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  evidence_items_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  missing_evidence_flags_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (profile_status IN ('draft', 'evidence_ready', 'evidence_gaps', 'approved_for_demo'))
);

CREATE TABLE tenders (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  source_type text NOT NULL,
  source_name text NOT NULL,
  source_url text,
  external_reference text,
  title text NOT NULL,
  buyer_name text,
  country_code text NOT NULL,
  summary text,
  requirement_items_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  exclusion_criteria_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  source_documents_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  submission_deadline_at timestamptz,
  tender_status text NOT NULL DEFAULT 'seeded',
  imported_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (source_type IN ('seed', 'public_source', 'mock_adapter')),
  CHECK (tender_status IN ('seeded', 'imported', 'parsed', 'analysis_ready', 'archived'))
);

CREATE TABLE match_assessments (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  company_profile_id uuid NOT NULL REFERENCES company_profiles(id),
  tender_id uuid NOT NULL REFERENCES tenders(id),
  assessment_status text NOT NULL DEFAULT 'pending',
  score numeric,
  recommendation text NOT NULL DEFAULT 'pending',
  exclusion_hits_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  missing_evidence_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  rationale_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  assessed_at timestamptz,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (assessment_status IN ('pending', 'assessed', 'blocked_by_exclusion', 'missing_evidence', 'recommended_bid', 'recommended_no_bid')),
  CHECK (recommendation IN ('pending', 'bid', 'no_bid', 'needs_review')),
  CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);

CREATE TABLE proposal_dossiers (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  tender_id uuid NOT NULL REFERENCES tenders(id),
  company_profile_id uuid NOT NULL REFERENCES company_profiles(id),
  match_assessment_id uuid REFERENCES match_assessments(id),
  title text NOT NULL,
  dossier_status text NOT NULL DEFAULT 'not_started',
  qualification_summary text,
  draft_summary text,
  selected_references_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  selected_evidence_items_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  generated_sections_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  unresolved_gaps_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  export_notes_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  UNIQUE (tenant_id, tender_id, company_profile_id),
  CHECK (dossier_status IN ('not_started', 'drafting', 'draft_ready', 'blocked_missing_evidence', 'awaiting_approval', 'approved', 'rejected'))
);

CREATE TABLE approval_tasks (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  proposal_dossier_id uuid NOT NULL REFERENCES proposal_dossiers(id),
  approval_type text NOT NULL DEFAULT 'submission_review',
  approval_status text NOT NULL DEFAULT 'open',
  reviewer_name text,
  required_decision text NOT NULL DEFAULT 'approve_or_reject',
  comments text,
  requested_at timestamptz NOT NULL,
  decided_at timestamptz,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (approval_type IN ('submission_review', 'commercial_review', 'final_release')),
  CHECK (approval_status IN ('open', 'approved', 'rejected', 'changes_requested'))
);

CREATE TABLE outcome_events (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  proposal_dossier_id uuid NOT NULL REFERENCES proposal_dossiers(id),
  outcome_status text NOT NULL,
  event_type text NOT NULL,
  result_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  simulated boolean NOT NULL DEFAULT true,
  occurred_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (outcome_status IN ('submission_simulated', 'award_simulated_won', 'award_simulated_lost', 'cancelled')),
  CHECK (event_type IN ('submission', 'award_decision')),
  CHECK (simulated = true)
);

CREATE TABLE billing_events (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  outcome_event_id uuid NOT NULL REFERENCES outcome_events(id),
  billing_status text NOT NULL DEFAULT 'not_applicable',
  event_type text NOT NULL,
  amount numeric,
  currency text NOT NULL DEFAULT 'EUR',
  simulated boolean NOT NULL DEFAULT true,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  CHECK (billing_status IN ('not_applicable', 'commission_calculated_test', 'invoice_generated_test', 'payment_simulated', 'voided')),
  CHECK (event_type IN ('commission', 'invoice', 'payment')),
  CHECK (currency = 'EUR'),
  CHECK (simulated = true)
);

CREATE INDEX company_profiles_tenant_status_idx ON company_profiles (tenant_id, profile_status);
CREATE INDEX tenders_tenant_status_idx ON tenders (tenant_id, tender_status);
CREATE INDEX match_assessments_tender_idx ON match_assessments (tenant_id, tender_id);
CREATE INDEX match_assessments_company_idx ON match_assessments (tenant_id, company_profile_id);
CREATE INDEX proposal_dossiers_tender_idx ON proposal_dossiers (tenant_id, tender_id);
CREATE INDEX approval_tasks_dossier_idx ON approval_tasks (tenant_id, proposal_dossier_id);
CREATE INDEX outcome_events_dossier_idx ON outcome_events (tenant_id, proposal_dossier_id);
CREATE INDEX billing_events_outcome_idx ON billing_events (tenant_id, outcome_event_id);
