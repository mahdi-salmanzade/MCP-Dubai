"""Dubai retail gold rates from Dubai City of Gold (keyless, no signup).

The Dubai Jewellery Group publishes suggested retail gold rates (AED per
gram for 24K, 22K, 21K, 18K and 14K) on dubaicityofgold.com, refreshed
around 09:00, 13:30 and 18:00 UAE time. The site's JSON API sits behind
a WAF, so this feature parses the server-rendered homepage HTML instead.
These are jewellery retail reference rates, not spot bullion prices.

Tier: 0 (no auth)
Source: https://dubaicityofgold.com/
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "gold_rate",
    "description": (
        "Dubai Jewellery Group suggested retail gold rates (AED per gram, "
        "24K to 14K) parsed from the Dubai City of Gold homepage. Keyless. "
        "Retail reference rates, not spot bullion."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://dubaicityofgold.com/",
}
