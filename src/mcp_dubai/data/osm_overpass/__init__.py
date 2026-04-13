"""
OpenStreetMap Overpass: POI fallback for Dubai.

Dubai Pulse has no general points-of-interest dataset (brief section 5.9).
OSM Overpass is the realistic fallback. We expose narrow tools that wrap
common Overpass QL queries so the LLM does not have to learn the QL
syntax.

Tier: 0 (no auth, but please rate-limit yourself, the public Overpass
endpoint is community-funded)
Source: https://wiki.openstreetmap.org/wiki/Overpass_API
Brief section: 5.9 (DM GIS, POI, food, permits)
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "osm_overpass",
    "description": (
        "OpenStreetMap POI search around a Dubai location via Overpass QL. "
        "Used as the fallback when Dubai Pulse has no native POI dataset."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://wiki.openstreetmap.org/wiki/Overpass_API",
}
