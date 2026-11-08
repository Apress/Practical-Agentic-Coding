"""Small JSON-over-HTTP helpers shared by the three demo services.

Standard library only. The services are deliberately simple: enough moving
parts to investigate, few enough lines to read in one sitting.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

# Default ports. Override with INVENTORY_PORT / PAYMENT_PORT / GATEWAY_PORT.
INVENTORY_PORT = int(os.environ.get("INVENTORY_PORT", "8081"))
PAYMENT_PORT = int(os.environ.get("PAYMENT_PORT", "8082"))
GATEWAY_PORT = int(os.environ.get("GATEWAY_PORT", "8080"))

INVENTORY_URL = os.environ.get("INVENTORY_URL", f"http://127.0.0.1:{INVENTORY_PORT}")
PAYMENT_URL = os.environ.get("PAYMENT_URL", f"http://127.0.0.1:{PAYMENT_PORT}")
GATEWAY_URL = os.environ.get("GATEWAY_URL", f"http://127.0.0.1:{GATEWAY_PORT}")


def get_logger(service: str) -> logging.Logger:
    """Console logger whose format matches the traces in starter/logs/."""
    logger = logging.getLogger(service)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03dZ %(levelname)s [" + service + "] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        formatter.converter = time.gmtime  # the trailing Z means UTC, so log in UTC
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class ServiceError(Exception):
    """Raised by a route handler to return a specific status and error code."""

    def __init__(self, status: int, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.status = status
        self.code = code
        self.message = message or code


class JsonHandler(BaseHTTPRequestHandler):
    """Dispatches GET/POST to a class-level route table.

    Subclasses set ``routes = {"/path": callable}``. Each callable takes a dict
    (JSON body for POST, query string for GET) plus the request headers, and
    returns a JSON-serializable dict.
    """

    routes: dict[str, Callable[[dict, dict], dict]] = {}
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        parsed = urllib.parse.urlparse(self.path)
        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
        self._dispatch(parsed.path, params)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._respond(400, {"error": "invalid_json"})
            return
        self._dispatch(urllib.parse.urlparse(self.path).path, payload)

    def _dispatch(self, path: str, payload: dict) -> None:
        handler = self.routes.get(path)
        if handler is None:
            self._respond(404, {"error": "not_found", "path": path})
            return
        try:
            self._respond(200, handler(payload, dict(self.headers)))
        except ServiceError as exc:
            self._respond(exc.status, {"error": exc.code, "message": exc.message})
        except Exception as exc:  # unexpected: surface as a 500, like production
            self._respond(500, {"error": "internal_error", "message": str(exc)})

    def _respond(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt: str, *args) -> None:
        """Silence the default access log; each service logs what matters."""


def serve(handler_cls: type[JsonHandler], port: int, logger: logging.Logger) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), handler_cls)
    logger.info("listening on 127.0.0.1:%d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("shutting down")
    finally:
        server.server_close()


class UpstreamTimeout(Exception):
    """The upstream service did not answer inside the deadline."""


class UpstreamError(Exception):
    """The upstream service answered with a non-2xx status."""

    def __init__(self, status: int, body: dict) -> None:
        super().__init__(f"{status}: {body}")
        self.status = status
        self.body = body


def post_json(url: str, payload: dict, timeout: float, headers: dict | None = None) -> dict:
    data = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            parsed = json.loads(body or b"{}")
        except json.JSONDecodeError:
            parsed = {"error": "unreadable_body"}
        raise UpstreamError(exc.code, parsed) from exc
    except (socket.timeout, TimeoutError) as exc:
        raise UpstreamTimeout(url) from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (socket.timeout, TimeoutError)):
            raise UpstreamTimeout(url) from exc
        raise
