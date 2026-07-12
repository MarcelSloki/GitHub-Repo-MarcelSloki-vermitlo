import copy
import unittest

from vermitlo_mvp.domain_fixture import DomainFixtureError, load_domain_fixture


class DomainFixtureLoaderTest(unittest.TestCase):
    def test_loads_golden_path_fixture(self):
        fixture = load_domain_fixture()
        records = fixture.as_records()

        self.assertEqual(records["tenant"]["workspace_status"], "active")
        self.assertEqual(records["proposal_dossier"]["dossier_status"], "approved")
        self.assertEqual(records["approval_task"]["approval_status"], "approved")

    def test_rejects_broken_relationships(self):
        fixture = load_domain_fixture()
        payload = copy.deepcopy(fixture.as_records())
        payload["proposal_dossier"]["company_profile_id"] = "not-the-company-profile"

        with self.assertRaisesRegex(DomainFixtureError, "proposal_dossier.company_profile_id"):
            fixture.from_mapping(payload)

    def test_rejects_decided_approval_without_decision_timestamp(self):
        fixture = load_domain_fixture()
        payload = copy.deepcopy(fixture.as_records())
        payload["approval_task"]["approval_status"] = "approved"
        payload["approval_task"]["decided_at"] = None

        with self.assertRaisesRegex(DomainFixtureError, "decided_at is required"):
            fixture.from_mapping(payload)

    def test_rejects_fixture_without_non_binding_note(self):
        fixture = load_domain_fixture()
        payload = copy.deepcopy(fixture.as_records())
        payload["proposal_dossier"]["export_notes_json"] = []

        with self.assertRaisesRegex(DomainFixtureError, "no legally binding submission"):
            fixture.from_mapping(payload)


if __name__ == "__main__":
    unittest.main()
