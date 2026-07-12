from __future__ import annotations

import json

from .workflow import run_demo


def main() -> None:
    print(json.dumps(run_demo(approved=True), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
