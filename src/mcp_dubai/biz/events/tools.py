"""events tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("events.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("events", KNOWLEDGE)


def _all_events() -> list[dict[str, Any]]:
    items = _DATA.get("events", [])
    return list(items) if isinstance(items, list) else []


async def startup_events(category: str | None = None) -> dict[str, object]:
    """
    List Dubai and UAE startup and tech events.

    Args:
        category: Optional substring filter on event type or name.
    """
    events = _all_events()
    if category:
        needle = category.lower()
        events = [
            e
            for e in events
            if needle in str(e.get("type", "")).lower()
            or needle in str(e.get("name", "")).lower()
            or needle in str(e.get("tagline", "")).lower()
        ]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {"count": len(events), "events": events},
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def gitex_info() -> dict[str, object]:
    """Return GITEX Global 2026 details and venue."""
    events = _all_events()
    for e in events:
        if str(e.get("id", "")) == "gitex_global_2026":
            return ToolResponse[dict[str, object]].ok(e, knowledge=KNOWLEDGE).model_dump()
    return (
        ToolResponse[dict[str, object]]
        .fail(error="GITEX 2026 entry not found in curated dataset")
        .model_dump()
    )


async def ens_calendar() -> dict[str, object]:
    """Return Expand North Star 2026 calendar, application window, and venue."""
    events = _all_events()
    for e in events:
        if str(e.get("id", "")) == "expand_north_star_2026":
            return ToolResponse[dict[str, object]].ok(e, knowledge=KNOWLEDGE).model_dump()
    return (
        ToolResponse[dict[str, object]]
        .fail(error="Expand North Star 2026 entry not found in curated dataset")
        .model_dump()
    )
