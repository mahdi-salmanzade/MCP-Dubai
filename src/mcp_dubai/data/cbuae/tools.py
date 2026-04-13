"""Pure CBUAE tool functions."""

from __future__ import annotations

from datetime import date

import httpx

from mcp_dubai._shared.errors import upstream_error_response
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.cbuae.client import CbuaeClient

CBUAE_VERIFY_URL = "https://www.centralbank.ae/en/forex-eibor/exchange-rates/"


def _parse_iso_date(value: str | None) -> date | None:
    if value is None or value == "":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date: {value}") from exc


async def cbuae_exchange_rates(date_str: str | None = None) -> dict[str, object]:
    """
    Get CBUAE exchange rates for today or a historical date.

    Returns ~75 currencies vs AED. Updated Mon to Fri at ~18:00 GST. The
    underlying CBUAE endpoint is undocumented but verified live.
    """
    client = CbuaeClient()
    target = _parse_iso_date(date_str)

    try:
        if target is None:
            rates = await client.get_exchange_rates_today()
        else:
            rates = await client.get_exchange_rates_for_date(target)
    except (HttpClientError, httpx.HTTPError) as exc:
        return upstream_error_response(exc, verify_at=CBUAE_VERIFY_URL)

    if not rates:
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
                }
            )
            .model_dump()
        )

    if target is None:
        return {
            "date": "today",
            "currency_count": len(rates),
            "rates": rates,
            "source": "CBUAE Umbraco endpoint, undocumented",
            "warning": (
                "These endpoints are not officially documented. They have been "
                "verified live but could break without notice."
            ),
        }

    return {
        "date": target.isoformat(),
        "currency_count": len(rates),
        "rates": rates,
        "source": "CBUAE Umbraco endpoint, undocumented",
    }


async def cbuae_base_rate() -> dict[str, object]:
    """
    Get the current CBUAE base rate (a percentage).

    Updated each business day around 11:00 GST, excluding Saturdays.
    """
    client = CbuaeClient()
    try:
        result = await client.get_key_interest_rate()
    except (HttpClientError, httpx.HTTPError) as exc:
        return upstream_error_response(
            exc,
            verify_at="https://www.centralbank.ae/en/monetary-policy/base-rate/",
        )
    return {
        "base_rate_percent": result["base_rate_percent"],
        "source": "CBUAE Umbraco endpoint, undocumented",
        "raw_excerpt": result.get("raw", ""),
    }
