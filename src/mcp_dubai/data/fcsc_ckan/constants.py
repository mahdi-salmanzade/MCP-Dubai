"""FCSC CKAN endpoints."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import FCSC_CKAN_BASE

PACKAGE_SEARCH: Final[str] = f"{FCSC_CKAN_BASE}/package_search"
PACKAGE_SHOW: Final[str] = f"{FCSC_CKAN_BASE}/package_show"
ORGANIZATION_LIST: Final[str] = f"{FCSC_CKAN_BASE}/organization_list"
ORGANIZATION_SHOW: Final[str] = f"{FCSC_CKAN_BASE}/organization_show"
DATASTORE_SEARCH: Final[str] = f"{FCSC_CKAN_BASE}/datastore_search"

# Federal Customs Authority CKAN organization slug.
FCA_ORG_SLUG: Final[str] = "federal-customs-authority"
