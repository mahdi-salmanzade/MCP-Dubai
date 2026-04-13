"""
FCSC Open Data: UAE federal open data portal (CKAN).

The Federal Competitiveness and Statistics Centre runs a standard CKAN 2.9
deployment at opendata.fcsc.gov.ae. Anonymous read access works for the
standard `/api/3/action/*` endpoints. This is the lowest-friction federal
data path and is the recommended channel for FCA (Federal Customs Authority)
trade statistics.

Tier: 0 (no auth)
Source: https://opendata.fcsc.gov.ae
Brief sections: 4.4, 5.10
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "fcsc_ckan",
    "description": (
        "UAE federal open data via the FCSC CKAN portal. Anonymous, no auth. "
        "Best path for federal customs trade statistics (FCA)."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://opendata.fcsc.gov.ae",
}
