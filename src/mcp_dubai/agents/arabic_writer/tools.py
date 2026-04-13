"""
arabic_writer tool functions.

These are pure template helpers that generate bilingual UAE business
correspondence. The tools intentionally do NOT call an LLM. They produce
structured templates and bilingual building blocks that the calling LLM
can fill in. This keeps the agent deterministic and credential-free.
"""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse

KNOWLEDGE: KnowledgeMetadata = KnowledgeMetadata(
    knowledge_date="2026-04-13",
    volatility="stable",
    verify_at="https://u.ae",
    disclaimer=(
        "Templates use standard UAE business correspondence conventions. "
        "Verify any official titles or honorifics before sending to a "
        "specific recipient. Arabic spelling of personal and corporate "
        "names should be confirmed by a native speaker."
    ),
)
register_domain_knowledge("arabic_writer", KNOWLEDGE)


# ----------------------------------------------------------------------------
# Honorifics and salutations
# ----------------------------------------------------------------------------

HONORIFICS: Final[dict[str, dict[str, str]]] = {
    "his_highness": {
        "en": "His Highness",
        "ar": "صاحب السمو",
        "use_for": "Member of the ruling family of an emirate",
    },
    "his_excellency": {
        "en": "His Excellency",
        "ar": "سعادة",
        "use_for": "Minister, ambassador, federal director general",
    },
    "her_excellency": {
        "en": "Her Excellency",
        "ar": "سعادة",
        "use_for": "Female minister, ambassador, federal director general",
    },
    "mr": {
        "en": "Mr.",
        "ar": "السيد",
        "use_for": "Standard professional address (male)",
    },
    "ms": {
        "en": "Ms.",
        "ar": "السيدة",
        "use_for": "Standard professional address (female)",
    },
    "dr": {
        "en": "Dr.",
        "ar": "الدكتور",
        "use_for": "PhD or medical doctor (male)",
    },
    "dr_f": {
        "en": "Dr.",
        "ar": "الدكتورة",
        "use_for": "PhD or medical doctor (female)",
    },
    "engineer": {
        "en": "Engineer",
        "ar": "المهندس",
        "use_for": "Practicing engineer (male)",
    },
}

OPENINGS: Final[dict[str, dict[str, str]]] = {
    "formal": {
        "en": "Greetings,",
        "ar": "تحية طيبة وبعد،",
    },
    "warm": {
        "en": "Warm greetings,",
        "ar": "تحية طيبة وبعد،",
    },
    "respectful": {
        "en": "With my highest respect,",
        "ar": "أتقدم إليكم بأسمى آيات الاحترام والتقدير،",
    },
}

CLOSINGS: Final[dict[str, dict[str, str]]] = {
    "standard": {
        "en": "Sincerely,",
        "ar": "وتفضلوا بقبول فائق الاحترام والتقدير،",
    },
    "formal": {
        "en": "Yours faithfully,",
        "ar": "وتفضلوا بقبول فائق الاحترام،",
    },
    "warm": {
        "en": "Best regards,",
        "ar": "مع أطيب التحيات،",
    },
}


VALID_HONORIFICS = set(HONORIFICS.keys())
VALID_OPENINGS = set(OPENINGS.keys())
VALID_CLOSINGS = set(CLOSINGS.keys())


# ----------------------------------------------------------------------------
# Tools
# ----------------------------------------------------------------------------


