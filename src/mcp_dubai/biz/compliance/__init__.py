"""compliance: ESR, AML, UBO, PDPL frameworks. Tier 2."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "compliance",
    "description": (
        "UAE compliance frameworks: ESR (dead post-2022), AML/CFT, UBO, "
        "PDPL data protection. Stable but enforcement guidance changes."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://www.fiu.gov.ae",
}
