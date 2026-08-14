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
}

# Verified against the current AQICN station pages on 2026-08-14. WAQI's
# feed API accepts these stable station IDs; the old `dubai/{slug}` paths did
# not identify the advertised stations. No current Nad Al Shiba station could
# be verified, so it is deliberately absent rather than guessed.
DUBAI_STATION_FEED_IDS: Final[dict[str, str]] = {
    "karama": "A470305",
    "jebel-ali-village": "A470308",
}

DEFAULT_STATION: Final[str] = "karama"
