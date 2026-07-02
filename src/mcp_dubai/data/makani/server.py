"""FastMCP server for makani (Dubai Municipality geo-addressing)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.makani import tools

mcp: FastMCP = FastMCP("makani")


@mcp.tool
async def makani_reverse_geocode(latitude: float, longitude: float) -> dict[str, object]:
    """
    Find the Makani numbers and building at a Dubai coordinate (no key).

    Reverse geocodes against the official Dubai Municipality Makani public
    service: building, community, and emirate names in English and Arabic,
    plus every Makani number at that location with its coordinates and
    short URL.

    Args:
        latitude: Latitude in decimal degrees (WGS84), e.g. 25.26464.
        longitude: Longitude in decimal degrees (WGS84), e.g. 55.31217.
    """
    return await tools.makani_reverse_geocode(latitude=latitude, longitude=longitude)


@mcp.tool
async def makani_details(makani_number: str) -> dict[str, object]:
    """
    Look up the building behind a 10-digit Makani number (no key).

    Returns building, community, and emirate names in English and Arabic,
    exact coordinates, and the official makani.ae short URL.

    Args:
        makani_number: Makani number, 10 digits with or without a space,
            e.g. "30032 95320" or "3003295320".
    """
    return await tools.makani_details(makani_number=makani_number)


@mcp.tool
async def makani_validate(makani_number: str) -> dict[str, object]:
    """
    Check whether a 10-digit Makani number exists (no key).

    Returns a validity boolean plus the emirate (English and Arabic) when
    the number is valid.

    Args:
        makani_number: Makani number, 10 digits with or without a space,
            e.g. "30032 95320" or "3003295320".
    """
    return await tools.makani_validate(makani_number=makani_number)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="makani_reverse_geocode",
        description=(
            "Find the Makani numbers and building at a Dubai coordinate via "
            "the official Dubai Municipality public service. Returns building, "
            "community, and emirate in English and Arabic plus each Makani "
            "number with coordinates and short URL."
        ),
        feature="makani",
        tier=TIER_OPEN,
        tags=[
            "makani",
            "address",
            "geo address",
            "reverse geocode",
            "coordinates",
            "location",
            "building",
            "community",
            "dubai municipality",
            "what is here",
            "مكاني",
            "عنوان",
            "رقم مكاني",
            "احداثيات",
            "موقع",
            "بلدية دبي",
        ],
    ),
    ToolMeta(
        name="makani_details",
        description=(
            "Look up the building behind a 10-digit Makani number: building, "
            "community, and emirate names in English and Arabic, exact "
            "coordinates, and the official makani.ae short URL. Official "
            "Dubai Municipality public service."
        ),
        feature="makani",
        tier=TIER_OPEN,
        tags=[
            "makani",
            "makani number",
            "address lookup",
            "geocode",
            "building",
            "location",
            "coordinates",
            "navigate",
            "dubai municipality",
            "مكاني",
            "رقم مكاني",
            "عنوان المبنى",
            "تفاصيل مكاني",
            "موقع",
            "بلدية دبي",
        ],
    ),
    ToolMeta(
        name="makani_validate",
        description=(
            "Check whether a 10-digit Makani number exists and which emirate "
            "it belongs to. Official Dubai Municipality public service."
        ),
        feature="makani",
        tier=TIER_OPEN,
        tags=[
            "makani",
            "validate",
            "verify",
            "check",
            "makani number",
            "valid",
            "address",
            "dubai municipality",
            "مكاني",
            "رقم مكاني",
            "تحقق",
            "صحة",
            "عنوان",
            "بلدية دبي",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
