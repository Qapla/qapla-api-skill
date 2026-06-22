#!/usr/bin/env python3
"""Thin client for the Qapla' API **v2** (the RESTful / Bearer-JWT generation).

Standard library only (Python 3.8+) — nothing to `pip install`. v2 is a different
beast from v1.x, and this client encapsulates the parts that are easy to get wrong
(mirrors references/v2/):

  1. AUTH IS A TWO-STEP FLOW. You don't send the API key on every call. You
     exchange it once at POST /v2/auth/token for a Bearer JWT (valid 24h), then
     send `Authorization: Bearer <token>`. This client caches the token and
     refreshes it automatically before expiry. The auth field is `apiKey`
     (camelCase) — NOT `api_key`.
  2. NO ENVELOPE. Success/failure is the HTTP status code (200/201/202/204 vs
     4xx/5xx); errors are RFC 7807 `application/problem+json`. `QaplaV2Error`
     carries the parsed `status`/`title`/`detail`/`violations`.
  3. BULK WRITES GO ASYNC. Creating >10 parcels returns 202 + a job; poll
     GET /v2/jobs/{jobId} until it's done. `poll_job()` does that for you.
  4. SCOPES ARE ENFORCED. A valid token missing the endpoint's scope → 403.

This is the v2 counterpart to qapla_client.py (which stays on v1.3). Read
references/v2/overview.md and references/v2/authentication.md for the full contract.

Use as a LIBRARY:
    from qapla_v2_client import QaplaV2Client, QaplaV2Error
    client = QaplaV2Client()                      # reads QAPLA_API_KEY from env
    status, body = client.create_parcels(
        order={"reference": "ORDER-123", "origin": "shopify"},
        parcels=[{"weightKg": 0.8, "lengthCm": 20, "widthCm": 15,
                  "heightCm": 10, "originCountryIso": "IT"}],
    )
    if status == 202:                             # >10 parcels -> async job
        result = client.poll_job(body["jobId"])

Use as a CLI connectivity test (exchanges a token and prints the granted scopes):
    QAPLA_API_KEY=xxxxx python3 qapla_v2_client.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.qapla.it"
API_PREFIX = "v2"

# 429 is transient (token bucket, refill ~2/sec). Same backoff shape as the v1
# client: 5 attempts, 1,2,4,8,16s.
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0
HTTP_TIMEOUT_SECONDS = 30
# Refresh the JWT this many seconds before it actually expires, to avoid racing
# the boundary on a slow call.
TOKEN_REFRESH_SKEW_SECONDS = 60


class QaplaV2Error(RuntimeError):
    """Raised on transport errors or any non-2xx v2 response. When the body is an
    RFC 7807 problem+json, its fields are parsed out for inspection."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        title: str | None = None,
        detail: str | None = None,
        violations: list | None = None,
    ):
        super().__init__(message)
        self.status = status
        self.title = title
        self.detail = detail
        self.violations = violations or []


