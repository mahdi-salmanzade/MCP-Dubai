"""open.er-api.com endpoints for the keyless everyday currency converter.

The base URL is defined locally here on purpose: this feature does not
touch the shared constants module. The ExchangeRate-API open endpoint is
keyless and returns a JSON document of the form:

    {"result": "success", "base_code": "AED",
     "time_last_update_utc": "...", "rates": {"USD": 0.272, ...}}
"""

from __future__ import annotations

from typing import Final

CURRENCY_API_BASE: Final[str] = "https://open.er-api.com/v6"
