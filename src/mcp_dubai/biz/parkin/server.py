"""FastMCP server for parkin."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.parkin import tools

mcp: FastMCP = FastMCP("parkin")


@mcp.tool
async def parking_zones() -> dict[str, object]:
    """
    Dubai Parkin zones, tariffs, free periods, and mParking SMS shortcode.

    Variable tariffs since 4 April 2025: peak 4 to 6 AED/h, off-peak 2 to
    4 AED/h. Free Sundays, public holidays, and 22:00 to 08:00. mParking
    SMS shortcode is 7275 (PARK), format `<plate> <zone> <hours>`.

    CRITICAL: 'Mawaqif' is the Abu Dhabi parking system. Dubai parking is
    operated by Parkin Company PJSC (DFM:PARKIN), spun out of RTA in
    December 2023.
    """
    return await tools.parking_zones()


@mcp.tool
async def nol_card_guide(card_type: str | None = None) -> dict[str, object]:
    """
    Nol card guide and RTA fare structure.

    Returns the 5 Nol card types (Red, Silver, Gold, Blue personalized,
    Blue PoD) plus the 2025 fare structure (1-zone AED 3, 2-zone AED 5,
    3+ zone AED 7.50, daily caps, transfer rules, unlimited passes).

    Args:
        card_type: Optional card type filter substring.
    """
    return await tools.nol_card_guide(card_type=card_type)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="parking_zones",
        description=(
            "Dubai Parkin parking zones, tariffs, free periods, and mParking "
            "SMS shortcode (7275). Note: NOT 'Mawaqif' which is Abu Dhabi."
        ),
        feature="parkin",
        tier=TIER_BIZ,
        tags=[
            "parking",
            "parkin",
            "dubai parking",
            "mparking",
            "tariff",
            "zone",
            "7275",
            "park",
            "rta",
        ],
    ),
    ToolMeta(
        name="nol_card_guide",
        description="Nol card types and RTA fare structure (Silver, Gold, Blue, Red, PoD).",
        feature="parkin",
        tier=TIER_BIZ,
        tags=[
            "nol",
            "nol card",
            "rta",
            "fare",
            "metro",
            "bus",
            "tram",
            "silver",
            "gold",
            "blue",
            "balance",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
