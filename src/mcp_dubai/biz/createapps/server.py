"""FastMCP server for createapps."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.createapps import tools

mcp: FastMCP = FastMCP("createapps")


@mcp.tool
async def createapps_championship() -> dict[str, object]:
    """
    Return Create Apps Championship details for the current cycle.

    Operated by DCDE. Cycle 3 registration is closed and the competition is
    ongoing in its finalist phase. Twelve finalists were announced on
    14 April 2026, and the official structured timeline schedules the finals
    for 7 October 2026. The page's stale FAQ says April 2026, so the returned
    record flags that inconsistency and advises reconfirming before travel.
    """
    return await tools.createapps_championship()


@mcp.tool
async def submission_guide() -> dict[str, object]:
    """
    Return submission guidance for Create Apps Championship.

    Includes evaluation criteria, application URL, and the full program
    list (Championship, Emirati Training Academy, Learning Lab).
    """
    return await tools.submission_guide()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="createapps_championship",
        description=(
            "Create Apps Championship details. Cycle 3 registration is closed, "
            "12 finalists are in the ongoing finalist phase, and the structured "
            "timeline schedules the finals for 7 October 2026."
        ),
        feature="createapps",
        tier=TIER_BIZ,
        tags=[
            "create apps",
            "createapps",
            "championship",
            "dcde",
            "competition",
            "prize",
            "finals",
            "app developer",
        ],
    ),
    ToolMeta(
        name="submission_guide",
        description="Create Apps Championship submission guidance and evaluation criteria.",
        feature="createapps",
        tier=TIER_BIZ,
        tags=[
            "submission",
            "create apps",
            "evaluation criteria",
            "application",
            "guide",
            "app developer",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
