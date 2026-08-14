"""aviationweather.gov client. Returns parsed JSON when format=json is supported."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.aviation_weather import constants


def _decode_records(response: httpx.Response, endpoint: str) -> list[dict[str, Any]]:
    """Decode a JSON record array while preserving legitimate no-data responses."""
    if response.status_code == 204 or not response.content:
        return []
    try:
        payload = response.json()
    except ValueError as exc:
        raise HttpClientError(f"Non-JSON body from {endpoint}") from exc
    if not isinstance(payload, list):
        raise HttpClientError(f"Invalid JSON shape from {endpoint}: expected a list")
    if any(not isinstance(item, dict) for item in payload):
        raise HttpClientError(f"Invalid JSON shape from {endpoint}: list contains a non-object")
    return [dict(item) for item in payload]


class AviationWeatherClient:
    """Async client for the aviationweather.gov data API."""

    async def get_metar(self, icaos: list[str]) -> list[dict[str, Any]]:
        """
        Get METAR observations for one or more ICAO codes.

        aviationweather.gov accepts comma-separated station IDs.
        """
        params = {
            "ids": ",".join(icaos),
            "format": "json",
        }
        async with HttpClient() as client:
            response = await client.get(constants.METAR_ENDPOINT, params=params)
        return _decode_records(response, constants.METAR_ENDPOINT)

    async def get_taf(self, icaos: list[str]) -> list[dict[str, Any]]:
        """Get TAF (terminal aerodrome forecast) for one or more ICAO codes."""
        params = {
            "ids": ",".join(icaos),
            "format": "json",
        }
        async with HttpClient() as client:
            response = await client.get(constants.TAF_ENDPOINT, params=params)
        return _decode_records(response, constants.TAF_ENDPOINT)
