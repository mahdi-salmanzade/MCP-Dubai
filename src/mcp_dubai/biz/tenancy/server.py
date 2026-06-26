"""FastMCP server for tenancy."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.tenancy import tools

mcp: FastMCP = FastMCP("tenancy")


@mcp.tool
async def ejari_guide() -> dict[str, object]:
    """
    Return the full Ejari registration guide.

    Covers the required documents, fees by channel (Dubai REST app, Real
    Estate Trustee Centre, typing center), timelines, channels, and the
    common mistakes that block a Dubai tenancy.
    """
    return await tools.ejari_guide()


@mcp.tool
async def rera_rent_increase(
    current_annual_rent: float,
    area_average_rent: float,
) -> dict[str, object]:
    """
    Compute the maximum legal rent increase under Dubai Decree 43 of 2013.

    Maps how far the current rent sits below the area average market rent
    (RERA Rent Index) to the allowed increase slab and returns the gap
    percentage, the max increase percentage, and the max new rent.

    Args:
        current_annual_rent: The current annual rent in AED.
        area_average_rent: The area average market rent in AED (RERA Rent Index).
    """
    return await tools.rera_rent_increase(
        current_annual_rent=current_annual_rent,
        area_average_rent=area_average_rent,
    )


@mcp.tool
async def rental_dispute_guide(annual_rent: float | None = None) -> dict[str, object]:
    """
    Return the Rental Disputes Centre (RDC) filing guide.

    If annual_rent is provided, also compute the filing fee (3.5% of annual
    rent, AED 500 floor, AED 20,000 cap).

    Args:
        annual_rent: Optional annual rent in AED to compute the filing fee.
    """
    return await tools.rental_dispute_guide(annual_rent=annual_rent)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="ejari_guide",
        description=(
            "Ejari registration: required documents, fees by channel, timelines, "
            "channels, and common mistakes."
        ),
        feature="tenancy",
        tier=TIER_BIZ,
        tags=[
            "ejari",
            "tenancy",
            "tenancy contract",
            "rental contract registration",
            "dewa premise number",
            "dubai rest",
            "إيجاري",
        ],
    ),
    ToolMeta(
        name="rera_rent_increase",
        description=(
            "RERA rent-increase calculator under Dubai Decree 43 of 2013: how much "
            "can the landlord raise the rent at renewal."
        ),
        feature="tenancy",
        tier=TIER_BIZ,
        tags=[
            "rent increase",
            "rera",
            "rent index",
            "decree 43",
            "landlord increase rent",
            "renewal",
            "tenancy",
            "زيادة الإيجار",
        ],
    ),
    ToolMeta(
        name="rental_dispute_guide",
        description=(
            "Rental Disputes Centre (RDC) filing: fees, prerequisites, and channels "
            "for a Dubai landlord or tenant dispute."
        ),
        feature="tenancy",
        tier=TIER_BIZ,
        tags=[
            "dispute",
            "rental dispute",
            "rdc",
            "rental disputes centre",
            "eviction",
            "filing fee",
            "tenancy",
            "لجنة فض المنازعات الإيجارية",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
