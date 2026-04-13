"""
Curated KHDA Dubai private schools snapshot.

This is a hand-curated subset for v0. Replaced by full dataset when
`scripts/refresh_khda.py` is run against the live KHDA XLSX.

Each rating uses KHDA's published categories:
"Outstanding" > "Very Good" > "Good" > "Acceptable" > "Weak" > "Very Weak"

Knowledge date: 2026-04-12.
Source: https://web.khda.gov.ae/en/Resources/KHDA-data-statistics
"""

from __future__ import annotations

from typing import Final, TypedDict


class School(TypedDict):
    name: str
    area: str
    curriculum: str
    rating: str
    fees_min_aed: int
    fees_max_aed: int
    grades: str
    website: str


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
        "area": "Al Barsha South",
        "curriculum": "British / IB",
        "rating": "Very Good",
        "fees_min_aed": 56000,
        "fees_max_aed": 95000,
        "grades": "FS1 to Year 13",
        "website": "https://www.nordangliaeducation.com/dubai",
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
        "area": "Al Barsha",
        "curriculum": "American",
        "rating": "Outstanding",
        "fees_min_aed": 75000,
        "fees_max_aed": 98000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.asdubai.org",
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
        "area": "Umm Suqeim",
        "curriculum": "IB",
        "rating": "Very Good",
        "fees_min_aed": 50000,
        "fees_max_aed": 80000,
        "grades": "KG to Grade 12",
        "website": "https://www.rafflesis.com",
    },
    {
        "name": "Sharjah English School",
        "area": "Sharjah",
        "curriculum": "British",
        "rating": "Good",
        "fees_min_aed": 27000,
        "fees_max_aed": 55000,
        "grades": "FS1 to Year 13",
        "website": "https://www.sesmail.com",
    },
    {
        "name": "Al Salam Private School",
        "area": "Al Mizhar",
        "curriculum": "American",
        "rating": "Good",
        "fees_min_aed": 19000,
        "fees_max_aed": 38000,
        "grades": "KG1 to Grade 12",
        "website": "",
    },
    {
        "name": "Indian High School Dubai",
        "area": "Oud Metha",
        "curriculum": "Indian / CBSE",
        "rating": "Outstanding",
        "fees_min_aed": 7000,
        "fees_max_aed": 17000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.ihsdubai.org",
    },
    {
        "name": "Delhi Private School Dubai",
        "area": "Al Quoz",
        "curriculum": "Indian / CBSE",
        "rating": "Outstanding",
        "fees_min_aed": 9000,
        "fees_max_aed": 18000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.dpsdubai.com",
    },
    {
        "name": "GEMS Modern Academy",
        "area": "Nad Al Sheba",
        "curriculum": "Indian / CBSE / IB",
        "rating": "Outstanding",
        "fees_min_aed": 12000,
        "fees_max_aed": 47000,
        "grades": "KG1 to Grade 12",
        "website": "https://www.gemsmodernacademy.com",
    },
    {
        "name": "Lycee Francais International Georges Pompidou",
        "area": "Al Barsha South",
        "curriculum": "French",
        "rating": "Very Good",
        "fees_min_aed": 30000,
        "fees_max_aed": 60000,
        "grades": "PS to Terminale",
        "website": "https://www.lyceepompidou.com",
    },
    {
        "name": "Deutsche Internationale Schule Dubai",
        "area": "Al Sufouh",
        "curriculum": "German",
        "rating": "Very Good",
        "fees_min_aed": 35000,
        "fees_max_aed": 60000,
        "grades": "Kindergarten to Abitur",
        "website": "https://www.dsdubai.de",
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
