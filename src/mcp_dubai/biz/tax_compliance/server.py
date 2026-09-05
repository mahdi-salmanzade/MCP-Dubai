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
    is_qfzp: bool | None = None,
) -> dict[str, object]:
    """
    Estimate UAE corporate tax liability under Federal Decree-Law 47 of 2022.

    Ordinary taxable persons receive the AED 375,000 band, then 9% above.
    QFZPs receive 0% on Qualifying Income and 9% on other taxable income
    without the ordinary band. Confirm QFZP status and income classification.

    Args:
        annual_taxable_income_aed: Annual taxable income in AED.
        is_free_zone: True if the entity is in a free zone.
        qfzp_qualifying_pct: Percentage of income that is Qualifying
            Activity income (0 to 100). Only relevant if is_free_zone.
        industry: Industry category. SaaS triggers an income-classification
            warning because qualification depends on the specific transaction.
        is_qfzp: Explicit QFZP status, including when qualifying income is zero.
            Omission retains inference from a positive qualifying percentage.
    """
    return await tools.corporate_tax_estimate(
        annual_taxable_income_aed=annual_taxable_income_aed,
        is_free_zone=is_free_zone,
        qfzp_qualifying_pct=qfzp_qualifying_pct,
        industry=industry,
        is_qfzp=is_qfzp,
    )


@mcp.tool
async def vat_filing_calendar(annual_revenue_aed: int) -> dict[str, object]:
    """
    Determine the UAE VAT registration requirement and filing frequency.

    Treats the input as taxable supplies and imports in the past 12 months:
    mandatory above AED 375,000, voluntary above AED 187,500. Filing frequency
    is indicative; the FTA assigns the actual period. Standard rate is 5%.
    Includes the Federal Decree-Law 16 of 2025 amendments effective
    1 January 2026 (reverse-charge invoicing, 5-year VAT credit
    carry-forward cap, evasion-linked input VAT denial).
    """
    return await tools.vat_filing_calendar(annual_revenue_aed=annual_revenue_aed)


@mcp.tool
async def qfzp_check(
    industry: str = "general",
    is_free_zone: bool = True,
) -> dict[str, object]:
    """
    Check QFZP eligibility for a free zone business.

    Returns one of: not_eligible, potentially_qualifying, verify, with the
    reason. SaaS requires assessment of the counterparty, exclusions and
    any qualifying intellectual-property income.
    """
    return await tools.qfzp_check(industry=industry, is_free_zone=is_free_zone)


@mcp.tool
async def esr_status() -> dict[str, object]:
    """
    Return the current status of UAE Economic Substance Regulations.

    ESR is not required for financial years ending after 31 December 2022 per
    Cabinet Decision 98 of 2024. Obligations and penalties for in-scope
    financial years ending from 2019 through 2022 remain live, and penalties
    already imposed for those periods are not refundable.
    """
    return await tools.esr_status()


@mcp.tool
async def einvoicing_timeline() -> dict[str, object]:
    """
    Return the UAE e-invoicing regime, rollout timeline, and ASP deadlines.

    Legislated by Ministerial Decisions 243 and 244 of 2025 on the PINT AE
    DCTCE 5-corner model, reported to the FTA through EmaraTax. The pilot
    phase went live 1 July 2026 with voluntary adoption open from the same
    date. ASP appointment deadlines: 30 October 2026 for revenue at or
    above AED 50M (Ministerial Resolution 66 of 2026), 31 March 2027 below
    AED 50M. Mandatory go-live: January 2027 at or above AED 50M, July
    2027 below, government entities October 2027. Includes the official
    current MoF ASP accreditation register. Verify dates with the FTA/MoF.
    """
    return await tools.einvoicing_timeline()


@mcp.tool
async def late_payment_penalty_estimate(
    tax_due_aed: float,
    days_late: int,
) -> dict[str, object]:
    """
    Estimate the unified UAE late-payment penalty on overdue tax.

    Cabinet Decision 129 of 2025 applies 14% per annum to unpaid tax,
    effective 14 April 2026, unifying VAT, Excise and Corporate Tax. The
    charge accrues monthly at 14% divided by 12 for every month or part of a
    month; it is not pro-rated by day. Confirm the calendar-month count with
    the FTA.
    """
    return await tools.late_payment_penalty_estimate(
        tax_due_aed=tax_due_aed,
        days_late=days_late,
    )


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
        description=(
            "Check UAE Economic Substance Regulations status. ESR is DEAD "
            "for periods after 31 Dec 2022 per Cabinet Decision 98/2024, "
            "but historical obligations remain live and penalties for in-scope "
            "periods are not refundable."
        ),
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "esr",
            "esr check",
            "economic substance",
            "economic substance regulations",
            "filing",
            "do i need to file esr",
            "repealed",
            "dead",
            "cabinet decision 98",
            "not refundable",
            "compliance",
        ],
    ),
    ToolMeta(
        name="einvoicing_timeline",
        description=(
            "UAE e-invoicing regime: PINT AE / DCTCE 5-corner model, "
            "EmaraTax reporting, pilot live since 1 July 2026, ASP "
            "appointment deadlines (30 Oct 2026 / 31 Mar 2027), the MoF "
            "current ASP accreditation register, and the phased rollout through "
            "2027 (MD 243 and 244 of 2025, MR 66 of 2026)."
        ),
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "e-invoicing",
            "einvoice",
            "pint ae",
            "emaratax",
            "asp",
            "accredited service provider",
            "pilot",
            "فاتورة إلكترونية",
        ],
    ),
    ToolMeta(
        name="late_payment_penalty_estimate",
        description=(
            "Estimate the unified UAE late-payment penalty: a 14% annual rate "
            "charged monthly for every month or part of a month (Cabinet "
            "Decision 129 of 2025, effective 14 April 2026)."
        ),
        feature="tax_compliance",
        tier=TIER_BIZ,
        tags=[
            "late payment penalty",
            "14%",
            "غرامة تأخير",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
