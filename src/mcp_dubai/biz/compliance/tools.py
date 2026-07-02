"""compliance tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("compliance.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("compliance", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


VALID_DNFBP_CATEGORIES = {
    "real_estate",
    "precious_metals",
    "auditor",
    "corporate_service_provider",
    "trust_company_service_provider",
    "lawyer",
    "notary",
}


async def aml_requirements(
    business_category: str = "general",
) -> dict[str, object]:
    """
    Return AML/CFT requirements applicable to a business category.

    Specifically flags DNFBP (Designated Non-Financial Business or
    Profession) categories that must register on goAML.
    """
    aml = _block("aml_cft")
    dnfbp_list = aml.get("dnfbp_categories", [])
    if not isinstance(dnfbp_list, list):
        dnfbp_list = []

    matching: list[dict[str, Any]] = []
    if business_category != "general":
        needle = business_category.lower().replace("_", " ")
        for cat in dnfbp_list:
            if isinstance(cat, dict):
                cat_name = str(cat.get("category", "")).lower()
                if needle in cat_name:
                    matching.append(cat)

    is_dnfbp = len(matching) > 0

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "business_category": business_category,
                "is_dnfbp": is_dnfbp,
                "matching_categories": matching,
                "all_dnfbp_categories": dnfbp_list,
                "law": aml.get("law"),
                "law_in_force_since": aml.get("law_in_force_since"),
                "implementing_regulation": aml.get("implementing_regulation"),
                "previous_law": aml.get("previous_law"),
                "key_changes_2025": aml.get("key_changes_2025"),
                "dfsa_alignment": aml.get("dfsa_alignment"),
                "regulator": aml.get("regulator"),
                "portal_url": aml.get("portal_url"),
                "fines_aed": aml.get("fines_aed"),
                "vara_separate_note": aml.get("vara_separate"),
                "next_steps": (
                    [
                        "Register on goAML at https://www.fiu.gov.ae",
                        "Appoint a Money Laundering Reporting Officer (MLRO)",
                        "Implement KYC and Customer Due Diligence procedures",
                        "File Suspicious Transaction Reports (STRs) when triggered",
                    ]
                    if is_dnfbp
                    else [
                        "Not a DNFBP category. AML rules still apply for high-value transactions."
                    ]
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def emiratisation_requirements(
    employee_count: int | None = None,
) -> dict[str, object]:
    """
    Return MOHRE Emiratisation targets and non-compliance charges.

    Args:
        employee_count: Optional workforce size. When given, the response
            flags which band applies: "firms_50_plus" (1% semi-annual
            increase in skilled roles), "firms_20_to_49" (annual quota in
            14 selected sectors), or "none" (below 20 employees).
    """
    if employee_count is not None and employee_count < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"employee_count must be non-negative, got {employee_count}")
            .model_dump()
        )

    emiratisation = _block("emiratisation")
    applicable_band: str | None = None
    band_note: str | None = None
    if employee_count is not None:
        if employee_count >= 50:
            applicable_band = "firms_50_plus"
            band_note = (
                "Semi-annual 1% Emiratisation increase in skilled roles applies. "
                "The H1 2026 deadline of 2026-06-30 has passed; unachieved positions "
                "are charged AED 10,000 per month from 2026-07-01."
            )
        elif employee_count >= 20:
            applicable_band = "firms_20_to_49"
            band_note = "Annual quota applies only if the company operates in one of the 14 selected sectors."
        else:
            applicable_band = "none"
            band_note = (
                "Companies with fewer than 20 employees currently have no Emiratisation quota."
            )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "employee_count": employee_count,
                "applicable_band": applicable_band,
                "band_note": band_note,
                **emiratisation,
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def ubo_filing_guide() -> dict[str, object]:
    """Return UBO filing requirements and threshold rules."""
    ubo = _block("ubo")
    return ToolResponse[dict[str, object]].ok(ubo, knowledge=KNOWLEDGE).model_dump()


async def pdpl_compliance(
    jurisdiction: str = "uae_federal",
) -> dict[str, object]:
    """
    Return data protection compliance details for a UAE jurisdiction.

    Args:
        jurisdiction: One of "uae_federal", "difc", "adgm".
    """
    valid = {"uae_federal", "difc", "adgm"}
    if jurisdiction not in valid:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"jurisdiction must be one of {sorted(valid)}, got {jurisdiction!r}")
            .model_dump()
        )

    pdpl = _block("pdpl")
    if jurisdiction == "uae_federal":
        block = pdpl.get("uae_federal", {})
    elif jurisdiction == "difc":
        block = pdpl.get("difc_dpl", {})
    else:
        block = pdpl.get("adgm_dpr", {})

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {"jurisdiction": jurisdiction, **block}
            if isinstance(block, dict)
            else {"jurisdiction": jurisdiction},
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
