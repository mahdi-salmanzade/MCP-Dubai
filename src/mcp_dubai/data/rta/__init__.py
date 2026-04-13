"""
RTA: Roads and Transport Authority data via Dubai Pulse.

Tier: 1 (Dubai Pulse OAuth required)
Source: https://api.dubaipulse.gov.ae
Brief section: 5.2 (transport)

Note: GTFS static feed is also available at the public Transitland mirror
without auth, but the rest of the RTA datasets require Dubai Pulse OAuth.
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
    "source_url": "https://api.dubaipulse.gov.ae",
}
