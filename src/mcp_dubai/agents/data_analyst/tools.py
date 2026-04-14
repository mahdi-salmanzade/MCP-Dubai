"""
data_analyst tool functions.

These tools COMPOSE other MCP-Dubai tools rather than calling external
APIs. They produce structured plans and reports the LLM can execute or
present directly. Pure Python, no LLM calls inside the tools themselves.
"""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import (
    get_knowledge_registry,
    register_domain_knowledge,
)
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse

KNOWLEDGE: KnowledgeMetadata = KnowledgeMetadata(
    knowledge_date="2026-04-13",
    volatility="medium",
    verify_at="https://github.com/mahdi-salmanzade/MCP-Dubai",
    disclaimer=(
        "data_analyst tools produce execution plans and report templates "
        "from MCP-Dubai's curated knowledge. They do not call external "
        "APIs themselves. The freshness of any final answer depends on the "
        "freshness of the underlying tools called by the LLM."
    ),
)
register_domain_knowledge("data_analyst", KNOWLEDGE)


# ----------------------------------------------------------------------------
# Plan templates: known query categories mapped to the tools that should fire
# ----------------------------------------------------------------------------

PLAN_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "founder_setup": [
        {
            "tool": "setup_advisor",
            "purpose": "Recommend mainland vs free zone vs offshore",
            "args_template": {
                "activity": "<activity>",
                "budget_aed": "<budget_aed>",
                "industry": "<industry>",
            },
        },
        {
            "tool": "compare_free_zones",
            "purpose": "Shortlist 3 to 5 free zones matching the budget",
            "args_template": {
                "budget_aed": "<budget_aed>",
                "visa_count": "<visa_count>",
                "limit": 5,
            },
        },
        {
            "tool": "visa_recommend",
            "purpose": "Recommend the right visa for the founder profile",
            "args_template": {
                "profile": "founder",
                "has_uae_trade_license": True,
            },
        },
        {
            "tool": "bank_recommendation",
            "purpose": "Suggest 3 banks for the founder's industry",
            "args_template": {
                "industry": "<industry>",
                "limit": 3,
            },
        },
        {
            "tool": "corporate_tax_estimate",
            "purpose": "Estimate annual corporate tax exposure",
            "args_template": {
                "annual_taxable_income_aed": "<projected_revenue>",
                "is_free_zone": True,
                "industry": "<industry>",
            },
        },
        {
            "tool": "common_founder_mistakes",
            "purpose": "List the 11 most common mistakes",
            "args_template": {},
        },
    ],
    "market_research": [
        {
            "tool": "fcsc_search_dataset",
            "purpose": "Find UAE federal datasets matching the topic",
            "args_template": {"query": "<topic>"},
        },
        {
            "tool": "khda_search_school",
            "purpose": "If the topic touches education, search KHDA schools",
            "args_template": {"area": "<area>"},
        },
        {
            "tool": "cbuae_exchange_rates",
            "purpose": "Get current FX context for any cross-border numbers",
            "args_template": {},
        },
    ],
    "compliance_checkup": [
        {
            "tool": "esr_status",
            "purpose": "Confirm ESR is no longer required (DEAD post-2022)",
            "args_template": {},
        },
        {
            "tool": "aml_requirements",
            "purpose": "Check AML/CFT obligations for the business category",
            "args_template": {"business_category": "<category>"},
        },
        {
            "tool": "ubo_filing_guide",
            "purpose": "Confirm UBO register is in place",
            "args_template": {},
        },
        {
            "tool": "pdpl_compliance",
            "purpose": "Confirm PDPL data protection compliance",
            "args_template": {"jurisdiction": "uae_federal"},
        },
        {
            "tool": "vat_filing_calendar",
            "purpose": "Confirm VAT filing frequency",
            "args_template": {"annual_revenue_aed": "<revenue_aed>"},
        },
    ],
    "relocation": [
        {
            "tool": "visa_recommend",
            "purpose": "Recommend the right visa for the relocation profile",
            "args_template": {"profile": "<profile>"},
        },
        {
            "tool": "khda_search_school",
            "purpose": "Find suitable schools for the family",
            "args_template": {"curriculum": "<curriculum>"},
        },
        {
            "tool": "weather_uae_icao",
            "purpose": "Sanity-check the weather at the destination airport",
            "args_template": {"icao": "OMDB"},
        },
        {
            "tool": "uae_holidays",
            "purpose": "Show the calendar so the founder can plan around it",
            "args_template": {"year": 2026},
        },
        {
            "tool": "prayer_times_for",
            "purpose": "Show daily prayer times in the destination city",
            "args_template": {"city": "Dubai"},
        },
    ],
}


VALID_PLAN_CATEGORIES = set(PLAN_TEMPLATES.keys())


# ----------------------------------------------------------------------------
# Tools
# ----------------------------------------------------------------------------


