"""FastMCP server for events."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.events import tools

mcp: FastMCP = FastMCP("events")


@mcp.tool
async def startup_events(category: str | None = None) -> dict[str, object]:
    """
    List Dubai and UAE startup and tech events.

    Args:
        category: Optional substring filter on event type or name.
    """
    return await tools.startup_events(category=category)


@mcp.tool
async def gitex_info() -> dict[str, object]:
    """Return GITEX Global 2026 details and venue (Dubai Exhibition Centre)."""
    return await tools.gitex_info()


@mcp.tool
async def ens_calendar() -> dict[str, object]:
    """
    Return Expand North Star 2026 calendar.

    Edition 11, 8 to 10 December 2026 at Dubai Exhibition Centre.
    Supernova 0X format with 3 venture tracks and USD 200K prize pool.
    Applications open 1 May 2026, close 2 November 2026.
    """
    return await tools.ens_calendar()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="startup_events",
        description="List Dubai and UAE startup and tech events with dates, venues, and links.",
        feature="events",
        tier=TIER_BIZ,
        tags=[
            "event",
            "startup event",
            "conference",
            "expand north star",
            "ens",
            "gitex",
            "step",
            "aim congress",
            "world government summit",
            "dubai ai week",
        ],
    ),
    ToolMeta(
        name="gitex_info",
        description="GITEX Global 2026 details: world's largest tech and AI event in Dubai.",
        feature="events",
        tier=TIER_BIZ,
        tags=["gitex", "tech conference", "dwtc", "expo city", "dubai", "2026"],
    ),
    ToolMeta(
        name="ens_calendar",
        description="Expand North Star 2026 calendar, applications, and Supernova 0X format.",
        feature="events",
        tier=TIER_BIZ,
        tags=[
            "expand north star",
            "ens",
            "supernova",
            "0x",
            "december 2026",
            "dwtc",
            "kaoun",
            "expo city",
            "dubai",
            "startup event",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
