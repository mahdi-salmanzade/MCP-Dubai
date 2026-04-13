"""FastMCP server for DLD."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_DUBAI_PULSE,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.dld import tools

mcp: FastMCP = FastMCP("dld")


@mcp.tool
async def dld_search_transactions(
    area: str | None = None,
    property_type: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search Dubai Land Department real estate sale transactions.

    Tier 1 tool. Requires Dubai Pulse credentials. Returns a structured
    error if MCP_DUBAI_PULSE_CLIENT_ID and MCP_DUBAI_PULSE_CLIENT_SECRET
    are not set.

    Args:
        area: Optional area name filter (e.g., "Dubai Marina").
        property_type: Optional type filter (e.g., "Apartment", "Villa").
        limit: Max records (1 to 500, default 100).
    """
    return await tools.dld_search_transactions(area=area, property_type=property_type, limit=limit)


@mcp.tool
async def dld_search_rent_contracts(
    area: str | None = None,
    bedrooms: int | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search DLD rent contracts (Ejari data) via Dubai Pulse.

    Tier 1 tool, requires Dubai Pulse credentials.

    Args:
        area: Optional area name filter.
        bedrooms: Optional bedroom count.
        limit: Max records.
    """
    return await tools.dld_search_rent_contracts(area=area, bedrooms=bedrooms, limit=limit)


@mcp.tool
async def dld_lookup_broker(
    name: str | None = None,
    license_number: str | None = None,
    limit: int = 50,
) -> dict[str, object]:
    """
    Look up RERA-registered Dubai brokers.

    Tier 1 tool, requires Dubai Pulse credentials.

    Args:
        name: Broker name substring.
        license_number: Broker license number.
        limit: Max records.
    """
    return await tools.dld_lookup_broker(name=name, license_number=license_number, limit=limit)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="dld_search_transactions",
        description="Search Dubai Land Department real estate sale transactions via Dubai Pulse.",
        feature="dld",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=[
            "dld",
            "real estate",
            "property",
            "transaction",
            "sale",
            "dubai marina",
            "downtown",
            "apartment",
            "villa",
            "dubai pulse",
        ],
    ),
    ToolMeta(
        name="dld_search_rent_contracts",
        description="Search Dubai rent contracts (Ejari data) via Dubai Pulse DLD dataset.",
        feature="dld",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=[
            "dld",
            "ejari",
            "rent",
            "rental",
            "tenant",
            "landlord",
            "lease",
            "dubai",
            "dubai pulse",
        ],
    ),
    ToolMeta(
        name="dld_lookup_broker",
        description="Look up RERA-registered Dubai real estate brokers.",
        feature="dld",
        tier=TIER_DUBAI_PULSE,
        requires_auth=True,
        tags=[
            "dld",
            "rera",
            "broker",
            "agent",
            "real estate",
            "license",
            "dubai pulse",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
