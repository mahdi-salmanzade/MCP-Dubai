"""DFM tool functions (keyless Dubai Financial Market live market data)."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure as mark_upstream_failure
from mcp_dubai._shared.health import mark_success as mark_upstream_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.dfm.client import DfmClient

_SOURCE = "api2.dfm.ae"
_UPSTREAM = "dfm"
_VERIFY_AT = "https://marketwatch.dfm.ae/"
_ATTRIBUTION = (
    "Data from undocumented best-effort JSON endpoints behind dfm.ae "
    "(api2.dfm.ae); may be delayed and can change without notice. Not "
    "investment advice. Source: Dubai Financial Market."
)

_LIST_LIMIT = 50
_NEAR_MATCH_LIMIT = 8


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


def _symbol_of(record: dict[str, Any]) -> str:
    """The ticker symbol lives in the `id` field of a stocks record."""
    return str(record.get("id") or "").strip().upper()


def _near_matches(query: str, symbols: list[str]) -> list[str]:
    """
    Suggest symbols close to a query that matched nothing exactly.

    A symbol is "near" when either string contains the other, or when it
    shares the query's first three characters (which catches the common
    one-letter typo, e.g. EMAR for EMAAR).
    """
    prefix = query[:3]
    hits = {
        symbol
        for symbol in symbols
        if symbol and (query in symbol or symbol in query or symbol.startswith(prefix))
    }
    return sorted(hits)[:_NEAR_MATCH_LIMIT]


def _trim_quote(record: dict[str, Any]) -> dict[str, object]:
    """Reduce a raw ~47-field stocks record to the useful quote fields."""
    return {
        "symbol": _symbol_of(record),
        "name": record.get("name"),
        "last_trade_price": record.get("lastradeprice"),
        "last_trade_time": record.get("lastradetime"),
        "open": record.get("openingprice"),
        "day_high": record.get("highestprice"),
        "day_low": record.get("lowestprice"),
        "previous_close": record.get("previousclosingprice"),
        "change": record.get("netchange"),
        "change_pct": record.get("changepercentage"),
        "bid_price": record.get("bidprice"),
        "offer_price": record.get("offerprice"),
        "week_52_high": record.get("highestin52weeks"),
        "week_52_low": record.get("lowestin52weeks"),
        "total_trades": record.get("totaltrades"),
        "total_volume": record.get("totalvolume"),
        "total_value": record.get("totalvalue"),
        "is_suspended": record.get("suspended") == "S",
    }


async def dfm_index() -> dict[str, object]:
    """
    Get the latest DFM General Index snapshot with an intraday summary.

    Returns:
        Dict with `value`, `change`, `change_pct`, `volume`, and `timestamp`
        for the newest record, plus an `intraday` summary (open, high, low,
        record count) computed client-side from the minute-by-minute records
        the endpoint returns.
    """
    client = DfmClient()
    try:
        records = await client.indices()
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if not records:
        mark_upstream_failure(_UPSTREAM, "indices endpoint returned no records")
        return _fail("DFM indices endpoint returned no records.")

    mark_upstream_success(_UPSTREAM)

    # The endpoint returns newest first, but sort defensively: `id` is an
    # ISO minute timestamp, so lexicographic order is chronological order.
    ordered = sorted(records, key=lambda r: str(r.get("id") or ""), reverse=True)
    latest = ordered[0]
    values = [float(r["value"]) for r in ordered if isinstance(r.get("value"), int | float)]

    return _ok(
        {
            "index": "DFM General Index",
            "value": latest.get("value"),
            "change": latest.get("change"),
            "change_pct": latest.get("changepercentage"),
            "volume": latest.get("volume"),
            "timestamp": latest.get("id"),
            "intraday": {
                "open": values[-1] if values else None,
                "high": max(values) if values else None,
                "low": min(values) if values else None,
                "records": len(ordered),
            },
            "attribution": _ATTRIBUTION,
        }
    )


async def dfm_stock_quote(symbol: str) -> dict[str, object]:
    """
    Get a trimmed live quote for one DFM-listed security.

    Args:
        symbol: Ticker symbol on the Dubai Financial Market, e.g. EMAAR,
            SALIK, DEWA. Case-insensitive; matched client-side because the
            upstream ignores query parameters.

    Returns:
        Dict with the key quote fields: last trade price/time, open, day
        high/low, previous close, change, bid/offer, 52-week range, totals,
        and suspension flag. Fails with near-match suggestions when the
        symbol is not listed.
    """
    query = symbol.strip().upper()
    if not query:
        return _fail("symbol must not be empty")

    client = DfmClient()
    try:
        records = await client.stocks()
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if not records:
        mark_upstream_failure(_UPSTREAM, "stocks endpoint returned no records")
        return _fail("DFM stocks endpoint returned no records.")

    mark_upstream_success(_UPSTREAM)

    match = next((r for r in records if _symbol_of(r) == query), None)
    if match is None:
        near = _near_matches(query, [_symbol_of(r) for r in records])
        hint = (
            f" Did you mean: {', '.join(near)}?"
            if near
            else " Use dfm_list_securities to browse listed symbols."
        )
        return _fail(f"No DFM security with symbol {query}.{hint}")

    quote = _trim_quote(match)
    quote["attribution"] = _ATTRIBUTION
    return _ok(quote)


async def dfm_list_securities(search: str = "") -> dict[str, object]:
    """
    List DFM-listed securities, optionally filtered by a search string.

    Args:
        search: Optional substring matched case-insensitively against each
            security's symbol or name (the upstream returns null names as
            of 2026-08-14, so symbol is the practical filter). Empty lists
            the first 50 securities alphabetically.

    Returns:
        Dict with `securities` (list of {symbol, name}, max 50 entries),
        `returned`, and `total` matches across the whole listing.
    """
    needle = search.strip().upper()

    client = DfmClient()
    try:
        records = await client.stocks()
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if not records:
        mark_upstream_failure(_UPSTREAM, "stocks endpoint returned no records")
        return _fail("DFM stocks endpoint returned no records.")

    mark_upstream_success(_UPSTREAM)

    matches: list[dict[str, object]] = []
    for record in records:
        sym = _symbol_of(record)
        if not sym:
            continue
        name = record.get("name")
        if needle and needle not in sym and needle not in str(name or "").upper():
            continue
        matches.append({"symbol": sym, "name": name})

    matches.sort(key=lambda entry: str(entry["symbol"]))
    page = matches[:_LIST_LIMIT]

    return _ok(
        {
            "securities": page,
            "returned": len(page),
            "total": len(matches),
            "attribution": _ATTRIBUTION,
        }
    )
