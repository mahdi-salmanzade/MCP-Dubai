"""Phase 4 Tier 1 tests: dubai_pulse base client + dld + rta."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.constants import DUBAI_PULSE_API_BASE, DUBAI_PULSE_TOKEN_URL
from mcp_dubai._shared.health import get_upstream_registry
from mcp_dubai.data.dld import tools as dld_tools
from mcp_dubai.data.dubai_pulse.client import (
    DubaiPulseClient,
    DubaiPulseResponseError,
    DubaiPulseValidationError,
)
from mcp_dubai.data.rta import tools as rta_tools


def _token_payload() -> dict[str, object]:
    return {"access_token": "fake-token-xyz", "expires_in": 1800}


def _dataset_payload() -> dict[str, object]:
    return {
        "data": [
            {"id": 1, "area_name_en": "Dubai Marina", "amount": 1850000},
            {"id": 2, "area_name_en": "Downtown", "amount": 2750000},
        ],
        "total": 2,
        "offset": 0,
        "limit": 100,
    }


# ----------------------------------------------------------------------------
# Credential-missing pattern (the most important Phase 4 invariant)
# ----------------------------------------------------------------------------


class TestCredentialMissingPattern:
    @pytest.mark.asyncio
    async def test_dld_search_transactions_no_credentials(
        self, clean_dubai_pulse_env: None
    ) -> None:
        result = await dld_tools.dld_search_transactions(area="Dubai Marina")
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "credentials_missing"
        assert "MCP_DUBAI_PULSE_CLIENT_ID" in error["reason"]

    @pytest.mark.asyncio
    async def test_dld_search_rent_contracts_no_credentials(
        self, clean_dubai_pulse_env: None
    ) -> None:
        result = await dld_tools.dld_search_rent_contracts(area="Marina", bedrooms=2)
        assert result["success"] is False
        assert isinstance(result["error"], dict)

    @pytest.mark.asyncio
    async def test_dld_lookup_broker_no_credentials(self, clean_dubai_pulse_env: None) -> None:
        result = await dld_tools.dld_lookup_broker(name="John")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_rta_metro_no_credentials(self, clean_dubai_pulse_env: None) -> None:
        result = await rta_tools.rta_search_metro_stations(line="Red")
        assert result["success"] is False
        assert isinstance(result["error"], dict)


# ----------------------------------------------------------------------------
# Validation runs BEFORE the auth check
# ----------------------------------------------------------------------------


class TestValidationBeforeAuth:
    @pytest.mark.asyncio
    async def test_dld_invalid_limit_returns_validation_error(
        self, clean_dubai_pulse_env: None
    ) -> None:
        result = await dld_tools.dld_search_transactions(limit=999)
        assert result["success"] is False
        # Validation error is a string, not the credentials dict
        assert isinstance(result["error"], str)
        assert "limit" in result["error"]

    @pytest.mark.asyncio
    async def test_dld_lookup_broker_no_filter(self, clean_dubai_pulse_env: None) -> None:
        result = await dld_tools.dld_lookup_broker()
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert "name or license_number" in result["error"]


class TestDubaiPulseClientValidation:
    @pytest.mark.asyncio
    async def test_query_rejects_invalid_pagination_before_auth(
        self, clean_dubai_pulse_env: None
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(ValueError, match="limit"):
            await client.query(limit=0)
        with pytest.raises(ValueError, match="offset"):
            await client.query(offset=-1)

    @pytest.mark.asyncio
    async def test_query_rejects_filter_operators_before_auth(
        self, clean_dubai_pulse_env: None
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(ValueError, match="reserved query syntax"):
            await client.query(filters={"area_name_en": "Marina AND amount=0"})
        with pytest.raises(ValueError, match="filter key"):
            await client.query(filters={"area;drop": "Marina"})

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("query_kwargs", "expected_message"),
        [
            ({"order_by": "created_at; DROP"}, "order_by"),
            ({"columns": ["id"] * 51}, "at most 50"),
            ({"columns": ["invalid-column"]}, "column"),
            ({"filters": {f"field_{index}": index for index in range(21)}}, "at most 20"),
            ({"filters": {"amount": float("nan")}}, "finite"),
            ({"filters": {"payload": ["not", "scalar"]}}, "strings, numbers, or booleans"),
            ({"filters": {"name": "x" * 257}}, "at most 256"),
        ],
    )
    async def test_query_rejects_unsafe_options_before_auth(
        self,
        clean_dubai_pulse_env: None,
        query_kwargs: dict[str, object],
        expected_message: str,
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(DubaiPulseValidationError, match=expected_message):
            await client.query(**query_kwargs)

    def test_rejects_unsafe_path_slugs(self) -> None:
        with pytest.raises(ValueError, match="org"):
            DubaiPulseClient("../dld", "dld_transactions-open-api")
        with pytest.raises(ValueError, match="dataset"):
            DubaiPulseClient("dld", "../../secrets")

    @pytest.mark.asyncio
    async def test_get_all_rejects_zero_page_size(self, clean_dubai_pulse_env: None) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(ValueError, match="page_size"):
            await client.get_all(page_size=0)

    @pytest.mark.asyncio
    async def test_get_all_rejects_invalid_record_cap_before_auth(
        self, clean_dubai_pulse_env: None
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(DubaiPulseValidationError, match="max_records"):
            await client.get_all(max_records=0)

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_serializes_safe_options_and_filter_types(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json={"data": []})
        )
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        await client.query(
            order_by="created_at DESC",
            columns=["id", "area_name_en"],
            filters={
                "active": True,
                "archived": False,
                "attempts": 3,
                "ratio": 1.5,
                "area_name_en": "Dubai Marina",
            },
        )

        params = route.calls[0].request.url.params
        assert params["order_by"] == "created_at DESC"
        assert params["column"] == "id,area_name_en"
        assert params["filter"] == (
            "active=true AND archived=false AND attempts=3 AND ratio=1.5 "
            "AND area_name_en=Dubai Marina"
        )

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize(
        ("response", "expected_message"),
        [
            (Response(200, text="not-json"), "not valid JSON"),
            (Response(200, json=[{"id": 1}]), "non-object JSON response"),
        ],
    )
    async def test_query_rejects_malformed_success_response(
        self,
        configured_dubai_pulse_env: None,
        response: Response,
        expected_message: str,
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=response
        )
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(DubaiPulseResponseError, match=expected_message):
            await client.query()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("payload", "expected_message"),
        [
            ({"data": {"id": 1}}, "must be a list"),
            ({"data": [{"id": 1}, "not-an-object"]}, "records must be objects"),
        ],
    )
    async def test_get_all_rejects_malformed_pages(
        self,
        clean_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
        payload: dict[str, object],
        expected_message: str,
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")
        monkeypatch.setattr(client, "query", AsyncMock(return_value=payload))

        with pytest.raises(DubaiPulseResponseError, match=expected_message):
            await client.get_all()

    @pytest.mark.asyncio
    async def test_get_all_returns_empty_for_empty_page(
        self,
        clean_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")
        mock_query = AsyncMock(return_value={"data": []})
        monkeypatch.setattr(client, "query", mock_query)

        assert await client.get_all() == []
        assert mock_query.await_count == 1

    @pytest.mark.asyncio
    async def test_get_all_stops_at_declared_total_on_full_page(
        self,
        clean_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")
        mock_query = AsyncMock(return_value={"data": [{"id": 1}, {"id": 2}], "total": 2})
        monkeypatch.setattr(client, "query", mock_query)

        records = await client.get_all(max_records=10, page_size=2)

        assert [record["id"] for record in records] == [1, 2]
        assert mock_query.await_count == 1

    @pytest.mark.asyncio
    async def test_get_all_caps_records_after_full_pages(
        self,
        clean_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        client = DubaiPulseClient("dld", "dld_transactions-open-api")
        mock_query = AsyncMock(
            side_effect=[
                {"data": [{"id": 1}, {"id": 2}], "total": 99},
                {"data": [{"id": 3}, {"id": 4}], "total": 99},
            ]
        )
        monkeypatch.setattr(client, "query", mock_query)

        records = await client.get_all(max_records=3, page_size=2)

        assert [record["id"] for record in records] == [1, 2, 3]
        assert mock_query.await_count == 2
        assert mock_query.await_args_list[1].kwargs["offset"] == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_all_advances_by_records_and_honors_total(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            side_effect=[
                Response(200, json={"data": [{"id": 1}, {"id": 2}], "total": 3}),
                Response(200, json={"data": [{"id": 3}], "total": 3}),
            ]
        )
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        records = await client.get_all(max_records=10, page_size=2)

        assert [record["id"] for record in records] == [1, 2, 3]
        assert route.call_count == 2
        assert route.calls[1].request.url.params["offset"] == "2"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_all_rejects_repeated_page(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        repeated = {"data": [{"id": 1}, {"id": 2}], "total": 99}
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json=repeated)
        )
        client = DubaiPulseClient("dld", "dld_transactions-open-api")

        with pytest.raises(DubaiPulseResponseError, match="repeated a page"):
            await client.get_all(max_records=10, page_size=2)


# ----------------------------------------------------------------------------
# Happy path with mocked Dubai Pulse responses
# ----------------------------------------------------------------------------


class TestHappyPath:
    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_search_transactions(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json=_dataset_payload())
        )

        result = await dld_tools.dld_search_transactions(area="Dubai Marina")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 2
        transactions = data["transactions"]
        assert isinstance(transactions, list)
        assert transactions[0]["area_name_en"] == "Dubai Marina"
        assert result["source"] == DUBAI_PULSE_API_BASE
        assert result["retrieved_at"] is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_search_rent_contracts(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_rent_contracts-open-api").mock(
            return_value=Response(
                200,
                json={
                    "data": [{"contract_id": "EJARI-1", "area_en": "Marina"}],
                    "total": 1,
                },
            )
        )

        result = await dld_tools.dld_search_rent_contracts(
            area="Marina",
            bedrooms=2,
            limit=25,
        )

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 1
        assert data["rent_contracts"] == [{"contract_id": "EJARI-1", "area_en": "Marina"}]
        assert route.calls[0].request.url.params["limit"] == "25"
        assert route.calls[0].request.url.params["filter"] == "area_en=Marina AND no_of_rooms=2"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_search_rent_contracts_returns_upstream_error(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_rent_contracts-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await dld_tools.dld_search_rent_contracts(area="Marina")

        assert route.called
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_lookup_broker(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_brokers-open-api").mock(
            return_value=Response(
                200,
                json={
                    "data": [{"broker_name_en": "Aisha Broker", "license_number": "BR-42"}],
                    "total": 1,
                },
            )
        )

        result = await dld_tools.dld_lookup_broker(
            name="Aisha Broker",
            license_number="BR-42",
            limit=10,
        )

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 1
        assert data["brokers"] == [{"broker_name_en": "Aisha Broker", "license_number": "BR-42"}]
        assert route.calls[0].request.url.params["filter"] == (
            "broker_name_en=Aisha Broker AND license_number=BR-42"
        )

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_lookup_broker_returns_upstream_error(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_brokers-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await dld_tools.dld_lookup_broker(name="Aisha Broker")

        assert route.called
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_upstream_failure_is_structured(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await dld_tools.dld_search_transactions()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_invalid_shape_is_structured(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json={"data": {"unexpected": "object"}})
        )

        result = await dld_tools.dld_search_transactions()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_non_object_record_is_structured(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json={"data": ["junk"]})
        )

        result = await dld_tools.dld_search_transactions()

        assert result["success"] is False
        assert isinstance(result["error"], dict)
        assert result["error"]["status"] == "parse_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_dld_rejects_more_records_than_requested(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json={"data": [{"id": 1}, {"id": 2}], "total": 2})
        )

        result = await dld_tools.dld_search_transactions(limit=1)

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"
        assert "requested limit 1" in str(error["reason"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_legitimate_lowercase_and_in_filter_is_allowed(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/dld/dld_transactions-open-api").mock(
            return_value=Response(200, json={"data": []})
        )

        result = await dld_tools.dld_search_transactions(area="Dubai Parks and Resorts")

        assert result["success"] is True
        assert route.calls[0].request.url.params["filter"] == (
            "area_name_en=Dubai Parks and Resorts"
        )

    @pytest.mark.asyncio
    async def test_local_filter_rejection_does_not_poison_health(
        self, configured_dubai_pulse_env: None
    ) -> None:
        before = {item["name"]: item for item in get_upstream_registry().snapshot()}["dubai_pulse"]

        result = await dld_tools.dld_search_transactions(area="Marina OR Palm")

        after = {item["name"]: item for item in get_upstream_registry().snapshot()}["dubai_pulse"]
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert after["failure_count"] == before["failure_count"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_validation_error_is_returned_as_tool_failure(
        self, configured_dubai_pulse_env: None
    ) -> None:
        before = {item["name"]: item for item in get_upstream_registry().snapshot()}["dubai_pulse"]

        result = await rta_tools.rta_search_metro_stations(line="Red OR Green")

        after = {item["name"]: item for item in get_upstream_registry().snapshot()}["dubai_pulse"]
        assert result["success"] is False
        assert isinstance(result["error"], str)
        assert "reserved query syntax" in result["error"]
        assert result["source"] == DUBAI_PULSE_API_BASE
        assert result["retrieved_at"] is not None
        assert after["failure_count"] == before["failure_count"]
        assert not respx.calls

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_metro_stations(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(
                200,
                json={
                    "data": [{"name": "Burj Khalifa", "line": "Red"}],
                    "total": 1,
                },
            )
        )

        result = await rta_tools.rta_search_metro_stations(line="Red")
        assert result["success"] is True
        assert result["source"] == DUBAI_PULSE_API_BASE
        assert result["retrieved_at"] is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_search_bus_routes(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_bus_routes-open-api").mock(
            return_value=Response(
                200,
                json={
                    "data": [{"route_number": "27", "origin": "Gold Souq"}],
                    "total": 1,
                },
            )
        )

        result = await rta_tools.rta_search_bus_routes(
            route_number="27",
            origin="Gold Souq",
            limit=20,
        )

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 1
        assert data["routes"] == [{"route_number": "27", "origin": "Gold Souq"}]
        assert route.calls[0].request.url.params["filter"] == (
            "route_number=27 AND origin=Gold Souq"
        )

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_search_bus_routes_returns_upstream_error(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_bus_routes-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await rta_tools.rta_search_bus_routes(route_number="27")

        assert route.called
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_upstream_failure_is_structured(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await rta_tools.rta_search_metro_stations()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_invalid_shape_is_structured(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(200, json={"data": "not-a-list"})
        )

        result = await rta_tools.rta_search_metro_stations()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_non_object_record_is_structured(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(200, json={"data": [42]})
        )

        result = await rta_tools.rta_search_metro_stations()

        assert result["success"] is False
        assert isinstance(result["error"], dict)
        assert result["error"]["status"] == "parse_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_rejects_more_records_than_requested(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(200, json={"data": [{"id": 1}, {"id": 2}], "total": 2})
        )

        result = await rta_tools.rta_search_metro_stations(limit=1)

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "parse_error"
        assert "requested limit 1" in str(error["reason"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_salik_tariff_includes_warning(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_salik_tariff-open-api").mock(
            return_value=Response(
                200,
                json={"data": [{"gate": "Al Garhoud", "tariff_aed": 4}], "total": 1},
            )
        )

        result = await rta_tools.rta_salik_tariff()
        data = result["data"]
        assert isinstance(data, dict)
        assert "balances" in data["warning"].lower() or "Smart Salik" in data["warning"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_salik_tariff_returns_upstream_error(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        route = respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_salik_tariff-open-api").mock(
            return_value=Response(503, text="temporarily unavailable")
        )

        result = await rta_tools.rta_salik_tariff()

        assert route.called
        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_salik_tariff_includes_vat_block(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_salik_tariff-open-api").mock(
            return_value=Response(
                200,
                json={"data": [{"gate": "Al Garhoud", "tariff_aed": 4}], "total": 1},
            )
        )

        result = await rta_tools.rta_salik_tariff()
        data = result["data"]
        assert isinstance(data, dict)
        vat = data["vat"]
        assert isinstance(vat, dict)
        assert vat["effective_date"] == "2026-06-01"
        assert vat["vat_rate"] == 0.05
        assert vat["standard_crossing_aed_incl_vat"] == 4.20
        assert vat["peak_crossing_aed_incl_vat"] == 6.30
        assert "source_urls" in vat

    @pytest.mark.asyncio
    @respx.mock
    async def test_rta_metro_stations_includes_upcoming_line_notes(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(200, json=_token_payload()))
        respx.get(f"{DUBAI_PULSE_API_BASE}/open/rta/rta_metro_stations-open-api").mock(
            return_value=Response(
                200,
                json={"data": [{"name": "Burj Khalifa", "line": "Red"}], "total": 1},
            )
        )

        result = await rta_tools.rta_search_metro_stations(line="Red")
        data = result["data"]
        assert isinstance(data, dict)
        notes = data["upcoming_line_notes"]
        assert isinstance(notes, dict)
        assert "2029-09-09" in notes["blue_line"]
        assert "2032-09-09" in notes["gold_line"]


class TestRtaGtfsStaticUrl:
    @pytest.mark.asyncio
    async def test_returns_anonymous_7z_download(self) -> None:
        # No credentials and no network needed for the URL helper.
        result = await rta_tools.rta_gtfs_static_url()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["download_auth_required"] is False
        assert str(data["download_url"]).endswith(".7z")
        assert data["archive_format"] == "7z"
        assert "py7zr" in str(data["extraction_hint"])
        assert "GTFS_20250823" in str(data["feed_version_note"])
        assert "2026-09-05" in str(data["feed_version_note"])
        assert "fresher" in str(data["staleness_note"])
        assert data["query_api_auth_required"] is True
        assert data["gtfs_realtime_available"] is False
        assert result["retrieved_at"] == "2026-09-05"

    @pytest.mark.asyncio
    async def test_transitland_mirror_marked_dead(self) -> None:
        result = await rta_tools.rta_gtfs_static_url()
        data = result["data"]
        assert isinstance(data, dict)
        dead = data["dead_sources"]
        assert isinstance(dead, list)
        assert any("transit.land" in str(entry["url"]) for entry in dead)
        # The dead mirror must never be offered as the download URL.
        assert "transit.land" not in str(data["download_url"])


class TestDiscovery:
    def test_dld_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.dld import server as dld_server

        importlib.reload(dld_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("dld")}
        assert names == {
            "dld_search_transactions",
            "dld_search_rent_contracts",
            "dld_lookup_broker",
        }

    def test_rta_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.rta import server as rta_server

        importlib.reload(rta_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("rta")}
        assert names == {
            "rta_search_metro_stations",
            "rta_search_bus_routes",
            "rta_salik_tariff",
            "rta_gtfs_static_url",
        }
