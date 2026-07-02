"""Tests for the dfm feature (keyless Dubai Financial Market market data)."""

from __future__ import annotations

from typing import Any

import pytest
import respx
from httpx import Response

from mcp_dubai.data.dfm import constants, tools

# Modeled on the real /mw/v1/indices payload (newest first, one record per
# trading minute). Values chosen so open, high, and low are all distinct.
_INDEX_RECORDS: list[dict[str, object]] = [
    {
        "id": "2026-07-02T15:00:00",
        "change": -19.480,
        "changepercentage": -0.324,
        "value": 5990.590,
        "volume": 120701866,
    },
    {
        "id": "2026-07-02T14:59:00",
        "change": -19.480,
        "changepercentage": -0.324,
        "value": 5990.590,
        "volume": 120559353,
    },
    {
        "id": "2026-07-02T14:43:00",
        "change": -6.700,
        "changepercentage": -0.111,
        "value": 6003.370,
        "volume": 103861496,
    },
    {
        "id": "2026-07-02T10:00:00",
        "change": -9.070,
        "changepercentage": -0.151,
        "value": 6001.000,
        "volume": 1200000,
    },
]


def _stock(**overrides: Any) -> dict[str, Any]:
    """One /mw/v1/stocks record, modeled on the real EMAAR payload."""
    record: dict[str, Any] = {
        "id": "EMAAR",
        "openingprice": 12.06,
        "closingprice": 11.94,
        "previousclosingprice": 12.04,
        "lastradeprice": 11.94,
        "lastradetime": "2026-07-02T14:58:53",
        "highestprice": 12.18,
        "lowestprice": 11.94,
        "highestin52weeks": 17.26,
        "lowestin52weeks": 10.16,
        "bidprice": 11.94,
        "offerprice": 12.0,
        "totalvolume": 12445394,
        "totalvalue": 149273553.66,
        "netchange": -0.1,
        "changepercentage": -0.831,
        "totaltrades": 2892,
        "market": "510",
        "name": None,
        "suspended": "A",
    }
    record.update(overrides)
    return record


_STOCK_RECORDS: list[dict[str, Any]] = [
    _stock(),
    _stock(
        id="SALIK",
        lastradeprice=5.8,
        previousclosingprice=5.93,
        netchange=-0.13,
        changepercentage=-2.192,
    ),
    _stock(id="DEWA", lastradeprice=2.75, previousclosingprice=2.76),
    _stock(id="ABTC", lastradeprice=0.0, lastradetime=None, suspended="S", market="200"),
]


