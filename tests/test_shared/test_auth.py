"""Tests for DubaiPulseAuth and the graceful-degradation pattern."""

from __future__ import annotations

import asyncio

import pytest
import respx
from httpx import ConnectError, Response

import mcp_dubai._shared.auth as auth_module
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

    def test_fingerprint_rejects_partial_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_ID", "client-id")
        monkeypatch.delenv("MCP_DUBAI_PULSE_CLIENT_SECRET", raising=False)

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseCredentialsMissingError):
            auth._credential_fingerprint()


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
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                401,
                json={
                    "error": "invalid_client",
                    "client_secret": "must-never-escape",
                    "access_token": "also-secret",
                },
            )
        )

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError) as exc_info:
            await auth.get_token()
        assert "HTTP 401" in str(exc_info.value)
        assert "must-never-escape" not in str(exc_info.value)
        assert "also-secret" not in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_token_network_error_is_sanitized(self, configured_dubai_pulse_env: None) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            side_effect=ConnectError("upstream URL included client_secret=must-never-escape")
        )

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError) as exc_info:
            await auth.get_token()

        assert str(exc_info.value) == "Dubai Pulse token request failed"
        assert "must-never-escape" not in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize(
        ("response", "expected_message"),
        [
            (Response(200, text="<html>gateway failure</html>"), "not valid JSON"),
            (Response(200, json=["unexpected"]), "invalid shape"),
        ],
    )
    async def test_token_rejects_malformed_success_response(
        self,
        configured_dubai_pulse_env: None,
        response: Response,
        expected_message: str,
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(return_value=response)

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError, match=expected_message):
            await auth.get_token()

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("expiry", ['"not-a-number"', "1e999", str(10**400)])
    async def test_invalid_expiry_uses_default_ttl(
        self, configured_dubai_pulse_env: None, expiry: str
    ) -> None:
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                200,
                content='{"access_token": "cached-token", "expires_in": ' + expiry + "}",
            )
        )

        auth = DubaiPulseAuth()
        assert await auth.get_token() == "cached-token"
        assert await auth.get_token() == "cached-token"
        assert route.call_count == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_nonpositive_expiry_forces_refresh(
        self, configured_dubai_pulse_env: None
    ) -> None:
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            side_effect=[
                Response(200, json={"access_token": "stale-token", "expires_in": -1}),
                Response(200, json={"access_token": "fresh-token", "expires_in": 1800}),
            ]
        )

        auth = DubaiPulseAuth()
        assert await auth.get_token() == "stale-token"
        assert await auth.get_token() == "fresh-token"
        assert route.call_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_concurrent_refresh_is_single_flight(
        self, configured_dubai_pulse_env: None
    ) -> None:
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                200,
                json={"access_token": "shared-token", "expires_in": 1800},
            )
        )

        auth = DubaiPulseAuth()
        tokens = await asyncio.gather(*(auth.get_token() for _ in range(5)))

        assert tokens == ["shared-token"] * 5
        assert route.call_count == 1

    def test_concurrent_refresh_survives_sequential_event_loops(
        self,
        configured_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A package-level auth singleton must not retain another loop's lock."""
        from mcp_dubai._shared.auth import TokenCache

        auth = DubaiPulseAuth()
        fetch_count = 0

        async def fake_fetch(credential_fingerprint: str) -> str:
            nonlocal fetch_count
            fetch_count += 1
            token = f"loop-token-{fetch_count}"
            # Yield while holding the refresh lock so the other caller waits
            # and binds that loop's lock deterministically.
            await asyncio.sleep(0)
            auth._token_cache = TokenCache(
                access_token=token,
                expires_at_monotonic=float("inf"),
                credential_fingerprint=credential_fingerprint,
            )
            return token

        monkeypatch.setattr(auth, "_fetch_token", fake_fetch)

        async def concurrent_burst() -> list[str]:
            return await asyncio.gather(auth.get_token(), auth.get_token())

        assert asyncio.run(concurrent_burst()) == ["loop-token-1", "loop-token-1"]
        auth.reset_cache()
        assert asyncio.run(concurrent_burst()) == ["loop-token-2", "loop-token-2"]
        assert fetch_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_concurrent_failed_refresh_is_single_flight(
        self, configured_dubai_pulse_env: None
    ) -> None:
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(401, json={"error": "invalid_client"})
        )

        auth = DubaiPulseAuth()
        results = await asyncio.gather(
            *(auth.get_token() for _ in range(5)),
            return_exceptions=True,
        )

        assert all(isinstance(result, DubaiPulseAuthError) for result in results)
        assert {str(result) for result in results} == {"Dubai Pulse token fetch failed: HTTP 401"}
        assert route.call_count == 1

        # Explicit cache invalidation permits an immediate retry; otherwise a
        # short cooldown prevents a failing endpoint from being hammered.
        auth.reset_cache()
        with pytest.raises(DubaiPulseAuthError):
            await auth.get_token()
        assert route.call_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_failed_refresh_retries_after_cooldown(
        self,
        configured_dubai_pulse_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monotonic_now = [100.0]
        monkeypatch.setattr(auth_module.time, "monotonic", lambda: monotonic_now[0])
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            side_effect=[
                Response(503, json={"error": "temporarily_unavailable"}),
                Response(200, json={"access_token": "recovered-token", "expires_in": 1800}),
            ]
        )

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError, match="HTTP 503"):
            await auth.get_token()
        with pytest.raises(DubaiPulseAuthError, match="HTTP 503"):
            await auth.get_token()
        assert route.call_count == 1

        monotonic_now[0] = 101.1
        assert await auth.get_token() == "recovered-token"
        assert route.call_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_changed_credentials_bypass_failed_refresh_cooldown(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_ID", "first-id")
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "first-secret")
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            side_effect=[
                Response(401, json={"error": "invalid_client"}),
                Response(200, json={"access_token": "new-token", "expires_in": 1800}),
            ]
        )

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError, match="HTTP 401"):
            await auth.get_token()

        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "second-secret")
        assert await auth.get_token() == "new-token"
        assert route.call_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_cached_token_is_bound_to_credentials(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_ID", "first-id")
        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "first-secret")
        route = respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            side_effect=[
                Response(200, json={"access_token": "first-token", "expires_in": 1800}),
                Response(200, json={"access_token": "second-token", "expires_in": 1800}),
            ]
        )

        auth = DubaiPulseAuth()
        assert await auth.get_token() == "first-token"

        monkeypatch.setenv("MCP_DUBAI_PULSE_CLIENT_SECRET", "second-secret")
        assert await auth.get_token() == "second-token"
        assert route.call_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_token_error_does_not_echo_payload(
        self, configured_dubai_pulse_env: None
    ) -> None:
        respx.post(DUBAI_PULSE_TOKEN_URL).mock(
            return_value=Response(
                200,
                json={"client_secret": "must-never-escape", "error": "bad response"},
            )
        )

        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseAuthError) as exc_info:
            await auth.get_token()
        assert "missing 'access_token'" in str(exc_info.value)
        assert "must-never-escape" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_token_without_credentials_raises(self, clean_dubai_pulse_env: None) -> None:
        auth = DubaiPulseAuth()
        with pytest.raises(DubaiPulseCredentialsMissingError):
            await auth.get_token()
