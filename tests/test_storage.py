import tempfile
import unittest
from pathlib import Path

from vermitlo_mvp.storage import WorkflowStore
from vermitlo_mvp.workflow import run_and_persist_demo, run_demo


class StorageTest(unittest.TestCase):
    def test_persisted_run_can_be_loaded_with_audit_events(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "vermitlo.sqlite3"
            result = run_and_persist_demo(approved=True, db_path=str(db_path))

            stored = WorkflowStore(db_path).get_workflow_run(result["run_id"])

        self.assertIsNotNone(stored)
        self.assertEqual(stored["decision"], "bid")
        self.assertEqual(stored["match_score"], 80)
        self.assertEqual(stored["submission_status"], "simulated_submitted")
        self.assertGreaterEqual(len(stored["audit_events"]), 7)
        self.assertEqual(stored["audit_events"][0]["event_type"], "tender_imported")

    def test_list_workflow_runs_exposes_summary_without_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "vermitlo.sqlite3"
            store = WorkflowStore(db_path)
            run_id = store.save_workflow_run(run_demo(approved=False))

            runs = store.list_workflow_runs()

        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["id"], run_id)
        self.assertEqual(runs[0]["submission_status"], "blocked_pending_approval")
        self.assertNotIn("payload", runs[0])


if __name__ == "__main__":
    unittest.main()
