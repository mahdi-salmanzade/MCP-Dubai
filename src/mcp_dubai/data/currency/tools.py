"""Currency tool functions (keyless everyday conversion on an AED base)."""

from __future__ import annotations

import math
from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure as mark_upstream_failure
from mcp_dubai._shared.health import mark_success as mark_upstream_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.currency.client import CurrencyClient

_SOURCE = "open.er-api.com"
_UPSTREAM = "currency"
_VERIFY_AT = "https://www.exchangerate-api.com/docs/free"
_ATTRIBUTION = (
    "Rates by ExchangeRate-API (open.er-api.com), free tier, AED-base everyday "
    "rates; for official central-bank rates use cbuae tools."
)


def _fail(error: str | dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _error_type(payload: dict[str, Any]) -> str:
    return str(payload.get("error-type") or "unknown-error")


async def currency_rates(base: str = "AED") -> dict[str, object]:
    """
    Get everyday exchange rates for a base currency (defaults to AED).

    Args:
        base: ISO 4217 currency code to price everything against, e.g. AED,
            USD, EUR. Case-insensitive.

    Returns:
        Dict with `base`, `rates` (code -> multiplier), and `last_update_utc`.
    """
    code = base.strip().upper()

    client = CurrencyClient()
    try:
        payload = await client.latest(code)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if payload.get("result") != "success":
        err_type = _error_type(payload)
        mark_upstream_failure(_UPSTREAM, err_type)
        return _fail(f"Currency API error for base {code}: {err_type}")

    mark_upstream_success(_UPSTREAM)
    rates = payload.get("rates")
    return _ok(
        {
            "base": payload.get("base_code", code),
            "rates": rates if isinstance(rates, dict) else {},
            "last_update_utc": payload.get("time_last_update_utc"),
            "attribution": _ATTRIBUTION,
        }
    )


async def currency_convert(
    amount: float,
    from_currency: str = "AED",
    to_currency: str = "USD",
) -> dict[str, object]:
    """
    Convert an amount from one currency to another (defaults AED to USD).

    Args:
        amount: Amount to convert. Must be >= 0.
        from_currency: Source ISO 4217 currency code. Case-insensitive.
        to_currency: Target ISO 4217 currency code. Case-insensitive.

    Returns:
        Dict with `amount`, `from`, `to`, `rate`, and `converted_amount`
        (rounded to 2 decimal places).
    """
    if not math.isfinite(amount) or amount < 0:
        return _fail(f"amount must be finite and >= 0, got {amount}")

    src = from_currency.strip().upper()
    dst = to_currency.strip().upper()

    client = CurrencyClient()
    try:
        payload = await client.latest(src)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if payload.get("result") != "success":
        err_type = _error_type(payload)
        mark_upstream_failure(_UPSTREAM, err_type)
        return _fail(f"Currency API error for base {src}: {err_type}")

    mark_upstream_success(_UPSTREAM)
    rates = payload.get("rates")
    if not isinstance(rates, dict) or dst not in rates:
        return _fail(f"Unknown or unsupported target currency code: {dst}")

    rate = float(rates[dst])
    converted = amount * rate
    if not math.isfinite(converted):
        return _fail("converted amount exceeds the supported numeric range; use a smaller amount")
    converted = round(converted, 2)
    return _ok(
        {
            "amount": amount,
            "from": src,
            "to": dst,
            "rate": rate,
            "converted_amount": converted,
            "last_update_utc": payload.get("time_last_update_utc"),
            "attribution": _ATTRIBUTION,
        }
    )
