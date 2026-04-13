"""RTA tool functions with credential-missing pattern."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.auth import get_dubai_pulse_auth
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.dubai_pulse.client import DubaiPulseClient
from mcp_dubai.data.rta import constants


def _availability_check() -> dict[str, object] | None:
    avail = get_dubai_pulse_auth().availability()
    if avail.get("status") != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()
    return None


async def rta_search_metro_stations(
    line: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search Dubai Metro stations.

    Args:
        line: Optional line filter (e.g., "Red", "Green", "Route 2020").
        limit: Max records.
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
    if line:
        filters["line"] = line

    client = DubaiPulseClient(
        org=constants.RTA_ORG,
        dataset=constants.DATASETS["metro_stations"],
    )
    result = await client.query(limit=limit, filters=filters or None)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "stations": result.get("data", []),
            }
        )
        .model_dump()
    )


async def rta_search_bus_routes(
    route_number: str | None = None,
    origin: str | None = None,
    limit: int = 100,
) -> dict[str, object]:
    """
    Search Dubai bus routes.

    Args:
        route_number: Optional bus route number (e.g., "27").
        origin: Optional origin substring filter.
        limit: Max records.
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
    if route_number:
        filters["route_number"] = route_number
    if origin:
        filters["origin"] = origin

    client = DubaiPulseClient(
        org=constants.RTA_ORG,
        dataset=constants.DATASETS["bus_routes"],
    )
    result = await client.query(limit=limit, filters=filters or None)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "routes": result.get("data", []),
            }
        )
        .model_dump()
    )


async def rta_salik_tariff() -> dict[str, object]:
    """
    Return Salik toll tariff reference data.

    NOTE: This is the only Salik dataset publicly available. Account
    balances, trip history, and violations are NOT exposed via any
    public API and are deliberately not built (see DISCLAIMER.md).
    """
    fail = _availability_check()
    if fail is not None:
        return fail

    client = DubaiPulseClient(
        org=constants.RTA_ORG,
        dataset=constants.DATASETS["salik_tariff"],
    )
    result = await client.query(limit=100)
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(result.get("data", [])),
                "tariff": result.get("data", []),
                "warning": (
                    "Only Salik tariff is public. Account balances, trips, and "
                    "violations are NOT available via any public API. Use the "
                    "Smart Salik mobile app for those."
                ),
            }
        )
        .model_dump()
    )


async def rta_gtfs_static_url() -> dict[str, object]:
    """
    Return the URL for the RTA GTFS static feed.

    The Transitland mirror is anonymous (no Dubai Pulse credentials needed).
    The Dubai Pulse `rta_gtfs-open` dataset requires OAuth.

    NOTE: There is no GTFS-RT (real-time) feed for Dubai RTA.
    """
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "transitland_mirror_url": constants.GTFS_TRANSITLAND_MIRROR,
                "transitland_mirror_auth_required": False,
                "dubai_pulse_dataset": constants.DATASETS["gtfs_static"],
                "dubai_pulse_auth_required": True,
                "gtfs_realtime_available": False,
                "tip": (
                    "Use the Transitland mirror for an anonymous, no-credentials "
                    "download of the static GTFS feed. Use Dubai Pulse only if "
                    "you need the canonical RTA-published version."
                ),
            }
        )
        .model_dump()
    )
