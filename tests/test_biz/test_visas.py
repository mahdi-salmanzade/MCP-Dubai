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
        assert "property_investor_2yr" in ids
        assert "visa_on_arrival" in ids


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
    async def test_property_investor_2yr_july_2026_rules(self) -> None:
        result = await tools.visa_details("property_investor_2yr")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["id"] == "property_investor_2yr"
        assert data["duration_years"] == 2
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        # Sole owners: AED 750,000 minimum removed in April 2026.
        assert any("750,000" in e and "removed" in e for e in eligibility)
        # Co-owners: AED 400,000 registered share each.
        assert any("400,000" in e for e in eligibility)
        # No formal decree: thresholds flagged as subject to confirmation.
        change_note = data["change_note"]
        assert isinstance(change_note, str)
        assert "subject to confirmation" in change_note
        # GDRFA single-channel process note (GDRFA-DLD MoU of 11 April 2026).
        process_note = data["process_note"]
        assert isinstance(process_note, str)
        assert "GDRFA" in process_note

    @pytest.mark.asyncio
    async def test_golden_real_estate_offplan_note_is_caveated(self) -> None:
        result = await tools.visa_details("golden_investor_real_estate")
        data = result["data"]
        assert isinstance(data, dict)
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        assert any("AED 2 million" in e for e in eligibility)
        # The Oqood / 50% payment rule removal must stay flagged, not stated as fact.
        note = data["unverified_note"]
        assert isinstance(note, str)
        assert "UNCONFIRMED" in note
        assert "Oqood" in note
        assert "GDRFA" in str(data["process_note"])

    @pytest.mark.asyncio
    async def test_visa_on_arrival_2026_expansion(self) -> None:
        result = await tools.visa_details("visa_on_arrival")
        data = result["data"]
        assert isinstance(data, dict)
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        expansion = [e for e in eligibility if "25 June 2026" in e]
        assert len(expansion) == 1
        for nationality in (
            "Indonesia",
            "Vietnam",
            "Thailand",
            "Philippines",
            "Kenya",
            "South Africa",
        ):
            assert nationality in expansion[0]
        assert data["cost_aed_min"] == 100
        assert data["cost_aed_max"] == 250
        assert data["overstay_fine_aed_per_day"] == 50

    @pytest.mark.asyncio
    async def test_employment_visa_mohre_and_ai_screening_notes(self) -> None:
        result = await tools.visa_details("employment")
        data = result["data"]
        assert isinstance(data, dict)
        work_permit_note = data["work_permit_system_note"]
        assert isinstance(work_permit_note, str)
        assert "13 permit types" in work_permit_note
        ai_note = data["ai_screening_note"]
        assert isinstance(ai_note, str)
        assert "May 2026" in ai_note

    @pytest.mark.asyncio
    async def test_virtual_working_six_month_bank_statements(self) -> None:
        result = await tools.visa_details("virtual_working")
        data = result["data"]
        assert isinstance(data, dict)
        eligibility = data["eligibility"]
        assert isinstance(eligibility, list)
        assert any("Six consecutive months" in e for e in eligibility)
        # Income floor stays at the officially published USD 3,500.
        assert any("USD 3,500" in e for e in eligibility)
        # Higher-threshold claims stay flagged as unconfirmed.
        note = data["unverified_note"]
        assert isinstance(note, str)
        assert "UNCONFIRMED" in note

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
        assert "property_investor_2yr" in ids

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
    async def test_property_below_2m_points_to_2yr_visa(self) -> None:
        result = await tools.golden_visa_check(real_estate_value_aed=900000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["any_eligible"] is False
        not_eligible = data["not_eligible"]
        assert isinstance(not_eligible, list)
        assert any("2-year Property Investor Visa" in n["criterion"] for n in not_eligible)

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
        assert knowledge["knowledge_date"] == "2026-07-02"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.visas import tools as visas_tools

        importlib.reload(visas_tools)
        meta = get_knowledge_registry().get("visas")
        assert meta is not None
        assert meta.knowledge_date == "2026-07-02"


class TestCuratedPackSections:
    def test_myth_buster_lifetime_golden_visa_denied(self) -> None:
        myths = tools._DATA["myth_busters"]
        assert isinstance(myths, list)
        lifetime = [m for m in myths if "AED 100,000" in m["claim"]]
        assert len(lifetime) == 1
        assert lifetime[0]["status"] == "officially_denied"
        assert "ICP" in lifetime[0]["note"]
        assert lifetime[0]["source_urls"]

    def test_gcc_grand_tours_stays_provisional(self) -> None:
        upcoming = tools._DATA["upcoming"]
        assert isinstance(upcoming, list)
        grand_tours = [u for u in upcoming if u["id"] == "gcc_grand_tours"]
        assert len(grand_tours) == 1
        assert grand_tours[0]["status"] == "expected_not_live"
        assert "Q4 2026" in grand_tours[0]["note"]
