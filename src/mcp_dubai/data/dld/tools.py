"""
DLD tool functions with the credential-missing pattern.

Every DLD tool calls `auth.availability()` first and returns a structured
ToolResponse.fail when Dubai Pulse credentials are not configured. This
keeps the server bootable on a fresh machine.
"""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.auth import get_dubai_pulse_auth
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.dld import constants
from mcp_dubai.data.dubai_pulse.client import DubaiPulseClient


def _availability_check() -> dict[str, object] | None:
    """Return a ToolResponse.fail dict if credentials are missing, else None."""
    avail = get_dubai_pulse_auth().availability()
    if avail.get("status") != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()
    return None


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
    result = await client.query(limit=limit, filters=filters or None)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "transactions": result.get("data", []),
                "raw_meta": {k: v for k, v in result.items() if k != "data"},
            }
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
    result = await client.query(limit=limit, filters=filters or None)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "rent_contracts": result.get("data", []),
            }
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
    result = await client.query(limit=limit, filters=filters)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "brokers": result.get("data", []),
            }
        )
        .model_dump()
    )
