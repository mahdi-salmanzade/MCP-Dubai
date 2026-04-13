"""
Dubai Pulse base client.

Shared base client for all Dubai Pulse Tier 1 features (DLD, RTA, DET,
DHA, DEWA, DTCM, DM, Dubai Airports, etc.). Implements the OAuth2
client_credentials flow and provides a generic dataset query method.

Tier: 1 (Dubai Pulse OAuth, free but credential-issued)
Source: https://api.dubaipulse.gov.ae

This is NOT a feature folder with its own FastMCP server. It is the
shared building block that DLD, RTA, etc. use to query the Dubai Pulse
gateway. Each Tier 1 feature instantiates a `DubaiPulseClient` with its
own org and dataset slug.
"""

from __future__ import annotations

from mcp_dubai.data.dubai_pulse.client import DubaiPulseClient

__all__ = ["DubaiPulseClient"]
