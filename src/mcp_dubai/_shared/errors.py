"""
Shared error-response helpers for upstream failures.

Data tools that call external upstreams should wrap their HTTP calls in
try/except and route failures through these helpers instead of letting
exceptions escape to the MCP client. This mirrors the credential-missing
pattern used by Dubai Pulse tools (see dld/tools.py) so every failure mode
reaches the client as a structured ToolResponse.fail() envelope.
"""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse


def upstream_error_response(
    error: Exception,
    *,
    status: str | None = None,
    verify_at: str | None = None,
) -> dict[str, Any]:
    """
    Convert an upstream exception to a ToolResponse.fail() dict.

    Classifies common upstream failures so the MCP client can render a
    useful message instead of a raw traceback. Cloudflare bot-protection
    pages and 403/503 responses are surfaced as `upstream_blocked`, rate
    limits as `rate_limited`, and everything else as `upstream_error`.
    """
    reason = str(error)
    resolved_status = status or _classify(error, reason)

    payload: dict[str, str] = {
        "status": resolved_status,
        "reason": reason[:400],
    }
    if verify_at:
        payload["verify_at"] = verify_at

    return ToolResponse[dict[str, Any]].fail(error=payload).model_dump()


def cloudflare_blocked_response(
    endpoint: str,
    *,
    verify_at: str | None = None,
) -> dict[str, Any]:
    """Return a structured error for an endpoint known to be Cloudflare-blocked."""
    payload: dict[str, str] = {
        "status": "upstream_blocked",
        "reason": (
            f"Endpoint {endpoint} is behind Cloudflare bot protection. "
            "This tool cannot fetch data until the upstream removes the block."
        ),
    }
    if verify_at:
        payload["verify_at"] = verify_at
    return ToolResponse[dict[str, Any]].fail(error=payload).model_dump()


def _classify(error: Exception, reason: str) -> str:
    if isinstance(error, RateLimitError):
        return "rate_limited"
    if isinstance(error, HttpClientError):
        status_code = getattr(error, "status_code", None)
        if status_code in (403, 503) or "Just a moment" in reason:
            return "upstream_blocked"
        return "upstream_error"
    if "timeout" in reason.lower() or "timed out" in reason.lower():
        return "upstream_timeout"
    return "upstream_error"
