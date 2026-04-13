"""FastMCP server for halal."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.halal import tools

mcp: FastMCP = FastMCP("halal")


@mcp.tool
async def halal_certification(product_category: str | None = None) -> dict[str, object]:
    """
    Return UAE halal certification guidance.

    The authority is MOIAT (Ministry of Industry and Advanced Technology),
    which absorbed ESMA in 2020. Standards: UAE.S GSO 2055-1, 2055-2,
    2055-4, plus UAE.S 993 (slaughter). Single UAE Halal Mark.

    Args:
        product_category: Optional filter on the products list.
    """
    return await tools.halal_certification(product_category=product_category)


@mcp.tool
async def moiat_requirements() -> dict[str, object]:
    """
    Return MOIAT registration fees and timeline for Halal Certification Bodies.

    HCB registration: AED 1,000 per domain plus AED 1,000 certificate.
    Total AED 2,000. Timeline: 10 working days.
    """
    return await tools.moiat_requirements()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="halal_certification",
        description="UAE halal certification guidance via MOIAT (NOT ESMA, which was absorbed in 2020).",
        feature="halal",
        tier=TIER_BIZ,
        tags=[
            "halal",
            "moiat",
            "esma",
            "certification",
            "uae.s gso 2055",
            "halal mark",
            "food",
            "cosmetics",
            "pharma",
            "slaughter",
        ],
    ),
    ToolMeta(
        name="moiat_requirements",
        description="MOIAT registration fees and timeline for Halal Certification Bodies (HCBs).",
        feature="halal",
        tier=TIER_BIZ,
        tags=["moiat", "hcb", "halal certification body", "registration", "fees"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
