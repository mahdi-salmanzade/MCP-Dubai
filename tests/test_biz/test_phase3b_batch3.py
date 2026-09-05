"""Phase 3b batch 3: ip_trademark, halal, createapps smoke tests."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.createapps import tools as createapps_tools
from mcp_dubai.biz.halal import tools as halal_tools
from mcp_dubai.biz.ip_trademark import tools as ip_tools


class TestIpTrademark:
    @pytest.mark.asyncio
    async def test_trademark_registration_basic(self) -> None:
        result = await ip_tools.trademark_registration()
        data = result["data"]
        assert isinstance(data, dict)
        cost = data["estimated_total_aed"]
        assert isinstance(cost, dict)
        assert cost == {"min": 6500, "max": 6500}
        assert data["government_fee_breakdown_aed"]["regular_total"] == 6500
        assert data["examination_service_target_working_days"] == 20
        assert data["opposition_period_days"] == 30

    @pytest.mark.asyncio
    async def test_trademark_sme_discount(self) -> None:
        normal = await ip_tools.trademark_registration(is_sme=False)
        sme = await ip_tools.trademark_registration(is_sme=True)
        n = normal["data"]
        s = sme["data"]
        assert isinstance(n, dict)
        assert isinstance(s, dict)
        assert s["estimated_total_aed"]["min"] < n["estimated_total_aed"]["min"]
        assert s["sme_discount_applied_pct"] == 50

    @pytest.mark.asyncio
    async def test_trademark_expedited_adds_2250(self) -> None:
        result = await ip_tools.trademark_registration(expedited=True)
        data = result["data"]
        assert isinstance(data, dict)
        # AED 2,250 expedited examination replaces the AED 750 regular fee.
        assert data["estimated_total_aed"]["min"] == 8000
        assert data["expedited_examination_surcharge_aed"] == 1500
        assert data["expedited_examination"] is True

    @pytest.mark.asyncio
    async def test_authority_is_moet(self) -> None:
        result = await ip_tools.trademark_registration()
        data = result["data"]
        assert isinstance(data, dict)
        authority = data["authority"]
        assert isinstance(authority, dict)
        assert authority["short_name"] == "MOET"

    @pytest.mark.asyncio
    async def test_ip_protection_trademark(self) -> None:
        result = await ip_tools.ip_protection(ip_type="trademark")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["ip_type"] == "trademark"

    @pytest.mark.asyncio
    async def test_new_unitary_gcc_patent_filings_are_unavailable(self) -> None:
        result = await ip_tools.ip_protection(ip_type="patent")
        data = result["data"]
        assert isinstance(data, dict)
        gcc = data["details"]["gcc_patent"]
        assert gcc["new_unitary_gcc_applications_accepted"] is False
        assert gcc["unitary_filing_stopped_on"] == "2021-01-06"
        assert "UAE national route" in gcc["uae_filing_note"]
        assert ip_tools.KNOWLEDGE.knowledge_date == "2026-09-05"

    @pytest.mark.asyncio
    async def test_ip_protection_invalid_type(self) -> None:
        result = await ip_tools.ip_protection(ip_type="design")
        assert result["success"] is False


class TestHalal:
    @pytest.mark.asyncio
    async def test_halal_certification_authority_is_moiat(self) -> None:
        result = await halal_tools.halal_certification()
        data = result["data"]
        assert isinstance(data, dict)
        authority = data["authority"]
        assert isinstance(authority, dict)
        assert authority["short_name"] == "MOIAT"
        assert "ESMA" in authority["absorbed"]

    @pytest.mark.asyncio
    async def test_halal_filter_by_product(self) -> None:
        result = await halal_tools.halal_certification(product_category="food")
        data = result["data"]
        assert isinstance(data, dict)
        products = data["products_requiring_certification"]
        assert isinstance(products, list)
        assert len(products) >= 1

    @pytest.mark.asyncio
    async def test_halal_standards_count(self) -> None:
        result = await halal_tools.halal_certification()
        data = result["data"]
        assert isinstance(data, dict)
        standards = data["standards"]
        assert isinstance(standards, list)
        assert len(standards) == 4  # 2055-1, 2055-2, 2055-4, UAE.S 993

    @pytest.mark.asyncio
    async def test_moiat_requirements_fees(self) -> None:
        result = await halal_tools.moiat_requirements()
        data = result["data"]
        assert isinstance(data, dict)
        hcb = data["hcb_registration"]
        assert isinstance(hcb, dict)
        assert hcb["total_aed"] == 2000


class TestCreateApps:
    @pytest.mark.asyncio
    async def test_championship_returns_prize_pool(self) -> None:
        result = await createapps_tools.createapps_championship()
        data = result["data"]
        assert isinstance(data, dict)
        championship = data["championship"]
        assert isinstance(championship, dict)
        assert championship["prize_pool_usd"] == 720000

    @pytest.mark.asyncio
    async def test_championship_4_categories(self) -> None:
        result = await createapps_tools.createapps_championship()
        data = result["data"]
        assert isinstance(data, dict)
        championship = data["championship"]
        assert isinstance(championship, dict)
        categories = championship["categories"]
        assert isinstance(categories, list)
        assert len(categories) == 4
        for cat in categories:
            assert cat["winner_prize_usd"] == 150000

    @pytest.mark.asyncio
    async def test_cycle_3_structured_timeline(self) -> None:
        result = await createapps_tools.createapps_championship()
        data = result["data"]
        assert isinstance(data, dict)
        championship = data["championship"]
        assert isinstance(championship, dict)
        key_dates = championship["cycle_3_timeline"]
        assert isinstance(key_dates, dict)
        assert key_dates["registration_close"] == "2025-12-28"
        assert key_dates["finalists_announced"] == "2026-04-14"
        assert key_dates["finals"] == "2026-10-07"

    @pytest.mark.asyncio
    async def test_cycle_is_ongoing_but_registration_is_closed(self) -> None:
        result = await createapps_tools.createapps_championship()
        data = result["data"]
        assert isinstance(data, dict)
        championship = data["championship"]
        assert isinstance(championship, dict)
        assert "ongoing" in championship["cycle_status"].lower()
        assert championship["current_cycle"]["status"] == "ongoing_finalist_phase"
        assert championship["current_cycle"]["registration_status"] == "closed"
        assert "next_cycle" not in championship
        assert "stale FAQ" in championship["official_page_consistency_note"]

    @pytest.mark.asyncio
    async def test_submission_guide_includes_evaluation_criteria(self) -> None:
        result = await createapps_tools.submission_guide()
        data = result["data"]
        assert isinstance(data, dict)
        guide = data["submission_guide"]
        assert isinstance(guide, dict)
        criteria = guide["evaluation_criteria"]
        assert isinstance(criteria, list)
        assert len(criteria) >= 3


class TestKnowledgeRegistration:
    def test_three_features_register(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.createapps import tools as ct
        from mcp_dubai.biz.halal import tools as ht
        from mcp_dubai.biz.ip_trademark import tools as it

        importlib.reload(it)
        importlib.reload(ht)
        importlib.reload(ct)

        registry = get_knowledge_registry()
        assert registry.get("ip_trademark") is not None
        assert registry.get("halal") is not None
        assert registry.get("createapps") is not None
