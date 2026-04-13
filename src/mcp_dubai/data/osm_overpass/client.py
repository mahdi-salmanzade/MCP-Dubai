"""Overpass QL client."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.osm_overpass import constants


class OverpassClient:
    """Async client that POSTs Overpass QL to the public endpoint."""

    @staticmethod
    def build_query(
        tag_selectors: list[str],
        latitude: float,
        longitude: float,
        radius_meters: int,
    ) -> str:
        """
        Build a minimal Overpass QL query for nodes matching tag selectors
        within a circle around (lat, lon).

        Multiple selectors are AND-ed (all must match a single node).
        """
        chained = "".join(f"[{sel}]" for sel in tag_selectors)
        return (
            "[out:json][timeout:25];"
            f"node{chained}(around:{radius_meters},{latitude},{longitude});"
            "out body 100;"
        )

    async def search_nodes(
        self,
        tag_selectors: list[str],
        latitude: float,
        longitude: float,
        radius_meters: int = constants.DEFAULT_RADIUS_METERS,
    ) -> list[dict[str, Any]]:
        """Run an Overpass query and return the elements list."""
        query = self.build_query(
            tag_selectors=tag_selectors,
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
        )
        async with HttpClient() as client:
            response = await client.post(
                constants.OVERPASS_ENDPOINT,
                data={"data": query},
            )
        payload = response.json()
        elements = payload.get("elements", [])
        if isinstance(elements, list):
            return [dict(item) for item in elements if isinstance(item, dict)]
        return []
