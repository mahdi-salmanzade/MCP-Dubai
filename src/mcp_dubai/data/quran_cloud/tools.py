"""Quran Cloud tool functions."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure, mark_success
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.quran_cloud import constants
from mcp_dubai.data.quran_cloud.client import QuranCloudClient

_SOURCE = "api.alquran.cloud"
_UPSTREAM = "quran_cloud"
_VERIFY_AT = "https://alquran.cloud/api"


def _fail(error: str) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: object) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())  # type: ignore[arg-type]
        .model_dump()
    )


async def _run(coro: Awaitable[Any]) -> dict[str, object]:
    """Run an awaitable client call and wrap the result in the envelope."""
    try:
        result = await coro
    except RateLimitError:
        raise
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)
    mark_success(_UPSTREAM)
    return _ok(result)


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
    """
    if not constants.MIN_SURAH <= number <= constants.MAX_SURAH:
        return _fail(
            f"surah number must be {constants.MIN_SURAH} to {constants.MAX_SURAH}, got {number}"
        )
    client = QuranCloudClient()
    return await _run(client.get_surah(number=number, edition=edition))


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
    """
    if not reference:
        return _fail("reference must not be empty")
    client = QuranCloudClient()
    return await _run(client.get_ayah(reference=reference, edition=edition))


async def quran_juz(
    number: int,
    edition: str = constants.DEFAULT_ARABIC_EDITION,
) -> dict[str, object]:
    """Get a full juz (1 to 30) in a specific edition."""
    if not constants.MIN_JUZ <= number <= constants.MAX_JUZ:
        return _fail(f"juz number must be {constants.MIN_JUZ} to {constants.MAX_JUZ}, got {number}")
    client = QuranCloudClient()
    return await _run(client.get_juz(number=number, edition=edition))


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
        return _fail("query must not be empty")
    client = QuranCloudClient()
    return await _run(client.search(query=query, surah_filter=surah, edition=edition))
