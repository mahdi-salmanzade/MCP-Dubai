"""
DLD: Dubai Land Department real estate data via Dubai Pulse.

The DLD API Gateway is paywalled at ~AED 31,500/year per product. The
realistic open path is Dubai Pulse, which exposes the same datasets as
`dld_*-open-api` over the standard OAuth2 client_credentials flow.

Tier: 1 (Dubai Pulse OAuth required)
Source: https://api.dubaipulse.gov.ae
Brief section: 5.1 (real estate, DLD, Ejari, Trakheesi)
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "dld",
    "description": (
        "Dubai Land Department real estate data via Dubai Pulse: sale "
        "transactions, rent contracts (Ejari data), brokers, developers, "
        "projects."
    ),
    "tier": 1,
    "requires_auth": True,
    "source_url": "https://api.dubaipulse.gov.ae",
}
