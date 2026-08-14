"""open.er-api.com client. Keyless everyday currency rates on any base."""

from __future__ import annotations

import math
from typing import Any

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.currency import constants


class CurrencyClient:
    """Async client for the ExchangeRate-API open endpoint."""

    async def latest(self, base: str) -> dict[str, Any]:
        """
        Fetch the latest rates for a base currency code.

        The endpoint is `/latest/{BASE}`. A successful body carries
        `result == "success"` plus a `rates` map keyed by ISO currency code.
        An unknown code returns HTTP 200 with `result == "error"` and an
        `error-type` field, so the caller inspects the body, not just the
        status code.
        """
        url = f"{constants.CURRENCY_API_BASE}/latest/{base}"
        async with HttpClient() as client:
            response = await client.get(url)
        if response.status_code == 204 or not response.content:
            raise HttpClientError(f"Empty response from {url}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise HttpClientError(f"Non-JSON body from {url}") from exc
        if not isinstance(payload, dict):
            raise HttpClientError(f"Invalid JSON shape from {url}: expected an object")
        if payload.get("result") == "success":
            rates = payload.get("rates")
            if not isinstance(rates, dict) or any(
                not isinstance(code, str)
                or isinstance(rate, bool)
                or not isinstance(rate, int | float)
                or not math.isfinite(rate)
                or rate < 0
                for code, rate in rates.items()
            ):
                raise HttpClientError(f"Invalid JSON shape from {url}: rates are malformed")
        return dict(payload)
