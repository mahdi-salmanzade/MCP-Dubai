"""Tests for the holidays feature (no network calls, all static data)."""

from __future__ import annotations

import pytest

from mcp_dubai.data.holidays import tools
from mcp_dubai.data.holidays.data import HOLIDAYS_2026


class TestUaeHolidays:
    @pytest.mark.asyncio
    async def test_returns_2026_holidays(self) -> None:
        result = await tools.uae_holidays(year=2026)
        assert result["year"] == 2026
        assert isinstance(result["holidays"], list)
        assert len(result["holidays"]) == len(HOLIDAYS_2026)

    @pytest.mark.asyncio
    async def test_includes_new_year(self) -> None:
        result = await tools.uae_holidays(year=2026)
        names = [h["name"] for h in result["holidays"]]  # type: ignore[union-attr]
        assert "New Year's Day" in names

    @pytest.mark.asyncio
    async def test_includes_national_day(self) -> None:
        result = await tools.uae_holidays(year=2026)
        dates = [h["date"] for h in result["holidays"]]  # type: ignore[union-attr]
        assert "2026-12-02" in dates

    @pytest.mark.asyncio
    async def test_lunar_holidays_flagged_provisional(self) -> None:
        result = await tools.uae_holidays(year=2026)
        for holiday in result["holidays"]:  # type: ignore[union-attr]
            if holiday["category"] == "lunar":
                assert holiday["provisional"] is True
            elif holiday["category"] == "fixed":
                assert holiday["provisional"] is False

    @pytest.mark.asyncio
    async def test_unknown_year_returns_warning(self) -> None:
        result = await tools.uae_holidays(year=2099)
        assert result["holidays"] == []
        assert "warning" in result


class TestUaeNextHoliday:
    @pytest.mark.asyncio
    async def test_finds_next_holiday_after_reference(self) -> None:
        # Reference is mid-year so next is Hijri New Year (2026-06-16) or later.
        result = await tools.uae_next_holiday(from_date_str="2026-06-01")
        assert result["from_date"] == "2026-06-01"
        next_h = result["next_holiday"]
        assert next_h is not None
        assert isinstance(next_h, dict)
        # Should be Hijri New Year on 2026-06-16, 15 days away.
        assert next_h["date"] == "2026-06-16"
        assert result["days_away"] == 15

    @pytest.mark.asyncio
    async def test_reference_on_holiday_returns_same_day(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-12-02")
        next_h = result["next_holiday"]
        assert next_h is not None
        assert isinstance(next_h, dict)
        assert next_h["date"] == "2026-12-02"
        assert result["days_away"] == 0

    @pytest.mark.asyncio
    async def test_reference_after_last_holiday_of_year(self) -> None:
        # No 2027 data shipped, so this returns nothing.
        result = await tools.uae_next_holiday(from_date_str="2026-12-31")
        assert result["next_holiday"] is None
        assert "warning" in result


class TestIsUaeHoliday:
    @pytest.mark.asyncio
    async def test_national_day_is_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-12-02")
        assert result["is_holiday"] is True
        assert result["holiday"] is not None
        holiday = result["holiday"]
        assert isinstance(holiday, dict)
        assert holiday["name"] == "UAE National Day"

    @pytest.mark.asyncio
    async def test_random_workday_is_not_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-04-15")
        assert result["is_holiday"] is False
        assert result["holiday"] is None

    @pytest.mark.asyncio
    async def test_invalid_date_raises(self) -> None:
        with pytest.raises(ValueError, match=r"Invalid ISO date"):
            await tools.is_uae_holiday(date_str="not-a-date")


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
