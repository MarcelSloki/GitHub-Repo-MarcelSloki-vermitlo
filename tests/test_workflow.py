import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from vermitlo_mvp.models import Approval, Decision, SubmissionStatus
from vermitlo_mvp.rules import analyze_match, build_dossier, simulate_submission
from vermitlo_mvp.seed_loader import load_company_profile, load_tender
from vermitlo_mvp.storage import AuditStore
from vermitlo_mvp.workflow import run_demo


class WorkflowTest(unittest.TestCase):
    def test_demo_flow_reaches_test_payment(self):
        result = run_demo(approved=True)

        self.assertEqual(result["match"]["decision"], "bid")
        self.assertGreaterEqual(result["match"]["score"], 75)
        self.assertEqual(result["submission"]["status"], "simulated_submitted")
        self.assertEqual(result["billing"]["invoice_status"], "test_invoice_created")
        self.assertEqual(result["billing"]["payment_status"], "test_payment_succeeded")

    def test_submission_is_blocked_without_human_approval(self):
        company = load_company_profile()
        tender = load_tender()
        match = analyze_match(company, tender)
        dossier = build_dossier(company, tender, match)

        submission = simulate_submission(
            dossier,
            Approval(approved=False, approver=None, note="No approval"),
        )

        self.assertEqual(submission.status, SubmissionStatus.BLOCKED_PENDING_APPROVAL)

    def test_no_synthetic_reference_is_created(self):
        result = run_demo(approved=True)
        selected = set(result["dossier"]["selected_reference_ids"])
        available = {item["id"] for item in result["company"]["references"]}

        self.assertTrue(selected)
        self.assertTrue(selected <= available)

    def test_hard_ko_criteria_stop_before_pricing_submission_and_billing(self):
        result = run_demo(approved=True, no_go=True)

        self.assertEqual(result["match"]["decision"], Decision.NO_BID.value)
        self.assertTrue(result["match"]["ko_reasons"])
        self.assertNotIn("pricing", result["dossier"])
        self.assertEqual(result["dossier"]["selected_reference_ids"], [])
        self.assertEqual(result["submission"]["status"], SubmissionStatus.BLOCKED_PENDING_APPROVAL.value)
        self.assertEqual(result["billing"]["invoice_status"], "not_billable")
        self.assertEqual(result["billing"]["payment_status"], "not_started")

    def test_demo_run_can_be_persisted_for_audit(self):
        result = run_demo(approved=True, no_go=True)

        with TemporaryDirectory() as directory:
            store = AuditStore(Path(directory) / "vermitlo-demo.sqlite")
            run_id = store.save_demo_run(result)
            rows = store.list_runs()
            restored = store.get_run(run_id)

        self.assertEqual(rows[0]["id"], run_id)
        self.assertEqual(rows[0]["decision"], Decision.NO_BID.value)
        self.assertEqual(rows[0]["invoice_status"], "not_billable")
        self.assertEqual(restored["tender"]["id"], "tender-demo-2026-002")


if __name__ == "__main__":
    unittest.main()
