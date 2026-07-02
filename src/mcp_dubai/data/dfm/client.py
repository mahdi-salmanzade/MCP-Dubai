"""api2.dfm.ae client. Keyless Dubai Financial Market JSON endpoints."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.dfm import constants


def _decode_json(response: httpx.Response, url: str) -> object:
    """Decode a JSON body, converting non-JSON 200s into HttpClientError."""
    try:
        return response.json()
    except ValueError as exc:
        raise HttpClientError(f"Non-JSON body from {url}: {exc}") from exc


class DfmClient:
    """Async client for the undocumented dfm.ae market-data endpoints."""

    async def indices(self) -> list[dict[str, Any]]:
        """
        Fetch intraday DFM General Index records, newest first.

        Each record carries `id` (an ISO minute timestamp), `change`,
        `changepercentage`, `value`, and `volume`.
        """
        async with HttpClient() as client:
            response = await client.get(constants.INDICES_URL)
        if response.status_code == 204 or not response.content:
            return []
        return self._as_records(_decode_json(response, constants.INDICES_URL))

    async def stocks(self) -> list[dict[str, Any]]:
        """
        Fetch every listed security (~450 records, ~47 fields each).

        The server ignores query parameters, so callers filter client-side.
        The ticker symbol lives in `id`; `name` is null upstream today.
        """
        async with HttpClient() as client:
            response = await client.get(constants.STOCKS_URL)
        if response.status_code == 204 or not response.content:
            return []
        return self._as_records(_decode_json(response, constants.STOCKS_URL))

    @staticmethod
    def _as_records(payload: object) -> list[dict[str, Any]]:
        """Keep only dict entries; the endpoints return bare JSON arrays."""
        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]
