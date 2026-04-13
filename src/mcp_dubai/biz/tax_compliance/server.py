"""FastMCP server for tax_compliance."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.tax_compliance import tools

mcp: FastMCP = FastMCP("tax_compliance")


@mcp.tool
async def corporate_tax_estimate(
    annual_taxable_income_aed: int,
    is_free_zone: bool = False,
    qfzp_qualifying_pct: int = 0,
    industry: str = "general",
) -> dict[str, object]:
    """
    Estimate UAE corporate tax liability under Federal Decree-Law 47 of 2022.

    Tax-free band on the first AED 375,000, then 9% above. QFZP free zone
    entities can apply 0% to Qualifying Activity income (per Ministerial
    Decision 229 of 2025).

    Args:
        annual_taxable_income_aed: Annual taxable income in AED.
        is_free_zone: True if the entity is in a free zone.
        qfzp_qualifying_pct: Percentage of income that is Qualifying
            Activity income (0 to 100). Only relevant if is_free_zone.
        industry: Industry category. SaaS triggers a critical warning
            since it is NOT a Qualifying Activity under MD 229/2025.
    """
    return await tools.corporate_tax_estimate(
        annual_taxable_income_aed=annual_taxable_income_aed,
        is_free_zone=is_free_zone,
        qfzp_qualifying_pct=qfzp_qualifying_pct,
        industry=industry,
    )


@mcp.tool
async def vat_filing_calendar(annual_revenue_aed: int) -> dict[str, object]:
    """
    Determine the UAE VAT registration requirement and filing frequency.

    Mandatory at AED 375,000 revenue, voluntary at AED 187,500. Filing is
    quarterly under AED 150 million revenue, monthly above. Standard rate
    is 5%.
    """
    return await tools.vat_filing_calendar(annual_revenue_aed=annual_revenue_aed)


@mcp.tool
async def qfzp_check(
    industry: str = "general",
    is_free_zone: bool = True,
) -> dict[str, object]:
    """
    Check QFZP eligibility for a free zone business.

    Returns one of: not_eligible, not_qualifying, potentially_qualifying,
    verify, with the reason. SaaS is explicitly NOT a Qualifying Activity
    under Ministerial Decision 229 of 2025.
    """
    return await tools.qfzp_check(industry=industry, is_free_zone=is_free_zone)


@mcp.tool
async def esr_status() -> dict[str, object]:
    """
    Return the current status of UAE Economic Substance Regulations.

    ESR is DEAD for periods after 31 December 2022 per Cabinet Resolution
    98 of 2024. Historical penalties are refundable.
    """
    return await tools.esr_status()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="corporate_tax_estimate",
        description=(
            "Estimate UAE corporate tax liability with QFZP free zone "
            "rules and the 9% rate above AED 375,000."
        ),
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "corporate tax",
            "ct",
            "tax",
            "9%",
            "qfzp",
            "free zone",
            "375000",
            "estimate",
            "calculate",
            "uae",
            "saas",
            "fta",
        ],
    ),
    ToolMeta(
        name="vat_filing_calendar",
        description="UAE VAT registration requirement and filing frequency by revenue.",
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "vat",
            "5%",
            "filing",
            "quarterly",
            "monthly",
            "registration",
            "375000",
            "187500",
            "uae",
            "fta",
            "emaratax",
        ],
    ),
    ToolMeta(
        name="qfzp_check",
        description=(
            "Check whether a free zone business qualifies for the QFZP "
            "0% rate on Qualifying Activity income."
        ),
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "qfzp",
            "qualifying free zone",
            "qualifying activity",
            "free zone",
            "0%",
            "saas",
            "md 229",
        ],
    ),
    ToolMeta(
        name="esr_status",
        description="Current status of UAE Economic Substance Regulations (DEAD post-2022).",
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "esr",
            "economic substance",
            "repealed",
            "dead",
            "cabinet resolution 98",
            "refundable",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
