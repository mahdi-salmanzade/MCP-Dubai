"""
setup_advisor: the headline biz/* feature.

Recommends mainland vs free zone vs offshore for a Dubai business setup.
Reads curated data from free_zones.json, visas.json, banks.json, and
tax_compliance.json to ground recommendations in the actual landscape.

Tier: 2 (curated business knowledge, no external API)
Brief section: 6.1
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "setup_advisor",
    "description": (
        "Recommends mainland vs free zone vs offshore for a Dubai business "
        "setup. Cross-references curated free zones, visas, banks, and tax "
        "rules to give grounded, honest recommendations."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://invest.dubai.ae",
}
