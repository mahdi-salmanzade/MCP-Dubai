"""Tests for the CBUAE feature (HTML fragment parsing)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.cbuae import constants, tools
from mcp_dubai.data.cbuae.client import CbuaeClient

# Approximate shape of the real CBUAE HTML fragment.
SAMPLE_RATES_HTML = """
<table>
    <thead>
        <tr><th>Currency</th><th>Rate</th></tr>
    </thead>
    <tbody>
        <tr><td>US Dollar</td><td>3.6725</td></tr>
        <tr><td>Euro</td><td>4.307918</td></tr>
        <tr><td>British Pound</td><td>4.945568</td></tr>
        <tr><td>Japanese Yen</td><td>0.023071</td></tr>
        <tr><td>Indian Rupee</td><td>0.044012</td></tr>
    </tbody>
</table>
"""

SAMPLE_BASE_RATE_HTML = """
<div class="rate-display">
    <span class="value">3.476%</span>
</div>
"""


class TestExchangeRatesParser:
    def test_parses_currency_rows(self) -> None:
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        assert len(rows) == 5
        names = [r["currency"] for r in rows]
        assert "US Dollar" in names
        assert "Euro" in names

    def test_extracts_numeric_rates(self) -> None:
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        usd = next(r for r in rows if r["currency"] == "US Dollar")
        assert usd["rate_aed"] == pytest.approx(3.6725)
        eur = next(r for r in rows if r["currency"] == "Euro")
        assert eur["rate_aed"] == pytest.approx(4.307918)

    def test_handles_empty_fragment(self) -> None:
        assert CbuaeClient._parse_currency_table("") == []

    def test_handles_malformed_html(self) -> None:
        # Should not crash on garbage input.
        result = CbuaeClient._parse_currency_table("<not><valid<html")
        assert isinstance(result, list)


class TestBaseRateParser:
    def test_parses_percentage(self) -> None:
        result = CbuaeClient._parse_base_rate(SAMPLE_BASE_RATE_HTML)
        assert result["base_rate_percent"] == pytest.approx(3.476)

    def test_handles_no_percent_sign(self) -> None:
        result = CbuaeClient._parse_base_rate("<div>3.476</div>")
        assert result["base_rate_percent"] == pytest.approx(3.476)

    def test_handles_empty(self) -> None:
        result = CbuaeClient._parse_base_rate("")
        assert result["base_rate_percent"] is None


class TestCbuaeExchangeRatesTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_today_calls_correct_endpoint(self) -> None:
        route = respx.get(constants.EXCHANGE_RATES_TODAY).mock(
            return_value=Response(200, text=SAMPLE_RATES_HTML)
        )

        result = await tools.cbuae_exchange_rates()

        assert route.called
        assert result["date"] == "today"
        assert result["currency_count"] == 5
        rates = result["rates"]
        assert isinstance(rates, list)
        names = [r["currency"] for r in rates]
        assert "US Dollar" in names

    @pytest.mark.asyncio
    @respx.mock
    async def test_historical_calls_dated_endpoint(self) -> None:
        route = respx.get(constants.EXCHANGE_RATES_HISTORICAL).mock(
            return_value=Response(200, text=SAMPLE_RATES_HTML)
        )

        result = await tools.cbuae_exchange_rates(date_str="2026-04-10")

        assert route.called
        assert route.calls.last.request.url.params["dateTime"] == "2026-04-10"
        assert result["date"] == "2026-04-10"

    @pytest.mark.asyncio
    async def test_invalid_date_raises(self) -> None:
        with pytest.raises(ValueError, match=r"Invalid ISO date"):
            await tools.cbuae_exchange_rates(date_str="not-a-date")


class TestCbuaeBaseRateTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_base_rate(self) -> None:
        route = respx.get(constants.KEY_INTEREST_RATE).mock(
            return_value=Response(200, text=SAMPLE_BASE_RATE_HTML)
        )

        result = await tools.cbuae_base_rate()

        assert route.called
        assert result["base_rate_percent"] == pytest.approx(3.476)


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.cbuae import server as cbuae_server

        importlib.reload(cbuae_server)

        names = {t.name for t in get_tool_discovery().get_by_feature("cbuae")}
        assert names == {"cbuae_exchange_rates", "cbuae_base_rate"}

    def test_recommend_for_currency_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.cbuae import server as cbuae_server

        importlib.reload(cbuae_server)

        results = get_tool_discovery().recommend("aed to usd exchange rate", top_k=3)
        assert results
        assert results[0].name == "cbuae_exchange_rates"
