"""data.dubai catalog client. Anonymous Liferay Objects JSON API reads."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.data_dubai import constants


def _decode_json_dict(response: httpx.Response, url: str) -> dict[str, Any]:
    """Decode a JSON object body, converting non-JSON 200s into HttpClientError."""
    try:
        payload = response.json()
    except ValueError as exc:
        raise HttpClientError(f"Non-JSON body from {url}: {exc}") from exc
    return dict(payload) if isinstance(payload, dict) else {}


class DataDubaiClient:
    """Async client for the credential-free data.dubai catalog API."""

    async def search_datasets(
        self,
        query: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """
        Search the dataset catalog by free-text query.

        The endpoint is `/datasets/` with `search`, `page`, and `pageSize`
        query params. An empty query returns the full catalog (617 datasets
        as of 2026-07-02). The response is a Liferay page envelope with
        `totalCount`, `page`, `pageSize`, `lastPage`, and `items`.
        """
        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if query.strip():
            params["search"] = query.strip()
        async with HttpClient() as client:
            response = await client.get(constants.DATASETS_ENDPOINT, params=params)
        if response.status_code == 204 or not response.content:
            return {}
        return _decode_json_dict(response, constants.DATASETS_ENDPOINT)

    async def list_themes(self) -> dict[str, Any]:
        """
        List every catalog theme (11 as of 2026-07-02).

        Single request: the theme count sits far below the page size.
        """
        params: dict[str, Any] = {"pageSize": constants.LIST_ALL_PAGE_SIZE}
        async with HttpClient() as client:
            response = await client.get(constants.THEMES_ENDPOINT, params=params)
        if response.status_code == 204 or not response.content:
            return {}
        return _decode_json_dict(response, constants.THEMES_ENDPOINT)

    async def list_issuing_entities(self) -> dict[str, Any]:
        """
        List every issuing entity (76 as of 2026-07-02).

        Single request with pageSize=100 fetches all records at once
        (verified: totalCount 76, lastPage 1).
        """
        params: dict[str, Any] = {"pageSize": constants.LIST_ALL_PAGE_SIZE}
        async with HttpClient() as client:
            response = await client.get(constants.ISSUING_ENTITIES_ENDPOINT, params=params)
        if response.status_code == 204 or not response.content:
            return {}
        return _decode_json_dict(response, constants.ISSUING_ENTITIES_ENDPOINT)
