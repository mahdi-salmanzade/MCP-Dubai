"""gov_portals: UAE government digital portal lookup. Tier 2."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "gov_portals",
    "description": (
        "UAE government digital portals: UAE Pass, Basher, Invest in "
        "Dubai, EmaraTax, MOHRE, GDRFA, ICP, Dubai Now, u.ae, and more. "
        "Includes disambiguation for Sahel (Kuwait, not UAE)."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://u.ae",
}
