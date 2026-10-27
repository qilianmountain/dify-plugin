"""Local transport for two real BrowserAct tool services; not a Dify runtime."""

import argparse
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from provider import TOOLS
from shared.client import ApiError, BrowserActClient

ROOT = Path(__file__).resolve().parent
ROUTE = re.compile(r"/api/tools/([a-z_]+)/(options|invoke)")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_data(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def reply(self, status, obj):
        self.send_data(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def local_request(self):
        expected = f"127.0.0.1:{self.server.server_port}"
        return self.headers.get("Host") == expected and self.headers.get("Origin", f"http://{expected}") == f"http://{expected}"

    def do_GET(self):
        if not self.local_request():
            return self.reply(403, {"error": "Only this local demo origin is allowed."})
        if self.path == "/api/tools":
            return self.reply(200, {"tools": [{"name": tool.name, "label": tool.label} for tool in TOOLS.values()]})
        files = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/app.js": ("app.js", "application/javascript; charset=utf-8")}
        if self.path not in files:
            return self.reply(404, {"error": "Not found"})
        name, kind = files[self.path]
        self.send_data(200, (ROOT / name).read_bytes(), kind)

    def do_POST(self):
        if not self.local_request():
            return self.reply(403, {"error": "Request not allowed"})
        match = ROUTE.fullmatch(self.path)
        if not match or match[1] not in TOOLS:
            return self.reply(404, {"error": "Unknown tool or action"})
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer ") or not authorization[7:].strip():
            return self.reply(401, {"error": "Enter your BrowserAct API Key."})
        client = BrowserActClient(authorization[7:])
        started = time.monotonic()
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                raise ApiError("Request too large or empty", 413)
            parameters = json.loads(self.rfile.read(length))
            if not isinstance(parameters, dict):
                raise ApiError("Parameters must be a JSON object.")
            tool, action = TOOLS[match[1]], match[2]
            if action == "options":
                result = {"options": tool.list_options(client)}
            else:
                result = {"result": tool.invoke(client, parameters)}
            result.update(api_calls=client.calls, elapsed_seconds=round(time.monotonic()-started, 3))
            self.reply(200, result)
        except ApiError as error:
            message = str(error).replace(authorization[7:], "[REDACTED]")
            self.reply(error.status, {"error": message, "api_calls": client.calls})
        except (ValueError, TypeError, KeyError, AttributeError):
            self.reply(400, {"error": "The request or API response format is invalid.", "api_calls": client.calls})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1840)
    options = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", options.port), Handler)
    print(f"BrowserAct live demo: http://127.0.0.1:{server.server_port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
