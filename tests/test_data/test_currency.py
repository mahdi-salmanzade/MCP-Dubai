"""Tests for the currency feature (keyless everyday AED-base converter)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.currency import constants, tools


def _latest_url(base: str) -> str:
    return f"{constants.CURRENCY_API_BASE}/latest/{base}"


def _rates_payload(
    base: str = "AED",
    rates: dict[str, float] | None = None,
) -> dict[str, object]:
    return {
        "result": "success",
        "base_code": base,
        "time_last_update_utc": "Fri, 26 Jun 2026 00:00:01 +0000",
        "rates": rates if rates is not None else {"AED": 1.0, "USD": 0.2723, "EUR": 0.25},
    }


class TestCurrencyRates:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_rates_and_source(self) -> None:
        respx.get(_latest_url("AED")).mock(return_value=Response(200, json=_rates_payload()))

        result = await tools.currency_rates(base="AED")

        assert result["success"] is True
        assert result["source"] == "open.er-api.com"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["base"] == "AED"
        rates = data["rates"]
        assert isinstance(rates, dict)
        assert rates["USD"] == 0.2723
        assert "cbuae" in str(data["attribution"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_base_normalized_to_upper(self) -> None:
        route = respx.get(_latest_url("USD")).mock(
            return_value=Response(200, json=_rates_payload(base="USD"))
        )

        result = await tools.currency_rates(base="usd")

        assert route.called
        assert result["success"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_result_error_body_returns_fail(self) -> None:
        respx.get(_latest_url("ZZZ")).mock(
            return_value=Response(200, json={"result": "error", "error-type": "unsupported-code"})
        )

        result = await tools.currency_rates(base="ZZZ")

        assert result["success"] is False
        assert "unsupported-code" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(_latest_url("AED")).mock(return_value=Response(503, text="busy"))

        result = await tools.currency_rates(base="AED")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_malformed_success_rates_return_structured_error(self) -> None:
        respx.get(_latest_url("AED")).mock(
            return_value=Response(200, json={"result": "success", "rates": "not-a-map"})
        )

        result = await tools.currency_rates(base="AED")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"


class TestCurrencyConvert:
    @pytest.mark.asyncio
    @respx.mock
    async def test_converts_aed_to_usd(self) -> None:
        respx.get(_latest_url("AED")).mock(return_value=Response(200, json=_rates_payload()))

        result = await tools.currency_convert(amount=100, from_currency="AED", to_currency="USD")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["from"] == "AED"
        assert data["to"] == "USD"
        assert data["rate"] == 0.2723
        assert data["converted_amount"] == 27.23

    @pytest.mark.asyncio
    @respx.mock
    async def test_unknown_target_code_returns_fail(self) -> None:
        respx.get(_latest_url("AED")).mock(
            return_value=Response(200, json=_rates_payload(rates={"AED": 1.0, "USD": 0.2723}))
        )

        result = await tools.currency_convert(amount=10, from_currency="AED", to_currency="ZZZ")

        assert result["success"] is False
        assert "ZZZ" in str(result["error"])

    @pytest.mark.asyncio
    async def test_negative_amount_returns_fail(self) -> None:
        result = await tools.currency_convert(amount=-5, from_currency="AED", to_currency="USD")
        assert result["success"] is False
        assert "amount" in str(result["error"])

    @pytest.mark.asyncio
    async def test_non_finite_amount_returns_fail(self) -> None:
        result = await tools.currency_convert(
            amount=float("nan"), from_currency="AED", to_currency="USD"
        )
        assert result["success"] is False
        assert "finite" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_result_error_body_returns_fail(self) -> None:
        respx.get(_latest_url("ZZZ")).mock(
            return_value=Response(200, json={"result": "error", "error-type": "unsupported-code"})
        )

        result = await tools.currency_convert(amount=10, from_currency="ZZZ", to_currency="USD")

        assert result["success"] is False
        assert "unsupported-code" in str(result["error"])


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.currency import server as cur_server

        importlib.reload(cur_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("currency")}
        assert names == {"currency_rates", "currency_convert"}

    def test_recommend_for_convert_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.currency import server as cur_server

        importlib.reload(cur_server)
        results = get_tool_discovery().recommend("convert aed to usd exchange rate", top_k=5)
        assert results
        assert any(r.feature == "currency" for r in results)
