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

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    mcp: FastMCP


try:
    __version__ = _pkg_version("mcp-dubai")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

__author__ = "Mahdi Salmanzade"
__organization__ = "CLRT Studio (https://clrtstudio.com)"

__all__ = ["mcp", "__version__", "__author__", "__organization__"]


def __getattr__(name: str) -> object:
    """Load the root server only when the package-level ``mcp`` export is requested."""
    if name != "mcp":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from mcp_dubai.server import mcp as root_mcp

    # Cache the resolved export so repeated attribute access does not repeat
    # module lookup. Importing helpers such as mcp_dubai._shared.schemas stays
    # lightweight and no longer constructs all mounted feature servers.
    globals()[name] = root_mcp
    return root_mcp
