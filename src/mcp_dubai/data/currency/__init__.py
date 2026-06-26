"""Everyday currency converter on an AED base (keyless, no signup).

A lightweight companion to the official `cbuae` exchange-rate tools. This
feature uses the ExchangeRate-API open endpoint (open.er-api.com), which
needs no API key, to answer plain "convert X to Y" questions. For official
central-bank reference rates, use the `cbuae` tools instead.

Tier: 0 (no auth)
Source: https://www.exchangerate-api.com/docs/free
"""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "currency",
    "description": (
        "Everyday currency conversion on an AED base via the ExchangeRate-API "
        "open endpoint (open.er-api.com). Keyless. The convenient companion to "
        "the official cbuae central-bank rates."
    ),
    "tier": 0,
    "requires_auth": False,
    "source_url": "https://www.exchangerate-api.com/docs/free",
}
