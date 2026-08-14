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
        assert not any("shareholder" in w.lower() for w in warnings)

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


class TestOpenFinance:
    @pytest.mark.asyncio
    async def test_list_banks_surfaces_open_finance_block(self) -> None:
        result = await tools.list_banks()
        data = result["data"]
        assert isinstance(data, dict)
        open_finance = data["open_finance"]
        assert isinstance(open_finance, dict)
        assert open_finance["name"] == "Al Tareq"
        assert open_finance["operator"] == "Nebras Open Finance"
        live = {b["bank_id"]: b for b in open_finance["live_banks"]}
        assert "cbd" in live
        assert live["fab"]["live_date"] == "2025-12-30"
        assert live["adib"]["live_date"] == "2026-01-19"
        law = open_finance["central_bank_law"]
        assert isinstance(law, dict)
        assert law["compliance_deadline"] == "2026-09-16"

    @pytest.mark.asyncio
    async def test_recent_entrants_are_not_matrix_entries(self) -> None:
        result = await tools.list_banks()
        data = result["data"]
        assert isinstance(data, dict)
        matrix_ids = {b["id"] for b in data["banks"]}  # type: ignore[union-attr, index]
        entrants = data["recent_entrants_2026"]
        assert isinstance(entrants, dict)
        entrant_ids = {e["id"] for e in entrants["entrants"]}
        assert entrant_ids == {"tabby", "mal", "revolut", "alaan"}
        assert entrant_ids.isdisjoint(matrix_ids)

    @pytest.mark.asyncio
    async def test_regulators_note_mentions_cma(self) -> None:
        result = await tools.list_banks()
        data = result["data"]
        assert isinstance(data, dict)
        regulators = data["regulators"]
        assert isinstance(regulators, dict)
        note = str(regulators["note"])
        assert "Capital Market Authority" in note
        assert "2026-01-01" in note


class TestDulEligibility:
    @pytest.mark.asyncio
    async def test_emirates_nbd_is_integrated_and_dmcc_is_covered(self) -> None:
        result = await tools.dul_eligibility(bank_id="emirates_nbd", free_zone="DMCC")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["eligible"] is True
        assert data["bank_status"] == "integrated"
        assert data["zone_status"] == "covered_if_dubai"

    @pytest.mark.asyncio
    async def test_wio_is_not_in_dated_official_bank_list(self) -> None:
        result = await tools.dul_eligibility(bank_id="wio")
        data = result["data"]
        assert isinstance(data, dict)
        assert data["bank_status"] == "not_listed_in_official_announcement"
        assert data["eligible"] is False

    @pytest.mark.asyncio
    async def test_summary_lists_integrated_banks_and_caveat(self) -> None:
        result = await tools.dul_eligibility()
        data = result["data"]
        assert isinstance(data, dict)
        summary = data["dul_summary"]
        assert isinstance(summary, dict)
        integrated = summary["integrated_banks"]
        assert isinstance(integrated, list)
        assert "Emirates NBD" in integrated
        assert "ruya" in integrated
        assert summary["average_onboarding_days"] == 5
        assert "All businesses in Dubai" in summary["coverage"]
        assert "not a service-level guarantee" in summary["caveat"]
        assert any("mediaoffice.ae" in url for url in summary["source_urls"])


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.list_banks()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-08-14"
        assert knowledge["previous_knowledge_date"] == "2026-07-02"
        assert "unsupported claim" in knowledge["last_refresh_scope"]
        assert knowledge["volatility"] == "medium"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.banking import tools as banking_tools

        importlib.reload(banking_tools)
        meta = get_knowledge_registry().get("banking")
        assert meta is not None
