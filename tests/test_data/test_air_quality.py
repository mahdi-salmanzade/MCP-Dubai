"""Tests for the air_quality feature including the credential-missing path."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.air_quality import constants, tools


def _waqi_payload(station_name: str, aqi: int = 75) -> dict[str, object]:
    return {
        "status": "ok",
        "data": {
            "aqi": aqi,
            "idx": 12345,
            "city": {"name": station_name, "geo": [25.2048, 55.2708]},
            "iaqi": {
                "pm25": {"v": 30.0},
                "pm10": {"v": 45.0},
                "no2": {"v": 12.5},
                "o3": {"v": 25.0},
                "so2": {"v": 4.2},
                "co": {"v": 0.6},
                "t": {"v": 32.0},
                "h": {"v": 60.0},
            },
            "dominentpol": "pm10",
            "time": {"iso": "2026-04-12T12:00:00+04:00"},
        },
    }


def _waqi_error_payload() -> dict[str, object]:
    return {"status": "error", "data": "Invalid token"}


@pytest.fixture
def configured_waqi_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_DUBAI_WAQI_TOKEN", "test-token-abc")


@pytest.fixture
def no_waqi_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_DUBAI_WAQI_TOKEN", raising=False)


class TestAirQualityDubai:
    @pytest.mark.asyncio
    @respx.mock
    async def test_happy_path(self, configured_waqi_token: None) -> None:
        url = constants.FEED_BY_CITY.format(path="A470305")
        respx.get(url).mock(return_value=Response(200, json=_waqi_payload("Karama, Dubai")))

        result = await tools.air_quality_dubai(station="karama")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["aqi"] == 75
        assert data["category"] == "Moderate"
        pollutants = data["pollutants"]
        assert isinstance(pollutants, dict)
        assert pollutants["pm25"] == pytest.approx(30.0)
        assert "attribution" in data

    @pytest.mark.asyncio
    async def test_missing_token_returns_structured_error(self, no_waqi_token: None) -> None:
        result = await tools.air_quality_dubai(station="karama")
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "token_missing"
        assert "MCP_DUBAI_WAQI_TOKEN" in error["reason"]

    @pytest.mark.asyncio
    async def test_unknown_station_returns_error(self, configured_waqi_token: None) -> None:
        result = await tools.air_quality_dubai(station="not-a-station")
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, str)
        assert "Unknown Dubai station" in error

    @pytest.mark.asyncio
    @respx.mock
    async def test_waqi_error_response_is_structured(self, configured_waqi_token: None) -> None:
        url = constants.FEED_BY_CITY.format(path="A470305")
        respx.get(url).mock(return_value=Response(200, json=_waqi_error_payload()))

        result = await tools.air_quality_dubai(station="karama")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("bad_data", ["not-an-object", {}, 42])
    async def test_invalid_station_data_is_structured(
        self,
        configured_waqi_token: None,
        bad_data: object,
    ) -> None:
        url = constants.FEED_BY_CITY.format(path="A470305")
        respx.get(url).mock(return_value=Response(200, json={"status": "ok", "data": bad_data}))

        result = await tools.air_quality_dubai(station="karama")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_jebel_ali_uses_verified_feed_id(self, configured_waqi_token: None) -> None:
        route = respx.get(constants.FEED_BY_CITY.format(path="A470308")).mock(
            return_value=Response(200, json=_waqi_payload("Jebel Ali Village, Dubai"))
        )

        result = await tools.air_quality_dubai(station="jebel-ali-village")

        assert result["success"] is True
        assert route.called


class TestAirQualityByCoords:
    @pytest.mark.asyncio
    @respx.mock
    async def test_happy_path(self, configured_waqi_token: None) -> None:
        url = constants.FEED_BY_GEO.format(lat=25.2048, lon=55.2708)
        respx.get(url).mock(return_value=Response(200, json=_waqi_payload("Closest Station")))

        result = await tools.air_quality_by_coords(latitude=25.2048, longitude=55.2708)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_latitude(self, configured_waqi_token: None) -> None:
        result = await tools.air_quality_by_coords(latitude=91.0, longitude=55.0)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_no_token_path(self, no_waqi_token: None) -> None:
        result = await tools.air_quality_by_coords(latitude=25.0, longitude=55.0)
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "token_missing"


class TestAirQualityStations:
    @pytest.mark.asyncio
    async def test_lists_stations(self) -> None:
        result = await tools.air_quality_dubai_stations()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == len(constants.DUBAI_STATIONS)
        stations = data["stations"]
        assert isinstance(stations, list)
        assert {station["waqi_feed_id"] for station in stations} == {"A470305", "A470308"}
        assert data["verified_at"] == "2026-08-14"
        assert str(result["retrieved_at"]).endswith("Z")


class TestAqiCategory:
    def test_category_buckets(self) -> None:
        assert tools._aqi_category(25) == "Good"
        assert tools._aqi_category(75) == "Moderate"
        assert tools._aqi_category(125) == "Unhealthy for Sensitive Groups"
        assert tools._aqi_category(175) == "Unhealthy"
        assert tools._aqi_category(250) == "Very Unhealthy"
        assert tools._aqi_category(400) == "Hazardous"


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.air_quality import server as aq_server

        importlib.reload(aq_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("air_quality")}
        assert names == {
            "air_quality_dubai",
            "air_quality_by_coords",
            "air_quality_dubai_stations",
        }
