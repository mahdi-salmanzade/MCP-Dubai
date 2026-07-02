"""Credential-free catalog search on data.dubai (the Dubai Pulse successor).

The data.dubai portal replaced Dubai Pulse between December 2025 and
January 2026. Its Liferay Objects JSON API (`/o/c/*`) serves catalog
METADATA anonymously: dataset descriptions, themes, and issuing entities.
The dataset APIs themselves (apis.data.dubai) still require Dubai
Pulse/DDSE credentials and return 401 anonymously, and the new portal
exposes no anonymous file download URLs.

Tier: 0 (no auth)
Source: https://data.dubai
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "data_dubai",
    "description": (
        "Credential-free catalog search on data.dubai, the portal that "
        "replaced Dubai Pulse. Metadata only: dataset descriptions, themes, "
        "and issuing entities. The dataset APIs themselves still require "
        "Dubai Pulse/DDSE credentials."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://data.dubai",
}
