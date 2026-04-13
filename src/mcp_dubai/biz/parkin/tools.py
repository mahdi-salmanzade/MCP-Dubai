"""parkin tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("parkin.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("parkin", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _list(name: str) -> list[dict[str, Any]]:
    item = _DATA.get(name, [])
    return list(item) if isinstance(item, list) else []


async def parking_zones() -> dict[str, object]:
    """
    Return Dubai parking (Parkin) zone info, tariffs, and free periods.

    CRITICAL: 'Mawaqif' is Abu Dhabi, not Dubai. Dubai paid parking is
    operated by Parkin Company PJSC.
    """
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "operator": _block("operator"),
                "naming_correction": _block("naming_correction"),
                "tariffs": _block("tariffs"),
                "zones": _block("zones"),
                "mparking": _block("mparking"),
                "datasets_status": _block("datasets_status"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def nol_card_guide(card_type: str | None = None) -> dict[str, object]:
    """
    Return Nol card guide and RTA fare structure.

    Args:
        card_type: Optional card type substring filter (Red, Silver, Gold,
            Blue, PoD).
    """
    cards = _list("nol_cards")
    if card_type:
        needle = card_type.lower()
        cards = [c for c in cards if needle in str(c.get("type", "")).lower()]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "rta_fares": _block("rta_fares"),
                "cards_count": len(cards),
                "cards": cards,
                "nol_api_status": _block("nol_api_status"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
