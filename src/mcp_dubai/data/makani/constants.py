"""SOAP protocol constants for the Makani public data service.

The endpoint URL itself lives in the shared constants module
(`MAKANI_SOAP_ENDPOINT`); this module carries only the SOAP 1.1 protocol
details. The service is document/literal: element names are lowercase
xs:string fields in the tempuri namespace, and each call must set the
SOAPAction header to the operation URI. Verified live 2026-07-02.
"""

from __future__ import annotations

from typing import Final

MAKANI_SOAP_NAMESPACE: Final[str] = "http://tempuri.org/"
MAKANI_SOAP_ACTION_PREFIX: Final[str] = "http://tempuri.org/IMakaniPublic/"
# The service asks callers to identify themselves in a <remarks> field.
MAKANI_REMARKS: Final[str] = "mcp-dubai"
