import unittest

from vermitlo_mvp.source_registry import (
    get_first_adapter_candidate,
    load_source_registry,
    source_allows,
)


class SourceRegistryTest(unittest.TestCase):
    def test_registry_contains_official_candidate_sources(self):
        registry = load_source_registry()
        ids = {source.id for source in registry}

        self.assertIn("ted-api", ids)
        self.assertIn("doe-bekanntmachungsservice", ids)
        self.assertIn("service-bund-notices", ids)

    def test_first_adapter_candidate_is_german_bekanntmachungsservice(self):
        source = get_first_adapter_candidate()

        self.assertEqual(source.id, "doe-bekanntmachungsservice")
        self.assertEqual(source.jurisdiction, "DE")
        self.assertEqual(source.adapter_status, "planned")
        self.assertTrue(source_allows(source, "search_notices"))

    def test_registry_never_allows_submission_actions_in_mvp(self):
        registry = load_source_registry()

        for source in registry:
            self.assertFalse(source_allows(source, "submit_bid"))
            self.assertFalse(source_allows(source, "submit_notice"))
            self.assertIn("bypass_portal_rules", source.mvp_forbidden_actions)


if __name__ == "__main__":
    unittest.main()
