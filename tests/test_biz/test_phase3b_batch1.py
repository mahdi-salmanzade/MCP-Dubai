"""Phase 3b batch 1: compliance, funding, gov_portals smoke tests."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.compliance import tools as compliance_tools
from mcp_dubai.biz.funding import tools as funding_tools
from mcp_dubai.biz.gov_portals import tools as gov_portals_tools


class TestCompliance:
    @pytest.mark.asyncio
    async def test_aml_real_estate_is_dnfbp(self) -> None:
        result = await compliance_tools.aml_requirements(business_category="real_estate")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_dnfbp"] is True
        assert any("goAML" in step for step in data["next_steps"])  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_aml_general_is_not_dnfbp(self) -> None:
        result = await compliance_tools.aml_requirements()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_dnfbp"] is False

    @pytest.mark.asyncio
    async def test_aml_law_is_fdl_10_of_2025(self) -> None:
        result = await compliance_tools.aml_requirements()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["law"] == "Federal Decree-Law 10 of 2025"
        assert data["law_in_force_since"] == "2025-10-14"
        previous = data["previous_law"]
        assert isinstance(previous, dict)
        assert previous["law"] == "Federal Decree-Law 20 of 2018"
        fines = data["fines_aed"]
        assert isinstance(fines, dict)
        assert fines["legal_persons_minimum"] == 5_000_000
        assert fines["legal_persons_maximum"] == 100_000_000
        assert any(
            "Tax evasion" in change
            for change in data["key_changes_2025"]  # type: ignore[union-attr]
        )

    @pytest.mark.asyncio
    async def test_emiratisation_50_plus_band(self) -> None:
        result = await compliance_tools.emiratisation_requirements(employee_count=120)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["applicable_band"] == "firms_50_plus"
        band = data["firms_50_plus"]
        assert isinstance(band, dict)
        assert band["h1_2026_deadline"] == "2026-06-30"
        charge = band["non_compliance_charge"]
        assert isinstance(charge, dict)
        assert charge["monthly_charge_aed_per_position"] == 10_000
        assert charge["charged_from"] == "2026-07-01"

    @pytest.mark.asyncio
    async def test_emiratisation_20_49_band(self) -> None:
        result = await compliance_tools.emiratisation_requirements(employee_count=30)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["applicable_band"] == "firms_20_to_49"
        band = data["firms_20_to_49"]
        assert isinstance(band, dict)
        assert band["non_compliance_charge"]["shortfall_2025_aed"] == 108_000  # type: ignore[index]

    @pytest.mark.asyncio
    async def test_emiratisation_no_count_returns_all_bands(self) -> None:
        result = await compliance_tools.emiratisation_requirements()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["applicable_band"] is None
        assert "firms_50_plus" in data
        assert "firms_20_to_49" in data
        assert data["regulator"] == "Ministry of Human Resources and Emiratisation (MOHRE)"

    @pytest.mark.asyncio
    async def test_emiratisation_negative_count_fails(self) -> None:
        result = await compliance_tools.emiratisation_requirements(employee_count=-1)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_ubo_filing_25pct_threshold(self) -> None:
        result = await compliance_tools.ubo_filing_guide()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["threshold_pct"] == 25
        assert data["update_window_days"] == 15

    @pytest.mark.asyncio
    async def test_pdpl_uae_federal(self) -> None:
        result = await compliance_tools.pdpl_compliance(jurisdiction="uae_federal")
        data = result["data"]
        assert isinstance(data, dict)
        assert "Federal Decree-Law 45 of 2021" in str(data.get("law", ""))

    @pytest.mark.asyncio
    async def test_pdpl_invalid_jurisdiction(self) -> None:
        result = await compliance_tools.pdpl_compliance(jurisdiction="mars")
        assert result["success"] is False


class TestFunding:
    @pytest.mark.asyncio
    async def test_accelerator_search_no_filter(self) -> None:
        result = await funding_tools.accelerator_search()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 5
        ids = {a["id"] for a in data["accelerators"]}  # type: ignore[union-attr]
        assert "in5" in ids
        assert "hub71" in ids

    @pytest.mark.asyncio
    async def test_accelerator_search_free_only_excludes_paid(self) -> None:
        result = await funding_tools.accelerator_search(free_only=True)
        data = result["data"]
        assert isinstance(data, dict)
        ids = {a["id"] for a in data["accelerators"]}  # type: ignore[union-attr]
        assert "astrolabs" not in ids

    @pytest.mark.asyncio
    async def test_accelerator_search_by_sector(self) -> None:
        result = await funding_tools.accelerator_search(sector="fintech")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_vc_list_filters_by_stage(self) -> None:
        result = await funding_tools.vc_list(stage="seed")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 1

    @pytest.mark.asyncio
    async def test_vc_list_includes_excluded_section(self) -> None:
        result = await funding_tools.vc_list()
        data = result["data"]
        assert isinstance(data, dict)
        excluded = data["excluded_with_reason"]
        assert isinstance(excluded, list)
        names = {e["name"] for e in excluded}
        assert "Cypress Growth Capital" in names

    @pytest.mark.asyncio
    async def test_vc_list_invalid_stage(self) -> None:
        result = await funding_tools.vc_list(stage="series_z")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_grant_programs_includes_mbrif_warning(self) -> None:
        result = await funding_tools.grant_programs()
        data = result["data"]
        assert isinstance(data, dict)
        assert "MBRIF" in str(data["warning"])
        assert data["count"] >= 3


class TestGovPortals:
    @pytest.mark.asyncio
    async def test_portal_lookup_uae_pass(self) -> None:
        result = await gov_portals_tools.portal_guide(portal_id="uae_pass")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["developer_api"] is True
        assert data["auth_protocol"] == "OAuth 2.0 / OpenID Connect"

    @pytest.mark.asyncio
    async def test_portal_lookup_emaratax(self) -> None:
        result = await gov_portals_tools.portal_guide(portal_id="emaratax")
        data = result["data"]
        assert isinstance(data, dict)
        assert "FTA" in str(data.get("operator", ""))

    @pytest.mark.asyncio
    async def test_portal_keyword_search(self) -> None:
        result = await gov_portals_tools.portal_guide(keyword="immigration")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 2

    @pytest.mark.asyncio
    async def test_portal_no_filter_lists_all_with_disambiguation(self) -> None:
        result = await gov_portals_tools.portal_guide()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 10
        disambig = data["disambiguation"]
        assert isinstance(disambig, list)
        names = {d["name"] for d in disambig}
        assert "Sahel app" in names

    @pytest.mark.asyncio
    async def test_portal_unknown_id(self) -> None:
        result = await gov_portals_tools.portal_guide(portal_id="not_a_portal")
        assert result["success"] is False


class TestKnowledgeRegistration:
    def test_three_features_register(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.compliance import tools as ct
        from mcp_dubai.biz.funding import tools as ft
        from mcp_dubai.biz.gov_portals import tools as gt

        importlib.reload(ct)
        importlib.reload(ft)
        importlib.reload(gt)

        registry = get_knowledge_registry()
        assert registry.get("compliance") is not None
        assert registry.get("funding") is not None
        assert registry.get("gov_portals") is not None
