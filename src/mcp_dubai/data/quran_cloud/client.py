"""Al-Quran Cloud client."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.quran_cloud import constants


class QuranCloudClient:
    """Async client for the Al-Quran Cloud API."""

    @staticmethod
    def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("code") != 200:
            raise RuntimeError(f"Quran Cloud API error: {payload.get('status', payload)}")
        result = payload.get("data", {})
        return result if isinstance(result, dict) else {"items": result}

    async def get_surah(self, number: int, edition: str) -> dict[str, Any]:
        """Get a full surah in a specific edition."""
        url = f"{constants.SURAH}/{number}/{edition}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def get_ayah(self, reference: str, edition: str) -> dict[str, Any]:
        """Get a single ayah by reference (e.g., '2:255' for Ayat al-Kursi)."""
        url = f"{constants.AYAH}/{reference}/{edition}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def get_juz(self, number: int, edition: str) -> dict[str, Any]:
        """Get a full juz (1 to 30) in a specific edition."""
        url = f"{constants.JUZ}/{number}/{edition}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())

    async def search(
        self,
        query: str,
        surah_filter: str = "all",
        edition: str = "en",
    ) -> dict[str, Any]:
        """Search for a phrase across the Quran in a given edition or language."""
        url = f"{constants.SEARCH}/{query}/{surah_filter}/{edition}"
        async with HttpClient() as client:
            response = await client.get(url)
        return self._unwrap(response.json())
