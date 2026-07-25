"""
Tests for the read-only tool annotation middleware.

Every MCP-Dubai tool is a read-only lookup. Declaring that through MCP tool
annotations is what lets a client skip a confirmation prompt, so these are
behavioural guarantees, not cosmetics.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from mcp_dubai._shared.annotations import OPEN_WORLD_TOOLS
from mcp_dubai._shared.constants import PACKAGE_VERSION
from mcp_dubai.server import mcp


@pytest.mark.asyncio
async def test_every_tool_is_annotated_read_only() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

    assert tools, "server exposed no tools"
    missing = [t.name for t in tools if not t.annotations or t.annotations.readOnlyHint is not True]
    assert missing == [], f"tools without readOnlyHint=True: {missing}"


@pytest.mark.asyncio
async def test_every_tool_is_non_destructive_and_idempotent() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

    bad_destructive = [t.name for t in tools if t.annotations.destructiveHint is not False]
    bad_idempotent = [t.name for t in tools if t.annotations.idempotentHint is not True]
    assert bad_destructive == [], f"tools not marked non-destructive: {bad_destructive}"
    assert bad_idempotent == [], f"tools not marked idempotent: {bad_idempotent}"


@pytest.mark.asyncio
async def test_open_world_hint_distinguishes_live_upstreams_from_bundled_data() -> None:
    """A live API call is open-world; reading a bundled JSON pack is not."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
    by_name = {t.name: t for t in tools}

    # Live upstream calls.
    for name in ("uae_weather", "dfm_index", "makani_validate", "cbuae_exchange_rates"):
        assert by_name[name].annotations.openWorldHint is True, (
            f"{name} calls a live upstream and must be openWorldHint=True"
        )

    # Bundled data or pure computation.
    for name in ("uae_holidays", "corporate_tax_estimate", "list_visa_types", "recommend_tools"):
        assert by_name[name].annotations.openWorldHint is False, (
            f"{name} reads bundled data and must be openWorldHint=False"
        )


@pytest.mark.asyncio
async def test_open_world_set_contains_no_unknown_tool_names() -> None:
    """A rename would otherwise silently drop a tool back to closed-world."""
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}

    unknown = sorted(OPEN_WORLD_TOOLS - names)
    assert unknown == [], (
        f"OPEN_WORLD_TOOLS names tools that no longer exist: {unknown}. "
        "Update the set in _shared/annotations.py."
    )


@pytest.mark.asyncio
async def test_new_data_tools_are_deliberately_classified() -> None:
    """
    Guard against a new live-upstream tool defaulting to closed-world.

    Any tool whose name matches a known network-calling feature prefix must be
    listed in OPEN_WORLD_TOOLS, unless it is one of the documented exceptions
    that read bundled data.
    """
    bundled_exceptions = {
        "air_quality_dubai_stations",
        "khda_list_areas",
        "khda_list_curricula",
        "khda_search_school",
        "list_uae_weather_cities",
        "osm_list_categories",
        "rta_gtfs_static_url",
    }
    network_prefixes = (
        "air_quality_",
        "cbuae_",
        "currency_",
        "data_dubai_",
        "dfm_",
        "dld_",
        "fcsc_",
        "makani_",
        "osm_",
        "quran_",
        "rta_",
    )

    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}

    misclassified = sorted(
        n
        for n in names
        if n.startswith(network_prefixes)
        and n not in OPEN_WORLD_TOOLS
        and n not in bundled_exceptions
    )
    assert misclassified == [], (
        f"these tools look like live-upstream calls but are marked closed-world: "
        f"{misclassified}. Add them to OPEN_WORLD_TOOLS, or to the documented "
        "bundled-data exceptions if they do not touch the network."
    )


@pytest.mark.asyncio
async def test_server_info_reports_the_package_version() -> None:
    """Regression: serverInfo.version used to report FastMCP's own version."""
    async with Client(mcp) as client:
        info = client.initialize_result.serverInfo

    assert info.name == "mcp-dubai"
    assert info.version == PACKAGE_VERSION
