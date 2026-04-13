"""
WAQI token availability check (Pattern 2 reused for a single env var).

Tools call `waqi_availability()` instead of crashing when the token is
missing. The structured response slots into ToolResponse.fail() the same
way DubaiPulseAuth does.
"""

from __future__ import annotations

import os
from typing import Any


def get_waqi_token() -> str | None:
    """Read MCP_DUBAI_WAQI_TOKEN from the environment, lazily."""
    token = os.getenv("MCP_DUBAI_WAQI_TOKEN")
    return token if token else None


def waqi_availability() -> dict[str, Any]:
    """Return a structured availability descriptor for graceful degradation."""
    if get_waqi_token() is not None:
        return {"status": "ready"}
    return {
        "status": "token_missing",
        "reason": (
            "WAQI air quality token is not configured. Set MCP_DUBAI_WAQI_TOKEN. "
            "Get a free token at https://aqicn.org/data-platform/token/."
        ),
        "docs": ("https://github.com/mahdi-salmanzade/MCP-Dubai#air-quality-waqi"),
    }
