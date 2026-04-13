"""visas tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("visas.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("visas", KNOWLEDGE)


def _all_visas() -> list[dict[str, Any]]:
    items = _DATA.get("visas", [])
    return list(items) if isinstance(items, list) else []


VALID_PROFILES = {
    "founder",
    "salaried_employee",
    "freelancer",
    "remote_worker",
    "investor",
    "real_estate_investor",
    "specialized_talent",
    "spouse_or_dependent",
    "retiree",
    "tourist",
}


async def list_visa_types() -> dict[str, object]:
    """List every UAE visa type in the curated dataset."""
    visas = _all_visas()
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(visas),
                "visas": [
                    {
                        "id": v.get("id"),
                        "name": v.get("name"),
                        "track": v.get("track"),
                        "duration_label": v.get("duration_label"),
                    }
                    for v in visas
                ],
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def visa_details(visa_id: str) -> dict[str, object]:
    """Return the full curated record for a single visa type by id."""
    if not visa_id:
        return ToolResponse[dict[str, object]].fail(error="visa_id must not be empty").model_dump()

    needle = visa_id.strip().lower()
    for visa in _all_visas():
        if str(visa.get("id", "")).lower() == needle:
            return ToolResponse[dict[str, object]].ok(visa, knowledge=KNOWLEDGE).model_dump()

    valid_ids = sorted(str(v.get("id", "")) for v in _all_visas())
    return (
        ToolResponse[dict[str, object]]
        .fail(error=f"Unknown visa_id {visa_id!r}. Valid: {valid_ids}")
        .model_dump()
    )


async def visa_recommend(
    profile: str,
    monthly_salary_aed: int | None = None,
    annual_income_aed: int | None = None,
    has_uae_employer: bool = False,
    has_uae_trade_license: bool = False,
    age: int | None = None,
    duration_years_min: int | None = None,
) -> dict[str, object]:
    """Recommend a UAE visa type for a given founder/employee profile."""
    if profile not in VALID_PROFILES:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=(f"profile must be one of {sorted(VALID_PROFILES)}, got {profile!r}"))
            .model_dump()
        )
    if monthly_salary_aed is not None and monthly_salary_aed < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"monthly_salary_aed must be >= 0, got {monthly_salary_aed}")
            .model_dump()
        )
    if age is not None and age < 0:
        return (
            ToolResponse[dict[str, object]].fail(error=f"age must be >= 0, got {age}").model_dump()
        )

    candidates: list[dict[str, Any]] = []
    reasoning: list[str] = []
    warnings: list[str] = []

    visas = _all_visas()
    by_id = {str(v.get("id", "")): v for v in visas}

    def _add(visa_id: str, why: str) -> None:
        v = by_id.get(visa_id)
        if v is not None:
            candidates.append(
                {
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "track": v.get("track"),
                    "duration_label": v.get("duration_label"),
                    "why": why,
                }
            )

    if profile == "founder":
        if has_uae_trade_license:
            _add(
                "investor_partner",
                "You hold a UAE trade license, so the Investor / Partner Visa is the standard founder route (2-year residence).",
            )
        if monthly_salary_aed and monthly_salary_aed >= 30000:
            _add(
                "golden_specialized_talent",
                "AED 30,000+ monthly salary qualifies for Golden Visa specialized talent track (10-year). Note: salary must be BASIC (not total comp), verified for 24 months.",
            )
        _add(
            "golden_entrepreneur",
            "Founders with a project worth at least AED 500,000 in technical/future fields can apply for the Golden Visa entrepreneur category.",
        )

    elif profile == "salaried_employee":
        if has_uae_employer:
            _add("employment", "Standard 2-year Employment Visa, sponsored by your UAE employer.")
        if monthly_salary_aed and monthly_salary_aed >= 15000:
            _add(
                "green_skilled_employee",
                "AED 15,000+ monthly salary qualifies for the Green Visa skilled employee track (5-year, self-sponsored).",
            )
            warnings.append(
                "Green Visa requires MOHRE skill level 1, 2, or 3 plus a bachelor's degree."
            )
        if monthly_salary_aed and monthly_salary_aed >= 30000:
            _add(
                "golden_specialized_talent",
                "AED 30,000+ monthly basic salary may qualify for Golden Visa specialized talent.",
            )

    elif profile == "freelancer":
        _add(
            "freelance_permit",
            "Start with a Freelance Permit (TECOM, GoFreelance, or other free zone freelance program). 1 to 2 years.",
        )
        if annual_income_aed and annual_income_aed >= 180000:
            _add(
                "green_freelancer",
                "AED 360,000 cumulative income over the prior 2 years qualifies for the Green Visa freelancer track (5-year, self-sponsored).",
            )

    elif profile == "remote_worker":
        if monthly_salary_aed and monthly_salary_aed * 3.67 >= 3500:  # rough USD conversion
            _add(
                "virtual_working",
                "USD 3,500+ monthly salary from a foreign employer qualifies for the Virtual Working Programme (1-year UAE residency).",
            )
        else:
            _add(
                "virtual_working",
                "Virtual Working Programme requires USD 3,500+ monthly salary from a foreign employer.",
            )

    elif profile == "investor":
        _add(
            "investor_partner", "Investor / Partner Visa (2 years), linked to a UAE trade license."
        )
        _add(
            "golden_entrepreneur",
            "Golden Visa entrepreneur category for projects worth at least AED 500,000 in technical/future fields.",
        )

    elif profile == "real_estate_investor":
        _add(
            "golden_investor_real_estate",
            "Real estate worth AED 2 million or more in approved areas qualifies for the 10-year Golden Visa.",
        )

    elif profile == "specialized_talent":
        _add(
            "golden_specialized_talent",
            "Specialised talent Golden Visa requires AED 30,000+ basic monthly salary verified over 24 months and a recognised qualification.",
        )

    elif profile == "spouse_or_dependent":
        _add(
            "family_dependent", "Family / Dependent Visa, linked to your sponsor's residence visa."
        )
        warnings.append(
            "Sponsor minimum salary: AED 4,000 + housing OR AED 5,000 all-in. Marriage and birth certificates must be attested."
        )

    elif profile == "retiree":
        if age is not None and age >= 55:
            _add(
                "retirement",
                "Retirement Visa (5 years). Requires AED 1M property OR savings OR AED 20,000 monthly income.",
            )
        else:
            warnings.append("Retirement Visa requires age 55 or older.")

    elif profile == "tourist":
        _add("tourist_60", "60-day Tourist Visa for longer scoping trips.")
        _add("tourist_30", "30-day Tourist Visa for short scoping trips.")

    if not candidates:
        warnings.append(
            "No recommendation matched this profile and the supplied numbers. "
            "Use list_visa_types() to browse all options."
        )

    reasoning.append(
        "Recommendations are derived from the curated visas dataset. "
        "Verify final requirements with ICP, GDRFA Dubai, or Amer."
    )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "profile": profile,
                "candidates": candidates,
                "reasoning": reasoning,
                "warnings": warnings,
                "inputs": {
                    "monthly_salary_aed": monthly_salary_aed,
                    "annual_income_aed": annual_income_aed,
                    "has_uae_employer": has_uae_employer,
                    "has_uae_trade_license": has_uae_trade_license,
                    "age": age,
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def golden_visa_check(
    monthly_salary_aed: int | None = None,
    real_estate_value_aed: int | None = None,
    project_value_aed: int | None = None,
) -> dict[str, object]:
    """Check eligibility for the main Golden Visa categories."""
    eligible: list[dict[str, str]] = []
    not_eligible: list[dict[str, str]] = []

    if monthly_salary_aed is not None:
        if monthly_salary_aed >= 30000:
            eligible.append(
                {
                    "category": "specialized_talent",
                    "criterion": (
                        "AED 30,000+ basic monthly salary (verified over the "
                        "prior 24 months). Tightened in early 2026."
                    ),
                }
            )
        else:
            not_eligible.append(
                {
                    "category": "specialized_talent",
                    "criterion": (
                        f"Need AED 30,000+ basic monthly. Have AED {monthly_salary_aed}. "
                        "Note: must be BASIC salary, not total compensation."
                    ),
                }
            )

    if real_estate_value_aed is not None:
        if real_estate_value_aed >= 2000000:
            eligible.append(
                {
                    "category": "real_estate_investor",
                    "criterion": "AED 2,000,000+ in UAE property in approved areas.",
                }
            )
        else:
            not_eligible.append(
                {
                    "category": "real_estate_investor",
                    "criterion": (
                        f"Need AED 2,000,000+ in property. Have AED {real_estate_value_aed}."
                    ),
                }
            )

    if project_value_aed is not None:
        if project_value_aed >= 500000:
            eligible.append(
                {
                    "category": "entrepreneur",
                    "criterion": (
                        "Project worth AED 500,000+ in technical / future fields. "
                        "Requires Ministry of Economy or accredited incubator approval."
                    ),
                }
            )
        else:
            not_eligible.append(
                {
                    "category": "entrepreneur",
                    "criterion": (
                        f"Need AED 500,000+ project value. Have AED {project_value_aed}."
                    ),
                }
            )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "any_eligible": len(eligible) > 0,
                "eligible": eligible,
                "not_eligible": not_eligible,
                "inputs": {
                    "monthly_salary_aed": monthly_salary_aed,
                    "real_estate_value_aed": real_estate_value_aed,
                    "project_value_aed": project_value_aed,
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
