"""FastMCP server for ip_trademark."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.ip_trademark import tools

mcp: FastMCP = FastMCP("ip_trademark")


@mcp.tool
async def trademark_registration(
    is_sme: bool = False,
    expedited: bool = False,
) -> dict[str, object]:
    """
    Return UAE trademark registration steps, fees, and timeline.

    The IP authority is MOET (Ministry of Economy and Tourism, formerly
    Ministry of Economy). Cabinet Resolution 102 of 2025 introduced new
    fees with a 50% reduction for members of the UAE National Programme for
    SMEs.

    Args:
        is_sme: True only for a qualifying member of the UAE National
            Programme for SMEs.
        expedited: True to replace the AED 750 regular examination with the
            AED 2,250 one-day expedited examination (AED 1,500 net surcharge).
    """
    return await tools.trademark_registration(is_sme=is_sme, expedited=expedited)


@mcp.tool
async def ip_protection(ip_type: str = "trademark") -> dict[str, object]:
    """
    Return UAE IP protection guidance.

    Args:
        ip_type: One of "trademark", "patent", "copyright".
    """
    return await tools.ip_protection(ip_type=ip_type)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="trademark_registration",
        description=(
            "UAE trademark registration steps, fees, and timeline via MOET. "
            "Includes Cabinet Resolution 102 of 2025 expedited and SME options."
        ),
        feature="ip_trademark",
        tier=TIER_BIZ,
        tags=[
            "trademark",
            "moet",
            "ministry of economy",
            "ip",
            "register",
            "wipo",
            "madrid",
            "sme discount",
        ],
    ),
    ToolMeta(
        name="ip_protection",
        description="UAE IP protection guidance for trademark, patent, or copyright.",
        feature="ip_trademark",
        tier=TIER_BIZ,
        tags=[
            "ip",
            "intellectual property",
            "trademark",
            "patent",
            "copyright",
            "moet",
            "berne",
            "gcc patent",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
