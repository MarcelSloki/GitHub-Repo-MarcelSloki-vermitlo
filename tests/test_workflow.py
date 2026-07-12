import unittest

from vermitlo_mvp.models import Approval, SubmissionStatus
from vermitlo_mvp.rules import analyze_match, build_dossier, simulate_submission
from vermitlo_mvp.seed_loader import load_company_profile, load_tender
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


if __name__ == "__main__":
    unittest.main()
