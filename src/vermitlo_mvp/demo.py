from __future__ import annotations

import json
import sys

from .workflow import run_and_persist_demo, run_demo


def main() -> None:
    persist = "--persist" in sys.argv
    result = run_and_persist_demo(approved=True) if persist else run_demo(approved=True)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
