"""
Shared error-response helpers for upstream failures.

Data tools that call external upstreams should wrap their HTTP calls in
try/except and route failures through these helpers instead of letting
exceptions escape to the MCP client. This mirrors the credential-missing
pattern used by Dubai Pulse tools (see dld/tools.py) so every failure mode
reaches the client as a structured ToolResponse.fail() envelope.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse

_HTTP_FORBIDDEN_RE = re.compile(r"\bHTTP\s+403\b", re.IGNORECASE)
_BOT_BLOCK_MARKERS = ("cloudflare", "just a moment")


def is_upstream_blocked(reason: str, *, status_code: int | None = None) -> bool:
    """Return whether an error has concrete HTTP 403 or bot-block evidence."""
    normalized_reason = reason.casefold()
    return (
        status_code == 403
        or _HTTP_FORBIDDEN_RE.search(reason) is not None
        or any(marker in normalized_reason for marker in _BOT_BLOCK_MARKERS)
    )


def now_iso() -> str:
    """UTC timestamp in the form tools should stamp on live responses."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def upstream_error_response(
    error: Exception,
    *,
    status: str | None = None,
    verify_at: str | None = None,
    source: str | None = None,
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """
    Convert an upstream exception to a ToolResponse.fail() dict.

    Classifies common upstream failures so the MCP client can render a
    useful message instead of a raw traceback. HTTP 403 and responses with
    Cloudflare bot-protection evidence are surfaced as `upstream_blocked`,
    rate limits as `rate_limited`, and everything else as `upstream_error`.
    """
    reason = str(error)
    resolved_status = status or _classify(error, reason)

    payload: dict[str, str] = {
        "status": resolved_status,
        "reason": reason[:400],
    }
    if verify_at:
        payload["verify_at"] = verify_at

    return (
        ToolResponse[dict[str, Any]]
        .fail(error=payload, source=source, retrieved_at=retrieved_at or now_iso())
        .model_dump()
    )


def cloudflare_blocked_response(
    endpoint: str,
    *,
    verify_at: str | None = None,
    source: str | None = None,
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
    return (
        ToolResponse[dict[str, Any]]
        .fail(error=payload, source=source or endpoint, retrieved_at=now_iso())
        .model_dump()
    )


def _classify(error: Exception, reason: str) -> str:
    if isinstance(error, RateLimitError):
        return "rate_limited"
    status_code = getattr(error, "status_code", None)
    if is_upstream_blocked(reason, status_code=status_code):
        return "upstream_blocked"
    if isinstance(error, HttpClientError):
        return "upstream_error"
    if "timeout" in reason.lower() or "timed out" in reason.lower():
        return "upstream_timeout"
    return "upstream_error"
