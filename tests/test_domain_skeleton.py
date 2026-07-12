import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "0001_domain_skeleton.sql"
FIXTURE = ROOT / "fixtures" / "golden_path.json"


class DomainSkeletonTest(unittest.TestCase):
    def setUp(self):
        self.sql = MIGRATION.read_text(encoding="utf-8")
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_migration_declares_stage_two_backbone_tables(self):
        expected_tables = [
            "tenants",
            "company_profiles",
            "tenders",
            "proposal_dossiers",
            "approval_tasks",
        ]

        for table in expected_tables:
            self.assertRegex(self.sql, rf"CREATE TABLE {table} \(")

    def test_relationships_keep_artifacts_tenant_scoped(self):
        required_references = [
            "tenant_id uuid NOT NULL REFERENCES tenants(id)",
            "tender_id uuid NOT NULL REFERENCES tenders(id)",
            "company_profile_id uuid NOT NULL REFERENCES company_profiles(id)",
            "dossier_id uuid NOT NULL REFERENCES proposal_dossiers(id)",
        ]

        for reference in required_references:
            self.assertIn(reference, self.sql)

    def test_status_constraints_preserve_human_approval_gate(self):
        self.assertIn("approval_status IN ('pending', 'approved', 'rejected', 'cancelled')", self.sql)
        self.assertIn("approval_status = 'pending' AND decided_at IS NULL", self.sql)
        self.assertIn("approval_status <> 'pending' AND decided_at IS NOT NULL", self.sql)
        self.assertIn("'awaiting_approval'", self.sql)
        self.assertIn("'approved'", self.sql)

    def test_json_columns_are_intentionally_array_shaped(self):
        json_columns = [
            "capabilities_json",
            "certifications_json",
            "reference_projects_json",
            "requirement_items_json",
            "exclusion_criteria_json",
            "selected_references_json",
            "generated_sections_json",
            "open_questions_json",
        ]

        for column in json_columns:
            self.assertRegex(self.sql, rf"jsonb_typeof\({column}\) = 'array'")

    def test_golden_fixture_relationships_are_consistent(self):
        tenant_id = self.fixture["tenant"]["id"]
        company = self.fixture["company_profile"]
        tender = self.fixture["tender"]
        dossier = self.fixture["proposal_dossier"]
        approval = self.fixture["approval_task"]

        self.assertEqual(company["tenant_id"], tenant_id)
        self.assertEqual(tender["tenant_id"], tenant_id)
        self.assertEqual(dossier["tenant_id"], tenant_id)
        self.assertEqual(dossier["company_profile_id"], company["id"])
        self.assertEqual(dossier["tender_id"], tender["id"])
        self.assertEqual(approval["tenant_id"], tenant_id)
        self.assertEqual(approval["dossier_id"], dossier["id"])

    def test_golden_fixture_stays_synthetic_and_non_binding(self):
        serialized = json.dumps(self.fixture)

        self.assertIn("synthetic", serialized.lower())
        self.assertIn("No legally binding submission", serialized)
        self.assertEqual(self.fixture["approval_task"]["approval_status"], "approved")
        self.assertIsNotNone(self.fixture["approval_task"]["decided_at"])

    def test_migration_does_not_add_deferred_layers(self):
        deferred_tables = ["match_assessments", "outcome_events", "billing_events"]
        create_table_names = set(re.findall(r"CREATE TABLE ([a-z_]+) \(", self.sql))

        self.assertTrue(create_table_names.isdisjoint(deferred_tables))


if __name__ == "__main__":
    unittest.main()
