"""
RTA: Roads and Transport Authority data via Dubai Pulse.

Tier: 1 (Dubai Pulse OAuth required)
Source: https://apis.data.dubai
Brief section: 5.2 (transport)

Note: the GTFS static feed remains anonymously downloadable as a direct
7z file from the legacy Dubai Pulse host (the old Transitland mirror now
returns 401), but the query APIs for the RTA datasets require OAuth
credentials. The Dubai Pulse portal itself was decommissioned and now
redirects to https://data.dubai.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "rta",
    "description": (
        "Dubai Roads and Transport Authority data via Dubai Pulse: metro "
        "stations, bus routes, tram, taxi, marine transport, Salik tariff."
    ),
    "tier": 1,
    "requires_auth": True,
    "source_url": "https://apis.data.dubai",
}
