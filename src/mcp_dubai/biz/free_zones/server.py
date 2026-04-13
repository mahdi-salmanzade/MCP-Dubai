"""FastMCP server for free_zones."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.free_zones import tools

mcp: FastMCP = FastMCP("free_zones")


@mcp.tool
async def list_free_zones() -> dict[str, object]:
    """
    List every Dubai free zone in the curated dataset.

    Returns a compact list with id, name, sector, location, and initial
    license cost in AED.
    """
    return await tools.list_free_zones()


@mcp.tool
async def free_zone_details(free_zone_id: str) -> dict[str, object]:
    """
    Get the full curated record for a single free zone by id.

    Args:
        free_zone_id: Free zone id slug (e.g., "ifza", "dmcc",
            "difc_innovation", "jafza", "dafza", "meydan", "dubai_south",
            "dso_dtec", "tecom", "dhcc", "dpc_dsc", "difc_full").
    """
    return await tools.free_zone_details(free_zone_id=free_zone_id)


@mcp.tool
async def compare_free_zones(
    activity: str | None = None,
    budget_aed: int | None = None,
    visa_count: int = 1,
    needs_physical_office: bool = False,
    sector: str | None = None,
    limit: int = 5,
) -> dict[str, object]:
    """
    Compare Dubai free zones for a specific use case and return a ranked
    shortlist.

    Args:
        activity: Optional activity description (informational).
        budget_aed: Filter to free zones with initial license at or under this.
        visa_count: Minimum visa quota required.
        needs_physical_office: True to exclude virtual-only zones.
        sector: Optional sector substring filter (e.g., "tech", "healthcare").
        limit: Maximum results (1 to 50).
    """
    return await tools.compare_free_zones(
        activity=activity,
        budget_aed=budget_aed,
        visa_count=visa_count,
        needs_physical_office=needs_physical_office,
        sector=sector,
        limit=limit,
    )


@mcp.tool
async def list_offshore() -> dict[str, object]:
    """List Dubai-relevant offshore options (JAFZA Offshore, RAK ICC)."""
    return await tools.list_offshore()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="list_free_zones",
        description="List every Dubai free zone with id, name, sector, and initial license cost.",
        feature="free_zones",
        tier=TIER_BIZ,
        tags=["free zone", "list", "all", "dubai", "dmcc", "difc", "ifza", "jafza", "dafza"],
    ),
    ToolMeta(
        name="free_zone_details",
        description="Get the full curated record for a specific Dubai free zone by id.",
        feature="free_zones",
        tier=TIER_BIZ,
        tags=["free zone", "details", "lookup", "ifza", "dmcc", "difc", "jafza"],
    ),
    ToolMeta(
        name="compare_free_zones",
        description=(
            "Compare and rank Dubai free zones for a specific budget, visa "
            "count, sector, and office requirement. Returns a shortlist with "
            "cost, bank acceptance, and best-for tags."
        ),
        feature="free_zones",
        tier=TIER_BIZ,
        tags=[
            "compare",
            "free zone",
            "shortlist",
            "ranked",
            "best",
            "cheap",
            "budget",
            "dubai",
        ],
    ),
    ToolMeta(
        name="list_offshore",
        description="List Dubai-relevant offshore options (JAFZA Offshore, RAK ICC).",
        feature="free_zones",
        tier=TIER_BIZ,
        tags=["offshore", "rak icc", "jafza offshore", "holding", "asset"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
