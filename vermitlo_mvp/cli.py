from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .pipeline import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Vermitlo MVP demo flows.")
    parser.add_argument("command", choices=["run-demo"])
    args = parser.parse_args()

    if args.command == "run-demo":
        print(json.dumps(asdict(run_demo()), indent=2))


if __name__ == "__main__":
    main()
