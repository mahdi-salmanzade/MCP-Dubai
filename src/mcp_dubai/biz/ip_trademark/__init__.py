"""ip_trademark: UAE IP and trademark via MOET. Tier 2."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "ip_trademark",
    "description": (
        "UAE intellectual property and trademark registration via the "
        "Ministry of Economy and Tourism (MOET, formerly Ministry of "
        "Economy). Includes Cabinet Resolution 102 of 2025 fee schedule "
        "with 50% SME discount."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://moet.gov.ae",
}
