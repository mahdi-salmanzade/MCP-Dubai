"""
DLD tool functions with the credential-missing pattern.

Every DLD tool calls `auth.availability()` first and returns a structured
ToolResponse.fail when Dubai Pulse credentials are not configured. This
keeps the server bootable on a fresh machine.
"""

from __future__ import annotations

from typing import Any, cast

import httpx

from mcp_dubai._shared.auth import DubaiPulseAuthError, get_dubai_pulse_auth
from mcp_dubai._shared.constants import DUBAI_DATA_PORTAL_BASE, DUBAI_PULSE_API_BASE
from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.dld import constants
from mcp_dubai.data.dubai_pulse.client import (
    DubaiPulseClient,
    DubaiPulseResponseError,
    DubaiPulseValidationError,
)

_SOURCE = DUBAI_PULSE_API_BASE
_UPSTREAM = "dubai_pulse"
_VERIFY_AT = DUBAI_DATA_PORTAL_BASE


def _availability_check() -> dict[str, object] | None:
    """Return a ToolResponse.fail dict if credentials are missing, else None."""
    avail = get_dubai_pulse_auth().availability()
    if avail.get("status") != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()
    return None


async def _query(
    client: DubaiPulseClient,
    *,
    limit: int,
    filters: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Query data.dubai and require the list-shaped payload DLD tools expose."""
    try:
        result = await client.query(limit=limit, filters=filters)
        records = result.get("data")
        if not isinstance(records, list):
            raise DubaiPulseResponseError("data.dubai response field 'data' must be a list")
        if not all(isinstance(record, dict) for record in records):
            raise DubaiPulseResponseError("data.dubai response records must be objects")
        if len(records) > limit:
            raise DubaiPulseResponseError(
                f"data.dubai returned {len(records)} records for requested limit {limit}"
            )
    except DubaiPulseValidationError as exc:
        return (
            None,
            ToolResponse[dict[str, Any]]
            .fail(error=str(exc), source=_SOURCE, retrieved_at=now_iso())
            .model_dump(),
        )
    except (
        DubaiPulseAuthError,
        DubaiPulseResponseError,
        HttpClientError,
        httpx.HTTPError,
        RuntimeError,
        ValueError,
    ) as exc:
        mark_failure(_UPSTREAM, str(exc))
        status = "parse_error" if isinstance(exc, (DubaiPulseResponseError, ValueError)) else None
        return None, upstream_error_response(
            exc,
            status=status,
            verify_at=_VERIFY_AT,
            source=_SOURCE,
        )
    mark_success(_UPSTREAM)
    return result, None


async def dld_search_transactions(
    area: str | None = None,
    property_type: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search DLD real estate sale transactions.

    Args:
        area: Optional area name filter (matches against `area_name_en`).
        property_type: Optional property type filter.
        limit: Max records to return (1 to 500, default 100).
    """
    if limit < 1 or limit > 500:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"limit must be 1 to 500, got {limit}")
            .model_dump()
        )

    fail = _availability_check()
    if fail is not None:
        return fail

    filters: dict[str, Any] = {}
    if area:
        filters["area_name_en"] = area
    if property_type:
        filters["property_type_en"] = property_type

    client = DubaiPulseClient(
        org=constants.DLD_ORG,
        dataset=constants.DATASETS["transactions"],
    )
    result, upstream_error = await _query(client, limit=limit, filters=filters or None)
    if upstream_error is not None:
        return upstream_error
    result = cast(dict[str, Any], result)
    records = cast(list[dict[str, Any]], result["data"])
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(records),
                "transactions": records,
                "raw_meta": {k: v for k, v in result.items() if k != "data"},
            },
            source=_SOURCE,
            retrieved_at=now_iso(),
        )
        .model_dump()
    )


async def dld_search_rent_contracts(
    area: str | None = None,
    bedrooms: int | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search DLD rent contracts (Ejari data).

    Args:
        area: Optional area name filter.
        bedrooms: Optional bedroom count filter.
        limit: Max records to return.
    """
    if limit < 1 or limit > 500:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"limit must be 1 to 500, got {limit}")
            .model_dump()
        )

    fail = _availability_check()
    if fail is not None:
        return fail

    filters: dict[str, Any] = {}
    if area:
        filters["area_en"] = area
    if bedrooms is not None:
        filters["no_of_rooms"] = bedrooms

    client = DubaiPulseClient(
        org=constants.DLD_ORG,
        dataset=constants.DATASETS["rent_contracts"],
    )
    result, upstream_error = await _query(client, limit=limit, filters=filters or None)
    if upstream_error is not None:
        return upstream_error
    result = cast(dict[str, Any], result)
    records = cast(list[dict[str, Any]], result["data"])
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(records),
                "rent_contracts": records,
            },
            source=_SOURCE,
            retrieved_at=now_iso(),
        )
        .model_dump()
    )


async def dld_lookup_broker(
    name: str | None = None,
    license_number: str | None = None,
    limit: int = 50,
) -> dict[str, object]:
    """
    Look up RERA-registered brokers.

    Args:
        name: Optional broker name substring.
        license_number: Optional broker license number.
        limit: Max records to return.
    """
    if limit < 1 or limit > 500:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"limit must be 1 to 500, got {limit}")
            .model_dump()
        )
    if not name and not license_number:
        return (
            ToolResponse[dict[str, object]]
            .fail(error="Provide either name or license_number")
            .model_dump()
        )

    fail = _availability_check()
    if fail is not None:
        return fail

    filters: dict[str, Any] = {}
    if name:
        filters["broker_name_en"] = name
    if license_number:
        filters["license_number"] = license_number

    client = DubaiPulseClient(
        org=constants.DLD_ORG,
        dataset=constants.DATASETS["brokers"],
    )
    result, upstream_error = await _query(client, limit=limit, filters=filters)
    if upstream_error is not None:
        return upstream_error
    result = cast(dict[str, Any], result)
    records = cast(list[dict[str, Any]], result["data"])
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(records),
                "brokers": records,
            },
            source=_SOURCE,
            retrieved_at=now_iso(),
        )
        .model_dump()
    )
