"""FastMCP server for air_quality."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.air_quality import tools

mcp: FastMCP = FastMCP("air_quality")


@mcp.tool
async def air_quality_dubai(station: str = "karama") -> dict[str, object]:
    """
    Get real-time air quality for a Dubai station.

    Returns AQI, EPA category bucket, individual pollutants (PM2.5, PM10,
    NO2, SO2, CO, O3), and the dominant pollutant.

    Args:
        station: Station ID (`karama`, `jebel-ali-village`, `nad-al-shiba`).

    Returns:
        ToolResponse envelope. On success, `data` contains the AQI summary.
        On failure (no token, unknown station), `error` contains a structured
        descriptor.
    """
    return await tools.air_quality_dubai(station=station)


@mcp.tool
async def air_quality_by_coords(
    latitude: float,
    longitude: float,
) -> dict[str, object]:
    """
    Get air quality for the closest WAQI station to a given lat/lon.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
    """
    return await tools.air_quality_by_coords(latitude=latitude, longitude=longitude)


@mcp.tool
async def air_quality_dubai_stations() -> dict[str, object]:
    """List the supported Dubai air quality stations."""
    return await tools.air_quality_dubai_stations()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="air_quality_dubai",
        description=(
            "Real-time current air quality (AQI, PM2.5, PM10, NO2, SO2, CO, O3) "
            "for a Dubai monitoring station: Karama, Jebel Ali Village, or "
            "Nad Al Shiba."
        ),
        feature="air_quality",
        tier=TIER_OPEN,
        requires_auth=True,
        tags=[
            "air",
            "quality",
            "aqi",
            "pollution",
            "pm2.5",
            "pm10",
            "no2",
            "so2",
            "ozone",
            "dubai",
            "smog",
            "health",
            "current",
            "real-time",
            "karama",
            "jebel ali village",
            "nad al shiba",
        ],
    ),
    ToolMeta(
        name="air_quality_by_coords",
        description="Real-time air quality at the WAQI station closest to a lat/lon.",
        feature="air_quality",
        tier=TIER_OPEN,
        requires_auth=True,
        tags=[
            "air",
            "quality",
            "aqi",
            "coordinates",
            "near",
            "closest",
            "geo",
        ],
    ),
    ToolMeta(
        name="air_quality_dubai_stations",
        description="List the curated Dubai air quality stations.",
        feature="air_quality",
        tier=TIER_OPEN,
        requires_auth=False,
        tags=["air", "quality", "stations", "list", "dubai"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
