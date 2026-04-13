"""
Pytest configuration and shared fixtures.

The most important fixture is `reset_singletons`, used by every test that
monkeypatches Dubai Pulse env vars or registers tools with ToolDiscovery.
Without it, a previous test's cached state leaks into the next test.

Test rules:
- @respx.mock on every test that touches httpx
- reset singletons after monkeypatching env
- always assert on the route, not just the return value
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from mcp_dubai._shared.auth import reset_dubai_pulse_auth
from mcp_dubai._shared.discovery import reset_tool_discovery
from mcp_dubai._shared.knowledge import reset_knowledge_registry


@pytest.fixture(autouse=True)
def reset_singletons() -> Iterator[None]:
    """
    Reset all module-level singletons before AND after every test.

    Auto-used so individual tests do not have to remember the import gymnastics.
    Covers DubaiPulseAuth, ToolDiscovery, and KnowledgeRegistry.
    """
    reset_dubai_pulse_auth()
    reset_tool_discovery()
    reset_knowledge_registry()
    yield
    reset_dubai_pulse_auth()
    reset_tool_discovery()
    reset_knowledge_registry()


@pytest.fixture
def clean_dubai_pulse_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop Dubai Pulse env vars for credential-missing tests."""
    monkeypatch.delenv("MCP_DUBAI_PULSE_CLIENT_ID", raising=False)
    monkeypatch.delenv("MCP_DUBAI_PULSE_CLIENT_SECRET", raising=False)


@pytest.fixture
def configured_dubai_pulse_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set fake Dubai Pulse env vars for happy-path tests."""
    monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "test-client-secret")
