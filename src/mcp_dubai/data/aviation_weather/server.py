"""FastMCP server for aviation_weather."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.aviation_weather import tools

mcp: FastMCP = FastMCP("aviation_weather")


@mcp.tool
async def weather_uae_icao(
    icao: str,
    include_taf: bool = True,
) -> dict[str, object]:
    """
    Get METAR (current weather observation) and optional TAF (forecast)
    for a UAE airport.

    Args:
        icao: ICAO code. Valid: OMDB (Dubai International), OMDW (Al Maktoum),
            OMSJ (Sharjah), OMAA (Abu Dhabi), OMAL (Al Ain), OMRK (Ras Al Khaimah).
        include_taf: If True, fetch the TAF forecast as well.

    Returns:
        Dict with `icao`, `airport`, `metar`, and optional `taf`.
    """
    return await tools.weather_uae_icao(icao=icao, include_taf=include_taf)


@mcp.tool
async def weather_uae_all(include_taf: bool = False) -> dict[str, object]:
    """
    Get METAR observations for all 6 UAE airports in a single call.

    Args:
        include_taf: If True, also fetch TAF forecasts (slower).
    """
    return await tools.weather_uae_all(include_taf=include_taf)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="weather_uae_icao",
        description=(
            "METAR (current weather) and TAF (forecast) for a UAE airport "
            "(OMDB Dubai, OMDW Al Maktoum, OMSJ Sharjah, OMAA Abu Dhabi, "
            "OMAL Al Ain, OMRK RAK)."
        ),
        feature="aviation_weather",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "metar",
            "taf",
            "airport",
            "aviation",
            "uae",
            "dubai",
            "abu dhabi",
            "sharjah",
            "wind",
            "temperature",
            "visibility",
            "forecast",
        ],
    ),
    ToolMeta(
        name="weather_uae_all",
        description="METAR observations for all 6 UAE international airports in one call.",
        feature="aviation_weather",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "metar",
            "uae",
            "airports",
            "all",
            "list",
            "aviation",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
