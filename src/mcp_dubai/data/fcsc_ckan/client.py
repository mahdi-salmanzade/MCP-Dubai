"""FCSC CKAN client (anonymous read)."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.fcsc_ckan import constants


class FcscCkanClient:
    """Anonymous read client for the FCSC CKAN API."""

    @staticmethod
    def _unwrap(payload: object) -> object:
        """CKAN wraps everything in {'success': bool, 'result': ...}."""
        if not isinstance(payload, dict):
            raise RuntimeError("CKAN response must be an object")
        if payload.get("success") is not True:
            raise RuntimeError("CKAN reported failure")
        if "result" not in payload:
            raise RuntimeError("CKAN response is missing result")
        result: object = payload["result"]
        return result

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
        result = self._unwrap(response.json())
        if not isinstance(result, dict):
            raise RuntimeError("CKAN search result must be an object")
        count = result.get("count")
        records = result.get("results")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise RuntimeError("CKAN search count must be a non-negative integer")
        if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
            raise RuntimeError("CKAN search results must be a list of objects")
        if count < len(records):
            raise RuntimeError("CKAN search count is smaller than the returned result set")
        # Enforce the requested page size even when an upstream ignores rows.
        return {**result, "results": records[:rows]}

    async def package_show(self, dataset_id: str) -> dict[str, Any]:
        """Get full metadata for a specific dataset by id or slug."""
        async with HttpClient() as client:
            response = await client.get(constants.PACKAGE_SHOW, params={"id": dataset_id})
        result = self._unwrap(response.json())
        if not isinstance(result, dict) or not result:
            raise RuntimeError("CKAN dataset result must be a non-empty object")
        return result

    async def organization_list(self) -> list[str]:
        """List all CKAN organizations on the portal."""
        async with HttpClient() as client:
            response = await client.get(constants.ORGANIZATION_LIST)
        result = self._unwrap(response.json())
        if not isinstance(result, list) or any(
            not isinstance(item, str) or not item.strip() for item in result
        ):
            raise RuntimeError("CKAN organizations must be a list of non-empty strings")
        return [str(item) for item in result]
