"""halal tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("halal.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("halal", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _list(name: str) -> list[dict[str, Any]]:
    item = _DATA.get(name, [])
    return list(item) if isinstance(item, list) else []


async def halal_certification(
    product_category: str | None = None,
) -> dict[str, object]:
    """
    Return UAE halal certification guidance.

    The authority is MOIAT (Ministry of Industry and Advanced Technology),
    which absorbed ESMA in 2020. Do not refer founders to ESMA.

    Args:
        product_category: Optional substring filter on the products list.
    """
    products = _DATA.get("products_requiring_certification", [])
    if not isinstance(products, list):
        products = []
    if product_category:
        needle = product_category.lower()
        products = [p for p in products if needle in str(p).lower()]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "authority": _block("authority"),
                "standards": _list("standards"),
                "governing_law": _DATA.get("governing_law"),
                "halal_mark": _block("halal_mark"),
                "products_requiring_certification": products,
                "certification_bodies": _block("certification_bodies"),
                "recommended_approach": _DATA.get("recommended_approach"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def moiat_requirements() -> dict[str, object]:
    """Return MOIAT registration fees and timeline for Halal Certification Bodies."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "authority": _block("authority"),
                "hcb_registration": _block("hcb_registration"),
                "certification_bodies": _block("certification_bodies"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
