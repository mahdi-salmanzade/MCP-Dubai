"""Tests for the holidays feature (no network calls, all static data)."""

from __future__ import annotations

import pytest

from mcp_dubai.data.holidays import tools
from mcp_dubai.data.holidays.data import HOLIDAYS_2026


class TestUaeHolidays:
    @pytest.mark.asyncio
    async def test_returns_2026_holidays(self) -> None:
        result = await tools.uae_holidays(year=2026)
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["year"] == 2026
        assert isinstance(data["holidays"], list)
        assert len(data["holidays"]) == len(HOLIDAYS_2026)
        assert result["source"]
        assert result["retrieved_at"]

    @pytest.mark.asyncio
    async def test_includes_new_year(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        names = [h["name"] for h in data["holidays"]]
        assert "New Year's Day" in names

    @pytest.mark.asyncio
    async def test_includes_national_day(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        dates = [h["date"] for h in data["holidays"]]
        assert "2026-12-02" in dates

    @pytest.mark.asyncio
    async def test_lunar_holidays_flagged_provisional(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        for holiday in data["holidays"]:
            if holiday["category"] == "lunar":
                assert holiday["provisional"] is True
            elif holiday["category"] == "fixed":
                assert holiday["provisional"] is False

    @pytest.mark.asyncio
    async def test_unknown_year_returns_warning(self) -> None:
        result = await tools.uae_holidays(year=2099)
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["holidays"] == []
        assert "warning" in data


class TestUaeNextHoliday:
    @pytest.mark.asyncio
    async def test_finds_next_holiday_after_reference(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-06-01")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["from_date"] == "2026-06-01"
        next_h = data["next_holiday"]
        assert next_h is not None
        assert isinstance(next_h, dict)
        assert next_h["date"] == "2026-06-16"
        assert data["days_away"] == 15

    @pytest.mark.asyncio
    async def test_reference_on_holiday_returns_same_day(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-12-02")
        data = result["data"]
        assert isinstance(data, dict)
        next_h = data["next_holiday"]
        assert next_h is not None
        assert isinstance(next_h, dict)
        assert next_h["date"] == "2026-12-02"
        assert data["days_away"] == 0

    @pytest.mark.asyncio
    async def test_reference_after_last_holiday_of_year(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-12-31")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["next_holiday"] is None
        assert "warning" in data

    @pytest.mark.asyncio
    async def test_invalid_date_returns_fail_envelope(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="not-a-date")
        assert result["success"] is False
        assert "Invalid ISO date" in str(result["error"])


class TestIsUaeHoliday:
    @pytest.mark.asyncio
    async def test_national_day_is_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-12-02")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is True
        assert data["holiday"] is not None
        holiday = data["holiday"]
        assert isinstance(holiday, dict)
        assert holiday["name"] == "UAE National Day"

    @pytest.mark.asyncio
    async def test_random_workday_is_not_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-04-15")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is False
        assert data["holiday"] is None

    @pytest.mark.asyncio
    async def test_invalid_date_returns_fail_envelope(self) -> None:
        result = await tools.is_uae_holiday(date_str="not-a-date")
        assert result["success"] is False
        assert "Invalid ISO date" in str(result["error"])


class TestDiscovery:
    def test_all_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.holidays import server as holidays_server

        importlib.reload(holidays_server)

        discovery = get_tool_discovery()
        names = {t.name for t in discovery.get_by_feature("holidays")}
        assert names == {"uae_holidays", "uae_next_holiday", "is_uae_holiday"}

    def test_recommend_for_eid_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.holidays import server as holidays_server

        importlib.reload(holidays_server)

        discovery = get_tool_discovery()
        results = discovery.recommend("when is eid public holiday in uae", top_k=3)
        assert results
        assert results[0].feature == "holidays"
