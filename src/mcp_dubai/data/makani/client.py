"""Makani public SOAP client (Dubai Municipality geo-addressing).

The service speaks SOAP 1.1 document/literal over a single POST endpoint.
Each operation returns a SOAP envelope whose `<OperationName>Result`
element carries a JSON string, so this client parses the XML, extracts
the result text, and returns the decoded JSON dict. The shared HttpClient
is JSON-GET oriented and cannot post a raw XML body, so this client uses
httpx directly with the same timeout and User-Agent defaults, and raises
the same typed errors as the shared client.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any
from xml.sax.saxutils import escape

import httpx

from mcp_dubai._shared.constants import (
    HTTP_DEFAULT_TIMEOUT_SECONDS,
    HTTP_USER_AGENT,
    MAKANI_SOAP_ENDPOINT,
)
from mcp_dubai._shared.http_client import HttpClientError, RateLimitError
from mcp_dubai.data.makani import constants

_ENVELOPE_TEMPLATE = (
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
    "<s:Body>{body}</s:Body></s:Envelope>"
)


class MakaniClient:
    """Async client for the Makani public SOAP service."""

    async def get_makani_info_from_coord(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Reverse geocode: Makani numbers and building info at a coordinate."""
        return await self._call(
            "GetMakaniInfoFromCoord",
            {
                "latitude": str(latitude),
                "longitude": str(longitude),
                "remarks": constants.MAKANI_REMARKS,
            },
        )

    async def get_makani_details(self, makani_number: str) -> dict[str, Any]:
        """Building, community, emirate, and coordinates for a Makani number."""
        return await self._call(
            "GetMakaniDetails",
            {"makanino": makani_number, "remarks": constants.MAKANI_REMARKS},
        )

    async def is_valid_makani(self, makani_number: str) -> dict[str, Any]:
        """Whether a Makani number exists, plus its emirate when it does."""
        return await self._call(
            "IsValidMakani",
            {"makanino": makani_number, "remarks": constants.MAKANI_REMARKS},
        )

    async def _call(self, operation: str, fields: dict[str, str]) -> dict[str, Any]:
        """POST one SOAP operation and return its decoded JSON result."""
        headers = {
            "User-Agent": HTTP_USER_AGENT,
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{constants.MAKANI_SOAP_ACTION_PREFIX}{operation}"',
        }
        async with httpx.AsyncClient(timeout=HTTP_DEFAULT_TIMEOUT_SECONDS) as client:
            response = await client.post(
                MAKANI_SOAP_ENDPOINT,
                content=_build_envelope(operation, fields),
                headers=headers,
            )
        _raise_for_status(response)
        return _extract_result(operation, response.text)


def _build_envelope(operation: str, fields: dict[str, str]) -> str:
    """Build the SOAP 1.1 request envelope (lowercase field tags)."""
    parts = "".join(f"<{name}>{escape(value)}</{name}>" for name, value in fields.items())
    body = f'<{operation} xmlns="{constants.MAKANI_SOAP_NAMESPACE}">{parts}</{operation}>'
    return _ENVELOPE_TEMPLATE.format(body=body)


def _raise_for_status(response: httpx.Response) -> None:
    """Mirror the shared HttpClient error mapping for non-2xx responses."""
    if response.status_code == 429:
        raise RateLimitError(
            f"Rate limited by {response.url}: {response.text[:200]}",
            status_code=429,
        )
    if response.status_code >= 400:
        raise HttpClientError(
            f"HTTP {response.status_code} from {response.url}: {response.text[:200]}",
            status_code=response.status_code,
        )


def _extract_result(operation: str, xml_text: str) -> dict[str, Any]:
    """Pull the JSON string out of `<OperationName>Result` and decode it."""
    # stdlib ElementTree never fetches external entities, so this response is
    # not an XXE risk. It does expand INTERNAL entities, which is the "billion
    # laughs" quadratic-blowup vector. A legitimate Makani SOAP response carries
    # no DTD, so refusing any doctype closes that off without adding defusedxml.
    if "<!DOCTYPE" in xml_text[:2048].upper():
        raise HttpClientError(
            "Makani SOAP response declares a DTD, which a legitimate response "
            "never does. Refusing to parse it (entity-expansion guard)."
        )
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise HttpClientError(f"Malformed SOAP response from Makani: {exc}") from exc

    element = root.find(f".//{{{constants.MAKANI_SOAP_NAMESPACE}}}{operation}Result")
    if element is None or not element.text:
        raise HttpClientError(f"Makani SOAP response is missing the {operation}Result element")

    try:
        payload = json.loads(element.text)
    except json.JSONDecodeError as exc:
        raise HttpClientError(f"Non-JSON payload inside Makani {operation}Result: {exc}") from exc
    return dict(payload) if isinstance(payload, dict) else {}
