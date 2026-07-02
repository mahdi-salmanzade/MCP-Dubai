"""data.dubai catalog tool functions (credential-free metadata search).

The raw Liferay items carry heavy platform noise (actions maps, i18n
duplicates, workflow status blocks). These tools trim every record to the
useful subset and stamp each response with the metadata-only caveat: the
dataset APIs behind the catalog still need Dubai Pulse/DDSE credentials.
"""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure as mark_upstream_failure
from mcp_dubai._shared.health import mark_success as mark_upstream_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.data_dubai.client import DataDubaiClient

_SOURCE = "data.dubai"
_UPSTREAM = "data_dubai_catalog"
_VERIFY_AT = "https://data.dubai"
_METADATA_NOTE = (
    "This catalog is METADATA ONLY. The dataAPIEndpoints URLs (host "
    "apis.data.dubai) return 401 without Dubai Pulse/DDSE credentials, and "
    "the new portal exposes no anonymous file download URLs."
)

_MAX_PAGE_SIZE = 100


def _fail(error: str | dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _arabic(value: Any) -> str | None:
    """Pull the ar_SA string out of a Liferay `*_i18n` map, if present."""
    if isinstance(value, dict):
        arabic = value.get("ar_SA")
        if isinstance(arabic, str) and arabic.strip():
            return arabic.strip()
    return None


def _to_int(value: Any) -> int:
    """Liferay serialises some counters as strings. Normalise to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _name_of(value: Any) -> str | None:
    """Extract the display name from a Liferay picklist dict like license."""
    if isinstance(value, dict):
        name = value.get("name")
        return str(name) if name is not None else None
    if isinstance(value, str) and value:
        return value
    return None


def _trim_dataset(item: dict[str, Any]) -> dict[str, object]:
    """Trim a raw catalog dataset record to the useful metadata subset."""
    keywords = item.get("keywords")
    return {
        "id": item.get("id"),
        "dataset_name": item.get("datasetName"),
        "title": item.get("title"),
        "title_ar": _arabic(item.get("title_i18n")),
        "description": item.get("description"),
        "description_ar": _arabic(item.get("description_i18n")),
        "themes": item.get("themes"),
        "subthemes": item.get("subthemes"),
        "keywords": [str(k) for k in keywords] if isinstance(keywords, list) else [],
        "format": item.get("format"),
        "license": _name_of(item.get("license")),
        "frequency_of_update": item.get("frequencyOfUpdateOnSource"),
        "ingestion_date": item.get("ingestionDate"),
        "published_date": item.get("publishedDate"),
        "date_modified": item.get("dateModified"),
        "view_count": _to_int(item.get("customViewCounts") or item.get("viewCount")),
        "download_count": _to_int(item.get("customDownloadCount") or item.get("downloadCount")),
        "dataset_source": item.get("datasetSource"),
        "issuing_entity_erc": item.get("r_issuingEntityOfDataset_c_issuingEntityERC"),
        "issuing_entity_id": item.get("r_issuingEntityOfDataset_c_issuingEntityId"),
        "data_api_endpoint": item.get("dataAPIEndpoints"),
    }


def _trim_theme(item: dict[str, Any]) -> dict[str, object]:
    """Trim a raw theme record to the useful subset."""
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "title_ar": _arabic(item.get("title_i18n")),
        "description": item.get("description"),
        "description_ar": _arabic(item.get("description_i18n")),
        "dataset_count": _to_int(item.get("datasetCounts")),
    }


def _trim_entity(item: dict[str, Any]) -> dict[str, object]:
    """Trim a raw issuing-entity record to the useful subset."""
    return {
        "id": item.get("id"),
        "key": item.get("key"),
        "title": item.get("title"),
        "title_ar": _arabic(item.get("title_i18n")),
        "description": item.get("description"),
        "dataset_usages": _to_int(item.get("usages")),
        "external_reference_code": item.get("externalReferenceCode"),
    }


def _items_of(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


async def data_dubai_search(
    query: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict[str, object]:
    """
    Search the data.dubai catalog for dataset metadata (no credentials).

    Args:
        query: Free-text search over titles, descriptions, and keywords.
            Empty string lists the full catalog (617 datasets as of
            2026-07-02).
        page: 1-based page number.
        page_size: Datasets per page, 1 to 100.

    Returns:
        Dict with `total_count`, `page`, `page_size`, `last_page`,
        `datasets` (trimmed metadata records), and the metadata-only `note`.
    """
    if page < 1:
        return _fail(f"page must be >= 1, got {page}")
    if page_size < 1 or page_size > _MAX_PAGE_SIZE:
        return _fail(f"page_size must be 1 to {_MAX_PAGE_SIZE}, got {page_size}")

    client = DataDubaiClient()
    try:
        payload = await client.search_datasets(query=query, page=page, page_size=page_size)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    if not payload:
        # An empty body would otherwise read as "the catalog is empty".
        mark_upstream_failure(_UPSTREAM, "empty catalog response")
        return _fail("data.dubai catalog returned an empty response; try again later.")

    mark_upstream_success(_UPSTREAM)
    return _ok(
        {
            "total_count": _to_int(payload.get("totalCount")),
            "page": page,
            "page_size": page_size,
            "last_page": _to_int(payload.get("lastPage")),
            "datasets": [_trim_dataset(item) for item in _items_of(payload)],
            "note": _METADATA_NOTE,
        }
    )


async def data_dubai_themes() -> dict[str, object]:
    """
    List the data.dubai catalog themes (no credentials).

    Returns:
        Dict with `total_count`, `themes` (id, bilingual title and
        description, dataset_count), and the metadata-only `note`.
    """
    client = DataDubaiClient()
    try:
        payload = await client.list_themes()
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_upstream_success(_UPSTREAM)
    return _ok(
        {
            "total_count": _to_int(payload.get("totalCount")),
            "themes": [_trim_theme(item) for item in _items_of(payload)],
            "note": _METADATA_NOTE,
        }
    )


async def data_dubai_entities(search: str = "") -> dict[str, object]:
    """
    List data.dubai issuing entities, optionally filtered (no credentials).

    The upstream endpoint has no server-side search, so the filter runs
    client-side over the full entity list (76 records as of 2026-07-02).

    Args:
        search: Case-insensitive substring matched against each entity's
            English title, Arabic title, and short key (e.g. "rta").
            Empty string returns every entity.

    Returns:
        Dict with `total_count` (all entities), `matched_count`, `search`,
        `entities` (trimmed records), and the metadata-only `note`.
    """
    client = DataDubaiClient()
    try:
        payload = await client.list_issuing_entities()
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    mark_upstream_success(_UPSTREAM)
    entities = [_trim_entity(item) for item in _items_of(payload)]

    needle = search.strip().lower()
    if needle:
        matched = [
            entity
            for entity in entities
            if any(
                needle in str(entity[field] or "").lower() for field in ("title", "title_ar", "key")
            )
        ]
    else:
        matched = entities

    return _ok(
        {
            "total_count": _to_int(payload.get("totalCount")),
            "matched_count": len(matched),
            "search": search,
            "entities": matched,
            "note": _METADATA_NOTE,
        }
    )
