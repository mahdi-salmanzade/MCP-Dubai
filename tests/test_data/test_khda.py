"""Tests for the KHDA school search feature (no network)."""

from __future__ import annotations

import pytest

from mcp_dubai.data.khda import tools
from mcp_dubai.data.khda.snapshot import SCHOOLS


class TestKhdaSearchSchool:
    @pytest.mark.asyncio
    async def test_no_filters_returns_all_within_limit(self) -> None:
        result = await tools.khda_search_school()
        assert result["count"] == len(SCHOOLS)
        schools = result["schools"]
        assert isinstance(schools, list)
        assert len(schools) == len(SCHOOLS)

    @pytest.mark.asyncio
    async def test_filter_by_name(self) -> None:
        result = await tools.khda_search_school(name="Wellington")
        schools = result["schools"]
        assert isinstance(schools, list)
        assert any("Wellington" in s["name"] for s in schools)

    @pytest.mark.asyncio
    async def test_filter_by_area(self) -> None:
        result = await tools.khda_search_school(area="Jumeirah")
        schools = result["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert "jumeirah" in school["area"].lower()

    @pytest.mark.asyncio
    async def test_filter_by_curriculum(self) -> None:
        result = await tools.khda_search_school(curriculum="British")
        schools = result["schools"]
        assert isinstance(schools, list)
        assert len(schools) > 0
        for school in schools:
            assert "british" in school["curriculum"].lower()

    @pytest.mark.asyncio
    async def test_filter_by_rating_outstanding(self) -> None:
        result = await tools.khda_search_school(rating="Outstanding")
        schools = result["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert school["rating"] == "Outstanding"

    @pytest.mark.asyncio
    async def test_invalid_rating_raises(self) -> None:
        with pytest.raises(ValueError, match=r"rating"):
            await tools.khda_search_school(rating="Excellent")

    @pytest.mark.asyncio
    async def test_filter_by_max_fee(self) -> None:
        result = await tools.khda_search_school(max_fee_aed=15000)
        schools = result["schools"]
        assert isinstance(schools, list)
        for school in schools:
            assert school["fees_min_aed"] <= 15000

    @pytest.mark.asyncio
    async def test_combined_filters(self) -> None:
        result = await tools.khda_search_school(curriculum="Indian", rating="Outstanding")
        schools = result["schools"]
        assert isinstance(schools, list)
        assert len(schools) > 0
        for school in schools:
            assert "indian" in school["curriculum"].lower()
            assert school["rating"] == "Outstanding"

    @pytest.mark.asyncio
    async def test_invalid_limit_raises(self) -> None:
        with pytest.raises(ValueError, match=r"limit"):
            await tools.khda_search_school(limit=500)

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(self) -> None:
        result = await tools.khda_search_school(name="ZZZ_NoSuchSchool")
        assert result["count"] == 0
        assert result["schools"] == []


class TestKhdaListCurricula:
    @pytest.mark.asyncio
    async def test_returns_unique_curricula(self) -> None:
        result = await tools.khda_list_curricula()
        curricula = result["curricula"]
        assert isinstance(curricula, list)
        # Should be sorted and unique
        assert curricula == sorted(set(curricula))


class TestKhdaListAreas:
    @pytest.mark.asyncio
    async def test_returns_unique_areas(self) -> None:
        result = await tools.khda_list_areas()
        areas = result["areas"]
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
        # Use a query that does not collide with "curriculum" or "area" which
        # would otherwise outrank the search tool in a 3-doc corpus.
        results = get_tool_discovery().recommend(
            "find outstanding rated british school in dubai for my child", top_k=3
        )
        assert results
        assert results[0].name == "khda_search_school"
