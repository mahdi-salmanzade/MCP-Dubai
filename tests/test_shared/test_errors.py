"""Tests for the shared upstream error helpers."""

from __future__ import annotations

import httpx

from mcp_dubai._shared.errors import (
    cloudflare_blocked_response,
    upstream_error_response,
)
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError


class TestUpstreamErrorResponse:
    def test_plain_exception_maps_to_upstream_error(self) -> None:
        result = upstream_error_response(ValueError("boom"))
        assert result["success"] is False
        assert result["error"]["status"] == "upstream_error"
        assert "boom" in result["error"]["reason"]

    def test_explicit_status_overrides_classification(self) -> None:
        result = upstream_error_response(ValueError("x"), status="custom_status")
        assert result["error"]["status"] == "custom_status"

    def test_verify_at_is_included(self) -> None:
        result = upstream_error_response(
            ValueError("x"),
            verify_at="https://example.ae",
        )
        assert result["error"]["verify_at"] == "https://example.ae"

    def test_rate_limit_maps_to_rate_limited(self) -> None:
        err = RateLimitError("429 from upstream", status_code=429)
        result = upstream_error_response(err)
        assert result["error"]["status"] == "rate_limited"

    def test_http_403_maps_to_upstream_blocked(self) -> None:
        err = HttpClientError("HTTP 403 from upstream", status_code=403)
        result = upstream_error_response(err)
        assert result["error"]["status"] == "upstream_blocked"

    def test_cloudflare_page_maps_to_upstream_blocked(self) -> None:
        err = HttpClientError(
            "HTTP 403 from upstream: Just a moment...", status_code=403
        )
        result = upstream_error_response(err)
        assert result["error"]["status"] == "upstream_blocked"

    def test_503_maps_to_upstream_blocked(self) -> None:
        err = HttpClientError("HTTP 503 from upstream", status_code=503)
        result = upstream_error_response(err)
        assert result["error"]["status"] == "upstream_blocked"

    def test_other_http_error_maps_to_upstream_error(self) -> None:
        err = HttpClientError("HTTP 500 from upstream", status_code=500)
        result = upstream_error_response(err)
        assert result["error"]["status"] == "upstream_error"

    def test_timeout_text_maps_to_upstream_timeout(self) -> None:
        err = httpx.ConnectTimeout("timed out after 30s")
        result = upstream_error_response(err)
        assert result["error"]["status"] == "upstream_timeout"

    def test_reason_is_truncated_to_400_chars(self) -> None:
        huge = "x" * 1000
        result = upstream_error_response(ValueError(huge))
        assert len(result["error"]["reason"]) == 400


class TestCloudflareBlockedResponse:
    def test_basic_envelope(self) -> None:
        result = cloudflare_blocked_response("api.example.com")
        assert result["success"] is False
        assert result["error"]["status"] == "upstream_blocked"
        assert "Cloudflare" in result["error"]["reason"]
        assert "api.example.com" in result["error"]["reason"]

    def test_verify_at_is_optional(self) -> None:
        result = cloudflare_blocked_response(
            "api.example.com",
            verify_at="https://example.com",
        )
        assert result["error"]["verify_at"] == "https://example.com"


class TestImportSurface:
    def test_exports_from_shared_package(self) -> None:
        from mcp_dubai._shared import cloudflare_blocked_response as cbr
        from mcp_dubai._shared import upstream_error_response as uer

        assert callable(uer)
        assert callable(cbr)
