"""
Per-domain knowledge registry.

Each biz/* module exposes a module-level `KNOWLEDGE` constant of type
`KnowledgeMetadata`. At import time, the module calls
`register_domain_knowledge(domain, KNOWLEDGE)` so the root server's
`get_knowledge_status()` meta-tool can return current freshness without
duplicating the constants.

When a quarterly re-verification sweep bumps the knowledge_date in
`biz/setup_advisor/tools.py`, the change shows up in
`get_knowledge_status()` automatically.
"""

from __future__ import annotations

from mcp_dubai._shared.schemas import KnowledgeMetadata


class KnowledgeRegistry:
    """Maps domain name to its KnowledgeMetadata."""

    def __init__(self) -> None:
        self._domains: dict[str, KnowledgeMetadata] = {}

    def register(self, domain: str, knowledge: KnowledgeMetadata) -> None:
        """Register or update a domain's knowledge metadata."""
        self._domains[domain] = knowledge

    def get(self, domain: str) -> KnowledgeMetadata | None:
        return self._domains.get(domain)

    def all(self) -> dict[str, KnowledgeMetadata]:
        return dict(self._domains)

    def clear(self) -> None:
        self._domains.clear()


# ----------------------------------------------------------------------------
# Singleton accessor
# ----------------------------------------------------------------------------
_registry_instance: KnowledgeRegistry | None = None


def get_knowledge_registry() -> KnowledgeRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = KnowledgeRegistry()
    return _registry_instance


def register_domain_knowledge(domain: str, knowledge: KnowledgeMetadata) -> None:
    """Convenience wrapper. Used by every biz/* module at import time."""
    get_knowledge_registry().register(domain, knowledge)


def reset_knowledge_registry() -> None:
    """Drop the singleton. Used by the test fixture."""
    global _registry_instance
    _registry_instance = None
