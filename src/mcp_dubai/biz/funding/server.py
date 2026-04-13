"""FastMCP server for funding."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.funding import tools

mcp: FastMCP = FastMCP("funding")


@mcp.tool
async def accelerator_search(
    sector: str | None = None,
    free_only: bool = False,
    location: str | None = None,
) -> dict[str, object]:
    """
    Search UAE accelerators and incubators by sector, cost, and location.

    Args:
        sector: Optional sector filter (e.g., "fintech", "tech", "media").
        free_only: True to exclude paid accelerators (e.g., AstroLabs).
        location: Optional location filter (e.g., "Dubai", "Abu Dhabi").
    """
    return await tools.accelerator_search(sector=sector, free_only=free_only, location=location)


@mcp.tool
async def vc_list(
    stage: str | None = None,
    sector: str | None = None,
) -> dict[str, object]:
    """
    List active UAE / MENA VCs by stage and sector.

    Args:
        stage: Optional stage focus, one of: pre_seed, seed, series_a,
            series_b, growth.
        sector: Optional sector substring (e.g., "fintech", "saas").
    """
    return await tools.vc_list(stage=stage, sector=sector)


@mcp.tool
async def grant_programs(grant_type: str | None = None) -> dict[str, object]:
    """
    List UAE government grant and funding support programs.

    Args:
        grant_type: Optional type filter (guarantee_loan, venture_fund,
            support_programs, loan_grant).
    """
    return await tools.grant_programs(grant_type=grant_type)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="accelerator_search",
        description=(
            "Search UAE accelerators and incubators (in5, Hub71, DIFC "
            "Innovation Hub, Dtec, AstroLabs, Sheraa)."
        ),
        feature="funding",
        tier=TIER_BIZ,
        tags=[
            "accelerator",
            "incubator",
            "in5",
            "hub71",
            "difc",
            "dtec",
            "astrolabs",
            "sheraa",
            "tecom",
            "cohort",
            "funding",
            "startup",
        ],
    ),
    ToolMeta(
        name="vc_list",
        description="List active UAE / MENA VCs (BECO, Wamda, MEVP, Shorooq, Global Ventures, etc.).",
        feature="funding",
        tier=TIER_BIZ,
        tags=[
            "vc",
            "venture capital",
            "investor",
            "beco",
            "wamda",
            "mevp",
            "shorooq",
            "global ventures",
            "funding",
            "raise",
            "round",
        ],
    ),
    ToolMeta(
        name="grant_programs",
        description="UAE government grant programs (MBRIF, DFDF, Dubai SME, Khalifa Fund).",
        feature="funding",
        tier=TIER_BIZ,
        tags=[
            "grant",
            "government grant",
            "mbrif",
            "dfdf",
            "dubai sme",
            "khalifa fund",
            "non-dilutive",
            "funding",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
