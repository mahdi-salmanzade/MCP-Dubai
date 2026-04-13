"""FastMCP server for KHDA school search."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.khda import tools

mcp: FastMCP = FastMCP("khda")


@mcp.tool
async def khda_search_school(
    name: str | None = None,
    area: str | None = None,
    curriculum: str | None = None,
    rating: str | None = None,
    max_fee_aed: int | None = None,
    limit: int = 20,
) -> dict[str, object]:
    """
    Search Dubai private schools by name, area, curriculum, rating, or fee.

    Args:
        name: Substring match on school name (case-insensitive).
        area: Substring match on area / neighborhood (e.g., "Jumeirah").
        curriculum: Substring match on curriculum (e.g., "British", "IB").
        rating: Exact match on KHDA inspection rating. Valid values:
            "Outstanding", "Very Good", "Good", "Acceptable", "Weak", "Very Weak".
        max_fee_aed: Filter to schools whose fees_min_aed is at or below this.
        limit: Max results (1 to 200, default 20).

    Returns:
        Dict with `count`, `schools` (list), and `knowledge_date`.
    """
    return await tools.khda_search_school(
        name=name,
        area=area,
        curriculum=curriculum,
        rating=rating,
        max_fee_aed=max_fee_aed,
        limit=limit,
    )


@mcp.tool
async def khda_list_curricula() -> dict[str, object]:
    """List the curricula available in the snapshot (e.g., British, IB, CBSE)."""
    return await tools.khda_list_curricula()


@mcp.tool
async def khda_list_areas() -> dict[str, object]:
    """List the Dubai areas covered by schools in the snapshot."""
    return await tools.khda_list_areas()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="khda_search_school",
        description=(
            "Search Dubai private schools by name, area, curriculum, KHDA "
            "inspection rating, or fee ceiling."
        ),
        feature="khda",
        tier=TIER_OPEN,
        tags=[
            "school",
            "schools",
            "education",
            "khda",
            "dubai",
            "private",
            "british",
            "ib",
            "american",
            "cbse",
            "curriculum",
            "rating",
            "outstanding",
            "fees",
        ],
    ),
    ToolMeta(
        name="khda_list_curricula",
        description="List curricula available in Dubai schools (British, IB, CBSE, etc.).",
        feature="khda",
        tier=TIER_OPEN,
        tags=["khda", "curriculum", "list", "school", "education"],
    ),
    ToolMeta(
        name="khda_list_areas",
        description="List Dubai areas covered by KHDA private schools.",
        feature="khda",
        tier=TIER_OPEN,
        tags=["khda", "area", "neighborhood", "school", "list"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