class TestDfmIndex:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_latest_snapshot_and_intraday_summary(self) -> None:
        respx.get(constants.INDICES_URL).mock(return_value=Response(200, json=_INDEX_RECORDS))

        result = await tools.dfm_index()

        assert result["success"] is True
        assert result["source"] == "api2.dfm.ae"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["value"] == 5990.59
        assert data["change"] == -19.48
        assert data["change_pct"] == -0.324
        assert data["volume"] == 120701866
        assert data["timestamp"] == "2026-07-02T15:00:00"
        intraday = data["intraday"]
        assert isinstance(intraday, dict)
        assert intraday["open"] == 6001.0
        assert intraday["high"] == 6003.37
        assert intraday["low"] == 5990.59
        assert intraday["records"] == 4
        assert "Not investment advice" in str(data["attribution"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_sorts_records_when_upstream_order_changes(self) -> None:
        shuffled = [_INDEX_RECORDS[2], _INDEX_RECORDS[0], _INDEX_RECORDS[3], _INDEX_RECORDS[1]]
        respx.get(constants.INDICES_URL).mock(return_value=Response(200, json=shuffled))

        result = await tools.dfm_index()

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["timestamp"] == "2026-07-02T15:00:00"
        assert data["value"] == 5990.59

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_payload_returns_fail(self) -> None:
        respx.get(constants.INDICES_URL).mock(return_value=Response(200, json=[]))

        result = await tools.dfm_index()

        assert result["success"] is False
        assert "no records" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(constants.INDICES_URL).mock(return_value=Response(503, text="busy"))

        result = await tools.dfm_index()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDfmStockQuote:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_trimmed_quote(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_stock_quote(symbol="EMAAR")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["symbol"] == "EMAAR"
        assert data["last_trade_price"] == 11.94
        assert data["last_trade_time"] == "2026-07-02T14:58:53"
        assert data["open"] == 12.06
        assert data["day_high"] == 12.18
        assert data["day_low"] == 11.94
        assert data["previous_close"] == 12.04
        assert data["change"] == -0.1
        assert data["change_pct"] == -0.831
        assert data["week_52_high"] == 17.26
        assert data["week_52_low"] == 10.16
        assert data["total_trades"] == 2892
        assert data["is_suspended"] is False
        # Raw upstream field names must not leak into the trimmed quote.
        assert "lastradeprice" not in data
        assert "Dubai Financial Market" in str(data["attribution"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_symbol_match_is_case_insensitive(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_stock_quote(symbol="  salik ")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["symbol"] == "SALIK"
        assert data["change_pct"] == -2.192

    @pytest.mark.asyncio
    @respx.mock
    async def test_suspended_security_is_flagged(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_stock_quote(symbol="ABTC")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_suspended"] is True
        assert data["last_trade_time"] is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_unknown_symbol_fails_with_near_matches(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_stock_quote(symbol="EMAR")

        assert result["success"] is False
        error = str(result["error"])
        assert "EMAR" in error
        assert "EMAAR" in error

    @pytest.mark.asyncio
    @respx.mock
    async def test_unknown_symbol_without_near_matches_points_to_listing(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_stock_quote(symbol="ZZZZZZ")

        assert result["success"] is False
        assert "dfm_list_securities" in str(result["error"])

    @pytest.mark.asyncio
    async def test_empty_symbol_fails_without_network(self) -> None:
        result = await tools.dfm_stock_quote(symbol="   ")

        assert result["success"] is False
        assert "symbol" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(503, text="busy"))

        result = await tools.dfm_stock_quote(symbol="EMAAR")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDfmListSecurities:
    @pytest.mark.asyncio
    @respx.mock
    async def test_lists_all_sorted_by_symbol(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_list_securities()

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        securities = data["securities"]
        assert isinstance(securities, list)
        assert [s["symbol"] for s in securities] == ["ABTC", "DEWA", "EMAAR", "SALIK"]
        assert data["returned"] == 4
        assert data["total"] == 4

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_filters_by_symbol_substring(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_list_securities(search="ma")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        securities = data["securities"]
        assert isinstance(securities, list)
        assert [s["symbol"] for s in securities] == ["EMAAR"]
        assert data["total"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_match_returns_empty_list_with_zero_total(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=_STOCK_RECORDS))

        result = await tools.dfm_list_securities(search="zzz")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["securities"] == []
        assert data["returned"] == 0
        assert data["total"] == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_limit_caps_page_but_total_reports_all_matches(self) -> None:
        many = [_stock(id=f"SYM{i:03d}") for i in range(60)]
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=many))

        result = await tools.dfm_list_securities(search="SYM")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        securities = data["securities"]
        assert isinstance(securities, list)
        assert len(securities) == 50
        assert data["returned"] == 50
        assert data["total"] == 60

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_payload_returns_fail(self) -> None:
        respx.get(constants.STOCKS_URL).mock(return_value=Response(200, json=[]))

        result = await tools.dfm_list_securities()

        assert result["success"] is False
        assert "no records" in str(result["error"])


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.dfm import server as dfm_server

        importlib.reload(dfm_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("dfm")}
        assert names == {"dfm_index", "dfm_stock_quote", "dfm_list_securities"}

    def test_recommend_for_stock_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.dfm import server as dfm_server

        importlib.reload(dfm_server)
        results = get_tool_discovery().recommend("emaar share price dubai stock market", top_k=5)
        assert results
        assert any(r.feature == "dfm" for r in results)
