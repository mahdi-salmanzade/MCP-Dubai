"""Phase 4 Tier 1 tests: dubai_pulse base client + dld + rta."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.constants import DUBAI_PULSE_API_BASE, DUBAI_PULSE_TOKEN_URL
from mcp_dubai.data.dld import tools as dld_tools
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


class TestRtaGtfsStaticUrl:
    @pytest.mark.asyncio
    async def test_returns_anonymous_mirror(self) -> None:
        # No credentials needed for the URL helper.
        result = await rta_tools.rta_gtfs_static_url()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["transitland_mirror_auth_required"] is False
        assert "transit.land" in str(data["transitland_mirror_url"])
        assert data["gtfs_realtime_available"] is False


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
