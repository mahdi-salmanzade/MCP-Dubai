"""
Generic Dubai Pulse dataset client.

All Dubai Pulse Tier 1 features (DLD, RTA, DHA, DEWA, etc.) inherit the
same auth flow and the same query parameters. This client encapsulates
both so feature implementations stay focused on dataset semantics.

Endpoint pattern (verified live April 2026, see knowledge brief 4.2):

    POST {DUBAI_PULSE_TOKEN_URL}?grant_type=client_credentials
    Form: client_id={KEY}&client_secret={SECRET}
    -> { "access_token": "...", "expires_in": 1800 }

    GET https://api.dubaipulse.gov.ae/{open|shared}/{org}/{dataset-slug}
    Header: Authorization: Bearer {token}
    Query: limit, offset, order_by, column, filter=col=val AND col2=val2
"""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.auth import get_dubai_pulse_auth
from mcp_dubai._shared.constants import DUBAI_PULSE_API_BASE
from mcp_dubai._shared.http_client import HttpClient


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
        self.org = org
        self.dataset = dataset
        self.auth = get_dubai_pulse_auth()
        self.base_url = DUBAI_PULSE_API_BASE

    @property
    def endpoint(self) -> str:
        """Full dataset URL."""
        access = "open" if "-open" in self.dataset else "shared"
        return f"{self.base_url}/{access}/{self.org}/{self.dataset}"

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
        headers = await self.auth.get_auth_header()

        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if order_by:
            params["order_by"] = order_by
        if columns:
            params["column"] = ",".join(columns)
        if filters:
            filter_parts = [f"{k}={v}" for k, v in filters.items()]
            params["filter"] = " AND ".join(filter_parts)

        async with HttpClient() as client:
            response = await client.get(self.endpoint, params=params, headers=headers)

        payload = response.json()
        return dict(payload) if isinstance(payload, dict) else {"data": payload}

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
        all_records: list[dict[str, Any]] = []
        offset = 0

        while len(all_records) < max_records:
            result = await self.query(
                limit=page_size,
                offset=offset,
                filters=filters,
            )
            records = result.get("data", [])
            if not isinstance(records, list) or not records:
                break

            all_records.extend(records)
            if len(records) < page_size:
                break

            offset += page_size

        return all_records[:max_records]
