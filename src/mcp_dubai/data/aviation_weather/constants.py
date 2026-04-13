"""aviationweather.gov endpoints and UAE airport metadata."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import AVIATION_WEATHER_BASE, UAE_ICAO_CODES

METAR_ENDPOINT: Final[str] = f"{AVIATION_WEATHER_BASE}/metar"
TAF_ENDPOINT: Final[str] = f"{AVIATION_WEATHER_BASE}/taf"

UAE_AIRPORTS: Final[dict[str, str]] = {
    "OMDB": "Dubai International",
    "OMDW": "Al Maktoum International",
    "OMSJ": "Sharjah International",
    "OMAA": "Abu Dhabi International",
    "OMAL": "Al Ain International",
    "OMRK": "Ras Al Khaimah International",
}

# Re-export so other modules can do "from constants import UAE_ICAO_CODES".
__all__ = ["METAR_ENDPOINT", "TAF_ENDPOINT", "UAE_AIRPORTS", "UAE_ICAO_CODES"]
