from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .storage import AuditStore
from .workflow import run_demo


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"status": "ok", "service": "vermitlo-mvp"})
            return
        self._json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:
        if self.path != "/demo/run":
            self._json({"error": "not_found"}, status=404)
            return

        length = int(self.headers.get("content-length", "0"))
        payload = {}
        if length:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        approved = bool(payload.get("approved", True))
        no_go = bool(payload.get("no_go", False))
        result = run_demo(approved=approved, no_go=no_go)
        db_path = payload.get("db_path")
        if db_path:
            run_id = AuditStore(str(db_path)).save_demo_run(result)
            result["audit_persistence"] = {"db_path": str(db_path), "run_id": run_id}
        self._json(result)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Vermitlo MVP server listening on http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
