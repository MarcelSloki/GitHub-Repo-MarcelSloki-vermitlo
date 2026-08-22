import os
import unittest
from unittest.mock import patch

from vermitlo_mvp.server import bind_address_from_env, demo_overview_payload


class ServerTest(unittest.TestCase):
    def test_demo_overview_exposes_stage_2_flow_and_boundaries(self):
        overview = demo_overview_payload()

        self.assertIn("Company profile", overview["flow"])
        self.assertIn("Tender import", overview["flow"])
        self.assertIn("Offer dossier", overview["flow"])
        self.assertTrue(any("No real tender portal submission" in item for item in overview["boundaries"]))
        self.assertTrue(any("No real customer payment" in item for item in overview["boundaries"]))

    def test_bind_address_defaults_to_localhost(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(bind_address_from_env(), ("127.0.0.1", 8000))

    def test_bind_address_can_be_configured_for_docker(self):
        with patch.dict(os.environ, {"VERMITLO_HOST": "0.0.0.0", "VERMITLO_PORT": "8080"}, clear=True):
            self.assertEqual(bind_address_from_env(), ("0.0.0.0", 8080))


if __name__ == "__main__":
    unittest.main()
