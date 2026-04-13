"""Aviation weather tool functions."""

from __future__ import annotations

from mcp_dubai.data.aviation_weather import constants
from mcp_dubai.data.aviation_weather.client import AviationWeatherClient


def _normalize_icao(icao: str) -> str:
    return icao.strip().upper()


async def weather_uae_icao(
    icao: str,
    include_taf: bool = True,
) -> dict[str, object]:
    """
    Get METAR (current) and optionally TAF (forecast) for a UAE airport.

    Args:
        icao: 4-letter ICAO code (OMDB, OMDW, OMSJ, OMAA, OMAL, OMRK).
        include_taf: If True, also fetch the TAF.
    """
    code = _normalize_icao(icao)
    if code not in constants.UAE_AIRPORTS:
        raise ValueError(
            f"Unknown UAE ICAO code: {code}. Valid codes: {sorted(constants.UAE_AIRPORTS.keys())}"
        )

    client = AviationWeatherClient()
    metar_records = await client.get_metar([code])
    metar = metar_records[0] if metar_records else None

    taf = None
    if include_taf:
        taf_records = await client.get_taf([code])
        taf = taf_records[0] if taf_records else None

    return {
        "icao": code,
        "airport": constants.UAE_AIRPORTS[code],
        "metar": metar,
        "taf": taf,
    }


async def weather_uae_all(include_taf: bool = False) -> dict[str, object]:
    """
    Get METAR observations for all UAE airports in one call.

    Args:
        include_taf: If True, also fetch TAF forecasts.
    """
    codes = list(constants.UAE_AIRPORTS.keys())
    client = AviationWeatherClient()

    metar_records = await client.get_metar(codes)
    metar_by_icao: dict[str, dict[str, object]] = {}
    for record in metar_records:
        station = str(record.get("icaoId") or record.get("station_id") or "").upper()
        if station:
            metar_by_icao[station] = dict(record)

    taf_by_icao: dict[str, dict[str, object]] = {}
    if include_taf:
        taf_records = await client.get_taf(codes)
        for record in taf_records:
            station = str(record.get("icaoId") or record.get("station_id") or "").upper()
            if station:
                taf_by_icao[station] = dict(record)

    return {
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
