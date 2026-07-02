"""Phase 3b batch 2: dcde, events, parkin smoke tests."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.dcde import tools as dcde_tools
from mcp_dubai.biz.events import tools as events_tools
from mcp_dubai.biz.parkin import tools as parkin_tools


class TestDcde:
    @pytest.mark.asyncio
    async def test_list_all_programs(self) -> None:
        result = await dcde_tools.dcde_programs()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 5
        ids = {p["id"] for p in data["programs"]}  # type: ignore[union-attr]
        assert "antler_residency" in ids
        assert "frwrdx" in ids
        assert "create_apps_championship" in ids

    @pytest.mark.asyncio
    async def test_lookup_specific_program(self) -> None:
        result = await dcde_tools.dcde_programs(program_id="antler_residency")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["target"] == "600+ founders"

    @pytest.mark.asyncio
    async def test_unknown_program(self) -> None:
        result = await dcde_tools.dcde_programs(program_id="not_a_program")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_chamber_membership_no_standalone(self) -> None:
        result = await dcde_tools.chamber_membership()
        data = result["data"]
        assert isinstance(data, dict)
        membership = data["membership"]
        assert isinstance(membership, dict)
        assert membership["standalone_membership"] is False


class TestEvents:
    @pytest.mark.asyncio
    async def test_list_all_events(self) -> None:
        result = await events_tools.startup_events()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 18

    @pytest.mark.asyncio
    async def test_filter_events_by_category(self) -> None:
        result = await events_tools.startup_events(category="tech")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_filter_retail_festivals(self) -> None:
        result = await events_tools.startup_events(category="retail")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 4
        ids = {e["id"] for e in data["events"]}  # type: ignore[union-attr]
        assert "dubai_summer_surprises_2026" in ids
        assert "dubai_shopping_festival_2026_27" in ids

    @pytest.mark.asyncio
    async def test_list_includes_curated_notes(self) -> None:
        result = await events_tools.startup_events()
        data = result["data"]
        assert isinstance(data, dict)
        availability = data["data_availability"]
        assert isinstance(availability, dict)
        assert availability["public_api"] is False
        venue_shift = data["venue_shift"]
        assert isinstance(venue_shift, dict)
        assert "Dubai Exhibition Centre" in str(venue_shift["summary"])

    @pytest.mark.asyncio
    async def test_gitex_info_returns_2026(self) -> None:
        result = await events_tools.gitex_info()
        data = result["data"]
        assert isinstance(data, dict)
        assert "2026" in data["name"]
        dates = data["dates"]
        assert isinstance(dates, dict)
        assert dates["start"] == "2026-12-07"
        assert dates["end"] == "2026-12-11"
        assert "Expo City" in str(data["venue"])

    @pytest.mark.asyncio
    async def test_ens_calendar_returns_supernova_0x(self) -> None:
        result = await events_tools.ens_calendar()
        data = result["data"]
        assert isinstance(data, dict)
        supernova = data["supernova_format"]
        assert isinstance(supernova, dict)
        assert supernova["name"] == "Supernova 0X"
        assert supernova["prize_pool_usd"] == 200000

    @pytest.mark.asyncio
    async def test_ens_dates_sit_inside_gitex_week(self) -> None:
        result = await events_tools.ens_calendar()
        data = result["data"]
        assert isinstance(data, dict)
        dates = data["dates"]
        assert isinstance(dates, dict)
        assert dates["start"] == "2026-12-08"
        assert dates["end"] == "2026-12-10"

    def test_knowledge_date_refreshed(self) -> None:
        assert events_tools.KNOWLEDGE.knowledge_date == "2026-07-02"


class TestParkin:
    @pytest.mark.asyncio
    async def test_parking_zones_naming_correction(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        naming = data["naming_correction"]
        assert isinstance(naming, dict)
        assert naming["wrong"] == "Mawaqif"
        assert naming["wrong_belongs_to"] == "Abu Dhabi"

    @pytest.mark.asyncio
    async def test_parking_variable_tariffs(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        tariffs = data["tariffs"]
        assert isinstance(tariffs, dict)
        assert tariffs["live_since"] == "2025-04-04"
        assert tariffs["premium_peak_aed_per_hour"] == 6

    @pytest.mark.asyncio
    async def test_parking_mparking_shortcode(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        mparking = data["mparking"]
        assert isinstance(mparking, dict)
        assert mparking["sms_shortcode"] == "7275"

    @pytest.mark.asyncio
    async def test_parking_vat_block(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        vat = data["vat"]
        assert isinstance(vat, dict)
        assert vat["rate_pct"] == 5
        assert vat["applies_from"] == "2026-06-01"
        assert "VAT-inclusive" in str(vat["summary"])
        tariffs = data["tariffs"]
        assert isinstance(tariffs, dict)
        assert "5% VAT" in str(tariffs["vat_note"])

    @pytest.mark.asyncio
    async def test_parking_cashless_payments_note(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        payments = data["payments"]
        assert isinstance(payments, dict)
        assert payments["cashless_meters_from"] == "2026-06-01"
        assert any("Nol" in m for m in payments["accepted_methods"])

    @pytest.mark.asyncio
    async def test_parking_new_paid_areas_2026(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        zones = data["zones"]
        assert isinstance(zones, dict)
        areas = {a["area"]: a for a in zones["new_paid_areas_2026"]}
        assert areas["International City"]["operator"] == "Parkin"
        assert "Parkonic" in areas["Discovery Gardens"]["operator"]

    @pytest.mark.asyncio
    async def test_parking_mall_expansion(self) -> None:
        result = await parkin_tools.parking_zones()
        data = result["data"]
        assert isinstance(data, dict)
        mall = data["mall_parking"]
        assert isinstance(mall, dict)
        assert "Mall of the Emirates" in str(mall["majid_al_futtaim"])
        assert "Dubai Mall" in str(mall["emaar"])
        assert "Al Futtaim" in str(mall["al_futtaim"])
        assert "60,000" in str(mall["secure_parking_jv"])

    @pytest.mark.asyncio
    async def test_nol_card_guide_lists_5_types(self) -> None:
        result = await parkin_tools.nol_card_guide()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["cards_count"] == 5

    @pytest.mark.asyncio
    async def test_nol_silver_filter(self) -> None:
        result = await parkin_tools.nol_card_guide(card_type="Silver")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["cards_count"] == 1

    @pytest.mark.asyncio
    async def test_nol_no_balance_api(self) -> None:
        result = await parkin_tools.nol_card_guide()
        data = result["data"]
        assert isinstance(data, dict)
        api_status = data["nol_api_status"]
        assert isinstance(api_status, dict)
        assert api_status["balance_check_api"] is False


class TestKnowledgeRegistration:
    def test_three_features_register(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.dcde import tools as dt
        from mcp_dubai.biz.events import tools as et
        from mcp_dubai.biz.parkin import tools as pt

        importlib.reload(dt)
        importlib.reload(et)
        importlib.reload(pt)

        registry = get_knowledge_registry()
        assert registry.get("dcde") is not None
        assert registry.get("events") is not None
        assert registry.get("parkin") is not None
