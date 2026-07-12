from __future__ import annotations

import argparse
import json

from .storage import AuditStore
from .workflow import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Vermitlo MVP demo flow.")
    parser.add_argument("--no-approval", action="store_true", help="Block the submission at approval.")
    parser.add_argument("--no-go", action="store_true", help="Use a tender with hard K.O. criteria.")
    parser.add_argument("--db", help="Optional SQLite path for persisting the audited demo run.")
    args = parser.parse_args()

    result = run_demo(approved=not args.no_approval, no_go=args.no_go)
    if args.db:
        run_id = AuditStore(args.db).save_demo_run(result)
        result["audit_persistence"] = {"db_path": args.db, "run_id": run_id}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
