"""Air quality tool functions with graceful credential degradation."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.air_quality import constants
from mcp_dubai.data.air_quality.auth import waqi_availability
from mcp_dubai.data.air_quality.client import WaqiClient


def _format_aqi_summary(data: dict[str, Any]) -> dict[str, object]:
    """Extract a friendly summary from a WAQI feed payload."""
    aqi = data.get("aqi")
    iaqi = data.get("iaqi", {})

    pollutants: dict[str, float] = {}
    for key, value in iaqi.items():
        if isinstance(value, dict) and "v" in value:
            try:
                pollutants[key] = float(value["v"])
            except (TypeError, ValueError):
                continue

    return {
        "station_name": data.get("city", {}).get("name"),
        "aqi": aqi,
        "category": _aqi_category(aqi) if isinstance(aqi, (int, float)) else None,
        "pollutants": pollutants,
        "dominant_pollutant": data.get("dominentpol"),
        "time": data.get("time", {}).get("iso"),
        "attribution": (
            "Air quality data from the World Air Quality Index project, "
            "https://aqicn.org. Free for non-commercial use, attribution required."
        ),
    }


def _aqi_category(aqi: int | float) -> str:
    """US EPA AQI bucket name."""
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


async def air_quality_dubai(
    station: str = constants.DEFAULT_STATION,
) -> dict[str, object]:
    """
    Get real-time air quality for a Dubai station.

    Returns the standard ToolResponse envelope. If MCP_DUBAI_WAQI_TOKEN is
    not configured, returns `success=False` with a structured error.
    """
    avail = waqi_availability()
    if avail["status"] != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()

    if station not in constants.DUBAI_STATIONS:
        return (
            ToolResponse[dict[str, object]]
            .fail(
                error=(
                    f"Unknown Dubai station {station!r}. Valid: "
                    f"{sorted(constants.DUBAI_STATIONS.keys())}"
                )
            )
            .model_dump()
        )

    client = WaqiClient()
    raw = await client.feed_by_station(f"dubai/{station}")
    summary = _format_aqi_summary(raw)
    return ToolResponse[dict[str, object]].ok(summary).model_dump()


async def air_quality_by_coords(
    latitude: float,
    longitude: float,
) -> dict[str, object]:
    """
    Get air quality for the WAQI station closest to a lat/lon.

    Useful when you want air quality near a specific Dubai location.
    """
    if not -90 <= latitude <= 90:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"latitude must be -90 to 90, got {latitude}")
            .model_dump()
        )
    if not -180 <= longitude <= 180:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"longitude must be -180 to 180, got {longitude}")
            .model_dump()
        )

    avail = waqi_availability()
    if avail["status"] != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()

    client = WaqiClient()
    raw = await client.feed_by_coords(latitude, longitude)
    summary = _format_aqi_summary(raw)
    return ToolResponse[dict[str, object]].ok(summary).model_dump()


async def air_quality_dubai_stations() -> dict[str, object]:
    """List the curated Dubai air quality stations supported by this feature."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(constants.DUBAI_STATIONS),
                "stations": [
                    {"id": sid, "name": name} for sid, name in constants.DUBAI_STATIONS.items()
                ],
            }
        )
        .model_dump()
    )
