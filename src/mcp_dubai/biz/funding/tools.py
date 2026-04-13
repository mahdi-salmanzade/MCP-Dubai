"""funding tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("funding.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("funding", KNOWLEDGE)


def _list(name: str) -> list[dict[str, Any]]:
    items = _DATA.get(name, [])
    return list(items) if isinstance(items, list) else []


VALID_STAGES = {"pre_seed", "seed", "series_a", "series_b", "growth"}
VALID_SECTORS = {
    "tech",
    "saas",
    "fintech",
    "ai",
    "marketplace",
    "consumer",
    "healthtech",
    "edtech",
    "logistics",
    "deeptech",
    "cleantech",
    "media",
    "design",
    "general",
}


async def accelerator_search(
    sector: str | None = None,
    free_only: bool = False,
    location: str | None = None,
) -> dict[str, object]:
    """
    Search UAE accelerators and incubators by sector and cost.

    Args:
        sector: Optional sector filter (substring on best_for and tags).
        free_only: True to exclude paid accelerators (e.g., AstroLabs).
        location: Optional location filter (e.g., "Dubai", "Abu Dhabi").
    """
    accelerators = _list("accelerators")
    matching: list[dict[str, Any]] = []

    for acc in accelerators:
        if sector:
            needle = sector.lower()
            best_for = acc.get("best_for", [])
            if not isinstance(best_for, list):
                best_for = []
            best_for_str = " ".join(str(b).lower() for b in best_for)
            if needle not in best_for_str:
                continue

        if free_only and acc.get("tier") == "paid_accelerator":
            continue

        if location:
            acc_loc = str(acc.get("location", "")).lower()
            if location.lower() not in acc_loc:
                continue

        matching.append(acc)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(matching),
                "accelerators": matching,
                "filters": {
                    "sector": sector,
                    "free_only": free_only,
                    "location": location,
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def vc_list(
    stage: str | None = None,
    sector: str | None = None,
) -> dict[str, object]:
    """
    List UAE / MENA active VCs, optionally filtered by stage focus or sector.

    Args:
        stage: Optional stage filter, one of pre_seed, seed, series_a,
            series_b, growth.
        sector: Optional sector substring filter on the VC's sector list.
    """
    vcs = _list("vcs")
    matching: list[dict[str, Any]] = []

    stage_label_map = {
        "pre_seed": "Pre-seed",
        "seed": "Seed",
        "series_a": "Series A",
        "series_b": "Series B",
        "growth": "Series B+",
    }

    for vc in vcs:
        if stage:
            if stage not in VALID_STAGES:
                return (
                    ToolResponse[dict[str, object]]
                    .fail(error=f"stage must be one of {sorted(VALID_STAGES)}, got {stage!r}")
                    .model_dump()
                )
            stage_label = stage_label_map.get(stage, stage)
            stages = vc.get("stage_focus", [])
            if not isinstance(stages, list):
                stages = []
            if stage_label not in stages:
                continue

        if sector:
            sectors = vc.get("sectors", [])
            if not isinstance(sectors, list):
                sectors = []
            sector_str = " ".join(str(s).lower() for s in sectors)
            if sector.lower() not in sector_str:
                continue

        matching.append(vc)

    excluded = _list("vcs_excluded_with_reason")

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(matching),
                "vcs": matching,
                "excluded_with_reason": excluded,
                "filters": {"stage": stage, "sector": sector},
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def grant_programs(
    grant_type: str | None = None,
) -> dict[str, object]:
    """
    List UAE government grant and funding support programs.

    Args:
        grant_type: Optional filter, e.g., "guarantee_loan", "venture_fund",
            "support_programs", "loan_grant".
    """
    grants = _list("grants")
    matching = grants
    if grant_type:
        matching = [g for g in grants if g.get("type") == grant_type]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(matching),
                "grants": matching,
                "filter": {"grant_type": grant_type},
                "warning": (
                    "MBRIF AED 5M figure from the original brief is unverified. "
                    "Third-party sources cite up to AED 2M interest-free loans. "
                    "Verify directly with MBRIF before quoting."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
