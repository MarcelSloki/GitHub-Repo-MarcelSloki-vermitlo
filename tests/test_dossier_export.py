import unittest

from vermitlo_mvp.dossier_export import build_submission_package
from vermitlo_mvp.rules import analyze_match, build_dossier
from vermitlo_mvp.seed_loader import load_company_profile, load_tender


class DossierExportTest(unittest.TestCase):
    def test_submission_package_contains_expected_demo_files(self):
        company = load_company_profile()
        tender = load_tender()
        dossier = build_dossier(company, tender, analyze_match(company, tender))

        package = build_submission_package(dossier)

        self.assertEqual(package.id, "submission-package-demo-001")
        self.assertEqual(package.status, "draft_export_simulated")
        self.assertIn("Angebotsdossier.pdf", package.files)
        self.assertIn("Preisblatt.xlsx", package.files)
        self.assertIn("Referenzanhang.pdf", package.files)

    def test_submission_package_preserves_safety_boundaries(self):
        company = load_company_profile()
        tender = load_tender()
        dossier = build_dossier(company, tender, analyze_match(company, tender))

        package = build_submission_package(dossier)

        self.assertFalse(package.external_portal_called)
        self.assertFalse(package.legal_submission_allowed)
        self.assertTrue(any("Human approval" in check for check in package.checks))
        self.assertTrue(package.open_questions)


if __name__ == "__main__":
    unittest.main()
