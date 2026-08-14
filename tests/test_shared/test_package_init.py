"""Tests for the lightweight package import and lazy root-server export."""

from __future__ import annotations

import subprocess
import sys


def test_package_level_mcp_export_is_lazy_and_backwards_compatible() -> None:
    code = """
import sys
import mcp_dubai

assert "mcp_dubai.server" not in sys.modules
assert mcp_dubai.__version__

from mcp_dubai import mcp

assert "mcp_dubai.server" in sys.modules
assert mcp.name == "mcp-dubai"
assert mcp_dubai.mcp is mcp
"""
    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
