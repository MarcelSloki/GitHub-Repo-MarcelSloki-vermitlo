import unittest

from vermitlo_mvp.adapters import BekanntmachungsserviceMockAdapter, get_default_import_adapter
from vermitlo_mvp.source_registry import get_first_adapter_candidate


class AdapterTest(unittest.TestCase):
    def test_default_adapter_uses_german_bekanntmachungsservice_candidate(self):
        adapter = get_default_import_adapter()
        result = adapter.import_notice("tender-demo-essen-2026-001")

        self.assertEqual(result.source_id, "doe-bekanntmachungsservice")
        self.assertEqual(result.tender.id, "tender-demo-essen-2026-001")
        self.assertEqual(result.mode, "fixture_only")

    def test_adapter_never_performs_live_request_in_stage_2(self):
        result = BekanntmachungsserviceMockAdapter().import_notice("tender-demo-essen-2026-001")

        self.assertFalse(result.external_request_performed)
        self.assertIn("submit_bid", result.forbidden_actions)
        self.assertIn("bypass_portal_rules", result.forbidden_actions)
        self.assertTrue(result.warnings)

    def test_adapter_requires_retrieve_permission(self):
        source = get_first_adapter_candidate()
        blocked_source = type(source)(
            **{
                **source.__dict__,
                "mvp_allowed_actions": ["search_notices", "source_attribution"],
            }
        )
        adapter = BekanntmachungsserviceMockAdapter(source=blocked_source)

        with self.assertRaises(PermissionError):
            adapter.import_notice("tender-demo-essen-2026-001")


if __name__ == "__main__":
    unittest.main()
