-- Vermitlo MVP initial relational baseline
-- Dialect: SQLite-compatible SQL for local MVP development.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tenants (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS company_profiles (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  legal_name TEXT NOT NULL,
  country TEXT NOT NULL,
  industries_json TEXT NOT NULL DEFAULT '[]',
  capabilities_json TEXT NOT NULL DEFAULT '[]',
  certifications_json TEXT NOT NULL DEFAULT '[]',
  max_contract_value_eur INTEGER NOT NULL CHECK (max_contract_value_eur >= 0),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reference_projects (
  id TEXT PRIMARY KEY,
  company_profile_id TEXT NOT NULL REFERENCES company_profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  industries_json TEXT NOT NULL DEFAULT '[]',
  capabilities_json TEXT NOT NULL DEFAULT '[]',
  contract_value_eur INTEGER NOT NULL CHECK (contract_value_eur >= 0),
  evidence_source TEXT NOT NULL,
  evidence_quality TEXT NOT NULL,
  evidence_note TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenders (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  buyer TEXT NOT NULL,
  country TEXT NOT NULL,
  estimated_value_eur INTEGER NOT NULL CHECK (estimated_value_eur >= 0),
  source_url TEXT NOT NULL,
  deadline TEXT NOT NULL,
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tender_requirements (
  id TEXT PRIMARY KEY,
  tender_id TEXT NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
  requirement_text TEXT NOT NULL,
  category TEXT NOT NULL,
  mandatory INTEGER NOT NULL CHECK (mandatory IN (0, 1)),
  keywords_json TEXT NOT NULL DEFAULT '[]',
  required_certification TEXT,
  min_contract_value_eur INTEGER CHECK (min_contract_value_eur IS NULL OR min_contract_value_eur >= 0)
);

CREATE TABLE IF NOT EXISTS match_decisions (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
  tender_id TEXT NOT NULL REFERENCES tenders(id),
  score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  decision TEXT NOT NULL CHECK (decision IN ('bid', 'review', 'no_bid')),
  ko_reasons_json TEXT NOT NULL DEFAULT '[]',
  assessments_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proposal_dossiers (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  match_decision_id TEXT NOT NULL REFERENCES match_decisions(id),
  tender_id TEXT NOT NULL REFERENCES tenders(id),
  company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
  selected_reference_ids_json TEXT NOT NULL DEFAULT '[]',
  pricing_json TEXT NOT NULL,
  missing_information_json TEXT NOT NULL DEFAULT '[]',
  source_attribution_json TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL CHECK (status IN ('draft', 'approval_pending', 'approved', 'blocked', 'submitted_simulated')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  proposal_dossier_id TEXT NOT NULL REFERENCES proposal_dossiers(id),
  approved INTEGER NOT NULL CHECK (approved IN (0, 1)),
  approver TEXT,
  note TEXT NOT NULL,
  decided_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS submission_simulations (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  proposal_dossier_id TEXT NOT NULL REFERENCES proposal_dossiers(id),
  approval_id TEXT REFERENCES approvals(id),
  status TEXT NOT NULL CHECK (status IN ('blocked_pending_approval', 'simulated_submitted')),
  portal TEXT NOT NULL,
  message TEXT NOT NULL,
  simulated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outcome_simulations (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  submission_simulation_id TEXT NOT NULL REFERENCES submission_simulations(id),
  awarded INTEGER NOT NULL CHECK (awarded IN (0, 1)),
  award_value_eur INTEGER NOT NULL CHECK (award_value_eur >= 0),
  reason TEXT NOT NULL,
  simulated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS billing_events (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  outcome_simulation_id TEXT NOT NULL REFERENCES outcome_simulations(id),
  commission_rate REAL NOT NULL CHECK (commission_rate >= 0),
  commission_eur INTEGER NOT NULL CHECK (commission_eur >= 0),
  invoice_status TEXT NOT NULL,
  payment_status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_profiles_tenant ON company_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenders_tenant ON tenders(tenant_id);
CREATE INDEX IF NOT EXISTS idx_match_decisions_tenant_tender ON match_decisions(tenant_id, tender_id);
CREATE INDEX IF NOT EXISTS idx_proposal_dossiers_tenant_status ON proposal_dossiers(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_entity ON audit_events(tenant_id, entity_type, entity_id);
