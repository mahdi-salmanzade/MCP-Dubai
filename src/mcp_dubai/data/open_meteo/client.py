"""open-meteo.com forecast client. Keyless JSON weather API."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.open_meteo import constants


class OpenMeteoClient:
    """Async client for the Open-Meteo forecast endpoint."""

    async def forecast(
        self,
        latitude: float,
        longitude: float,
        *,
        include_current: bool = True,
        include_daily: bool = True,
        forecast_days: int = 7,
    ) -> dict[str, Any]:
        """
        Fetch a forecast for a coordinate.

        Open-Meteo returns current conditions and daily arrays in a single
        response. Times are localised to Asia/Dubai via the `timezone` param.
        """
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": constants.TIMEZONE_NAME,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "forecast_days": forecast_days,
        }
        if include_current:
            params["current"] = ",".join(constants.CURRENT_VARIABLES)
        if include_daily:
            params["daily"] = ",".join(constants.DAILY_VARIABLES)

        async with HttpClient() as client:
            response = await client.get(constants.FORECAST_ENDPOINT, params=params)
        if response.status_code == 204 or not response.content:
            raise HttpClientError(f"Empty response from {constants.FORECAST_ENDPOINT}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise HttpClientError(f"Non-JSON body from {constants.FORECAST_ENDPOINT}") from exc
        if not isinstance(payload, dict):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.FORECAST_ENDPOINT}: expected an object"
            )
        if include_current and not isinstance(payload.get("current"), dict):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.FORECAST_ENDPOINT}: current is missing"
            )
        if include_daily and not isinstance(payload.get("daily"), dict):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.FORECAST_ENDPOINT}: daily is missing"
            )
        current = payload.get("current")
        if include_current and isinstance(current, dict):
            self._validate_weather_code(current.get("weather_code"))
        daily = payload.get("daily")
        if include_daily and isinstance(daily, dict) and "weather_code" in daily:
            codes = daily["weather_code"]
            if not isinstance(codes, list):
                raise HttpClientError("Open-Meteo daily weather_code must be a list")
            for code in codes:
                self._validate_weather_code(code)
        return dict(payload)

    @staticmethod
    def _validate_weather_code(code: object) -> None:
        """A missing code is allowed; malformed codes must not crash summaries."""
        if code is not None and (
            isinstance(code, bool)
            or not isinstance(code, int | float)
            or (isinstance(code, float) and not code.is_integer())
        ):
            raise HttpClientError("Open-Meteo weather_code must be an integer or null")
