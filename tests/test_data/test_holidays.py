"""Tests for the holidays feature (no network calls, all static data)."""

from __future__ import annotations

import pytest

from mcp_dubai.data.holidays import FEATURE_META, tools
from mcp_dubai.data.holidays.data import HOLIDAY_DATA_DATE, HOLIDAYS_2026, HOLIDAYS_2027


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
        assert len(data["holidays"]) == 13
        assert result["source"]
        assert result["retrieved_at"] == HOLIDAY_DATA_DATE

    @pytest.mark.asyncio
    async def test_returns_2027_holidays(self) -> None:
        result = await tools.uae_holidays(year=2027)
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["year"] == 2027
        assert isinstance(data["holidays"], list)
        assert len(data["holidays"]) == len(HOLIDAYS_2027)
        assert len(data["holidays"]) == 12
        assert "dataset_note" in data
        assert "2026-08-14" in str(data["dataset_note"])

    @pytest.mark.asyncio
    async def test_includes_new_year(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        names = [h["name"] for h in data["holidays"]]
        assert "New Year's Day" in names

    @pytest.mark.asyncio
    async def test_includes_eid_al_etihad(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        dates = [h["date"] for h in data["holidays"]]
        assert "2026-12-02" in dates
        assert "2026-12-03" in dates
        names = [h["name"] for h in data["holidays"]]
        assert "Eid Al Etihad (UAE National Day)" in names

    @pytest.mark.asyncio
    async def test_eid_al_fitr_2026_includes_30_ramadan_day(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        fitr = [h for h in data["holidays"] if h["date"].startswith("2026-03")]
        assert [h["date"] for h in fitr] == [
            "2026-03-19",
            "2026-03-20",
            "2026-03-21",
            "2026-03-22",
        ]
        assert all(h["provisional"] is False for h in fitr)

    @pytest.mark.asyncio
    async def test_eid_al_adha_2026_confirmed(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        adha = [h for h in data["holidays"] if h["date"].startswith("2026-05")]
        assert [h["date"] for h in adha] == [
            "2026-05-26",
            "2026-05-27",
            "2026-05-28",
            "2026-05-29",
        ]
        assert all(h["provisional"] is False for h in adha)
        arafat = adha[0]
        assert arafat["name"] == "Arafat Day"
        assert "2026-05-25" in arafat["note"]

    @pytest.mark.asyncio
    async def test_hijri_new_year_2026_observed_june_15(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        dates = [h["date"] for h in data["holidays"]]
        assert "2026-06-15" in dates
        assert "2026-06-16" not in dates
        hijri = next(h for h in data["holidays"] if h["date"] == "2026-06-15")
        assert hijri["provisional"] is False
        assert "transferable-holiday" in hijri["note"]

    @pytest.mark.asyncio
    async def test_prophets_birthday_2026_still_provisional(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        mawlid = next(h for h in data["holidays"] if h["date"] == "2026-08-25")
        assert mawlid["provisional"] is True
        assert mawlid["official_observance_announced"] is False
        assert "no transferred day is assumed" in mawlid["note"]

    @pytest.mark.asyncio
    async def test_commemoration_day_not_listed(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        dates = [h["date"] for h in data["holidays"]]
        names = [h["name"] for h in data["holidays"]]
        assert "2026-12-01" not in dates
        assert "Commemoration Day" not in names

    @pytest.mark.asyncio
    async def test_2026_provisional_flags(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        for holiday in data["holidays"]:
            if holiday["category"] == "fixed":
                assert holiday["provisional"] is False
            elif holiday["date"] == "2026-08-25":
                assert holiday["provisional"] is True
                assert holiday["official_observance_announced"] is False
            else:
                assert holiday["provisional"] is False
                assert holiday["official_observance_announced"] is True

    @pytest.mark.asyncio
    async def test_2027_lunar_holidays_flagged_provisional(self) -> None:
        result = await tools.uae_holidays(year=2027)
        data = result["data"]
        assert isinstance(data, dict)
        for holiday in data["holidays"]:
            if holiday["category"] == "lunar":
                assert holiday["provisional"] is True
                assert holiday["official_observance_announced"] is False
            elif holiday["category"] == "fixed":
                assert holiday["provisional"] is False

    @pytest.mark.asyncio
    async def test_note_field_optional(self) -> None:
        result = await tools.uae_holidays(year=2026)
        data = result["data"]
        assert isinstance(data, dict)
        new_year = next(h for h in data["holidays"] if h["date"] == "2026-01-01")
        assert "note" not in new_year
        hijri = next(h for h in data["holidays"] if h["date"] == "2026-06-15")
        assert isinstance(hijri["note"], str)

    @pytest.mark.asyncio
    async def test_unknown_year_returns_warning(self) -> None:
        result = await tools.uae_holidays(year=2099)
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["holidays"] == []
        assert "warning" in data

    def test_feature_metadata_uses_current_official_sources(self) -> None:
        source_url = str(FEATURE_META["source_url"])
        description = str(FEATURE_META["description"])
        assert "public-holidays-and-religious-affairs/public-holidays" in source_url
        assert "/jobs/public-holidays" not in source_url
        assert "MOHRE and FAHR" in description


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
        assert next_h["date"] == "2026-06-15"
        assert data["days_away"] == 14

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
    async def test_reference_after_last_2026_holiday_rolls_into_2027(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-12-31")
        data = result["data"]
        assert isinstance(data, dict)
        next_h = data["next_holiday"]
        assert next_h is not None
        assert isinstance(next_h, dict)
        assert next_h["date"] == "2027-01-01"
        assert data["days_away"] == 1

    @pytest.mark.asyncio
    async def test_reference_after_last_curated_holiday(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2027-12-31")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["next_holiday"] is None
        assert "warning" in data

    @pytest.mark.asyncio
    async def test_unannounced_mawlid_is_candidate_not_next_confirmed_holiday(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="2026-08-14")
        data = result["data"]
        assert isinstance(data, dict)
        next_holiday = data["next_holiday"]
        candidate = data["next_provisional_candidate"]
        assert isinstance(next_holiday, dict)
        assert isinstance(candidate, dict)
        assert next_holiday["date"] == "2026-12-02"
        assert candidate["date"] == "2026-08-25"
        assert "not" in str(data["warning"]).lower()

    @pytest.mark.asyncio
    async def test_invalid_date_returns_fail_envelope(self) -> None:
        result = await tools.uae_next_holiday(from_date_str="not-a-date")
        assert result["success"] is False
        assert "Invalid ISO date" in str(result["error"])


class TestIsUaeHoliday:
    @pytest.mark.asyncio
    async def test_eid_al_etihad_is_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-12-02")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is True
        assert data["holiday"] is not None
        holiday = data["holiday"]
        assert isinstance(holiday, dict)
        assert holiday["name"] == "Eid Al Etihad (UAE National Day)"

    @pytest.mark.asyncio
    async def test_hijri_new_year_observed_day_is_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-06-15")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is True
        holiday = data["holiday"]
        assert isinstance(holiday, dict)
        assert holiday["name"] == "Hijri New Year"
        assert "note" in holiday

    @pytest.mark.asyncio
    async def test_hijri_religious_date_is_not_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-06-16")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is False
        assert data["holiday"] is None

    @pytest.mark.asyncio
    async def test_unannounced_mawlid_is_indeterminate(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-08-25")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is None
        assert data["determination"] == "provisional_candidate"
        assert isinstance(data["holiday"], dict)
        assert "cannot yet be determined" in str(data["warning"])

    @pytest.mark.asyncio
    async def test_commemoration_day_is_not_holiday(self) -> None:
        result = await tools.is_uae_holiday(date_str="2026-12-01")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_holiday"] is False
        assert data["holiday"] is None

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

    @pytest.mark.asyncio
    async def test_uncovered_year_fails_instead_of_false(self) -> None:
        # 2028-01-01 IS a statutory holiday; a bare is_holiday=False would be
        # a wrong fact, so uncovered years must fail with a coverage message.
        result = await tools.is_uae_holiday(date_str="2028-01-01")
        assert result["success"] is False
        assert "No curated holiday data for 2028" in str(result["error"])


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
