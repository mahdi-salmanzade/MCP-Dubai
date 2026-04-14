"""
Global constants for MCP-Dubai.

All base URLs are env-overridable so the Dubai Pulse to data.dubai migration
can be handled without code changes. The KNOWLEDGE_DATE constant is the
project-wide freshness stamp surfaced through `get_knowledge_status()`.
"""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from zoneinfo import ZoneInfo


def _read_package_version() -> str:
    """Read the installed package version, falling back to a dev tag."""
    try:
        return _pkg_version("mcp-dubai")
    except PackageNotFoundError:
        return "0.0.0+dev"


PACKAGE_VERSION: str = _read_package_version()

# ----------------------------------------------------------------------------
# Project freshness
# ----------------------------------------------------------------------------
# Bumped when the curated business knowledge files are re-verified.
KNOWLEDGE_DATE: str = "2026-04-14"


# ----------------------------------------------------------------------------
# Dubai Pulse (gateway for ~20 Dubai government dataset organisations)
# ----------------------------------------------------------------------------
DUBAI_PULSE_API_BASE: str = os.getenv(
    "MCP_DUBAI_PULSE_API_BASE",
    "https://api.dubaipulse.gov.ae",
)
DUBAI_PULSE_TOKEN_URL: str = f"{DUBAI_PULSE_API_BASE}/oauth/client_credential/accesstoken"
# Token TTL is documented as 30 minutes by Dubai Pulse.
DUBAI_PULSE_TOKEN_TTL_SECONDS: int = 1800
# Refresh slightly before expiry to avoid races on long-running calls.
DUBAI_PULSE_TOKEN_REFRESH_BUFFER_SECONDS: int = 60

# ----------------------------------------------------------------------------
# Dubai data portal (web/HTML, used for documentation links only)
# ----------------------------------------------------------------------------
DUBAI_DATA_PORTAL_BASE: str = os.getenv(
    "MCP_DUBAI_DATA_PORTAL_BASE",
    "https://data.dubai",
)

# ----------------------------------------------------------------------------
# Timezone
# ----------------------------------------------------------------------------
UAE_TIMEZONE: ZoneInfo = ZoneInfo("Asia/Dubai")
UAE_TZ_OFFSET: str = "+04:00"

# ----------------------------------------------------------------------------
# Anonymous third-party APIs (no auth, no key)
# ----------------------------------------------------------------------------
ALADHAN_BASE: str = "https://api.aladhan.com/v1"
QURAN_CLOUD_BASE: str = "https://api.alquran.cloud/v1"
FCSC_CKAN_BASE: str = "https://opendata.fcsc.gov.ae/api/3/action"
CBUAE_UMBRACO_BASE: str = "https://www.centralbank.ae/umbraco/Surface"
AVIATION_WEATHER_BASE: str = "https://aviationweather.gov/api/data"
OVERPASS_BASE: str = "https://overpass-api.de/api/interpreter"
TRANSITLAND_GTFS_DUBAI: str = "https://gtfs-source-feeds.transit.land/dubai-rta.zip"

# ----------------------------------------------------------------------------
# Free-key third parties (require a free signup)
# ----------------------------------------------------------------------------
WAQI_BASE: str = "https://api.waqi.info"
CALENDARIFIC_BASE: str = "https://calendarific.com/api/v2"

# ----------------------------------------------------------------------------
# UAE airports for aviationweather.gov METAR/TAF lookups
# ----------------------------------------------------------------------------
UAE_ICAO_CODES: tuple[str, ...] = (
    "OMDB",  # Dubai International
    "OMDW",  # Al Maktoum International
    "OMSJ",  # Sharjah International
    "OMAA",  # Abu Dhabi International
    "OMAL",  # Al Ain International
    "OMRK",  # Ras Al Khaimah International
)

# ----------------------------------------------------------------------------
# HTTP defaults
# ----------------------------------------------------------------------------
HTTP_DEFAULT_TIMEOUT_SECONDS: float = float(os.getenv("MCP_DUBAI_HTTP_TIMEOUT", "30.0"))
HTTP_DEFAULT_MAX_RETRIES: int = int(os.getenv("MCP_DUBAI_HTTP_MAX_RETRIES", "3"))
HTTP_USER_AGENT: str = (
    f"mcp-dubai/{PACKAGE_VERSION} (+https://github.com/mahdi-salmanzade/MCP-Dubai)"
)
