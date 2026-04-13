"""WAQI / AQICN endpoints and Dubai stations."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import WAQI_BASE

# WAQI API endpoints take a station path or geo coordinates.
FEED_BY_CITY: Final[str] = f"{WAQI_BASE}/feed/{{path}}/"
FEED_BY_GEO: Final[str] = f"{WAQI_BASE}/feed/geo:{{lat}};{{lon}}/"

DUBAI_STATIONS: Final[dict[str, str]] = {
    "karama": "Karama",
    "jebel-ali-village": "Jebel Ali Village",
    "nad-al-shiba": "Nad Al Shiba",
}

DEFAULT_STATION: Final[str] = "karama"
