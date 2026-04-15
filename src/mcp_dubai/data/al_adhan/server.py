"""
Al-Adhan FastMCP server.

Thin wrappers over the pure functions in `tools.py`. Each wrapper carries
the docstring the LLM sees, and side-effects only at module import time
to register tool metadata with ToolDiscovery so `recommend_tools` can
surface them.
"""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.al_adhan import tools

mcp: FastMCP = FastMCP("al_adhan")


@mcp.tool
async def prayer_times_for(
    city: str | None = None,
    country: str = "United Arab Emirates",
    latitude: float | None = None,
    longitude: float | None = None,
    date_str: str | None = None,
    method: int = 8,
    school: int = 0,
) -> dict[str, object]:
    """
    Get the five daily prayer times for a UAE city or arbitrary coordinates.

    Pass either a city name OR a latitude+longitude pair, not both. The
    response includes Fajr, Sunrise, Dhuhr, Asr, Sunset, Maghrib, Isha, plus
    Imsak (start of fasting), Midnight, Firstthird, and Lastthird, along
    with the matching Hijri and Gregorian dates.

    Args:
        city: City name (default Dubai). Use this OR coordinates.
        country: Country name. Defaults to "United Arab Emirates".
        latitude: Latitude in decimal degrees, -90 to 90.
        longitude: Longitude in decimal degrees, -180 to 180.
        date_str: ISO date YYYY-MM-DD. Defaults to today.
        method: Calculation method ID. 8 = Gulf Region (default for UAE),
            16 = Dubai experimental (matches Dubai mosque announcements),
            4 = Umm Al-Qura Makkah, 3 = Muslim World League.
        school: Asr school. 0 = Shafi (default for UAE), 1 = Hanafi.

    Returns:
        Dict with `timings`, `date` (hijri + gregorian), and `meta`.
    """
    return await tools.prayer_times_for(
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
        date_str=date_str,
        method=method,
        school=school,
    )


@mcp.tool
async def prayer_times_calendar(
    city: str,
    month: int,
    year: int,
    country: str = "United Arab Emirates",
    method: int = 8,
    school: int = 0,
) -> dict[str, object]:
    """
    Get prayer times for an entire month in one call.

    Args:
        city: City name (e.g., "Dubai").
        month: Month number, 1 to 12.
        year: Gregorian year.
        country: Country name. Defaults to "United Arab Emirates".
        method: Calculation method ID. 8 = Gulf Region (default).
        school: Asr school. 0 = Shafi (default).

    Returns:
        List of daily entries, each with `timings` and `date`.
    """
    return await tools.prayer_times_calendar(
        city=city,
        month=month,
        year=year,
        country=country,
        method=method,
        school=school,
    )


@mcp.tool
async def qibla_direction(latitude: float, longitude: float) -> dict[str, object]:
    """
    Get the Qibla compass bearing from a given location toward Mecca.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.

    Returns:
        Dict with `latitude`, `longitude`, and `direction` in degrees
        (0 = north, 90 = east, etc.). For Dubai, the direction is around
        258 degrees (roughly west-southwest).
    """
    return await tools.qibla_direction(latitude=latitude, longitude=longitude)


@mcp.tool
async def hijri_to_gregorian(day: int, month: int, year: int) -> dict[str, object]:
    """
    Convert a Hijri (Islamic) date to a Gregorian date.

    Args:
        day: Hijri day, 1 to 30.
        month: Hijri month, 1 (Muharram) to 12 (Dhu al-Hijjah).
        year: Hijri year (e.g., 1447).

    Returns:
        Dict with `hijri` and `gregorian` blocks.
    """
    return await tools.hijri_to_gregorian(day=day, month=month, year=year)


@mcp.tool
async def gregorian_to_hijri(day: int, month: int, year: int) -> dict[str, object]:
    """
    Convert a Gregorian date to a Hijri (Islamic) date.

    Args:
        day: Gregorian day, 1 to 31.
        month: Gregorian month, 1 to 12.
        year: Gregorian year (e.g., 2026).

    Returns:
        Dict with `hijri` and `gregorian` blocks.
    """
    return await tools.gregorian_to_hijri(day=day, month=month, year=year)


# ----------------------------------------------------------------------------
# Register with ToolDiscovery so `recommend_tools` can surface us.
# Runs once at module import time. The reset_singletons fixture in the
# test suite drops these registrations between tests.
# ----------------------------------------------------------------------------
_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="prayer_times_for",
        description=(
            "Get the five daily prayer times (Fajr, Dhuhr, Asr, Maghrib, "
            "Isha) for a UAE city or arbitrary coordinates on a specific date."
        ),
        feature="al_adhan",
        tier=TIER_OPEN,
        tags=[
            "prayer",
            "salat",
            "salah",
            "fajr",
            "dhuhr",
            "asr",
            "maghrib",
            "isha",
            "imsak",
            "islamic",
            "muslim",
            "namaz",
            "dubai",
            "uae",
        ],
    ),
    ToolMeta(
        name="prayer_times_calendar",
        description="Get prayer times for an entire month in a single call.",
        feature="al_adhan",
        tier=TIER_OPEN,
        tags=[
            "prayer",
            "salat",
            "calendar",
            "month",
            "schedule",
            "islamic",
            "muslim",
            "ramadan",
        ],
    ),
    ToolMeta(
        name="qibla_direction",
        description="Get the compass bearing from a location to Mecca (the Qibla).",
        feature="al_adhan",
        tier=TIER_OPEN,
        tags=[
            "qibla",
            "qiblah",
            "mecca",
            "makkah",
            "kaaba",
            "compass",
            "direction",
            "bearing",
            "islamic",
            "muslim",
        ],
    ),
    ToolMeta(
        name="hijri_to_gregorian",
        description="Convert a Hijri (Islamic) date to a Gregorian calendar date.",
        feature="al_adhan",
        tier=TIER_OPEN,
        tags=[
            "hijri",
            "islamic",
            "calendar",
            "convert",
            "ramadan",
            "muharram",
            "lunar",
        ],
    ),
    ToolMeta(
        name="gregorian_to_hijri",
        description="Convert a Gregorian calendar date to a Hijri (Islamic) date.",
        feature="al_adhan",
        tier=TIER_OPEN,
        tags=[
            "gregorian",
            "hijri",
            "calendar",
            "convert",
            "islamic",
            "lunar",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
