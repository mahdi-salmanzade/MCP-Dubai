"""
tenancy: the Dubai tenancy loop.

Bundles Ejari registration, the RERA rent-increase calculator (Decree 43 of
2013), and Rental Disputes Centre (RDC) filing.

Tier: 2 (curated business knowledge)
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "tenancy",
    "description": (
        "The Dubai tenancy loop: Ejari registration documents and fees, the "
        "RERA rent-increase calculator (Decree 43 of 2013), and Rental "
        "Disputes Centre filing fees and steps."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://dubailand.gov.ae/en/eservices/ejari/",
}
