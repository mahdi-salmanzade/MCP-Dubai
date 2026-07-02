"""FastMCP server for data_dubai (credential-free catalog on data.dubai)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.data_dubai import tools

mcp: FastMCP = FastMCP("data_dubai")


@mcp.tool
async def data_dubai_search(
    query: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict[str, object]:
    """
    Search the data.dubai catalog for dataset metadata (no credentials).

    data.dubai is the portal that replaced Dubai Pulse. This searches its
    catalog of 600+ dataset descriptions. METADATA ONLY: the dataset APIs
    themselves still require Dubai Pulse/DDSE credentials.

    Args:
        query: Free-text search over titles, descriptions, and keywords.
            Empty string lists the full catalog.
        page: 1-based page number.
        page_size: Datasets per page, 1 to 100.
    """
    return await tools.data_dubai_search(query=query, page=page, page_size=page_size)


@mcp.tool
async def data_dubai_themes() -> dict[str, object]:
    """
    List the data.dubai catalog themes with dataset counts (no credentials).

    Eleven themes such as Infrastructure, Population, Trade, and
    Employment, each with bilingual titles and a dataset count.
    """
    return await tools.data_dubai_themes()


@mcp.tool
async def data_dubai_entities(search: str = "") -> dict[str, object]:
    """
    List data.dubai issuing entities, optionally filtered (no credentials).

    Issuing entities are the publishers behind the catalog (RTA, DEWA,
    Dubai Police, and 70+ more). Filtering is client-side.

    Args:
        search: Case-insensitive substring matched against each entity's
            English title, Arabic title, and short key. Empty string
            returns every entity.
    """
    return await tools.data_dubai_entities(search=search)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="data_dubai_search",
        description=(
            "Search the data.dubai open-data catalog (the Dubai Pulse "
            "successor) for dataset metadata: titles, descriptions, themes, "
            "formats, update frequency. Credential-free, metadata only."
        ),
        feature="data_dubai",
        tier=TIER_OPEN,
        tags=[
            "open data",
            "dataset",
            "catalog",
            "search",
            "data.dubai",
            "dubai pulse",
            "metadata",
            "government data",
            "portal",
            "بيانات مفتوحة",
            "مجموعة بيانات",
            "بحث",
            "دبي",
        ],
    ),
    ToolMeta(
        name="data_dubai_themes",
        description=(
            "List the 11 data.dubai catalog themes (Infrastructure, "
            "Population, Trade, Employment, and more) with bilingual titles "
            "and dataset counts. Credential-free."
        ),
        feature="data_dubai",
        tier=TIER_OPEN,
        tags=[
            "open data",
            "themes",
            "categories",
            "topics",
            "catalog",
            "data.dubai",
            "browse",
            "مواضيع",
            "فئات",
            "بيانات مفتوحة",
            "دبي",
        ],
    ),
    ToolMeta(
        name="data_dubai_entities",
        description=(
            "List the 76 issuing entities publishing on data.dubai (RTA, "
            "DEWA, Dubai Police, Dubai Municipality, and more), with an "
            "optional client-side name filter. Credential-free."
        ),
        feature="data_dubai",
        tier=TIER_OPEN,
        tags=[
            "open data",
            "issuing entities",
            "publishers",
            "government departments",
            "agencies",
            "data.dubai",
            "rta",
            "dewa",
            "municipality",
            "جهات حكومية",
            "ناشر",
            "بيانات مفتوحة",
            "دبي",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
