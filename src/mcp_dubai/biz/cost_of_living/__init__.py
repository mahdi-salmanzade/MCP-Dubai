"""
cost_of_living: ballpark Dubai living costs plus the deterministic rules.

Tier: 2 (curated business knowledge)

Rents and groceries are market ranges that drift (DLD Smart Rental Index is
the canonical rent source). The deterministic parts are the DEWA tariff slabs
and housing fee, the Salik toll windows, and the KHDA fee-increase cap rule.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "cost_of_living",
    "description": (
        "Dubai cost of living: rent ranges by area and bedroom, DEWA bills "
        "and housing fee, grocery baskets, Nol and Salik transport costs, and "
        "British-curriculum school fees with the KHDA fee-cap rule."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://dubailand.gov.ae",
}
