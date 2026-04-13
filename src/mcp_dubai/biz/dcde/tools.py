"""dcde tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("dcde.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("dcde", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _list(name: str) -> list[dict[str, Any]]:
    item = _DATA.get(name, [])
    return list(item) if isinstance(item, list) else []


async def dcde_programs(program_id: str | None = None) -> dict[str, object]:
    """
    Look up Dubai Chamber of Digital Economy programs.

    Args:
        program_id: Optional program id (e.g., "antler_residency",
            "frwrdx", "create_apps_championship", "dubai_founders_hq").
    """
    programs = _list("programs")
    if program_id:
        needle = program_id.lower()
        for p in programs:
            if str(p.get("id", "")).lower() == needle:
                return ToolResponse[dict[str, object]].ok(p, knowledge=KNOWLEDGE).model_dump()
        valid = sorted(str(p.get("id", "")) for p in programs)
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"Unknown program_id {program_id!r}. Valid: {valid}")
            .model_dump()
        )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(programs),
                "programs": programs,
                "chamber": _block("chamber"),
                "impact_2025": _block("impact_2025"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def chamber_membership() -> dict[str, object]:
    """
    Return Dubai chamber membership rules.

    DCDE has no standalone membership scheme. Dubai Chamber of Commerce
    membership is mandatory for mainland commercial license holders.
    """
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "membership": _block("membership"),
                "chamber": _block("chamber"),
                "knowledge_hub": _block("knowledge_hub"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
