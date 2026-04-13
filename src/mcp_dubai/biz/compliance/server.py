"""FastMCP server for compliance."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import TIER_BIZ, ToolMeta, get_tool_discovery
from mcp_dubai.biz.compliance import tools

mcp: FastMCP = FastMCP("compliance")


@mcp.tool
async def esr_check() -> dict[str, object]:
    """
    Check the current status of UAE Economic Substance Regulations.

    ESR is DEAD for periods after 31 December 2022 per Cabinet Resolution
    98 of 2024. This tool gives a clear answer to the still-common
    "do I need to file ESR?" question.
    """
    return await tools.esr_check()


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
async def ubo_filing_guide() -> dict[str, object]:
    """
    Return UBO (Ultimate Beneficial Owner) filing requirements.

    Cabinet Decision 58 of 2020. 25% threshold. 15-day update window.
    Max fine AED 1,000,000.
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
        name="esr_check",
        description="Check whether you need to file UAE ESR (spoiler: not for periods after Dec 2022).",
        feature="compliance",
        tier=TIER_BIZ,
        tags=["esr", "economic substance", "repealed", "filing", "compliance"],
    ),
    ToolMeta(
        name="aml_requirements",
        description="UAE AML/CFT requirements for DNFBPs (real estate, precious metals, auditors, CSPs, lawyers).",
        feature="compliance",
        tier=TIER_BIZ,
        tags=["aml", "cft", "money laundering", "goaml", "dnfbp", "fiu", "kyc", "compliance"],
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