async def plan_query(
    category: str,
    inputs: dict[str, object] | None = None,
) -> dict[str, object]:
    """
    Build a multi-tool execution plan for a query category.

    Args:
        category: One of: founder_setup, market_research, compliance_checkup,
            relocation.
        inputs: Optional dict of named inputs the LLM can substitute into
            the plan's args templates (e.g., {"budget_aed": 25000}).

    Returns:
        Structured plan: list of tool calls in order, each with a purpose
        and an args template the LLM can fill in.
    """
    if category not in VALID_PLAN_CATEGORIES:
        return (
            ToolResponse[dict[str, object]]
            .fail(
                error=(f"category must be one of {sorted(VALID_PLAN_CATEGORIES)}, got {category!r}")
            )
            .model_dump()
        )

    plan = PLAN_TEMPLATES[category]
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "category": category,
                "step_count": len(plan),
                "steps": plan,
                "inputs_provided": inputs or {},
                "execution_note": (
                    "Each step describes a tool to call and an args template. "
                    "Substitute the input values, then call recommend_tools "
                    "first if you are unsure which exact tool name matches, or "
                    "call the named tool directly if it is in the catalogue."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def list_plan_categories() -> dict[str, object]:
    """List the available plan categories."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(PLAN_TEMPLATES),
                "categories": [
                    {
                        "id": category,
                        "step_count": len(steps),
                        "first_step_tool": steps[0]["tool"] if steps else None,
                    }
                    for category, steps in PLAN_TEMPLATES.items()
                ],
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def synthesize_report(
    title: str,
    sections: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """
    Build a structured Markdown report skeleton from named sections.

    Args:
        title: Report title.
        sections: List of {heading, body} dicts. Each becomes an H2 section.

    Returns:
        A Markdown report string the LLM can present directly. Includes a
        knowledge block at the bottom with the project's knowledge_date and
        the freshness of every domain that contributed to the report.
    """
    if not title.strip():
        return ToolResponse[dict[str, object]].fail(error="title must not be empty").model_dump()

    sections = sections or []
    body_parts: list[str] = [f"# {title}", ""]
    for section in sections:
        if not isinstance(section, dict):
            continue
        heading = str(section.get("heading", "")).strip()
        body = str(section.get("body", "")).strip()
        if not heading:
            continue
        body_parts.append(f"## {heading}")
        body_parts.append("")
        if body:
            body_parts.append(body)
            body_parts.append("")

    # Append a freshness footer reading from the registry.
    registry = get_knowledge_registry()
    domains = registry.all()
    body_parts.append("---")
    body_parts.append("")
    body_parts.append("## Knowledge freshness")
    body_parts.append("")
    body_parts.append("This report draws on the following MCP-Dubai knowledge domains:")
    body_parts.append("")
    for name, meta in sorted(domains.items()):
        body_parts.append(
            f"- **{name}**: verified {meta.knowledge_date}, volatility {meta.volatility}"
        )
    body_parts.append("")
    body_parts.append("Always verify quoted figures with the official source before acting.")

    markdown = "\n".join(body_parts)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "markdown": markdown,
                "title": title,
                "section_count": len(sections),
                "domains_referenced": sorted(domains.keys()),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def analyze_setup_decision(
    activity: str,
    budget_aed: int,
    industry: str = "general",
) -> dict[str, object]:
    """
    Build a complete cross-tool analysis brief for a founder setup decision.

    This is a meta-tool that returns a STRUCTURED PLAN, not a final answer.
    The LLM should execute the plan steps and synthesize a final brief.
    """
    if budget_aed < 0:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"budget_aed must be >= 0, got {budget_aed}")
            .model_dump()
        )

    plan = [
        {
            "step": 1,
            "tool": "setup_advisor",
            "args": {
                "activity": activity,
                "budget_aed": budget_aed,
                "industry": industry,
                "needs_visa": True,
            },
            "purpose": "Get the headline jurisdiction recommendation",
        },
        {
            "step": 2,
            "tool": "compare_free_zones",
            "args": {
                "budget_aed": budget_aed,
                "visa_count": 1,
                "limit": 5,
            },
            "purpose": "Get a cost-ranked free zone shortlist",
        },
        {
            "step": 3,
            "tool": "qfzp_check",
            "args": {"industry": industry, "is_free_zone": True},
            "purpose": "Confirm whether QFZP 0% applies (SaaS does NOT qualify)",
        },
        {
            "step": 4,
            "tool": "bank_recommendation",
            "args": {"industry": industry, "limit": 3},
            "purpose": "Get 3 bank candidates for this industry",
        },
        {
            "step": 5,
            "tool": "common_founder_mistakes",
            "args": {},
            "purpose": "List the 11 mistakes to warn the founder about",
        },
        {
            "step": 6,
            "tool": "setup_timeline_estimate",
            "args": {},
            "purpose": "Show realistic 1 to 16 week banking timeline",
        },
    ]

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "plan": plan,
                "step_count": len(plan),
                "synthesis_instructions": (
                    "Execute steps 1 to 6 in order. Then call synthesize_report "
                    "with sections: 'Recommendation', 'Free Zone Shortlist', "
                    "'Tax Treatment', 'Banking', 'Mistakes to Avoid', and "
                    "'Timeline'. The final report should be ~600 words."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
