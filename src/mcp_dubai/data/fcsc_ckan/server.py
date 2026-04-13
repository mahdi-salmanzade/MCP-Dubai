"""FastMCP server for FCSC CKAN."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.fcsc_ckan import tools

mcp: FastMCP = FastMCP("fcsc_ckan")


@mcp.tool
async def fcsc_search_dataset(
    query: str = "",
    rows: int = 10,
    start: int = 0,
    organization: str | None = None,
) -> dict[str, object]:
    """
    Search the FCSC UAE federal open data portal for datasets.

    Args:
        query: Free-text Solr query, e.g., "trade", "population", "energy".
            Empty string returns recent datasets.
        rows: Maximum results per page (1 to 100, default 10).
        start: Pagination offset.
        organization: Optional CKAN organization slug filter.

    Returns:
        Dict with `count`, `results` (dataset metadata array), and pagination.
    """
    return await tools.fcsc_search_dataset(
        query=query, rows=rows, start=start, organization=organization
    )


@mcp.tool
async def fcsc_get_dataset(dataset_id: str) -> dict[str, object]:
    """
    Get full metadata for a specific FCSC dataset.

    Args:
        dataset_id: CKAN dataset id or slug.

    Returns:
        Full dataset metadata including resources (download URLs).
    """
    return await tools.fcsc_get_dataset(dataset_id=dataset_id)


@mcp.tool
async def fcsc_list_organizations() -> dict[str, object]:
    """
    List all CKAN organizations publishing on the FCSC portal.

    Useful for finding the right org slug to use as a filter on
    `fcsc_search_dataset`.
    """
    return await tools.fcsc_list_organizations()


@mcp.tool
async def fca_trade_stats(query: str = "", rows: int = 10) -> dict[str, object]:
    """
    Search Federal Customs Authority trade statistics datasets.

    Convenience wrapper that filters `fcsc_search_dataset` to the
    `federal-customs-authority` organization. Covers UAE non-oil foreign
    trade by HS chapter, imports, exports, and re-exports.
    """
    return await tools.fca_trade_stats(query=query, rows=rows)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="fcsc_search_dataset",
        description="Search UAE federal open data datasets via the FCSC CKAN portal.",
        feature="fcsc_ckan",
        tier=TIER_OPEN,
        tags=[
            "fcsc",
            "uae",
            "federal",
            "open data",
            "ckan",
            "dataset",
            "search",
            "statistics",
        ],
    ),
    ToolMeta(
        name="fcsc_get_dataset",
        description="Get full metadata and download URLs for a specific FCSC dataset.",
        feature="fcsc_ckan",
        tier=TIER_OPEN,
        tags=["fcsc", "ckan", "dataset", "metadata", "download"],
    ),
    ToolMeta(
        name="fcsc_list_organizations",
        description="List all federal organizations publishing on the FCSC CKAN portal.",
        feature="fcsc_ckan",
        tier=TIER_OPEN,
        tags=["fcsc", "ckan", "organization", "list", "federal"],
    ),
    ToolMeta(
        name="fca_trade_stats",
        description=(
            "Search Federal Customs Authority UAE trade statistics: imports, "
            "exports, re-exports, by HS chapter."
        ),
        feature="fcsc_ckan",
        tier=TIER_OPEN,
        tags=[
            "fca",
            "customs",
            "trade",
            "import",
            "export",
            "re-export",
            "hs code",
            "hs chapter",
            "uae",
            "tariff",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
