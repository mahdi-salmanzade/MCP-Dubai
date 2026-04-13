"""WAQI / AQICN client."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.air_quality import constants
from mcp_dubai.data.air_quality.auth import get_waqi_token


class WaqiClient:
    """Async client for the WAQI feed API."""

    async def feed_by_station(self, station_path: str) -> dict[str, Any]:
        """Fetch a single station feed."""
        token = get_waqi_token()
        if token is None:
            raise RuntimeError("WAQI token is not configured")

        url = constants.FEED_BY_CITY.format(path=station_path)
        async with HttpClient() as client:
            response = await client.get(url, params={"token": token})
        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(f"WAQI API error: {payload.get('data', payload)}")
        result = payload.get("data", {})
        return result if isinstance(result, dict) else {}

    async def feed_by_coords(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Fetch the closest station feed for a given lat/lon."""
        token = get_waqi_token()
        if token is None:
            raise RuntimeError("WAQI token is not configured")

        url = constants.FEED_BY_GEO.format(lat=latitude, lon=longitude)
        async with HttpClient() as client:
            response = await client.get(url, params={"token": token})
        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(f"WAQI API error: {payload.get('data', payload)}")
        result = payload.get("data", {})
        return result if isinstance(result, dict) else {}
