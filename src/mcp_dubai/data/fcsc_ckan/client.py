"""FCSC CKAN client (anonymous read)."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.fcsc_ckan import constants


class FcscCkanClient:
    """Anonymous read client for the FCSC CKAN API."""

    @staticmethod
    def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
        """CKAN wraps everything in {'success': bool, 'result': ...}."""
        if not payload.get("success", False):
            raise RuntimeError(f"CKAN reported failure: {payload.get('error', payload)}")
        result = payload.get("result", {})
        return result if isinstance(result, dict) else {"items": result}

    async def package_search(
        self,
        query: str = "",
        rows: int = 10,
        start: int = 0,
        organization: str | None = None,
    ) -> dict[str, Any]:
        """
        Search datasets by free-text query.

        Args:
            query: Solr query string. Empty string returns all datasets.
            rows: Maximum results per page.
            start: Pagination offset.
            organization: CKAN organization slug to filter by.

        Returns:
            CKAN result block with `count` and `results`.
        """
        params: dict[str, Any] = {"q": query or "*:*", "rows": rows, "start": start}
        if organization:
            params["fq"] = f"organization:{organization}"

        async with HttpClient() as client:
            response = await client.get(constants.PACKAGE_SEARCH, params=params)
        return self._unwrap(response.json())

    async def package_show(self, dataset_id: str) -> dict[str, Any]:
        """Get full metadata for a specific dataset by id or slug."""
        async with HttpClient() as client:
            response = await client.get(constants.PACKAGE_SHOW, params={"id": dataset_id})
        return self._unwrap(response.json())

    async def organization_list(self) -> list[str]:
        """List all CKAN organizations on the portal."""
        async with HttpClient() as client:
            response = await client.get(constants.ORGANIZATION_LIST)
        result = self._unwrap(response.json())
        items = result.get("items", [])
        if isinstance(items, list):
            return [str(item) for item in items]
        return []
