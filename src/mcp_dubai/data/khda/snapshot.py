"""
Curated KHDA Dubai private schools snapshot.

Hand-curated subset of well-known Dubai schools for fast lookup. Expand
coverage by appending to SCHOOLS from the live KHDA XLSX at the source
URL below (contributions welcome).

Each rating uses KHDA's published categories:
"Outstanding" > "Very Good" > "Good" > "Acceptable" > "Weak" > "Very Weak"

Full snapshot date: 2026-04-14.
Targeted correction: 2026-09-05 (selected ratings, curricula, locations and
grades checked against KHDA directory records; see each record's verified_fields).
Fees and untouched fields retain the April snapshot date. This is not a full refresh.
Source: https://web.khda.gov.ae/en/Resources/KHDA-data-statistics
"""

from __future__ import annotations

from typing import Final, NotRequired, TypedDict

SNAPSHOT_DATE: Final[str] = "2026-04-14"
TARGETED_CORRECTION_DATE: Final[str] = "2026-09-05"


class School(TypedDict):
    name: str
    area: str
    curriculum: str
    rating: str
    fees_min_aed: int
    fees_max_aed: int
    grades: str
    website: str
    source_url: NotRequired[str]
    verified_as_of: NotRequired[str]
    verified_fields: NotRequired[list[str]]
    rating_year: NotRequired[str]


SCHOOLS: Final[list[School]] = [
    {
        "name": "GEMS Wellington International School",
        "area": "Al Sufouh",
        "curriculum": "British / IB",
        "rating": "Outstanding",
        "fees_min_aed": 47000,
        "fees_max_aed": 89000,
        "grades": "FS1 to Year 13",
        "website": "https://www.gemswellingtoninternational-dubai.com",
    },
    {
        "name": "Jumeirah College",
        "area": "Jumeirah",
        "curriculum": "British",
        "rating": "Outstanding",
        "fees_min_aed": 75000,
        "fees_max_aed": 92000,
        "grades": "Year 7 to Year 13",
        "website": "https://www.jumeirahcollegedubai.com",
    },
    {
        "name": "Dubai College",
        "area": "Al Sufouh",
        "curriculum": "British",
        "rating": "Outstanding",
        "fees_min_aed": 79000,
        "fees_max_aed": 96000,
        "grades": "Year 7 to Year 13",
        "website": "https://www.dubaicollege.org",
    },
    {
        "name": "Dubai English Speaking College",
        "area": "Academic City",
        "curriculum": "British",
        "rating": "Outstanding",
        "fees_min_aed": 65000,
        "fees_max_aed": 86000,
        "grades": "Year 7 to Year 13",
        "website": "https://www.descdubai.com",
    },
    {
        "name": "Repton School Dubai",
        "area": "Nad Al Sheba",
        "curriculum": "British",
        "rating": "Outstanding",
        "fees_min_aed": 59000,
        "fees_max_aed": 96000,
        "grades": "FS1 to Year 13",
        "website": "https://www.reptondubai.org",
    },
    {
        "name": "Nord Anglia International School Dubai",
        "area": "Al Barsha Second",
        "curriculum": "British / IB",
        "rating": "Outstanding",
        "fees_min_aed": 56000,
        "fees_max_aed": 95000,
        "grades": "FS1 to Year 13",
        "website": "https://www.nordangliaeducation.com/dubai",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools/School-Details?CenterID=2222&Id=4441",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["rating", "area"],
        "rating_year": "2023-2024",
    },
    {
        "name": "Dubai American Academy",
        "area": "Al Barsha",
        "curriculum": "American / IB",
        "rating": "Outstanding",
        "fees_min_aed": 64000,
        "fees_max_aed": 95000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.gemsdaa.net",
    },
    {
        "name": "American School of Dubai",
        "area": "Al Barsha Second",
        "curriculum": "American",
        "rating": "Good",
        "fees_min_aed": 75000,
        "fees_max_aed": 98000,
        "grades": "Pre primary to Grade 12",
        "website": "https://www.asdubai.org",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools/School-Details?CenterID=34&Id=201",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["rating", "area", "grades"],
        "rating_year": "2023-2024",
    },
    {
        "name": "Dubai International Academy Emirates Hills",
        "area": "Emirates Hills",
        "curriculum": "IB",
        "rating": "Outstanding",
        "fees_min_aed": 60000,
        "fees_max_aed": 95000,
        "grades": "KG to Grade 12",
        "website": "https://www.diadubai.com",
    },
    {
        "name": "Raffles International School",
        "area": "Umm Suqeim Third",
        "curriculum": "British",
        "rating": "Very Good",
        "fees_min_aed": 50000,
        "fees_max_aed": 80000,
        "grades": "FS1 to Year 13",
        "website": "https://www.rafflesis.com",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["curriculum", "area", "grades"],
    },
    {
        "name": "Al Salam Private School",
        "area": "Al Nahda Second",
        "curriculum": "British",
        "rating": "Good",
        "fees_min_aed": 19000,
        "fees_max_aed": 38000,
        "grades": "FS1 to Year 11",
        "website": "",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["curriculum", "area", "grades"],
    },
    {
        "name": "Indian High School Dubai",
        "area": "Oud Metha",
        "curriculum": "Indian / CBSE",
        "rating": "Very Good",
        "fees_min_aed": 7000,
        "fees_max_aed": 17000,
        "grades": "Grade 5 to Grade 12",
        "website": "https://www.ihsdubai.org",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["rating", "grades"],
        "rating_year": "2023-2024",
    },
    {
        "name": "Delhi Private School Dubai",
        "area": "Jabal Ali First",
        "curriculum": "Indian / CBSE",
        "rating": "Very Good",
        "fees_min_aed": 9000,
        "fees_max_aed": 18000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.dpsdubai.com",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["rating"],
        "rating_year": "2023-2024",
    },
    {
        "name": "GEMS Modern Academy",
        "area": "Nad Al Sheba",
        "curriculum": "Indian / ICSE / IB",
        "rating": "Outstanding",
        "fees_min_aed": 12000,
        "fees_max_aed": 47000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.gemsmodernacademy-dubai.com",
        "source_url": "https://www.gemsmodernacademy-dubai.com/curriculum/",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["curriculum", "website"],
    },
    {
        "name": "Lycee Francais International Georges Pompidou (Dubai Branch)",
        "area": "Al Rowaiyah First",
        "curriculum": "French",
        "rating": "Very Good",
        "fees_min_aed": 30000,
        "fees_max_aed": 60000,
        "grades": "Grade 1 to Grade 12",
        "website": "https://lfigp.org",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools/School-Details?CenterID=137&Id=309",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["name", "area", "grades", "website"],
    },
    {
        "name": "Deutsche Internationale Schule Dubai",
        "area": "Academic City",
        "curriculum": "German",
        "rating": "Very Good",
        "fees_min_aed": 35000,
        "fees_max_aed": 60000,
        "grades": "Kindergarten to Abitur",
        "website": "https://www.dsdubai.de",
        "source_url": "https://web.khda.gov.ae/en/Education-Directory/Schools",
        "verified_as_of": "2026-09-05",
        "verified_fields": ["area"],
    },
]


VALID_RATINGS: Final[set[str]] = {
    "Outstanding",
    "Very Good",
    "Good",
    "Acceptable",
    "Weak",
    "Very Weak",
}
