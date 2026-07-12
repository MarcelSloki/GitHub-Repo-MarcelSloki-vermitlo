import unittest

from vermitlo_mvp.models import Approval, SubmissionStatus
from vermitlo_mvp.rules import analyze_match, build_dossier, simulate_submission
from vermitlo_mvp.seed_loader import load_company_profile, load_tender
from vermitlo_mvp.workflow import run_demo


class WorkflowTest(unittest.TestCase):
    def test_demo_flow_reaches_sandbox_payment(self):
        result = run_demo(approved=True)

        self.assertEqual(result["company"]["legal_name"], "RheinMain Digital GmbH")
        self.assertEqual(result["tender"]["id"], "tender-demo-essen-2026-001")
        self.assertEqual(result["import"]["source_id"], "doe-bekanntmachungsservice")
        self.assertFalse(result["import"]["external_request_performed"])
        self.assertEqual(result["match"]["score"], 78)
        self.assertEqual(result["submission_package"]["status"], "draft_export_simulated")
        self.assertFalse(result["submission_package"]["external_portal_called"])
        self.assertEqual(result["match"]["decision"], "bid")
        self.assertEqual(result["match"]["recommendation"], "bid_with_conditions")
        self.assertEqual(result["approval"]["decision"], "approved_with_conditions")
        self.assertFalse(result["approval"]["legal_submission_allowed"])
        self.assertEqual(result["submission"]["status"], "simulated_submitted")
        self.assertEqual(result["billing"]["invoice_status"], "sandbox_invoice_created")
        self.assertEqual(result["billing"]["payment_status"], "sandbox_paid")

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
        self.assertFalse(submission.external_portal_called)

    def test_no_synthetic_reference_is_created(self):
        result = run_demo(approved=True)
        selected = set(result["dossier"]["selected_reference_ids"])
        available = {item["id"] for item in result["company"]["references"]}

        self.assertEqual(selected, {"ref-kommportal-2024", "ref-fachverfahren-2023"})
        self.assertTrue(selected <= available)

    def test_iso27001_is_warning_not_hard_fail(self):
        result = run_demo(approved=True)

        self.assertEqual(result["match"]["ko_reasons"], [])
        self.assertTrue(result["match"]["warnings"])
        self.assertIn("ISO 27001 missing", result["match"]["warnings"][0])
        self.assertIn("ISO 27001", result["dossier"]["missing_information"][0])

    def test_pricing_and_billing_match_golden_flow(self):
        result = run_demo(approved=True)

        self.assertEqual(result["dossier"]["pricing"]["person_days"], 280)
        self.assertEqual(result["dossier"]["pricing"]["day_rate_eur"], 980)
        self.assertEqual(result["dossier"]["pricing"]["total_price_eur"], 307328)
        self.assertEqual(result["outcome"]["award_value_eur"], 302000)
        self.assertEqual(result["billing"]["commission_rate"], 0.03)
        self.assertEqual(result["billing"]["commission_eur"], 9060)
        self.assertFalse(result["billing"]["real_charge_created"])

    def test_audit_log_contains_full_golden_sequence(self):
        result = run_demo(approved=True)

        self.assertEqual(
            result["audit_log"],
            [
                "company_profile.created",
                "tender.imported",
                "tender.requirements_analyzed",
                "match.evaluated",
                "pricing.draft_created",
                "references.selected",
                "dossier.generated",
                "approval.completed",
                "submission.simulated",
                "outcome.simulated",
                "billing.success_fee_calculated",
                "payment.sandbox_completed",
                "learning.event_recorded",
            ],
        )


if __name__ == "__main__":
    unittest.main()
