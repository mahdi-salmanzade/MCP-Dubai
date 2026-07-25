"""FastMCP server for compliance."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.compliance import tools

mcp: FastMCP = FastMCP("compliance")


@mcp.tool
async def aml_requirements(business_category: str = "general") -> dict[str, object]:
    """
    Return AML/CFT requirements for a business category.

    Specifically flags DNFBP (Designated Non-Financial Business or
    Profession) categories that must register on goAML. Common categories:
    real_estate, precious_metals, auditor, corporate_service_provider,
    lawyer, notary.
    """
    return await tools.aml_requirements(business_category=business_category)


@mcp.tool
async def emiratisation_requirements(employee_count: int | None = None) -> dict[str, object]:
    """
    Return MOHRE Emiratisation targets and non-compliance charges.

    Firms with 50+ employees: 1% semi-annual increase of Emiratis in
    skilled roles (2% per year, toward 10% by end-2026); unachieved
    positions charged AED 10,000 per month from 2026-07-01. Firms with
    20-49 employees in 14 selected sectors: annual quota (1 Emirati by
    2024, 2 by 2025).

    Args:
        employee_count: Optional workforce size to flag the applicable band.
    """
    return await tools.emiratisation_requirements(employee_count=employee_count)


@mcp.tool
async def ubo_filing_guide() -> dict[str, object]:
    """
    Return UBO (Ultimate Beneficial Owner) filing requirements.

    Cabinet Decision 109 of 2023, in force since 16 November 2023 (it
    superseded Cabinet Decision 58 of 2020). 25% threshold. 15-day update
    window. Administrative penalties come from Cabinet Decision 132 of 2023
    and are graduated: warning, then up to AED 50,000, then up to AED 100,000.
    """
    return await tools.ubo_filing_guide()


@mcp.tool
async def pdpl_compliance(jurisdiction: str = "uae_federal") -> dict[str, object]:
    """
    Return data protection compliance details for a UAE jurisdiction.

    Args:
        jurisdiction: One of "uae_federal" (Federal Decree-Law 45/2021),
            "difc" (DIFC Law 5/2020), "adgm" (ADGM DPR 2021).
    """
    return await tools.pdpl_compliance(jurisdiction=jurisdiction)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="aml_requirements",
        description="UAE AML/CFT requirements under Federal Decree-Law 10 of 2025 for DNFBPs (real estate, precious metals, auditors, CSPs, lawyers).",
        feature="compliance",
        tier=TIER_BIZ,
        tags=["aml", "cft", "money laundering", "goaml", "dnfbp", "fiu", "kyc", "compliance"],
    ),
    ToolMeta(
        name="emiratisation_requirements",
        description="MOHRE Emiratisation targets and charges: 50+ employee firms (1% semi-annual, AED 10,000/month per unachieved position from July 2026) and 20-49 employee firms in selected sectors.",
        feature="compliance",
        tier=TIER_BIZ,
        tags=[
            "emiratisation",
            "nafis",
            "mohre",
            "quota",
            "skilled roles",
            "workforce",
            "hiring",
            "uae nationals",
            "compliance",
        ],
    ),
    ToolMeta(
        name="ubo_filing_guide",
        description="UAE Ultimate Beneficial Owner (UBO) filing requirements and 25% threshold.",
        feature="compliance",
        tier=TIER_BIZ,
        tags=["ubo", "beneficial owner", "25%", "filing", "cabinet decision 58", "compliance"],
    ),
    ToolMeta(
        name="pdpl_compliance",
        description="UAE data protection law compliance: federal PDPL, DIFC DPL, ADGM DPR.",
        feature="compliance",
        tier=TIER_BIZ,
        tags=[
            "pdpl",
            "data protection",
            "gdpr",
            "privacy",
            "difc",
            "adgm",
            "federal decree-law 45",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
