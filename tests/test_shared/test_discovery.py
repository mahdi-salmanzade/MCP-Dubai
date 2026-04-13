"""Tests for ToolDiscovery BM25 ranking."""

from __future__ import annotations

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    TIER_DUBAI_PULSE,
    TIER_OPEN,
    ToolDiscovery,
    ToolMeta,
)


def _build_sample_discovery() -> ToolDiscovery:
    """Build a discovery instance with a representative MCP-Dubai tool catalogue."""
    discovery = ToolDiscovery()
    discovery.register_many(
        [
            ToolMeta(
                name="prayer_times_for",
                description="Get prayer times for a city or coordinates",
                feature="al_adhan",
                tier=TIER_OPEN,
                tags=["prayer", "salat", "fajr", "maghrib", "islamic", "muslim"],
            ),
            ToolMeta(
                name="qibla_direction",
                description="Get Qibla compass bearing to Mecca",
                feature="al_adhan",
                tier=TIER_OPEN,
                tags=["qibla", "mecca", "compass"],
            ),
            ToolMeta(
                name="cbuae_exchange_rates",
                description="Central Bank of UAE exchange rates",
                feature="cbuae",
                tier=TIER_OPEN,
                tags=["currency", "fx", "forex", "rate"],
            ),
            ToolMeta(
                name="dld_search_transactions",
                description="Search Dubai Land Department real estate transactions",
                feature="dld",
                tier=TIER_DUBAI_PULSE,
                requires_auth=True,
                tags=["real estate", "property", "dubai", "land", "transaction"],
            ),
            ToolMeta(
                name="setup_advisor",
                description="Recommend mainland or free zone for business setup in Dubai",
                feature="setup_advisor",
                tier=TIER_BIZ,
                tags=["business", "setup", "license", "free zone", "mainland", "founder"],
            ),
        ]
    )
    return discovery


class TestRecommend:
    def test_recommends_prayer_times_for_islamic_query(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("when is fajr prayer in dubai", top_k=3)
        assert len(results) >= 1
        assert results[0].name == "prayer_times_for"

    def test_recommends_qibla_for_mecca_query(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("compass direction to mecca", top_k=3)
        assert results[0].name == "qibla_direction"

    def test_recommends_cbuae_for_exchange_rate_query(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("aed to usd currency rate", top_k=3)
        assert results[0].name == "cbuae_exchange_rates"

    def test_recommends_setup_advisor_for_founder_query(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("best free zone for a saas founder business setup", top_k=3)
        assert results[0].name == "setup_advisor"

    def test_recommends_dld_for_real_estate_query(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("dubai property transactions", top_k=3)
        assert results[0].name == "dld_search_transactions"

    def test_top_k_limits_results(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("dubai", top_k=2)
        assert len(results) <= 2

    def test_query_with_no_matches_returns_empty(self) -> None:
        discovery = _build_sample_discovery()
        results = discovery.recommend("xyzzy frobnicate quux", top_k=5)
        assert results == []

    def test_empty_discovery_returns_empty(self) -> None:
        discovery = ToolDiscovery()
        results = discovery.recommend("anything", top_k=5)
        assert results == []


class TestFilters:
    def test_get_by_feature(self) -> None:
        discovery = _build_sample_discovery()
        al_adhan_tools = discovery.get_by_feature("al_adhan")
        assert len(al_adhan_tools) == 2
        assert {t.name for t in al_adhan_tools} == {
            "prayer_times_for",
            "qibla_direction",
        }

    def test_get_by_tier(self) -> None:
        discovery = _build_sample_discovery()
        tier_0 = discovery.get_by_tier(TIER_OPEN)
        assert len(tier_0) == 3  # prayer, qibla, cbuae

    def test_list_all(self) -> None:
        discovery = _build_sample_discovery()
        assert len(discovery.list_all()) == 5

    def test_clear(self) -> None:
        discovery = _build_sample_discovery()
        discovery.clear()
        assert discovery.list_all() == []
