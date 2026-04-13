"""
Curated UAE federal public holidays.

Lunar holidays use placeholder dates that need to be re-verified against
the MoHRE circular (typically published 10 days before the date) and the
Saudi Umm al-Qura calendar. Each lunar entry is flagged with `provisional=True`.

Knowledge date: 2026-04-12.
Source: u.ae federal holidays page and MoHRE circulars.
"""

from __future__ import annotations

from typing import Final, TypedDict


class Holiday(TypedDict):
    name: str
    name_ar: str
    date: str  # ISO YYYY-MM-DD
    provisional: bool
    category: str  # "fixed" | "lunar"


# 2026 UAE federal public holidays. Provisional dates flagged.
HOLIDAYS_2026: Final[list[Holiday]] = [
    {
        "name": "New Year's Day",
        "name_ar": "رأس السنة الميلادية",
        "date": "2026-01-01",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "Eid Al Fitr",
        "name_ar": "عيد الفطر",
        "date": "2026-03-20",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2026-03-21",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Fitr Holiday",
        "name_ar": "عيد الفطر",
        "date": "2026-03-22",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Arafat Day",
        "name_ar": "يوم عرفة",
        "date": "2026-05-26",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-27",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-28",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Eid Al Adha Holiday",
        "name_ar": "عيد الأضحى",
        "date": "2026-05-29",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Hijri New Year",
        "name_ar": "رأس السنة الهجرية",
        "date": "2026-06-16",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Prophet Muhammad's Birthday",
        "name_ar": "المولد النبوي الشريف",
        "date": "2026-08-25",
        "provisional": True,
        "category": "lunar",
    },
    {
        "name": "Commemoration Day",
        "name_ar": "يوم الشهيد",
        "date": "2026-12-01",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "UAE National Day",
        "name_ar": "اليوم الوطني للإمارات",
        "date": "2026-12-02",
        "provisional": False,
        "category": "fixed",
    },
    {
        "name": "UAE National Day Holiday",
        "name_ar": "اليوم الوطني للإمارات",
        "date": "2026-12-03",
        "provisional": False,
        "category": "fixed",
    },
]


HOLIDAYS_BY_YEAR: Final[dict[int, list[Holiday]]] = {
    2026: HOLIDAYS_2026,
}
