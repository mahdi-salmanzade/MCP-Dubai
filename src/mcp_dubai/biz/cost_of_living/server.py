"""FastMCP server for cost_of_living."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.cost_of_living import tools

mcp: FastMCP = FastMCP("cost_of_living")


@mcp.tool
async def cost_of_living_overview() -> dict[str, object]:
    """
    Headline cost-of-living ranges across rent, utilities, groceries,
    transport, and schooling, plus a sample monthly budget for a single
    person, a couple, and a family of four.
    """
    return await tools.cost_of_living_overview()


@mcp.tool
async def rent_estimate(
    area: str = "Dubai Marina",
    bedrooms: str = "1BR",
) -> dict[str, object]:
    """
    Annual rent range (AED) for an area and bedroom size.

    Args:
        area: Area name, case-insensitive (e.g. Dubai Marina, JLT, JVC).
        bedrooms: One of: studio, 1BR, 2BR.
    """
    return await tools.rent_estimate(area=area, bedrooms=bedrooms)


@mcp.tool
async def dewa_bill_estimate(
    unit_size: str = "1BR",
    season: str = "summer",
) -> dict[str, object]:
    """
    Typical monthly DEWA bill for a unit size, with the housing-fee
    explanation and the electricity slab table.

    Args:
        unit_size: One of: studio, 1BR, 2BR, 3BR.
        season: One of: summer, winter. Summer figures already reflect the
            2.5x to 3.5x AC multiplier.
    """
    return await tools.dewa_bill_estimate(unit_size=unit_size, season=season)


@mcp.tool
async def salik_toll_estimate(
    time_of_day: str = "08:00",
    day: str = "weekday",
) -> dict[str, object]:
    """
    Deterministic Salik toll (AED) for a time of day using the official
    variable-pricing windows.

    Args:
        time_of_day: 24-hour HH:MM, e.g. '08:00'.
        day: 'weekday' or 'sunday' (Sunday has a flat toll outside the free
            window).
    """
    return await tools.salik_toll_estimate(time_of_day=time_of_day, day=day)


@mcp.tool
async def grocery_estimate(household_size: str = "single") -> dict[str, object]:
    """
    Monthly and weekly grocery ranges plus the staples basket.

    Args:
        household_size: One of: single, couple, family_of_four.
    """
    return await tools.grocery_estimate(household_size=household_size)


@mcp.tool
async def school_fee_estimate(stage: str = "primary") -> dict[str, object]:
    """
    British-curriculum annual school fee range plus the KHDA fee-cap rule.

    Args:
        stage: One of: foundation_primary, primary, secondary.
    """
    return await tools.school_fee_estimate(stage=stage)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="cost_of_living_overview",
        description=(
            "Headline Dubai cost of living across rent, utilities, groceries, "
            "transport, and schooling, with a sample monthly budget."
        ),
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "cost of living",
            "تكلفة المعيشة",
            "budget",
            "monthly budget",
            "expenses",
            "dubai",
            "expat",
            "overview",
        ],
    ),
    ToolMeta(
        name="rent_estimate",
        description="Annual rent range in AED by Dubai area and bedroom size.",
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "rent",
            "إيجار",
            "rental",
            "apartment",
            "studio",
            "1BR",
            "2BR",
            "dubai marina",
            "jlt",
            "jvc",
            "downtown",
            "smart rental index",
        ],
    ),
    ToolMeta(
        name="dewa_bill_estimate",
        description="Typical monthly DEWA bill, housing fee, and electricity slabs.",
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "dewa",
            "ديوا",
            "electricity",
            "water",
            "utilities",
            "bill",
            "housing fee",
            "tariff",
            "ac",
        ],
    ),
    ToolMeta(
        name="salik_toll_estimate",
        description="Deterministic Salik road toll by time of day using the 2025 windows.",
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "salik",
            "سالك",
            "toll",
            "road toll",
            "gate",
            "peak",
            "off-peak",
            "driving",
            "transport",
        ],
    ),
    ToolMeta(
        name="grocery_estimate",
        description="Monthly and weekly grocery cost ranges and the staples basket.",
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "groceries",
            "بقالة",
            "food",
            "supermarket",
            "carrefour",
            "lulu",
            "union coop",
            "spinneys",
            "basket",
        ],
    ),
    ToolMeta(
        name="school_fee_estimate",
        description="British-curriculum school fee range and the KHDA fee-cap rule.",
        feature="cost_of_living",
        tier=TIER_BIZ,
        tags=[
            "school fees",
            "رسوم المدارس",
            "khda",
            "british curriculum",
            "education",
            "primary",
            "secondary",
            "tuition",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
