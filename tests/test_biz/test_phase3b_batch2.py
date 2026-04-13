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
        assert data["count"] >= 5

    @pytest.mark.asyncio
    async def test_filter_events_by_category(self) -> None:
        result = await events_tools.startup_events(category="tech")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_gitex_info_returns_2026(self) -> None:
        result = await events_tools.gitex_info()
        data = result["data"]
        assert isinstance(data, dict)
        assert "2026" in data["name"]

    @pytest.mark.asyncio
    async def test_ens_calendar_returns_supernova_0x(self) -> None:
        result = await events_tools.ens_calendar()
        data = result["data"]
        assert isinstance(data, dict)
        supernova = data["supernova_format"]
        assert isinstance(supernova, dict)
        assert supernova["name"] == "Supernova 0X"
        assert supernova["prize_pool_usd"] == 200000


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
