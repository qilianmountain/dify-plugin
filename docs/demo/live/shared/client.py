import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class BrowserActClient:
    """Fixed-host HTTP client. Keys exist only in request/process memory."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.calls = []

    def request(self, method, path, body=None, timeout=30):
        if timeout <= 0:
            raise ApiError("The wait timed out; the remote task may still be running.", 408)
        request = Request(
            "https://api.browseract.com" + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Authorization": "Bearer " + self.api_key,
                     "api-channel-ak": "difyak",
                     "Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            try:
                with build_opener(NoRedirect()).open(request, timeout=min(30, timeout)) as response:
                    status, raw = response.status, response.read()
            except HTTPError as error:
                status, raw = error.code, error.read()
        except (URLError, TimeoutError, OSError):
            suffix = "Task creation is uncertain. Check BrowserAct before resubmitting." if method == "POST" else ""
            raise ApiError("The BrowserAct request failed or timed out. " + suffix, 502) from None
        self.calls.append({"method": method, "path": path, "status": status})
        print(f"BrowserAct {method} {path} -> HTTP {status}", flush=True)
        raw = raw.replace(self.api_key.encode(), b"[REDACTED]")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ApiError(f"BrowserAct returned a non-JSON response, HTTP {status}", 502) from None
        if not 200 <= status < 300:
            message = data.get("message") or data.get("msg") or "API request failed" if isinstance(data, dict) else "API request failed"
            code = data.get("code") if isinstance(data, dict) else None
            raise ApiError(f"HTTP {status}: {message}" + (f" (code={code})" if code else ""), status)
        return data
