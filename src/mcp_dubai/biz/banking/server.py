"""FastMCP server for banking."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.banking import tools

mcp: FastMCP = FastMCP("banking")


@mcp.tool
async def list_banks() -> dict[str, object]:
    """List every UAE business bank in the curated dataset."""
    return await tools.list_banks()


@mcp.tool
async def bank_details(bank_id: str) -> dict[str, object]:
    """
    Get the full curated record for a UAE business bank.

    Args:
        bank_id: Bank id slug. Examples: "wio", "mashreq_neobiz", "zand",
            "ruya", "emirates_nbd", "rakbank", "cbd", "adcb", "fab", "adib",
            "hsbc", "standard_chartered", "citi".
    """
    return await tools.bank_details(bank_id=bank_id)


@mcp.tool
async def bank_recommendation(
    industry: str = "general",
    budget_min_balance_aed: int | None = None,
    speed_priority: bool = False,
    tier: str | None = None,
    is_high_risk: bool = False,
    limit: int = 5,
) -> dict[str, object]:
    """
    Recommend UAE business banks based on industry, minimum balance budget,
    and onboarding speed.

    Args:
        industry: Business industry category. Crypto, forex, jewelry, used
            cars, and money service businesses are auto-flagged as high risk.
        budget_min_balance_aed: Maximum minimum-balance the founder can
            accept (filters out banks above this).
        speed_priority: True if onboarding speed matters more than min
            balance (favours digital banks).
        tier: Optional filter, one of "digital", "traditional", "international".
        is_high_risk: Force the high-risk warning even if industry is not
            in the auto-list.
        limit: Maximum results (1 to 20, default 5).
    """
    return await tools.bank_recommendation(
        industry=industry,
        budget_min_balance_aed=budget_min_balance_aed,
        speed_priority=speed_priority,
        tier=tier,
        is_high_risk=is_high_risk,
        limit=limit,
    )


@mcp.tool
async def dul_eligibility(
    bank_id: str | None = None,
    free_zone: str | None = None,
) -> dict[str, object]:
    """
    Report Dubai Unified Licence (DUL) bank integration and coverage.

    DUL is issued across mainland and free zone businesses in Dubai. The
    official 12 November 2025 announcement named seven integrated banks
    and reported a 5-day average account-opening time. That average is not
    a guarantee for an individual application.

    Args:
        bank_id: Bank id slug to check (e.g., "emirates_nbd", "fab", "ruya").
        free_zone: Dubai free zone name or slug. DUL coverage is not limited
            to a short participant list.

    Returns:
        Dict with a compatibility `eligible` flag, `bank_status`,
        `zone_status`, and the dated official integration snapshot. Here,
        `eligible` only means that the bank was named as integrated.
    """
    return await tools.dul_eligibility(bank_id=bank_id, free_zone=free_zone)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="list_banks",
        description="List every UAE business bank in the curated matrix.",
        feature="banking",
        tier=TIER_BIZ,
        tags=["bank", "banks", "list", "uae", "business banking", "all"],
    ),
    ToolMeta(
        name="bank_details",
        description="Get the full curated record for a specific UAE business bank.",
        feature="banking",
        tier=TIER_BIZ,
        tags=["bank", "details", "lookup", "wio", "mashreq", "rakbank", "fab", "enbd"],
    ),
    ToolMeta(
        name="bank_recommendation",
        description=(
            "Recommend UAE business banks based on industry, minimum balance "
            "budget, and onboarding speed."
        ),
        feature="banking",
        tier=TIER_BIZ,
        tags=[
            "bank",
            "recommend",
            "open account",
            "business banking",
            "best bank",
            "fastest bank",
            "cheap bank",
            "wio",
            "mashreq",
            "uae",
        ],
    ),
    ToolMeta(
        name="dul_eligibility",
        description=(
            "Check whether a bank was named as Dubai Unified Licence (DUL) "
            "integrated and explain Dubai-wide business coverage."
        ),
        feature="banking",
        tier=TIER_BIZ,
        tags=["dul", "integration", "dubai unified licence", "5 days", "onboarding"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
