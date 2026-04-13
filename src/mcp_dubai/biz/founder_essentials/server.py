"""FastMCP server for founder_essentials."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.founder_essentials import tools

mcp: FastMCP = FastMCP("founder_essentials")


@mcp.tool
async def attestation_guide(
    document_type: str = "personal",
    home_country: str | None = None,
) -> dict[str, object]:
    """
    Walk through the UAE attestation chain for a foreign document.

    The UAE is NOT a Hague Apostille member as of April 2026. Foreign
    documents still require the full 5-step legalization chain (home
    country notary, home country MOFA, UAE embassy, UAE MOFAIC, MOJ
    legal translation if needed).

    Args:
        document_type: One of: personal, commercial, degree, marriage,
            birth, power_of_attorney.
        home_country: Optional source country for context.
    """
    return await tools.attestation_guide(document_type=document_type, home_country=home_country)


@mcp.tool
async def pro_services_estimate(
    visas_per_year: int = 2,
    license_renewals_per_year: int = 1,
    use_retainer: bool = False,
) -> dict[str, object]:
    """
    Estimate annual PRO service cost.

    Args:
        visas_per_year: How many visa transactions are expected per year.
        license_renewals_per_year: How many license renewals per year.
        use_retainer: True to force a monthly retainer estimate.
    """
    return await tools.pro_services_estimate(
        visas_per_year=visas_per_year,
        license_renewals_per_year=license_renewals_per_year,
        use_retainer=use_retainer,
    )


@mcp.tool
async def legal_translation_estimate(
    pages: int,
    same_day: bool = False,
) -> dict[str, object]:
    """
    Estimate legal translation cost based on page count and urgency.

    Only MOJ-licensed sworn translators are accepted by UAE courts and
    government counters.

    Args:
        pages: Number of pages.
        same_day: True for same-day turnaround (25 to 50% uplift).
    """
    return await tools.legal_translation_estimate(pages=pages, same_day=same_day)


@mcp.tool
async def chamber_of_commerce_info() -> dict[str, object]:
    """Return Dubai Chamber of Commerce membership and Certificate of Origin info."""
    return await tools.chamber_of_commerce_info()


@mcp.tool
async def setup_timeline_estimate() -> dict[str, object]:
    """Return realistic end-to-end timelines for a Dubai setup."""
    return await tools.setup_timeline_estimate()


@mcp.tool
async def common_founder_mistakes(category: str | None = None) -> dict[str, object]:
    """
    List the 11 most common founder mistakes that break Dubai setups.

    Args:
        category: Optional substring filter on the mistake title or id.
    """
    return await tools.common_founder_mistakes(category=category)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="attestation_guide",
        description=(
            "Walk through the UAE attestation chain for a foreign document. "
            "The UAE is NOT a Hague Apostille member."
        ),
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "attestation",
            "legalization",
            "mofa",
            "mofaic",
            "apostille",
            "degree",
            "marriage certificate",
            "birth certificate",
            "power of attorney",
            "embassy",
        ],
    ),
    ToolMeta(
        name="pro_services_estimate",
        description="Estimate annual PRO service cost based on visa and renewal volume.",
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "pro",
            "public relations officer",
            "visa processing",
            "tas'heel",
            "tasheel",
            "renewal",
            "estimate",
            "cost",
        ],
    ),
    ToolMeta(
        name="legal_translation_estimate",
        description="Estimate Arabic legal translation cost (MOJ-licensed translators).",
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "translation",
            "arabic",
            "moj",
            "sworn translator",
            "legal",
            "court",
            "estimate",
        ],
    ),
    ToolMeta(
        name="chamber_of_commerce_info",
        description="Dubai Chamber of Commerce membership tiers and CoO fees.",
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "chamber",
            "commerce",
            "certificate of origin",
            "coo",
            "membership",
            "dubai chamber",
        ],
    ),
    ToolMeta(
        name="setup_timeline_estimate",
        description="Realistic end-to-end timelines for a Dubai business setup.",
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "timeline",
            "how long",
            "weeks",
            "setup",
            "license",
            "visa",
            "bank account",
            "ejari",
        ],
    ),
    ToolMeta(
        name="common_founder_mistakes",
        description="The 11 most common founder mistakes that break Dubai setups.",
        feature="founder_essentials",
        tier=TIER_BIZ,
        tags=[
            "mistakes",
            "pitfalls",
            "errors",
            "wrong",
            "avoid",
            "founder",
            "setup",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
