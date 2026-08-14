"""Al-Quran Cloud client."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.quran_cloud import constants


class QuranCloudClient:
    """Async client for the Al-Quran Cloud API."""

    @staticmethod
    def _unwrap(payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise RuntimeError("Quran Cloud API error: top-level response is not an object")
        if payload.get("code") != 200:
            raise RuntimeError(f"Quran Cloud API error: {payload.get('status', payload)}")
        result = payload.get("data")
        if not isinstance(result, dict):
            raise RuntimeError("Quran Cloud API error: data is not an object")
        return result

    @staticmethod
    def _segment(value: str) -> str:
        """Encode a user-supplied value as exactly one URL path segment."""
        return quote(value, safe="")

    async def get_surah(self, number: int, edition: str) -> dict[str, Any]:
        """Get a full surah in a specific edition."""
        url = f"{constants.SURAH}/{number}/{self._segment(edition)}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def get_ayah(self, reference: str, edition: str) -> dict[str, Any]:
        """Get a single ayah by reference (e.g., '2:255' for Ayat al-Kursi)."""
        url = f"{constants.AYAH}/{self._segment(reference)}/{self._segment(edition)}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def get_juz(self, number: int, edition: str) -> dict[str, Any]:
        """Get a full juz (1 to 30) in a specific edition."""
        url = f"{constants.JUZ}/{number}/{self._segment(edition)}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def search(
        self,
        query: str,
        surah_filter: str = "all",
        edition: str = "en",
        limit: int = constants.DEFAULT_SEARCH_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search the Quran and return one bounded slice of upstream matches."""
        if not 1 <= limit <= constants.MAX_SEARCH_LIMIT:
            raise ValueError(f"limit must be 1 to {constants.MAX_SEARCH_LIMIT}, got {limit}")
        if offset < 0:
            raise ValueError(f"offset must be at least 0, got {offset}")
        url = (
            f"{constants.SEARCH}/{self._segment(query)}/"
            f"{self._segment(surah_filter)}/{self._segment(edition)}"
        )
        async with HttpClient() as client:
            response = await client.get(url)
        result = self._unwrap(response.json())
        matches = result.get("matches", [])
        if not isinstance(matches, list):
            raise RuntimeError("Quran Cloud API error: search matches is not a list")

        upstream_count = result.get("count")
        if upstream_count is not None:
            if (
                isinstance(upstream_count, bool)
                or not isinstance(upstream_count, int)
                or upstream_count < 0
            ):
                raise RuntimeError(
                    "Quran Cloud API error: search count is not a non-negative integer"
                )
            if upstream_count != len(matches):
                raise RuntimeError(
                    "Quran Cloud API error: search count does not match the returned matches"
                )

        # This endpoint returns its complete match set in one response, so the
        # locally paginated total must agree with the actual list length.
        total = len(matches)
        page = matches[offset : offset + limit]
        has_more = offset + len(page) < total
        next_offset = offset + len(page) if has_more else None
        return {
            **result,
            "count": total,
            "matches": page,
            "total": total,
            "returned": len(page),
            "offset": offset,
            "next_offset": next_offset,
            "truncated": has_more,
        }
