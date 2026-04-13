"""OSM Overpass POI search tools."""

from __future__ import annotations

from typing import Any

from mcp_dubai.data.osm_overpass import constants
from mcp_dubai.data.osm_overpass.client import OverpassClient


def _format_node(node: dict[str, Any]) -> dict[str, object]:
    """Strip an OSM node down to LLM-friendly fields."""
    tags = node.get("tags", {}) or {}
    return {
        "id": node.get("id"),
        "name": tags.get("name") or tags.get("name:en"),
        "name_ar": tags.get("name:ar"),
        "latitude": node.get("lat"),
        "longitude": node.get("lon"),
        "tags": {
            k: v
            for k, v in tags.items()
            if k
            in {
                "amenity",
                "shop",
                "tourism",
                "leisure",
                "highway",
                "railway",
                "religion",
                "cuisine",
                "phone",
                "website",
                "opening_hours",
                "addr:street",
                "addr:city",
            }
        },
    }


async def osm_search_poi(
    latitude: float,
    longitude: float,
    category: str,
    radius_meters: int = constants.DEFAULT_RADIUS_METERS,
    limit: int = constants.DEFAULT_LIMIT,
) -> dict[str, object]:
    """
    Search for POIs of a given category around a coordinate.

    Args:
        latitude: Centre latitude.
        longitude: Centre longitude.
        category: One of the curated categories (see `osm_list_categories`),
            e.g., "restaurant", "pharmacy", "metro_station", "mosque".
        radius_meters: Search radius (max 10000).
        limit: Max results to return after the Overpass query.
    """
    if not -90 <= latitude <= 90:
        raise ValueError(f"latitude must be -90 to 90, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"longitude must be -180 to 180, got {longitude}")
    if radius_meters < 1 or radius_meters > constants.MAX_RADIUS_METERS:
        raise ValueError(
            f"radius_meters must be 1 to {constants.MAX_RADIUS_METERS}, got {radius_meters}"
        )
    if limit < 1 or limit > 100:
        raise ValueError(f"limit must be 1 to 100, got {limit}")

    if category not in constants.COMMON_POI_TAGS:
        raise ValueError(
            f"Unknown category {category!r}. Valid: {sorted(constants.COMMON_POI_TAGS.keys())}"
        )

    selectors = constants.COMMON_POI_TAGS[category]
    client = OverpassClient()
    elements = await client.search_nodes(
        tag_selectors=selectors,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
    )

    formatted = [_format_node(node) for node in elements[:limit]]
    return {
        "count": len(formatted),
        "category": category,
        "centre": {"latitude": latitude, "longitude": longitude},
        "radius_meters": radius_meters,
        "results": formatted,
        "attribution": "Map data \u00a9 OpenStreetMap contributors, ODbL.",
    }


async def osm_list_categories() -> dict[str, object]:
    """List the curated POI categories supported by `osm_search_poi`."""
    return {
        "count": len(constants.COMMON_POI_TAGS),
        "categories": sorted(constants.COMMON_POI_TAGS.keys()),
    }
