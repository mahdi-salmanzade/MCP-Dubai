"""Dubai Financial Market live market data (keyless, undocumented endpoints).

Reads the anonymous JSON endpoints behind the dfm.ae website (api2.dfm.ae)
for the DFM General Index and every listed security. The endpoints are
undocumented and best-effort: the server ignores query parameters (all
filtering here is client-side), data may be delayed, and shapes can change
without notice. Nothing this feature returns is investment advice.

Tier: 0 (no auth)
Source: https://marketwatch.dfm.ae/
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "dfm",
    "description": (
        "Dubai Financial Market live market data via the anonymous JSON "
        "endpoints behind dfm.ae (api2.dfm.ae): DFM General Index snapshot, "
        "trimmed per-security quotes, and a searchable list of listed "
        "securities. Keyless, undocumented, best-effort; not investment advice."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://marketwatch.dfm.ae/",
}
