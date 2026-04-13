"""FastMCP server for CBUAE exchange rates and base rate."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.cbuae import tools

mcp: FastMCP = FastMCP("cbuae")


@mcp.tool
async def cbuae_exchange_rates(date_str: str | None = None) -> dict[str, object]:
    """
    Get CBUAE exchange rates for today or a historical date (~75 currencies).

    Args:
        date_str: ISO date YYYY-MM-DD. Omit for today's rates.

    Returns:
        Dict with `date`, `currency_count`, and `rates` (list of
        `{currency, rate_aed}` entries).
    """
    return await tools.cbuae_exchange_rates(date_str=date_str)


@mcp.tool
async def cbuae_base_rate() -> dict[str, object]:
    """
    Get the current CBUAE base rate (percentage).

    Returns:
        Dict with `base_rate_percent` and source attribution.
    """
    return await tools.cbuae_base_rate()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="cbuae_exchange_rates",
        description=(
            "Central Bank of UAE exchange rates against AED for today or a "
            "specific historical date. Covers ~75 currencies including USD, "
            "EUR, GBP, JPY, INR, PKR, CNY."
        ),
        feature="cbuae",
        tier=TIER_OPEN,
        tags=[
            "currency",
            "fx",
            "forex",
            "exchange rate",
            "aed",
            "usd",
            "eur",
            "gbp",
            "convert",
            "central bank",
            "cbuae",
        ],
    ),
    ToolMeta(
        name="cbuae_base_rate",
        description="The current CBUAE base interest rate (percentage).",
        feature="cbuae",
        tier=TIER_OPEN,
        tags=[
            "interest",
            "rate",
            "base",
            "cbuae",
            "central bank",
            "monetary",
            "policy",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
