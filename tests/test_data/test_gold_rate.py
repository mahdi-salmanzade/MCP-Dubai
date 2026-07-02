"""Tests for the gold_rate feature (DJG retail rates from Dubai City of Gold)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.gold_rate import constants, tools

# Trimmed from the live dubaicityofgold.com homepage, captured 2026-07-02.
_PAGE_HTML = """\
<html><body>
<div class="sortd-gold-price-date">
    <select id="gold-price-date">
        <option value="2026-07-02">Jul 02, 2026</option><option value="2026-07-01">Jul 01, 2026</option>
    </select>
</div>
<div id="gold-price-container" class="sortd-gold-price-list">
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">24K Gold</span>
        <span class="sortd-gold-value">AED 494.75</span>
    </div>
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">22K Gold</span>
        <span class="sortd-gold-value">AED 458.00</span>
    </div>
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">21K Gold</span>
        <span class="sortd-gold-value">AED 439.25</span>
    </div>
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">18K Gold</span>
        <span class="sortd-gold-value">AED 376.50</span>
    </div>
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">14K Gold</span>
        <span class="sortd-gold-value">AED 293.75</span>
    </div>
<span class="update-dte">
    Updated 3 minutes ago</span></div>
</body></html>
"""

# Layout drift: only two karat rows survive, below the MIN_KARAT_RATES bar.
_MALFORMED_HTML = """\
<html><body>
<div class="gold-prices-redesigned">
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">24K Gold</span>
        <span class="sortd-gold-value">AED 494.75</span>
    </div>
    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">22K Gold</span>
        <span class="sortd-gold-value">AED 458.00</span>
    </div>
</div>
</body></html>
"""

# Edge shape: thousands separators in values, no date dropdown, no hint.
_SPARSE_HTML = """\
<html><body>
<div class="sortd-gold-price-item"><span class="sortd-gold-type">24K Gold</span><span class="sortd-gold-value">AED 1,494.75</span></div>
<div class="sortd-gold-price-item"><span class="sortd-gold-type">22K Gold</span><span class="sortd-gold-value">AED 1,458.00</span></div>
<div class="sortd-gold-price-item"><span class="sortd-gold-type">21K Gold</span><span class="sortd-gold-value">AED 1,439.25</span></div>
</body></html>
"""


class TestDubaiGoldRate:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_all_five_karat_rates(self) -> None:
        respx.get(constants.PAGE_URL).mock(return_value=Response(200, text=_PAGE_HTML))

        result = await tools.dubai_gold_rate()

        assert result["success"] is True
        assert result["source"] == "dubaicityofgold.com"
        data = result["data"]
        assert isinstance(data, dict)
        rates = data["rates_aed_per_gram"]
        assert isinstance(rates, dict)
        assert rates == {
            "24k": 494.75,
            "22k": 458.00,
            "21k": 439.25,
            "18k": 376.50,
            "14k": 293.75,
        }
        assert data["rate_date"] == "2026-07-02"
        assert data["updated_hint"] == "Updated 3 minutes ago"
        assert "09:00" in str(data["update_schedule"])
        assert "Dubai Jewellery Group" in str(data["attribution"])
        assert "not spot bullion" in str(data["disclaimer"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_desktop_browser_user_agent(self) -> None:
        route = respx.get(constants.PAGE_URL).mock(return_value=Response(200, text=_PAGE_HTML))

        result = await tools.dubai_gold_rate()

        assert result["success"] is True
        assert route.called
        sent_ua = route.calls.last.request.headers["User-Agent"]
        assert sent_ua.startswith("Mozilla/5.0")
        assert "mcp-dubai" in sent_ua

    @pytest.mark.asyncio
    @respx.mock
    async def test_tolerates_missing_date_and_hint(self) -> None:
        respx.get(constants.PAGE_URL).mock(return_value=Response(200, text=_SPARSE_HTML))

        result = await tools.dubai_gold_rate()

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        rates = data["rates_aed_per_gram"]
        assert isinstance(rates, dict)
        assert rates["24k"] == 1494.75
        assert rates["21k"] == 1439.25
        assert data["rate_date"] is None
        assert data["updated_hint"] is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_too_few_rates_returns_parse_error(self) -> None:
        respx.get(constants.PAGE_URL).mock(return_value=Response(200, text=_MALFORMED_HTML))

        result = await tools.dubai_gold_rate()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"
        assert "2 karat rates" in str(error["reason"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_page_returns_parse_error(self) -> None:
        respx.get(constants.PAGE_URL).mock(
            return_value=Response(200, text="<html><body>maintenance</body></html>")
        )

        result = await tools.dubai_gold_rate()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(constants.PAGE_URL).mock(return_value=Response(503, text="busy"))

        result = await tools.dubai_gold_rate()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDiscovery:
    def test_tool_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.gold_rate import server as gold_server

        importlib.reload(gold_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("gold_rate")}
        assert names == {"dubai_gold_rate"}

    def test_recommend_for_gold_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.gold_rate import server as gold_server

        importlib.reload(gold_server)
        results = get_tool_discovery().recommend("today 22k gold rate in dubai souk", top_k=5)
        assert results
        assert any(r.feature == "gold_rate" for r in results)
