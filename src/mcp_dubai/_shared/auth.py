"""
Dubai Pulse OAuth2 client_credentials authentication.

    POST {DUBAI_PULSE_TOKEN_URL}?grant_type=client_credentials
    Form: client_id={KEY}&client_secret={SECRET}
    -> { "access_token": "...", "expires_in": 1800 }

    GET .../{open|shared}/{org}/{dataset-slug}
    Header: Authorization: Bearer {token}

Key design point: tools must NOT crash when credentials are missing. They
call `availability()` and fail soft with a structured error so the MCP
client can render a help message. The server must always start, even on a
fresh machine with no env vars.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from mcp_dubai._shared.constants import (
    DUBAI_PULSE_TOKEN_REFRESH_BUFFER_SECONDS,
    DUBAI_PULSE_TOKEN_TTL_SECONDS,
    DUBAI_PULSE_TOKEN_URL,
)

logger = logging.getLogger(__name__)


class DubaiPulseAuthError(Exception):
    """Raised when the OAuth token endpoint returns an error."""


class DubaiPulseCredentialsMissingError(DubaiPulseAuthError):
    """
    Raised by `require_credentials()` when env vars are not set.

    Tools should NOT call `require_credentials()`. They should call
    `availability()` and return a structured ToolResponse.fail instead.
    """

    def __init__(self) -> None:
        super().__init__(
            "Dubai Pulse credentials are not configured. Set "
            "MCP_DUBAI_PULSE_CLIENT_ID and MCP_DUBAI_PULSE_CLIENT_SECRET. "
            "Get credentials by requesting dataset access at https://data.dubai."
        )


@dataclass
class TokenCache:
    """Cached OAuth token with expiry tracking."""

    access_token: str
    expires_at: float

    @property
    def is_valid(self) -> bool:
        return time.time() < (self.expires_at - DUBAI_PULSE_TOKEN_REFRESH_BUFFER_SECONDS)


class DubaiPulseAuth:
    """
    Dubai Pulse OAuth2 client_credentials authenticator.

    Reads credentials lazily from the environment on first use, so changing
    env vars between calls is honoured (important for tests). The token is
    cached in memory and refreshed automatically before expiry.
    """

    def __init__(self) -> None:
        self._token_cache: TokenCache | None = None

    @property
    def client_id(self) -> str | None:
        return os.getenv("MCP_DUBAI_PULSE_CLIENT_ID") or None

    @property
    def client_secret(self) -> str | None:
        return os.getenv("MCP_DUBAI_PULSE_CLIENT_SECRET") or None

    @property
    def is_configured(self) -> bool:
        """True if both env vars are set to non-empty values."""
        return bool(self.client_id and self.client_secret)

    def availability(self) -> dict[str, Any]:
        """
        Return a structured availability descriptor for graceful degradation.

        Tools call this instead of `require_credentials()` so they can
        return ToolResponse.fail with a helpful error rendered by the MCP
        client. Never raises.
        """
        if self.is_configured:
            return {"status": "ready"}
        return {
            "status": "credentials_missing",
            "reason": (
                "Dubai Pulse credentials are not configured. This tool requires "
                "MCP_DUBAI_PULSE_CLIENT_ID and MCP_DUBAI_PULSE_CLIENT_SECRET. "
                "Get credentials by requesting dataset access at https://data.dubai."
            ),
            "docs": ("https://github.com/mahdi-salmanzade/MCP-Dubai#dubai-pulse-credentials"),
        }

    def require_credentials(self) -> None:
        """
        Raise DubaiPulseCredentialsMissingError if credentials are not configured.

        Use only inside the auth module itself. Tools should call
        `availability()` and fail soft.
        """
        if not self.is_configured:
            raise DubaiPulseCredentialsMissingError()

    def reset_cache(self) -> None:
        """Drop the cached token. Used by tests after monkeypatching env."""
        self._token_cache = None

    async def get_token(self) -> str:
        """
        Return a valid bearer token, refreshing if needed.

        Raises:
            DubaiPulseCredentialsMissingError: if env vars are not set.
            DubaiPulseAuthError: if the token endpoint returns an error.
        """
        self.require_credentials()

        if self._token_cache is not None and self._token_cache.is_valid:
            return self._token_cache.access_token

        logger.debug("Fetching new Dubai Pulse access token")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DUBAI_PULSE_TOKEN_URL,
                params={"grant_type": "client_credentials"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

        if response.status_code != 200:
            raise DubaiPulseAuthError(
                f"Dubai Pulse token fetch failed: HTTP {response.status_code} {response.text[:200]}"
            )

        payload = response.json()
        raw_token = payload.get("access_token")
        if not raw_token or not isinstance(raw_token, str):
            raise DubaiPulseAuthError(
                f"Dubai Pulse token response missing 'access_token': {payload}"
            )
        access_token: str = raw_token

        expires_in = int(payload.get("expires_in", DUBAI_PULSE_TOKEN_TTL_SECONDS))
        self._token_cache = TokenCache(
            access_token=access_token,
            expires_at=time.time() + expires_in,
        )
        logger.debug("Dubai Pulse token cached, expires in %ds", expires_in)
        return access_token

    async def get_auth_header(self) -> dict[str, str]:
        """Return a ready-to-use Authorization header dict."""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}


# ----------------------------------------------------------------------------
# Singleton accessor
# ----------------------------------------------------------------------------
_auth_instance: DubaiPulseAuth | None = None


def get_dubai_pulse_auth() -> DubaiPulseAuth:
    """
    Return the singleton DubaiPulseAuth instance.

    Tests that monkeypatch the env vars must call `reset_dubai_pulse_auth()`
    afterwards (or use the `reset_singletons` fixture in tests/conftest.py),
    otherwise the cached singleton still has the previous configuration.
    """
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = DubaiPulseAuth()
    return _auth_instance


def reset_dubai_pulse_auth() -> None:
    """Drop the singleton. Used by the test fixture."""
    global _auth_instance
    _auth_instance = None
