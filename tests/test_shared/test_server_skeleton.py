"""Smoke tests for the Phase 1 root server skeleton."""

from __future__ import annotations

from mcp_dubai.server import (
    get_knowledge_status,
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
