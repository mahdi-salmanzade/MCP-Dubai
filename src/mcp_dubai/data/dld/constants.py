"""Confirmed DLD dataset slugs on Dubai Pulse."""

from __future__ import annotations

from typing import Final

DLD_ORG: Final[str] = "dld"

DATASETS: Final[dict[str, str]] = {
    "transactions": "dld_transactions-open-api",
    "rent_contracts": "dld_rent_contracts-open-api",
    "brokers": "dld_brokers-open-api",
    "developers": "dld_developers-open-api",
    "projects": "dld_projects-open-api",
    "buildings": "dld_buildings-open-api",
    "land_registry": "dld_land_registry-open-api",
    "real_estate_permits": "dld_real_estate_permits-open-api",
    "real_estate_licenses": "dld_real_estate_licenses-open-api",
}