class QaplaV2Client:
    def __init__(self, api_key: str | None = None, *, base_url: str = BASE_URL):
        self.api_key = api_key or os.environ.get("QAPLA_API_KEY")
        if not self.api_key:
            raise QaplaV2Error(
                "No API key. Pass api_key=... or set the QAPLA_API_KEY env var. "
                "The key is the per-channel Private API Key from the Qapla' "
                "Control Panel (Settings > Channels > [channel] > Private API Key)."
            )
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._token_expiry: float = 0.0  # epoch seconds
        self.scopes: list[str] = []

    # --- auth -------------------------------------------------------------

    def authenticate(self) -> dict:
        """Exchange the API key for a Bearer JWT. Caches the token and its expiry,
        records the granted scopes, and returns the raw token response dict."""
        status, body = self._raw_request(
            "POST", "auth/token", json_body={"apiKey": self.api_key}, _authed=False
        )
        if status != 200 or not isinstance(body, dict) or "token" not in body:
            raise QaplaV2Error(f"Token exchange failed (HTTP {status})", status=status)
        self._token = body["token"]
        # expires_in is seconds from now; refresh a bit early.
        expires_in = int(body.get("expires_in", 86400))
        self._token_expiry = time.time() + expires_in - TOKEN_REFRESH_SKEW_SECONDS
        self.scopes = list(body.get("scopes", []))
        return body

    def _bearer(self) -> str:
        """Return a valid token, (re)authenticating if missing or near expiry."""
        if self._token is None or time.time() >= self._token_expiry:
            self.authenticate()
        assert self._token is not None
        return self._token

    # --- transport --------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[int, object]:
        """Make an authenticated v2 call and return (http_status, parsed_body).

        `path` is relative to /v2 (e.g. "parcels", "jobs/abc123"). Raises
        QaplaV2Error on transport failure, exhausted 429 retries, or any non-2xx
        status (with the RFC 7807 fields parsed out). 204 returns (204, None)."""
        return self._raw_request(
            method, path, params=params, json_body=json_body, headers=headers, _authed=True
        )

    def _raw_request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
        headers: dict | None = None,
        _authed: bool = True,
    ) -> tuple[int, object]:
        url = f"{self.base_url}/{API_PREFIX}/{path.lstrip('/')}"
        if params:
            # Drop None values so optional params can be passed through cleanly.
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = f"{url}?{urllib.parse.urlencode(clean)}"

        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        if _authed:
            req_headers["Authorization"] = f"Bearer {self._bearer()}"
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        for attempt in range(MAX_RETRIES):
            req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                    return resp.status, _parse_body(resp.read(), resp.headers)
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < MAX_RETRIES - 1:
                    retry_after = exc.headers.get("X-RateLimit-Retry-After")
                    delay = float(retry_after) if retry_after else BACKOFF_BASE_SECONDS * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise _error_from_http(exc, method, path)
            except urllib.error.URLError as exc:
                raise QaplaV2Error(f"Network error on {method} {path}: {exc.reason}") from exc
        raise QaplaV2Error(
            f"Rate limited (429) on {method} {path} after {MAX_RETRIES} attempts", status=429
        )

    # --- convenience: parcels --------------------------------------------

    def create_parcels(
        self,
        *,
        order: dict,
        parcels: list,
        webhook_url: str | None = None,
        label_format: str | None = None,
    ) -> tuple[int, object]:
        """POST /v2/parcels. Returns (201, parcel(s)) for <=10 parcels (sync) or
        (202, AsyncJobResponse) for >10 (async). `label_format` is "PDF"|"ZPL"."""
        body: dict = {"order": order, "parcels": parcels}
        if webhook_url is not None:
            body["webhookUrl"] = webhook_url
        headers = {"x-label-format": label_format} if label_format else None
        return self.request("POST", "parcels", json_body=body, headers=headers)

    def list_parcels(
        self, *, order_reference: str, order_origin: str, page: int = 1, limit: int = 20
    ) -> tuple[int, object]:
        """GET /v2/parcels — the parcels of one order (paginated)."""
        return self.request(
            "GET",
            "parcels",
            params={
                "orderReference": order_reference,
                "orderOrigin": order_origin,
                "page": page,
                "limit": limit,
            },
        )

    def get_parcel(self, parcel_hash: str) -> tuple[int, object]:
        """GET /v2/parcels/{hash}."""
        return self.request("GET", f"parcels/{parcel_hash}")

    def update_parcel(self, parcel_hash: str, changes: dict) -> tuple[int, object]:
        """PATCH /v2/parcels/{hash} — partial update."""
        return self.request("PATCH", f"parcels/{parcel_hash}", json_body=changes)

    def delete_parcel(self, parcel_hash: str) -> tuple[int, object]:
        """DELETE /v2/parcels/{hash}. Returns (204, None) on success."""
        return self.request("DELETE", f"parcels/{parcel_hash}")

    # --- convenience: async jobs -----------------------------------------

    def get_job(self, job_id: str) -> tuple[int, object]:
        """GET /v2/jobs/{jobId} — one poll of an async job."""
        return self.request("GET", f"jobs/{job_id}")

    def poll_job(
        self, job_id: str, *, interval: float = 2.0, timeout: float = 300.0
    ) -> dict:
        """Poll GET /v2/jobs/{jobId} until status is completed/failed, then return
        the final job dict. Raises QaplaV2Error on timeout."""
        deadline = time.time() + timeout
        while True:
            _, job = self.get_job(job_id)
            status = job.get("status") if isinstance(job, dict) else None
            if status in ("completed", "failed"):
                return job  # type: ignore[return-value]
            if time.time() >= deadline:
                raise QaplaV2Error(
                    f"Job {job_id} did not finish within {timeout:.0f}s (last status: {status})"
                )
            time.sleep(interval)


def _parse_body(raw: bytes, headers) -> object:
    """Parse a successful response body. JSON when it looks like JSON, else text;
    empty body (e.g. 204) -> None."""
    if not raw:
        return None
    ctype = (headers.get("Content-Type") or "").lower()
    if "json" in ctype:
        return json.loads(raw.decode("utf-8"))
    text = raw.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _error_from_http(exc: urllib.error.HTTPError, method: str, path: str) -> QaplaV2Error:
    """Turn an HTTPError into a QaplaV2Error, parsing the RFC 7807 body if present."""
    title = detail = None
    violations: list = []
    try:
        payload = json.loads(exc.read().decode("utf-8"))
        if isinstance(payload, dict):
            title = payload.get("title")
            detail = payload.get("detail")
            violations = payload.get("violations") or []
    except Exception:  # noqa: BLE001 — body may be empty/non-JSON; fall back to reason
        pass
    msg = f"HTTP {exc.code} on {method} {path}"
    if title or detail:
        msg += f": {title or ''} {('- ' + detail) if detail else ''}".rstrip()
    else:
        msg += f": {exc.reason}"
    return QaplaV2Error(msg, status=exc.code, title=title, detail=detail, violations=violations)


def _connectivity_test() -> int:
    """CLI entry point: exchange a token and report the granted scopes."""
    try:
        client = QaplaV2Client()
        body = client.authenticate()
    except QaplaV2Error as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("OK: API key is valid; obtained a v2 Bearer token.")
    print(f"  token_type: {body.get('token_type')}")
    print(f"  expires_in: {body.get('expires_in')}s")
    print(f"  scopes:     {', '.join(body.get('scopes', [])) or '(none)'}")
    return 0


if __name__ == "__main__":
    sys.exit(_connectivity_test())
