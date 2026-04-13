"""
banking: UAE business banking matrix and DUL fast-track lookup.

Tier: 2 (curated business knowledge)
Brief section: 6.5
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "banking",
    "description": (
        "UAE business banking: 14 banks compared on onboarding speed, "
        "minimum balance, crypto stance. Plus DUL (Dubai Unified Licence) "
        "fast-track eligibility check."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://www.centralbank.ae",
}
