-- Vermitlo Stage 2 baseline schema.
-- This migration is intentionally adapter-neutral SQL for the MVP planning layer.
-- Production database specifics can be added once the persistence adapter is chosen.

CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE company_profiles (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    legal_name TEXT NOT NULL,
    country TEXT NOT NULL,
    location TEXT NOT NULL,
    company_size TEXT NOT NULL,
    max_contract_value_eur INTEGER NOT NULL,
    pricing_person_days INTEGER NOT NULL,
    pricing_day_rate_eur INTEGER NOT NULL,
    pricing_contingency_pct REAL NOT NULL,
    pricing_success_fee_pct REAL NOT NULL
);

CREATE TABLE company_capabilities (
    id TEXT PRIMARY KEY,
    company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
    capability TEXT NOT NULL
);

CREATE TABLE company_certifications (
    id TEXT PRIMARY KEY,
    company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
    certification TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE company_references (
    id TEXT PRIMARY KEY,
    company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
    title TEXT NOT NULL,
    industries_json TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    contract_value_eur INTEGER NOT NULL,
    evidence_source TEXT NOT NULL,
    evidence_quality TEXT NOT NULL,
    evidence_note TEXT NOT NULL
);

CREATE TABLE tenders (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    title TEXT NOT NULL,
    buyer TEXT NOT NULL,
    country TEXT NOT NULL,
    delivery_location TEXT NOT NULL,
    estimated_value_eur INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT NOT NULL,
    deadline TEXT NOT NULL
);

CREATE TABLE tender_documents (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL REFERENCES tenders(id),
    filename TEXT NOT NULL,
    source_status TEXT NOT NULL
);

CREATE TABLE tender_requirements (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL REFERENCES tenders(id),
    text TEXT NOT NULL,
    category TEXT NOT NULL,
    mandatory INTEGER NOT NULL,
    keywords_json TEXT NOT NULL,
    required_certification TEXT,
    min_contract_value_eur INTEGER,
    min_references INTEGER
);

CREATE TABLE knockout_criteria (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL REFERENCES tenders(id),
    text TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    note TEXT
);

CREATE TABLE match_evaluations (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL REFERENCES tenders(id),
    company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
    score INTEGER NOT NULL,
    decision TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    ko_reasons_json TEXT NOT NULL,
    warnings_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE requirement_assessments (
    id TEXT PRIMARY KEY,
    match_evaluation_id TEXT NOT NULL REFERENCES match_evaluations(id),
    requirement_id TEXT NOT NULL REFERENCES tender_requirements(id),
    status TEXT NOT NULL,
    score INTEGER NOT NULL,
    explanation TEXT NOT NULL
);

CREATE TABLE pricing_drafts (
    id TEXT PRIMARY KEY,
    match_evaluation_id TEXT NOT NULL REFERENCES match_evaluations(id),
    person_days INTEGER NOT NULL,
    day_rate_eur INTEGER NOT NULL,
    base_price_eur INTEGER NOT NULL,
    contingency_eur INTEGER NOT NULL,
    total_price_eur INTEGER NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE proposal_dossiers (
    id TEXT PRIMARY KEY,
    tender_id TEXT NOT NULL REFERENCES tenders(id),
    company_profile_id TEXT NOT NULL REFERENCES company_profiles(id),
    match_evaluation_id TEXT NOT NULL REFERENCES match_evaluations(id),
    pricing_draft_id TEXT NOT NULL REFERENCES pricing_drafts(id),
    status TEXT NOT NULL,
    sections_json TEXT NOT NULL,
    selected_reference_ids_json TEXT NOT NULL,
    missing_information_json TEXT NOT NULL
);

CREATE TABLE approval_tasks (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES proposal_dossiers(id),
    role TEXT NOT NULL,
    decision TEXT NOT NULL,
    approver TEXT,
    note TEXT NOT NULL,
    legal_submission_allowed INTEGER NOT NULL
);

CREATE TABLE submission_simulations (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES proposal_dossiers(id),
    approval_task_id TEXT NOT NULL REFERENCES approval_tasks(id),
    status TEXT NOT NULL,
    portal TEXT NOT NULL,
    external_portal_called INTEGER NOT NULL,
    message TEXT NOT NULL
);

CREATE TABLE outcome_simulations (
    id TEXT PRIMARY KEY,
    submission_simulation_id TEXT NOT NULL REFERENCES submission_simulations(id),
    awarded INTEGER NOT NULL,
    award_value_eur INTEGER NOT NULL,
    reason TEXT NOT NULL
);

CREATE TABLE billing_events (
    id TEXT PRIMARY KEY,
    outcome_simulation_id TEXT NOT NULL REFERENCES outcome_simulations(id),
    commission_rate REAL NOT NULL,
    commission_eur INTEGER NOT NULL,
    billable INTEGER NOT NULL
);

CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    billing_event_id TEXT NOT NULL REFERENCES billing_events(id),
    invoice_number TEXT NOT NULL,
    net_eur INTEGER NOT NULL,
    vat_pct REAL NOT NULL,
    gross_eur REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE payment_simulations (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    status TEXT NOT NULL,
    real_charge_created INTEGER NOT NULL
);

CREATE TABLE audit_log_entries (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_name TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
