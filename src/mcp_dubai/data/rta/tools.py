"""RTA tool functions with credential-missing pattern."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.auth import get_dubai_pulse_auth
from mcp_dubai._shared.constants import RTA_GTFS_DOWNLOAD_URL
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

    Covers operating lines (Red, Green, Route 2020). The Blue Line (under
    construction, opening 2029-09-09) and the Gold Line (approved 2026,
    opening 2032-09-09) are not in the dataset; the response carries
    context notes for them.

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
                "upcoming_line_notes": constants.METRO_LINE_NOTES,
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

    From 2026-06-01 a 5% VAT applies to Salik tolls and tag activation
    fees (standard AED 4 crossing becomes AED 4.20, peak AED 6 becomes
    AED 6.30); the response carries a `vat` block with the VAT-inclusive
    amounts because dataset rows may still show pre-VAT base amounts.

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
                "vat": constants.SALIK_VAT_NOTE,
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
    Return download details for the RTA GTFS static feed.

    The direct FILE download (Dubai Pulse file store) is anonymous: no
    credentials needed. Only the query API (`rta_gtfs-open-api` on
    apis.data.dubai, or the legacy api.dubaipulse.gov.ae host) requires
    OAuth credentials. The old Transitland mirror is dead (HTTP 401 since
    2026, and its archived data is from 2021).

    NOTE: There is no GTFS-RT (real-time) feed for Dubai RTA.
    """
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "download_url": RTA_GTFS_DOWNLOAD_URL,
                "download_auth_required": False,
                "archive_format": "7z",
                "archive_size_mb_approx": 10.4,
                "extraction_hint": (
                    "The download is a 7-zip archive, NOT a plain zip, and is "
                    "served with a wrong text/html Content-Type. Extract with "
                    "py7zr (Python) or bsdtar."
                ),
                "feed_version_note": (
                    f"Archive contains {constants.GTFS_FEED_VERSION} (feed "
                    f"built 2025-08-23) as of "
                    f"{constants.GTFS_FEED_VERSION_CHECKED}."
                ),
                "staleness_note": (
                    "The feed build predates 2026 bus network changes. "
                    "Re-download and check feed_info.txt for a fresher build "
                    "before relying on schedule data."
                ),
                "dubai_pulse_dataset": constants.DATASETS["gtfs_static"],
                "query_api_auth_required": True,
                "gtfs_realtime_available": False,
                "dead_sources": [
                    {
                        "url": constants.GTFS_TRANSITLAND_MIRROR_DEAD,
                        "status": (
                            "dead: returns HTTP 401 (Transitland requires an "
                            "API token) and its archived data is from 2021"
                        ),
                    }
                ],
                "tip": (
                    "Use download_url for an anonymous, no-credentials copy "
                    "of the static GTFS feed. Use the credentialed query API "
                    "only if you need row-level filtering."
                ),
            },
            source="curated (www.dubaipulse.gov.ae file store)",
            retrieved_at=constants.GTFS_FEED_VERSION_CHECKED,
        )
        .model_dump()
    )
