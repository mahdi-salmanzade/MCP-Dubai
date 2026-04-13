"""Quran Cloud tool functions."""

from __future__ import annotations

from mcp_dubai.data.quran_cloud import constants
from mcp_dubai.data.quran_cloud.client import QuranCloudClient


async def quran_surah(
    number: int,
    edition: str = constants.DEFAULT_ARABIC_EDITION,
) -> dict[str, object]:
    """
    Get a full surah by number (1 to 114) in a specific edition.

    Args:
        number: Surah number, 1 (Al-Fatiha) to 114 (An-Nas).
        edition: Edition slug. Defaults to `quran-uthmani` (Arabic). Use
            `en.sahih` for Sahih International English translation.

    Returns:
        Dict with surah metadata, ayah count, and the full ayah list.
    """
    if not constants.MIN_SURAH <= number <= constants.MAX_SURAH:
        raise ValueError(
            f"surah number must be {constants.MIN_SURAH} to {constants.MAX_SURAH}, got {number}"
        )
    client = QuranCloudClient()
    return await client.get_surah(number=number, edition=edition)


async def quran_ayah(
    reference: str,
    edition: str = constants.DEFAULT_ARABIC_EDITION,
) -> dict[str, object]:
    """
    Get a single ayah by reference.

    Args:
        reference: Either a surah:ayah pair (e.g., "2:255" for Ayat al-Kursi)
            or an absolute ayah number (e.g., "262").
        edition: Edition slug. Defaults to `quran-uthmani` (Arabic).

    Returns:
        Dict with the ayah text, surah info, juz, page, and audio URL if
        available.
    """
    if not reference:
        raise ValueError("reference must not be empty")
    client = QuranCloudClient()
    return await client.get_ayah(reference=reference, edition=edition)


async def quran_juz(
    number: int,
    edition: str = constants.DEFAULT_ARABIC_EDITION,
) -> dict[str, object]:
    """Get a full juz (1 to 30) in a specific edition."""
    if not constants.MIN_JUZ <= number <= constants.MAX_JUZ:
        raise ValueError(
            f"juz number must be {constants.MIN_JUZ} to {constants.MAX_JUZ}, got {number}"
        )
    client = QuranCloudClient()
    return await client.get_juz(number=number, edition=edition)


async def quran_search(
    query: str,
    surah: str = "all",
    edition: str = "en",
) -> dict[str, object]:
    """
    Search the Quran for a phrase.

    Args:
        query: The phrase to search for.
        surah: Surah number or "all".
        edition: Edition slug or language code (e.g., "en", "ar").
    """
    if not query:
        raise ValueError("query must not be empty")
    client = QuranCloudClient()
    return await client.search(query=query, surah_filter=surah, edition=edition)
