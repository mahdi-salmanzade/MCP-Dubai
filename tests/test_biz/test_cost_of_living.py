"""Tests for the cost_of_living biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.cost_of_living import tools


class TestOverview:
    @pytest.mark.asyncio
    async def test_returns_all_blocks(self) -> None:
        result = await tools.cost_of_living_overview()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        for block in ("rents", "utilities", "groceries", "transport", "schooling"):
            assert block in data
        budget = data["sample_monthly_budget_aed"]
        assert isinstance(budget, dict)
        for household in ("single", "couple", "family_of_four"):
            assert household in budget
            assert "total_monthly_aed" in budget[household]

    @pytest.mark.asyncio
    async def test_citywide_average(self) -> None:
        result = await tools.cost_of_living_overview()
        data = result["data"]
        assert isinstance(data, dict)
        rents = data["rents"]
        assert isinstance(rents, dict)
        assert rents["citywide_1br_average_aed"] == 97000


class TestRentEstimate:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        result = await tools.rent_estimate(area="Dubai Marina", bedrooms="1BR")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["area"] == "Dubai Marina"
        assert data["annual_rent_aed"] == [75000, 115000]

    @pytest.mark.asyncio
    async def test_case_insensitive_area(self) -> None:
        result = await tools.rent_estimate(area="dubai marina", bedrooms="2BR")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["area"] == "Dubai Marina"
        assert data["annual_rent_aed"] == [110000, 170000]

    @pytest.mark.asyncio
    async def test_unknown_area_fails(self) -> None:
        result = await tools.rent_estimate(area="Atlantis Moon Base")
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert "Valid areas" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_bedrooms_fails(self) -> None:
        result = await tools.rent_estimate(area="JLT", bedrooms="penthouse")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_bedroom_not_available_in_area_fails(self) -> None:
        # Downtown Dubai has no studio entry in the curated data.
        result = await tools.rent_estimate(area="Downtown Dubai", bedrooms="studio")
        assert result["success"] is False


class TestDewaBillEstimate:
    @pytest.mark.asyncio
    async def test_happy_path_summer(self) -> None:
        result = await tools.dewa_bill_estimate(unit_size="2BR", season="summer")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["typical_monthly_bill_aed"] == [400, 700]
        assert "2.5x" in data["season_note"]
        slabs = data["electricity_slabs_fils_per_kwh"]
        assert isinstance(slabs, list)
        assert len(slabs) == 4

    @pytest.mark.asyncio
    async def test_housing_fee_present(self) -> None:
        result = await tools.dewa_bill_estimate(unit_size="1BR")
        data = result["data"]
        assert isinstance(data, dict)
        fee = data["housing_fee"]
        assert isinstance(fee, dict)
        assert fee["apartment_pct_of_annual_rent"] == 5
        assert fee["villa_pct_of_annual_rent"] == 10

    @pytest.mark.asyncio
    async def test_invalid_unit_size_fails(self) -> None:
        result = await tools.dewa_bill_estimate(unit_size="mansion")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_season_fails(self) -> None:
        result = await tools.dewa_bill_estimate(unit_size="1BR", season="monsoon")
        assert result["success"] is False


class TestSalikTollEstimate:
    @pytest.mark.asyncio
    async def test_peak_weekday(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="08:00", day="weekday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 6
        assert data["window_applied"] == "peak"

    @pytest.mark.asyncio
    async def test_off_peak_weekday(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="12:00", day="weekday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 4
        assert data["window_applied"] == "off-peak"

    @pytest.mark.asyncio
    async def test_free_window(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="03:00")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 0
        assert "free" in data["window_applied"]

    @pytest.mark.asyncio
    async def test_sunday_flat(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="12:00", day="sunday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 4
        assert data["window_applied"] == "sunday flat"

    @pytest.mark.asyncio
    async def test_sunday_inside_free_window_is_zero(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="03:00", day="sunday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 0

    @pytest.mark.asyncio
    async def test_late_evening_off_peak(self) -> None:
        # 20:00-01:00 is off-peak.
        result = await tools.salik_toll_estimate(time_of_day="22:30", day="weekday")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["toll_aed"] == 4

    @pytest.mark.asyncio
    async def test_bad_format_fails(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="8 oclock")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_out_of_range_time_fails(self) -> None:
        result = await tools.salik_toll_estimate(time_of_day="25:99")
        assert result["success"] is False


class TestGroceryEstimate:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        result = await tools.grocery_estimate(household_size="family_of_four")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["monthly_aed"] == [2000, 3000]
        assert data["weekly_aed"] == [650, 1200]
        staples = data["staples_aed"]
        assert isinstance(staples, dict)
        assert staples["milk_1l"] == [6, 8]

    @pytest.mark.asyncio
    async def test_single_includes_branded_tier(self) -> None:
        result = await tools.grocery_estimate(household_size="single")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["branded_imported_monthly_aed"] == [1000, 2500]

    @pytest.mark.asyncio
    async def test_invalid_household_fails(self) -> None:
        result = await tools.grocery_estimate(household_size="commune")
        assert result["success"] is False


class TestSchoolFeeEstimate:
    @pytest.mark.asyncio
    async def test_primary_maps_to_foundation_band(self) -> None:
        result = await tools.school_fee_estimate(stage="primary")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["annual_fee_aed"] == [7000, 40000]

    @pytest.mark.asyncio
    async def test_secondary(self) -> None:
        result = await tools.school_fee_estimate(stage="secondary")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["annual_fee_aed"] == [20000, 120000]
        assert "KHDA" in data["fee_increase_cap_rule"]

    @pytest.mark.asyncio
    async def test_invalid_stage_fails(self) -> None:
        result = await tools.school_fee_estimate(stage="kindergarten")
        assert result["success"] is False


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.cost_of_living_overview()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-06-26"
        assert knowledge["volatility"] == "high"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.cost_of_living import tools as col_tools

        importlib.reload(col_tools)
        meta = get_knowledge_registry().get("cost_of_living")
        assert meta is not None


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.cost_of_living import server as col_server

        importlib.reload(col_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("cost_of_living")}
        assert names == {
            "cost_of_living_overview",
            "rent_estimate",
            "dewa_bill_estimate",
            "salik_toll_estimate",
            "grocery_estimate",
            "school_fee_estimate",
        }

    def test_recommends_for_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.cost_of_living import server as col_server

        importlib.reload(col_server)
        recs = get_tool_discovery().recommend("cost of living rent dubai")
        names = {t.name for t in recs}
        assert "cost_of_living_overview" in names or "rent_estimate" in names
