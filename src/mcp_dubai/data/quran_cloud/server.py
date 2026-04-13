"""FastMCP server for Quran Cloud."""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_dubai._shared.discovery import (
    TIER_OPEN,
    ToolMeta,
    get_tool_discovery,
)
from mcp_dubai.data.quran_cloud import tools

mcp: FastMCP = FastMCP("quran_cloud")


@mcp.tool
async def quran_surah(
    number: int,
    edition: str = "quran-uthmani",
) -> dict[str, object]:
    """
    Get a full surah by number (1 to 114) in a specific edition.

    Args:
        number: Surah number, 1 (Al-Fatiha) to 114 (An-Nas).
        edition: Edition slug. Default `quran-uthmani` (Arabic Uthmani).
            Common alternatives: `en.sahih` (Sahih International English),
            `en.pickthall`, `ur.jalandhry` (Urdu).

    Returns:
        Dict with surah metadata and the full ayah list.
    """
    return await tools.quran_surah(number=number, edition=edition)


@mcp.tool
async def quran_ayah(
    reference: str,
    edition: str = "quran-uthmani",
) -> dict[str, object]:
    """
    Get a single ayah by reference (e.g., "2:255" for Ayat al-Kursi).

    Args:
        reference: surah:ayah (e.g., "2:255") or absolute ayah number.
        edition: Edition slug. Default `quran-uthmani`.
    """
    return await tools.quran_ayah(reference=reference, edition=edition)


@mcp.tool
async def quran_juz(
    number: int,
    edition: str = "quran-uthmani",
) -> dict[str, object]:
    """
    Get a full juz (1 to 30) in a specific edition.

    Args:
        number: Juz number, 1 to 30.
        edition: Edition slug. Default `quran-uthmani`.
    """
    return await tools.quran_juz(number=number, edition=edition)


@mcp.tool
async def quran_search(
    query: str,
    surah: str = "all",
    edition: str = "en",
) -> dict[str, object]:
    """
    Search the Quran for a phrase.

    Args:
        query: Phrase to search for.
        surah: Surah number or "all".
        edition: Edition slug or language code (e.g., "en" or "ar").
    """
    return await tools.quran_search(query=query, surah=surah, edition=edition)


_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="quran_surah",
        description="Get a full surah of the Quran by number (1 to 114).",
        feature="quran_cloud",
        tier=TIER_OPEN,
        tags=[
            "quran",
            "surah",
            "chapter",
            "fatiha",
            "baqarah",
            "ikhlas",
            "an-nas",
            "arabic",
            "translation",
            "islamic",
        ],
    ),
    ToolMeta(
        name="quran_ayah",
        description="Get a single ayah of the Quran by reference, e.g., 2:255 for Ayat al-Kursi.",
        feature="quran_cloud",
        tier=TIER_OPEN,
        tags=[
            "quran",
            "ayah",
            "verse",
            "kursi",
            "ayatul",
            "translation",
            "arabic",
        ],
    ),
    ToolMeta(
        name="quran_juz",
        description="Get a full juz of the Quran (1 to 30, the daily reading sections).",
        feature="quran_cloud",
        tier=TIER_OPEN,
        tags=["quran", "juz", "para", "ramadan", "30", "section"],
    ),
    ToolMeta(
        name="quran_search",
        description="Search the Quran for a phrase across editions.",
        feature="quran_cloud",
        tier=TIER_OPEN,
        tags=["quran", "search", "find", "phrase", "verse", "translation"],
    ),
]

get_tool_discovery().register_many(_TOOLS)
