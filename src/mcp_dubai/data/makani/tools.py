"""Makani tool functions (Dubai Municipality geo-addressing)."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure as mark_upstream_failure
from mcp_dubai._shared.health import mark_success as mark_upstream_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.makani.client import MakaniClient

_SOURCE = "www.makani.ae"
_UPSTREAM = "makani"
_VERIFY_AT = "https://www.makani.ae/"
_ATTRIBUTION = "Makani data by Dubai Municipality; attribution required, resale prohibited."


def _fail(error: str | dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _service_error(payload: dict[str, Any]) -> str | None:
    """Makani signals errors as `{"DATA": "Invalid latitude value!"}` bodies."""
    if "DATA" in payload:
        return str(payload.get("DATA") or "unknown error")
    return None


def _bilingual(payload: dict[str, Any], stem: str) -> dict[str, str]:
    """Read `<stem>_E` / `<stem>_A` fields into an {en, ar} pair."""
    return {
        "en": str(payload.get(f"{stem}_E") or "").strip(),
        "ar": str(payload.get(f"{stem}_A") or "").strip(),
    }


def _parse_latlng(raw: object) -> tuple[float | None, float | None]:
    """Split a `"25.26464,55.31217"` string into float coordinates."""
    parts = str(raw or "").split(",")
    if len(parts) != 2:
        return None, None
    try:
        latitude, longitude = float(parts[0]), float(parts[1])
    except ValueError:
        return None, None
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return None, None
    return latitude, longitude


# Arabic-Indic and Extended Arabic-Indic digits, transliterated to ASCII so
# that Arabic-script input (realistic for this service) validates correctly.
_EASTERN_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def _normalize_makani(makani_number: str) -> str | None:
    """
    Normalize a Makani number to the service's "NNNNN NNNNN" format.

    Accepts 10 digits with or without spaces or hyphens, in Western or
    Arabic-Indic numerals. Returns None when the input is not exactly
    10 digits.
    """
    digits = makani_number.replace(" ", "").replace("-", "").strip()
    digits = digits.translate(_EASTERN_DIGITS)
    if len(digits) != 10 or not (digits.isascii() and digits.isdigit()):
        return None
    return f"{digits[:5]} {digits[5:]}"


async def makani_reverse_geocode(latitude: float, longitude: float) -> dict[str, object]:
    """
    Find the Makani numbers and building at a coordinate (reverse geocode).

    Args:
        latitude: Latitude in decimal degrees (WGS84), e.g. 25.26464.
        longitude: Longitude in decimal degrees (WGS84), e.g. 55.31217.

    Returns:
        Dict with `building`, `community`, and `emirate` (each {en, ar}),
        plus `makani_numbers`: a list of entries carrying `makani`,
        `latitude`, `longitude`, and `short_url`.
    """
    if not -90 <= latitude <= 90:
        return _fail(f"latitude must be between -90 and 90, got {latitude}")
    if not -180 <= longitude <= 180:
        return _fail(f"longitude must be between -180 and 180, got {longitude}")

    client = MakaniClient()
    try:
        payload = await client.get_makani_info_from_coord(latitude, longitude)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    error = _service_error(payload)
    if error is not None:
        # The round-trip succeeded; a DATA error usually means the input is
        # outside Makani coverage, not that the upstream is unhealthy.
        mark_upstream_success(_UPSTREAM)
        return _fail(
            f"Makani service error for ({latitude}, {longitude}): {error} "
            "The service covers Dubai and participating UAE emirates only."
        )

    mark_upstream_success(_UPSTREAM)
    raw_info = payload.get("MAKANI_INFO")
    entries = raw_info if isinstance(raw_info, list) else []
    makani_numbers: list[dict[str, object]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        lat, lng = _parse_latlng(entry.get("LATLNG"))
        makani_numbers.append(
            {
                "makani": str(entry.get("MAKANI") or ""),
                "latitude": lat,
                "longitude": lng,
                "short_url": str(entry.get("SHORT_URL") or ""),
            }
        )
    return _ok(
        {
            "building": _bilingual(payload, "BLDG_NAME"),
            "community": _bilingual(payload, "COMMUNITY"),
            "emirate": _bilingual(payload, "EMIRATE"),
            "makani_numbers": makani_numbers,
            "attribution": _ATTRIBUTION,
        }
    )


async def makani_details(makani_number: str) -> dict[str, object]:
    """
    Look up the building behind a 10-digit Makani number.

    Args:
        makani_number: Makani number, 10 digits with or without a space,
            e.g. "30032 95320" or "3003295320".

    Returns:
        Dict with `makani` (normalized), `building`, `community`, and
        `emirate` (each {en, ar}), `latitude`, `longitude`, and `short_url`.
    """
    formatted = _normalize_makani(makani_number)
    if formatted is None:
        return _fail(
            f"Invalid Makani number {makani_number!r}: expected 10 digits, e.g. '30032 95320'."
        )

    client = MakaniClient()
    try:
        payload = await client.get_makani_details(formatted)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    error = _service_error(payload)
    if error is not None:
        # Round-trip succeeded; DATA errors are input problems, not outages.
        mark_upstream_success(_UPSTREAM)
        return _fail(f"Makani service error for {formatted}: {error}")

    mark_upstream_success(_UPSTREAM)
    raw_info = payload.get("MAKANI_INFO")
    entries = [e for e in raw_info if isinstance(e, dict)] if isinstance(raw_info, list) else []
    if not entries:
        return _fail(f"No details found for Makani number {formatted}; it may not exist.")

    entry = entries[0]
    lat, lng = _parse_latlng(entry.get("LATLNG"))
    return _ok(
        {
            "makani": str(payload.get("MAKANI") or formatted),
            "building": _bilingual(entry, "BLDG_NAME"),
            "community": _bilingual(entry, "COMMUNITY"),
            "emirate": _bilingual(entry, "EMIRATE"),
            "latitude": lat,
            "longitude": lng,
            "short_url": str(entry.get("SHORT_URL") or ""),
            "attribution": _ATTRIBUTION,
        }
    )


async def makani_validate(makani_number: str) -> dict[str, object]:
    """
    Check whether a 10-digit Makani number exists.

    Args:
        makani_number: Makani number, 10 digits with or without a space,
            e.g. "30032 95320" or "3003295320".

    Returns:
        Dict with `makani` (normalized), `is_valid` (bool), and `emirate`
        ({en, ar} when valid, None otherwise).
    """
    formatted = _normalize_makani(makani_number)
    if formatted is None:
        return _fail(
            f"Invalid Makani number {makani_number!r}: expected 10 digits, e.g. '30032 95320'."
        )

    client = MakaniClient()
    try:
        payload = await client.is_valid_makani(formatted)
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    error = _service_error(payload)
    if error is not None:
        # Round-trip succeeded; DATA errors are input problems, not outages.
        mark_upstream_success(_UPSTREAM)
        return _fail(f"Makani service error for {formatted}: {error}")

    mark_upstream_success(_UPSTREAM)
    is_valid = str(payload.get("IS_VALID") or "").strip().lower() == "true"
    raw_valid = payload.get("VALID")
    emirate: dict[str, str] | None = None
    if is_valid and isinstance(raw_valid, list) and raw_valid and isinstance(raw_valid[0], dict):
        emirate = _bilingual(raw_valid[0], "EMIRATE")
    return _ok(
        {
            "makani": str(payload.get("MAKANI") or formatted),
            "is_valid": is_valid,
            "emirate": emirate,
            "attribution": _ATTRIBUTION,
        }
    )
