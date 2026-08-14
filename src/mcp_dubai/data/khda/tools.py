"""KHDA school search tools (curated snapshot, no network)."""

from __future__ import annotations

from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.khda.snapshot import (
    SCHOOLS,
    SNAPSHOT_DATE,
    TARGETED_CORRECTION_DATE,
    VALID_RATINGS,
)

_SOURCE = "KHDA curated snapshot"


def _fail(error: str) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=TARGETED_CORRECTION_DATE)
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    payload: dict[str, object] = {
        "full_snapshot_date": SNAPSHOT_DATE,
        "targeted_correction_date": TARGETED_CORRECTION_DATE,
        **data,
    }
    return (
        ToolResponse[dict[str, object]]
        .ok(payload, source=_SOURCE, retrieved_at=TARGETED_CORRECTION_DATE)
        .model_dump()
    )


async def khda_search_school(
    name: str | None = None,
    area: str | None = None,
    curriculum: str | None = None,
    rating: str | None = None,
    max_fee_aed: int | None = None,
    limit: int = 20,
) -> dict[str, object]:
    """
    Search Dubai private schools by name, area, curriculum, rating, or fee.

    All filters are case-insensitive substring matches except `rating`
    (exact match) and `max_fee_aed` (numeric ceiling on the fees_min_aed
    column).
    """
    if rating is not None and rating not in VALID_RATINGS:
        return _fail(f"rating must be one of {sorted(VALID_RATINGS)}, got {rating!r}")
    if limit < 1 or limit > 200:
        return _fail(f"limit must be 1 to 200, got {limit}")

    results = list(SCHOOLS)

    if name:
        needle = name.lower()
        results = [s for s in results if needle in s["name"].lower()]
    if area:
        needle = area.lower()
        results = [s for s in results if needle in s["area"].lower()]
    if curriculum:
        needle = curriculum.lower()
        results = [s for s in results if needle in s["curriculum"].lower()]
    if rating:
        results = [s for s in results if s["rating"] == rating]
    if max_fee_aed is not None:
        results = [s for s in results if s["fees_min_aed"] <= max_fee_aed]

    results = results[:limit]

    return _ok(
        {
            "count": len(results),
            "schools": results,
            "note": (
                "Curated subset of well-known Dubai schools for fast lookup. "
                "The full ratings and fees snapshot is dated 2026-04-14; a targeted "
                "jurisdiction/location correction was applied 2026-08-14. "
                "Contributions to expand coverage from the live KHDA XLSX at "
                "https://web.khda.gov.ae/en/Resources/KHDA-data-statistics are welcome."
            ),
        }
    )


async def khda_list_curricula() -> dict[str, object]:
    """List all unique curricula present in the snapshot."""
    curricula = sorted({s["curriculum"] for s in SCHOOLS})
    return _ok(
        {
            "count": len(curricula),
            "curricula": curricula,
            "note": "Full school attributes are from the 2026-04-14 curated snapshot.",
        }
    )


async def khda_list_areas() -> dict[str, object]:
    """List all unique areas present in the snapshot."""
    areas = sorted({s["area"] for s in SCHOOLS})
    return _ok(
        {
            "count": len(areas),
            "areas": areas,
            "note": (
                "Full school attributes are from the 2026-04-14 curated snapshot. "
                "A jurisdiction/location correction was applied 2026-08-14."
            ),
        }
    )
