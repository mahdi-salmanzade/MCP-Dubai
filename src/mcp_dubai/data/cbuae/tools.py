"""Pure CBUAE tool functions."""

from __future__ import annotations

from datetime import date

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.cbuae.client import CbuaeClient

CBUAE_VERIFY_URL = "https://www.centralbank.ae/en/forex-eibor/exchange-rates/"
_SOURCE = "centralbank.ae"
_UPSTREAM_EXCHANGE = "cbuae_exchange"
_UPSTREAM_BASE_RATE = "cbuae_base_rate"


def _parse_iso_date(value: str | None) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(value)


async def cbuae_exchange_rates(date_str: str | None = None) -> dict[str, object]:
    """
    Get CBUAE exchange rates for today or a historical date.

    Returns ~75 currencies vs AED. Updated Mon to Fri at ~18:00 GST. The
    underlying CBUAE endpoint is undocumented but verified live.
    """
    try:
        target = _parse_iso_date(date_str)
    except ValueError as exc:
        return (
            ToolResponse[dict[str, object]]
            .fail(
                error=f"Invalid ISO date: {date_str!r} ({exc})",
                source=_SOURCE,
                retrieved_at=now_iso(),
            )
            .model_dump()
        )

    client = CbuaeClient()

    try:
        if target is None:
            rates = await client.get_exchange_rates_today()
        else:
            rates = await client.get_exchange_rates_for_date(target)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM_EXCHANGE, str(exc))
        return upstream_error_response(
            exc,
            verify_at=CBUAE_VERIFY_URL,
            source=_SOURCE,
        )

    if not rates:
        mark_failure(_UPSTREAM_EXCHANGE, "parse_error: zero rates returned")
        return (
            ToolResponse[dict[str, object]]
            .fail(
                error={
                    "status": "parse_error",
                    "reason": (
                        "Upstream returned zero exchange rates. The CBUAE HTML "
                        "structure may have changed or the endpoint may be blocked."
                    ),
                    "verify_at": CBUAE_VERIFY_URL,
                },
                source=_SOURCE,
                retrieved_at=now_iso(),
            )
            .model_dump()
        )

    mark_success(_UPSTREAM_EXCHANGE)

    if target is None:
        data: dict[str, object] = {
            "date": "today",
            "currency_count": len(rates),
            "rates": rates,
            "warning": (
                "These endpoints are not officially documented. They have been "
                "verified live but could break without notice."
            ),
        }
    else:
        data = {
            "date": target.isoformat(),
            "currency_count": len(rates),
            "rates": rates,
        }

    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


async def cbuae_base_rate() -> dict[str, object]:
    """
    Get the current CBUAE base rate (a percentage).

    Updated each business day around 11:00 GST, excluding Saturdays.
    """
    client = CbuaeClient()
    try:
        result = await client.get_key_interest_rate()
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM_BASE_RATE, str(exc))
        return upstream_error_response(
            exc,
            verify_at="https://www.centralbank.ae/en/monetary-policy/base-rate/",
            source=_SOURCE,
        )

    mark_success(_UPSTREAM_BASE_RATE)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "base_rate_percent": result["base_rate_percent"],
                "raw_excerpt": result.get("raw", ""),
            },
            source=_SOURCE,
            retrieved_at=now_iso(),
        )
        .model_dump()
    )
