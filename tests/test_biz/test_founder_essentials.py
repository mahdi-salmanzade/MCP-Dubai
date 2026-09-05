"""Tests for the founder_essentials biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.founder_essentials import tools


class TestAttestationGuide:
    @pytest.mark.asyncio
    async def test_returns_5_step_chain(self) -> None:
        result = await tools.attestation_guide(document_type="degree")
        data = result["data"]
        assert isinstance(data, dict)
        chain = data["legalization_chain"]
        assert isinstance(chain, list)
        assert len(chain) == 5
        assert "Notarisation" in data["legalization_chain_note"]
        assert "UAE" in data["digital_attestation"]["scope"]
        assert "walk-in" not in data["tip"]

    @pytest.mark.asyncio
    async def test_uae_apostille_correction(self) -> None:
        result = await tools.attestation_guide()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["uae_apostille_member"] is False
        assert "official HCCH" in data["apostille_correction_note"]

    @pytest.mark.asyncio
    async def test_personal_vs_commercial_fee(self) -> None:
        personal = await tools.attestation_guide(document_type="personal")
        commercial = await tools.attestation_guide(document_type="commercial")
        p_data = personal["data"]
        c_data = commercial["data"]
        assert isinstance(p_data, dict)
        assert isinstance(c_data, dict)
        assert p_data["estimated_mofa_fee_aed"] == 150
        assert c_data["estimated_mofa_fee_aed"] == 2000

    @pytest.mark.asyncio
    async def test_invalid_document_type(self) -> None:
        result = await tools.attestation_guide(document_type="hieroglyph")
        assert result["success"] is False


class TestProServicesEstimate:
    @pytest.mark.asyncio
    async def test_low_volume_recommends_per_transaction(self) -> None:
        result = await tools.pro_services_estimate(visas_per_year=1, license_renewals_per_year=1)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["recommendation"] == "per_transaction"
        assert "Private-provider market estimate" in data["pricing_basis"]
        assert any("mohre.gov.ae" in url for url in data["source_urls"])

    @pytest.mark.asyncio
    async def test_high_volume_recommends_retainer(self) -> None:
        result = await tools.pro_services_estimate(visas_per_year=5, license_renewals_per_year=2)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["recommendation"] == "monthly_retainer"

    @pytest.mark.asyncio
    async def test_force_retainer(self) -> None:
        result = await tools.pro_services_estimate(visas_per_year=1, use_retainer=True)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["recommendation"] == "monthly_retainer"

    @pytest.mark.asyncio
    async def test_negative_visas_returns_error(self) -> None:
        result = await tools.pro_services_estimate(visas_per_year=-1)
        assert result["success"] is False


class TestLegalTranslationEstimate:
    @pytest.mark.asyncio
    async def test_basic_estimate(self) -> None:
        result = await tools.legal_translation_estimate(pages=5)
        data = result["data"]
        assert isinstance(data, dict)
        cost = data["estimated_cost_aed"]
        assert isinstance(cost, dict)
        assert cost["min"] == 250  # 5 pages * AED 50
        assert cost["max"] == 750  # 5 pages * AED 150
        assert "MOJ does not publish" in data["pricing_basis"]
        assert any("moj.gov.ae" in url for url in data["source_urls"])
        assert "receiving authority" in data["important"]

    @pytest.mark.asyncio
    async def test_same_day_uplift_applied(self) -> None:
        normal = await tools.legal_translation_estimate(pages=10)
        rush = await tools.legal_translation_estimate(pages=10, same_day=True)
        n = normal["data"]
        r = rush["data"]
        assert isinstance(n, dict)
        assert isinstance(r, dict)
        assert r["estimated_cost_aed"]["min"] > n["estimated_cost_aed"]["min"]

    @pytest.mark.asyncio
    async def test_zero_pages_returns_error(self) -> None:
        result = await tools.legal_translation_estimate(pages=0)
        assert result["success"] is False


class TestChamberOfCommerceInfo:
    @pytest.mark.asyncio
    async def test_returns_membership_tiers(self) -> None:
        result = await tools.chamber_of_commerce_info()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["annual_fee_aed_min"] == 50
        assert data["annual_fee_aed_max"] == 2200
        assert "subject to statutory exemptions" in data["mandatory_for"]
        categories = data["annual_fee_categories"]
        assert isinstance(categories, dict)
        assert categories["free_zone_companies_aed"] == 2200
        assert categories["simple_handicrafts_aed"] == 50
        assert any("membership-renewal" in url for url in data["source_urls"])

    @pytest.mark.asyncio
    async def test_certificate_of_origin_fee(self) -> None:
        result = await tools.chamber_of_commerce_info()
        data = result["data"]
        assert isinstance(data, dict)
        coo = data["certificate_of_origin"]
        assert isinstance(coo, dict)
        assert coo["fee_aed"] == 100


class TestSetupTimelineEstimate:
    @pytest.mark.asyncio
    async def test_returns_timelines(self) -> None:
        result = await tools.setup_timeline_estimate()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["mainland_setup_weeks_min"] == 2
        assert data["mainland_setup_weeks_max"] == 4
        assert data["bank_account_weeks_max"] == 16


class TestCommonFounderMistakes:
    @pytest.mark.asyncio
    async def test_returns_corrected_mistake_set(self) -> None:
        result = await tools.common_founder_mistakes()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 10
        mistakes = data["mistakes"]
        assert isinstance(mistakes, list)
        assert not any(m["id"] == "single_shareholder" for m in mistakes)
        local_trade = next(m for m in mistakes if m["id"] == "free_zone_mainland_invoice")
        assert "Resolution 11 of 2025" in local_trade["fix"]
        assert any("dlp.dubai.gov.ae" in url for url in local_trade["source_urls"])

    @pytest.mark.asyncio
    async def test_filter_by_category(self) -> None:
        result = await tools.common_founder_mistakes(category="bank")
        data = result["data"]
        assert isinstance(data, dict)
        mistakes = data["mistakes"]
        assert isinstance(mistakes, list)
        assert all(
            "bank" in str(m.get("title", "")).lower() or "bank" in str(m.get("id", "")).lower()
            for m in mistakes
        )

    @pytest.mark.asyncio
    async def test_each_mistake_has_fix(self) -> None:
        result = await tools.common_founder_mistakes()
        data = result["data"]
        assert isinstance(data, dict)
        mistakes = data["mistakes"]
        assert isinstance(mistakes, list)
        for m in mistakes:
            assert "fix" in m
            assert "impact" in m


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.attestation_guide()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-09-05"
        assert knowledge["previous_knowledge_date"] == "2026-08-14"
        assert "MoFA digital/courier" in knowledge["last_refresh_scope"]

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.founder_essentials import tools as fe_tools

        importlib.reload(fe_tools)
        meta = get_knowledge_registry().get("founder_essentials")
        assert meta is not None
