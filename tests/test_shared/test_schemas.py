"""Tests for the ToolResponse envelope and KnowledgeMetadata."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_dubai._shared.schemas import (
    BilingualField,
    Coordinates,
    DateRange,
    KnowledgeMetadata,
    ToolResponse,
)


class TestToolResponse:
    def test_ok_carries_data(self) -> None:
        response = ToolResponse[dict].ok({"hello": "world"})
        assert response.success is True
        assert response.data == {"hello": "world"}
        assert response.error is None

    def test_ok_carries_knowledge_metadata(self) -> None:
        knowledge = KnowledgeMetadata(
            knowledge_date="2026-04-12",
            volatility="high",
            verify_at="https://example.ae",
        )
        response = ToolResponse[dict].ok({"x": 1}, knowledge=knowledge)
        assert response.knowledge is not None
        assert response.knowledge.knowledge_date == "2026-04-12"
        assert response.knowledge.volatility == "high"

    def test_fail_with_string_error(self) -> None:
        response = ToolResponse[dict].fail("something broke")
        assert response.success is False
        assert response.error == "something broke"
        assert response.data is None

    def test_fail_with_structured_error(self) -> None:
        """Pattern 2: credential-missing path returns dict error."""
        error_payload = {
            "status": "credentials_missing",
            "reason": "MCP_DUBAI_PULSE_CLIENT_ID is not set",
            "docs": "https://example.com",
        }
        response = ToolResponse[dict].fail(error_payload)
        assert response.success is False
        assert isinstance(response.error, dict)
        assert response.error["status"] == "credentials_missing"

    def test_success_with_error_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            ToolResponse(success=True, data={"x": 1}, error="contradiction")

    def test_failure_without_error_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            ToolResponse(success=False, data=None, error=None)

    def test_envelope_round_trips_through_model_dump(self) -> None:
        """The MCP server returns model_dump output. Make sure it round trips."""
        response = ToolResponse[dict].ok({"k": "v"})
        dumped = response.model_dump()
        assert dumped["success"] is True
        assert dumped["data"] == {"k": "v"}
        assert dumped["error"] is None
        assert dumped["source"] is None
        assert dumped["retrieved_at"] is None

    def test_ok_carries_source_and_retrieved_at(self) -> None:
        response = ToolResponse[dict].ok(
            {"k": "v"},
            source="example.ae",
            retrieved_at="2026-04-15T12:00:00Z",
        )
        assert response.source == "example.ae"
        assert response.retrieved_at == "2026-04-15T12:00:00Z"

    def test_fail_carries_source_and_retrieved_at(self) -> None:
        response = ToolResponse[dict].fail(
            "boom",
            source="example.ae",
            retrieved_at="2026-04-15T12:00:00Z",
        )
        assert response.source == "example.ae"
        assert response.retrieved_at == "2026-04-15T12:00:00Z"


class TestKnowledgeMetadata:
    def test_defaults_use_project_knowledge_date(self) -> None:
        from mcp_dubai._shared.constants import KNOWLEDGE_DATE

        meta = KnowledgeMetadata()
        assert meta.knowledge_date == KNOWLEDGE_DATE
        assert meta.volatility == "medium"
        assert "Verify" in meta.disclaimer

    def test_custom_volatility(self) -> None:
        meta = KnowledgeMetadata(volatility="stable")
        assert meta.volatility == "stable"


class TestBilingualField:
    def test_str_returns_english(self) -> None:
        field = BilingualField(en="Dubai", ar="دبي")
        assert str(field) == "Dubai"

    def test_arabic_defaults_to_empty(self) -> None:
        field = BilingualField(en="Dubai")
        assert field.ar == ""


class TestCoordinates:
    def test_valid_coords(self) -> None:
        coords = Coordinates(latitude=25.2048, longitude=55.2708)
        assert coords.latitude == 25.2048

    def test_latitude_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            Coordinates(latitude=91.0, longitude=55.0)

    def test_longitude_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            Coordinates(latitude=25.0, longitude=181.0)


class TestDateRange:
    def test_valid_range(self) -> None:
        from datetime import date

        dr = DateRange(start=date(2026, 1, 1), end=date(2026, 12, 31))
        assert dr.start.year == 2026

    def test_end_before_start_is_invalid(self) -> None:
        from datetime import date

        with pytest.raises(ValidationError):
            DateRange(start=date(2026, 12, 31), end=date(2026, 1, 1))
