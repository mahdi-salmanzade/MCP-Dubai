"""banking tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("banks.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("banking", KNOWLEDGE)


def _all_banks() -> list[dict[str, Any]]:
    items = _DATA.get("banks", [])
    return list(items) if isinstance(items, list) else []


def _dul_block() -> dict[str, Any]:
    block = _DATA.get("dul", {})
    return block if isinstance(block, dict) else {}


VALID_TIERS = {"digital", "traditional", "international"}
VALID_INDUSTRIES = {
    "general",
    "saas",
    "tech",
    "ecommerce",
    "consulting",
    "fintech",
    "trading",
    "import_export",
    "manufacturing",
    "logistics",
    "healthcare",
    "media",
    "real_estate",
    "fb",
    "retail",
    "crypto",
    "forex",
    "jewelry",
    "msb",
    "used_cars",
}


async def list_banks() -> dict[str, object]:
    """
    List every UAE business bank in the curated dataset, plus the CBUAE
    open finance (Al Tareq) status, recent 2026 market entrants, and the
    capital markets regulator note.
    """
    banks = _all_banks()
    open_finance = _DATA.get("open_finance", {})
    recent_entrants = _DATA.get("recent_entrants_2026", {})
    regulators = _DATA.get("regulators", {})
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(banks),
                "banks": [
                    {
                        "id": b.get("id"),
                        "name": b.get("name"),
                        "tier": b.get("tier"),
                        "type": b.get("type"),
                        "onboarding_speed_label": b.get("onboarding_speed_label"),
                        "min_balance_aed": b.get("min_balance_aed"),
                    }
                    for b in banks
                ],
                "open_finance": open_finance if isinstance(open_finance, dict) else {},
                "recent_entrants_2026": (
                    recent_entrants if isinstance(recent_entrants, dict) else {}
                ),
                "regulators": regulators if isinstance(regulators, dict) else {},
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def bank_details(bank_id: str) -> dict[str, object]:
    """Return the full curated record for a specific UAE bank."""
    if not bank_id:
        return ToolResponse[dict[str, object]].fail(error="bank_id must not be empty").model_dump()

    needle = bank_id.strip().lower()
    for bank in _all_banks():
        if str(bank.get("id", "")).lower() == needle:
            return ToolResponse[dict[str, object]].ok(bank, knowledge=KNOWLEDGE).model_dump()

    valid_ids = sorted(str(b.get("id", "")) for b in _all_banks())
    return (
        ToolResponse[dict[str, object]]
        .fail(error=f"Unknown bank_id {bank_id!r}. Valid: {valid_ids}")
        .model_dump()
    )


async def bank_recommendation(
    industry: str = "general",
    budget_min_balance_aed: int | None = None,
    speed_priority: bool = False,
    tier: str | None = None,
    is_high_risk: bool = False,
    limit: int = 5,
) -> dict[str, object]:
    """
    Recommend banks based on industry, minimum balance budget, and speed.
    """
    if industry not in VALID_INDUSTRIES:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"industry must be one of {sorted(VALID_INDUSTRIES)}, got {industry!r}")
            .model_dump()
        )
    if tier is not None and tier not in VALID_TIERS:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"tier must be one of {sorted(VALID_TIERS)}, got {tier!r}")
            .model_dump()
        )
    if limit < 1 or limit > 20:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"limit must be 1 to 20, got {limit}")
            .model_dump()
        )

    high_risk_industries = {"crypto", "forex", "jewelry", "used_cars", "msb"}
    if industry in high_risk_industries:
        is_high_risk = True

    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []

    for bank in _all_banks():
        # Skip Liv (retail-only)
        if bank.get("type") == "digital_retail":
            continue

        # Tier filter
        if tier and bank.get("tier") != tier:
            continue

        # Min balance filter
        if budget_min_balance_aed is not None:
            min_bal = bank.get("min_balance_aed", 0)
            if isinstance(min_bal, (int, float)) and min_bal > budget_min_balance_aed:
                continue

        # High-risk industries: warn that no bank officially welcomes them
        # but still return the digital banks first.

        # Compute a score: lower onboarding days + lower min balance wins
        days_min = bank.get("onboarding_days_min", 14)
        min_bal_val = bank.get("min_balance_aed", 0)
        days_min_val = days_min if isinstance(days_min, (int, float)) else 14
        min_bal_num = min_bal_val if isinstance(min_bal_val, (int, float)) else 0
        score: float = float(days_min_val) * 1000 + float(min_bal_num)
        if speed_priority:
            score = float(days_min_val) * 5000  # weight speed heavily

        candidates.append(
            {
                "id": bank.get("id"),
                "name": bank.get("name"),
                "tier": bank.get("tier"),
                "onboarding_speed_label": bank.get("onboarding_speed_label"),
                "onboarding_days_min": bank.get("onboarding_days_min"),
                "onboarding_days_max": bank.get("onboarding_days_max"),
                "min_balance_aed": bank.get("min_balance_aed"),
                "crypto_friendly": bank.get("crypto_friendly", False),
                "notes": bank.get("notes", ""),
                "_score": score,
            }
        )

    candidates.sort(key=lambda c: c["_score"])
    top = [{k: v for k, v in c.items() if k != "_score"} for c in candidates[:limit]]

    if is_high_risk:
        warnings.append(
            "None of the listed UAE banks officially welcome high-risk "
            "industries (crypto, forex, jewelry, used cars, money service "
            "businesses) as of April 2026. Prepare extensive source-of-funds "
            "documentation and expect 8 to 16 week onboarding."
        )
    warnings.append("Apply to 2 or 3 banks in parallel to hedge onboarding risk.")

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(top),
                "banks": top,
                "warnings": warnings,
                "filters": {
                    "industry": industry,
                    "budget_min_balance_aed": budget_min_balance_aed,
                    "speed_priority": speed_priority,
                    "tier": tier,
                    "is_high_risk": is_high_risk,
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def dul_eligibility(
    bank_id: str | None = None,
    free_zone: str | None = None,
) -> dict[str, object]:
    """
    Report recorded Dubai Unified Licence (DUL) bank integration and
    Dubai-wide free-zone coverage.
    """

    def _norm(value: str) -> str:
        return value.lower().replace("_", " ").replace("-", " ").strip()

    dul = _dul_block()
    integrated_banks = [_norm(str(bank)) for bank in dul.get("integrated_banks", [])]

    bank_status: str | None = None
    if bank_id:
        needle = _norm(bank_id)
        if any(needle == bank or needle in bank or bank in needle for bank in integrated_banks):
            bank_status = "integrated"
        else:
            bank_status = "not_listed_in_official_announcement"

    zone_status = "covered_if_dubai" if free_zone else None
    eligible = bank_status == "integrated"

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "eligible": eligible,
                "bank_id": bank_id,
                "bank_status": bank_status,
                "free_zone": free_zone,
                "zone_status": zone_status,
                "dul_summary": {
                    "average_onboarding_days": dul.get("average_onboarding_days"),
                    "integrated_banks": dul.get("integrated_banks", []),
                    "bank_list_as_of": dul.get("as_of"),
                    "coverage": dul.get("coverage"),
                    "caveat": dul.get("average_note"),
                    "bank_list_note": dul.get("bank_list_note"),
                    "source_urls": dul.get("source_urls", []),
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
