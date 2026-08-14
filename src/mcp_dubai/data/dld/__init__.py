"""
DLD: Dubai Land Department real estate data via Dubai Pulse.

The DLD API Gateway is paywalled at ~AED 31,500/year per product. The
realistic open path is the former Dubai Pulse gateway, which exposes the
same datasets as `dld_*-open-api` over the standard OAuth2
client_credentials flow.

Tier: 1 (Dubai Pulse OAuth required)
Source: https://apis.data.dubai
Brief section: 5.1 (real estate, DLD, Ejari, Trakheesi)

Migration note (verified 2026-07-02): the Dubai Pulse portal
(www.dubaipulse.gov.ae) was decommissioned between Dec 2025 and Jan 2026
and now redirects to https://data.dubai. Request dataset access and
credentials at https://data.dubai; the canonical API host going forward
is apis.data.dubai (same endpoint pattern, still OAuth).
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
    "source_url": "https://apis.data.dubai",
}
