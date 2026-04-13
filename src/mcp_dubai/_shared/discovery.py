"""
BM25-based tool discovery for the recommend_tools meta-tool.

Each feature registers its tools with `ToolMeta` records on import. The root
server's `recommend_tools` calls `ToolDiscovery.recommend(query)` to get a
ranked list of relevant tools, so an LLM does not need to scan all 50+
tool definitions to find the right one.

This is the BM25 layer from mcp-brasil, adapted for our tier system.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Tool tiers
# ----------------------------------------------------------------------------
TIER_OPEN: Final[int] = 0  # No auth, ship first
TIER_DUBAI_PULSE: Final[int] = 1  # OAuth gated, free but credential-issued
TIER_BIZ: Final[int] = 2  # Curated business knowledge, no external API
TIER_META: Final[int] = 3  # recommend_tools, get_knowledge_status, etc.


@dataclass
class ToolMeta:
    """Metadata for a single registered tool."""

    name: str
    description: str
    feature: str
    tier: int
    tags: list[str] = field(default_factory=list)
    requires_auth: bool = False

    @property
    def searchable_text(self) -> str:
        """Text used for BM25 indexing."""
        return f"{self.name} {self.description} {' '.join(self.tags)}"


class ToolDiscovery:
    """
    BM25-based tool recommendation engine.

    Indexes all registered tools and returns ranked recommendations for
    natural-language queries. The index is rebuilt lazily on the first
    `recommend()` call after a registration.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolMeta] = {}
        self._bm25: BM25Okapi | None = None
        self._tool_names: list[str] = []

    def register(self, tool: ToolMeta) -> None:
        """Register one tool. Invalidates the index."""
        self._tools[tool.name] = tool
        self._bm25 = None

    def register_many(self, tools: list[ToolMeta]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.register(tool)

    def _build_index(self) -> None:
        if not self._tools:
            return
        self._tool_names = list(self._tools.keys())
        tokenized = [self._tools[name].searchable_text.lower().split() for name in self._tool_names]
        self._bm25 = BM25Okapi(tokenized)
        logger.debug("Built BM25 index with %d tools", len(self._tool_names))

    def recommend(self, query: str, top_k: int = 5) -> list[ToolMeta]:
        """
        Recommend tools for a natural-language query.

        Args:
            query: What the user is trying to do.
            top_k: Maximum number of recommendations to return.

        Returns:
            ToolMeta entries ranked by BM25 score, descending. Filters out
            tools with zero token overlap with the query (which is more
            reliable than the absolute BM25 score, since BM25 with very
            few documents in the corpus can produce negative scores even
            when the query is clearly relevant).
        """
        if self._bm25 is None:
            self._build_index()
        if self._bm25 is None or not self._tool_names:
            return []

        tokenized_query = query.lower().split()
        if not tokenized_query:
            return []

        # Compute token overlap between the query and each tool. This is
        # the actual "relevant?" signal. BM25 then ranks within the
        # relevant set.
        relevant_indices: list[int] = []
        for i, name in enumerate(self._tool_names):
            tool_tokens = set(self._tools[name].searchable_text.lower().split())
            if any(token in tool_tokens for token in tokenized_query):
                relevant_indices.append(i)

        if not relevant_indices:
            return []

        scores = self._bm25.get_scores(tokenized_query)
        ranked = sorted(
            relevant_indices,
            key=lambda i: scores[i],
            reverse=True,
        )[:top_k]

        return [self._tools[self._tool_names[i]] for i in ranked]

    def get_by_feature(self, feature: str) -> list[ToolMeta]:
        return [t for t in self._tools.values() if t.feature == feature]

    def get_by_tier(self, tier: int) -> list[ToolMeta]:
        return [t for t in self._tools.values() if t.tier == tier]

    def list_all(self) -> list[ToolMeta]:
        return list(self._tools.values())

    def clear(self) -> None:
        """Drop all registrations. Used by tests."""
        self._tools.clear()
        self._bm25 = None
        self._tool_names = []


# ----------------------------------------------------------------------------
# Singleton accessor
# ----------------------------------------------------------------------------
_discovery_instance: ToolDiscovery | None = None


def get_tool_discovery() -> ToolDiscovery:
    """Return the singleton ToolDiscovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = ToolDiscovery()
    return _discovery_instance


def reset_tool_discovery() -> None:
    """Drop the singleton. Used by the test fixture."""
    global _discovery_instance
    _discovery_instance = None
