"""Overpass QL client."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.http_client import HttpClient, HttpClientError
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
        if response.status_code == 204 or not response.content:
            raise HttpClientError(f"Empty response from {constants.OVERPASS_ENDPOINT}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise HttpClientError(f"Non-JSON body from {constants.OVERPASS_ENDPOINT}") from exc
        if not isinstance(payload, dict):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.OVERPASS_ENDPOINT}: expected an object"
            )
        elements = payload.get("elements")
        if not isinstance(elements, list):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.OVERPASS_ENDPOINT}: elements is not a list"
            )
        if any(not isinstance(item, dict) for item in elements):
            raise HttpClientError(
                f"Invalid JSON shape from {constants.OVERPASS_ENDPOINT}: "
                "elements contains a non-object"
            )
        return [dict(item) for item in elements]
