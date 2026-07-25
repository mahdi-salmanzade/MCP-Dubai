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

    Operated by DCDE. Cycle 3 ran October 2025 to May 2026 and has
    CONCLUDED: its semi-finals (13 April 2026) and grand finale (11 May
    2026, Museum of the Future) are both in the past. Its USD 720,000 prize
    pool across 4 categories (Best Youth, Most Innovative, Most Impactful,
    Longevity) at USD 150,000 each is historical precedent, not a current
    offer. Cycle 4 was not announced as of 25 July 2026, so do not quote
    cycle 3 dates as upcoming. Check createapps.ae for the next intake.
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
            "Create Apps Championship details. Cycle 3 (USD 720K prize pool, 4 "
            "categories at USD 150K each, grand finale at Museum of the Future) "
            "concluded in May 2026; cycle 4 is unannounced."
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
            "museum of the future",
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
