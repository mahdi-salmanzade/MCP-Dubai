"""Tests for the osm_overpass feature."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.osm_overpass import constants, tools
from mcp_dubai.data.osm_overpass.client import OverpassClient


def _overpass_payload() -> dict[str, object]:
    return {
        "version": 0.6,
        "generator": "Overpass API",
        "elements": [
            {
                "type": "node",
                "id": 12345,
                "lat": 25.2048,
                "lon": 55.2708,
                "tags": {
                    "amenity": "restaurant",
                    "name": "Al Mallah",
                    "name:ar": "المله",
                    "cuisine": "lebanese",
                    "phone": "+971-4-123-4567",
                },
            },
            {
                "type": "node",
                "id": 23456,
                "lat": 25.205,
                "lon": 55.272,
                "tags": {
                    "amenity": "restaurant",
                    "name": "Bu Qtair",
                    "cuisine": "seafood",
                },
            },
        ],
    }


class TestOverpassClient:
    def test_query_builder_includes_tag_and_radius(self) -> None:
        query = OverpassClient.build_query(
            tag_selectors=["amenity=restaurant"],
            latitude=25.2048,
            longitude=55.2708,
            radius_meters=500,
        )
        assert "[amenity=restaurant]" in query
        assert "around:500,25.2048,55.2708" in query
        assert "out body" in query

    def test_query_builder_chains_multiple_tags(self) -> None:
        query = OverpassClient.build_query(
            tag_selectors=["amenity=place_of_worship", "religion=muslim"],
            latitude=25.2,
            longitude=55.3,
            radius_meters=1000,
        )
        assert "[amenity=place_of_worship][religion=muslim]" in query


class TestOsmSearchPoi:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_formatted_pois(self) -> None:
        route = respx.post(constants.OVERPASS_ENDPOINT).mock(
            return_value=Response(200, json=_overpass_payload())
        )

        result = await tools.osm_search_poi(
            latitude=25.2048,
            longitude=55.2708,
            category="restaurant",
            radius_meters=500,
        )

        assert route.called
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 2
        results = data["results"]
        assert isinstance(results, list)
        assert results[0]["name"] == "Al Mallah"
        assert results[0]["name_ar"] == "المله"
        assert result["source"] == "overpass-api.de"

    @pytest.mark.asyncio
    async def test_unknown_category_returns_fail(self) -> None:
        result = await tools.osm_search_poi(latitude=25.0, longitude=55.0, category="laundromat")
        assert result["success"] is False
        assert "Unknown category" in str(result["error"])

    @pytest.mark.asyncio
    async def test_invalid_latitude_returns_fail(self) -> None:
        result = await tools.osm_search_poi(latitude=91.0, longitude=55.0, category="restaurant")
        assert result["success"] is False
        assert "latitude" in str(result["error"])

    @pytest.mark.asyncio
    async def test_radius_out_of_range_returns_fail(self) -> None:
        result = await tools.osm_search_poi(
            latitude=25.0,
            longitude=55.0,
            category="restaurant",
            radius_meters=50000,
        )
        assert result["success"] is False
        assert "radius_meters" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_limit_caps_results(self) -> None:
        respx.post(constants.OVERPASS_ENDPOINT).mock(
            return_value=Response(200, json=_overpass_payload())
        )
        result = await tools.osm_search_poi(
            latitude=25.0,
            longitude=55.0,
            category="restaurant",
            limit=1,
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 1


class TestOsmListCategories:
    @pytest.mark.asyncio
    async def test_returns_curated_categories(self) -> None:
        result = await tools.osm_list_categories()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == len(constants.COMMON_POI_TAGS)
        cats = data["categories"]
        assert isinstance(cats, list)
        assert "restaurant" in cats
        assert "mosque" in cats


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.osm_overpass import server as osm_server

        importlib.reload(osm_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("osm_overpass")}
        assert names == {"osm_search_poi", "osm_list_categories"}
