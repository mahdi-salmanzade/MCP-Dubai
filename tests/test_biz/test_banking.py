"""Tests for the banking biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.banking import tools


class TestListBanks:
    @pytest.mark.asyncio
    async def test_returns_all_banks(self) -> None:
        result = await tools.list_banks()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 14
        ids = {b["id"] for b in data["banks"]}  # type: ignore[union-attr, index]
        assert "wio" in ids
        assert "mashreq_neobiz" in ids
        assert "fab" in ids
        assert "hsbc" in ids


class TestBankDetails:
    @pytest.mark.asyncio
    async def test_wio_details(self) -> None:
        result = await tools.bank_details("wio")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["name"] == "Wio Business"
        assert data["onboarding_days_min"] == 1
        assert data["onboarding_days_max"] == 3

    @pytest.mark.asyncio
    async def test_unknown_bank_returns_error(self) -> None:
        result = await tools.bank_details("not_a_bank")
        assert result["success"] is False


class TestBankRecommendation:
    @pytest.mark.asyncio
    async def test_speed_priority_returns_digital_banks(self) -> None:
        result = await tools.bank_recommendation(speed_priority=True, limit=3)
        data = result["data"]
        assert isinstance(data, dict)
        banks = data["banks"]
        assert isinstance(banks, list)
        # Wio should be in the top 3 for speed priority.
        ids = {b["id"] for b in banks}
        assert "wio" in ids

    @pytest.mark.asyncio
    async def test_min_balance_filter(self) -> None:
        result = await tools.bank_recommendation(budget_min_balance_aed=20000, limit=20)
        data = result["data"]
        assert isinstance(data, dict)
        banks = data["banks"]
        assert isinstance(banks, list)
        for bank in banks:
            min_bal = bank.get("min_balance_aed") or 0
            assert min_bal <= 20000

    @pytest.mark.asyncio
    async def test_crypto_industry_triggers_warning(self) -> None:
        result = await tools.bank_recommendation(industry="crypto")
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("crypto" in w.lower() or "high-risk" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_tier_filter_digital(self) -> None:
        result = await tools.bank_recommendation(tier="digital", limit=10)
        data = result["data"]
        assert isinstance(data, dict)
        banks = data["banks"]
        assert isinstance(banks, list)
        for bank in banks:
            assert bank["tier"] == "digital"

    @pytest.mark.asyncio
    async def test_invalid_industry_returns_error(self) -> None:
        result = await tools.bank_recommendation(industry="space_mining")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_excludes_liv_retail_only(self) -> None:
        result = await tools.bank_recommendation(limit=20)
        data = result["data"]
        assert isinstance(data, dict)
        banks = data["banks"]
        assert isinstance(banks, list)
        ids = {b["id"] for b in banks}
        assert "liv" not in ids


class TestDulEligibility:
    @pytest.mark.asyncio
    async def test_emirates_nbd_dmcc_eligible(self) -> None:
        result = await tools.dul_eligibility(bank_id="emirates_nbd", free_zone="DMCC")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["eligible"] is True
        assert data["bank_status"] == "participating"
        assert data["zone_status"] == "participating"

    @pytest.mark.asyncio
    async def test_wio_not_participating(self) -> None:
        result = await tools.dul_eligibility(bank_id="wio")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["bank_status"] == "not_participating"
        assert data["eligible"] is False

    @pytest.mark.asyncio
    async def test_summary_lists_participants(self) -> None:
        result = await tools.dul_eligibility()
        data = result["data"]
        assert isinstance(data, dict)
        summary = data["dul_summary"]
        assert isinstance(summary, dict)
        participating = summary["participating_banks"]
        assert isinstance(participating, list)
        assert "Emirates NBD" in participating
        assert "ruya" in participating


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.list_banks()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["volatility"] == "medium"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.banking import tools as banking_tools

        importlib.reload(banking_tools)
        meta = get_knowledge_registry().get("banking")
        assert meta is not None
