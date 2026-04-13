"""
MCP-Dubai root server.

Phase 1 skeleton: just the root FastMCP instance and the meta-tools
(`recommend_tools`, `get_knowledge_status`). Feature mounts are added in
Phase 2 (Tier 0 features) and Phase 4 (Tier 1 Dubai Pulse features), once
those features exist.

The auto-mount block at the bottom of this file uses the FastMCP 3.x API:

    main = FastMCP("mcp-dubai")
    main.mount(child_server)                # tools available unprefixed
    main.mount(child_server, namespace="x") # tools prefixed as "x_<tool>"

For MCP-Dubai we mount without a namespace because every feature has
already chosen unique tool names (e.g., `prayer_times_for`, `cbuae_exchange_rates`).
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from mcp_dubai._shared import (
    KNOWLEDGE_DATE,
    ToolMeta,
    get_knowledge_registry,
    get_tool_discovery,
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Root server
# ----------------------------------------------------------------------------
mcp: FastMCP = FastMCP(
    "mcp-dubai",
    instructions=(
        "MCP-Dubai gives AI agents access to Dubai and UAE public APIs and "
        "curated business knowledge. Call `recommend_tools` with a natural-"
        "language query to find the right tool, or `list_features` to see "
        "what is available. Business knowledge tools (setup, visas, tax, "
        "banking, funding) return a `knowledge_date` field so you can see "
        "when each domain was last verified. Call `get_knowledge_status` to "
        "see the freshness of every domain at once."
    ),
)


# ----------------------------------------------------------------------------
# Phase 2: Tier 0 features (no auth)
# Imports are intentionally below the root `mcp` definition because each
# feature mounts itself onto the root server. ruff E402 is suppressed.
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# Phase 3: Tier 2 business knowledge features (curated, no external API)
# ----------------------------------------------------------------------------
from mcp_dubai.agents.arabic_writer.server import mcp as arabic_writer_mcp  # noqa: E402
from mcp_dubai.agents.data_analyst.server import mcp as data_analyst_mcp  # noqa: E402
from mcp_dubai.biz.banking.server import mcp as banking_mcp  # noqa: E402
from mcp_dubai.biz.compliance.server import mcp as compliance_mcp  # noqa: E402
from mcp_dubai.biz.createapps.server import mcp as createapps_mcp  # noqa: E402
from mcp_dubai.biz.dcde.server import mcp as dcde_mcp  # noqa: E402
from mcp_dubai.biz.events.server import mcp as events_mcp  # noqa: E402
from mcp_dubai.biz.founder_essentials.server import mcp as founder_essentials_mcp  # noqa: E402
from mcp_dubai.biz.free_zones.server import mcp as free_zones_mcp  # noqa: E402
from mcp_dubai.biz.funding.server import mcp as funding_mcp  # noqa: E402
from mcp_dubai.biz.gov_portals.server import mcp as gov_portals_mcp  # noqa: E402
from mcp_dubai.biz.halal.server import mcp as halal_mcp  # noqa: E402
from mcp_dubai.biz.ip_trademark.server import mcp as ip_trademark_mcp  # noqa: E402
from mcp_dubai.biz.parkin.server import mcp as parkin_mcp  # noqa: E402
from mcp_dubai.biz.setup_advisor.server import mcp as setup_advisor_mcp  # noqa: E402
from mcp_dubai.biz.tax_compliance.server import mcp as tax_compliance_mcp  # noqa: E402
from mcp_dubai.biz.visas.server import mcp as visas_mcp  # noqa: E402
from mcp_dubai.data.air_quality.server import mcp as air_quality_mcp  # noqa: E402
from mcp_dubai.data.al_adhan.server import mcp as al_adhan_mcp  # noqa: E402
from mcp_dubai.data.aviation_weather.server import mcp as aviation_weather_mcp  # noqa: E402
from mcp_dubai.data.cbuae.server import mcp as cbuae_mcp  # noqa: E402
from mcp_dubai.data.dld.server import mcp as dld_mcp  # noqa: E402
from mcp_dubai.data.fcsc_ckan.server import mcp as fcsc_ckan_mcp  # noqa: E402
from mcp_dubai.data.holidays.server import mcp as holidays_mcp  # noqa: E402
from mcp_dubai.data.khda.server import mcp as khda_mcp  # noqa: E402
from mcp_dubai.data.osm_overpass.server import mcp as osm_overpass_mcp  # noqa: E402
from mcp_dubai.data.quran_cloud.server import mcp as quran_cloud_mcp  # noqa: E402
from mcp_dubai.data.rta.server import mcp as rta_mcp  # noqa: E402

mcp.mount(air_quality_mcp)
mcp.mount(al_adhan_mcp)
mcp.mount(aviation_weather_mcp)
mcp.mount(cbuae_mcp)
mcp.mount(dld_mcp)
mcp.mount(fcsc_ckan_mcp)
mcp.mount(holidays_mcp)
mcp.mount(khda_mcp)
mcp.mount(osm_overpass_mcp)
mcp.mount(quran_cloud_mcp)
mcp.mount(rta_mcp)
mcp.mount(banking_mcp)
mcp.mount(compliance_mcp)
mcp.mount(createapps_mcp)
mcp.mount(dcde_mcp)
mcp.mount(events_mcp)
mcp.mount(founder_essentials_mcp)
mcp.mount(free_zones_mcp)
mcp.mount(funding_mcp)
mcp.mount(gov_portals_mcp)
mcp.mount(halal_mcp)
mcp.mount(ip_trademark_mcp)
mcp.mount(parkin_mcp)
mcp.mount(setup_advisor_mcp)
mcp.mount(tax_compliance_mcp)
mcp.mount(visas_mcp)
mcp.mount(arabic_writer_mcp)
mcp.mount(data_analyst_mcp)


# ----------------------------------------------------------------------------
# Phase 4: Tier 1 features (Dubai Pulse OAuth)
# ----------------------------------------------------------------------------
# from mcp_dubai.data.dld.server import mcp as dld
# ...
# mcp.mount(dld)


# ----------------------------------------------------------------------------
# Phase 3: Tier 2 business knowledge features
# ----------------------------------------------------------------------------
# from mcp_dubai.biz.setup_advisor.server import mcp as setup_advisor
# ...
# mcp.mount(setup_advisor)


# ----------------------------------------------------------------------------
# Tier 3: meta-tools (defined inline on the root server)
# ----------------------------------------------------------------------------


@mcp.tool
def recommend_tools(query: str, top_k: int = 5) -> list[dict[str, object]]:
    """
    Recommend MCP-Dubai tools for a natural-language query.

    Uses BM25 over every registered tool's name, description, and tags so
    the LLM can find the right tool without scanning the full catalogue.

    Args:
        query: What you are trying to do, in plain English or Arabic.
        top_k: Maximum number of recommendations to return (default 5).

    Returns:
        A list of tool descriptors ranked by relevance, each containing
        `name`, `description`, `feature`, `tier`, and `requires_auth`.
    """
    discovery = get_tool_discovery()
    matches: list[ToolMeta] = discovery.recommend(query, top_k=top_k)
    return [
        {
            "name": match.name,
            "description": match.description,
            "feature": match.feature,
            "tier": match.tier,
            "requires_auth": match.requires_auth,
            "tags": match.tags,
        }
        for match in matches
    ]


@mcp.tool
def list_features() -> list[dict[str, object]]:
    """
    List every registered MCP-Dubai feature with its tool count and tier.

    Returns:
        One entry per feature, sorted by tier then name. Each entry has
        `feature`, `tier`, `requires_auth`, `tool_count`, and `tools`.
    """
    discovery = get_tool_discovery()
    grouped: dict[str, dict[str, object]] = {}
    for tool in discovery.list_all():
        if tool.feature not in grouped:
            grouped[tool.feature] = {
                "feature": tool.feature,
                "tier": tool.tier,
                "requires_auth": tool.requires_auth,
                "tools": [],
            }
        tools_list = grouped[tool.feature]["tools"]
        if isinstance(tools_list, list):
            tools_list.append(tool.name)

    out: list[dict[str, object]] = []
    for entry in grouped.values():
        tools_list = entry["tools"]
        tool_count = len(tools_list) if isinstance(tools_list, list) else 0
        entry["tool_count"] = tool_count
        out.append(entry)

    def _sort_key(entry: dict[str, object]) -> tuple[int, str]:
        tier_value = entry["tier"]
        feature_value = entry["feature"]
        return (
            tier_value if isinstance(tier_value, int) else 99,
            feature_value if isinstance(feature_value, str) else "",
        )

    out.sort(key=_sort_key)
    return out


@mcp.tool
def get_knowledge_status() -> dict[str, object]:
    """
    Return freshness status of every registered business knowledge domain.

    Each `biz/*` feature registers its KnowledgeMetadata at import time via
    `register_domain_knowledge`. This meta-tool reads from that registry, so
    bumping a single per-domain `KNOWLEDGE` constant flows through here
    automatically. The project-wide default date is in `_shared/constants.py`.

    Returns:
        Dict with `knowledge_date` (project default), `total_domains`, and
        `domains` mapping each registered domain to its date, volatility,
        verify_at URL, and disclaimer.
    """
    registry = get_knowledge_registry()
    domains = registry.all()
    return {
        "knowledge_date": KNOWLEDGE_DATE,
        "total_domains": len(domains),
        "domains": {
            name: {
                "knowledge_date": meta.knowledge_date,
                "volatility": meta.volatility,
                "verify_at": meta.verify_at,
                "disclaimer": meta.disclaimer,
            }
            for name, meta in sorted(domains.items())
        },
    }
