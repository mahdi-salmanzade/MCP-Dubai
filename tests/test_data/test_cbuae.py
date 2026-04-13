"""Tests for the CBUAE feature (HTML fragment parsing)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.cbuae import constants, tools
from mcp_dubai.data.cbuae.client import CbuaeClient

# Real CBUAE HTML shape as of 2026-04-13. Three cells per row:
# an empty decorative td, the Arabic currency name, and the rate cell
# with class="... value". First row is a header with English labels.
SAMPLE_RATES_HTML = """
<section>
<table>
    <tr>
        <td class="font-m fs-small"></td>
        <td class="font-m fs-small">Currency</td>
        <td class="font-m fs-small">Rates</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">دولار امريكي</td>
        <td class="font-r fs-small value">3.6725</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">يورو</td>
        <td class="font-r fs-small value">4.307918</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">جنيه استرليني</td>
        <td class="font-r fs-small value">4.945568</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">ين ياباني</td>
        <td class="font-r fs-small value">0.023071</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">روبية هندية</td>
        <td class="font-r fs-small value">0.044012</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">ريال ايراني</td>
        <td class="font-r fs-small value">3E-06</td>
    </tr>
    <tr>
        <td class="font-r fs-small"></td>
        <td class="font-r fs-small">عملة مجهولة</td>
        <td class="font-r fs-small value">1.234</td>
    </tr>
</table>
</section>
"""

SAMPLE_BASE_RATE_HTML = """
<div class="rate-display">
    <span class="value">3.476%</span>
</div>
"""


class TestExchangeRatesParser:
    def test_skips_header_row(self) -> None:
        """The header row has no value class and must not become a rate."""
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        assert all(r["currency"] != "Currency" for r in rows)
        assert all(r["currency_ar"] != "Currency" for r in rows)

    def test_parses_all_data_rows(self) -> None:
        """Six known currencies plus one unknown fallback should all parse."""
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        assert len(rows) == 7

    def test_translates_arabic_names_to_iso_and_english(self) -> None:
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        iso_codes = {r["iso_code"] for r in rows if r["iso_code"]}
        assert {"USD", "EUR", "GBP", "JPY", "INR", "IRR"}.issubset(iso_codes)

        usd = next(r for r in rows if r["iso_code"] == "USD")
        assert usd["currency"] == "US Dollar"
        assert usd["currency_ar"] == "دولار امريكي"
        assert usd["rate_aed"] == pytest.approx(3.6725)

    def test_handles_scientific_notation(self) -> None:
        """Iranian Rial is quoted as 3E-06, which must parse as a float."""
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        irr = next(r for r in rows if r["iso_code"] == "IRR")
        assert irr["rate_aed"] == pytest.approx(3e-06)

    def test_unknown_arabic_name_passes_through(self) -> None:
        """An unmapped Arabic name is kept so data is not silently dropped."""
        rows = CbuaeClient._parse_currency_table(SAMPLE_RATES_HTML)
        unknown = next(r for r in rows if r["currency_ar"] == "عملة مجهولة")
        assert unknown["iso_code"] is None
        assert unknown["currency"] is None
        assert unknown["rate_aed"] == pytest.approx(1.234)

    def test_handles_empty_fragment(self) -> None:
        assert CbuaeClient._parse_currency_table("") == []

    def test_handles_malformed_html(self) -> None:
        # Should not crash on garbage input.
        result = CbuaeClient._parse_currency_table("<not><valid<html")
        assert isinstance(result, list)

    def test_old_shape_without_value_class_returns_empty(self) -> None:
        """The pre-2026-04 two-cell shape has no value class and yields nothing,
        which is the signal the zero-parse guard relies on."""
        old_shape = (
            "<table><tr><td>US Dollar</td><td>3.6725</td></tr>"
            "<tr><td>Euro</td><td>4.307918</td></tr></table>"
        )
        assert CbuaeClient._parse_currency_table(old_shape) == []


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
        assert result["currency_count"] == 7
        rates = result["rates"]
        assert isinstance(rates, list)
        iso_codes = [r["iso_code"] for r in rates if r["iso_code"]]
        assert "USD" in iso_codes

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


class TestCurrencyMap:
    def test_lookup_returns_iso_and_english(self) -> None:
        from mcp_dubai.data.cbuae.currency_map import ARABIC_TO_ISO, lookup

        iso, name = lookup("دولار امريكي")
        assert iso == "USD"
        assert name == "US Dollar"
        assert len(ARABIC_TO_ISO) >= 70

    def test_lookup_unknown_returns_none_pair(self) -> None:
        from mcp_dubai.data.cbuae.currency_map import lookup

        assert lookup("غير موجود") == (None, None)

    def test_all_iso_codes_are_three_letters(self) -> None:
        from mcp_dubai.data.cbuae.currency_map import ARABIC_TO_ISO

        for iso, name in ARABIC_TO_ISO.values():
            assert len(iso) == 3
            assert iso.isupper()
            assert name


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


class TestCbuaeUpstreamFailures:
    @pytest.mark.asyncio
    @respx.mock
    async def test_exchange_rates_empty_parse_returns_parse_error(self) -> None:
        """Zero parsed rows should surface as success=false, not silent empty."""
        respx.get(constants.EXCHANGE_RATES_TODAY).mock(
            return_value=Response(200, text="<html><body>no table here</body></html>")
        )

        result = await tools.cbuae_exchange_rates()

        assert result["success"] is False
        assert result["error"]["status"] == "parse_error"
        assert "verify_at" in result["error"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_exchange_rates_cloudflare_block_returns_structured_error(self) -> None:
        """A Cloudflare 403 should surface as success=false upstream_blocked."""
        respx.get(constants.EXCHANGE_RATES_TODAY).mock(
            return_value=Response(403, text="<html>Just a moment...</html>")
        )

        result = await tools.cbuae_exchange_rates()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"

    @pytest.mark.asyncio
    @respx.mock
    async def test_base_rate_cloudflare_block_returns_structured_error(self) -> None:
        """cbuae_base_rate must not crash on Cloudflare 403."""
        respx.get(constants.KEY_INTEREST_RATE).mock(
            return_value=Response(403, text="<html>Just a moment...</html>")
        )

        result = await tools.cbuae_base_rate()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"


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
