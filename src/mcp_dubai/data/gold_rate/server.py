"""FastMCP server for gold_rate (DJG retail rates from Dubai City of Gold)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.gold_rate import tools

mcp: FastMCP = FastMCP("gold_rate")


@mcp.tool
async def dubai_gold_rate() -> dict[str, object]:
    """
    Today's Dubai retail gold rates in AED per gram by karat (no key).

    Dubai Jewellery Group suggested retail rates (24K, 22K, 21K, 18K, 14K)
    from Dubai City of Gold, published around 09:00, 13:30 and 18:00 UAE
    time. Jewellery retail reference rates, not spot bullion prices.
    """
    return await tools.dubai_gold_rate()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="dubai_gold_rate",
        description=(
            "Today's Dubai retail gold rates in AED per gram by karat (24k, "
            "22k, 21k, 18k, 14k): Dubai Jewellery Group suggested retail "
            "rates via Dubai City of Gold, updated around three times daily. "
            "Retail reference rates, not spot bullion."
        ),
        feature="gold_rate",
        tier=TIER_OPEN,
        tags=[
            "gold",
            "gold rate",
            "gold price",
            "gold souk",
            "karat",
            "carat",
            "24k",
            "22k",
            "21k",
            "18k",
            "jewellery",
            "jewelry",
            "aed per gram",
            "dubai jewellery group",
            "city of gold",
            "سعر الذهب",
            "الذهب",
            "عيار",
            "ذهب عيار 24",
            "ذهب عيار 22",
            "مجوهرات",
            "سوق الذهب",
            "درهم للجرام",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
