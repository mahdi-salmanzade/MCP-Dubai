"""Pure CBUAE tool functions."""

from __future__ import annotations

from datetime import date

from mcp_dubai.data.cbuae.client import CbuaeClient


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

    if target is None:
        rates = await client.get_exchange_rates_today()
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

    rates = await client.get_exchange_rates_for_date(target)
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
    result = await client.get_key_interest_rate()
    return {
        "base_rate_percent": result["base_rate_percent"],
        "source": "CBUAE Umbraco endpoint, undocumented",
        "raw_excerpt": result.get("raw", ""),
    }
