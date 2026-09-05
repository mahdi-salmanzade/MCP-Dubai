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

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any
from weakref import WeakKeyDictionary

import httpx

from mcp_dubai._shared.constants import (
    DUBAI_PULSE_TOKEN_REFRESH_BUFFER_SECONDS,
    DUBAI_PULSE_TOKEN_TTL_SECONDS,
    DUBAI_PULSE_TOKEN_URL,
)

logger = logging.getLogger(__name__)

_TOKEN_REFRESH_FAILURE_COOLDOWN_SECONDS = 1.0


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
    expires_at_monotonic: float
    credential_fingerprint: str

    def is_valid_for(self, credential_fingerprint: str) -> bool:
        """Return whether this token is fresh and belongs to the active credentials."""
        return self.credential_fingerprint == credential_fingerprint and time.monotonic() < (
            self.expires_at_monotonic - DUBAI_PULSE_TOKEN_REFRESH_BUFFER_SECONDS
        )


@dataclass(frozen=True)
class TokenRefreshFailure:
    """Safe failed-refresh result shared by callers in the same burst."""

    credential_fingerprint: str
    message: str
    retry_after_monotonic: float

    def is_active_for(self, credential_fingerprint: str) -> bool:
        """Return whether callers should reuse this failed refresh."""
        return (
            self.credential_fingerprint == credential_fingerprint
            and time.monotonic() < self.retry_after_monotonic
        )


class DubaiPulseAuth:
    """
    Dubai Pulse OAuth2 client_credentials authenticator.

    Reads credentials lazily from the environment on first use, so changing
    env vars between calls is honoured (important for tests). The token is
    cached in memory and refreshed automatically before expiry.
    """

    def __init__(self) -> None:
        self._token_cache: TokenCache | None = None
        # A long-running MCP process can receive many tool calls concurrently.
        # Only one caller per event loop should refresh an expired OAuth token.
        # The package-level auth singleton can also be embedded in hosts that
        # create sequential event loops, so never retain one loop-bound lock.
        self._refresh_locks: WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
            WeakKeyDictionary()
        )
        self._refresh_locks_guard = Lock()
        self._refresh_failure: TokenRefreshFailure | None = None

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
        """Drop cached token and refresh failure state."""
        self._token_cache = None
        self._refresh_failure = None

    def _credential_fingerprint(self) -> str:
        """Hash the active credential pair without retaining another plaintext copy."""
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise DubaiPulseCredentialsMissingError()
        material = f"{client_id}\0{client_secret}".encode()
        return hashlib.sha256(material).hexdigest()

    def _refresh_lock_for_current_loop(self) -> asyncio.Lock:
        """Return the single-flight lock owned by the active event loop."""
        loop = asyncio.get_running_loop()
        with self._refresh_locks_guard:
            for closed_loop in [known for known in self._refresh_locks if known.is_closed()]:
                del self._refresh_locks[closed_loop]
            lock = self._refresh_locks.get(loop)
            if lock is None:
                lock = asyncio.Lock()
                self._refresh_locks[loop] = lock
            return lock

    async def get_token(self) -> str:
        """
        Return a valid bearer token, refreshing if needed.

        Raises:
            DubaiPulseCredentialsMissingError: if env vars are not set.
            DubaiPulseAuthError: if the token endpoint returns an error.
        """
        self.require_credentials()
        credential_fingerprint = self._credential_fingerprint()

        if self._token_cache is not None and self._token_cache.is_valid_for(credential_fingerprint):
            return self._token_cache.access_token

        async with self._refresh_lock_for_current_loop():
            # Credentials may have changed while this caller waited. Re-read and
            # double-check the cache so a burst produces exactly one token POST.
            self.require_credentials()
            credential_fingerprint = self._credential_fingerprint()
            if self._token_cache is not None and self._token_cache.is_valid_for(
                credential_fingerprint
            ):
                return self._token_cache.access_token

            failure = self._refresh_failure
            if failure is not None and failure.is_active_for(credential_fingerprint):
                # Reuse the safe result briefly instead of issuing one
                # sequential POST per caller in a burst. The cooldown is
                # credential-bound, so changed credentials retry immediately.
                raise DubaiPulseAuthError(failure.message)

            try:
                access_token = await self._fetch_token(credential_fingerprint)
            except DubaiPulseAuthError as exc:
                self._refresh_failure = TokenRefreshFailure(
                    credential_fingerprint=credential_fingerprint,
                    message=str(exc),
                    retry_after_monotonic=(
                        time.monotonic() + _TOKEN_REFRESH_FAILURE_COOLDOWN_SECONDS
                    ),
                )
                raise

            self._refresh_failure = None
            return access_token

    async def _fetch_token(self, credential_fingerprint: str) -> str:
        """Fetch and cache one token; callers serialize and coalesce this method."""
        logger.debug("Fetching new Dubai Pulse access token")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    DUBAI_PULSE_TOKEN_URL,
                    params={"grant_type": "client_credentials"},
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
        except httpx.HTTPError as exc:
            # Do not include request URLs, form bodies, or upstream response
            # bodies here: OAuth endpoints handle the project's secrets.
            raise DubaiPulseAuthError("Dubai Pulse token request failed") from exc

        if response.status_code != 200:
            raise DubaiPulseAuthError(
                f"Dubai Pulse token fetch failed: HTTP {response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise DubaiPulseAuthError("Dubai Pulse token response was not valid JSON") from exc

        if not isinstance(payload, dict):
            raise DubaiPulseAuthError("Dubai Pulse token response had an invalid shape")
        raw_token = payload.get("access_token")
        if not raw_token or not isinstance(raw_token, str):
            raise DubaiPulseAuthError("Dubai Pulse token response missing 'access_token'")
        access_token: str = raw_token

        try:
            expires_in = int(payload.get("expires_in", DUBAI_PULSE_TOKEN_TTL_SECONDS))
        except (TypeError, ValueError, OverflowError):
            expires_in = DUBAI_PULSE_TOKEN_TTL_SECONDS
        # Never let malformed or arbitrarily large upstream integers overflow
        # monotonic arithmetic or retain a bearer token indefinitely. Refreshing
        # earlier than a longer advertised expiry remains safe.
        expires_in = min(expires_in, DUBAI_PULSE_TOKEN_TTL_SECONDS)
        self._token_cache = TokenCache(
            access_token=access_token,
            expires_at_monotonic=time.monotonic() + max(expires_in, 0),
            credential_fingerprint=credential_fingerprint,
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
