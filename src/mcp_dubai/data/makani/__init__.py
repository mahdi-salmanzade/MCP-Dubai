"""Dubai Municipality Makani geo-addressing (anonymous public SOAP service).

Makani is the official UAE geo-address system: every building entrance
carries a 10-digit Makani number that maps to exact coordinates. This
feature wraps the Dubai Municipality public SOAP service (no key, no
signup) to reverse geocode coordinates to Makani numbers, look up the
details behind a Makani number, and validate one. Attribution to Dubai
Municipality is required by the service licence; resale is prohibited.

Tier: 0 (no auth)
Source: https://www.makani.ae/
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "makani",
    "description": (
        "Dubai Municipality Makani geo-addressing via the official anonymous "
        "public SOAP service: reverse geocode coordinates to Makani numbers, "
        "fetch building details for a Makani number, and validate one. "
        "Attribution required, resale prohibited."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://www.makani.ae/",
}
