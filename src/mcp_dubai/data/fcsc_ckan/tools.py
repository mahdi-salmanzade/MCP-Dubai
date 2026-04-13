"""FCSC CKAN tool functions."""

from __future__ import annotations

import httpx

from mcp_dubai._shared.errors import upstream_error_response
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai.data.fcsc_ckan import constants
from mcp_dubai.data.fcsc_ckan.client import FcscCkanClient

FCSC_VERIFY_URL = "https://opendata.fcsc.gov.ae"


async def fcsc_search_dataset(
    query: str = "",
    rows: int = 10,
    start: int = 0,
    organization: str | None = None,
) -> dict[str, object]:
    """
    Search the FCSC UAE federal open data portal for datasets.

    Args:
        query: Free-text query (Solr syntax). Empty returns recent datasets.
        rows: Max results per page (default 10).
        start: Pagination offset.
        organization: Optional CKAN organization slug filter.

    Returns:
        Dict with `count`, `results` (dataset metadata), and pagination info.
    """
    if rows < 1 or rows > 100:
        raise ValueError(f"rows must be 1 to 100, got {rows}")
    if start < 0:
        raise ValueError(f"start must be >= 0, got {start}")

    client = FcscCkanClient()
    try:
        result = await client.package_search(
            query=query,
            rows=rows,
            start=start,
            organization=organization,
        )
    except (HttpClientError, httpx.HTTPError) as exc:
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL)
    return {
        "count": result.get("count", 0),
        "rows": rows,
        "start": start,
        "results": result.get("results", []),
    }


async def fcsc_get_dataset(dataset_id: str) -> dict[str, object]:
    """
    Get full metadata for a specific FCSC dataset.

    Args:
        dataset_id: CKAN dataset id or slug.

    Returns:
        Dict with the full dataset metadata including resources (download URLs).
    """
    if not dataset_id:
        raise ValueError("dataset_id must not be empty")

    client = FcscCkanClient()
    try:
        return await client.package_show(dataset_id)
    except (HttpClientError, httpx.HTTPError) as exc:
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL)


async def fcsc_list_organizations() -> dict[str, object]:
    """
    List all CKAN organizations publishing on the FCSC portal.

    Useful for finding the right org slug to filter `fcsc_search_dataset`.
    """
    client = FcscCkanClient()
    try:
        orgs = await client.organization_list()
    except (HttpClientError, httpx.HTTPError) as exc:
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL)
    return {"count": len(orgs), "organizations": orgs}


async def fca_trade_stats(
    query: str = "",
    rows: int = 10,
) -> dict[str, object]:
    """
    Search Federal Customs Authority trade statistics datasets.

    Convenience wrapper that filters `fcsc_search_dataset` to the
    `federal-customs-authority` organization. Covers non-oil foreign trade
    by HS chapter, imports, exports, re-exports, monthly and quarterly.

    Args:
        query: Optional free-text query.
        rows: Max results.
    """
    return await fcsc_search_dataset(
        query=query,
        rows=rows,
        organization=constants.FCA_ORG_SLUG,
    )
