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
        if response.status_code == 429:
            raise RateLimitError(
                f"Rate limited by {response.url}: {response.text[:200]}",
                status_code=429,
            )
        if response.status_code >= 400:
            raise HttpClientError(
                f"HTTP {response.status_code} from {response.url}: {response.text[:200]}",
                status_code=response.status_code,
            )
