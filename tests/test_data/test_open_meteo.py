"""Tests for the open_meteo feature."""

from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai.data.open_meteo import constants, tools
from mcp_dubai.data.open_meteo.client import OpenMeteoClient


def _forecast_payload(days: int = 1, with_current: bool = True) -> dict[str, object]:
    times = [f"2026-06-2{i}" for i in range(days)]
    payload: dict[str, object] = {
        "latitude": 25.2,
        "longitude": 55.27,
        "timezone": "Asia/Dubai",
        "daily": {
            "time": times,
            "weather_code": [0] * days,
            "temperature_2m_max": [42.1] * days,
            "temperature_2m_min": [30.4] * days,
            "apparent_temperature_max": [48.0] * days,
            "apparent_temperature_min": [33.0] * days,
            "sunrise": ["2026-06-20T05:30"] * days,
            "sunset": ["2026-06-20T19:10"] * days,
            "uv_index_max": [11.2] * days,
            "precipitation_sum": [0.0] * days,
            "precipitation_probability_max": [0] * days,
            "wind_speed_10m_max": [18.5] * days,
        },
    }
    if with_current:
        payload["current"] = {
            "time": "2026-06-20T14:00",
            "temperature_2m": 41.3,
            "relative_humidity_2m": 38,
            "apparent_temperature": 47.0,
            "is_day": 1,
            "precipitation": 0.0,
            "weather_code": 0,
            "cloud_cover": 5,
            "wind_speed_10m": 14.2,
            "wind_direction_10m": 315,
            "wind_gusts_10m": 22.0,
        }
    return payload


class TestOpenMeteoClient:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("code", [float("nan"), float("inf"), True, 1.5, "clear"])
    @pytest.mark.parametrize("block", ["current", "daily"])
    async def test_malformed_weather_code_returns_structured_failure(
        self, code: object, block: str
    ) -> None:
        payload = _forecast_payload()
        section = payload[block]
        assert isinstance(section, dict)
        section["weather_code"] = [code] if block == "daily" else code
        respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, content=json.dumps(payload))
        )

        result = await tools.uae_weather()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize(
        ("response", "message"),
        [
            pytest.param(Response(200, text="not json"), "Non-JSON body", id="non-json"),
            pytest.param(Response(200, json=[]), "expected an object", id="non-object"),
            pytest.param(
                Response(200, json={"current": {}}),
                "daily is missing",
                id="missing-daily",
            ),
        ],
    )
    async def test_rejects_malformed_upstream_payloads(
        self, response: Response, message: str
    ) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(return_value=response)

        with pytest.raises(HttpClientError, match=message):
            await OpenMeteoClient().forecast(25.2, 55.27)


class TestUaeWeather:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_current_and_today(self) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=1))
        )

        result = await tools.uae_weather(city="Dubai")

        assert result["success"] is True
        assert result["source"] == "api.open-meteo.com"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["city"] == "Dubai"
        current = data["current"]
        assert isinstance(current, dict)
        assert current["temperature_c"] == 41.3
        assert current["conditions"] == "Clear sky"
        assert current["is_day"] is True
        today = data["today"]
        assert isinstance(today, dict)
        assert today["temp_max_c"] == 42.1

    @pytest.mark.asyncio
    @respx.mock
    async def test_city_alias_resolves(self) -> None:
        route = respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=1))
        )

        result = await tools.uae_weather(city="abu dhabi")

        assert route.called
        params = route.calls.last.request.url.params
        assert params["latitude"] == "24.4539"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["city"] == "Abu Dhabi"

    @pytest.mark.asyncio
    async def test_unknown_city_returns_fail(self) -> None:
        result = await tools.uae_weather(city="London")
        assert result["success"] is False
        assert "Unknown UAE city" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_body_returns_structured_error(self) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(return_value=Response(200, content=b""))

        result = await tools.uae_weather(city="Dubai")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_current_block_returns_structured_error(self) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json={"timezone": "Asia/Dubai", "daily": {}})
        )

        result = await tools.uae_weather(city="Dubai")

        assert result["success"] is False
        assert isinstance(result["error"], dict)
        assert result["error"]["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_upstream_error_is_structured(self) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.uae_weather(city="Dubai")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestUaeWeatherForecast:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_multi_day(self) -> None:
        route = respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=5, with_current=False))
        )

        result = await tools.uae_weather_forecast(city="Dubai", days=5)

        assert route.called
        params = route.calls.last.request.url.params
        assert params["forecast_days"] == "5"
        data = result["data"]
        assert isinstance(data, dict)
        forecast = data["forecast"]
        assert isinstance(forecast, list)
        assert len(forecast) == 5
        assert forecast[0]["conditions"] == "Clear sky"

    @pytest.mark.asyncio
    @respx.mock
    async def test_days_clamped_to_max(self) -> None:
        route = respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=1, with_current=False))
        )

        await tools.uae_weather_forecast(city="Dubai", days=99)

        params = route.calls.last.request.url.params
        assert params["forecast_days"] == str(constants.MAX_FORECAST_DAYS)

    @pytest.mark.asyncio
    @respx.mock
    async def test_days_clamped_to_min(self) -> None:
        route = respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=1, with_current=False))
        )

        await tools.uae_weather_forecast(city="Dubai", days=0)

        params = route.calls.last.request.url.params
        assert params["forecast_days"] == "1"


class TestWeatherByCoords:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_current_and_forecast(self) -> None:
        respx.get(constants.FORECAST_ENDPOINT).mock(
            return_value=Response(200, json=_forecast_payload(days=3))
        )

        result = await tools.weather_by_coords(latitude=25.2, longitude=55.27, days=3)

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert isinstance(data["current"], dict)
        assert len(data["forecast"]) == 3

    @pytest.mark.asyncio
    async def test_invalid_latitude_returns_fail(self) -> None:
        result = await tools.weather_by_coords(latitude=200.0, longitude=55.0)
        assert result["success"] is False
        assert "latitude" in str(result["error"])

    @pytest.mark.asyncio
    async def test_invalid_longitude_returns_fail(self) -> None:
        result = await tools.weather_by_coords(latitude=25.0, longitude=999.0)
        assert result["success"] is False
        assert "longitude" in str(result["error"])


class TestListCities:
    @pytest.mark.asyncio
    async def test_lists_cities(self) -> None:
        result = await tools.list_uae_weather_cities()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == len(constants.UAE_CITIES)


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.open_meteo import server as om_server

        importlib.reload(om_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("open_meteo")}
        assert names == {
            "uae_weather",
            "uae_weather_forecast",
            "weather_by_coords",
            "list_uae_weather_cities",
        }

    def test_recommend_for_weather_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.open_meteo import server as om_server

        importlib.reload(om_server)
        results = get_tool_discovery().recommend(
            "what is the temperature in dubai today weather", top_k=5
        )
        assert results
        assert any(r.feature == "open_meteo" for r in results)
