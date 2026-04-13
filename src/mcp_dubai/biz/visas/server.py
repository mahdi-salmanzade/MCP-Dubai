"""FastMCP server for visas."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.biz.visas import tools

mcp: FastMCP = FastMCP("visas")


@mcp.tool
async def list_visa_types() -> dict[str, object]:
    """List every UAE visa type in the curated dataset."""
    return await tools.list_visa_types()


@mcp.tool
async def visa_details(visa_id: str) -> dict[str, object]:
    """
    Get the full curated record for a single UAE visa type.

    Args:
        visa_id: Visa id slug. Examples: "investor_partner", "employment",
            "golden_specialized_talent", "golden_investor_real_estate",
            "golden_entrepreneur", "green_skilled_employee",
            "green_freelancer", "freelance_permit", "virtual_working",
            "retirement", "family_dependent", "tourist_30", "tourist_60".
    """
    return await tools.visa_details(visa_id=visa_id)


@mcp.tool
async def visa_recommend(
    profile: str,
    monthly_salary_aed: int | None = None,
    annual_income_aed: int | None = None,
    has_uae_employer: bool = False,
    has_uae_trade_license: bool = False,
    age: int | None = None,
    duration_years_min: int | None = None,
) -> dict[str, object]:
    """
    Recommend a UAE visa type for a given founder/employee profile.

    Args:
        profile: One of: founder, salaried_employee, freelancer,
            remote_worker, investor, real_estate_investor,
            specialized_talent, spouse_or_dependent, retiree, tourist.
        monthly_salary_aed: Monthly basic salary in AED, if relevant.
        annual_income_aed: Annual income in AED for freelancer profiles.
        has_uae_employer: True if there is a UAE-registered employer.
        has_uae_trade_license: True if the user already holds a UAE
            trade license.
        age: Age in years (used for retirement visa).
        duration_years_min: Optional minimum residency duration.

    Returns:
        ToolResponse envelope. `data` carries `profile`, `candidates`
        (ranked list of visa options with `why`), `reasoning`, `warnings`.
    """
    return await tools.visa_recommend(
        profile=profile,
        monthly_salary_aed=monthly_salary_aed,
        annual_income_aed=annual_income_aed,
        has_uae_employer=has_uae_employer,
        has_uae_trade_license=has_uae_trade_license,
        age=age,
        duration_years_min=duration_years_min,
    )


@mcp.tool
async def golden_visa_check(
    monthly_salary_aed: int | None = None,
    real_estate_value_aed: int | None = None,
    project_value_aed: int | None = None,
) -> dict[str, object]:
    """
    Check eligibility for the main Golden Visa categories.

    Args:
        monthly_salary_aed: Basic monthly salary for the specialized talent
            category. Must be at least AED 30,000 (verified over the prior
            24 months as of early 2026).
        real_estate_value_aed: UAE property value for the investor category.
            Must be at least AED 2,000,000 in approved areas.
        project_value_aed: Business project value for the entrepreneur
            category. Must be at least AED 500,000 in technical / future
            fields with Ministry of Economy or accredited incubator approval.
    """
    return await tools.golden_visa_check(
        monthly_salary_aed=monthly_salary_aed,
        real_estate_value_aed=real_estate_value_aed,
        project_value_aed=project_value_aed,
    )


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="list_visa_types",
        description="List every UAE visa type with id, name, and duration.",
        feature="visas",
        tier=TIER_BIZ,
        tags=["visa", "list", "types", "uae", "residence", "all"],
    ),
    ToolMeta(
        name="visa_details",
        description="Get the full curated record for a specific UAE visa type by id.",
        feature="visas",
        tier=TIER_BIZ,
        tags=["visa", "details", "lookup", "golden", "green", "freelance", "investor"],
    ),
    ToolMeta(
        name="visa_recommend",
        description=(
            "Recommend a UAE visa type for a founder, employee, freelancer, "
            "remote worker, retiree, or family member. Cross-references "
            "salary, income, age, and employer status."
        ),
        feature="visas",
        tier=TIER_BIZ,
        tags=[
            "visa",
            "recommend",
            "advice",
            "founder",
            "freelancer",
            "remote",
            "employee",
            "investor",
            "retiree",
            "family",
            "spouse",
            "dependent",
            "which visa",
            "what visa",
        ],
    ),
    ToolMeta(
        name="golden_visa_check",
        description=(
            "Check eligibility for the Golden Visa specialized talent, real "
            "estate investor, and entrepreneur categories."
        ),
        feature="visas",
        tier=TIER_BIZ,
        tags=[
            "golden visa",
            "10 year",
            "long term",
            "eligibility",
            "specialized talent",
            "investor",
            "entrepreneur",
            "real estate",
        ],
    ),
]

get_tool_discovery().register_many(_TOOLS)
