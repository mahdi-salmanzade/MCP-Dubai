"""
Al-Adhan API client.

Thin wrapper over the shared HttpClient that knows the Al-Adhan endpoint
shapes and parses responses into Pydantic models. No business logic,
no MCP concerns. Easy to unit test against respx mocks.
"""

from __future__ import annotations

from datetime import date
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from mcp_dubai._shared.constants import uae_today
from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.al_adhan import constants
from mcp_dubai.data.al_adhan.schemas import (
    CalendarDay,
    DateConversion,
    QiblaResponse,
    TimingsResponse,
)

_ModelT = TypeVar("_ModelT", bound=BaseModel)


def _response_data(response: httpx.Response, endpoint: str) -> Any:
    """Decode the required Al-Adhan response envelope."""
    if response.status_code == 204 or not response.content:
        raise HttpClientError(f"Empty response from {endpoint}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise HttpClientError(f"Non-JSON body from {endpoint}") from exc
    if not isinstance(payload, dict) or "data" not in payload:
        raise HttpClientError(f"Invalid JSON shape from {endpoint}: missing data")
    return payload["data"]


def _validate(model: type[_ModelT], data: Any, endpoint: str) -> _ModelT:
    """Convert Pydantic validation failures into the shared upstream error type."""
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise HttpClientError(f"Invalid JSON shape from {endpoint}") from exc


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
        """Al-Adhan path segments use DD-MM-YYYY. Defaults to the Dubai date."""
        return (value or uae_today()).strftime("%d-%m-%Y")

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
        return _validate(
            TimingsResponse,
            _response_data(response, constants.TIMINGS_BY_CITY),
            constants.TIMINGS_BY_CITY,
        )

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
        return _validate(
            TimingsResponse,
            _response_data(response, constants.TIMINGS),
            constants.TIMINGS,
        )

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
        data = _response_data(response, constants.CALENDAR_BY_CITY)
        if not isinstance(data, list):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.CALENDAR_BY_CITY}: data is not a list"
            )
        return [_validate(CalendarDay, day, constants.CALENDAR_BY_CITY) for day in data]

    async def get_qibla(self, latitude: float, longitude: float) -> QiblaResponse:
        """Compass bearing from a lat/lon to Mecca."""
        url = f"{constants.QIBLA}/{latitude}/{longitude}"
        async with HttpClient() as client:
            response = await client.get(url)
        return _validate(QiblaResponse, _response_data(response, url), url)

    async def hijri_to_gregorian(self, hijri_ddmmyyyy: str) -> DateConversion:
        """Convert a Hijri date string (DD-MM-YYYY) to a Gregorian date."""
        url = f"{constants.HIJRI_TO_GREGORIAN}/{hijri_ddmmyyyy}"
        async with HttpClient() as client:
            response = await client.get(url)
        return _validate(DateConversion, _response_data(response, url), url)

    async def gregorian_to_hijri(self, gregorian_ddmmyyyy: str) -> DateConversion:
        """Convert a Gregorian date string (DD-MM-YYYY) to a Hijri date."""
        url = f"{constants.GREGORIAN_TO_HIJRI}/{gregorian_ddmmyyyy}"
        async with HttpClient() as client:
            response = await client.get(url)
        return _validate(DateConversion, _response_data(response, url), url)
