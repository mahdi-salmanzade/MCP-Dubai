"""Aviation weather tool functions."""

from __future__ import annotations

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.aviation_weather import constants
from mcp_dubai.data.aviation_weather.client import AviationWeatherClient

_SOURCE = "aviationweather.gov"
_UPSTREAM = "aviation_weather"
_VERIFY_AT = "https://aviationweather.gov/data/api/"


def _fail(error: str) -> dict[str, object]:
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


def _normalize_icao(icao: str) -> str:
    return icao.strip().upper()


async def weather_uae_icao(
    icao: str,
    include_taf: bool = True,
) -> dict[str, object]:
    """
    Get METAR (current) and optionally TAF (forecast) for a UAE airport.
    """
    code = _normalize_icao(icao)
    if code not in constants.UAE_AIRPORTS:
        return _fail(
            f"Unknown UAE ICAO code: {code}. Valid codes: {sorted(constants.UAE_AIRPORTS.keys())}"
        )

    client = AviationWeatherClient()
    try:
        metar_records = await client.get_metar([code])
        taf_records: list[dict[str, object]] = []
        if include_taf:
            taf_records = await client.get_taf([code])
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    metar = metar_records[0] if metar_records else None
    taf = taf_records[0] if taf_records else None
    return _ok(
        {
            "icao": code,
            "airport": constants.UAE_AIRPORTS[code],
            "metar": metar,
            "taf": taf,
        }
    )


async def weather_uae_all(include_taf: bool = False) -> dict[str, object]:
    """Get METAR observations for all UAE airports in one call."""
    codes = list(constants.UAE_AIRPORTS.keys())
    client = AviationWeatherClient()

    try:
        metar_records = await client.get_metar(codes)
        taf_records: list[dict[str, object]] = []
        if include_taf:
            taf_records = await client.get_taf(codes)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_success(_UPSTREAM)
    metar_by_icao: dict[str, dict[str, object]] = {}
    for record in metar_records:
        station = str(record.get("icaoId") or record.get("station_id") or "").upper()
        if station:
            metar_by_icao[station] = dict(record)

    taf_by_icao: dict[str, dict[str, object]] = {}
    for record in taf_records:
        station = str(record.get("icaoId") or record.get("station_id") or "").upper()
        if station:
            taf_by_icao[station] = dict(record)

    return _ok(
        {
            "airports": [
                {
                    "icao": code,
                    "airport": constants.UAE_AIRPORTS[code],
                    "metar": metar_by_icao.get(code),
                    "taf": taf_by_icao.get(code) if include_taf else None,
                }
                for code in codes
            ],
        }
    )
