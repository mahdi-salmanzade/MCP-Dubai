"""
Pure Al-Adhan tool functions.

These are the actual implementations that the FastMCP server in `server.py`
exposes. Splitting them out keeps `server.py` thin and lets unit tests
exercise the logic without going through FastMCP's wrapping layer.

All functions return envelope dicts via ToolResponse so they serialise
cleanly to JSON for the MCP wire format.
"""

from __future__ import annotations

from datetime import date

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.al_adhan import constants
from mcp_dubai.data.al_adhan.client import AlAdhanClient

_SOURCE = "api.aladhan.com"
_UPSTREAM = "al_adhan"
_VERIFY_AT = "https://aladhan.com/prayer-times-api"


def _fail(error: str) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: object) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())  # type: ignore[arg-type]
        .model_dump()
    )


def _parse_iso_date(value: str | None) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(value)


async def prayer_times_for(
    city: str | None = None,
    country: str = constants.DEFAULT_COUNTRY,
    latitude: float | None = None,
    longitude: float | None = None,
    date_str: str | None = None,
    method: int = constants.DEFAULT_METHOD,
    school: int = constants.DEFAULT_SCHOOL,
) -> dict[str, object]:
    """
    Get prayer times for a UAE city or arbitrary coordinates.

    Pass either `city` (e.g., "Dubai") OR `latitude` plus `longitude`.
    """
    if latitude is None and longitude is None and not city:
        return _fail("prayer_times_for: provide either `city` or both `latitude` and `longitude`")
    if (latitude is None) != (longitude is None):
        return _fail("prayer_times_for: latitude and longitude must be provided together")

    try:
        on_date = _parse_iso_date(date_str)
    except ValueError as exc:
        return _fail(f"Invalid ISO date: {date_str!r} ({exc})")

    client = AlAdhanClient(method=method, school=school)

    try:
        if latitude is not None and longitude is not None:
            result = await client.get_timings_by_coords(latitude, longitude, on_date)
        else:
            assert city is not None  # narrowed above
            result = await client.get_timings_by_city(city, country, on_date)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(result.model_dump())


async def prayer_times_calendar(
    city: str,
    month: int,
    year: int,
    country: str = constants.DEFAULT_COUNTRY,
    method: int = constants.DEFAULT_METHOD,
    school: int = constants.DEFAULT_SCHOOL,
) -> dict[str, object]:
    """Get prayer times for an entire month in one call."""
    if not 1 <= month <= 12:
        return _fail(f"prayer_times_calendar: month must be 1 to 12, got {month}")
    if year < 1 or year > 9999:
        return _fail(f"prayer_times_calendar: year must be 1 to 9999, got {year}")

    client = AlAdhanClient(method=method, school=school)
    try:
        days = await client.get_calendar_by_city(city, country, month, year)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok({"days": [day.model_dump() for day in days], "count": len(days)})


async def qibla_direction(latitude: float, longitude: float) -> dict[str, object]:
    """Get the compass bearing to Mecca for a given location."""
    if not -90 <= latitude <= 90:
        return _fail(f"qibla_direction: latitude must be -90 to 90, got {latitude}")
    if not -180 <= longitude <= 180:
        return _fail(f"qibla_direction: longitude must be -180 to 180, got {longitude}")

    client = AlAdhanClient()
    try:
        result = await client.get_qibla(latitude, longitude)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(result.model_dump())


async def hijri_to_gregorian(day: int, month: int, year: int) -> dict[str, object]:
    """Convert a Hijri (Islamic) date to a Gregorian date."""
    if not 1 <= day <= 30:
        return _fail(f"hijri_to_gregorian: day must be 1 to 30, got {day}")
    if not 1 <= month <= 12:
        return _fail(f"hijri_to_gregorian: month must be 1 to 12, got {month}")

    client = AlAdhanClient()
    hijri_str = f"{day:02d}-{month:02d}-{year:04d}"
    try:
        result = await client.hijri_to_gregorian(hijri_str)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(result.model_dump())


async def gregorian_to_hijri(day: int, month: int, year: int) -> dict[str, object]:
    """Convert a Gregorian date to a Hijri (Islamic) date."""
    if not 1 <= day <= 31:
        return _fail(f"gregorian_to_hijri: day must be 1 to 31, got {day}")
    if not 1 <= month <= 12:
        return _fail(f"gregorian_to_hijri: month must be 1 to 12, got {month}")

    client = AlAdhanClient()
    gregorian_str = f"{day:02d}-{month:02d}-{year:04d}"
    try:
        result = await client.gregorian_to_hijri(gregorian_str)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(result.model_dump())
