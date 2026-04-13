"""parkin: Dubai parking and Nol fares (NOT Mawaqif). Tier 2."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "parkin",
    "description": (
        "Dubai parking (run by Parkin Company PJSC, NOT 'Mawaqif' which is "
        "Abu Dhabi) tariffs and zones. Plus Nol card guide and RTA fares."
    ),
    "tier": 2,
    "requires_auth": False,
    "source_url": "https://parkin.ae",
}
