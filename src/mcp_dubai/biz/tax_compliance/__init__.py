"""
tax_compliance: UAE corporate tax, VAT, QFZP, and compliance lookup.

Tier: 2 (curated business knowledge)
Brief section: 6.4
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "tax_compliance",
    "description": (
        "UAE Corporate Tax (9% above AED 375,000), VAT (5%), QFZP free "
        "zone rules, ESR (dead post-2022), VARA, UBO, PDPL. Includes a "
        "corporate tax estimator and a QFZP eligibility check (SaaS is NOT "
        "a Qualifying Activity per MD 229/2025)."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://tax.gov.ae",
}
