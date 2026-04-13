"""FastMCP server for RTA."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_DUBAI_PULSE,
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.rta import tools

mcp: FastMCP = FastMCP("rta")


@mcp.tool
async def rta_search_metro_stations(
    line: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search Dubai Metro stations via Dubai Pulse.

    Tier 1, requires Dubai Pulse credentials.

    Args:
        line: Optional line filter (Red, Green, Route 2020).
        limit: Max records.
    """
    return await tools.rta_search_metro_stations(line=line, limit=limit)


@mcp.tool
async def rta_search_bus_routes(
    route_number: str | None = None,
    origin: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search Dubai bus routes via Dubai Pulse.

    Tier 1, requires Dubai Pulse credentials.
    """
    return await tools.rta_search_bus_routes(route_number=route_number, origin=origin, limit=limit)


@mcp.tool
async def rta_salik_tariff() -> dict[str, object]:
    """
    Return Salik toll tariff reference data.

    Tier 1, requires Dubai Pulse credentials.

    Only the tariff is public. Account balances, trips, and violations
    are NOT exposed via any public API.
    """
    return await tools.rta_salik_tariff()


@mcp.tool
async def rta_gtfs_static_url() -> dict[str, object]:
    """
    Return the URL for the RTA GTFS static feed.

    The Transitland mirror is anonymous and works without any credentials.
    No GTFS-RT (real-time) feed exists for Dubai RTA.
    """
    return await tools.rta_gtfs_static_url()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="rta_search_metro_stations",
        description="Search Dubai Metro stations (Red, Green, Route 2020) via Dubai Pulse.",
        feature="rta",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=[
            "rta",
            "metro",
            "dubai metro",
            "red line",
            "green line",
            "route 2020",
            "station",
            "transit",
            "transport",
            "dubai pulse",
        ],
    ),
    ToolMeta(
        name="rta_search_bus_routes",
        description="Search Dubai bus routes via Dubai Pulse.",
        feature="rta",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=["rta", "bus", "route", "dubai", "transit", "transport", "dubai pulse"],
    ),
    ToolMeta(
        name="rta_salik_tariff",
        description="Salik toll tariff reference (the only public Salik dataset).",
        feature="rta",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=["salik", "toll", "rta", "tariff", "dubai", "dubai pulse"],
    ),
    ToolMeta(
        name="rta_gtfs_static_url",
        description="GTFS static feed URL for Dubai RTA (Transitland mirror is anonymous).",
        feature="rta",
        tier=TIER_OPEN,
        requires_auth=False,
        tags=["gtfs", "rta", "transit feed", "transitland", "static", "feed"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
