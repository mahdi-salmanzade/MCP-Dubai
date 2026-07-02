"""FastMCP server for dfm (keyless Dubai Financial Market live market data)."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.dfm import tools

mcp: FastMCP = FastMCP("dfm")


@mcp.tool
async def dfm_index() -> dict[str, object]:
    """
    Latest DFM General Index snapshot with an intraday summary (no key).

    Returns the newest index value, change, change percentage, volume, and
    timestamp, plus a client-side intraday open/high/low summary. Data may
    be delayed; not investment advice.
    """
    return await tools.dfm_index()


@mcp.tool
async def dfm_stock_quote(symbol: str) -> dict[str, object]:
    """
    Trimmed live quote for one DFM-listed security by ticker symbol (no key).

    Data may be delayed; not investment advice.

    Args:
        symbol: Ticker on the Dubai Financial Market, e.g. EMAAR, SALIK,
            DEWA. Case-insensitive. Unknown symbols fail with near-match
            suggestions.
    """
    return await tools.dfm_stock_quote(symbol=symbol)


@mcp.tool
async def dfm_list_securities(search: str = "") -> dict[str, object]:
    """
    List DFM-listed securities, optionally filtered by symbol or name (no key).

    Args:
        search: Optional substring matched case-insensitively against each
            security's symbol or name. Empty lists the first 50 securities
            alphabetically; the response reports the total match count.
    """
    return await tools.dfm_list_securities(search=search)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="dfm_index",
        description=(
            "Latest DFM General Index snapshot (value, change, volume, "
            "timestamp) with a client-side intraday open/high/low summary, "
            "from the keyless endpoints behind dfm.ae. Data may be delayed; "
            "not investment advice."
        ),
        feature="dfm",
        tier=TIER_OPEN,
        tags=[
            "dfm",
            "dubai financial market",
            "stock market",
            "index",
            "dfmgi",
            "general index",
            "equities",
            "shares",
            "trading",
            "market data",
            "بورصة",
            "سوق دبي المالي",
            "مؤشر",
            "الأسهم",
            "تداول",
        ],
    ),
    ToolMeta(
        name="dfm_stock_quote",
        description=(
            "Trimmed live quote for one Dubai Financial Market security by "
            "ticker symbol (e.g. EMAAR, SALIK, DEWA): last trade, day range, "
            "previous close, change, bid/offer, 52-week range, totals. "
            "Keyless; data may be delayed; not investment advice."
        ),
        feature="dfm",
        tier=TIER_OPEN,
        tags=[
            "dfm",
            "dubai financial market",
            "stock",
            "quote",
            "share price",
            "ticker",
            "emaar",
            "salik",
            "dewa",
            "equities",
            "trading",
            "بورصة",
            "سوق دبي المالي",
            "سهم",
            "سعر السهم",
            "تداول",
        ],
    ),
    ToolMeta(
        name="dfm_list_securities",
        description=(
            "Search or list the ~450 securities on the Dubai Financial "
            "Market by symbol or name substring (max 50 results, reports "
            "total). Keyless; not investment advice."
        ),
        feature="dfm",
        tier=TIER_OPEN,
        tags=[
            "dfm",
            "dubai financial market",
            "securities",
            "listed companies",
            "tickers",
            "symbols",
            "search",
            "stocks",
            "equities",
            "bonds",
            "sukuk",
            "بورصة",
            "سوق دبي المالي",
            "الأوراق المالية",
            "الشركات المدرجة",
            "أسهم",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
