"""createapps tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("createapps.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("createapps", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _list(name: str) -> list[dict[str, Any]]:
    item = _DATA.get(name, [])
    return list(item) if isinstance(item, list) else []


async def createapps_championship() -> dict[str, object]:
    """
    Return Create Apps Championship details for the current cycle.

    Cycle 3: Oct 2025 to May 2026, USD 720,000 prize pool across 4
    categories (USD 150,000 each). Semi-finals 13 April 2026, grand
    finale 11 May 2026 at Museum of the Future.
    """
    programs = _list("programs")
    for p in programs:
        if str(p.get("id", "")) == "championship":
            return (
                ToolResponse[dict[str, object]]
                .ok(
                    {
                        "championship": p,
                        "initiative": _block("initiative"),
                    },
                    knowledge=KNOWLEDGE,
                )
                .model_dump()
            )

    return (
        ToolResponse[dict[str, object]]
        .fail(error="Championship entry not found in curated dataset")
        .model_dump()
    )


async def submission_guide() -> dict[str, object]:
    """
    Return submission guidance for Create Apps Championship and other programs.

    Includes evaluation criteria, application URL, and tips for the next
    cycle window.
    """
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "initiative": _block("initiative"),
                "submission_guide": _block("submission_guide"),
                "all_programs": _list("programs"),
                "contact": _block("contact"),
                "api_status": _block("api_status"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
