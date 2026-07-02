"""api2.dfm.ae endpoint paths for the keyless DFM market-data feature.

The base URL lives in the shared constants module (`DFM_API_BASE`) because
the upstream health registry references the same host. These are the
undocumented JSON endpoints the marketwatch.dfm.ae site itself calls; both
accept anonymous GET requests and IGNORE query parameters, so every filter
in this feature is applied client-side.

    GET /mw/v1/indices  -> intraday DFM General Index records, newest first:
        {"id": "2026-07-02T15:00:00", "change": -19.48,
         "changepercentage": -0.324, "value": 5990.59, "volume": 120701866}

    GET /mw/v1/stocks   -> ~450 listed securities, ~47 fields each
        (id is the ticker symbol; `name` is null upstream as of 2026-07-02).
"""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import DFM_API_BASE

INDICES_URL: Final[str] = f"{DFM_API_BASE}/mw/v1/indices"
STOCKS_URL: Final[str] = f"{DFM_API_BASE}/mw/v1/stocks"
