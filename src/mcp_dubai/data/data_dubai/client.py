"""data.dubai catalog client. Anonymous Liferay Objects JSON API reads."""

from __future__ import annotations

from typing import Any, cast

import httpx

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
from mcp_dubai.data.data_dubai import constants


def _page_integer(
    payload: dict[str, Any],
    field: str,
    url: str,
    *,
    minimum: int,
) -> int:
    """Read one required pagination integer without accepting booleans."""
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise HttpClientError(
            f"Invalid JSON shape from {url}: {field} is not an integer >= {minimum}"
        )
    return value


def _decode_page_envelope(
    response: httpx.Response,
    url: str,
    *,
    expected_page: int,
    expected_page_size: int,
) -> dict[str, Any]:
    """Decode and validate a Liferay page envelope."""
    if response.status_code == 204 or not response.content:
        raise HttpClientError(f"Empty response from {url}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise HttpClientError(f"Non-JSON body from {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise HttpClientError(f"Invalid JSON shape from {url}: expected an object")

    items = payload.get("items")
    if not isinstance(items, list):
        raise HttpClientError(f"Invalid JSON shape from {url}: items is not a list")
    if any(not isinstance(item, dict) for item in items):
        raise HttpClientError(f"Invalid JSON shape from {url}: items contains a non-object")

    total_count = _page_integer(payload, "totalCount", url, minimum=0)
    page = _page_integer(payload, "page", url, minimum=1)
    page_size = _page_integer(payload, "pageSize", url, minimum=1)
    last_page = _page_integer(payload, "lastPage", url, minimum=1)

    if page != expected_page:
        raise HttpClientError(
            f"Invalid pagination from {url}: requested page {expected_page}, returned {page}"
        )
    if page_size != expected_page_size:
        raise HttpClientError(
            f"Invalid pagination from {url}: requested pageSize {expected_page_size}, "
            f"returned {page_size}"
        )
    if total_count < len(items):
        raise HttpClientError(f"Invalid JSON shape from {url}: totalCount is smaller than items")
    if len(items) > page_size:
        raise HttpClientError(f"Invalid JSON shape from {url}: items exceeds pageSize")

    calculated_last_page = max(1, (total_count + page_size - 1) // page_size)
    if last_page != calculated_last_page:
        raise HttpClientError(
            f"Invalid pagination from {url}: lastPage {last_page} does not match "
            f"totalCount/pageSize ({calculated_last_page})"
        )
    if page > last_page and items:
        raise HttpClientError(f"Invalid pagination from {url}: page after lastPage has items")
    expected_items = (
        min(page_size, total_count - ((page - 1) * page_size)) if page <= last_page else 0
    )
    if len(items) != expected_items:
        raise HttpClientError(
            f"Invalid pagination from {url}: page {page} should contain "
            f"{expected_items} items, returned {len(items)}"
        )
    return dict(payload)


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
        query params. An empty query returns the full catalog (614 datasets
        as of 2026-08-14). The response is a Liferay page envelope with
        `totalCount`, `page`, `pageSize`, `lastPage`, and `items`.
        """
        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if query.strip():
            params["search"] = query.strip()
        async with HttpClient() as client:
            response = await client.get(constants.DATASETS_ENDPOINT, params=params)
        return _decode_page_envelope(
            response,
            constants.DATASETS_ENDPOINT,
            expected_page=page,
            expected_page_size=page_size,
        )

    async def list_themes(self) -> dict[str, Any]:
        """
        List every catalog theme (11 as of 2026-08-14).

        The current count fits in one request; additional pages are followed.
        """
        return await self._list_all(constants.THEMES_ENDPOINT)

    async def list_issuing_entities(self) -> dict[str, Any]:
        """
        List every issuing entity (76 as of 2026-08-14).

        The current count fits in one pageSize=100 request (verified:
        totalCount 76, lastPage 1); additional pages are followed.
        """
        return await self._list_all(constants.ISSUING_ENTITIES_ENDPOINT)

    async def _list_all(self, url: str) -> dict[str, Any]:
        """Fetch every page with stable-total, repeat, and request bounds."""
        page_size = constants.LIST_ALL_PAGE_SIZE
        async with HttpClient() as client:
            first_response = await client.get(url, params={"page": 1, "pageSize": page_size})
            first = _decode_page_envelope(
                first_response,
                url,
                expected_page=1,
                expected_page_size=page_size,
            )

            total_count = cast(int, first["totalCount"])
            last_page = cast(int, first["lastPage"])
            if last_page > constants.MAX_LIST_PAGES:
                raise HttpClientError(
                    f"Pagination from {url} exceeds the {constants.MAX_LIST_PAGES}-page safety limit"
                )

            all_items: list[dict[str, Any]] = []
            seen_ids: set[tuple[str, str]] = set()
            self._append_unique_items(
                all_items,
                seen_ids,
                cast(list[dict[str, Any]], first["items"]),
                url,
            )

            for page in range(2, last_page + 1):
                response = await client.get(url, params={"page": page, "pageSize": page_size})
                payload = _decode_page_envelope(
                    response,
                    url,
                    expected_page=page,
                    expected_page_size=page_size,
                )
                if payload["totalCount"] != total_count:
                    raise HttpClientError(
                        f"Pagination from {url} changed totalCount from "
                        f"{total_count} to {payload['totalCount']}"
                    )
                if payload["lastPage"] != last_page:
                    raise HttpClientError(
                        f"Pagination from {url} changed lastPage from "
                        f"{last_page} to {payload['lastPage']}"
                    )
                self._append_unique_items(
                    all_items,
                    seen_ids,
                    cast(list[dict[str, Any]], payload["items"]),
                    url,
                )

        if len(all_items) != total_count:
            raise HttpClientError(
                f"Incomplete pagination from {url}: expected {total_count} items, "
                f"received {len(all_items)}"
            )

        result = dict(first)
        result["items"] = all_items
        return result

    @staticmethod
    def _append_unique_items(
        destination: list[dict[str, Any]],
        seen_ids: set[tuple[str, str]],
        items: list[dict[str, Any]],
        url: str,
    ) -> None:
        """Append page items while rejecting repeated catalog identities."""
        for item in items:
            item_id = item.get("id")
            if isinstance(item_id, bool) or not isinstance(item_id, int | str):
                raise HttpClientError(
                    f"Invalid JSON shape from {url}: item id is missing or invalid"
                )
            identity = (type(item_id).__name__, str(item_id))
            if identity in seen_ids:
                raise HttpClientError(f"Repeated item id {item_id!r} while paginating {url}")
            seen_ids.add(identity)
            destination.append(item)
