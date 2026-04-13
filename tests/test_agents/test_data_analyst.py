"""Tests for data_analyst agent."""

from __future__ import annotations

import pytest

from mcp_dubai.agents.data_analyst import tools


class TestPlanQuery:
    @pytest.mark.asyncio
    async def test_founder_setup_plan(self) -> None:
        result = await tools.plan_query(
            category="founder_setup",
            inputs={"budget_aed": 25000, "industry": "saas"},
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["category"] == "founder_setup"
        assert data["step_count"] == 6
        steps = data["steps"]
        assert isinstance(steps, list)
        tools_called = {s["tool"] for s in steps}
        assert "setup_advisor" in tools_called
        assert "compare_free_zones" in tools_called
        assert "common_founder_mistakes" in tools_called

    @pytest.mark.asyncio
    async def test_compliance_checkup_plan(self) -> None:
        result = await tools.plan_query(category="compliance_checkup")
        data = result["data"]
        assert isinstance(data, dict)
        steps = data["steps"]
        assert isinstance(steps, list)
        tools_called = {s["tool"] for s in steps}
        assert "esr_check" in tools_called
        assert "ubo_filing_guide" in tools_called

    @pytest.mark.asyncio
    async def test_relocation_plan(self) -> None:
        result = await tools.plan_query(category="relocation")
        data = result["data"]
        assert isinstance(data, dict)
        steps = data["steps"]
        assert isinstance(steps, list)
        tools_called = {s["tool"] for s in steps}
        assert "visa_recommend" in tools_called
        assert "khda_search_school" in tools_called
        assert "weather_uae_icao" in tools_called

    @pytest.mark.asyncio
    async def test_invalid_category(self) -> None:
        result = await tools.plan_query(category="quantum_computing")
        assert result["success"] is False


class TestListPlanCategories:
    @pytest.mark.asyncio
    async def test_lists_all_4_categories(self) -> None:
        result = await tools.list_plan_categories()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 4
        ids = {c["id"] for c in data["categories"]}  # type: ignore[union-attr]
        assert "founder_setup" in ids
        assert "compliance_checkup" in ids


class TestSynthesizeReport:
    @pytest.mark.asyncio
    async def test_basic_report(self) -> None:
        result = await tools.synthesize_report(
            title="Founder Setup Brief",
            sections=[
                {"heading": "Recommendation", "body": "Use IFZA."},
                {"heading": "Tax", "body": "9% above AED 375,000."},
            ],
        )
        data = result["data"]
        assert isinstance(data, dict)
        markdown = data["markdown"]
        assert isinstance(markdown, str)
        assert "# Founder Setup Brief" in markdown
        assert "## Recommendation" in markdown
        assert "## Tax" in markdown
        assert "## Knowledge freshness" in markdown

    @pytest.mark.asyncio
    async def test_report_includes_freshness_footer(self) -> None:
        # First force-register a domain so the freshness footer has something.
        from mcp_dubai._shared.knowledge import register_domain_knowledge
        from mcp_dubai._shared.schemas import KnowledgeMetadata

        register_domain_knowledge(
            "test_dom",
            KnowledgeMetadata(knowledge_date="2026-04-13", volatility="high"),
        )
        result = await tools.synthesize_report(title="X")
        data = result["data"]
        assert isinstance(data, dict)
        markdown = data["markdown"]
        assert isinstance(markdown, str)
        assert "test_dom" in markdown

    @pytest.mark.asyncio
    async def test_empty_title_returns_error(self) -> None:
        result = await tools.synthesize_report(title="")
        assert result["success"] is False


class TestAnalyzeSetupDecision:
    @pytest.mark.asyncio
    async def test_returns_6_step_plan(self) -> None:
        result = await tools.analyze_setup_decision(
            activity="b2b saas",
            budget_aed=25000,
            industry="saas",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["step_count"] == 6
        plan = data["plan"]
        assert isinstance(plan, list)
        # Step 3 must be qfzp_check (the SaaS warning is the most important step)
        assert plan[2]["tool"] == "qfzp_check"

    @pytest.mark.asyncio
    async def test_negative_budget_returns_error(self) -> None:
        result = await tools.analyze_setup_decision(activity="x", budget_aed=-1)
        assert result["success"] is False


class TestKnowledgeRegistration:
    def test_registers_with_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.agents.data_analyst import tools as da_tools

        importlib.reload(da_tools)
        meta = get_knowledge_registry().get("data_analyst")
        assert meta is not None
