"""
setup_advisor decision tree.

Pure functions, no FastMCP imports. Exercises:
- Pattern 1: per-domain KNOWLEDGE constant + ToolResponse envelope
- Pattern 3: load curated JSON via the loader

The KNOWLEDGE constant is registered with the shared registry at module
import time so `get_knowledge_status()` reflects setup_advisor freshness.
"""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

# ----------------------------------------------------------------------------
# Per-domain knowledge constant.
# Sourced from free_zones.json's envelope so a single update flows through.
# ----------------------------------------------------------------------------
_FREE_ZONES_DATA = load_data_file("free_zones.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_FREE_ZONES_DATA)
# Override with a setup_advisor specific verify_at since this tool spans
# multiple domains.
KNOWLEDGE = KnowledgeMetadata(
    knowledge_date=KNOWLEDGE.knowledge_date,
    volatility="high",
    verify_at="https://invest.dubai.ae",
    disclaimer=(
        "This is a structured opinion built from the curated free zones, "
        "visas, banks, and tax rules captured in MCP-Dubai. Verify any "
        "specific number with the licensing authority before committing."
    ),
)
register_domain_knowledge("setup_advisor", KNOWLEDGE)


# ----------------------------------------------------------------------------
# Decision tree
# ----------------------------------------------------------------------------

VALID_INDUSTRIES = {
    "general",
    "saas",
    "tech",
    "ecommerce",
    "consulting",
    "fintech",
    "ai",
    "blockchain",
    "crypto",
    "trading",
    "import_export",
    "manufacturing",
    "logistics",
    "healthcare",
    "media",
    "education",
    "real_estate",
    "fb",
    "retail",
}


def _decide(
    activity: str,
    budget_aed: int,
    needs_local_trade: bool,
    needs_visa: bool,
    visa_count: int,
    industry: str,
    free_zones: list[dict[str, Any]],
) -> dict[str, Any]:
    """Pure decision logic. No I/O, easy to unit test."""
    reasoning: list[str] = []
    warnings: list[str] = []
    candidates: list[str] = []

    # Rule 1: Local trade requirement forces mainland.
    if needs_local_trade:
        jurisdiction = "mainland"
        reasoning.append(
            "Mainland (DET) is required to invoice mainland UAE B2C customers "
            "directly without a local distributor or dual license."
        )
        warnings.append(
            "Mainland setup typically requires Ejari (registered tenancy) "
            "before visa quota is granted. Budget for office cost on top of license."
        )
        cost_min = 12000
        cost_max = 30000
        timeline_weeks = "2 to 4"

    # Rule 2: No visa needed + low budget = offshore
    elif not needs_visa and budget_aed < 15000:
        jurisdiction = "offshore"
        reasoning.append(
            "Offshore (RAK ICC or JAFZA Offshore) is the cheapest path when "
            "no UAE visa is needed. Useful for asset holding, IP ownership, "
            "or international structuring."
        )
        warnings.append(
            "Offshore companies cannot get UAE visas, cannot trade with UAE "
            "customers, and cannot lease office space inside the UAE."
        )
        cost_min = 5500  # USD 1500 in AED-ish
        cost_max = 30000
        timeline_weeks = "1 to 3"

    # Rule 3: Tight budget steers to cheap free zones
    elif budget_aed < 20000:
        jurisdiction = "free_zone"
        reasoning.append(
            "A budget under AED 20,000 fits a cheap mainstream free zone like "
            "IFZA (from approximately AED 12,900) or Meydan (from approximately "
            "AED 12,500). Both offer zero-visa to multi-visa packages."
        )
        warnings.append(
            "Meydan has documented bank account difficulties (founder reports). "
            "Consider IFZA or Dubai South unless you have a specific reason for Meydan."
        )
        candidates = ["IFZA", "Meydan", "Dubai South"]
        cost_min = 12500
        cost_max = 20000
        timeline_weeks = "1 to 3"

    # Rule 4: Fintech / AI / regulated tech with budget - DIFC Innovation
    elif industry in {"fintech", "ai", "blockchain"} and budget_aed >= 25000:
        jurisdiction = "free_zone"
        reasoning.append(
            "DIFC Innovation Licence offers premium fintech/AI positioning "
            "with common-law jurisdiction. Subsidised at approximately USD "
            "1,500/yr for years 1 to 2, then approximately USD 12,000/yr standard."
        )
        warnings.append(
            "DIFC Innovation Licence excludes regulated financial services "
            "(needs DFSA), crypto exchanges, and physical goods trading. "
            "Maximum 4 visas on a flexi-desk; more requires private office. "
            "DIFC physical presence is mandatory."
        )
        candidates = ["DIFC Innovation Licence"]
        cost_min = 5500
        cost_max = 50000
        timeline_weeks = "2 to 4"

    # Rule 5: Crypto specifically → VARA territory
    elif industry == "crypto":
        jurisdiction = "free_zone"
        reasoning.append(
            "Crypto / virtual asset businesses operating in Dubai require a "
            "VARA (Virtual Assets Regulatory Authority) licence under Law 4 "
            "of 2022. Choose a free zone aligned with VARA expectations and "
            "expect heavy KYC."
        )
        warnings.append(
            "DIFC ADGM is regulated separately. None of the listed retail "
            "banks officially welcome crypto/VARA-licensed entities as of "
            "April 2026. Bank account opening will be the hardest step."
        )
        candidates = ["VARA-aware free zone (consult specialist)"]
        cost_min = 50000
        cost_max = 250000
        timeline_weeks = "8 to 24"

    # Rule 6: SaaS specifically - call out the QFZP exclusion
    elif industry == "saas":
        jurisdiction = "free_zone"
        reasoning.append(
            "SaaS works well in any general free zone (IFZA, Meydan, DSO/Dtec, "
            "TECOM, DMCC). Choose based on budget, visa needs, and whether you "
            "need premium positioning."
        )
        warnings.append(
            "CRITICAL TAX NOTE: SaaS is NOT a Qualifying Activity under MD "
            "229/2025. Most free zone SaaS revenue is taxed at 9% corporate "
            "tax (above the AED 375,000 threshold), not the 0% QFZP rate."
        )
        candidates = ["IFZA", "DSO Dtec", "TECOM (DIC)", "DMCC"]
        cost_min = 12500
        cost_max = 35000
        timeline_weeks = "1 to 3"

    # Default: free zone for most founders
    else:
        jurisdiction = "free_zone"
        reasoning.append(
            "A free zone is the right default for most founders. Best balance "
            "of cost, flexibility, visa quota, and 100% foreign ownership."
        )
        candidates = ["IFZA", "DAFZA", "DMCC", "DSO Dtec", "TECOM"]
        cost_min = 12500
        cost_max = 50000
        timeline_weeks = "1 to 3"

    # Cross-cutting warnings that always apply
    warnings.extend(
        [
            "Bank account opening takes 1 to 16 weeks. Apply to 2 or 3 banks "
            "in parallel. Wio Business is fastest (1 to 3 days) for clean profiles.",
            "Single-shareholder structures face more bank scrutiny. Adding a 2% "
            "to 10% co-shareholder softens the bank profile.",
            "Budget AED 5,000 to 15,000 on top of the license for PRO services, "
            "MOFA attestation, and legal translation.",
        ]
    )

    next_steps = [
        "Reserve a trade name via app.invest.dubai.ae or your chosen free zone portal",
        "Prepare passport copies, address proof, and a one-page business plan",
        "Get Ejari (mainland) or flexi-desk (free zone) before applying for visa quota",
        "Apply to 2 or 3 banks in parallel to hedge onboarding risk",
        "Register for UAE Pass on day one",
    ]

    return {
        "jurisdiction": jurisdiction,
        "candidate_free_zones": candidates,
        "reasoning": reasoning,
        "warnings": warnings,
        "estimated_setup_cost_aed": {"min": cost_min, "max": cost_max},
        "estimated_timeline_weeks": timeline_weeks,
        "next_steps": next_steps,
        "inputs": {
            "activity": activity,
            "budget_aed": budget_aed,
            "needs_local_trade": needs_local_trade,
            "needs_visa": needs_visa,
            "visa_count": visa_count,
            "industry": industry,
        },
    }


# ----------------------------------------------------------------------------
# Tool function
# ----------------------------------------------------------------------------


async def setup_advisor(
    activity: str,
    budget_aed: int,
    needs_local_trade: bool = False,
    needs_visa: bool = True,
    visa_count: int = 1,
    industry: str = "general",
) -> dict[str, object]:
    """
    Recommend the best jurisdiction (mainland, free zone, or offshore) for
    a Dubai business setup, grounded in curated knowledge.

    Returns a ToolResponse envelope with `data` (the recommendation) and
    `knowledge` (date, volatility, verify_at, disclaimer).
    """
    if budget_aed < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"budget_aed must be >= 0, got {budget_aed}")
            .model_dump()
        )
    if visa_count < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"visa_count must be >= 0, got {visa_count}")
            .model_dump()
        )
    if industry not in VALID_INDUSTRIES:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=(f"industry must be one of {sorted(VALID_INDUSTRIES)}, got {industry!r}"))
            .model_dump()
        )

    free_zones = _FREE_ZONES_DATA.get("free_zones", [])
    if not isinstance(free_zones, list):
        free_zones = []

    recommendation = _decide(
        activity=activity,
        budget_aed=budget_aed,
        needs_local_trade=needs_local_trade,
        needs_visa=needs_visa,
        visa_count=visa_count,
        industry=industry,
        free_zones=free_zones,
    )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            recommendation,
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
