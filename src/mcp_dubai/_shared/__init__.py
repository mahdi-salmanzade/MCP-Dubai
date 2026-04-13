"""Shared utilities for MCP-Dubai features."""

from mcp_dubai._shared.auth import (
    DubaiPulseAuth,
    DubaiPulseAuthError,
    DubaiPulseCredentialsMissingError,
    get_dubai_pulse_auth,
    reset_dubai_pulse_auth,
)
from mcp_dubai._shared.constants import (
    DUBAI_PULSE_API_BASE,
    DUBAI_PULSE_TOKEN_URL,
    KNOWLEDGE_DATE,
    UAE_ICAO_CODES,
    UAE_TIMEZONE,
)
from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    TIER_DUBAI_PULSE,
    TIER_META,
    TIER_OPEN,
    ToolDiscovery,
    ToolMeta,
    get_tool_discovery,
    reset_tool_discovery,
)
from mcp_dubai._shared.http_client import (
    HttpClient,
    HttpClientError,
    RateLimitError,
)
from mcp_dubai._shared.knowledge import (
    KnowledgeRegistry,
    get_knowledge_registry,
    register_domain_knowledge,
    reset_knowledge_registry,
)
from mcp_dubai._shared.schemas import (
    BilingualField,
    Coordinates,
    DateRange,
    KnowledgeMetadata,
    PaginatedResponse,
    ToolResponse,
)

__all__ = [
    # auth
    "DubaiPulseAuth",
    "DubaiPulseAuthError",
    "DubaiPulseCredentialsMissingError",
    "get_dubai_pulse_auth",
    "reset_dubai_pulse_auth",
    # constants
    "DUBAI_PULSE_API_BASE",
    "DUBAI_PULSE_TOKEN_URL",
    "KNOWLEDGE_DATE",
    "UAE_ICAO_CODES",
    "UAE_TIMEZONE",
    # discovery
    "TIER_BIZ",
    "TIER_DUBAI_PULSE",
    "TIER_META",
    "TIER_OPEN",
    "ToolDiscovery",
    "ToolMeta",
    "get_tool_discovery",
    "reset_tool_discovery",
    # http
    "HttpClient",
    "HttpClientError",
    "RateLimitError",
    # knowledge
    "KnowledgeRegistry",
    "get_knowledge_registry",
    "register_domain_knowledge",
    "reset_knowledge_registry",
    # schemas
    "BilingualField",
    "Coordinates",
    "DateRange",
    "KnowledgeMetadata",
    "PaginatedResponse",
    "ToolResponse",
]
