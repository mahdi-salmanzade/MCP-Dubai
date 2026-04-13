"""
UAE federal public holidays.

Tier: 0 (no auth)
Source: u.ae and MoHRE federal circulars (HTML, no JSON), curated.
Brief sections: 5.13 (public holidays), 22 (Calendarific is the recommended
third-party API; Nager.Date does NOT support UAE).

Implementation note: Lunar holidays (Eid al-Fitr, Eid al-Adha, Hijri New Year,
Mawlid, Isra and Miraj, Arafat Day) are PROVISIONAL until announced by MoHRE
roughly 10 days before the date. The data file marks each entry with a
`provisional` flag so tools can surface this to the LLM.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "holidays",
    "description": (
        "UAE federal public holidays. Lunar holidays are flagged as "
        "provisional until officially announced by MoHRE."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://u.ae/en/information-and-services/jobs/public-holidays",
}
