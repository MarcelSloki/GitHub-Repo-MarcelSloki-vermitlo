from unittest import TestCase

from vermitlo_mvp.pipeline import build_dossier, run_demo
from vermitlo_mvp.seeds import demo_company, demo_tender


class PipelineTests(TestCase):
    def test_demo_flow_reaches_test_payment(self) -> None:
        result = run_demo()

        self.assertEqual(result.approval_status, "approved_for_simulation")
        self.assertEqual(result.submission_status, "simulated")
        self.assertEqual(result.outcome_status, "simulated_awarded")
        self.assertEqual(result.commission_invoice_status, "test_invoice_created")
        self.assertEqual(result.payment_status, "test_payment_succeeded")

    def test_portal_submission_is_flagged_for_manual_handling(self) -> None:
        dossier = build_dossier(demo_company(), demo_tender())

        self.assertIn("portal_submission_requires_manual_or_authorized_adapter", dossier.risk_flags)
        self.assertTrue(dossier.approval_required)

    def test_no_unverified_references_are_selected(self) -> None:
        dossier = build_dossier(demo_company(), demo_tender())

        self.assertTrue(dossier.selected_references)
        self.assertTrue(all(ref.evidence_status == "verified" for ref in dossier.selected_references))
