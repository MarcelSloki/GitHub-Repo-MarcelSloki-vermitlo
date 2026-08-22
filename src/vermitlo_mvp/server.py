from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .workflow import run_demo


def demo_overview_payload() -> dict:
    return {
        "current_goal": "Make the existing Vermitlo MVP core visible through one local UI and backend runtime.",
        "flow": [
            "Company profile",
            "Tender import",
            "Requirement analysis",
            "Match and K.O. criteria",
            "Pricing preparation",
            "Reference selection",
            "Offer dossier",
            "Human approval",
            "Submission simulation",
            "Outcome and billing simulation",
        ],
        "boundaries": [
            "Synthetic data is used for the current demo path.",
            "No real tender portal submission is executed.",
            "No real customer payment is charged.",
        ],
    }


def bind_address_from_env() -> tuple[str, int]:
    host = os.environ.get("VERMITLO_HOST", "127.0.0.1")
    port = int(os.environ.get("VERMITLO_PORT", "8000"))
    return host, port


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_common_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"status": "ok", "service": "vermitlo-mvp"})
            return
        if self.path == "/demo/overview":
            self._json(demo_overview_payload())
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
        self._json(run_demo(approved=approved))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_common_headers(self) -> None:
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host, port = bind_address_from_env()
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Vermitlo MVP server listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
