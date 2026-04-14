"""
MCP-Dubai: An MCP server for Dubai and UAE public APIs and business knowledge.

Usage:
    # As a stdio MCP server (default)
    python -m mcp_dubai

    # Via uvx
    uvx mcp-dubai

    # In Claude Desktop config:
    {
        "mcpServers": {
            "dubai": {
                "command": "uvx",
                "args": ["mcp-dubai"]
            }
        }
    }

See README.md for the full tool catalogue and Dubai Pulse credential setup.
"""

from mcp_dubai._shared.constants import PACKAGE_VERSION
from mcp_dubai.server import mcp

__version__ = PACKAGE_VERSION
__author__ = "Mahdi Salmanzade"

__all__ = ["mcp", "__version__", "__author__"]
