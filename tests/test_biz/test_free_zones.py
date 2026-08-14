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
        assert all(fz["source_urls"] for fz in free_zones)


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


class TestFreezoneToMainland:
    @pytest.mark.asyncio
    async def test_list_free_zones_surfaces_mainland_permit_block(self) -> None:
        result = await tools.list_free_zones()
        data = result["data"]
        assert isinstance(data, dict)
        mainland = data["freezone_to_mainland"]
        assert isinstance(mainland, dict)
        assert mainland["legislation"] == "Dubai Executive Council Resolution No. 11 of 2025"
        assert mainland["regularisation_deadline"] == "2026-03-21"
        assert "Director General may grant one extension" in mainland["regularisation_status"]
        assert any("OGD-2025-707.pdf" in url for url in mainland["source_urls"])
        permit_types = mainland["permit_types"]
        assert isinstance(permit_types, list)
        fees = {p["type"]: p["fee_aed"] for p in permit_types}
        assert fees["branch_licence"] == 10000
        assert fees["temporary_permit"] == 5000
        assert "Invest in Dubai" in str(mainland["apply_via"])

    @pytest.mark.asyncio
    async def test_list_free_zones_surfaces_2026_developments(self) -> None:
        result = await tools.list_free_zones()
        data = result["data"]
        assert isinstance(data, dict)
        developments = data["developments_2026"]
        assert isinstance(developments, list)
        ids = {d["id"] for d in developments}
        assert "dso_district_io" in ids
        assert "dmcc_26000_members_tether" in ids
        # The Meydan remote-setup item is single-source and must be flagged.
        meydan = next(d for d in developments if d["id"] == "meydan_remote_setup")
        assert meydan["tag"] == "single_source"

    @pytest.mark.asyncio
    async def test_developments_do_not_add_zone_matrix_entries(self) -> None:
        result = await tools.list_free_zones()
        data = result["data"]
        assert isinstance(data, dict)
        zone_ids = {fz["id"] for fz in data["free_zones"]}
        assert "al_selmiyyah_defence_fz" not in zone_ids


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
        assert all(o["source_urls"] for o in offshore)


class TestKnowledgeMetadata:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.list_free_zones()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-08-14"
        assert knowledge["previous_knowledge_date"] == "2026-07-02"
        assert "regularisation deadline" in knowledge["last_refresh_scope"]
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
