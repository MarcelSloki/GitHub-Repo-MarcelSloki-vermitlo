from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from vermitlo_mvp.persistence import (
    DEFAULT_TENANT_ID,
    apply_migrations,
    get_company_profile_snapshot,
    get_latest_dossier_snapshot,
    get_tenant_overview,
    get_tender_snapshot,
    persist_demo_run,
    seed_demo_data,
    table_count,
)


class PersistenceTest(unittest.TestCase):
    def test_migrations_and_seed_load_core_demo_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "vermitlo.sqlite3"

            apply_migrations(db_path)
            result = seed_demo_data(db_path)

            self.assertEqual(result["company_profiles"], 1)
            self.assertEqual(result["tenders"], 1)
            self.assertEqual(table_count(db_path, "tenants"), 1)
            self.assertEqual(table_count(db_path, "reference_projects"), 2)
            self.assertEqual(table_count(db_path, "tender_requirements"), 4)
            self.assertEqual(table_count(db_path, "audit_events"), 1)

    def test_persist_demo_run_records_approval_submission_and_billing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "vermitlo.sqlite3"

            apply_migrations(db_path)
            result = persist_demo_run(db_path, approved=True)

            self.assertEqual(result["submission_status"], "simulated_submitted")
            self.assertGreater(result["commission_eur"], 0)
            self.assertEqual(table_count(db_path, "match_decisions"), 1)
            self.assertEqual(table_count(db_path, "proposal_dossiers"), 1)
            self.assertEqual(table_count(db_path, "approvals"), 1)
            self.assertEqual(table_count(db_path, "submission_simulations"), 1)
            self.assertEqual(table_count(db_path, "outcome_simulations"), 1)
            self.assertEqual(table_count(db_path, "billing_events"), 1)

    def test_persist_blocked_run_keeps_billing_non_chargeable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "vermitlo.sqlite3"

            apply_migrations(db_path)
            result = persist_demo_run(db_path, approved=False)

            self.assertEqual(result["submission_status"], "blocked_pending_approval")
            self.assertEqual(result["commission_eur"], 0)
            self.assertEqual(table_count(db_path, "billing_events"), 1)

    def test_read_models_return_demo_snapshots(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "vermitlo.sqlite3"

            apply_migrations(db_path)
            persist_demo_run(db_path, approved=True)

            tenant = get_tenant_overview(db_path, tenant_id=DEFAULT_TENANT_ID)
            company = get_company_profile_snapshot(db_path)
            tender = get_tender_snapshot(db_path)
            dossier = get_latest_dossier_snapshot(db_path)

            self.assertEqual(tenant["counts"]["company_profiles"], 1)
            self.assertEqual(company["legal_name"], "Demo IT Services GmbH")
            self.assertEqual(len(company["references"]), 2)
            self.assertEqual(tender["id"], "tender-demo-2026-001")
            self.assertEqual(len(tender["requirements"]), 4)
            self.assertEqual(dossier["match"]["decision"], "bid")
            self.assertEqual(dossier["submission"]["status"], "simulated_submitted")
            self.assertGreater(dossier["billing"]["commission_eur"], 0)


if __name__ == "__main__":
    unittest.main()
