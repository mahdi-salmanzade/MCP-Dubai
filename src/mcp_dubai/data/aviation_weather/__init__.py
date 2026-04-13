"""
Aviation weather (METAR / TAF) for UAE airports via aviationweather.gov.

NCM (UAE National Center of Meteorology) does not expose a public API
(brief section 5.6). The recommended substitute for UAE airport weather
is the US aviationweather.gov API filtered to UAE ICAO codes.

Tier: 0 (no auth)
Source: https://aviationweather.gov/data/api/
Brief section: 5.6 (utilities, environment, immigration)

UAE ICAOs covered: OMDB (Dubai International), OMDW (Al Maktoum),
OMSJ (Sharjah), OMAA (Abu Dhabi), OMAL (Al Ain), OMRK (Ras Al Khaimah).
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "aviation_weather",
    "description": (
        "METAR (current observation) and TAF (forecast) for UAE airports. "
        "Sourced from aviationweather.gov, no auth, the standard substitute "
        "for the missing NCM public API."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://aviationweather.gov/data/api/",
}
