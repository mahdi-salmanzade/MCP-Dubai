"""Tests for the aviation_weather feature."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.aviation_weather import constants, tools


def _metar_payload(icao: str) -> list[dict[str, object]]:
    return [
        {
            "icaoId": icao,
            "rawOb": f"{icao} 121200Z 27010KT 9999 NSC 32/12 Q1012",
            "obsTime": 1776346800,
            "temp": 32,
            "dewp": 12,
            "wdir": 270,
            "wspd": 10,
            "visib": 9999,
        }
    ]


def _taf_payload(icao: str) -> list[dict[str, object]]:
    return [
        {
            "icaoId": icao,
            "rawTAF": (f"TAF {icao} 121130Z 1212/1318 27010KT 9999 NSC BECMG 1217/1219 32010KT"),
            "issueTime": 1776344400,
        }
    ]


class TestWeatherUaeIcao:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_metar_and_taf(self) -> None:
        respx.get(constants.METAR_ENDPOINT).mock(
            return_value=Response(200, json=_metar_payload("OMDB"))
        )
        respx.get(constants.TAF_ENDPOINT).mock(
            return_value=Response(200, json=_taf_payload("OMDB"))
        )

        result = await tools.weather_uae_icao(icao="OMDB", include_taf=True)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["icao"] == "OMDB"
        assert data["airport"] == "Dubai International"
        metar = data["metar"]
        assert isinstance(metar, dict)
        assert metar["temp"] == 32
        taf = data["taf"]
        assert isinstance(taf, dict)
        assert "BECMG" in str(taf["rawTAF"])
        assert result["source"] == "aviationweather.gov"

    @pytest.mark.asyncio
    @respx.mock
    async def test_metar_only(self) -> None:
        metar_route = respx.get(constants.METAR_ENDPOINT).mock(
            return_value=Response(200, json=_metar_payload("OMSJ"))
        )
        taf_route = respx.get(constants.TAF_ENDPOINT).mock(return_value=Response(200, json=[]))

        result = await tools.weather_uae_icao(icao="OMSJ", include_taf=False)

        assert metar_route.called
        assert not taf_route.called
        data = result["data"]
        assert isinstance(data, dict)
        assert data["taf"] is None

    @pytest.mark.asyncio
    async def test_invalid_icao_returns_fail(self) -> None:
        result = await tools.weather_uae_icao(icao="EGLL")
        assert result["success"] is False
        assert "Unknown UAE ICAO code" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_204_empty_response(self) -> None:
        """HTTP 204 from aviationweather.gov returns no metar, not a crash."""
        respx.get(constants.METAR_ENDPOINT).mock(return_value=Response(204, content=b""))
        respx.get(constants.TAF_ENDPOINT).mock(return_value=Response(204, content=b""))

        result = await tools.weather_uae_icao(icao="OMDB", include_taf=True)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["icao"] == "OMDB"
        assert data["metar"] is None
        assert data["taf"] is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_empty_body_without_204(self) -> None:
        """A 200 with empty body is treated the same as 204."""
        respx.get(constants.METAR_ENDPOINT).mock(return_value=Response(200, content=b""))
        respx.get(constants.TAF_ENDPOINT).mock(return_value=Response(200, content=b""))

        result = await tools.weather_uae_icao(icao="OMDB", include_taf=True)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["metar"] is None
        assert data["taf"] is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_icao_normalization(self) -> None:
        respx.get(constants.METAR_ENDPOINT).mock(
            return_value=Response(200, json=_metar_payload("OMDB"))
        )
        respx.get(constants.TAF_ENDPOINT).mock(return_value=Response(200, json=[]))

        result = await tools.weather_uae_icao(icao="omdb")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["icao"] == "OMDB"


class TestWeatherUaeAll:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_all_airports(self) -> None:
        all_metars = [
            {"icaoId": code, "rawOb": f"{code} 121200Z"} for code in constants.UAE_AIRPORTS
        ]
        route = respx.get(constants.METAR_ENDPOINT).mock(
            return_value=Response(200, json=all_metars)
        )

        result = await tools.weather_uae_all()

        assert route.called
        ids_param = route.calls.last.request.url.params["ids"]
        for code in constants.UAE_AIRPORTS:
            assert code in ids_param

        data = result["data"]
        assert isinstance(data, dict)
        airports = data["airports"]
        assert isinstance(airports, list)
        assert len(airports) == len(constants.UAE_AIRPORTS)


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.aviation_weather import server as av_server

        importlib.reload(av_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("aviation_weather")}
        assert names == {"weather_uae_icao", "weather_uae_all"}

    def test_recommend_for_weather_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.aviation_weather import server as av_server

        importlib.reload(av_server)
        results = get_tool_discovery().recommend(
            "current weather at dubai airport metar wind", top_k=3
        )
        assert results
        assert results[0].name == "weather_uae_icao"
