"""Tests for the passive upstream health registry and meta tool."""

from __future__ import annotations

import pytest

from mcp_dubai._shared.health import (
    UpstreamRegistry,
    get_upstream_registry,
    mark_failure,
    mark_success,
    register_upstream,
    reset_upstream_registry,
)


class TestUpstreamRegistry:
    def test_register_is_idempotent(self) -> None:
        reg = UpstreamRegistry()
        reg.register("x", "example.com", requires_auth=False)
        reg.register("x", "example.com", requires_auth=True)
        snap = reg.snapshot()
        assert len(snap) == 1
        assert snap[0]["requires_auth"] is True

    def test_register_preserves_existing_status_on_re_register(self) -> None:
        """Second register should not overwrite a status that has moved past `unknown`."""
        reg = UpstreamRegistry()
        reg.register("x", "example.com", initial_status="blocked", initial_reason="cf")
        reg.register("x", "example.com", initial_status="unknown")
        snap = reg.snapshot()
        assert snap[0]["status"] == "blocked"
        assert snap[0]["reason"] == "cf"

    def test_mark_success_flips_status_to_working(self) -> None:
        reg = UpstreamRegistry()
        reg.register("x", "example.com", initial_status="unknown")
        reg.mark_success("x")
        snap = reg.snapshot()[0]
        assert snap["status"] == "working"
        assert snap["reason"] is None
        assert snap["success_count"] == 1
        assert snap["last_success"] is not None

    def test_mark_failure_with_cloudflare_flips_to_blocked(self) -> None:
        reg = UpstreamRegistry()
        reg.register("x", "example.com")
        reg.mark_failure("x", "HTTP 403 from example.com: Just a moment...")
        snap = reg.snapshot()[0]
        assert snap["status"] == "blocked"
        assert "Just a moment" in str(snap["reason"])

    def test_mark_failure_three_times_degrades(self) -> None:
        reg = UpstreamRegistry()
        reg.register("x", "example.com", initial_status="working")
        reg.mark_failure("x", "network down")
        reg.mark_failure("x", "network down")
        reg.mark_failure("x", "network down")
        snap = reg.snapshot()[0]
        assert snap["status"] == "degraded"
        assert snap["failure_count"] == 3

    def test_mark_unknown_upstream_is_silent(self) -> None:
        """mark_success / mark_failure must not raise for unregistered names."""
        reg = UpstreamRegistry()
        reg.mark_success("never_registered")
        reg.mark_failure("never_registered", "reason")

    def test_summary_counts_by_bucket(self) -> None:
        reg = UpstreamRegistry()
        reg.register("a", "a.com", initial_status="working")
        reg.register("b", "b.com", initial_status="blocked")
        reg.register("c", "c.com", initial_status="blocked")
        reg.register("d", "d.com", initial_status="credentials_missing")
        summary = reg.summary()
        assert summary["working"] == 1
        assert summary["blocked"] == 2
        assert summary["credentials_missing"] == 1
        assert summary["total"] == 4


class TestBootstrap:
    def test_singleton_bootstraps_known_upstreams(self) -> None:
        reset_upstream_registry()
        snap = get_upstream_registry().snapshot()
        names = {u["name"] for u in snap}
        assert {
            "al_adhan",
            "cbuae_exchange",
            "cbuae_base_rate",
            "fcsc_ckan",
            "dubai_pulse",
            "waqi",
            "khda_static",
        }.issubset(names)

    def test_cbuae_base_rate_is_pre_marked_blocked(self) -> None:
        reset_upstream_registry()
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["cbuae_base_rate"]["status"] == "blocked"
        assert "Cloudflare" in str(snap["cbuae_base_rate"]["reason"])

    def test_fcsc_is_pre_marked_blocked(self) -> None:
        reset_upstream_registry()
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["fcsc_ckan"]["status"] == "blocked"

    def test_dubai_pulse_credentials_missing_without_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MCP_DUBAI_PULSE_CLIENT_ID", raising=False)
        monkeypatch.delenv("MCP_DUBAI_PULSE_CLIENT_SECRET", raising=False)
        reset_upstream_registry()
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["dubai_pulse"]["status"] == "credentials_missing"
        assert snap["dubai_pulse"]["requires_auth"] is True

    def test_dubai_pulse_working_when_env_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_ID", "id")
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "secret")
        reset_upstream_registry()
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["dubai_pulse"]["status"] == "working"

    def test_waqi_credentials_missing_without_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_DUBAI_WAQI_TOKEN", raising=False)
        reset_upstream_registry()
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["waqi"]["status"] == "credentials_missing"


class TestModuleHelpers:
    def test_register_upstream_module_shortcut(self) -> None:
        reset_upstream_registry()
        register_upstream("custom", "custom.example", initial_status="working")
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["custom"]["status"] == "working"

    def test_mark_success_module_shortcut(self) -> None:
        reset_upstream_registry()
        register_upstream("custom", "custom.example")
        mark_success("custom")
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["custom"]["status"] == "working"
        assert snap["custom"]["success_count"] == 1

    def test_mark_failure_module_shortcut(self) -> None:
        reset_upstream_registry()
        register_upstream("custom", "custom.example", initial_status="working")
        mark_failure("custom", "HTTP 403: Just a moment...")
        snap = {u["name"]: u for u in get_upstream_registry().snapshot()}
        assert snap["custom"]["status"] == "blocked"
