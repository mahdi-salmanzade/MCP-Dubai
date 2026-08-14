"""
UAE federal public holidays.

Tier: 0 (no auth)
Source: u.ae plus MOHRE and FAHR holiday circulars (HTML, no JSON), curated.
Brief sections: 5.13 (public holidays), 22 (Calendarific is the recommended
third-party API; Nager.Date does NOT support UAE).

Implementation note: Lunar holidays (Eid al-Fitr, Eid al-Adha, Hijri New Year,
Mawlid, and Arafat Day) remain PROVISIONAL until the relevant MOHRE/private-
sector and FAHR/federal-sector observances are announced. The data file marks
each entry with `provisional` and `official_observance_announced` metadata so
tools can distinguish a religious-date candidate from a confirmed day off.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "holidays",
    "description": (
        "UAE federal public holidays. Lunar holidays are flagged as "
        "provisional until officially announced by MOHRE and FAHR."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": (
        "https://u.ae/en/information-and-services/"
        "public-holidays-and-religious-affairs/public-holidays"
    ),
}
