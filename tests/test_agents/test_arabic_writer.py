"""Tests for arabic_writer agent."""

from __future__ import annotations

import pytest

from mcp_dubai.agents.arabic_writer import tools


class TestListHonorifics:
    @pytest.mark.asyncio
    async def test_returns_catalogue(self) -> None:
        result = await tools.list_honorifics()
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] >= 5
        ids = {h["id"] for h in data["honorifics"]}  # type: ignore[union-attr]
        assert "his_excellency" in ids
        assert "mr" in ids


class TestAddresseeBlock:
    @pytest.mark.asyncio
    async def test_basic_block(self) -> None:
        result = await tools.addressee_block(
            name="John Smith",
            honorific="mr",
            title="CEO",
            organization="Acme Trading LLC",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert "Mr. John Smith" in data["english"]
        assert "CEO" in data["english"]
        assert "السيد" in data["arabic"]

    @pytest.mark.asyncio
    async def test_excellency(self) -> None:
        result = await tools.addressee_block(
            name="Omar Al Olama",
            honorific="his_excellency",
            title="Minister of State for AI",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert "His Excellency" in data["english"]
        assert "سعادة" in data["arabic"]

    @pytest.mark.asyncio
    async def test_invalid_honorific(self) -> None:
        result = await tools.addressee_block(name="X", honorific="lord")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_empty_name(self) -> None:
        result = await tools.addressee_block(name="")
        assert result["success"] is False


class TestBusinessLetterTemplate:
    @pytest.mark.asyncio
    async def test_basic_template(self) -> None:
        result = await tools.business_letter_template(
            addressee_name="John Smith",
            subject="Partnership Proposal",
            honorific="mr",
        )
        data = result["data"]
        assert isinstance(data, dict)
        en = data["english"]
        ar = data["arabic"]
        assert isinstance(en, str)
        assert isinstance(ar, str)
        assert "Subject: Partnership Proposal" in en
        assert "الموضوع:" in ar
        assert "تحية طيبة وبعد" in ar

    @pytest.mark.asyncio
    async def test_custom_opening_closing(self) -> None:
        result = await tools.business_letter_template(
            addressee_name="X",
            subject="Y",
            opening="respectful",
            closing="warm",
        )
        data = result["data"]
        assert isinstance(data, dict)
        en = data["english"]
        assert isinstance(en, str)
        assert "Best regards" in en

    @pytest.mark.asyncio
    async def test_invalid_opening(self) -> None:
        result = await tools.business_letter_template(
            addressee_name="X",
            subject="Y",
            opening="casual",
        )
        assert result["success"] is False


class TestListSalutations:
    @pytest.mark.asyncio
    async def test_returns_openings_and_closings(self) -> None:
        result = await tools.list_salutations()
        data = result["data"]
        assert isinstance(data, dict)
        openings = data["openings"]
        closings = data["closings"]
        assert isinstance(openings, list)
        assert isinstance(closings, list)
        assert len(openings) >= 3
        assert len(closings) >= 3


class TestKnowledgeRegistration:
    def test_registers_with_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.agents.arabic_writer import tools as aw_tools

        importlib.reload(aw_tools)
        meta = get_knowledge_registry().get("arabic_writer")
        assert meta is not None
