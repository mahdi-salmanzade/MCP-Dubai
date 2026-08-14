"""Tests for the HttpClient retry and error wrapping."""

from __future__ import annotations

import logging
import subprocess
import sys

import pytest
import respx
from httpx import Response

from mcp_dubai.__main__ import _configure_logging
from mcp_dubai._shared.http_client import (
    HttpClient,
    HttpClientError,
    RateLimitError,
    protect_http_dependency_logging,
)


class TestHttpClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_returns_response(self) -> None:
        respx.get("https://example.com/data").mock(
            return_value=Response(200, json={"hello": "world"})
        )
        async with HttpClient() as client:
            response = await client.get("https://example.com/data")
        assert response.status_code == 200
        assert response.json() == {"hello": "world"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_raises_on_429(self) -> None:
        respx.get("https://example.com/data").mock(
            return_value=Response(429, text="Too Many Requests")
        )
        async with HttpClient() as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.get("https://example.com/data")
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_raises_on_500(self) -> None:
        respx.get("https://example.com/data").mock(
            return_value=Response(500, text="Internal Server Error")
        )
        async with HttpClient() as client:
            with pytest.raises(HttpClientError) as exc_info:
                await client.get("https://example.com/data")
        assert exc_info.value.status_code == 500
        assert not isinstance(exc_info.value, RateLimitError)

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_with_form_data(self) -> None:
        route = respx.post("https://example.com/oauth").mock(
            return_value=Response(200, json={"token": "abc"})
        )
        async with HttpClient() as client:
            response = await client.post(
                "https://example.com/oauth",
                data={"client_id": "x", "client_secret": "y"},
            )
        assert route.called
        assert response.json() == {"token": "abc"}

    @pytest.mark.asyncio
    async def test_must_be_used_as_context_manager(self) -> None:
        client = HttpClient()
        with pytest.raises(RuntimeError, match="async with"):
            _ = client.client

    @pytest.mark.asyncio
    @respx.mock
    async def test_default_user_agent_is_set(self) -> None:
        route = respx.get("https://example.com/check").mock(return_value=Response(200, json={}))
        async with HttpClient() as client:
            await client.get("https://example.com/check")
        assert "mcp-dubai" in route.calls.last.request.headers["user-agent"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_error_redacts_query_secret_echoed_in_response_body(self) -> None:
        secret = "super-secret-waqi-token"
        respx.get(f"https://example.com/data?token={secret}").mock(
            return_value=Response(
                403,
                text=f"Denied request /data?token={secret}; echoed={secret}",
            )
        )

        async with HttpClient() as client:
            with pytest.raises(HttpClientError) as exc_info:
                await client.get("https://example.com/data", params={"token": secret})

        message = str(exc_info.value)
        assert secret not in message
        assert "https://example.com/data?token=" not in message
        assert "token=[REDACTED]" in message

    @pytest.mark.asyncio
    @respx.mock
    async def test_error_redacts_bare_bearer_credential_from_body(self) -> None:
        secret = "bare-bearer-secret-123"
        respx.get("https://example.com/private").mock(
            return_value=Response(500, text=f"Rejected credential {secret}")
        )

        async with HttpClient() as client:
            with pytest.raises(HttpClientError) as exc_info:
                await client.get(
                    "https://example.com/private",
                    headers={"Authorization": f"Bearer {secret}"},
                )

        message = str(exc_info.value)
        assert secret not in message
        assert "Rejected credential [REDACTED]" in message

    def test_logging_configuration_suppresses_http_library_urls(self) -> None:
        httpx_logger = logging.getLogger("httpx")
        httpcore_logger = logging.getLogger("httpcore")
        previous_httpx_level = httpx_logger.level
        previous_httpcore_level = httpcore_logger.level
        try:
            httpx_logger.setLevel(logging.NOTSET)
            httpcore_logger.setLevel(logging.NOTSET)
            _configure_logging()

            assert httpx_logger.getEffectiveLevel() >= logging.WARNING
            assert httpcore_logger.getEffectiveLevel() >= logging.WARNING
        finally:
            httpx_logger.setLevel(previous_httpx_level)
            httpcore_logger.setLevel(previous_httpcore_level)

    def test_dependency_filter_redacts_token_if_host_reenables_info_logs(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        secret = "audit-secret-123"
        httpx_logger = logging.getLogger("httpx")
        previous_level = httpx_logger.level
        try:
            protect_http_dependency_logging()
            httpx_logger.setLevel(logging.INFO)
            with caplog.at_level(logging.INFO, logger="httpx"):
                httpx_logger.info(
                    'HTTP Request: GET %s "HTTP/1.1 200 OK"',
                    f"https://api.waqi.info/feed/here/?token={secret}",
                )
            output = caplog.text
            assert secret not in output
            assert "token=[REDACTED]" in output
        finally:
            httpx_logger.setLevel(previous_level)

    def test_embedded_server_import_installs_log_protection(self) -> None:
        code = """
import io
import logging

logging.basicConfig(level=logging.INFO)
from mcp_dubai.server import mcp

secret = "embedded-secret-456"
stream = io.StringIO()
handler = logging.StreamHandler(stream)
httpx_logger = logging.getLogger("httpx")
httpx_logger.handlers = [handler]
httpx_logger.propagate = False
httpx_logger.setLevel(logging.INFO)
httpx_logger.info("HTTP Request: GET %s", f"https://api.waqi.info/?token={secret}")
assert secret not in stream.getvalue(), stream.getvalue()
assert "token=[REDACTED]" in stream.getvalue(), stream.getvalue()
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