async def list_honorifics() -> dict[str, object]:
    """List the bilingual UAE honorifics catalogue."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "count": len(HONORIFICS),
                "honorifics": [{"id": hid, **info} for hid, info in HONORIFICS.items()],
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


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
        name_ar: Recipient name in Arabic. If omitted, the English name
            is repeated as a placeholder for the LLM to translate.
        honorific: Honorific id (use list_honorifics for the catalogue).
        title: Job title in English.
        title_ar: Job title in Arabic.
        organization: Organization name in English.
        organization_ar: Organization name in Arabic.
    """
    if honorific not in VALID_HONORIFICS:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"honorific must be one of {sorted(VALID_HONORIFICS)}, got {honorific!r}")
            .model_dump()
        )
    if not name.strip():
        return ToolResponse[dict[str, object]].fail(error="name must not be empty").model_dump()

    h = HONORIFICS[honorific]
    name_ar_value = name_ar or f"[{name}]"

    en_lines = [f"{h['en']} {name}"]
    ar_lines = [f"{h['ar']}/ {name_ar_value}"]

    if title:
        en_lines.append(title)
    if title_ar:
        ar_lines.append(title_ar)

    if organization:
        en_lines.append(organization)
    if organization_ar:
        ar_lines.append(organization_ar)

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "english": "\n".join(en_lines),
                "arabic": "\n".join(ar_lines),
                "honorific": h,
                "rtl_note": (
                    "When rendering the Arabic block in a document, set "
                    "direction: rtl and align: right. Most word processors "
                    "auto-detect."
                ),
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


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
    Build a bilingual UAE business letter template (English left, Arabic right).

    The letter is a structured template with placeholders for the LLM to
    fill in (subject, body paragraphs). Returns both English and Arabic
    versions side by side.

    Args:
        addressee_name: Recipient name in English.
        subject: Letter subject in English.
        subject_ar: Letter subject in Arabic (optional).
        honorific: Honorific id.
        opening: Opening salutation id (formal, warm, respectful).
        closing: Closing salutation id (standard, formal, warm).
        sender_name: Sender name (default placeholder).
        sender_title: Sender title (default placeholder).
        sender_org: Sender organization (default placeholder).
    """
    if opening not in VALID_OPENINGS:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"opening must be one of {sorted(VALID_OPENINGS)}, got {opening!r}")
            .model_dump()
        )
    if closing not in VALID_CLOSINGS:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"closing must be one of {sorted(VALID_CLOSINGS)}, got {closing!r}")
            .model_dump()
        )
    if honorific not in VALID_HONORIFICS:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"honorific must be one of {sorted(VALID_HONORIFICS)}, got {honorific!r}")
            .model_dump()
        )

    h = HONORIFICS[honorific]
    o = OPENINGS[opening]
    c = CLOSINGS[closing]
    subject_ar_value = subject_ar or f"[{subject}]"

    english = (
        f"To: {h['en']} {addressee_name}\n\n"
        f"Subject: {subject}\n\n"
        f"{o['en']}\n\n"
        f"[Body paragraph 1]\n\n"
        f"[Body paragraph 2]\n\n"
        f"{c['en']}\n\n"
        f"{sender_name}\n"
        f"{sender_title}\n"
        f"{sender_org}\n"
    )

    arabic = (
        f"إلى: {h['ar']}/ [{addressee_name}]\n\n"
        f"الموضوع: {subject_ar_value}\n\n"
        f"{o['ar']}\n\n"
        f"[الفقرة الأولى من النص]\n\n"
        f"[الفقرة الثانية من النص]\n\n"
        f"{c['ar']}\n\n"
        f"[{sender_name}]\n"
        f"[{sender_title}]\n"
        f"[{sender_org}]\n"
    )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "english": english,
                "arabic": arabic,
                "rendering_tip": (
                    "For a side-by-side bilingual document, place the English "
                    "block in a left-to-right column and the Arabic block in a "
                    "right-to-left column. Most UAE government letters use this "
                    "format."
                ),
                "subject": {"en": subject, "ar": subject_ar_value},
                "addressee": {"en": addressee_name, "honorific": h},
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )


async def list_salutations() -> dict[str, object]:
    """List the bilingual openings and closings catalogue."""
    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "openings": [{"id": k, **v} for k, v in OPENINGS.items()],
                "closings": [{"id": k, **v} for k, v in CLOSINGS.items()],
            },
            knowledge=KNOWLEDGE,
        )
        .model_dump()
    )
