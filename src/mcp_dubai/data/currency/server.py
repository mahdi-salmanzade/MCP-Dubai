"""FastMCP server for currency (keyless everyday AED-base converter)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.currency import tools

mcp: FastMCP = FastMCP("currency")


@mcp.tool
async def currency_rates(base: str = "AED") -> dict[str, object]:
    """
    Everyday exchange rates for a base currency (defaults to AED, no key).

    The convenient companion to the official `cbuae` central-bank rate tools.

    Args:
        base: ISO 4217 currency code to price everything against, e.g. AED,
            USD, EUR. Case-insensitive.
    """
    return await tools.currency_rates(base=base)


@mcp.tool
async def currency_convert(
    amount: float,
    from_currency: str = "AED",
    to_currency: str = "USD",
) -> dict[str, object]:
    """
    Convert an amount between two currencies (defaults AED to USD, no key).

    Args:
        amount: Amount to convert. Must be >= 0.
        from_currency: Source ISO 4217 currency code. Case-insensitive.
        to_currency: Target ISO 4217 currency code. Case-insensitive.
    """
    return await tools.currency_convert(
        amount=amount, from_currency=from_currency, to_currency=to_currency
    )


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="currency_rates",
        description=(
            "Everyday exchange rates for a base currency (defaults to AED) via "
            "the keyless ExchangeRate-API open endpoint. The convenient "
            "companion to the official cbuae central-bank rates."
        ),
        feature="currency",
        tier=TIER_OPEN,
        tags=[
            "currency",
            "exchange rate",
            "convert",
            "rates",
            "forex",
            "aed",
            "usd",
            "eur",
            "dirham",
            "dollar",
            "تحويل عملة",
            "سعر الصرف",
        ],
    ),
    ToolMeta(
        name="currency_convert",
        description=(
            "Convert an amount between two currencies (defaults AED to USD) "
            "using keyless everyday rates from the ExchangeRate-API open endpoint."
        ),
        feature="currency",
        tier=TIER_OPEN,
        tags=[
            "currency",
            "convert",
            "exchange rate",
            "conversion",
            "forex",
            "aed",
            "usd",
            "dirham",
            "dollar",
            "money",
            "تحويل عملة",
            "سعر الصرف",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
