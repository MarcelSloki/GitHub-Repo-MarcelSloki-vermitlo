import unittest

from vermitlo_mvp.api import (
    demo_approval_payload,
    demo_import_payload,
    demo_submission_package_payload,
    golden_flow_payload,
    health_payload,
    source_registry_payload,
)


class ApiPayloadTest(unittest.TestCase):
    def test_golden_flow_payload_exposes_import_metadata(self):
        payload = golden_flow_payload()

        self.assertEqual(payload["import"]["source_id"], "doe-bekanntmachungsservice")
        self.assertEqual(payload["import"]["mode"], "fixture_only")
        self.assertFalse(payload["import"]["external_request_performed"])
        self.assertIn("submit_bid", payload["import"]["forbidden_actions"])

    def test_demo_run_payload_can_show_blocked_submission(self):
        payload = golden_flow_payload(approved=False)

        self.assertEqual(payload["approval"]["decision"], "blocked")
        self.assertEqual(payload["approval"]["audit_event"], "approval.blocked")
        self.assertEqual(payload["submission"]["status"], "blocked_pending_approval")
        self.assertFalse(payload["submission"]["external_portal_called"])

    def test_source_registry_payload_exposes_first_adapter_candidate(self):
        payload = source_registry_payload()

        self.assertEqual(payload["first_adapter_candidate"]["id"], "doe-bekanntmachungsservice")
        self.assertEqual(len(payload["sources"]), 3)

    def test_demo_import_payload_is_fixture_only(self):
        payload = demo_import_payload()

        self.assertEqual(payload["import"]["notice_id"], "tender-demo-essen-2026-001")
        self.assertEqual(payload["import"]["tender"]["id"], "tender-demo-essen-2026-001")
        self.assertFalse(payload["import"]["external_request_performed"])

    def test_demo_submission_package_payload_is_simulated_export(self):
        payload = demo_submission_package_payload()
        package = payload["submission_package"]

        self.assertEqual(package["status"], "draft_export_simulated")
        self.assertIn("Angebotsdossier.pdf", package["files"])
        self.assertFalse(package["external_portal_called"])
        self.assertFalse(package["legal_submission_allowed"])

    def test_demo_approval_payload_is_structured_and_conditional(self):
        payload = demo_approval_payload()
        approval = payload["approval"]

        self.assertEqual(approval["role"], "commercial_approver")
        self.assertEqual(approval["decision"], "approved_with_conditions")
        self.assertFalse(approval["legal_submission_allowed"])
        self.assertTrue(approval["conditions"])

    def test_health_payload(self):
        self.assertEqual(health_payload(), {"status": "ok", "service": "vermitlo-mvp"})


if __name__ == "__main__":
    unittest.main()
