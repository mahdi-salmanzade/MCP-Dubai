"""
Dubai Pulse base client.

Shared base client for all Dubai Pulse Tier 1 features (DLD, RTA, DET,
DHA, DEWA, DTCM, DM, Dubai Airports, etc.). Implements the OAuth2
client_credentials flow and provides a generic dataset query method.

Tier: 1 (OAuth, free but credential-issued)
Source: https://api.dubaipulse.gov.ae (legacy host, still resolves)

Migration note (verified 2026-07-02): the Dubai Pulse web portal
(www.dubaipulse.gov.ae) was decommissioned between Dec 2025 and Jan 2026
and now redirects to https://data.dubai. The canonical API host going
forward is apis.data.dubai, with the same
/open/{entity}/{dataset}-open-api pattern and the same OAuth credential
requirement; the legacy api.dubaipulse.gov.ae host still resolves and is
kept as the default base URL (override via MCP_DUBAI_PULSE_API_BASE).

This is NOT a feature folder with its own FastMCP server. It is the
shared building block that DLD, RTA, etc. use to query the dataset
gateway. Each Tier 1 feature instantiates a `DubaiPulseClient` with its
own org and dataset slug.
"""

from __future__ import annotations

from mcp_dubai.data.dubai_pulse.client import DubaiPulseClient

__all__ = ["DubaiPulseClient"]
