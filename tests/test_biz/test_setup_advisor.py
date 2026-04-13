"""Tests for the headline biz/* setup_advisor feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.setup_advisor import tools


class TestSetupAdvisorHappyPaths:
    @pytest.mark.asyncio
    async def test_local_trade_forces_mainland(self) -> None:
        result = await tools.setup_advisor(
            activity="restaurant",
            budget_aed=50000,
            needs_local_trade=True,
            needs_visa=True,
            visa_count=2,
            industry="fb",
        )
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "mainland"
        reasoning = data["reasoning"]
        assert isinstance(reasoning, list)
        assert any("DET" in r for r in reasoning)

    @pytest.mark.asyncio
    async def test_no_visa_low_budget_offshore(self) -> None:
        result = await tools.setup_advisor(
            activity="holding company for european assets",
            budget_aed=10000,
            needs_visa=False,
            industry="general",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "offshore"

    @pytest.mark.asyncio
    async def test_low_budget_steers_to_cheap_free_zone(self) -> None:
        result = await tools.setup_advisor(
            activity="general consulting",
            budget_aed=15000,
            needs_visa=True,
            industry="consulting",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "free_zone"
        candidates = data["candidate_free_zones"]
        assert isinstance(candidates, list)
        assert "IFZA" in candidates
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("Meydan" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_fintech_premium_routes_to_difc_innovation(self) -> None:
        result = await tools.setup_advisor(
            activity="b2b fintech tooling",
            budget_aed=40000,
            needs_visa=True,
            visa_count=3,
            industry="fintech",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "free_zone"
        candidates = data["candidate_free_zones"]
        assert isinstance(candidates, list)
        assert any("DIFC" in c for c in candidates)
        # Must surface the Innovation Licence restrictions explicitly.
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("DFSA" in w or "regulated" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_crypto_goes_to_vara_path(self) -> None:
        result = await tools.setup_advisor(
            activity="crypto exchange",
            budget_aed=100000,
            needs_visa=True,
            industry="crypto",
        )
        data = result["data"]
        assert isinstance(data, dict)
        reasoning = data["reasoning"]
        assert isinstance(reasoning, list)
        assert any("VARA" in r for r in reasoning)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("crypto" in w.lower() or "VARA" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_saas_surfaces_qfzp_warning(self) -> None:
        """SaaS is NOT a Qualifying Activity. setup_advisor must say so."""
        result = await tools.setup_advisor(
            activity="b2b saas",
            budget_aed=25000,
            needs_visa=True,
            industry="saas",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "free_zone"
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("QFZP" in w or "Qualifying Activity" in w for w in warnings)
        assert any("9%" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_default_path_is_free_zone(self) -> None:
        result = await tools.setup_advisor(
            activity="trading company",
            budget_aed=30000,
            needs_visa=True,
            industry="trading",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["jurisdiction"] == "free_zone"


class TestSetupAdvisorEnvelope:
    @pytest.mark.asyncio
    async def test_returns_knowledge_metadata(self) -> None:
        result = await tools.setup_advisor(
            activity="test",
            budget_aed=20000,
            needs_visa=True,
        )
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["volatility"] == "high"
        assert knowledge["verify_at"] == "https://invest.dubai.ae"
        assert knowledge["knowledge_date"] == "2026-04-13"
        assert "disclaimer" in knowledge

    @pytest.mark.asyncio
    async def test_always_returns_next_steps(self) -> None:
        result = await tools.setup_advisor(
            activity="random",
            budget_aed=20000,
        )
        data = result["data"]
        assert isinstance(data, dict)
        next_steps = data["next_steps"]
        assert isinstance(next_steps, list)
        assert len(next_steps) >= 3
        # The UAE Pass step is universally important.
        assert any("UAE Pass" in step for step in next_steps)

    @pytest.mark.asyncio
    async def test_always_returns_cost_range(self) -> None:
        result = await tools.setup_advisor(
            activity="random",
            budget_aed=20000,
        )
        data = result["data"]
        assert isinstance(data, dict)
        cost = data["estimated_setup_cost_aed"]
        assert isinstance(cost, dict)
        assert "min" in cost
        assert "max" in cost
        assert cost["min"] < cost["max"]


class TestSetupAdvisorValidation:
    @pytest.mark.asyncio
    async def test_negative_budget_returns_error(self) -> None:
        result = await tools.setup_advisor(activity="x", budget_aed=-1)
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, str)
        assert "budget" in error

    @pytest.mark.asyncio
    async def test_negative_visa_count_returns_error(self) -> None:
        result = await tools.setup_advisor(activity="x", budget_aed=20000, visa_count=-1)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_industry_returns_error(self) -> None:
        result = await tools.setup_advisor(
            activity="x", budget_aed=20000, industry="aerospace_defense"
        )
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, str)
        assert "industry" in error


class TestSetupAdvisorDiscovery:
    def test_registers_with_discovery(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.setup_advisor import server as sa_server

        importlib.reload(sa_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("setup_advisor")}
        assert names == {"setup_advisor"}

    def test_registers_knowledge(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.setup_advisor import tools as sa_tools

        importlib.reload(sa_tools)
        registry = get_knowledge_registry()
        meta = registry.get("setup_advisor")
        assert meta is not None
        assert meta.knowledge_date == "2026-04-13"
        assert meta.volatility == "high"

    def test_recommend_for_setup_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.setup_advisor import server as sa_server

        importlib.reload(sa_server)
        results = get_tool_discovery().recommend(
            "where should i incorporate my saas company in dubai", top_k=3
        )
        assert results
        assert results[0].name == "setup_advisor"
