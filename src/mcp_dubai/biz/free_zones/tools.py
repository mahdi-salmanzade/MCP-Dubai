"""free_zones tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("free_zones.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("free_zones", KNOWLEDGE)


def _all_free_zones() -> list[dict[str, Any]]:
    items = _DATA.get("free_zones", [])
    return list(items) if isinstance(items, list) else []


def _all_offshore() -> list[dict[str, Any]]:
    items = _DATA.get("offshore", [])
    return list(items) if isinstance(items, list) else []


def _initial_aed(fz: dict[str, Any]) -> int:
    license_block = fz.get("license", {})
    if not isinstance(license_block, dict):
        return 0
    val = license_block.get("initial_aed", 0)
    return int(val) if isinstance(val, (int, float)) else 0


async def list_free_zones() -> dict[str, object]:
    """List every Dubai free zone in the curated dataset."""
    free_zones = _all_free_zones()
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(free_zones),
                "free_zones": [
                    {
                        "id": fz.get("id"),
                        "name": fz.get("name"),
                        "sector": fz.get("sector"),
                        "location": fz.get("location"),
                        "initial_license_aed": _initial_aed(fz),
                    }
                    for fz in free_zones
                ],
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def free_zone_details(free_zone_id: str) -> dict[str, object]:
    """Return the full curated record for a single free zone by id."""
    if not free_zone_id:
        return (
            ToolResponse[dict[str, object]]
            .fail(error="free_zone_id must not be empty")
            .model_dump()
        )

    needle = free_zone_id.strip().lower()
    for fz in _all_free_zones():
        if str(fz.get("id", "")).lower() == needle:
            return ToolResponse[dict[str, object]].ok(fz, knowledge=KNOWLEDGE).model_dump()

    valid_ids = sorted(str(fz.get("id", "")) for fz in _all_free_zones())
    return (
        ToolResponse[dict[str, object]]
        .fail(error=f"Unknown free_zone_id {free_zone_id!r}. Valid: {valid_ids}")
        .model_dump()
    )


async def compare_free_zones(
    activity: str | None = None,
    budget_aed: int | None = None,
    visa_count: int = 1,
    needs_physical_office: bool = False,
    sector: str | None = None,
    limit: int = 5,
) -> dict[str, object]:
    """
    Compare Dubai free zones for a specific use case. Filters by budget,
    visa quota, office requirements, and sector, then ranks by cost.
    """
    if visa_count < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"visa_count must be >= 0, got {visa_count}")
            .model_dump()
        )
    if limit < 1 or limit > 50:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"limit must be 1 to 50, got {limit}")
            .model_dump()
        )

    candidates: list[dict[str, Any]] = []
    for fz in _all_free_zones():
        # Budget filter
        cost = _initial_aed(fz)
        if budget_aed is not None and cost > 0 and cost > budget_aed:
            continue

        # Visa quota filter
        visa_block = fz.get("visas", {})
        visa_max = 999
        if isinstance(visa_block, dict):
            try:
                visa_max = int(visa_block.get("max", 999))
            except (TypeError, ValueError):
                visa_max = 999
        if visa_count > visa_max:
            continue

        # Office filter (needs_physical_office=True excludes virtual-only zones)
        office_block = fz.get("office", {})
        if needs_physical_office and isinstance(office_block, dict):
            options = office_block.get("options", [])
            if isinstance(options, list) and not any(
                o in {"flexi", "private", "warehouse", "studio", "clinic"} for o in options
            ):
                continue

        # Sector filter (substring on tags + sector)
        if sector:
            sector_lower = sector.lower()
            tags = fz.get("tags", [])
            sector_str = str(fz.get("sector", "")).lower()
            tags_str = " ".join(str(t).lower() for t in tags) if isinstance(tags, list) else ""
            if sector_lower not in sector_str and sector_lower not in tags_str:
                continue

        # Compute a ranking score: lower cost wins, bank-difficult is
        # penalised. Zones with cost==0 ("varies, get a quote") get a
        # placeholder score so they sort BELOW known-cheap zones, not above.
        banking_block = fz.get("banking", {})
        bank_acceptance = "moderate"
        if isinstance(banking_block, dict):
            bank_acceptance = str(banking_block.get("acceptance", "moderate"))
        bank_penalty = {"easy": 0, "moderate": 2500, "difficult": 8000}.get(bank_acceptance, 2500)
        cost_for_ranking = cost if cost > 0 else 50000
        score = cost_for_ranking + bank_penalty

        candidates.append(
            {
                "id": fz.get("id"),
                "name": fz.get("name"),
                "sector": fz.get("sector"),
                "initial_license_aed": cost,
                "visa_quota_max": visa_max,
                "bank_acceptance": bank_acceptance,
                "best_for": fz.get("best_for", []),
                "_score": score,
            }
        )

    candidates.sort(key=lambda c: c["_score"])
    top = [{k: v for k, v in c.items() if k != "_score"} for c in candidates[:limit]]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(top),
                "filters": {
                    "activity": activity,
                    "budget_aed": budget_aed,
                    "visa_count": visa_count,
                    "needs_physical_office": needs_physical_office,
                    "sector": sector,
                },
                "free_zones": top,
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def list_offshore() -> dict[str, object]:
    """List the Dubai-relevant offshore options (RAK ICC, JAFZA Offshore)."""
    offshore = _all_offshore()
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {"count": len(offshore), "offshore": offshore},
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
