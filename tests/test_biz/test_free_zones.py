"""Tests for the free_zones biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.free_zones import tools


class TestListFreeZones:
    @pytest.mark.asyncio
    async def test_returns_all_free_zones(self) -> None:
        result = await tools.list_free_zones()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 10
        free_zones = data["free_zones"]
        assert isinstance(free_zones, list)
        ids = {fz["id"] for fz in free_zones}
        assert "ifza" in ids
        assert "dmcc" in ids
        assert "difc_innovation" in ids
        assert "jafza" in ids


class TestFreeZoneDetails:
    @pytest.mark.asyncio
    async def test_lookup_by_id(self) -> None:
        result = await tools.free_zone_details("dmcc")
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["id"] == "dmcc"
        assert data["name"] == "DMCC"

    @pytest.mark.asyncio
    async def test_difc_innovation_includes_restrictions(self) -> None:
        result = await tools.free_zone_details("difc_innovation")
        data = result["data"]
        assert isinstance(data, dict)
        restrictions = data["restrictions"]
        assert isinstance(restrictions, list)
        assert any("DFSA" in r for r in restrictions)
        assert any("crypto" in r.lower() for r in restrictions)

    @pytest.mark.asyncio
    async def test_unknown_id_returns_error(self) -> None:
        result = await tools.free_zone_details("nonexistent_zone")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_empty_id_returns_error(self) -> None:
        result = await tools.free_zone_details("")
        assert result["success"] is False


class TestCompareFreeZones:
    @pytest.mark.asyncio
    async def test_budget_filter(self) -> None:
        result = await tools.compare_free_zones(budget_aed=15000, limit=10)
        data = result["data"]
        assert isinstance(data, dict)
        free_zones = data["free_zones"]
        assert isinstance(free_zones, list)
        for fz in free_zones:
            cost = fz.get("initial_license_aed", 0)
            assert cost == 0 or cost <= 15000

    @pytest.mark.asyncio
    async def test_no_budget_returns_all_within_limit(self) -> None:
        result = await tools.compare_free_zones(limit=20)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 5

    @pytest.mark.asyncio
    async def test_needs_physical_office_filter(self) -> None:
        result = await tools.compare_free_zones(needs_physical_office=True, limit=20)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_sector_filter(self) -> None:
        result = await tools.compare_free_zones(sector="tech", limit=20)
        data = result["data"]
        assert isinstance(data, dict)
        free_zones = data["free_zones"]
        assert isinstance(free_zones, list)
        assert len(free_zones) >= 1

    @pytest.mark.asyncio
    async def test_results_ranked_by_cost(self) -> None:
        result = await tools.compare_free_zones(limit=5)
        data = result["data"]
        assert isinstance(data, dict)
        free_zones = data["free_zones"]
        assert isinstance(free_zones, list)
        # The cheapest options (IFZA, Meydan) should be in the top 5.
        names = {fz["name"] for fz in free_zones}
        assert "IFZA" in names or "Meydan Free Zone" in names

    @pytest.mark.asyncio
    async def test_invalid_visa_count_returns_error(self) -> None:
        result = await tools.compare_free_zones(visa_count=-1)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_limit_returns_error(self) -> None:
        result = await tools.compare_free_zones(limit=100)
        assert result["success"] is False


class TestListOffshore:
    @pytest.mark.asyncio
    async def test_returns_offshore_options(self) -> None:
        result = await tools.list_offshore()
        data = result["data"]
        assert isinstance(data, dict)
        offshore = data["offshore"]
        assert isinstance(offshore, list)
        ids = {o["id"] for o in offshore}
        assert "rak_icc" in ids
        assert "jafza_offshore" in ids


class TestKnowledgeMetadata:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.list_free_zones()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-04-13"
        assert knowledge["volatility"] == "high"


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.free_zones import server as fz_server

        importlib.reload(fz_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("free_zones")}
        assert names == {
            "list_free_zones",
            "free_zone_details",
            "compare_free_zones",
            "list_offshore",
        }
