"""
Al-Adhan: Islamic services (prayer times, Qibla, Hijri calendar).

The Al-Adhan API at https://api.aladhan.com/v1 is keyless and free, with
documented rate limit of approximately 12 requests per second per IP.
This is the gold-standard free integration for Islamic services.

Tier: 0 (no auth required)
Source: https://aladhan.com/prayer-times-api
Brief section: 5.8 (tourism, culture, Islamic services)
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "al_adhan",
    "description": (
        "Islamic services: prayer times, Qibla compass direction, "
        "Hijri to Gregorian calendar conversion. Powered by the keyless "
        "Al-Adhan API."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://aladhan.com/prayer-times-api",
}
