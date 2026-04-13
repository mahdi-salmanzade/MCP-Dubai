"""Tests for DubaiPulseAuth and the graceful-degradation pattern."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.auth import (
    DubaiPulseAuth,
    DubaiPulseAuthError,
    DubaiPulseCredentialsMissingError,
    get_dubai_pulse_auth,
)
from mcp_dubai._shared.constants import DUBAI_PULSE_TOKEN_URL


class TestAvailability:
    def test_unconfigured_returns_credentials_missing(self, clean_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        result = auth.availability()
        assert result["status"] == "credentials_missing"
        assert "MCP_DUBAI_PULSE_CLIENT_ID" in result["reason"]
        assert "docs" in result

    def test_configured_returns_ready(self, configured_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        result = auth.availability()
        assert result["status"] == "ready"

    def test_availability_never_raises(self, clean_dubai_pulse_env: None) -> None:
        """Critical Pattern 2 invariant: availability() never raises."""
        auth = DubaiPulseAuth()
        # Should not raise even with no env at all
        result = auth.availability()
        assert isinstance(result, dict)


class TestRequireCredentials:
    def test_unconfigured_raises(self, clean_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseCredentialsMissingError):
            auth.require_credentials()

    def test_configured_does_not_raise(self, configured_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        auth.require_credentials()  # should not raise


class TestSingleton:
    def test_returns_same_instance(self) -> None:
        a = get_dubai_pulse_auth()
        b = get_dubai_pulse_auth()
        assert a is b

    def test_reset_drops_singleton(self) -> None:
        from mcp_dubai._shared.auth import reset_dubai_pulse_auth

        a = get_dubai_pulse_auth()
        reset_dubai_pulse_auth()
        b = get_dubai_pulse_auth()
        assert a is not b


class TestTokenFetch:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_token_caches_response(self, configured_dubai_pulse_env: None) -> None:
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                200,
                json={"access_token": "fake-token-abc", "expires_in": 1800},
            )
        )

        auth = DubaiPulseAuth()
        token1 = await auth.get_token()
        token2 = await auth.get_token()  # should hit the cache

        assert token1 == "fake-token-abc"
        assert token2 == "fake-token-abc"
        assert route.call_count == 1  # cache prevented second call

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_auth_header_returns_bearer(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                200,
                json={"access_token": "xyz", "expires_in": 1800},
            )
        )

        auth = DubaiPulseAuth()
        header = await auth.get_auth_header()
        assert header == {"Authorization": "Bearer xyz"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_token_endpoint_failure_raises(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=Response(401, text="invalid_client"))

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError):
            await auth.get_token()

    @pytest.mark.asyncio
    async def test_get_token_without_credentials_raises(self, clean_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseCredentialsMissingError):
            await auth.get_token()
