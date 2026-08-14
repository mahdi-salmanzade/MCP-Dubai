"""
Async HTTP client with retry, backoff, and structured errors.

A thin wrapper over httpx.AsyncClient that:
- retries on transient network errors using tenacity exponential backoff,
- raises typed errors (HttpClientError, RateLimitError) on >=400 responses,
- defaults to a project user-agent and a 30s timeout,
- supports use as an async context manager.

Used by every feature client. Centralising the retry policy here means a
single place to tune backoff for the whole project.
"""

from __future__ import annotations

import logging
import re
from types import TracebackType
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from mcp_dubai._shared.constants import (
    HTTP_DEFAULT_MAX_RETRIES,
    HTTP_DEFAULT_TIMEOUT_SECONDS,
    HTTP_USER_AGENT,
)

logger = logging.getLogger(__name__)

_ERROR_EXCERPT_SCAN_LIMIT = 4096
_ERROR_EXCERPT_OUTPUT_LIMIT = 200
_SENSITIVE_NAME_RE = re.compile(r"[^a-z0-9]+")
_SENSITIVE_NAMES = frozenset(
    {
        "accesstoken",
        "apikey",
        "authorization",
        "clientsecret",
        "proxyauthorization",
        "refreshtoken",
        "subscriptionkey",
        "token",
    }
)
_SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)((?:access[_-]?token|api[_-]?key|authorization|client[_-]?secret|"
    r"proxy[_-]?authorization|refresh[_-]?token|subscription[_-]?key|token)"
    r"[\"']?\s*[:=]\s*[\"']?)[^&,\s\"'<>}]+"
)
_BEARER_TOKEN_RE = re.compile(r"(?i)(\bbearer\s+)[a-z0-9._~+/=-]+")


class _CredentialRedactionFilter(logging.Filter):
    """Remove query and bearer credentials from dependency log records."""

    _mcp_dubai_credential_filter = True

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rendered = record.getMessage()
        except Exception:
            return True
        rendered = _SENSITIVE_ASSIGNMENT_RE.sub(r"\1[REDACTED]", rendered)
        rendered = _BEARER_TOKEN_RE.sub(r"\1[REDACTED]", rendered)
        record.msg = rendered
        record.args = ()
        return True


def protect_http_dependency_logging() -> None:
    """Install safe defaults for HTTPX/HTTPCore in CLI and embedded use."""
    logger_names = {"httpx", "httpcore"}
    logger_names.update(
        name
        for name in logging.Logger.manager.loggerDict
        if name.startswith("httpx.") or name.startswith("httpcore.")
    )
    for name in logger_names:
        dependency_logger = logging.getLogger(name)
        if dependency_logger.getEffectiveLevel() < logging.WARNING:
            dependency_logger.setLevel(logging.WARNING)
        if not any(
            getattr(log_filter, "_mcp_dubai_credential_filter", False)
            for log_filter in dependency_logger.filters
        ):
            dependency_logger.addFilter(_CredentialRedactionFilter())


# The package supports direct import and mounting, which bypasses the CLI's
# logging setup. Protect dependency logs as soon as the shared client loads.
protect_http_dependency_logging()


def _is_sensitive_name(name: str) -> bool:
    normalized = _SENSITIVE_NAME_RE.sub("", name.casefold())
    return normalized in _SENSITIVE_NAMES or normalized.endswith("token")


def _redact_error_excerpt(response: httpx.Response) -> str:
    """Return a short response-body excerpt with request credentials removed."""
    excerpt = response.text[:_ERROR_EXCERPT_SCAN_LIMIT]

    # Redact the concrete values from sensitive request query parameters and
    # headers first. This also catches an upstream that echoes a credential
    # without its original ``token=`` or ``Authorization:`` label.
    secret_values: set[str] = {
        value
        for key, value in response.url.params.multi_items()
        if value and _is_sensitive_name(key)
    }
    if response.request is not None:
        for key, value in response.request.headers.multi_items():
            if not value or not _is_sensitive_name(key):
                continue
            secret_values.add(value)

            # Authorization values include an authentication scheme. An
            # upstream may echo only the credential, rather than the complete
            # ``Bearer <credential>`` header, so redact both representations.
            normalized_key = _SENSITIVE_NAME_RE.sub("", key.casefold())
            if normalized_key in {"authorization", "proxyauthorization"}:
                parts = value.split(maxsplit=1)
                if len(parts) == 2 and parts[1]:
                    secret_values.add(parts[1])
    for secret in sorted(secret_values, key=len, reverse=True):
        excerpt = excerpt.replace(secret, "[REDACTED]")

    # Also handle credentials echoed by an upstream under a conventional key,
    # even if that value was not present in the outgoing URL or headers.
    excerpt = _SENSITIVE_ASSIGNMENT_RE.sub(r"\1[REDACTED]", excerpt)
    excerpt = _BEARER_TOKEN_RE.sub(r"\1[REDACTED]", excerpt)
    return excerpt[:_ERROR_EXCERPT_OUTPUT_LIMIT]


class HttpClientError(Exception):
    """Raised on non-2xx responses that are not rate limits."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(HttpClientError):
    """Raised on HTTP 429 responses."""


class HttpClient:
    """
    Async HTTP client with sensible defaults for Dubai APIs.

    Always use as an async context manager so the underlying httpx client
    is closed on exit, even if an error is raised.

    Example:
        async with HttpClient() as client:
            response = await client.get("https://example.com/data")
            payload = response.json()
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = HTTP_DEFAULT_TIMEOUT_SECONDS,
        headers: dict[str, str] | None = None,
        follow_redirects: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.default_headers: dict[str, str] = {"User-Agent": HTTP_USER_AGENT}
        if headers:
            self.default_headers.update(headers)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> HttpClient:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.default_headers,
            follow_redirects=self.follow_redirects,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError(
                "HttpClient must be used inside `async with HttpClient() as client:`"
            )
        return self._client

    @retry(
        stop=stop_after_attempt(HTTP_DEFAULT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """GET with retry on transient network failures."""
        response = await self.client.get(url, params=params, headers=headers)
        self._raise_for_status(response)
        return response

    @retry(
        stop=stop_after_attempt(HTTP_DEFAULT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """POST with retry on transient network failures."""
        response = await self.client.post(
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return

        # Never interpolate the raw URL into an exception: query strings can
        # carry secrets (the WAQI air-quality upstream takes ?token=<key>), and
        # these messages reach both the server log and the MCP client, which
        # means they reach the LLM's context.
        safe_url = response.url.copy_with(query=None)
        safe_excerpt = _redact_error_excerpt(response)
        if response.status_code == 429:
            raise RateLimitError(
                f"Rate limited by {safe_url}: {safe_excerpt}",
                status_code=429,
            )
        if response.status_code >= 400:
            raise HttpClientError(
                f"HTTP {response.status_code} from {safe_url}: {safe_excerpt}",
                status_code=response.status_code,
            )
