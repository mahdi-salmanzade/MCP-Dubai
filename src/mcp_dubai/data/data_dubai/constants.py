"""data.dubai catalog endpoints (Liferay Objects JSON API, anonymous).

The base URL lives in the shared constants module because the Dubai Pulse
to data.dubai migration is tracked project-wide. Endpoints verified
2026-07-02:

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

# The portal lists 76 issuing entities and 11 themes (2026-07-02), so a
# single request with a generous pageSize fetches every record at once.
LIST_ALL_PAGE_SIZE: Final[int] = 100
