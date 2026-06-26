"""Open-Meteo tool functions (keyless human weather and forecast)."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.open_meteo import constants
from mcp_dubai.data.open_meteo.client import OpenMeteoClient

_SOURCE = "api.open-meteo.com"
_UPSTREAM = "open_meteo"
_VERIFY_AT = "https://open-meteo.com/"
_ATTRIBUTION = "Weather data by Open-Meteo.com (CC BY 4.0), https://open-meteo.com."


def _fail(error: str | dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _resolve_city(city: str) -> tuple[str, dict[str, object]] | None:
    """Resolve a free-text UAE city name to (slug, city_record) or None."""
    raw = city.strip().lower()
    slug = raw.replace(" ", "_").replace("-", "_")
    if slug in constants.UAE_CITIES:
        return slug, constants.UAE_CITIES[slug]
    if raw in constants.CITY_ALIASES:
        resolved = constants.CITY_ALIASES[raw]
        return resolved, constants.UAE_CITIES[resolved]
    if slug in constants.CITY_ALIASES:
        resolved = constants.CITY_ALIASES[slug]
        return resolved, constants.UAE_CITIES[resolved]
    return None


def _safe_index(values: object, index: int) -> object:
    if isinstance(values, list) and 0 <= index < len(values):
        return values[index]
    return None


def _summarize_current(payload: dict[str, Any]) -> dict[str, object] | None:
    current = payload.get("current")
    if not isinstance(current, dict):
        return None
    code = current.get("weather_code")
    is_day = current.get("is_day")
    return {
        "time": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "cloud_cover_pct": current.get("cloud_cover"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_gust_kmh": current.get("wind_gusts_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "is_day": bool(is_day) if is_day is not None else None,
        "weather_code": code,
        "conditions": constants.describe_weather_code(code),
    }


def _summarize_daily(payload: dict[str, Any]) -> list[dict[str, object]]:
    daily = payload.get("daily")
    if not isinstance(daily, dict):
        return []
    times = daily.get("time")
    if not isinstance(times, list):
        return []
    out: list[dict[str, object]] = []
    for i, day in enumerate(times):
        code = _safe_index(daily.get("weather_code"), i)
        out.append(
            {
                "date": day,
                "weather_code": code,
                "conditions": constants.describe_weather_code(code),
                "temp_max_c": _safe_index(daily.get("temperature_2m_max"), i),
                "temp_min_c": _safe_index(daily.get("temperature_2m_min"), i),
                "feels_like_max_c": _safe_index(daily.get("apparent_temperature_max"), i),
                "feels_like_min_c": _safe_index(daily.get("apparent_temperature_min"), i),
                "sunrise": _safe_index(daily.get("sunrise"), i),
                "sunset": _safe_index(daily.get("sunset"), i),
                "uv_index_max": _safe_index(daily.get("uv_index_max"), i),
                "precipitation_sum_mm": _safe_index(daily.get("precipitation_sum"), i),
                "precipitation_probability_max_pct": _safe_index(
                    daily.get("precipitation_probability_max"), i
                ),
                "wind_speed_max_kmh": _safe_index(daily.get("wind_speed_10m_max"), i),
            }
        )
    return out


def _clamp_days(days: int) -> int:
    if days < 1:
        return 1
    if days > constants.MAX_FORECAST_DAYS:
        return constants.MAX_FORECAST_DAYS
    return days


async def uae_weather(city: str = "Dubai") -> dict[str, object]:
    """
    Get current weather conditions plus today's high and low for a UAE city.

    Args:
        city: A UAE city name. Supported: Dubai, Abu Dhabi, Sharjah, Ajman,
            Ras Al Khaimah, Fujairah, Umm Al Quwain, Al Ain.
    """
    resolved = _resolve_city(city)
    if resolved is None:
        return _fail(
            f"Unknown UAE city: {city!r}. Valid: "
            f"{sorted(str(c['name']) for c in constants.UAE_CITIES.values())}"
        )
    slug, record = resolved
    latitude = float(record["latitude"])  # type: ignore[arg-type]
    longitude = float(record["longitude"])  # type: ignore[arg-type]

    client = OpenMeteoClient()
    try:
        payload = await client.forecast(
            latitude, longitude, include_current=True, include_daily=True, forecast_days=1
        )
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    daily = _summarize_daily(payload)
    return _ok(
        {
            "city": record["name"],
            "city_slug": slug,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": payload.get("timezone", constants.TIMEZONE_NAME),
            "current": _summarize_current(payload),
            "today": daily[0] if daily else None,
            "attribution": _ATTRIBUTION,
        }
    )


async def uae_weather_forecast(city: str = "Dubai", days: int = 7) -> dict[str, object]:
    """
    Get a multi-day daily weather forecast for a UAE city.

    Args:
        city: A UAE city name (see `uae_weather`).
        days: Number of forecast days, 1 to 16. Values are clamped to range.
    """
    resolved = _resolve_city(city)
    if resolved is None:
        return _fail(
            f"Unknown UAE city: {city!r}. Valid: "
            f"{sorted(str(c['name']) for c in constants.UAE_CITIES.values())}"
        )
    slug, record = resolved
    latitude = float(record["latitude"])  # type: ignore[arg-type]
    longitude = float(record["longitude"])  # type: ignore[arg-type]
    horizon = _clamp_days(days)

    client = OpenMeteoClient()
    try:
        payload = await client.forecast(
            latitude, longitude, include_current=False, include_daily=True, forecast_days=horizon
        )
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    forecast = _summarize_daily(payload)
    return _ok(
        {
            "city": record["name"],
            "city_slug": slug,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": payload.get("timezone", constants.TIMEZONE_NAME),
            "days": len(forecast),
            "forecast": forecast,
            "attribution": _ATTRIBUTION,
        }
    )


async def weather_by_coords(
    latitude: float,
    longitude: float,
    days: int = 3,
) -> dict[str, object]:
    """
    Get current weather plus a short forecast for any latitude/longitude.

    Args:
        latitude: Latitude, -90 to 90.
        longitude: Longitude, -180 to 180.
        days: Number of forecast days, 1 to 16. Values are clamped to range.
    """
    if not -90 <= latitude <= 90:
        return _fail(f"latitude must be -90 to 90, got {latitude}")
    if not -180 <= longitude <= 180:
        return _fail(f"longitude must be -180 to 180, got {longitude}")
    horizon = _clamp_days(days)

    client = OpenMeteoClient()
    try:
        payload = await client.forecast(
            latitude, longitude, include_current=True, include_daily=True, forecast_days=horizon
        )
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(
        {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": payload.get("timezone", constants.TIMEZONE_NAME),
            "current": _summarize_current(payload),
            "forecast": _summarize_daily(payload),
            "attribution": _ATTRIBUTION,
        }
    )


async def list_uae_weather_cities() -> dict[str, object]:
    """List the UAE cities supported by the Open-Meteo weather tools."""
    return _ok(
        {
            "count": len(constants.UAE_CITIES),
            "cities": [
                {
                    "slug": slug,
                    "name": record["name"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"],
                }
                for slug, record in constants.UAE_CITIES.items()
            ],
        }
    )
