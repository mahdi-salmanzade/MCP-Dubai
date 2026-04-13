"""tax_compliance tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("tax_compliance.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("tax_compliance", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


VALID_INDUSTRIES = {
    "saas",
    "tech",
    "ecommerce",
    "consulting",
    "fintech",
    "trading",
    "manufacturing",
    "logistics",
    "media",
    "healthcare",
    "real_estate",
    "general",
}


async def corporate_tax_estimate(
    annual_taxable_income_aed: int,
    is_free_zone: bool = False,
    qfzp_qualifying_pct: int = 0,
    industry: str = "general",
) -> dict[str, object]:
    """
    Estimate UAE corporate tax liability.

    Args:
        annual_taxable_income_aed: Annual taxable income in AED.
        is_free_zone: True if the entity is in a free zone.
        qfzp_qualifying_pct: Percentage of income that is Qualifying
            Activity income (0 to 100). Only used if is_free_zone is True.
        industry: Industry category. SaaS triggers a critical warning
            since it is NOT a Qualifying Activity.

    Returns:
        Tax breakdown with thresholds, qualifying split, and effective rate.
    """
    if annual_taxable_income_aed < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"annual_taxable_income_aed must be >= 0, got {annual_taxable_income_aed}")
            .model_dump()
        )
    if not 0 <= qfzp_qualifying_pct <= 100:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"qfzp_qualifying_pct must be 0 to 100, got {qfzp_qualifying_pct}")
            .model_dump()
        )
    if industry not in VALID_INDUSTRIES:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"industry must be one of {sorted(VALID_INDUSTRIES)}, got {industry!r}")
            .model_dump()
        )

    ct = _block("corporate_tax")
    thresholds = ct.get("thresholds", {})
    free_band = int(thresholds.get("tax_free_band_aed", 375000))
    standard_rate = float(thresholds.get("standard_rate_pct", 9)) / 100

    warnings: list[str] = []

    # SaaS warning per MD 229/2025
    if is_free_zone and industry == "saas" and qfzp_qualifying_pct > 0:
        warnings.append(
            "CRITICAL: SaaS is NOT a Qualifying Activity under Ministerial "
            "Decision 229 of 2025. Most free zone SaaS revenue is taxed at "
            "9% (above the AED 375,000 threshold), NOT the 0% QFZP rate. "
            "Treat your qfzp_qualifying_pct as 0 unless you have an explicit "
            "FTA ruling that says otherwise."
        )

    # Calculate
    taxable_above_threshold = max(0, annual_taxable_income_aed - free_band)

    if is_free_zone and qfzp_qualifying_pct > 0:
        qualifying_share = taxable_above_threshold * qfzp_qualifying_pct / 100
        non_qualifying_share = taxable_above_threshold - qualifying_share
        tax_qualifying = 0  # 0% on qualifying income
        tax_non_qualifying = int(non_qualifying_share * standard_rate)
        total_tax = tax_qualifying + tax_non_qualifying
    else:
        qualifying_share = 0
        non_qualifying_share = taxable_above_threshold
        tax_qualifying = 0
        tax_non_qualifying = int(taxable_above_threshold * standard_rate)
        total_tax = tax_non_qualifying

    effective_rate = (
        (total_tax / annual_taxable_income_aed * 100) if annual_taxable_income_aed > 0 else 0.0
    )

    # Small business relief check
    sbr = ct.get("small_business_relief", {})
    sbr_threshold = int(sbr.get("revenue_threshold_aed", 3000000))
    if annual_taxable_income_aed <= sbr_threshold:
        warnings.append(
            f"You may qualify for Small Business Relief (Ministerial Decision "
            f"73/2023) if your REVENUE is at or below AED {sbr_threshold:,}. "
            f"Available through tax periods ending 31 December 2026."
        )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "inputs": {
                    "annual_taxable_income_aed": annual_taxable_income_aed,
                    "is_free_zone": is_free_zone,
                    "qfzp_qualifying_pct": qfzp_qualifying_pct,
                    "industry": industry,
                },
                "tax_free_band_aed": free_band,
                "taxable_above_threshold_aed": taxable_above_threshold,
                "qualifying_income_aed": int(qualifying_share),
                "non_qualifying_income_aed": int(non_qualifying_share),
                "tax_on_qualifying_aed": tax_qualifying,
                "tax_on_non_qualifying_aed": tax_non_qualifying,
                "total_corporate_tax_aed": total_tax,
                "effective_rate_pct": round(effective_rate, 2),
                "warnings": warnings,
                "law": ct.get("law", "Federal Decree-Law 47 of 2022"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def vat_filing_calendar(
    annual_revenue_aed: int,
) -> dict[str, object]:
    """
    Determine the VAT registration requirement and filing frequency
    for a UAE business.
    """
    if annual_revenue_aed < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"annual_revenue_aed must be >= 0, got {annual_revenue_aed}")
            .model_dump()
        )

    vat = _block("vat")
    mandatory = int(vat.get("mandatory_registration_threshold_aed", 375000))
    voluntary = int(vat.get("voluntary_registration_threshold_aed", 187500))
    monthly_threshold = int(
        vat.get("filing_frequency", {}).get("monthly_at_or_above_aed_revenue", 150000000)
    )
    deadline_day = int(vat.get("filing_deadline_day_of_month", 28))

    if annual_revenue_aed >= mandatory:
        registration = "mandatory"
        registration_reason = (
            f"Annual revenue at or above AED {mandatory:,} requires mandatory VAT registration."
        )
    elif annual_revenue_aed >= voluntary:
        registration = "voluntary_eligible"
        registration_reason = (
            f"Annual revenue between AED {voluntary:,} and AED {mandatory:,} "
            "qualifies for voluntary VAT registration."
        )
    else:
        registration = "not_required"
        registration_reason = (
            f"Annual revenue below AED {voluntary:,} does not require VAT registration."
        )

    frequency = "monthly" if annual_revenue_aed >= monthly_threshold else "quarterly"

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "annual_revenue_aed": annual_revenue_aed,
                "registration": registration,
                "registration_reason": registration_reason,
                "filing_frequency": frequency,
                "filing_deadline_day_of_month": deadline_day,
                "rate_pct": vat.get("rate_pct", 5),
                "thresholds": {
                    "mandatory_aed": mandatory,
                    "voluntary_aed": voluntary,
                    "monthly_filing_at_aed_revenue": monthly_threshold,
                },
                "portal": "EmaraTax (https://eservices.tax.gov.ae)",
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def qfzp_check(
    industry: str = "general",
    is_free_zone: bool = True,
) -> dict[str, object]:
    """
    Check whether a business is likely to qualify for QFZP 0% on
    qualifying income.
    """
    if industry not in VALID_INDUSTRIES:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"industry must be one of {sorted(VALID_INDUSTRIES)}, got {industry!r}")
            .model_dump()
        )

    ct = _block("corporate_tax")
    qfzp = ct.get("qfzp", {}) if isinstance(ct.get("qfzp"), dict) else {}

    if not is_free_zone:
        verdict = "not_eligible"
        reason = "QFZP is only available to free zone entities."
    elif industry == "saas":
        verdict = "not_qualifying"
        reason = (
            "SaaS is NOT a Qualifying Activity under Ministerial Decision "
            "229 of 2025. Free zone SaaS revenue is taxed at 9% above the "
            "AED 375,000 threshold, not the 0% QFZP rate."
        )
    elif industry in {"trading", "logistics", "manufacturing"}:
        verdict = "potentially_qualifying"
        reason = (
            "Some trading, logistics, and manufacturing activities are "
            "Qualifying Activities under MD 229/2025. Verify your specific "
            "activity against the official list."
        )
    else:
        verdict = "verify"
        reason = (
            "Verify your specific activity against the Qualifying Activities "
            "list in Ministerial Decision 229 of 2025. Most professional "
            "services are NOT qualifying."
        )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "verdict": verdict,
                "reason": reason,
                "industry": industry,
                "is_free_zone": is_free_zone,
                "current_rules_source": qfzp.get("current_rules_source"),
                "de_minimis": qfzp.get("de_minimis"),
                "law": ct.get("law"),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def esr_status() -> dict[str, object]:
    """Return the current status of UAE Economic Substance Regulations."""
    esr = _block("esr")
    return ToolResponse[dict[str, object]].ok(esr, knowledge=KNOWLEDGE).model_dump()
