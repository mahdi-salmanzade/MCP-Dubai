"""
Pydantic v2 models for Al-Adhan API responses.

The upstream API returns capitalized field names (Fajr, Dhuhr, Maghrib).
We use Pydantic field aliases to expose snake_case to Python callers while
parsing the upstream shape directly.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PrayerTimes(BaseModel):
    """The five daily prayers plus related boundary times for one day."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    fajr: str = Field(alias="Fajr", description="Fajr prayer time, HH:MM in local TZ.")
    sunrise: str = Field(alias="Sunrise")
    dhuhr: str = Field(alias="Dhuhr", description="Dhuhr prayer time.")
    asr: str = Field(alias="Asr", description="Asr prayer time.")
    sunset: str = Field(alias="Sunset")
    maghrib: str = Field(alias="Maghrib", description="Maghrib prayer time.")
    isha: str = Field(alias="Isha", description="Isha prayer time.")
    imsak: str = Field(alias="Imsak", description="Imsak (start of fasting).")
    midnight: str = Field(alias="Midnight", description="Islamic midnight.")
    firstthird: str = Field(default="", alias="Firstthird")
    lastthird: str = Field(default="", alias="Lastthird")


class HijriDate(BaseModel):
    """Hijri (Islamic) calendar date as returned by Al-Adhan."""

    model_config = ConfigDict(extra="ignore")

    date: str
    day: str
    month: dict[str, Any]
    year: str
    designation: dict[str, str]
    weekday: dict[str, str] | None = None
    holidays: list[str] = Field(default_factory=list)


class GregorianDate(BaseModel):
    """Gregorian calendar date as returned by Al-Adhan."""

    model_config = ConfigDict(extra="ignore")

    date: str
    day: str
    month: dict[str, Any]
    year: str
    designation: dict[str, str]
    weekday: dict[str, str] | None = None


class DateInfo(BaseModel):
    """Combined Hijri and Gregorian date envelope."""

    model_config = ConfigDict(extra="ignore")

    readable: str | None = None
    timestamp: str | None = None
    hijri: HijriDate
    gregorian: GregorianDate


class TimingsResponse(BaseModel):
    """Top-level `data` payload of /timings, /timingsByCity, /timingsByAddress."""

    model_config = ConfigDict(extra="ignore")

    timings: PrayerTimes
    date: DateInfo
    meta: dict[str, Any] = Field(default_factory=dict)


class CalendarDay(BaseModel):
    """Single day in a /calendar response."""

    model_config = ConfigDict(extra="ignore")

    timings: PrayerTimes
    date: DateInfo


class QiblaResponse(BaseModel):
    """Response from /qibla/{lat}/{lon}."""

    model_config = ConfigDict(extra="ignore")

    latitude: float
    longitude: float
    direction: float = Field(description="Compass bearing to Mecca in degrees (0-360).")


class DateConversion(BaseModel):
    """Response shape for /gToH and /hToG date conversion endpoints."""

    model_config = ConfigDict(extra="ignore")

    hijri: HijriDate
    gregorian: GregorianDate
