"""open.er-api.com client. Keyless everyday currency rates on any base."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
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
            return {}
        payload = response.json()
        return dict(payload) if isinstance(payload, dict) else {}
