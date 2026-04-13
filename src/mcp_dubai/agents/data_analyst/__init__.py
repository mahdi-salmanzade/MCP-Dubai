"""data_analyst: cross-tool queries, data synthesis, report generation."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "data_analyst",
    "description": (
        "Cross-tool queries and structured report generation. Plans "
        "multi-feature queries (free zones + visas + tax + banking) and "
        "produces founder-ready reports from MCP-Dubai's curated knowledge."
    ),
    "tier": 4,
    "requires_auth": False,
    "source_url": "https://github.com/mahdi-salmanzade/MCP-Dubai",
}
