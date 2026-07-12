import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "0001_golden_path_domain_skeleton.sql"
GOLDEN_FIXTURE = ROOT / "fixtures" / "golden_path_it_services_demo.json"
BLOCKED_FIXTURE = ROOT / "fixtures" / "blocked_missing_evidence_demo.json"


class GoldenPathDomainSkeletonTest(unittest.TestCase):
    def setUp(self):
        self.sql = MIGRATION.read_text(encoding="utf-8")
        self.golden = json.loads(GOLDEN_FIXTURE.read_text(encoding="utf-8"))
        self.blocked = json.loads(BLOCKED_FIXTURE.read_text(encoding="utf-8"))

    def test_migration_declares_all_eight_golden_path_tables(self):
        expected_tables = [
            "tenants",
            "company_profiles",
            "tenders",
            "match_assessments",
            "proposal_dossiers",
            "approval_tasks",
            "outcome_events",
            "billing_events",
        ]

        for table in expected_tables:
            self.assertRegex(self.sql, rf"CREATE TABLE {table} \(")

    def test_migration_keeps_outcome_and_billing_simulated(self):
        self.assertIn("CHECK (simulated = true)", self.sql)
        self.assertIn("award_simulated_won", self.sql)
        self.assertIn("commission_calculated_test", self.sql)
        self.assertNotIn("payment_collected", self.sql)
        self.assertNotIn("submission_live", self.sql)

    def test_golden_fixture_links_from_tenant_through_billing(self):
        tenant_id = self.golden["tenant"]["id"]
        company = self.golden["company_profile"]
        tender = self.golden["tender"]
        match = self.golden["match_assessment"]
        dossier = self.golden["proposal_dossier"]
        approval = self.golden["approval_task"]
        outcome = self.golden["outcome_event"]
        billing = self.golden["billing_event"]

        for item in [company, tender, match, dossier, approval, outcome, billing]:
            self.assertEqual(item["tenant_id"], tenant_id)

        self.assertEqual(match["company_profile_id"], company["id"])
        self.assertEqual(match["tender_id"], tender["id"])
        self.assertEqual(dossier["match_assessment_id"], match["id"])
        self.assertEqual(approval["proposal_dossier_id"], dossier["id"])
        self.assertEqual(outcome["proposal_dossier_id"], dossier["id"])
        self.assertEqual(billing["outcome_event_id"], outcome["id"])

    def test_golden_fixture_preserves_human_approval_and_simulation_truth(self):
        self.assertEqual(self.golden["approval_task"]["approval_status"], "approved")
        self.assertTrue(self.golden["outcome_event"]["simulated"])
        self.assertTrue(self.golden["billing_event"]["simulated"])
        self.assertIn("No legally binding submission", self.golden["approval_task"]["comments"])
        self.assertEqual(self.golden["billing_event"]["currency"], "EUR")

    def test_blocked_fixture_stops_before_approval_outcome_and_billing(self):
        self.assertEqual(self.blocked["match_assessment"]["assessment_status"], "blocked_by_exclusion")
        self.assertEqual(self.blocked["match_assessment"]["recommendation"], "no_bid")
        self.assertEqual(self.blocked["proposal_dossier"]["dossier_status"], "blocked_missing_evidence")
        self.assertIsNone(self.blocked["approval_task"])
        self.assertIsNone(self.blocked["outcome_event"])
        self.assertIsNone(self.blocked["billing_event"])

    def test_missing_evidence_remains_visible_and_not_invented(self):
        serialized = json.dumps(self.blocked).lower()
        self.assertIn("mandatory iso 27001 certificate", serialized)
        self.assertIn("blocking", serialized)
        self.assertNotIn("certificate available", serialized)

    def test_no_old_five_table_guardrail_remains(self):
        create_table_names = set(re.findall(r"CREATE TABLE ([a-z_]+) \(", self.sql))
        self.assertEqual(len(create_table_names), 8)
        self.assertIn("match_assessments", create_table_names)
        self.assertIn("outcome_events", create_table_names)
        self.assertIn("billing_events", create_table_names)


if __name__ == "__main__":
    unittest.main()
