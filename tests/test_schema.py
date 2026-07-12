import unittest

from vermitlo_mvp.schema import CORE_TABLES, load_initial_migration


class SchemaTest(unittest.TestCase):
    def test_initial_migration_contains_core_tables(self):
        migration = load_initial_migration()

        for table in CORE_TABLES:
            self.assertIn(f"CREATE TABLE {table}", migration)

    def test_schema_keeps_submission_and_payment_as_simulations(self):
        migration = load_initial_migration()

        self.assertIn("submission_simulations", migration)
        self.assertIn("payment_simulations", migration)
        self.assertIn("external_portal_called INTEGER NOT NULL", migration)
        self.assertIn("real_charge_created INTEGER NOT NULL", migration)

    def test_schema_links_audit_log_to_tenant(self):
        migration = load_initial_migration()

        self.assertIn("CREATE TABLE audit_log_entries", migration)
        self.assertIn("tenant_id TEXT NOT NULL REFERENCES tenants(id)", migration)


if __name__ == "__main__":
    unittest.main()
