"""founder_essentials tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("founder_essentials.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("founder_essentials", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


def _list_block(name: str) -> list[dict[str, Any]]:
    item = _DATA.get(name, [])
    return list(item) if isinstance(item, list) else []


VALID_DOCUMENT_TYPES = {
    "personal",
    "commercial",
    "degree",
    "marriage",
    "birth",
    "power_of_attorney",
}


async def attestation_guide(
    document_type: str = "personal",
    home_country: str | None = None,
) -> dict[str, object]:
    """
    Walk through the UAE attestation chain for a foreign document.

    The UAE is NOT a Hague Apostille member as of April 2026. Foreign
    documents still require the full 5-step legalization chain.
    """
    if document_type not in VALID_DOCUMENT_TYPES:
        return (
            ToolResponse[dict[str, object]]
            .fail(
                error=(
                    f"document_type must be one of {sorted(VALID_DOCUMENT_TYPES)}, "
                    f"got {document_type!r}"
                )
            )
            .model_dump()
        )

    attestation = _block("attestation")
    chain = attestation.get("legalization_chain", [])
    fees = attestation.get("fees", {})

    is_commercial = document_type == "commercial"
    fee_aed = (
        fees.get("commercial_document_aed") if is_commercial else fees.get("personal_document_aed")
    )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "uae_apostille_member": attestation.get("uae_apostille_member", False),
                "apostille_correction_note": attestation.get("apostille_correction_note", ""),
                "document_type": document_type,
                "home_country": home_country,
                "is_commercial": is_commercial,
                "legalization_chain": chain,
                "estimated_mofa_fee_aed": fee_aed,
                "timeline_weeks_min": attestation.get("timeline_weeks_min"),
                "timeline_weeks_max": attestation.get("timeline_weeks_max"),
                "portals": attestation.get("portals", []),
                "tip": (
                    "Start the chain in the home country before flying. "
                    "MOFAIC accepts walk-in or online submission once the "
                    "document has been through the home country chain and the "
                    "UAE embassy."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def pro_services_estimate(
    visas_per_year: int = 2,
    license_renewals_per_year: int = 1,
    use_retainer: bool = False,
) -> dict[str, object]:
    """Estimate annual PRO service cost based on the curated price ranges."""
    if visas_per_year < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"visas_per_year must be >= 0, got {visas_per_year}")
            .model_dump()
        )
    if license_renewals_per_year < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"license_renewals_per_year must be >= 0, got {license_renewals_per_year}")
            .model_dump()
        )

    pro = _block("pro_services")

    per_min = int(pro.get("per_transaction_aed_min", 200))
    per_max = int(pro.get("per_transaction_aed_max", 4000))
    retainer_min = int(pro.get("monthly_retainer_aed_min", 1500))
    retainer_max = int(pro.get("monthly_retainer_aed_max", 8000))

    # Visa work is more expensive per-transaction than license renewal.
    visa_cost_min = visas_per_year * per_min * 4
    visa_cost_max = visas_per_year * per_max
    license_cost_min = license_renewals_per_year * per_min
    license_cost_max = license_renewals_per_year * per_max

    per_tx_total_min = visa_cost_min + license_cost_min
    per_tx_total_max = visa_cost_max + license_cost_max

    retainer_total_min = retainer_min * 12
    retainer_total_max = retainer_max * 12

    if use_retainer or visas_per_year >= 4:
        recommendation = "monthly_retainer"
        cost_min = retainer_total_min
        cost_max = retainer_total_max
    else:
        recommendation = "per_transaction"
        cost_min = per_tx_total_min
        cost_max = per_tx_total_max

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "recommendation": recommendation,
                "annual_cost_aed": {"min": cost_min, "max": cost_max},
                "per_transaction_estimate_aed": {
                    "min": per_tx_total_min,
                    "max": per_tx_total_max,
                },
                "monthly_retainer_estimate_aed": {
                    "min": retainer_total_min,
                    "max": retainer_total_max,
                },
                "what_a_pro_does": pro.get("what_a_pro_does", []),
                "inputs": {
                    "visas_per_year": visas_per_year,
                    "license_renewals_per_year": license_renewals_per_year,
                    "use_retainer": use_retainer,
                },
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def legal_translation_estimate(
    pages: int,
    same_day: bool = False,
) -> dict[str, object]:
    """Estimate legal translation cost based on page count and urgency."""
    if pages < 1:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"pages must be >= 1, got {pages}")
            .model_dump()
        )

    lt = _block("legal_translation")
    page_min = int(lt.get("price_per_page_aed_min", 50))
    page_max = int(lt.get("price_per_page_aed_max", 150))

    cost_min = pages * page_min
    cost_max = pages * page_max

    if same_day:
        uplift_min = float(lt.get("same_day_uplift_pct_min", 25)) / 100
        uplift_max = float(lt.get("same_day_uplift_pct_max", 50)) / 100
        cost_min = int(cost_min * (1 + uplift_min))
        cost_max = int(cost_max * (1 + uplift_max))

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "pages": pages,
                "same_day": same_day,
                "estimated_cost_aed": {"min": cost_min, "max": cost_max},
                "registry": lt.get("registry"),
                "registry_url": lt.get("registry_url"),
                "important": (
                    "Only MOJ-licensed sworn translators are accepted by UAE "
                    "courts, MOFA, RERA, and government counters. Always confirm "
                    "the translator is on the MOJ registry before commissioning."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def chamber_of_commerce_info() -> dict[str, object]:
    """Return Dubai Chamber of Commerce membership and CoO details."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            _block("chamber_of_commerce"),
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def setup_timeline_estimate() -> dict[str, object]:
    """Return realistic end-to-end timelines for a Dubai setup."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            _block("timelines"),
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def common_founder_mistakes(category: str | None = None) -> dict[str, object]:
    """List the 11 most common founder mistakes."""
    mistakes = _list_block("common_mistakes")
    if category:
        needle = category.lower()
        mistakes = [
            m
            for m in mistakes
            if needle in str(m.get("title", "")).lower() or needle in str(m.get("id", "")).lower()
        ]
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {"count": len(mistakes), "mistakes": mistakes},
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
