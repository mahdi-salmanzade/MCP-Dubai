"""tenancy tool functions: Ejari, RERA rent increase, and RDC filing."""

from __future__ import annotations

import math
from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("tenancy.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("tenancy", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _clamp(value: float, low: float, high: float) -> float:
    """Clamp value into the inclusive [low, high] range."""
    return max(low, min(high, value))


async def ejari_guide() -> dict[str, object]:
    """Return the full Ejari registration block."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            _block("ejari"),
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def rera_rent_increase(
    current_annual_rent: float,
    area_average_rent: float,
) -> dict[str, object]:
    """
    Compute the maximum allowed rent increase under Dubai Decree 43 of 2013.

    The slab is chosen by how far the current rent sits below the area
    average market rent (the RERA Rent Index). The decree describes the
    first band as "up to ten percent" below the average, inclusive of 10%.
    The intervals used for the estimate are:
        gap <= 10          -> 0% max increase
        10 < gap <= 20     -> 5%
        20 < gap <= 30      -> 10%
        30 < gap <= 40      -> 15%
        gap > 40            -> 20%
    A gap of exactly 20% stays in the 5% band. If the current rent is at or above
    the area average, the gap is non-positive and the max increase is 0%.
    """
    if not math.isfinite(current_annual_rent) or current_annual_rent <= 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"current_annual_rent must be > 0, got {current_annual_rent}")
            .model_dump()
        )
    if not math.isfinite(area_average_rent) or area_average_rent <= 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"area_average_rent must be > 0, got {area_average_rent}")
            .model_dump()
        )

    rera = _block("rera_rent_increase")
    slabs = rera.get("slabs", [])

    gap_pct = (area_average_rent - current_annual_rent) / area_average_rent * 100

    # DLD's Tenancy Guide includes exactly 10% in the no-increase band.
    if gap_pct <= 10:
        max_increase_pct = 0
        band = "up to 10% below"
    elif gap_pct <= 20:
        max_increase_pct = 5
        band = "11-20% below"
    elif gap_pct <= 30:
        max_increase_pct = 10
        band = "21-30% below"
    elif gap_pct <= 40:
        max_increase_pct = 15
        band = "31-40% below"
    else:
        max_increase_pct = 20
        band = "more than 40% below"

    slab_description = next(
        (
            str(s.get("description", ""))
            for s in slabs
            if isinstance(s, dict) and s.get("band") == band
        ),
        "",
    )

    max_new_rent_aed = current_annual_rent * (1 + max_increase_pct / 100)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "law": rera.get("law"),
                "current_annual_rent_aed": current_annual_rent,
                "area_average_rent_aed": area_average_rent,
                "gap_pct": gap_pct,
                "band": band,
                "max_increase_pct": max_increase_pct,
                "max_new_rent_aed": max_new_rent_aed,
                "slab_description": slab_description,
                "notice_note": rera.get("notice_rule"),
                "rent_cap_status": rera.get("rent_cap_status"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def rental_dispute_guide(annual_rent: float | None = None) -> dict[str, object]:
    """
    Return the Rental Disputes Centre (RDC) block.

    If annual_rent is given, also compute the filing fee as 3.5% of annual
    rent clamped to the AED 500 floor and AED 20,000 cap.
    """
    if annual_rent is not None and (not math.isfinite(annual_rent) or annual_rent <= 0):
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"annual_rent must be > 0 when provided, got {annual_rent}")
            .model_dump()
        )

    rdc = _block("rdc")
    payload: dict[str, object] = dict(rdc)

    if annual_rent is not None:
        pct = float(rdc.get("filing_fee_pct", 3.5)) / 100
        low = float(rdc.get("filing_fee_min_aed", 500))
        high = float(rdc.get("filing_fee_max_aed", 20000))
        filing_fee_aed = _clamp(annual_rent * pct, low, high)
        payload["annual_rent_aed"] = annual_rent
        payload["filing_fee_aed"] = filing_fee_aed

    return (
        ToolResponse[dict[str, object]]
        .ok(
            payload,
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
