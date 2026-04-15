"""FCSC CKAN tool functions."""

from __future__ import annotations

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.fcsc_ckan import constants
from mcp_dubai.data.fcsc_ckan.client import FcscCkanClient

FCSC_VERIFY_URL = "https://opendata.fcsc.gov.ae"
_SOURCE = "opendata.fcsc.gov.ae"
_UPSTREAM = "fcsc_ckan"


def _fail(error: str) -> dict[str, object]:
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


async def fcsc_search_dataset(
    query: str = "",
    rows: int = 10,
    start: int = 0,
    organization: str | None = None,
) -> dict[str, object]:
    """Search the FCSC UAE federal open data portal for datasets."""
    if rows < 1 or rows > 100:
        return _fail(f"rows must be 1 to 100, got {rows}")
    if start < 0:
        return _fail(f"start must be >= 0, got {start}")

    client = FcscCkanClient()
    try:
        result = await client.package_search(
            query=query,
            rows=rows,
            start=start,
            organization=organization,
        )
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok(
        {
            "count": result.get("count", 0),
            "rows": rows,
            "start": start,
            "results": result.get("results", []),
        }
    )


async def fcsc_get_dataset(dataset_id: str) -> dict[str, object]:
    """Get full metadata for a specific FCSC dataset."""
    if not dataset_id:
        return _fail("dataset_id must not be empty")

    client = FcscCkanClient()
    try:
        result = await client.package_show(dataset_id)
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL, source=_SOURCE)
    except RuntimeError as exc:
        mark_failure(_UPSTREAM, str(exc))
        return _fail(str(exc))

    mark_success(_UPSTREAM)
    return _ok(result)


async def fcsc_list_organizations() -> dict[str, object]:
    """List all CKAN organizations publishing on the FCSC portal."""
    client = FcscCkanClient()
    try:
        orgs = await client.organization_list()
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=FCSC_VERIFY_URL, source=_SOURCE)

    mark_success(_UPSTREAM)
    return _ok({"count": len(orgs), "organizations": orgs})


async def fca_trade_stats(
    query: str = "",
    rows: int = 10,
) -> dict[str, object]:
    """
    Search Federal Customs Authority trade statistics datasets.

    Convenience wrapper that filters `fcsc_search_dataset` to the
    `federal-customs-authority` organization.
    """
    return await fcsc_search_dataset(
        query=query,
        rows=rows,
        organization=constants.FCA_ORG_SLUG,
    )
