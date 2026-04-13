"""
Al-Quran Cloud: keyless free API for Quran text and translations.

Sibling project of Al-Adhan, linked from aladhan.com. Endpoints at
api.alquran.cloud/v1 cover surahs, ayahs, juz, and search across multiple
editions.

Tier: 0 (no auth)
Source: https://alquran.cloud/api
Brief section: 5.8
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "quran_cloud",
    "description": (
        "Free, keyless Quran text and translation API. Surahs, ayahs, juz, "
        "search, and multiple editions including Arabic and translations."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://alquran.cloud/api",
}
