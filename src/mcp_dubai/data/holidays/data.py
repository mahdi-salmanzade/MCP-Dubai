"""
Curated UAE federal public holidays.

Fixed-date holidays follow Cabinet Resolution 27/2024 (in force since
2025-01-01). Lunar holidays are confirmed against MOHRE/FAHR circulars once
published; unconfirmed entries are flagged with `provisional=True`. Entries
may carry an optional `note` with observance details (transferred days,
sector differences, pending circulars).

Commemoration Day (1 December) is deliberately NOT listed as a holiday:
under Cabinet Resolution 27/2024 it is a national observance (a minute of
silence at 11:30) with NO day off, and it does not appear on the official
u.ae public holidays list. Do not re-add it as a holiday entry.

2027 note: no official Cabinet-approved 2027 holiday calendar has been
published as of 2026-07-02. All 2027 lunar dates are astronomical
expectations subject to moon sighting and MOHRE/FAHR confirmation.

Knowledge date: 2026-07-02.
Sources:
- https://u.ae/en/information-and-services/public-holidays-and-religious-affairs/public-holidays
- https://uaelegislation.gov.ae/en/legislations/2595 (Cabinet Resolution 27/2024)
- https://www.mohre.gov.ae/ and https://www.fahr.gov.ae/ holiday circulars
"""

from __future__ import annotations

from typing import Final, NotRequired, TypedDict


class Holiday(TypedDict):
    name: str
    name_ar: str
    date: str  # ISO YYYY-MM-DD
    provisional: bool
    category: str  # "fixed" | "lunar"
    note: NotRequired[str]  # observance details, when relevant


# 2026 UAE federal public holidays. Observed dates confirmed through the
# Hijri New Year (June); the Prophet's Birthday remains provisional.
HOLIDAYS_2026: Final[list[Holiday]] = [
    {
        "name": "New Year's Day",
        "name_ar": "رأس السنة الميلادية",
        "date": "2026-01-01",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2026-03-19",
        "provisional": False,
        "category": "lunar",
        "note": (
            "30 Ramadan 1447. Ramadan lasted 30 days, so this day became a "
            "holiday under Cabinet Resolution 27/2024. Observed 19-22 March "
            "in both the public and private sectors."
        ),
    },
    {
        "name": "Eid Al Fitr",
        "name_ar": "عيد الفطر",
        "date": "2026-03-20",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2026-03-21",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2026-03-22",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Arafat Day",
        "name_ar": "يوم عرفة",
        "date": "2026-05-26",
        "provisional": False,
        "category": "lunar",
        "note": (
            "The federal public sector additionally received Monday "
            "2026-05-25 off (FAHR circular, holiday 25-29 May); the private "
            "sector holiday ran 26-29 May (MOHRE circular)."
        ),
    },
    {
        "name": "Eid Al Adha",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-27",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-28",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-29",
        "provisional": False,
        "category": "lunar",
    },
    {
        "name": "Hijri New Year",
        "name_ar": "رأس السنة الهجرية",
        "date": "2026-06-15",
        "provisional": False,
        "category": "lunar",
        "note": (
            "Observed Monday 2026-06-15 for both sectors, moved to the start "
            "of the week under the Cabinet Resolution 27/2024 "
            "transferable-holiday rule. The religious date (1 Muharram 1448) "
            "fell Tuesday 2026-06-16, which was a normal working day."
        ),
    },
    {
        "name": "Prophet Muhammad's Birthday",
        "name_ar": "المولد النبوي الشريف",
        "date": "2026-08-24",
        "provisional": True,
        "category": "lunar",
        "note": (
            "Expected observed day off is Monday 2026-08-24 under the "
            "transferable-holiday rule (dates use the expected observed day, "
            "matching the Hijri New Year convention). The religious date, "
            "12 Rabi Al Awwal 1448, is expected Tuesday 2026-08-25. The "
            "official MOHRE/FAHR circular is pending as of 2026-07-02."
        ),
    },
    {
        "name": "Eid Al Etihad (UAE National Day)",
        "name_ar": "عيد الاتحاد",
        "date": "2026-12-02",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "Eid Al Etihad (UAE National Day) Holiday",
        "name_ar": "عيد الاتحاد",
        "date": "2026-12-03",
        "provisional": False,
        "category": "fixed",
    },
]


# 2027 UAE federal public holidays. No official Cabinet-approved 2027
# calendar exists as of 2026-07-02; all lunar dates are astronomical
# expectations and flagged provisional=True.
HOLIDAYS_2027: Final[list[Holiday]] = [
    {
        "name": "New Year's Day",
        "name_ar": "رأس السنة الميلادية",
        "date": "2027-01-01",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "Eid Al Fitr",
        "name_ar": "عيد الفطر",
        "date": "2027-03-09",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2027-03-10",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2027-03-11",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Arafat Day",
        "name_ar": "يوم عرفة",
        "date": "2027-05-15",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha",
        "name_ar": "عيد الأضحى",
        "date": "2027-05-16",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2027-05-17",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2027-05-18",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Hijri New Year",
        "name_ar": "رأس السنة الهجرية",
        "date": "2027-06-07",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Prophet Muhammad's Birthday",
        "name_ar": "المولد النبوي الشريف",
        "date": "2027-08-16",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Etihad (UAE National Day)",
        "name_ar": "عيد الاتحاد",
        "date": "2027-12-02",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "Eid Al Etihad (UAE National Day) Holiday",
        "name_ar": "عيد الاتحاد",
        "date": "2027-12-03",
        "provisional": False,
        "category": "fixed",
    },
]


# Year-level caveats surfaced alongside the holiday list by the tools layer.
DATASET_NOTES: Final[dict[int, str]] = {
    2027: (
        "No official Cabinet-approved 2027 holiday calendar has been "
        "published as of 2026-07-02. All 2027 lunar dates are astronomical "
        "expectations subject to moon sighting and MOHRE/FAHR confirmation."
    ),
}


HOLIDAYS_BY_YEAR: Final[dict[int, list[Holiday]]] = {
    2026: HOLIDAYS_2026,
    2027: HOLIDAYS_2027,
}
