"""halal: UAE halal certification via MOIAT (NOT ESMA). Tier 2."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "halal",
    "description": (
        "UAE halal certification via the Ministry of Industry and Advanced "
        "Technology (MOIAT, which absorbed ESMA in 2020). Standards UAE.S "
        "GSO 2055-1, 2055-2, 2055-4, plus UAE.S 993 (slaughter)."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://qc.moiat.gov.ae/en/open-data/halal",
}
