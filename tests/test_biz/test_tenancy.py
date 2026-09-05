"""Tests for the tenancy biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.tenancy import tools


class TestEjariGuide:
    @pytest.mark.asyncio
    async def test_returns_current_channel_document_requirements(self) -> None:
        result = await tools.ejari_guide()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        docs = data["required_documents"]
        assert isinstance(docs, list)
        assert len(docs) == 3
        assert any("power of attorney" in doc.lower() for doc in docs)

    @pytest.mark.asyncio
    async def test_returns_fees_by_channel(self) -> None:
        result = await tools.ejari_guide()
        data = result["data"]
        assert isinstance(data, dict)
        fees = data["fees_by_channel_aed"]
        assert isinstance(fees, dict)
        assert fees["dubai_rest_app"] == 177.75
        assert fees["real_estate_trustee_centre"] == 220

    @pytest.mark.asyncio
    async def test_returns_channels_and_mistakes(self) -> None:
        result = await tools.ejari_guide()
        data = result["data"]
        assert isinstance(data, dict)
        assert isinstance(data["channels"], list)
        assert isinstance(data["common_mistakes"], list)
        assert len(data["common_mistakes"]) == 3
        assert isinstance(data["timeline"], dict)


class TestReraRentIncrease:
    @pytest.mark.asyncio
    async def test_gap_exactly_10_allows_no_increase(self) -> None:
        # DLD's Tenancy Guide says "up to ten percent": 10% is inclusive.
        result = await tools.rera_rent_increase(current_annual_rent=90000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["gap_pct"] == pytest.approx(10.0)
        assert data["max_increase_pct"] == 0
        assert data["max_new_rent_aed"] == pytest.approx(90000.0)
        assert data["band"] == "up to 10% below"

    @pytest.mark.asyncio
    async def test_gap_5_maps_to_0_pct(self) -> None:
        # current 95000 vs avg 100000 -> gap 5% -> 0% band.
        result = await tools.rera_rent_increase(current_annual_rent=95000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["gap_pct"] == pytest.approx(5.0)
        assert data["max_increase_pct"] == 0
        assert data["max_new_rent_aed"] == pytest.approx(95000.0)

    @pytest.mark.asyncio
    async def test_gap_25_maps_to_10_pct(self) -> None:
        # current 75000 vs avg 100000 -> gap 25% -> 10% band.
        result = await tools.rera_rent_increase(current_annual_rent=75000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["gap_pct"] == pytest.approx(25.0)
        assert data["max_increase_pct"] == 10

    @pytest.mark.asyncio
    async def test_gap_45_maps_to_20_pct(self) -> None:
        # current 55000 vs avg 100000 -> gap 45% -> 20% band.
        result = await tools.rera_rent_increase(current_annual_rent=55000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["gap_pct"] == pytest.approx(45.0)
        assert data["max_increase_pct"] == 20
        assert data["band"] == "more than 40% below"

    @pytest.mark.asyncio
    async def test_gap_exactly_20_stays_in_5_pct_band(self) -> None:
        # current 80000 vs avg 100000 -> gap 20% -> 5% band (boundary).
        result = await tools.rera_rent_increase(current_annual_rent=80000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["gap_pct"] == pytest.approx(20.0)
        assert data["max_increase_pct"] == 5

    @pytest.mark.asyncio
    async def test_current_at_or_above_average_is_0_pct(self) -> None:
        result = await tools.rera_rent_increase(
            current_annual_rent=120000, area_average_rent=100000
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["max_increase_pct"] == 0
        assert data["max_new_rent_aed"] == pytest.approx(120000.0)

    @pytest.mark.asyncio
    async def test_includes_notice_note(self) -> None:
        result = await tools.rera_rent_increase(current_annual_rent=90000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert "90 days" in str(data["notice_note"])

    @pytest.mark.asyncio
    async def test_includes_rent_cap_status(self) -> None:
        result = await tools.rera_rent_increase(current_annual_rent=90000, area_average_rent=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert "exactly 10% attracts no increase" in str(data["rent_cap_status"])

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
    async def test_nonfinite_inputs_fail(self, value: float) -> None:
        assert (await tools.rera_rent_increase(value, 100000))["success"] is False
        assert (await tools.rera_rent_increase(90000, value))["success"] is False
        assert (await tools.rental_dispute_guide(value))["success"] is False

    @pytest.mark.asyncio
    async def test_zero_current_rent_fails(self) -> None:
        result = await tools.rera_rent_increase(current_annual_rent=0, area_average_rent=100000)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_negative_average_fails(self) -> None:
        result = await tools.rera_rent_increase(current_annual_rent=90000, area_average_rent=-1)
        assert result["success"] is False


class TestRentalDisputeGuide:
    @pytest.mark.asyncio
    async def test_returns_rdc_block_without_rent(self) -> None:
        result = await tools.rental_dispute_guide()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["prerequisite"] == "active Ejari registration"
        assert "filing_fee_aed" not in data

    @pytest.mark.asyncio
    async def test_fee_hits_500_floor(self) -> None:
        # 10000 * 0.035 = 350 -> clamped up to 500.
        result = await tools.rental_dispute_guide(annual_rent=10000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["filing_fee_aed"] == pytest.approx(500.0)

    @pytest.mark.asyncio
    async def test_fee_mid_range(self) -> None:
        # 200000 * 0.035 = 7000.
        result = await tools.rental_dispute_guide(annual_rent=200000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["filing_fee_aed"] == pytest.approx(7000.0)

    @pytest.mark.asyncio
    async def test_fee_hits_20000_cap(self) -> None:
        # 1000000 * 0.035 = 35000 -> clamped down to 20000.
        result = await tools.rental_dispute_guide(annual_rent=1000000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["filing_fee_aed"] == pytest.approx(20000.0)

    @pytest.mark.asyncio
    async def test_negative_rent_fails(self) -> None:
        result = await tools.rental_dispute_guide(annual_rent=-5)
        assert result["success"] is False


class TestJuly2026PackAdditions:
    def test_flexi_rent_block(self) -> None:
        from mcp_dubai.biz._data.loader import load_data_file

        data = load_data_file("tenancy.json")
        flexi = data["flexi_rent"]
        assert flexi["launched"] == "2026-06-23"
        assert "monthly, quarterly, or semi-annual instalments" in flexi["summary"]
        partners = flexi["partners"]
        assert partners["count_at_launch"] == 12
        assert "Deyaar" in partners["named"]
        assert "Wasl" in partners["named"]
        assert len(flexi["source_urls"]) >= 2

    def test_shared_housing_block(self) -> None:
        from mcp_dubai.biz._data.loader import load_data_file

        data = load_data_file("tenancy.json")
        shared = data["shared_housing"]
        assert shared["law"] == "Dubai Law No. 4 of 2026"
        assert shared["fines"]["max_aed"] == 1000000
        assert "1 year" in shared["grace_period"]
        assert any("Registry" in rule for rule in shared["key_rules"])
        assert len(shared["source_urls"]) >= 3
        assert shared["published"] == "2026-03-12"
        assert shared["effective_from"] == "2026-09-08"
        assert "Upcoming" in shared["in_force"]

    def test_dld_initiatives_2026_block(self) -> None:
        from mcp_dubai.biz._data.loader import load_data_file

        data = load_data_file("tenancy.json")
        initiatives = data["dld_initiatives_2026"]
        assert "22 participating developers" in initiatives["first_time_home_buyer"]
        assert "PRYPCO Mint" in initiatives["tokenization"]
        assert "2026" in initiatives["smart_rental_index"]


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.ejari_guide()
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["knowledge_date"] == "2026-09-05"
        assert knowledge["volatility"] == "medium"

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.tenancy import tools as tenancy_tools

        importlib.reload(tenancy_tools)
        meta = get_knowledge_registry().get("tenancy")
        assert meta is not None


class TestDiscovery:
    def test_ejari_and_rent_queries_route_to_tenancy_tools(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.tenancy import server as tenancy_server

        importlib.reload(tenancy_server)

        disc = get_tool_discovery()

        ejari_results = disc.recommend("ejari registration dubai", top_k=3)
        assert ejari_results, "no recommendations for ejari registration dubai"
        assert ejari_results[0].name == "ejari_guide"

        rent_results = disc.recommend("can my landlord increase my rent", top_k=3)
        assert rent_results, "no recommendations for rent increase query"
        assert rent_results[0].name == "rera_rent_increase"
