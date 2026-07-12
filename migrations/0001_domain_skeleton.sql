-- Vermitlo Stage 2 domain skeleton.
-- This migration defines the first durable backbone for the MVP path:
-- tenant -> company profile -> tender -> proposal dossier -> approval task.
-- It intentionally keeps nested evidence, requirement, and generated-section
-- structures in JSONB until the workflow proves which parts need normalization.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  country_code text NOT NULL,
  workspace_status text NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT tenants_workspace_status_check
    CHECK (workspace_status IN ('active', 'inactive', 'archived'))
);

CREATE TABLE company_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  legal_name text NOT NULL,
  display_name text NOT NULL,
  summary text,
  headquarters_country text NOT NULL,
  employee_band text,
  website_url text,
  profile_status text NOT NULL DEFAULT 'draft',
  capabilities_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  certifications_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  industries_served_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  reference_projects_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  evidence_items_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT company_profiles_profile_status_check
    CHECK (profile_status IN ('draft', 'active', 'archived')),
  CONSTRAINT company_profiles_capabilities_json_array_check
    CHECK (jsonb_typeof(capabilities_json) = 'array'),
  CONSTRAINT company_profiles_certifications_json_array_check
    CHECK (jsonb_typeof(certifications_json) = 'array'),
  CONSTRAINT company_profiles_industries_served_json_array_check
    CHECK (jsonb_typeof(industries_served_json) = 'array'),
  CONSTRAINT company_profiles_reference_projects_json_array_check
    CHECK (jsonb_typeof(reference_projects_json) = 'array'),
  CONSTRAINT company_profiles_evidence_items_json_array_check
    CHECK (jsonb_typeof(evidence_items_json) = 'array')
);

CREATE INDEX company_profiles_tenant_status_idx
  ON company_profiles (tenant_id, profile_status);

CREATE TABLE tenders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id),
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
  tender_status text NOT NULL DEFAULT 'imported',
  imported_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT tenders_tender_status_check
    CHECK (tender_status IN (
      'imported',
      'reviewing',
      'qualified',
      'dossier_in_progress',
      'approval_pending',
      'closed'
    )),
  CONSTRAINT tenders_requirement_items_json_array_check
    CHECK (jsonb_typeof(requirement_items_json) = 'array'),
  CONSTRAINT tenders_exclusion_criteria_json_array_check
    CHECK (jsonb_typeof(exclusion_criteria_json) = 'array'),
  CONSTRAINT tenders_source_documents_json_array_check
    CHECK (jsonb_typeof(source_documents_json) = 'array')
);

CREATE INDEX tenders_tenant_status_idx
  ON tenders (tenant_id, tender_status);

CREATE INDEX tenders_tenant_deadline_idx
  ON tenders (tenant_id, submission_deadline_at);

CREATE UNIQUE INDEX tenders_tenant_source_reference_uidx
  ON tenders (tenant_id, source_name, external_reference)
  WHERE external_reference IS NOT NULL;

CREATE TABLE proposal_dossiers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  tender_id uuid NOT NULL REFERENCES tenders(id),
  company_profile_id uuid NOT NULL REFERENCES company_profiles(id),
  title text NOT NULL,
  dossier_status text NOT NULL DEFAULT 'draft',
  qualification_summary text,
  draft_summary text,
  selected_references_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  selected_evidence_items_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  generated_sections_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  open_questions_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  export_notes_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposal_dossiers_dossier_status_check
    CHECK (dossier_status IN (
      'draft',
      'review_ready',
      'awaiting_approval',
      'approved',
      'rework_required',
      'submission_simulated'
    )),
  CONSTRAINT proposal_dossiers_selected_references_json_array_check
    CHECK (jsonb_typeof(selected_references_json) = 'array'),
  CONSTRAINT proposal_dossiers_selected_evidence_items_json_array_check
    CHECK (jsonb_typeof(selected_evidence_items_json) = 'array'),
  CONSTRAINT proposal_dossiers_generated_sections_json_array_check
    CHECK (jsonb_typeof(generated_sections_json) = 'array'),
  CONSTRAINT proposal_dossiers_open_questions_json_array_check
    CHECK (jsonb_typeof(open_questions_json) = 'array'),
  CONSTRAINT proposal_dossiers_export_notes_json_array_check
    CHECK (jsonb_typeof(export_notes_json) = 'array')
);

CREATE INDEX proposal_dossiers_tenant_status_idx
  ON proposal_dossiers (tenant_id, dossier_status);

CREATE INDEX proposal_dossiers_tenant_tender_idx
  ON proposal_dossiers (tenant_id, tender_id);

CREATE UNIQUE INDEX proposal_dossiers_tenant_tender_profile_uidx
  ON proposal_dossiers (tenant_id, tender_id, company_profile_id);

CREATE TABLE approval_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  dossier_id uuid NOT NULL REFERENCES proposal_dossiers(id),
  approval_type text NOT NULL DEFAULT 'submission_review',
  approval_status text NOT NULL DEFAULT 'pending',
  requested_at timestamptz NOT NULL DEFAULT now(),
  decided_at timestamptz,
  approver_name text,
  decision_note text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT approval_tasks_approval_type_check
    CHECK (approval_type IN ('submission_review', 'commercial_review', 'final_release')),
  CONSTRAINT approval_tasks_approval_status_check
    CHECK (approval_status IN ('pending', 'approved', 'rejected', 'cancelled')),
  CONSTRAINT approval_tasks_decision_fields_check
    CHECK (
      (approval_status = 'pending' AND decided_at IS NULL)
      OR (approval_status <> 'pending' AND decided_at IS NOT NULL)
    )
);

CREATE INDEX approval_tasks_tenant_status_idx
  ON approval_tasks (tenant_id, approval_status);

CREATE INDEX approval_tasks_tenant_dossier_idx
  ON approval_tasks (tenant_id, dossier_id);
