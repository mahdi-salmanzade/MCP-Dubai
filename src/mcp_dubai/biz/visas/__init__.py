"""
visas: UAE visa lookup and recommendation.

Tier: 2 (curated business knowledge)
Brief section: 6.3
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "visas",
    "description": (
        "UAE visa lookup and recommendation: tourist, employment, "
        "investor/partner, Golden Visa (all categories), Green Visa "
        "(skilled vs freelancer tracks), freelance permit, Virtual "
        "Working, retirement, family/dependent."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://u.ae/en/information-and-services/visa-and-emirates-id",
}
