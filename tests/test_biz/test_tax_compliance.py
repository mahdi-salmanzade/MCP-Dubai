"""Tests for the tax_compliance biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.tax_compliance import tools


class TestCorporateTaxEstimate:
    @pytest.mark.asyncio
    async def test_below_threshold_zero_tax(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=300000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_corporate_tax_aed"] == 0

    @pytest.mark.asyncio
    async def test_above_threshold_charges_9_percent(self) -> None:
        # AED 1,000,000 - AED 375,000 = AED 625,000 taxable, * 9% = AED 56,250.
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=1000000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_corporate_tax_aed"] == 56250
        assert data["effective_rate_pct"] == round(56250 / 1000000 * 100, 2)

    @pytest.mark.asyncio
    async def test_qfzp_qualifying_split(self) -> None:
        # AED 1,000,000 income, 80% qualifying:
        # Above threshold: 625,000
        # Qualifying: 500,000 -> 0%
        # Non-qualifying: 125,000 -> 9% = 11,250
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=1000000,
            is_free_zone=True,
            qfzp_qualifying_pct=80,
            industry="trading",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_corporate_tax_aed"] == 11250

    @pytest.mark.asyncio
    async def test_saas_qfzp_warning(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=2000000,
            is_free_zone=True,
            qfzp_qualifying_pct=100,
            industry="saas",
        )
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("SaaS" in w and "229" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_small_business_relief_warning(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=2500000)
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("Small Business Relief" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_negative_income_returns_error(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=-1)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_qfzp_pct_returns_error(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=1000000, qfzp_qualifying_pct=150
        )
        assert result["success"] is False


class TestVatFilingCalendar:
    @pytest.mark.asyncio
    async def test_below_voluntary_threshold(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "not_required"

    @pytest.mark.asyncio
    async def test_voluntary_band(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=250000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "voluntary_eligible"

    @pytest.mark.asyncio
    async def test_mandatory_threshold(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=500000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "mandatory"
        assert data["filing_frequency"] == "quarterly"

    @pytest.mark.asyncio
    async def test_large_business_files_monthly(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=200000000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["filing_frequency"] == "monthly"


class TestQfzpCheck:
    @pytest.mark.asyncio
    async def test_saas_not_qualifying(self) -> None:
        result = await tools.qfzp_check(industry="saas", is_free_zone=True)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "not_qualifying"
        assert "229" in data["reason"]

    @pytest.mark.asyncio
    async def test_mainland_not_eligible(self) -> None:
        result = await tools.qfzp_check(industry="trading", is_free_zone=False)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "not_eligible"

    @pytest.mark.asyncio
    async def test_trading_potentially_qualifying(self) -> None:
        result = await tools.qfzp_check(industry="trading", is_free_zone=True)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "potentially_qualifying"


class TestEsrStatus:
    @pytest.mark.asyncio
    async def test_returns_dead_status(self) -> None:
        result = await tools.esr_status()
        data = result["data"]
        assert isinstance(data, dict)
        assert "DEAD" in data["status"]

    def test_esr_queries_route_to_single_surviving_tool(self) -> None:
        """After the esr_check removal there must be exactly one ESR tool and
        discovery must surface it for the common natural-language phrasings."""
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.compliance import server as compliance_server
        from mcp_dubai.biz.tax_compliance import server as tax_server

        importlib.reload(compliance_server)
        importlib.reload(tax_server)

        disc = get_tool_discovery()
        all_esr = [m for m in disc.list_all() if "esr" in m.name.lower()]
        assert [m.name for m in all_esr] == ["esr_status"]

        for query in (
            "do i need to file ESR",
            "economic substance regulations",
            "is ESR still required",
        ):
            results = disc.recommend(query, top_k=3)
            assert results, f"no recommendations for {query!r}"
            assert results[0].name == "esr_status", (
                f"query {query!r} did not route to esr_status; top was {results[0].name}"
            )


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=500000)
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["volatility"] == "high"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.tax_compliance import tools as tax_tools

        importlib.reload(tax_tools)
        meta = get_knowledge_registry().get("tax_compliance")
        assert meta is not None
