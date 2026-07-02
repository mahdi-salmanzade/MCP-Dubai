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
KNOWLEDGE_DATE: str = "2026-07-02"


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
# RTA GTFS static feed: the old transit.land mirror started returning 401 in
# 2026 (Transitland now requires an API token). The Dubai Pulse direct
# download below still serves anonymously (verified 2026-07-02): a ~10 MB
# 7-zip archive (not a plain zip) containing the GTFS text files.
RTA_GTFS_DOWNLOAD_URL: str = (
    "https://www.dubaipulse.gov.ae/dataset/73765e8f-e8c4-443c-9687-288072ed9d12/"
    "resource/11515bd3-bdba-466f-ab65-f057bd123ab5/download/gtfs.7z"
)
# Open-Meteo: keyless human-friendly weather and forecast (no token, no signup).
OPEN_METEO_BASE: str = "https://api.open-meteo.com/v1"
# Dubai Financial Market: anonymous JSON market-data endpoints behind the
# dfm.ae website (undocumented, best-effort). Verified 2026-07-02.
DFM_API_BASE: str = "https://api2.dfm.ae"
# Makani (Dubai Municipality geo-addressing): anonymous public SOAP service.
# Attribution to Dubai Municipality is required by the service licence.
MAKANI_SOAP_ENDPOINT: str = "https://www.makani.ae/MakaniPublicDataService/MakaniPublic.svc/basic"
# Dubai City of Gold (Dubai Jewellery Group): retail gold rates page,
# server-rendered HTML, updated three times daily (09:00, 13:30, 18:00 UAE).
GOLD_RATE_PAGE: str = "https://dubaicityofgold.com/"
# data.dubai catalog: credential-free Liferay Objects JSON API on the portal
# that replaced Dubai Pulse (metadata only; dataset APIs need credentials).
DATA_DUBAI_CATALOG_BASE: str = "https://data.dubai/o/c"

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
