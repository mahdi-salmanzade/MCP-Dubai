"""
Al-Adhan API client.

Thin wrapper over the shared HttpClient that knows the Al-Adhan endpoint
shapes and parses responses into Pydantic models. No business logic,
no MCP concerns. Easy to unit test against respx mocks.
"""

from __future__ import annotations

from datetime import date

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.al_adhan import constants
from mcp_dubai.data.al_adhan.schemas import (
    CalendarDay,
    DateConversion,
    QiblaResponse,
    TimingsResponse,
)


class AlAdhanClient:
    """
    Async client for the Al-Adhan API.

    Args:
        method: Calculation method ID. Defaults to 8 (Gulf Region). 16 is
            "Dubai (experimental)" and matches what Dubai mosques announce.
        school: Asr school. 0 = Shafi (default for UAE), 1 = Hanafi.
    """

    def __init__(
        self,
        method: int = constants.DEFAULT_METHOD,
        school: int = constants.DEFAULT_SCHOOL,
    ) -> None:
        self.method = method
        self.school = school

    @staticmethod
    def _format_date_ddmmyyyy(value: date | None) -> str:
        """Al-Adhan path segments use DD-MM-YYYY."""
        return (value or date.today()).strftime("%d-%m-%Y")

    async def get_timings_by_city(
        self,
        city: str,
        country: str,
        on_date: date | None = None,
    ) -> TimingsResponse:
        """Prayer times for a city on a specific date."""
        params: dict[str, str | int] = {
            "city": city,
            "country": country,
            "method": self.method,
            "school": self.school,
            "date": self._format_date_ddmmyyyy(on_date),
        }
        async with HttpClient() as client:
            response = await client.get(constants.TIMINGS_BY_CITY, params=params)
        payload = response.json()
        return TimingsResponse.model_validate(payload["data"])

    async def get_timings_by_coords(
        self,
        latitude: float,
        longitude: float,
        on_date: date | None = None,
    ) -> TimingsResponse:
        """Prayer times for a lat/lon on a specific date."""
        params: dict[str, str | int | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "method": self.method,
            "school": self.school,
            "date": self._format_date_ddmmyyyy(on_date),
        }
        async with HttpClient() as client:
            response = await client.get(constants.TIMINGS, params=params)
        payload = response.json()
        return TimingsResponse.model_validate(payload["data"])

    async def get_calendar_by_city(
        self,
        city: str,
        country: str,
        month: int,
        year: int,
    ) -> list[CalendarDay]:
        """Prayer times calendar for a full month in a given city."""
        params: dict[str, str | int] = {
            "city": city,
            "country": country,
            "method": self.method,
            "school": self.school,
            "month": month,
            "year": year,
        }
        async with HttpClient() as client:
            response = await client.get(constants.CALENDAR_BY_CITY, params=params)
        payload = response.json()
        return [CalendarDay.model_validate(day) for day in payload["data"]]

    async def get_qibla(self, latitude: float, longitude: float) -> QiblaResponse:
        """Compass bearing from a lat/lon to Mecca."""
        url = f"{constants.QIBLA}/{latitude}/{longitude}"
        async with HttpClient() as client:
            response = await client.get(url)
        payload = response.json()
        return QiblaResponse.model_validate(payload["data"])

    async def hijri_to_gregorian(self, hijri_ddmmyyyy: str) -> DateConversion:
        """Convert a Hijri date string (DD-MM-YYYY) to a Gregorian date."""
        url = f"{constants.HIJRI_TO_GREGORIAN}/{hijri_ddmmyyyy}"
        async with HttpClient() as client:
            response = await client.get(url)
        payload = response.json()
        return DateConversion.model_validate(payload["data"])

    async def gregorian_to_hijri(self, gregorian_ddmmyyyy: str) -> DateConversion:
        """Convert a Gregorian date string (DD-MM-YYYY) to a Hijri date."""
        url = f"{constants.GREGORIAN_TO_HIJRI}/{gregorian_ddmmyyyy}"
        async with HttpClient() as client:
            response = await client.get(url)
        payload = response.json()
        return DateConversion.model_validate(payload["data"])
