from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .api import demo_import_payload, golden_flow_payload, health_payload, source_registry_payload


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(health_payload())
            return
        if self.path == "/demo/golden-flow":
            self._json(golden_flow_payload(approved=True))
            return
        if self.path == "/sources":
            self._json(source_registry_payload())
            return
        if self.path == "/imports/demo":
            self._json(demo_import_payload())
            return
        self._json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:
        if self.path not in {"/demo/run", "/demo/golden-flow/run"}:
            self._json({"error": "not_found"}, status=404)
            return

        length = int(self.headers.get("content-length", "0"))
        payload = {}
        if length:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        approved = bool(payload.get("approved", True))
        self._json(golden_flow_payload(approved=approved))

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
