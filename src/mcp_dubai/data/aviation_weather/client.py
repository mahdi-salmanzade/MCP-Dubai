"""aviationweather.gov client. Returns parsed JSON when format=json is supported."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.aviation_weather import constants


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
        payload = response.json()
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        return []

    async def get_taf(self, icaos: list[str]) -> list[dict[str, Any]]:
        """Get TAF (terminal aerodrome forecast) for one or more ICAO codes."""
        params = {
            "ids": ",".join(icaos),
            "format": "json",
        }
        async with HttpClient() as client:
            response = await client.get(constants.TAF_ENDPOINT, params=params)
        payload = response.json()
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        return []
