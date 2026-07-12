import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "0001_core_domain.sql"


class SchemaMigrationTest(unittest.TestCase):
    def test_core_schema_applies_to_sqlite(self):
        connection = sqlite3.connect(":memory:")
        connection.executescript(MIGRATION.read_text(encoding="utf-8"))

        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

        self.assertIn("tenants", table_names)
        self.assertIn("company_profiles", table_names)
        self.assertIn("tenders", table_names)
        self.assertIn("match_runs", table_names)
        self.assertIn("proposal_dossiers", table_names)
        self.assertIn("approval_tasks", table_names)
        self.assertIn("submission_simulations", table_names)
        self.assertIn("billing_events", table_names)
        self.assertIn("audit_events", table_names)

    def test_submission_status_constraint_blocks_unknown_values(self):
        connection = sqlite3.connect(":memory:")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(MIGRATION.read_text(encoding="utf-8"))

        connection.execute(
            "INSERT INTO tenants (id, name) VALUES (?, ?)",
            ("tenant-demo", "Demo Tenant"),
        )
        connection.execute(
            """
            INSERT INTO company_profiles
                (id, tenant_id, legal_name, country, max_contract_value_eur)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("company-demo", "tenant-demo", "Demo IT Services GmbH", "DE", 750000),
        )
        connection.execute(
            """
            INSERT INTO tenders
                (id, tenant_id, title, buyer, country, estimated_value_eur, source_url, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "tender-demo",
                "tenant-demo",
                "Demo tender",
                "Demo Public Buyer",
                "DE",
                500000,
                "https://example.invalid/tender",
                "2026-09-15",
            ),
        )
        connection.execute(
            """
            INSERT INTO match_runs
                (id, tenant_id, tender_id, company_profile_id, score, decision)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("match-demo", "tenant-demo", "tender-demo", "company-demo", 90, "bid"),
        )
        connection.execute(
            """
            INSERT INTO proposal_dossiers
                (id, tenant_id, tender_id, company_profile_id, match_run_id, total_price_eur)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "dossier-demo",
                "tenant-demo",
                "tender-demo",
                "company-demo",
                "match-demo",
                459200,
            ),
        )
        connection.execute(
            """
            INSERT INTO approval_tasks
                (id, tenant_id, dossier_id, status, approver, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "approval-demo",
                "tenant-demo",
                "dossier-demo",
                "approved",
                "Demo Approver",
                "Synthetic approval",
            ),
        )

        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO submission_simulations
                    (id, tenant_id, dossier_id, approval_task_id, status, portal, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "submission-demo",
                    "tenant-demo",
                    "dossier-demo",
                    "approval-demo",
                    "real_submitted",
                    "mock-public-procurement-portal",
                    "Invalid status should be blocked",
                ),
            )


if __name__ == "__main__":
    unittest.main()
