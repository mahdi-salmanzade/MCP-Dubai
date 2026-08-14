"""
Generic Dubai Pulse dataset client.

All Dubai Pulse Tier 1 features (DLD, RTA, DHA, DEWA, etc.) inherit the
same auth flow and the same query parameters. This client encapsulates
both so feature implementations stay focused on dataset semantics.

Migration note (verified 2026-07-02): the Dubai Pulse portal
(www.dubaipulse.gov.ae) was decommissioned between Dec 2025 and Jan 2026
and now redirects to https://data.dubai. The canonical API host and project
default is apis.data.dubai; the legacy api.dubaipulse.gov.ae host still
resolves. Set MCP_DUBAI_PULSE_API_BASE only when an alternate gateway is
required.

Endpoint pattern (verified live April 2026, see knowledge brief 4.2):

    POST {DUBAI_PULSE_TOKEN_URL}?grant_type=client_credentials
    Form: client_id={KEY}&client_secret={SECRET}
    -> { "access_token": "...", "expires_in": 1800 }

    GET {base}/{open|shared}/{org}/{dataset-slug}
    Header: Authorization: Bearer {token}
    Query: limit, offset, order_by, column, filter=col=val AND col2=val2
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

from mcp_dubai._shared.auth import get_dubai_pulse_auth
from mcp_dubai._shared.constants import DUBAI_PULSE_API_BASE
from mcp_dubai._shared.http_client import HttpClient

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
_ORDER_BY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}(?:\s+(?:ASC|DESC))?$", re.I)
_PATH_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_FILTER_META_RE = re.compile(r"[=;<>!()\\\"'\r\n*]")
_FILTER_CONNECTOR_RE = re.compile(r"\b(?:AND|OR|NOT|LIKE|IN)\b")
_MAX_FILTERS = 20
_MAX_FILTER_VALUE_LENGTH = 256


class DubaiPulseValidationError(ValueError):
    """Raised for a caller-supplied query value rejected before network I/O."""


class DubaiPulseResponseError(ValueError):
    """Raised when the gateway returns malformed or non-progressing data."""


class DubaiPulseClient:
    """
    Generic client for any Dubai Pulse dataset.

    Args:
        org: Publishing organization slug (e.g., "dld", "rta", "dha").
        dataset: Dataset slug. Use the `*-open-api` variant for REST JSON
            and `*-open` for bulk CSV. The client picks the right path
            (`/open/...` or `/shared/...`) based on the dataset name.
    """

    def __init__(self, org: str, dataset: str) -> None:
        if _PATH_SLUG_RE.fullmatch(org) is None:
            raise DubaiPulseValidationError(f"org must be a simple path slug, got {org!r}")
        if _PATH_SLUG_RE.fullmatch(dataset) is None:
            raise DubaiPulseValidationError(f"dataset must be a simple path slug, got {dataset!r}")
        self.org = org
        self.dataset = dataset
        self.auth = get_dubai_pulse_auth()
        self.base_url = DUBAI_PULSE_API_BASE

    @property
    def endpoint(self) -> str:
        """Full dataset URL."""
        access = "open" if "-open" in self.dataset else "shared"
        return f"{self.base_url}/{access}/{self.org}/{self.dataset}"

    @staticmethod
    def _validate_identifier(value: str, field: str) -> str:
        if _IDENTIFIER_RE.fullmatch(value) is None:
            raise DubaiPulseValidationError(
                f"{field} must be a simple dataset column name, got {value!r}"
            )
        return value

    @staticmethod
    def _serialize_filter_value(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            if not math.isfinite(value):
                raise DubaiPulseValidationError("filter values must be finite")
            return str(value)
        if not isinstance(value, str):
            raise DubaiPulseValidationError("filter values must be strings, numbers, or booleans")
        if len(value) > _MAX_FILTER_VALUE_LENGTH:
            raise DubaiPulseValidationError(
                f"filter string values must be at most {_MAX_FILTER_VALUE_LENGTH} characters"
            )
        if (
            _FILTER_META_RE.search(value) is not None
            or _FILTER_CONNECTOR_RE.search(value) is not None
        ):
            raise DubaiPulseValidationError(
                "filter string contains reserved query syntax or a control character"
            )
        return value

    async def query(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
        columns: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Query the dataset.

        Args:
            limit: Max records per page (default 100).
            offset: Pagination offset.
            order_by: Column to sort by.
            filters: Dict of {column: value} filters joined with AND.
            columns: Optional column projection.

        Returns:
            Raw JSON response from the gateway, typically:
            `{"data": [...], "total": N, "offset": N, "limit": N}`.

        Raises:
            DubaiPulseCredentialsMissingError: If credentials are not set.
                Tools should call `auth.availability()` before this.
            DubaiPulseAuthError: If the token endpoint returns an error.
            HttpClientError: If the dataset endpoint returns >= 400.
        """
        if not 1 <= limit <= 500:
            raise DubaiPulseValidationError(f"limit must be 1 to 500, got {limit}")
        if offset < 0:
            raise DubaiPulseValidationError(f"offset must be at least 0, got {offset}")
        if order_by and _ORDER_BY_RE.fullmatch(order_by) is None:
            raise DubaiPulseValidationError(
                f"order_by has an invalid column or direction: {order_by!r}"
            )
        if columns:
            if len(columns) > 50:
                raise DubaiPulseValidationError("columns must contain at most 50 entries")
            for column in columns:
                self._validate_identifier(column, "column")
        if filters and len(filters) > _MAX_FILTERS:
            raise DubaiPulseValidationError(f"filters must contain at most {_MAX_FILTERS} entries")

        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if order_by:
            params["order_by"] = order_by
        if columns:
            params["column"] = ",".join(columns)
        if filters:
            filter_parts = [
                f"{self._validate_identifier(key, 'filter key')}="
                f"{self._serialize_filter_value(value)}"
                for key, value in filters.items()
            ]
            params["filter"] = " AND ".join(filter_parts)

        headers = await self.auth.get_auth_header()
        async with HttpClient() as client:
            response = await client.get(self.endpoint, params=params, headers=headers)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DubaiPulseResponseError(
                "data.dubai returned a response that was not valid JSON"
            ) from exc
        if not isinstance(payload, dict):
            raise DubaiPulseResponseError("data.dubai returned a non-object JSON response")
        return dict(payload)

    async def get_all(
        self,
        filters: dict[str, Any] | None = None,
        max_records: int = 10000,
        page_size: int = 500,
    ) -> list[dict[str, Any]]:
        """
        Fetch all records with automatic pagination.

        Args:
            filters: Optional column filters.
            max_records: Safety cap to prevent runaway loops.
            page_size: Records per request.

        Returns:
            Flat list of records.
        """
        if not 1 <= max_records <= 10000:
            raise DubaiPulseValidationError(f"max_records must be 1 to 10000, got {max_records}")
        if not 1 <= page_size <= 500:
            raise DubaiPulseValidationError(f"page_size must be 1 to 500, got {page_size}")

        all_records: list[dict[str, Any]] = []
        offset = 0
        page_fingerprints: set[str] = set()

        while len(all_records) < max_records:
            result = await self.query(
                limit=page_size,
                offset=offset,
                filters=filters,
            )
            records = result.get("data", [])
            if not isinstance(records, list):
                raise DubaiPulseResponseError("data.dubai response field 'data' must be a list")
            if not records:
                break

            typed_records = [record for record in records if isinstance(record, dict)]
            if len(typed_records) != len(records):
                raise DubaiPulseResponseError("data.dubai response records must be objects")

            page_bytes = json.dumps(
                typed_records,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode()
            page_fingerprint = hashlib.sha256(page_bytes).hexdigest()
            if page_fingerprint in page_fingerprints:
                raise DubaiPulseResponseError(
                    "data.dubai repeated a page while paginating; offset may be ignored"
                )
            page_fingerprints.add(page_fingerprint)

            all_records.extend(typed_records)
            if len(records) < page_size:
                break

            offset += len(records)
            total = result.get("total")
            if isinstance(total, int) and offset >= total:
                break

        return all_records[:max_records]
