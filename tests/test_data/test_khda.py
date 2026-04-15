"""Tests for the KHDA school search feature (no network)."""

from __future__ import annotations

import pytest

from mcp_dubai.data.khda import tools
from mcp_dubai.data.khda.snapshot import SCHOOLS


def _data(result: dict[str, object]) -> dict[str, object]:
    data = result["data"]
    assert isinstance(data, dict)
    return data


class TestKhdaSearchSchool:
    @pytest.mark.asyncio
    async def test_no_filters_returns_all_within_limit(self) -> None:
        result = await tools.khda_search_school()
        assert result["success"] is True
        data = _data(result)
        assert data["count"] == len(SCHOOLS)
        schools = data["schools"]
        assert isinstance(schools, list)
        assert len(schools) == len(SCHOOLS)
        assert result["source"] == "KHDA curated snapshot"

    @pytest.mark.asyncio
    async def test_filter_by_name(self) -> None:
        result = await tools.khda_search_school(name="Wellington")
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        assert any("Wellington" in s["name"] for s in schools)

    @pytest.mark.asyncio
    async def test_filter_by_area(self) -> None:
        result = await tools.khda_search_school(area="Jumeirah")
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert "jumeirah" in school["area"].lower()

    @pytest.mark.asyncio
    async def test_filter_by_curriculum(self) -> None:
        result = await tools.khda_search_school(curriculum="British")
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        assert len(schools) > 0
        for school in schools:
            assert "british" in school["curriculum"].lower()

    @pytest.mark.asyncio
    async def test_filter_by_rating_outstanding(self) -> None:
        result = await tools.khda_search_school(rating="Outstanding")
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert school["rating"] == "Outstanding"

    @pytest.mark.asyncio
    async def test_invalid_rating_returns_fail(self) -> None:
        result = await tools.khda_search_school(rating="Excellent")
        assert result["success"] is False
        assert "rating" in str(result["error"])

    @pytest.mark.asyncio
    async def test_filter_by_max_fee(self) -> None:
        result = await tools.khda_search_school(max_fee_aed=15000)
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert school["fees_min_aed"] <= 15000

    @pytest.mark.asyncio
    async def test_combined_filters(self) -> None:
        result = await tools.khda_search_school(curriculum="Indian", rating="Outstanding")
        schools = _data(result)["schools"]
        assert isinstance(schools, list)
        assert len(schools) > 0
        for school in schools:
            assert "indian" in school["curriculum"].lower()
            assert school["rating"] == "Outstanding"

    @pytest.mark.asyncio
    async def test_invalid_limit_returns_fail(self) -> None:
        result = await tools.khda_search_school(limit=500)
        assert result["success"] is False
        assert "limit" in str(result["error"])

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(self) -> None:
        result = await tools.khda_search_school(name="ZZZ_NoSuchSchool")
        data = _data(result)
        assert data["count"] == 0
        assert data["schools"] == []


class TestKhdaListCurricula:
    @pytest.mark.asyncio
    async def test_returns_unique_curricula(self) -> None:
        result = await tools.khda_list_curricula()
        curricula = _data(result)["curricula"]
        assert isinstance(curricula, list)
        assert curricula == sorted(set(curricula))


class TestKhdaListAreas:
    @pytest.mark.asyncio
    async def test_returns_unique_areas(self) -> None:
        result = await tools.khda_list_areas()
        areas = _data(result)["areas"]
        assert isinstance(areas, list)
        assert areas == sorted(set(areas))


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.khda import server as khda_server

        importlib.reload(khda_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("khda")}
        assert names == {"khda_search_school", "khda_list_curricula", "khda_list_areas"}

    def test_recommend_for_school_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.khda import server as khda_server

        importlib.reload(khda_server)
        results = get_tool_discovery().recommend(
            "find outstanding rated british school in dubai for my child", top_k=3
        )
        assert results
        assert results[0].name == "khda_search_school"
