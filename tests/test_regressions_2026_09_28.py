"""Regression tests for bugs found in the 28 September 2026 review."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.discovery import ToolDiscovery, ToolMeta
from mcp_dubai._shared.health import get_upstream_registry
from mcp_dubai.biz.banking import tools as banking_tools
from mcp_dubai.biz.cost_of_living import tools as col_tools
from mcp_dubai.data.currency import tools as currency_tools
from mcp_dubai.data.data_dubai import constants as data_dubai_constants
from mcp_dubai.data.data_dubai import tools as data_dubai_tools
from mcp_dubai.data.quran_cloud import constants as quran_constants
from mcp_dubai.data.quran_cloud import tools as quran_tools


def _upstream_failures(name: str) -> int:
    for entry in get_upstream_registry().snapshot():
        if isinstance(entry, dict) and entry.get("name") == name:
            return int(entry.get("failure_count", 0) or 0)
    return 0


class TestQuranSearchNoMatches:
    @pytest.mark.asyncio
    @respx.mock
    async def test_upstream_404_no_match_is_an_empty_result(self) -> None:
        # api.alquran.cloud answers a search with no results using HTTP 404.
        respx.get(f"{quran_constants.SEARCH}/zzzqqq/all/en").mock(
            return_value=Response(
                404,
                json={
                    "code": 404,
                    "status": "NOT FOUND",
                    "data": "Nothing matching your search was found..",
                },
            )
        )
        before = _upstream_failures("quran_cloud")

        result = await quran_tools.quran_search(query="zzzqqq")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 0
        assert data["matches"] == []
        assert data["next_offset"] is None
        assert _upstream_failures("quran_cloud") == before

    @pytest.mark.asyncio
    @respx.mock
    async def test_other_404_is_still_an_upstream_error(self) -> None:
        respx.get(f"{quran_constants.SEARCH}/abc/all/en").mock(
            return_value=Response(404, text="gateway route missing")
        )

        result = await quran_tools.quran_search(query="abc")

        assert result["success"] is False


class TestDataDubaiPastLastPage:
    @pytest.mark.asyncio
    @respx.mock
    async def test_unfiltered_page_after_last_page_is_empty_success(self) -> None:
        respx.get(data_dubai_constants.DATASETS_ENDPOINT).mock(
            return_value=Response(
                200,
                json={
                    "items": [],
                    "totalCount": 630,
                    "page": 999,
                    "pageSize": 10,
                    "lastPage": 63,
                },
            )
        )

        result = await data_dubai_tools.data_dubai_search(page=999)

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["datasets"] == []
        assert data["last_page"] == 63


class TestRecommendTopK:
    def test_non_positive_top_k_returns_nothing(self) -> None:
        discovery = ToolDiscovery()
        discovery.register_many(
            [
                ToolMeta(name=f"prayer_tool_{i}", description="prayer times", feature="f", tier=0)
                for i in range(4)
            ]
        )
        assert len(discovery.recommend("prayer times", top_k=2)) == 2
        # A negative slice bound used to return all but the last matches.
        assert discovery.recommend("prayer times", top_k=-1) == []
        assert discovery.recommend("prayer times", top_k=0) == []


class TestSalikDay:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("day", ["Sunday", "SUNDAY", " sun "])
    async def test_sunday_is_case_insensitive(self, day: str) -> None:
        result = await col_tools.salik_toll_estimate(time_of_day="08:00", day=day)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["window_applied"] == "sunday flat"
        assert data["day"] == "sunday"

    @pytest.mark.asyncio
    async def test_saturday_uses_weekday_peak(self) -> None:
        result = await col_tools.salik_toll_estimate(time_of_day="08:00", day="Saturday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["window_applied"] == "peak"

    @pytest.mark.asyncio
    async def test_unknown_day_fails(self) -> None:
        result = await col_tools.salik_toll_estimate(time_of_day="08:00", day="garbage")
        assert result["success"] is False


class TestDulBankMatching:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("bank_id", ["bank", "e", "emirates"])
    async def test_fragments_are_not_integrated(self, bank_id: str) -> None:
        result = await banking_tools.dul_eligibility(bank_id=bank_id)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["bank_status"] == "not_listed_in_official_announcement"
        assert data["eligible"] is False

    @pytest.mark.asyncio
    async def test_blank_bank_id_fails(self) -> None:
        result = await banking_tools.dul_eligibility(bank_id="  ")
        assert result["success"] is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize("bank_id", ["mashreq", "FAB", "mashreq_neobiz", "emirates-nbd"])
    async def test_real_names_still_match(self, bank_id: str) -> None:
        result = await banking_tools.dul_eligibility(bank_id=bank_id)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["bank_status"] == "integrated"


class TestCurrencyCodeValidation:
    @pytest.mark.asyncio
    @respx.mock
    async def test_path_like_base_is_rejected_without_a_request(self) -> None:
        route = respx.get(url__regex=r".*").mock(return_value=Response(200, json={}))
        result = await currency_tools.currency_rates(base="../../x?y#z")
        assert result["success"] is False
        assert not route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_target_code_is_rejected_without_a_request(self) -> None:
        route = respx.get(url__regex=r".*").mock(return_value=Response(200, json={}))
        result = await currency_tools.currency_convert(100, "AED", "US")
        assert result["success"] is False
        assert "to_currency" in str(result["error"])
        assert not route.called
