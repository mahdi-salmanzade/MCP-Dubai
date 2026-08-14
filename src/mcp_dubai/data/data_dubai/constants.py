"""data.dubai catalog endpoints (Liferay Objects JSON API, anonymous).

The base URL lives in the shared constants module because the Dubai Pulse
to data.dubai migration is tracked project-wide. Endpoints verified
2026-08-14:

    GET {base}/datasets/?search=<q>&page=<n>&pageSize=<n>
    GET {base}/themes/
    GET {base}/issuingentities/

All three return Liferay page envelopes of the form
{"totalCount": ..., "page": ..., "pageSize": ..., "lastPage": ...,
 "items": [...]} and need no credentials.
"""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import DATA_DUBAI_CATALOG_BASE

DATASETS_ENDPOINT: Final[str] = f"{DATA_DUBAI_CATALOG_BASE}/datasets/"
THEMES_ENDPOINT: Final[str] = f"{DATA_DUBAI_CATALOG_BASE}/themes/"
ISSUING_ENTITIES_ENDPOINT: Final[str] = f"{DATA_DUBAI_CATALOG_BASE}/issuingentities/"

# Current catalog totals from the 2026-08-14 verification.
CATALOG_VERIFIED_DATE: Final[str] = "2026-08-14"
DATASET_COUNT: Final[int] = 614
THEME_COUNT: Final[int] = 11
ISSUING_ENTITY_COUNT: Final[int] = 76

# The current 76 entities and 11 themes fit in one generous page. The client
# still follows pagination so growth cannot silently truncate either list.
LIST_ALL_PAGE_SIZE: Final[int] = 100
# Guard against an upstream pagination loop or an unexpectedly huge response.
MAX_LIST_PAGES: Final[int] = 100
