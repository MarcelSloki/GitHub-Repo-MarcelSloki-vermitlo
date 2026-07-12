from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .workflow import run_demo
from .storage import WorkflowStore


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"status": "ok", "service": "vermitlo-mvp"})
            return
        if self.path == "/runs":
            self._json({"runs": WorkflowStore().list_workflow_runs()})
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
        result = run_demo(approved=approved)
        run_id = WorkflowStore().save_workflow_run(result)
        self._json({"run_id": run_id, **result})

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
