"""Tests for the HttpClient retry and error wrapping."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.http_client import (
    HttpClient,
    HttpClientError,
    RateLimitError,
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
