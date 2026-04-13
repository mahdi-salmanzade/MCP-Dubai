"""FastMCP server for dcde."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.dcde import tools

mcp: FastMCP = FastMCP("dcde")


@mcp.tool
async def dcde_programs(program_id: str | None = None) -> dict[str, object]:
    """
    Look up Dubai Chamber of Digital Economy programs.

    Args:
        program_id: Optional program id, e.g., "dubai_founders_hq",
            "antler_residency", "frwrdx", "unicorn_30",
            "create_apps_championship", "canva_partnership".
    """
    return await tools.dcde_programs(program_id=program_id)


@mcp.tool
async def chamber_membership() -> dict[str, object]:
    """
    Return Dubai chamber membership rules.

    DCDE has no standalone membership scheme. Dubai Chamber of Commerce
    membership is mandatory for mainland commercial license holders
    (AED 700 to AED 2,200 annual fee tiers).
    """
    return await tools.chamber_membership()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="dcde_programs",
        description=(
            "Dubai Chamber of Digital Economy programs: Dubai Founders HQ, "
            "Antler Residency, FRWRDx, Unicorn 30, Create Apps Championship."
        ),
        feature="dcde",
        tier=TIER_BIZ,
        tags=[
            "dcde",
            "dubai chamber",
            "digital economy",
            "antler",
            "frwrdx",
            "unicorn",
            "founders hq",
            "create apps",
            "program",
        ],
    ),
    ToolMeta(
        name="chamber_membership",
        description="Dubai Chamber of Commerce membership rules and DCDE membership clarification.",
        feature="dcde",
        tier=TIER_BIZ,
        tags=["chamber", "membership", "dubai chamber of commerce", "dcde", "fee"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
