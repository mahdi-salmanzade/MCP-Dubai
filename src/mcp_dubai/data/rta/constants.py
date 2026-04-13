"""Confirmed RTA dataset slugs on Dubai Pulse."""

from __future__ import annotations

from typing import Final

RTA_ORG: Final[str] = "rta"

DATASETS: Final[dict[str, str]] = {
    "metro_stations": "rta_metro_stations-open-api",
    "bus_routes": "rta_bus_routes-open-api",
    "tram_stations": "rta_tram_stations-open-api",
    "taxi": "rta_taxi-open-api",
    "marine_transport": "rta_marine_transport-open-api",
    "salik_tariff": "rta_salik_tariff-open-api",
    "gtfs_static": "rta_gtfs-open",
}

GTFS_TRANSITLAND_MIRROR: Final[str] = "https://gtfs-source-feeds.transit.land/dubai-rta.zip"
