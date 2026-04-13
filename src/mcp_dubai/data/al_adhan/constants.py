"""Al-Adhan API endpoints and calculation method codes."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import ALADHAN_BASE

# ----------------------------------------------------------------------------
# Endpoints (verified live April 2026)
# ----------------------------------------------------------------------------
TIMINGS: Final[str] = f"{ALADHAN_BASE}/timings"
TIMINGS_BY_CITY: Final[str] = f"{ALADHAN_BASE}/timingsByCity"
TIMINGS_BY_ADDRESS: Final[str] = f"{ALADHAN_BASE}/timingsByAddress"
CALENDAR: Final[str] = f"{ALADHAN_BASE}/calendar"
CALENDAR_BY_CITY: Final[str] = f"{ALADHAN_BASE}/calendarByCity"
QIBLA: Final[str] = f"{ALADHAN_BASE}/qibla"
HIJRI_TO_GREGORIAN: Final[str] = f"{ALADHAN_BASE}/gToH"
GREGORIAN_TO_HIJRI: Final[str] = f"{ALADHAN_BASE}/hToG"
ASMA_AL_HUSNA: Final[str] = f"{ALADHAN_BASE}/asmaAlHusna"

# ----------------------------------------------------------------------------
# Calculation methods relevant to UAE
# ----------------------------------------------------------------------------
# The full method list is at https://aladhan.com/calculation-methods
# Method 8 is the published default for the Gulf Region.
# Method 16 is "Dubai (experimental)" and is the most aligned with what
# Dubai mosques actually announce.
CALCULATION_METHODS: Final[dict[int, str]] = {
    1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America (ISNA)",
    3: "Muslim World League",
    4: "Umm Al-Qura, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait",
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura, Singapore",
    12: "Union Organization Islamic de France",
    13: "Diyanet Isleri Baskanligi, Turkey",
    14: "Spiritual Administration of Muslims of Russia",
    15: "Moonsighting Committee Worldwide",
    16: "Dubai (experimental)",
    17: "Jabatan Kemajuan Islam Malaysia (JAKIM)",
    18: "Tunisia",
    19: "Algeria",
    20: "Kementerian Agama Republik Indonesia",
    21: "Morocco",
    22: "Comunidade Islamica de Lisboa",
    23: "Ministry of Awqaf, Islamic Affairs and Holy Places, Jordan",
}

# Sensible default for Dubai users.
DEFAULT_METHOD: Final[int] = 8

# Asr school: 0 = Shafi (default for UAE), 1 = Hanafi.
DEFAULT_SCHOOL: Final[int] = 0

# Default city/country for one-line "today's prayer times" use.
DEFAULT_CITY: Final[str] = "Dubai"
DEFAULT_COUNTRY: Final[str] = "United Arab Emirates"
