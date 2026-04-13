"""Tests for the visas biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.visas import tools


class TestListVisaTypes:
    @pytest.mark.asyncio
    async def test_returns_all_visa_types(self) -> None:
        result = await tools.list_visa_types()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 10
        ids = {v["id"] for v in data["visas"]}  # type: ignore[union-attr, index]
        assert "investor_partner" in ids
        assert "golden_specialized_talent" in ids
        assert "green_freelancer" in ids
        assert "green_skilled_employee" in ids


class TestVisaDetails:
    @pytest.mark.asyncio
    async def test_lookup_green_skilled(self) -> None:
        result = await tools.visa_details("green_skilled_employee")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["id"] == "green_skilled_employee"
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        assert any("AED 15,000" in e for e in eligibility)

    @pytest.mark.asyncio
    async def test_green_freelancer_360k_two_year_rule(self) -> None:
        result = await tools.visa_details("green_freelancer")
        data = result["data"]
        assert isinstance(data, dict)
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        assert any("360,000" in e and "two years" in e for e in eligibility)

    @pytest.mark.asyncio
    async def test_golden_specialized_talent_30k_rule(self) -> None:
        result = await tools.visa_details("golden_specialized_talent")
        data = result["data"]
        assert isinstance(data, dict)
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        assert any("30,000" in e and "BASIC" in e for e in eligibility)

    @pytest.mark.asyncio
    async def test_unknown_id_returns_error(self) -> None:
        result = await tools.visa_details("not_a_visa")
        assert result["success"] is False


class TestVisaRecommend:
    @pytest.mark.asyncio
    async def test_founder_with_license(self) -> None:
        result = await tools.visa_recommend(profile="founder", has_uae_trade_license=True)
        data = result["data"]
        assert isinstance(data, dict)
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        ids = {c["id"] for c in candidates}
        assert "investor_partner" in ids

    @pytest.mark.asyncio
    async def test_high_salary_founder_gets_golden(self) -> None:
        result = await tools.visa_recommend(
            profile="founder",
            monthly_salary_aed=35000,
            has_uae_trade_license=True,
        )
        data = result["data"]
        assert isinstance(data, dict)
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        ids = {c["id"] for c in candidates}
        assert "golden_specialized_talent" in ids

    @pytest.mark.asyncio
    async def test_employee_15k_salary_gets_green(self) -> None:
        result = await tools.visa_recommend(
            profile="salaried_employee",
            monthly_salary_aed=15000,
            has_uae_employer=True,
        )
        data = result["data"]
        assert isinstance(data, dict)
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        ids = {c["id"] for c in candidates}
        assert "green_skilled_employee" in ids
        assert "employment" in ids

    @pytest.mark.asyncio
    async def test_freelancer_recommendations(self) -> None:
        result = await tools.visa_recommend(profile="freelancer", annual_income_aed=200000)
        data = result["data"]
        assert isinstance(data, dict)
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        ids = {c["id"] for c in candidates}
        assert "freelance_permit" in ids
        assert "green_freelancer" in ids

    @pytest.mark.asyncio
    async def test_real_estate_investor(self) -> None:
        result = await tools.visa_recommend(profile="real_estate_investor")
        data = result["data"]
        assert isinstance(data, dict)
        candidates = data["candidates"]
        assert isinstance(candidates, list)
        ids = {c["id"] for c in candidates}
        assert "golden_investor_real_estate" in ids

    @pytest.mark.asyncio
    async def test_retiree_under_55(self) -> None:
        result = await tools.visa_recommend(profile="retiree", age=50)
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("55" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_invalid_profile_returns_error(self) -> None:
        result = await tools.visa_recommend(profile="alien")
        assert result["success"] is False


class TestGoldenVisaCheck:
    @pytest.mark.asyncio
    async def test_high_salary_eligible(self) -> None:
        result = await tools.golden_visa_check(monthly_salary_aed=35000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["any_eligible"] is True
        eligible = data["eligible"]
        assert isinstance(eligible, list)
        cats = {e["category"] for e in eligible}
        assert "specialized_talent" in cats

    @pytest.mark.asyncio
    async def test_low_salary_not_eligible_with_specific_reason(self) -> None:
        result = await tools.golden_visa_check(monthly_salary_aed=20000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["any_eligible"] is False
        not_eligible = data["not_eligible"]
        assert isinstance(not_eligible, list)
        assert any("BASIC" in n["criterion"] for n in not_eligible)

    @pytest.mark.asyncio
    async def test_property_eligible(self) -> None:
        result = await tools.golden_visa_check(real_estate_value_aed=2500000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["any_eligible"] is True

    @pytest.mark.asyncio
    async def test_project_eligible(self) -> None:
        result = await tools.golden_visa_check(project_value_aed=750000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["any_eligible"] is True


class TestKnowledgeRegistration:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.list_visa_types()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-04-13"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.visas import tools as visas_tools

        importlib.reload(visas_tools)
        meta = get_knowledge_registry().get("visas")
        assert meta is not None
        assert meta.knowledge_date == "2026-04-13"
