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


async def esr_check() -> dict[str, object]:
    """
    Check the current status of UAE Economic Substance Regulations.

    ESR is DEAD for periods after 31 December 2022 per Cabinet Resolution
    98 of 2024. This tool exists to give a clear answer to the still-common
    "do I need to file ESR?" question.
    """
    esr = _block("esr")
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "status": esr.get("status"),
                "active_for_current_periods": False,
                "warning": esr.get("warning"),
                "applies_to_periods": esr.get("applies_to_periods"),
                "repeal_law": esr.get("repeal_law"),
                "historical_penalties": esr.get("historical_penalties"),
                "relevant_activities": esr.get("relevant_activities", []),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


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
