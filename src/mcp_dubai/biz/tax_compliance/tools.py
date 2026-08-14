"""tax_compliance tool functions."""

from __future__ import annotations

import math
from typing import Any, Final

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("tax_compliance.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("tax_compliance", KNOWLEDGE)

# Average calendar month (365.25 / 12), used to convert a days_late input into
# the number of whole-or-part months the statutory penalty charges for.
_DAYS_PER_MONTH: Final[float] = 30.4375


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

    qfzp_rules_applied = is_free_zone and qfzp_qualifying_pct > 0

    # SaaS warning per MD 229/2025
    if qfzp_rules_applied and industry == "saas":
        warnings.append(
            "CRITICAL: SaaS is NOT a Qualifying Activity under Ministerial "
            "Decision 229 of 2025. Most free zone SaaS revenue is taxed at "
            "9% with no AED 375,000 tax-free band, NOT the 0% QFZP rate. "
            "Treat your qfzp_qualifying_pct as 0 unless you have an explicit "
            "FTA ruling that says otherwise."
        )

    # A QFZP does not receive the ordinary AED 375,000 0% band. Its full
    # taxable income is split between Qualifying Income at 0% and other
    # taxable income at 9%. The ordinary band still applies to a non-QFZP.
    if qfzp_rules_applied:
        tax_free_band_applied = 0
        taxable_at_rate_split = annual_taxable_income_aed
        qualifying_share = taxable_at_rate_split * qfzp_qualifying_pct / 100
        non_qualifying_share = taxable_at_rate_split - qualifying_share
        tax_qualifying = 0  # 0% on qualifying income
        tax_non_qualifying = int(non_qualifying_share * standard_rate)
        total_tax = tax_qualifying + tax_non_qualifying
        warnings.append(
            "QFZP treatment applied: the ordinary AED 375,000 0% band does not "
            "apply, and a QFZP cannot elect Small Business Relief. Confirm all "
            "QFZP conditions, including the de minimis test, with the FTA."
        )
    else:
        tax_free_band_applied = min(annual_taxable_income_aed, free_band)
        taxable_at_rate_split = max(0, annual_taxable_income_aed - free_band)
        qualifying_share = 0
        non_qualifying_share = taxable_at_rate_split
        tax_qualifying = 0
        tax_non_qualifying = int(taxable_at_rate_split * standard_rate)
        total_tax = tax_non_qualifying

    effective_rate = (
        (total_tax / annual_taxable_income_aed * 100) if annual_taxable_income_aed > 0 else 0.0
    )

    # Small business relief check
    sbr = ct.get("small_business_relief", {})
    sbr_threshold = int(sbr.get("revenue_threshold_aed", 3000000))
    sbr_period_end = str(sbr.get("available_through_periods_ending", "2029-12-31"))
    if not qfzp_rules_applied and annual_taxable_income_aed <= sbr_threshold:
        warnings.append(
            f"You may qualify for Small Business Relief (Ministerial Decision "
            f"73/2023, as amended by Ministerial Decision 131/2026) if your "
            f"REVENUE is at or below AED {sbr_threshold:,}. Available for "
            f"eligible tax periods ending on or before {sbr_period_end}."
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
                "tax_free_band_applied_aed": tax_free_band_applied,
                "qfzp_rules_applied": qfzp_rules_applied,
                # Retained for backwards compatibility. Under QFZP rules no
                # ordinary threshold applies, so this is the full taxable
                # income passed to the qualifying/non-qualifying rate split.
                "taxable_above_threshold_aed": taxable_at_rate_split,
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
    amendments = vat.get("amendments_2026", {})
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
                "amendments_2026": amendments,
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


async def einvoicing_timeline() -> dict[str, object]:
    """
    Return the UAE e-invoicing regime: legislation, the PINT AE / DCTCE
    model, the phased rollout dates, the ASP appointment deadlines, the
    current ASP accreditation register, published technical documents, and a short
    list of what to do now.

    The pilot phase went live on 1 July 2026 with voluntary adoption open
    from the same date. Verify dates against the FTA and the Ministry of
    Finance before relying on them.
    """
    einv = _block("e_invoicing")
    what_to_do_now = [
        "Appoint an accredited service provider (ASP): revenue at or above "
        "AED 50M must appoint by 30 October 2026, below AED 50M by "
        "31 March 2027. Pick from the official MoF accredited/pre-approved "
        "provider lists.",
        "Make sure your ERP or accounting system can emit PINT AE invoices "
        "and exchange them on the DCTCE 5-corner model.",
        "Consider joining the voluntary phase (open since 1 July 2026) to "
        "test end to end before your mandatory go-live date.",
        "Watch for the mandatory date that matches your revenue band so you "
        "are ready before it applies.",
    ]
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "name": einv.get("name"),
                "legislation": einv.get("legislation", []),
                "model": einv.get("model"),
                "penalties_law": einv.get("penalties_law"),
                "status": einv.get("status"),
                "rollout": einv.get("rollout", {}),
                "asp_appointment_deadlines": einv.get("asp_appointment_deadlines", {}),
                "asp_register": einv.get("asp_register", {}),
                "technical_docs": einv.get("technical_docs", {}),
                "scope_note": einv.get("scope_note"),
                "what_to_do_now": what_to_do_now,
                "source_urls": einv.get("source_urls", []),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def late_payment_penalty_estimate(
    tax_due_aed: float,
    days_late: int,
) -> dict[str, object]:
    """
    Estimate the unified UAE late-payment penalty (Cabinet Decision 129 of
    2025, effective 14 April 2026) on overdue tax.

    The 14% per annum rate accrues MONTHLY, for each month or part thereof,
    from the day following the due date. It is not pro-rated by day, so one
    day late already attracts a full month of penalty. There is no cap (the
    old regime's 300% ceiling went with the 2% + 4%-per-month structure).

    Args:
        tax_due_aed: The unpaid tax amount in AED (must be > 0).
        days_late: Number of days the payment is late (must be >= 0).
    """
    if tax_due_aed <= 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"tax_due_aed must be > 0, got {tax_due_aed}")
            .model_dump()
        )
    if days_late < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"days_late must be >= 0, got {days_late}")
            .model_dump()
        )

    lpp = _block("late_payment_penalty")
    annual_rate_pct = float(lpp.get("annual_rate_pct", 14))

    # CD 129/2025 charges the 14% per annum rate monthly, "for each month or
    # part thereof", from the day following the due date. Any part month counts
    # as a whole month, so round the month count up. days_late == 0 is not late.
    months_charged = math.ceil(days_late / _DAYS_PER_MONTH) if days_late > 0 else 0
    monthly_rate_pct = annual_rate_pct / 12
    estimated_penalty_aed = round(tax_due_aed * (monthly_rate_pct / 100) * months_charged, 2)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "rule": {
                    "name": lpp.get("name"),
                    "annual_rate_pct": annual_rate_pct,
                    "monthly_rate_pct": round(monthly_rate_pct, 4),
                    "accrual": "monthly, for each month or part thereof",
                    "cap": "none",
                    "law": lpp.get("law"),
                    "effective_from": lpp.get("effective_from"),
                },
                "inputs": {
                    "tax_due_aed": tax_due_aed,
                    "days_late": days_late,
                },
                "months_charged": months_charged,
                "estimated_penalty_aed": estimated_penalty_aed,
                "note": (
                    "The 14% per annum rate accrues monthly, for each month or "
                    "part thereof, from the day after the due date, so one day "
                    "late already costs a full month. Month count is derived "
                    "from days_late using an average month length; for an exact "
                    "figure count calendar months from the due date. No cap "
                    "applies. Confirm with the FTA before paying."
                ),
                "source_urls": lpp.get("source_urls", []),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
