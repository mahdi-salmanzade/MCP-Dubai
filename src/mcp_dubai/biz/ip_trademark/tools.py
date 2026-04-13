"""ip_trademark tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("ip_trademark.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("ip_trademark", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


async def trademark_registration(
    is_sme: bool = False,
    expedited: bool = False,
) -> dict[str, object]:
    """
    Return UAE trademark registration steps, fees, and timeline.

    Args:
        is_sme: True if the applicant qualifies for the 50% SME discount
            under Cabinet Resolution 102 of 2025.
        expedited: True for the AED 2,250 one-day expedited examination.
    """
    trademark = _block("trademark")
    registration = trademark.get("registration", {})
    cr_102 = trademark.get("cabinet_resolution_102_2025", {})

    fee_min = int(registration.get("fee_range_aed_min", 6700))
    fee_max = int(registration.get("fee_range_aed_max", 12000))

    expedited_fee = 0
    if expedited:
        cr_fees = cr_102.get("key_fees_aed", {}) if isinstance(cr_102, dict) else {}
        expedited_fee = int(cr_fees.get("expedited_one_day_examination", 2250))

    discount_pct = 0
    if is_sme and isinstance(cr_102, dict):
        discount_pct = int(cr_102.get("sme_discount_pct", 50))

    final_min = fee_min + expedited_fee
    final_max = fee_max + expedited_fee
    if discount_pct > 0:
        final_min = int(final_min * (100 - discount_pct) / 100)
        final_max = int(final_max * (100 - discount_pct) / 100)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "authority": _block("authority"),
                "search": trademark.get("search"),
                "process_steps": registration.get("process_steps", []),
                "timeline_months_min": registration.get("timeline_months_min"),
                "timeline_months_max": registration.get("timeline_months_max"),
                "estimated_total_aed": {"min": final_min, "max": final_max},
                "expedited_examination": expedited,
                "is_sme": is_sme,
                "sme_discount_applied_pct": discount_pct if discount_pct else 0,
                "cabinet_resolution_102_2025": cr_102,
                "wipo_madrid": trademark.get("wipo_madrid"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def ip_protection(
    ip_type: str = "trademark",
) -> dict[str, object]:
    """
    Return UAE IP protection guidance for trademark, patent, or copyright.

    Args:
        ip_type: One of "trademark", "patent", "copyright".
    """
    valid = {"trademark", "patent", "copyright"}
    if ip_type not in valid:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"ip_type must be one of {sorted(valid)}, got {ip_type!r}")
            .model_dump()
        )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "ip_type": ip_type,
                "authority": _block("authority"),
                "details": _block(ip_type),
                "api_status": _block("api_status"),
                "recommended_approach": _DATA.get("recommended_approach"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
