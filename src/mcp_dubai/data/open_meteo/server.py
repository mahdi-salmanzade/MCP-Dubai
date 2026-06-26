"""FastMCP server for open_meteo (keyless human weather and forecast)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.open_meteo import tools

mcp: FastMCP = FastMCP("open_meteo")


@mcp.tool
async def uae_weather(city: str = "Dubai") -> dict[str, object]:
    """
    Current weather and today's high/low for a UAE city (no API key needed).

    Covers plain temperature, feels-like, humidity, wind, and conditions,
    the everyday weather that the METAR/TAF `aviation_weather` tools do not
    present in a human-friendly way.

    Args:
        city: A UAE city. Supported: Dubai, Abu Dhabi, Sharjah, Ajman,
            Ras Al Khaimah, Fujairah, Umm Al Quwain, Al Ain.
    """
    return await tools.uae_weather(city=city)


@mcp.tool
async def uae_weather_forecast(city: str = "Dubai", days: int = 7) -> dict[str, object]:
    """
    Multi-day daily weather forecast for a UAE city (no API key needed).

    Args:
        city: A UAE city (see `uae_weather`).
        days: Number of forecast days, 1 to 16 (clamped to range).
    """
    return await tools.uae_weather_forecast(city=city, days=days)


@mcp.tool
async def weather_by_coords(
    latitude: float,
    longitude: float,
    days: int = 3,
) -> dict[str, object]:
    """
    Current weather plus a short forecast for any latitude/longitude.

    Args:
        latitude: Latitude, -90 to 90.
        longitude: Longitude, -180 to 180.
        days: Number of forecast days, 1 to 16 (clamped to range).
    """
    return await tools.weather_by_coords(latitude=latitude, longitude=longitude, days=days)


@mcp.tool
async def list_uae_weather_cities() -> dict[str, object]:
    """List the UAE cities supported by the Open-Meteo weather tools."""
    return await tools.list_uae_weather_cities()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="uae_weather",
        description=(
            "Current weather (temperature, feels-like, humidity, wind, "
            "conditions) and today's high/low for a UAE city via Open-Meteo. "
            "Keyless. The human-friendly companion to aviation_weather."
        ),
        feature="open_meteo",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "temperature",
            "humidity",
            "wind",
            "forecast",
            "hot",
            "rain",
            "dubai",
            "abu dhabi",
            "sharjah",
            "uae",
            "today",
            "feels like",
            "open-meteo",
        ],
    ),
    ToolMeta(
        name="uae_weather_forecast",
        description=(
            "Multi-day daily weather forecast (highs, lows, rain chance, UV, "
            "wind) for a UAE city via Open-Meteo. Keyless, up to 16 days."
        ),
        feature="open_meteo",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "forecast",
            "7 day",
            "week",
            "temperature",
            "rain",
            "uv index",
            "humidity",
            "wind",
            "dubai",
            "uae",
            "open-meteo",
        ],
    ),
    ToolMeta(
        name="weather_by_coords",
        description="Current weather and a short forecast for any latitude/longitude via Open-Meteo.",
        feature="open_meteo",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "forecast",
            "coordinates",
            "latitude",
            "longitude",
            "location",
            "temperature",
            "open-meteo",
        ],
    ),
    ToolMeta(
        name="list_uae_weather_cities",
        description="List the UAE cities supported by the Open-Meteo weather tools.",
        feature="open_meteo",
        tier=TIER_OPEN,
        tags=[
            "weather",
            "cities",
            "list",
            "supported",
            "uae",
            "open-meteo",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
