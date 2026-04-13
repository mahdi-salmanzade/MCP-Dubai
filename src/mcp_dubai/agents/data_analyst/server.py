"""FastMCP server for data_analyst."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.agents.data_analyst import tools

mcp: FastMCP = FastMCP("data_analyst")


@mcp.tool
async def plan_query(
    category: str,
    inputs: dict[str, object] | None = None,
) -> dict[str, object]:
    """
    Build a multi-tool execution plan for a query category.

    Args:
        category: One of: founder_setup, market_research, compliance_checkup,
            relocation.
        inputs: Optional dict of named inputs to substitute into the plan's
            args templates.

    Returns:
        Structured plan: list of tool calls in order, each with purpose
        and args template.
    """
    return await tools.plan_query(category=category, inputs=inputs)


@mcp.tool
async def list_plan_categories() -> dict[str, object]:
    """List the available data_analyst plan categories."""
    return await tools.list_plan_categories()


@mcp.tool
async def synthesize_report(
    title: str,
    sections: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """
    Build a structured Markdown report from named sections.

    The output includes a knowledge-freshness footer that lists every
    domain the report draws on with its current verified date and
    volatility tag.

    Args:
        title: Report title.
        sections: List of {heading, body} dicts. Each becomes an H2 section.
    """
    return await tools.synthesize_report(title=title, sections=sections)


@mcp.tool
async def analyze_setup_decision(
    activity: str,
    budget_aed: int,
    industry: str = "general",
) -> dict[str, object]:
    """
    Build a complete cross-tool analysis plan for a founder setup decision.

    Returns an ordered list of 6 tool calls (setup_advisor, compare_free_zones,
    qfzp_check, bank_recommendation, common_founder_mistakes,
    setup_timeline_estimate) plus synthesis instructions.

    The LLM should execute the plan and then call synthesize_report.

    Args:
        activity: Business activity (e.g., "SaaS", "consulting").
        budget_aed: First-year budget in AED.
        industry: Industry category.
    """
    return await tools.analyze_setup_decision(
        activity=activity, budget_aed=budget_aed, industry=industry
    )


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="plan_query",
        description=(
            "Build a multi-tool execution plan for a query category "
            "(founder_setup, market_research, compliance_checkup, relocation)."
        ),
        feature="data_analyst",
        tier=TIER_BIZ,
        tags=[
            "plan",
            "query",
            "cross tool",
            "multi step",
            "execution plan",
            "synthesis",
            "agent",
        ],
    ),
    ToolMeta(
        name="list_plan_categories",
        description="List the available data_analyst plan categories.",
        feature="data_analyst",
        tier=TIER_BIZ,
        tags=["plan", "category", "list", "agent"],
    ),
    ToolMeta(
        name="synthesize_report",
        description=(
            "Build a structured Markdown report from sections, with a "
            "knowledge freshness footer listing all domains referenced."
        ),
        feature="data_analyst",
        tier=TIER_BIZ,
        tags=[
            "report",
            "synthesize",
            "markdown",
            "summary",
            "brief",
            "agent",
        ],
    ),
    ToolMeta(
        name="analyze_setup_decision",
        description=(
            "Cross-tool analysis plan for a founder setup decision. Plans "
            "6 tool calls then synthesizes a structured brief."
        ),
        feature="data_analyst",
        tier=TIER_BIZ,
        tags=[
            "analyze",
            "setup",
            "decision",
            "founder",
            "cross tool",
            "agent",
            "plan",
            "brief",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
