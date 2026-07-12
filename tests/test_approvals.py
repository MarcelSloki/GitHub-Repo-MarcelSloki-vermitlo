import unittest

from vermitlo_mvp.approvals import approval_to_submission_input, decide_approval
from vermitlo_mvp.rules import analyze_match, build_dossier
from vermitlo_mvp.seed_loader import load_company_profile, load_tender


class ApprovalTest(unittest.TestCase):
    def test_approval_is_approved_with_conditions_for_golden_flow(self):
        company = load_company_profile()
        tender = load_tender()
        dossier = build_dossier(company, tender, analyze_match(company, tender))

        approval = decide_approval(dossier, approved=True)

        self.assertEqual(approval.id, "approval-demo-001")
        self.assertEqual(approval.role, "commercial_approver")
        self.assertEqual(approval.decision, "approved_with_conditions")
        self.assertEqual(approval.audit_event, "approval.completed")
        self.assertFalse(approval.legal_submission_allowed)
        self.assertTrue(approval.conditions)
        self.assertEqual(approval.blockers, [])

    def test_rejected_approval_blocks_submission_input(self):
        company = load_company_profile()
        tender = load_tender()
        dossier = build_dossier(company, tender, analyze_match(company, tender))

        approval = decide_approval(dossier, approved=False)
        submission_input = approval_to_submission_input(approval)

        self.assertEqual(approval.decision, "blocked")
        self.assertEqual(approval.audit_event, "approval.blocked")
        self.assertFalse(submission_input.approved)
        self.assertIn("withheld", submission_input.note)


if __name__ == "__main__":
    unittest.main()
