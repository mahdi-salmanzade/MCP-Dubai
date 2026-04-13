"""gov_portals tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("gov_portals.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("gov_portals", KNOWLEDGE)


def _all_portals() -> list[dict[str, Any]]:
    items = _DATA.get("portals", [])
    return list(items) if isinstance(items, list) else []


def _disambiguation() -> list[dict[str, Any]]:
    items = _DATA.get("disambiguation", [])
    return list(items) if isinstance(items, list) else []


async def portal_guide(
    portal_id: str | None = None,
    keyword: str | None = None,
) -> dict[str, object]:
    """
    Look up a UAE government portal by id or by keyword.

    Args:
        portal_id: Portal id slug (e.g., "uae_pass", "emaratax", "mohre").
        keyword: Substring search across portal name, type, and operator.
    """
    portals = _all_portals()

    if portal_id:
        needle = portal_id.strip().lower()
        for p in portals:
            if str(p.get("id", "")).lower() == needle:
                return ToolResponse[dict[str, object]].ok(p, knowledge=KNOWLEDGE).model_dump()

        valid_ids = sorted(str(p.get("id", "")) for p in portals)
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"Unknown portal_id {portal_id!r}. Valid: {valid_ids}")
            .model_dump()
        )

    if keyword:
        kw = keyword.lower()
        matching = [
            p
            for p in portals
            if kw in str(p.get("name", "")).lower()
            or kw in str(p.get("type", "")).lower()
            or kw in str(p.get("operator", "")).lower()
            or kw in str(p.get("what_it_does", "")).lower()
        ]
        return (
            ToolResponse[dict[str, object]]
            .ok(
                {"count": len(matching), "portals": matching},
                knowledge=KNOWLEDGE,
            )
            .model_dump()
        )

    # No filter: return a compact list
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(portals),
                "portals": [
                    {
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "url": p.get("url"),
                        "type": p.get("type"),
                        "developer_api": p.get("developer_api", False),
                    }
                    for p in portals
                ],
                "disambiguation": _disambiguation(),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
