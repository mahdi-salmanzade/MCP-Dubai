"""
Central Bank of UAE: exchange rates and base rate.

The CBUAE has no documented JSON API. Their public pages call internal
Umbraco "Surface" controllers that return HTML fragments. We parse those
fragments with lxml.

Tier: 0 (no auth)
Source: Internal Umbraco endpoints on centralbank.ae.

These endpoints have been verified live as of April 2026 but they are
undocumented and could break without notice. The fallback is to scrape the
HTML pages at centralbank.ae directly.
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "cbuae",
    "description": (
        "Central Bank of UAE exchange rates (~75 currencies) and base rate. "
        "Sourced from undocumented Umbraco endpoints, no auth."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://www.centralbank.ae/en/forex-eibor/exchange-rates/",
}
