"""
Real-time air quality for Dubai via WAQI / AQICN.

Dubai Municipality has no first-party air quality API (brief section 5.6).
The recommended substitute is WAQI/AQICN, which exposes Dubai stations
(Karama, Jebel Ali Village, Nad Al Shiba, plus a few inactive ones) with
PM2.5, PM10, NO2, SO2, CO, O3.

Tier: 0 (with free key from https://aqicn.org/data-platform/token/)
Source: https://aqicn.org/api/
Brief section: 5.6

This feature uses Pattern 2 (graceful credential degradation): tools never
crash when MCP_DUBAI_WAQI_TOKEN is missing. They return a structured
"token_missing" error in the standard ToolResponse envelope.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "air_quality",
    "description": (
        "Real-time air quality (PM2.5, PM10, NO2, SO2, CO, O3) for Dubai "
        "stations via WAQI/AQICN. Requires a free token from aqicn.org."
    ),
    "tier": 0,
    "requires_auth": True,
    "source_url": "https://aqicn.org/api/",
}
