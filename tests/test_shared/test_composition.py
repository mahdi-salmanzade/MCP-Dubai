"""Production-composition invariants that must run in a fresh interpreter."""

from __future__ import annotations

import json
import subprocess
import sys


def test_fresh_process_registers_the_complete_catalogue() -> None:
    """Catch fixture-masked registration loss and documentation count drift."""
    code = """
import asyncio
import json

from mcp_dubai._shared.discovery import get_tool_discovery
from mcp_dubai.server import get_knowledge_status, list_features, mcp


async def main():
    protocol_names = sorted(tool.name for tool in await mcp.list_tools())
    discovery_names = sorted(tool.name for tool in get_tool_discovery().list_all())
    print(json.dumps({
        "protocol_names": protocol_names,
        "discovery_names": discovery_names,
        "feature_count": len(list_features()),
        "knowledge_domain_count": get_knowledge_status()["total_domains"],
    }))


asyncio.run(main())
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip().splitlines()[-1])

    assert payload["protocol_names"] == payload["discovery_names"]
    assert len(payload["protocol_names"]) == 120
    assert payload["feature_count"] == 37
    assert payload["knowledge_domain_count"] == 19
