"""FastMCP server for the holidays feature."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.holidays import tools

mcp: FastMCP = FastMCP("holidays")


@mcp.tool
async def uae_holidays(year: int = 2026) -> dict[str, object]:
    """
    List all UAE federal public holidays for a Gregorian year.

    Lunar holidays (Eid al-Fitr, Eid al-Adha, Hijri New Year, Mawlid,
    Arafat Day) are returned with `provisional: true` until the relevant
    MOHRE and FAHR observance circulars are published. Every lunar record
    carries `official_observance_announced`; false identifies a religious-
    date candidate rather than a confirmed day off.

    Args:
        year: Gregorian year. Currently 2026 and 2027 are shipped
            (2027 lunar dates are astronomical expectations).

    Returns:
        Dict with `year`, `holidays` list, and `note` (plus `dataset_note`
        for years without an official Cabinet calendar).
    """
    return await tools.uae_holidays(year=year)


@mcp.tool
async def uae_next_holiday(from_date_str: str | None = None) -> dict[str, object]:
    """
    Find the next confirmed UAE public holiday on or after a reference date.

    An earlier unannounced lunar-date candidate is returned separately as
    `next_provisional_candidate`; it is not presented as a confirmed day off.

    Args:
        from_date_str: ISO date YYYY-MM-DD. Defaults to today.

    Returns:
        Dict with `from_date`, confirmed `next_holiday`, `days_away`, and
        provisional candidate metadata when relevant.
    """
    return await tools.uae_next_holiday(from_date_str=from_date_str)


@mcp.tool
async def is_uae_holiday(date_str: str) -> dict[str, object]:
    """
    Check whether a specific Gregorian date is a UAE public holiday.

    Args:
        date_str: ISO date YYYY-MM-DD.

    Returns:
        Dict with `date`, tri-state `is_holiday`, `determination`, and
        `holiday`. `is_holiday` is null for an unannounced provisional date.
    """
    return await tools.is_uae_holiday(date_str=date_str)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="uae_holidays",
        description="List all UAE federal public holidays for a Gregorian year.",
        feature="holidays",
        tier=TIER_OPEN,
        tags=[
            "uae",
            "holiday",
            "holidays",
            "public",
            "national",
            "calendar",
            "eid",
            "ramadan",
            "national day",
            "commemoration",
            "mohre",
        ],
    ),
    ToolMeta(
        name="uae_next_holiday",
        description=(
            "Find the next confirmed UAE public holiday and flag any earlier "
            "provisional lunar-date candidate."
        ),
        feature="holidays",
        tier=TIER_OPEN,
        tags=["uae", "holiday", "next", "upcoming", "soon", "vacation", "off"],
    ),
    ToolMeta(
        name="is_uae_holiday",
        description="Check whether a specific date is a UAE public holiday.",
        feature="holidays",
        tier=TIER_OPEN,
        tags=["uae", "holiday", "check", "is", "date", "off", "weekend"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
