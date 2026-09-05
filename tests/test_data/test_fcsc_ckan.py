"""Tests for fcsc_ckan."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.fcsc_ckan import constants, tools


def _ckan_search_payload() -> dict[str, object]:
    return {
        "success": True,
        "result": {
            "count": 2,
            "results": [
                {
                    "id": "abc-123",
                    "name": "uae-trade-2025",
                    "title": "UAE Foreign Trade 2025",
                    "organization": {"name": "federal-customs-authority"},
                    "resources": [
                        {
                            "url": "https://example.ae/trade.csv",
                            "format": "CSV",
                        }
                    ],
                },
                {
                    "id": "def-456",
                    "name": "uae-trade-2024",
                    "title": "UAE Foreign Trade 2024",
                    "organization": {"name": "federal-customs-authority"},
                    "resources": [],
                },
            ],
        },
    }


def _ckan_show_payload() -> dict[str, object]:
    return {
        "success": True,
        "result": {
            "id": "abc-123",
            "name": "uae-trade-2025",
            "title": "UAE Foreign Trade 2025",
            "notes": "HS chapter breakdown of UAE imports and exports.",
            "resources": [
                {
                    "url": "https://example.ae/trade.csv",
                    "format": "CSV",
                    "size": 102400,
                }
            ],
        },
    }


def _ckan_org_list_payload() -> dict[str, object]:
    return {
        "success": True,
        "result": [
            "federal-customs-authority",
            "ministry-of-economy",
            "moccae",
        ],
    }


def _ckan_failure_payload() -> dict[str, object]:
    return {
        "success": False,
        "error": {"message": "Dataset not found"},
    }


class TestFcscSearchDataset:
    @pytest.mark.asyncio
    @respx.mock
    async def test_basic_search(self) -> None:
        route = respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(200, json=_ckan_search_payload())
        )

        result = await tools.fcsc_search_dataset(query="trade")

        assert route.called
        assert route.calls.last.request.url.params["q"] == "trade"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 2
        results = data["results"]
        assert isinstance(results, list)
        assert len(results) == 2
        assert result["source"] == "opendata.fcsc.gov.ae"

    @pytest.mark.asyncio
    @respx.mock
    async def test_organization_filter_uses_fq(self) -> None:
        route = respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(200, json=_ckan_search_payload())
        )

        await tools.fcsc_search_dataset(query="", organization="federal-customs-authority")

        params = route.calls.last.request.url.params
        assert params["fq"] == "organization:federal-customs-authority"

    @pytest.mark.asyncio
    async def test_invalid_rows_returns_fail(self) -> None:
        result = await tools.fcsc_search_dataset(rows=200)
        assert result["success"] is False
        assert "rows" in str(result["error"])

    @pytest.mark.asyncio
    async def test_invalid_start_returns_fail(self) -> None:
        result = await tools.fcsc_search_dataset(start=-1)
        assert result["success"] is False
        assert "start" in str(result["error"])


class TestFcscGetDataset:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_metadata(self) -> None:
        route = respx.get(constants.PACKAGE_SHOW).mock(
            return_value=Response(200, json=_ckan_show_payload())
        )

        result = await tools.fcsc_get_dataset("uae-trade-2025")

        assert route.called
        assert route.calls.last.request.url.params["id"] == "uae-trade-2025"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["title"] == "UAE Foreign Trade 2025"
        resources = data["resources"]
        assert isinstance(resources, list)
        assert resources[0]["format"] == "CSV"

    @pytest.mark.asyncio
    @respx.mock
    async def test_failure_payload_returns_fail_envelope(self) -> None:
        respx.get(constants.PACKAGE_SHOW).mock(
            return_value=Response(200, json=_ckan_failure_payload())
        )

        result = await tools.fcsc_get_dataset("missing")
        assert result["success"] is False
        assert "CKAN reported failure" in str(result["error"])

    @pytest.mark.asyncio
    async def test_empty_id_returns_fail(self) -> None:
        result = await tools.fcsc_get_dataset("")
        assert result["success"] is False
        assert "dataset_id" in str(result["error"])


class TestFcscListOrganizations:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_org_list(self) -> None:
        respx.get(constants.ORGANIZATION_LIST).mock(
            return_value=Response(200, json=_ckan_org_list_payload())
        )

        result = await tools.fcsc_list_organizations()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 3
        orgs = data["organizations"]
        assert isinstance(orgs, list)
        assert "federal-customs-authority" in orgs


class TestFcaTradeStats:
    @pytest.mark.asyncio
    @respx.mock
    async def test_filters_by_fca_org(self) -> None:
        route = respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(200, json=_ckan_search_payload())
        )

        await tools.fca_trade_stats(query="2025")

        params = route.calls.last.request.url.params
        assert params["fq"] == "organization:federal-customs-authority"
        assert params["q"] == "2025"


class TestFcscUpstreamFailures:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("payload", [[], None, "html", {"success": "true", "result": {}}])
    async def test_malformed_envelope_returns_structured_error(self, payload: object) -> None:
        respx.get(constants.PACKAGE_SEARCH).mock(return_value=Response(200, json=payload))

        result = await tools.fcsc_search_dataset()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize(
        "result_block",
        [
            None,
            [],
            {},
            {"count": True, "results": []},
            {"count": 1, "results": ["bad"]},
            {"count": 0, "results": [{}]},
        ],
    )
    async def test_malformed_search_result_is_not_successful_empty_data(
        self, result_block: object
    ) -> None:
        respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(200, json={"success": True, "result": result_block})
        )

        result = await tools.fcsc_search_dataset()

        assert result["success"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_enforces_requested_rows(self) -> None:
        respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(200, json=_ckan_search_payload())
        )

        result = await tools.fcsc_search_dataset(rows=1)

        assert result["data"]["count"] == 2
        assert len(result["data"]["results"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("result_block", [None, {}, [42], [""]])
    async def test_organizations_rejects_invalid_items(self, result_block: object) -> None:
        respx.get(constants.ORGANIZATION_LIST).mock(
            return_value=Response(200, json={"success": True, "result": result_block})
        )

        result = await tools.fcsc_list_organizations()

        assert result["success"] is False

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("payload", [{"success": True}, {"success": True, "result": []}])
    async def test_dataset_rejects_missing_or_wrong_result(self, payload: object) -> None:
        respx.get(constants.PACKAGE_SHOW).mock(return_value=Response(200, json=payload))

        result = await tools.fcsc_get_dataset("test")

        assert result["success"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_dataset_403_returns_structured_error(self) -> None:
        respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(403, text="Just a moment...")
        )

        result = await tools.fcsc_search_dataset(query="test")

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dataset_403_returns_structured_error(self) -> None:
        respx.get(constants.PACKAGE_SHOW).mock(return_value=Response(403, text="Just a moment..."))

        result = await tools.fcsc_get_dataset("some-id")

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_organizations_403_returns_structured_error(self) -> None:
        respx.get(constants.ORGANIZATION_LIST).mock(
            return_value=Response(403, text="Just a moment...")
        )

        result = await tools.fcsc_list_organizations()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"

    @pytest.mark.asyncio
    @respx.mock
    async def test_fca_trade_stats_403_inherits_error_handling(self) -> None:
        respx.get(constants.PACKAGE_SEARCH).mock(
            return_value=Response(403, text="Just a moment...")
        )

        result = await tools.fca_trade_stats()

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.fcsc_ckan import server as fcsc_server

        importlib.reload(fcsc_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("fcsc_ckan")}
        assert names == {
            "fcsc_search_dataset",
            "fcsc_get_dataset",
            "fcsc_list_organizations",
            "fca_trade_stats",
        }

    def test_recommend_for_trade_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.fcsc_ckan import server as fcsc_server

        importlib.reload(fcsc_server)
        results = get_tool_discovery().recommend("uae imports exports trade", top_k=3)
        assert results
        assert results[0].feature == "fcsc_ckan"
