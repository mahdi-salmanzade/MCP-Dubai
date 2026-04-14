"""
KHDA: Dubai private schools, ratings, and curricula.

The Knowledge and Human Development Authority publishes a private schools
directory as a downloadable XLSX at web.khda.gov.ae/en/Resources/KHDA-data-
statistics. This is the cleanest no-auth source for Dubai school data.

Tier: 0 (no auth)
Source: https://web.khda.gov.ae/en/Resources/KHDA-data-statistics
Brief section: 5.4

Implementation note: v0 ships a small curated snapshot of well-known Dubai
schools so the tool is useful out of the box. Contributions to expand the
snapshot from the live KHDA XLSX are welcome (see CONTRIBUTING.md).
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "khda",
    "description": (
        "Dubai private schools directory: curriculum, area, KHDA inspection "
        "rating, fees range, contact info. Curated snapshot from KHDA XLSX."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://web.khda.gov.ae/en/Resources/KHDA-data-statistics",
}
