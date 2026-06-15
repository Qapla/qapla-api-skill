#!/usr/bin/env python3
"""Thin client for the Qapla' public REST API (v1.3).

Standard library only (no third-party packages) so it runs anywhere Python 3.8+
is available — nothing to `pip install`. It encapsulates the two things every
Qapla' call needs and that are easy to get wrong:

  1. The response envelope is TWO-LEVEL. There is a top-level `result`/`error`
     AND, for batch endpoints (pushShipment, pushOrder), a per-item
     `result`/`error` inside the returned array. A call can be "OK" overall
     while individual items are "KO". `split_batch()` separates them for you.
  2. Rate limiting is a token bucket (capacity 120, refill 2 tokens/sec); going
     over returns HTTP 429. `call()` retries 429 with exponential backoff.

This mirrors the rules documented in references/conventions.md and
references/authentication.md — read those for the full contract.

Use as a LIBRARY:
    from qapla_client import QaplaClient, QaplaError
    client = QaplaClient()                       # reads QAPLA_API_KEY from env
    resp = client.call("pushShipment", {"pushShipment": [{...}]})
    ok, failed = client.split_batch(resp, "pushShipment", "shipments")

Use as a CLI connectivity test (calls getChannel, the cheapest read):
    QAPLA_API_KEY=xxxxx python3 qapla_client.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://api.qapla.it"
DEFAULT_VERSION = "1.3"

# 429 is transient: the bucket refills at 2 tokens/sec, so the worst-case wait
# to clear a full 120-token burst is ~60s. Five attempts with exponential
# backoff (1,2,4,8,16s -> ~31s total) clears typical bursts without hanging.
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0
HTTP_TIMEOUT_SECONDS = 30  # getQuotes/createLabel hit live carriers and are slow


class QaplaError(RuntimeError):
    """Raised when a Qapla' call fails at the transport level or returns a
    top-level result == "KO". Per-item failures in a batch are NOT raised here —
    inspect them with split_batch()."""


class QaplaClient:
    def __init__(self, api_key: str | None = None, *, version: str = DEFAULT_VERSION):
        self.api_key = api_key or os.environ.get("QAPLA_API_KEY")
        if not self.api_key:
            raise QaplaError(
                "No API key. Pass api_key=... or set the QAPLA_API_KEY env var. "
                "The key is the per-channel Private API Key from the Qapla' "
                "Control Panel (Settings > Channels > [channel] > Private API Key)."
            )
        self.version = version

    def call(self, endpoint: str, payload: dict, *, version: str | None = None) -> dict:
        """POST `payload` to `endpoint` and return the parsed response dict.

        `apiKey` is injected automatically — do not put it in `payload`.
        Raises QaplaError on transport errors, exhausted 429 retries, or a
        top-level result == "KO".

        Note: getPudos is only served under /1.2/ — pass version="1.2" for it.
        """
        ver = version or self.version
        url = f"{BASE_URL}/{ver}/{endpoint}"
        body = {"apiKey": self.api_key, **payload}
        data = json.dumps(body).encode("utf-8")

        for attempt in range(MAX_RETRIES):
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}, method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                    parsed = json.loads(resp.read().decode("utf-8"))
                    break
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE_SECONDS * (2 ** attempt))
                    continue
                raise QaplaError(f"HTTP {exc.code} calling {endpoint}: {exc.reason}") from exc
            except urllib.error.URLError as exc:
                raise QaplaError(f"Network error calling {endpoint}: {exc.reason}") from exc
        else:  # loop exhausted without break -> all retries were 429
            raise QaplaError(f"Rate limited (429) on {endpoint} after {MAX_RETRIES} attempts")

        # The response is wrapped in a key equal to the endpoint name.
        inner = parsed.get(endpoint, parsed)
        if isinstance(inner, dict) and inner.get("result") == "KO":
            raise QaplaError(f"{endpoint} returned KO: {inner.get('error')}")
        return parsed

    @staticmethod
    def split_batch(response: dict, endpoint: str, items_key: str):
        """Split a batch response into (ok_items, failed_items) by each item's
        own `result`. `items_key` is the array field, e.g. "shipments" for
        pushShipment. Returns two lists of item dicts."""
        inner = response.get(endpoint, {})
        items = inner.get(items_key, []) if isinstance(inner, dict) else []
        ok = [it for it in items if it.get("result") == "OK"]
        failed = [it for it in items if it.get("result") == "KO"]
        return ok, failed


def _connectivity_test() -> int:
    """CLI entry point: call getChannel and report whether the key works."""
    try:
        client = QaplaClient()
        resp = client.call("getChannel", {})
    except QaplaError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    inner = resp.get("getChannel", resp)
    print("OK: API key is valid and the channel is reachable.")
    print(json.dumps(inner, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_connectivity_test())
