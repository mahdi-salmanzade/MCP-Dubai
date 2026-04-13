"""FastMCP server for gov_portals."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.gov_portals import tools

mcp: FastMCP = FastMCP("gov_portals")


@mcp.tool
async def portal_guide(
    portal_id: str | None = None,
    keyword: str | None = None,
) -> dict[str, object]:
    """
    Look up a UAE government portal by id or by keyword.

    Args:
        portal_id: Portal id slug, e.g., "uae_pass", "basher",
            "invest_in_dubai", "emaratax", "mohre", "gdrfa_dubai", "icp",
            "u_ae", "dubai_now", "dubai_rest", "developer_dubai".
        keyword: Substring search across portal name, type, and operator.

    Returns:
        Full portal record (when portal_id is given) or a list of matching
        portals (when keyword is given) or all portals (no filter). Includes
        disambiguation notes for Sahel (Kuwait, not UAE) and SmartPass.
    """
    return await tools.portal_guide(portal_id=portal_id, keyword=keyword)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="portal_guide",
        description=(
            "UAE government portal lookup: UAE Pass, Basher, Invest in Dubai, "
            "EmaraTax, MOHRE, GDRFA, ICP, Dubai Now, u.ae, and more."
        ),
        feature="gov_portals",
        tier=TIER_BIZ,
        tags=[
            "uae pass",
            "basher",
            "invest in dubai",
            "emaratax",
            "mohre",
            "gdrfa",
            "icp",
            "tas'heel",
            "tasheel",
            "dubai now",
            "u.ae",
            "smartpass",
            "portal",
            "government",
            "service",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
