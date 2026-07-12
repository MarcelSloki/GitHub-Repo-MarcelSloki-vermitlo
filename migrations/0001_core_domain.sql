-- Vermitlo MVP core relational baseline.
-- Target runtime for this first increment: SQLite-compatible SQL with
-- portable table boundaries for a later Postgres migration.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'DE',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS company_profiles (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    legal_name TEXT NOT NULL,
    country TEXT NOT NULL,
    max_contract_value_eur INTEGER NOT NULL CHECK (max_contract_value_eur >= 0),
    data_quality TEXT NOT NULL DEFAULT 'demo' CHECK (data_quality IN ('demo', 'source_backed', 'verified')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS company_industries (
    company_profile_id TEXT NOT NULL,
    industry TEXT NOT NULL,
    PRIMARY KEY (company_profile_id, industry),
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS company_capabilities (
    company_profile_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    evidence_status TEXT NOT NULL DEFAULT 'declared' CHECK (evidence_status IN ('declared', 'source_backed', 'missing')),
    PRIMARY KEY (company_profile_id, capability),
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS company_certifications (
    company_profile_id TEXT NOT NULL,
    certification TEXT NOT NULL,
    evidence_status TEXT NOT NULL DEFAULT 'declared' CHECK (evidence_status IN ('declared', 'source_backed', 'missing')),
    PRIMARY KEY (company_profile_id, certification),
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reference_projects (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    company_profile_id TEXT NOT NULL,
    title TEXT NOT NULL,
    contract_value_eur INTEGER NOT NULL CHECK (contract_value_eur >= 0),
    evidence_source TEXT NOT NULL,
    evidence_quality TEXT NOT NULL CHECK (evidence_quality IN ('demo', 'source_backed', 'verified')),
    evidence_note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reference_project_industries (
    reference_project_id TEXT NOT NULL,
    industry TEXT NOT NULL,
    PRIMARY KEY (reference_project_id, industry),
    FOREIGN KEY (reference_project_id) REFERENCES reference_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reference_project_capabilities (
    reference_project_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    PRIMARY KEY (reference_project_id, capability),
    FOREIGN KEY (reference_project_id) REFERENCES reference_projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tenders (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    title TEXT NOT NULL,
    buyer TEXT NOT NULL,
    country TEXT NOT NULL,
    estimated_value_eur INTEGER NOT NULL CHECK (estimated_value_eur >= 0),
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'public_open_data',
    deadline TEXT NOT NULL,
    import_status TEXT NOT NULL DEFAULT 'imported' CHECK (import_status IN ('imported', 'analyzed', 'archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tender_requirements (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL,
    text TEXT NOT NULL,
    category TEXT NOT NULL,
    mandatory INTEGER NOT NULL CHECK (mandatory IN (0, 1)),
    required_certification TEXT,
    min_contract_value_eur INTEGER CHECK (min_contract_value_eur IS NULL OR min_contract_value_eur >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tender_requirement_keywords (
    requirement_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    PRIMARY KEY (requirement_id, keyword),
    FOREIGN KEY (requirement_id) REFERENCES tender_requirements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS match_runs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    tender_id TEXT NOT NULL,
    company_profile_id TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    decision TEXT NOT NULL CHECK (decision IN ('bid', 'review', 'no_bid')),
    ko_reasons_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE,
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS requirement_assessments (
    id TEXT PRIMARY KEY,
    match_run_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('met', 'partial', 'missing')),
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    explanation TEXT NOT NULL,
    FOREIGN KEY (match_run_id) REFERENCES match_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES tender_requirements(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS proposal_dossiers (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    tender_id TEXT NOT NULL,
    company_profile_id TEXT NOT NULL,
    match_run_id TEXT NOT NULL,
    total_price_eur INTEGER NOT NULL CHECK (total_price_eur >= 0),
    pricing_assumptions_json TEXT NOT NULL DEFAULT '[]',
    missing_information_json TEXT NOT NULL DEFAULT '[]',
    source_attribution_json TEXT NOT NULL DEFAULT '[]',
    approval_required INTEGER NOT NULL DEFAULT 1 CHECK (approval_required IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'blocked', 'submitted_simulated')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE,
    FOREIGN KEY (company_profile_id) REFERENCES company_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (match_run_id) REFERENCES match_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dossier_references (
    dossier_id TEXT NOT NULL,
    reference_project_id TEXT NOT NULL,
    PRIMARY KEY (dossier_id, reference_project_id),
    FOREIGN KEY (dossier_id) REFERENCES proposal_dossiers(id) ON DELETE CASCADE,
    FOREIGN KEY (reference_project_id) REFERENCES reference_projects(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS approval_tasks (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    dossier_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    approver TEXT,
    note TEXT NOT NULL DEFAULT '',
    decided_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (dossier_id) REFERENCES proposal_dossiers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS submission_simulations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    dossier_id TEXT NOT NULL,
    approval_task_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('blocked_pending_approval', 'simulated_submitted')),
    portal TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (dossier_id) REFERENCES proposal_dossiers(id) ON DELETE CASCADE,
    FOREIGN KEY (approval_task_id) REFERENCES approval_tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outcome_simulations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    tender_id TEXT NOT NULL,
    dossier_id TEXT NOT NULL,
    awarded INTEGER NOT NULL CHECK (awarded IN (0, 1)),
    award_value_eur INTEGER NOT NULL CHECK (award_value_eur >= 0),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE,
    FOREIGN KEY (dossier_id) REFERENCES proposal_dossiers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS billing_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    outcome_simulation_id TEXT NOT NULL,
    commission_rate REAL NOT NULL CHECK (commission_rate >= 0),
    commission_eur INTEGER NOT NULL CHECK (commission_eur >= 0),
    invoice_status TEXT NOT NULL CHECK (invoice_status IN ('not_billable', 'test_invoice_created')),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('not_started', 'test_payment_succeeded')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (outcome_simulation_id) REFERENCES outcome_simulations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    tender_id TEXT NOT NULL,
    signal TEXT NOT NULL,
    notes_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'system',
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_company_profiles_tenant ON company_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_reference_projects_company ON reference_projects(company_profile_id);
CREATE INDEX IF NOT EXISTS idx_tenders_tenant_deadline ON tenders(tenant_id, deadline);
CREATE INDEX IF NOT EXISTS idx_tender_requirements_tender ON tender_requirements(tender_id);
CREATE INDEX IF NOT EXISTS idx_match_runs_tender_company ON match_runs(tender_id, company_profile_id);
CREATE INDEX IF NOT EXISTS idx_requirement_assessments_match ON requirement_assessments(match_run_id);
CREATE INDEX IF NOT EXISTS idx_dossiers_tender_status ON proposal_dossiers(tender_id, status);
CREATE INDEX IF NOT EXISTS idx_approval_tasks_dossier_status ON approval_tasks(dossier_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_entity ON audit_events(tenant_id, entity_type, entity_id);
