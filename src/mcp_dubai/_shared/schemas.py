"""
Shared Pydantic v2 models for MCP-Dubai.

The most important model here is `ToolResponse`, the envelope every tool
returns. It carries:

- `success`: True for happy path, False for graceful failure.
- `data`: the payload (anything Pydantic can serialise).
- `error`: a string OR a structured dict (used by Pattern 2 for missing
  Dubai Pulse credentials).
- `knowledge`: optional KnowledgeMetadata for biz/* tools, so the LLM can
  see when the underlying knowledge was last verified.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mcp_dubai._shared.constants import KNOWLEDGE_DATE


# ----------------------------------------------------------------------------
# Bilingual support
# ----------------------------------------------------------------------------
class BilingualField(BaseModel):
    """A field with English and Arabic values. Dubai data often has both."""

    en: str = Field(description="English value")
    ar: str = Field(default="", description="Arabic value")

    def __str__(self) -> str:
        return self.en


# ----------------------------------------------------------------------------
# Knowledge freshness metadata
# ----------------------------------------------------------------------------
class KnowledgeMetadata(BaseModel):
    """
    Freshness stamp returned by every biz/* tool.

    The values come from per-domain constants in each biz feature module.
    The root server's `get_knowledge_status()` reads these constants so it
    never drifts from what the tools actually return.
    """

    knowledge_date: str = Field(
        default=KNOWLEDGE_DATE,
        description="Date this knowledge was last verified, in YYYY-MM-DD format.",
    )
    volatility: str = Field(
        default="medium",
        description="How often this changes: stable | medium | high.",
    )
    verify_at: str = Field(
        default="",
        description="Official URL where the user can verify current information.",
    )
    disclaimer: str = Field(
        default="Verify current rules with the official source before acting.",
        description="Standard disclaimer for business advice.",
    )


# ----------------------------------------------------------------------------
# Tool response envelope
# ----------------------------------------------------------------------------
T = TypeVar("T")


class ToolResponse(BaseModel, Generic[T]):
    """
    Standard envelope for every MCP-Dubai tool response.

    `error` accepts either a plain string or a structured dict. Tools that
    fail because Dubai Pulse credentials are missing return a dict with
    `status`, `reason`, and `docs` fields so the MCP client can render a
    proper help message (Pattern 2).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    data: T | None = None
    error: str | dict[str, Any] | None = None
    knowledge: KnowledgeMetadata | None = None

    @model_validator(mode="after")
    def _validate_consistency(self) -> ToolResponse[T]:
        if self.success and self.error is not None:
            raise ValueError("ToolResponse: success=True must not carry an error")
        if not self.success and self.error is None:
            raise ValueError("ToolResponse: success=False must carry an error")
        return self

    @classmethod
    def ok(
        cls,
        data: T,
        knowledge: KnowledgeMetadata | None = None,
    ) -> ToolResponse[T]:
        """Build a success response."""
        return cls(success=True, data=data, error=None, knowledge=knowledge)

    @classmethod
    def fail(
        cls,
        error: str | dict[str, Any],
        knowledge: KnowledgeMetadata | None = None,
    ) -> ToolResponse[T]:
        """
        Build a failure response.

        Accepts either a plain error string or a structured dict (used by
        the credential-missing path in Pattern 2).
        """
        return cls(success=False, data=None, error=error, knowledge=knowledge)


# ----------------------------------------------------------------------------
# Pagination
# ----------------------------------------------------------------------------
class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated payload for list-style endpoints."""

    data: list[T]
    total: int = Field(description="Total records available across all pages.")
    limit: int = Field(description="Records per page.")
    offset: int = Field(description="Current offset.")

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.data) < self.total


# ----------------------------------------------------------------------------
# Common shared types
# ----------------------------------------------------------------------------
class Coordinates(BaseModel):
    """Geographic coordinates with bounds checks."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class DateRange(BaseModel):
    """Inclusive date range for queries."""

    start: date
    end: date

    @model_validator(mode="after")
    def _validate_order(self) -> DateRange:
        if self.end < self.start:
            raise ValueError("DateRange: end must be on or after start")
        return self
