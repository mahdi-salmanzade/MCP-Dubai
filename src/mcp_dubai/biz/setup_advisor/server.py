"""FastMCP server for setup_advisor."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.setup_advisor import tools

mcp: FastMCP = FastMCP("setup_advisor")


@mcp.tool
async def setup_advisor(
    activity: str,
    budget_aed: int,
    needs_local_trade: bool = False,
    needs_visa: bool = True,
    visa_count: int = 1,
    industry: str = "general",
) -> dict[str, object]:
    """
    Recommend the best jurisdiction for setting up a business in Dubai.

    Cross-references curated free zones, visas, banks, and tax rules
    (the headline biz/* feature). Returns a ToolResponse envelope with a
    structured recommendation: jurisdiction (mainland, free zone, or
    offshore), candidate free zones, reasoning, warnings, estimated cost
    range, timeline, and next steps. Always returns a `knowledge` block
    with date, volatility, verify_at, and disclaimer.

    Args:
        activity: Business activity description (e.g., "SaaS", "consulting",
            "trading", "ecommerce").
        budget_aed: Total first-year budget in AED for setup, license,
            visas, and bank account.
        needs_local_trade: True if the business needs to invoice mainland
            UAE consumers (B2C) directly without a local distributor.
        needs_visa: True if the founder needs a UAE residence visa from
            this license.
        visa_count: How many visas the company needs in total.
        industry: Industry category. One of: general, saas, tech,
            ecommerce, consulting, fintech, ai, blockchain, crypto,
            trading, import_export, manufacturing, logistics, healthcare,
            media, education, real_estate, fb, retail.

    Returns:
        ToolResponse envelope. On success, `data` carries `jurisdiction`,
        `candidate_free_zones`, `reasoning`, `warnings`,
        `estimated_setup_cost_aed`, `estimated_timeline_weeks`, and
        `next_steps`.
    """
    return await tools.setup_advisor(
        activity=activity,
        budget_aed=budget_aed,
        needs_local_trade=needs_local_trade,
        needs_visa=needs_visa,
        visa_count=visa_count,
        industry=industry,
    )


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="setup_advisor",
        description=(
            "Recommend the best jurisdiction (mainland, free zone, or "
            "offshore) for a Dubai business setup, grounded in curated "
            "knowledge of free zones, visas, banks, and tax rules."
        ),
        feature="setup_advisor",
        tier=TIER_BIZ,
        tags=[
            "setup",
            "incorporate",
            "register",
            "company",
            "business",
            "founder",
            "license",
            "trade license",
            "mainland",
            "free zone",
            "offshore",
            "advisor",
            "recommend",
            "jurisdiction",
            "dubai",
            "uae",
            "saas",
            "ecommerce",
            "consulting",
            "fintech",
            "where should i set up",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
