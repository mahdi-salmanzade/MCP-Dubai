"""FastMCP server for arabic_writer."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.agents.arabic_writer import tools

mcp: FastMCP = FastMCP("arabic_writer")


@mcp.tool
async def list_honorifics() -> dict[str, object]:
    """
    List bilingual UAE honorifics for use in formal correspondence.

    Includes His Highness, His/Her Excellency, Mr./Ms., Dr., Engineer
    with Arabic equivalents and use case notes.
    """
    return await tools.list_honorifics()


@mcp.tool
async def addressee_block(
    name: str,
    name_ar: str | None = None,
    honorific: str = "mr",
    title: str | None = None,
    title_ar: str | None = None,
    organization: str | None = None,
    organization_ar: str | None = None,
) -> dict[str, object]:
    """
    Build a bilingual addressee block for a UAE business letter.

    Args:
        name: Recipient name (English).
        name_ar: Recipient name in Arabic.
        honorific: Honorific id (use list_honorifics for the catalogue).
        title: Job title in English.
        title_ar: Job title in Arabic.
        organization: Organization name in English.
        organization_ar: Organization name in Arabic.
    """
    return await tools.addressee_block(
        name=name,
        name_ar=name_ar,
        honorific=honorific,
        title=title,
        title_ar=title_ar,
        organization=organization,
        organization_ar=organization_ar,
    )


@mcp.tool
async def business_letter_template(
    addressee_name: str,
    subject: str,
    subject_ar: str | None = None,
    honorific: str = "mr",
    opening: str = "formal",
    closing: str = "standard",
    sender_name: str = "[Your Name]",
    sender_title: str = "[Your Title]",
    sender_org: str = "[Your Organization]",
) -> dict[str, object]:
    """
    Build a bilingual UAE business letter template (English + Arabic).

    Returns side-by-side English and Arabic blocks ready for the LLM to
    fill in body paragraphs. Uses standard UAE formal correspondence
    conventions.

    Args:
        addressee_name: Recipient name in English.
        subject: Letter subject in English.
        subject_ar: Letter subject in Arabic (optional).
        honorific: Honorific id (mr, ms, dr, his_excellency, etc.).
        opening: Opening style (formal, warm, respectful).
        closing: Closing style (standard, formal, warm).
        sender_name: Sender name placeholder.
        sender_title: Sender title placeholder.
        sender_org: Sender organization placeholder.
    """
    return await tools.business_letter_template(
        addressee_name=addressee_name,
        subject=subject,
        subject_ar=subject_ar,
        honorific=honorific,
        opening=opening,
        closing=closing,
        sender_name=sender_name,
        sender_title=sender_title,
        sender_org=sender_org,
    )


@mcp.tool
async def list_salutations() -> dict[str, object]:
    """List bilingual opening and closing salutations for UAE business letters."""
    return await tools.list_salutations()


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="list_honorifics",
        description="List bilingual UAE honorifics (His Highness, His Excellency, Mr., Dr., etc.).",
        feature="arabic_writer",
        tier=TIER_BIZ,
        tags=[
            "honorific",
            "title",
            "his excellency",
            "his highness",
            "arabic",
            "uae",
            "letter",
            "formal",
        ],
    ),
    ToolMeta(
        name="addressee_block",
        description="Build a bilingual addressee block for a UAE business letter.",
        feature="arabic_writer",
        tier=TIER_BIZ,
        tags=[
            "addressee",
            "letter",
            "bilingual",
            "english arabic",
            "formal",
            "uae",
            "correspondence",
        ],
    ),
    ToolMeta(
        name="business_letter_template",
        description=(
            "Build a bilingual UAE business letter template (English left, "
            "Arabic right) with standard openings, closings, and addressee block."
        ),
        feature="arabic_writer",
        tier=TIER_BIZ,
        tags=[
            "letter",
            "template",
            "bilingual",
            "arabic",
            "english",
            "business letter",
            "formal correspondence",
            "uae",
            "rtl",
        ],
    ),
    ToolMeta(
        name="list_salutations",
        description="List bilingual openings and closings for UAE business letters.",
        feature="arabic_writer",
        tier=TIER_BIZ,
        tags=["salutation", "opening", "closing", "letter", "arabic", "bilingual"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
