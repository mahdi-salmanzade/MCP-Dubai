"""FastMCP server for osm_overpass."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.osm_overpass import tools

mcp: FastMCP = FastMCP("osm_overpass")


@mcp.tool
async def osm_search_poi(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = 1000,
    limit: int = 25,
) -> dict[str, object]:
    """
    Find OpenStreetMap points of interest near a Dubai location.

    Args:
        latitude: Centre latitude.
        longitude: Centre longitude.
        category: One of: restaurant, cafe, fast_food, pharmacy, hospital,
            clinic, atm, bank, fuel, school, kindergarten, mosque,
            supermarket, mall, bus_stop, metro_station, parking, park,
            gym, hotel, embassy, post_office.
        radius_meters: Search radius in metres (max 10000).
        limit: Max results to return.

    Returns:
        Dict with `count`, `category`, `centre`, `radius_meters`, and
        `results` (list of OSM nodes with id, name, lat/lon, and key tags).
    """
    return await tools.osm_search_poi(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius_meters=radius_meters,
        limit=limit,
    )


@mcp.tool
async def osm_list_categories() -> dict[str, object]:
    """List the curated POI categories supported by `osm_search_poi`."""
    return await tools.osm_list_categories()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="osm_search_poi",
        description=(
            "Find OpenStreetMap POIs near a Dubai location: restaurants, "
            "pharmacies, mosques, ATMs, metro stations, malls, parking, etc."
        ),
        feature="osm_overpass",
        tier=TIER_OPEN,
        tags=[
            "poi",
            "osm",
            "openstreetmap",
            "near",
            "nearby",
            "around",
            "restaurant",
            "pharmacy",
            "atm",
            "mall",
            "metro",
            "mosque",
            "hospital",
            "clinic",
            "supermarket",
            "dubai",
        ],
    ),
    ToolMeta(
        name="osm_list_categories",
        description="List the POI categories supported by osm_search_poi.",
        feature="osm_overpass",
        tier=TIER_OPEN,
        tags=["osm", "categories", "list", "poi"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
