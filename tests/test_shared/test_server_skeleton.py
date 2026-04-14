"""Smoke tests for the Phase 1 root server skeleton."""

from __future__ import annotations

from mcp_dubai.server import (
    get_knowledge_status,
    get_upstream_status,
    list_features,
    mcp,
    recommend_tools,
)


class TestServerExists:
    def test_root_mcp_is_named(self) -> None:
        assert mcp.name == "mcp-dubai"


class TestMetaTools:
    def test_recommend_tools_returns_list(self) -> None:
        result = recommend_tools(query="prayer times", top_k=3)
        assert isinstance(result, list)
        # Phase 1: no features mounted yet, so the catalogue is empty.
        assert result == []

    def test_list_features_returns_list(self) -> None:
        result = list_features()
        assert isinstance(result, list)
        assert result == []

    def test_get_knowledge_status_returns_envelope(self) -> None:
        result = get_knowledge_status()
        assert isinstance(result, dict)
        assert "knowledge_date" in result
        assert "domains" in result
        assert "total_domains" in result

    def test_knowledge_status_empty_when_no_biz_registered(self) -> None:
        # Phase 1 baseline: no biz/* features mounted, so the registry is empty.
        # The autouse `reset_singletons` fixture wipes any registrations from
        # previous tests, so we see a clean slate here.
        result = get_knowledge_status()
        assert result["total_domains"] == 0
        assert result["domains"] == {}

    def test_get_upstream_status_returns_bootstrapped_envelope(self) -> None:
        from mcp_dubai._shared.health import reset_upstream_registry

        reset_upstream_registry()
        result = get_upstream_status()
        assert isinstance(result, dict)
        assert "upstreams" in result
        assert "summary" in result
        names = {u["name"] for u in result["upstreams"]}
        assert {"al_adhan", "cbuae_exchange", "cbuae_base_rate", "fcsc_ckan"}.issubset(names)
        summary = result["summary"]
        assert summary["total"] == len(result["upstreams"])

    def test_knowledge_status_reflects_registered_domains(self) -> None:
        from mcp_dubai._shared.knowledge import register_domain_knowledge
        from mcp_dubai._shared.schemas import KnowledgeMetadata

        register_domain_knowledge(
            "test_domain",
            KnowledgeMetadata(
                knowledge_date="2026-04-13",
                volatility="high",
                verify_at="https://example.ae",
            ),
        )
        result = get_knowledge_status()
        assert result["total_domains"] == 1
        domains = result["domains"]
        assert isinstance(domains, dict)
        assert "test_domain" in domains
        info = domains["test_domain"]
        assert info["volatility"] == "high"
        assert info["verify_at"] == "https://example.ae"


class TestMetaToolDiscoveryRegistration:
    """
    Regression tests for the four root meta tools being findable via
    BM25 `recommend_tools`. The autouse `reset_tool_discovery` fixture
    wipes the registry before every test, so we reload `server` to
    re-run its module-level `register_many` call.
    """

    def _reload_server(self) -> None:
        import importlib

        from mcp_dubai import server as root_server

        importlib.reload(root_server)

    def test_all_five_meta_tools_are_registered(self) -> None:
        from mcp_dubai._shared.discovery import TIER_META, get_tool_discovery

        self._reload_server()
        registered = {m.name: m for m in get_tool_discovery().list_all() if m.feature == "meta"}
        assert set(registered.keys()) == {
            "recommend_tools",
            "list_features",
            "get_knowledge_status",
            "about",
            "get_upstream_status",
        }
        for meta in registered.values():
            assert meta.tier == TIER_META

    def test_navigational_queries_route_to_meta_tools(self) -> None:
        """The whole point of registering meta tools: BM25 surfaces them
        for the questions they answer."""
        from mcp_dubai._shared.discovery import get_tool_discovery

        self._reload_server()
        disc = get_tool_discovery()

        cases = {
            "what tools are available": "list_features",
            "list all features": "list_features",
            "how fresh is the knowledge": "get_knowledge_status",
            "when was this verified": "get_knowledge_status",
            "which version am i running": "about",
            "which endpoints are down": "get_upstream_status",
            "upstream health": "get_upstream_status",
        }
        for query, expected in cases.items():
            results = disc.recommend(query, top_k=3)
            assert results, f"no recommendations for {query!r}"
            assert results[0].name == expected, (
                f"query {query!r} routed to {results[0].name}, expected {expected}"
            )
