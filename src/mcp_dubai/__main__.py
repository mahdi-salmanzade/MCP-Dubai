"""Entry point for `python -m mcp_dubai` and the `mcp-dubai` console script."""

from __future__ import annotations

import logging
import os


def _configure_logging() -> None:
    level_name = os.getenv("MCP_DUBAI_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    # HTTPX logs complete request URLs at INFO, including WAQI's query token.
    # The shared helper also runs on direct package imports for mounted use.
    from mcp_dubai._shared.http_client import protect_http_dependency_logging

    protect_http_dependency_logging()


def main() -> None:
    """Run the MCP-Dubai server over stdio."""
    _configure_logging()
    from mcp_dubai.server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
