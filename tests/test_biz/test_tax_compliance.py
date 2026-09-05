"""Tests for the tax_compliance biz/* feature."""

from __future__ import annotations

import pytest

from mcp_dubai.biz.tax_compliance import tools


class TestCorporateTaxEstimate:
    @pytest.mark.asyncio
    async def test_below_threshold_zero_tax(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=300000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_corporate_tax_aed"] == 0

    @pytest.mark.asyncio
    async def test_above_threshold_charges_9_percent(self) -> None:
        # AED 1,000,000 - AED 375,000 = AED 625,000 taxable, * 9% = AED 56,250.
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=1000000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_corporate_tax_aed"] == 56250
        assert data["effective_rate_pct"] == round(56250 / 1000000 * 100, 2)

    @pytest.mark.asyncio
    async def test_qfzp_qualifying_split(self) -> None:
        # AED 1,000,000 income, 80% qualifying:
        # QFZPs do not receive the ordinary AED 375,000 0% band.
        # Qualifying: 800,000 -> 0%
        # Non-qualifying: 200,000 -> 9% = 18,000
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=1000000,
            is_free_zone=True,
            qfzp_qualifying_pct=80,
            industry="trading",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["qfzp_rules_applied"] is True
        assert data["tax_free_band_applied_aed"] == 0
        assert data["taxable_above_threshold_aed"] == 1000000
        assert data["qualifying_income_aed"] == 800000
        assert data["non_qualifying_income_aed"] == 200000
        assert data["total_corporate_tax_aed"] == 18000

    @pytest.mark.asyncio
    async def test_qfzp_has_no_threshold_or_small_business_relief(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=300000,
            is_free_zone=True,
            qfzp_qualifying_pct=80,
            industry="trading",
        )
        data = result["data"]
        assert isinstance(data, dict)
        assert data["qualifying_income_aed"] == 240000
        assert data["non_qualifying_income_aed"] == 60000
        assert data["total_corporate_tax_aed"] == 5400
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("AED 375,000" in warning for warning in warnings)
        assert not any("may qualify for Small Business Relief" in warning for warning in warnings)

    @pytest.mark.asyncio
    async def test_saas_qfzp_warning(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=2000000,
            is_free_zone=True,
            qfzp_qualifying_pct=100,
            industry="saas",
        )
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any("SaaS" in w and "counterparty" in w for w in warnings)
        assert any("do not assume all SaaS revenue is non-qualifying" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_small_business_relief_warning(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=2500000)
        data = result["data"]
        assert isinstance(data, dict)
        warnings = data["warnings"]
        assert isinstance(warnings, list)
        assert any(
            "Small Business Relief" in w and "131/2026" in w and "2029-12-31" in w for w in warnings
        )

    @pytest.mark.asyncio
    async def test_negative_income_returns_error(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=-1)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_qfzp_pct_returns_error(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=1000000, qfzp_qualifying_pct=150
        )
        assert result["success"] is False


class TestVatFilingCalendar:
    @pytest.mark.asyncio
    async def test_below_voluntary_threshold(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=100000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "not_required"

    @pytest.mark.asyncio
    async def test_voluntary_band(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=250000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "voluntary_eligible"

    @pytest.mark.asyncio
    async def test_mandatory_threshold(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=500000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["registration"] == "mandatory"
        assert data["filing_frequency"] == "quarterly"

    @pytest.mark.asyncio
    async def test_large_business_files_monthly(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=200000000)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["filing_frequency"] == "monthly"

    @pytest.mark.asyncio
    async def test_surfaces_fdl_16_2025_amendments(self) -> None:
        result = await tools.vat_filing_calendar(annual_revenue_aed=500000)
        data = result["data"]
        assert isinstance(data, dict)
        amendments = data["amendments_2026"]
        assert isinstance(amendments, dict)
        assert amendments["law"] == "Federal Decree-Law 16 of 2025"
        assert amendments["effective_from"] == "2026-01-01"
        changes = amendments["changes"]
        assert isinstance(changes, list)
        assert any("5 years" in c for c in changes)
        assert any("Reverse-charge" in c for c in changes)


class TestQfzpCheck:
    @pytest.mark.asyncio
    async def test_saas_requires_income_specific_assessment(self) -> None:
        result = await tools.qfzp_check(industry="saas", is_free_zone=True)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "verify"
        assert "counterparty" in data["reason"]
        assert "do not assume all SaaS revenue is non-qualifying" in data["reason"]

    @pytest.mark.asyncio
    async def test_mainland_not_eligible(self) -> None:
        result = await tools.qfzp_check(industry="trading", is_free_zone=False)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "not_eligible"

    @pytest.mark.asyncio
    async def test_trading_potentially_qualifying(self) -> None:
        result = await tools.qfzp_check(industry="trading", is_free_zone=True)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["verdict"] == "potentially_qualifying"


class TestEsrStatus:
    @pytest.mark.asyncio
    async def test_returns_dead_status(self) -> None:
        result = await tools.esr_status()
        data = result["data"]
        assert isinstance(data, dict)
        assert "DEAD" in data["status"]

    def test_esr_queries_route_to_single_surviving_tool(self) -> None:
        """After the esr_check removal there must be exactly one ESR tool and
        discovery must surface it for the common natural-language phrasings."""
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.biz.compliance import server as compliance_server
        from mcp_dubai.biz.tax_compliance import server as tax_server

        importlib.reload(compliance_server)
        importlib.reload(tax_server)

        disc = get_tool_discovery()
        all_esr = [m for m in disc.list_all() if "esr" in m.name.lower()]
        assert [m.name for m in all_esr] == ["esr_status"]

        for query in (
            "do i need to file ESR",
            "economic substance regulations",
            "is ESR still required",
        ):
            results = disc.recommend(query, top_k=3)
            assert results, f"no recommendations for {query!r}"
            assert results[0].name == "esr_status", (
                f"query {query!r} did not route to esr_status; top was {results[0].name}"
            )


class TestEInvoicing:
    @pytest.mark.asyncio
    async def test_returns_rollout_dates_and_legislation(self) -> None:
        result = await tools.einvoicing_timeline()
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        legislation = data["legislation"]
        assert isinstance(legislation, list)
        assert "Ministerial Decision 243 of 2025" in legislation
        assert "Ministerial Decision 244 of 2025" in legislation
        assert "Ministerial Resolution 66 of 2026" in legislation
        rollout = data["rollout"]
        assert isinstance(rollout, dict)
        assert rollout["voluntary_pilot_from"] == "2026-07-01"
        assert rollout["mandatory_revenue_at_or_above_aed_50m_from"] == "2027-01-01"
        assert rollout["mandatory_revenue_below_aed_50m_from"] == "2027-07-01"
        assert rollout["government_entities_from"] == "2027-10-01"
        what_to_do_now = data["what_to_do_now"]
        assert isinstance(what_to_do_now, list)
        assert len(what_to_do_now) >= 1

    @pytest.mark.asyncio
    async def test_status_reflects_live_pilot(self) -> None:
        result = await tools.einvoicing_timeline()
        data = result["data"]
        assert isinstance(data, dict)
        status = data["status"]
        assert isinstance(status, str)
        assert "pilot" in status.lower()
        assert "2026-07-01" in status

    @pytest.mark.asyncio
    async def test_surfaces_asp_appointment_deadlines(self) -> None:
        result = await tools.einvoicing_timeline()
        data = result["data"]
        assert isinstance(data, dict)
        deadlines = data["asp_appointment_deadlines"]
        assert isinstance(deadlines, dict)
        large = deadlines["revenue_at_or_above_aed_50m"]
        assert isinstance(large, dict)
        assert large["appoint_asp_by"] == "2026-10-30"
        assert large["extended_from"] == "2026-07-31"
        assert "66 of 2026" in large["extension_law"]
        assert large["go_live"] == "2027-01-01"
        small = deadlines["revenue_below_aed_50m"]
        assert isinstance(small, dict)
        assert small["appoint_asp_by"] == "2027-03-31"
        assert small["go_live"] == "2027-07-01"
        government = deadlines["government_entities"]
        assert isinstance(government, dict)
        assert government["go_live"] == "2027-10-01"

    @pytest.mark.asyncio
    async def test_surfaces_asp_register_and_technical_docs(self) -> None:
        result = await tools.einvoicing_timeline()
        data = result["data"]
        assert isinstance(data, dict)
        register = data["asp_register"]
        assert isinstance(register, dict)
        assert register["pre_approved_provider_count"] is None
        assert register["accredited_provider_count"] == 50
        assert register["under_final_assessment_count"] == 7
        assert register["as_of"] == "2026-09-05"
        assert register["register_url"] == (
            "https://mof.gov.ae/en/about-us/initiatives/einvoicing/"
            "einvoicing-accredited-service-providers-asps/"
        )
        assert "56 of 2026" in register["criteria_note"]
        docs = data["technical_docs"]
        assert isinstance(docs, dict)
        assert "V-1.1" in docs["guidelines"]
        assert "V-1.0" in docs["mandatory_fields"]
        assert "PINT AE" in docs["format"]


class TestLatePaymentPenalty:
    @pytest.mark.asyncio
    async def test_full_year(self) -> None:
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=365)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["estimated_penalty_aed"] == 14000.0

    @pytest.mark.asyncio
    async def test_thirty_days_is_one_whole_month(self) -> None:
        """CD 129/2025 charges per month or part thereof, not pro-rated by day."""
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=30)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["months_charged"] == 1
        assert data["estimated_penalty_aed"] == pytest.approx(1166.67, abs=0.01)

    @pytest.mark.asyncio
    async def test_one_day_late_charges_a_full_month(self) -> None:
        """A part month is a whole month, so day 1 already costs 14%/12."""
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=1)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["months_charged"] == 1
        assert data["estimated_penalty_aed"] == pytest.approx(1166.67, abs=0.01)

    @pytest.mark.asyncio
    async def test_thirty_one_days_rolls_into_a_second_month(self) -> None:
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=31)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["months_charged"] == 2

    @pytest.mark.asyncio
    async def test_zero_days_late_is_not_late(self) -> None:
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=0)
        data = result["data"]
        assert isinstance(data, dict)
        assert data["months_charged"] == 0
        assert data["estimated_penalty_aed"] == 0.0

    @pytest.mark.asyncio
    async def test_non_positive_tax_due_returns_error(self) -> None:
        result = await tools.late_payment_penalty_estimate(tax_due_aed=0, days_late=30)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_negative_days_late_returns_error(self) -> None:
        result = await tools.late_payment_penalty_estimate(tax_due_aed=100000, days_late=-1)
        assert result["success"] is False


class TestKnowledge:
    @pytest.mark.asyncio
    async def test_envelope_includes_knowledge(self) -> None:
        result = await tools.corporate_tax_estimate(annual_taxable_income_aed=500000)
        knowledge = result["knowledge"]
        assert isinstance(knowledge, dict)
        assert knowledge["volatility"] == "high"
        assert knowledge["knowledge_date"] == "2026-09-05"
        assert knowledge["previous_knowledge_date"] == "2026-08-14"
        assert "Pillar Two Information Return" in knowledge["last_refresh_scope"]

    def test_registers_with_knowledge_registry(self) -> None:
        import importlib

        from mcp_dubai._shared.knowledge import get_knowledge_registry
        from mcp_dubai.biz.tax_compliance import tools as tax_tools

        importlib.reload(tax_tools)
        meta = get_knowledge_registry().get("tax_compliance")
        assert meta is not None


class TestCuratedPackAugust2026:
    """Knowledge-only blocks refreshed for the 2026-08-14 pack."""

    def _data(self) -> dict[str, object]:
        from mcp_dubai.biz._data.loader import load_data_file

        return load_data_file("tax_compliance.json")

    def test_knowledge_date_bumped(self) -> None:
        data = self._data()
        assert data["knowledge_date"] == "2026-09-05"

    def test_tax_procedures_fdl_17_2025(self) -> None:
        data = self._data()
        tp = data["tax_procedures"]
        assert isinstance(tp, dict)
        assert "Federal Decree-Law 17 of 2025" in tp["law"]
        assert tp["effective_from"] == "2026-01-01"
        audit = tp["audit_window"]
        assert isinstance(audit, dict)
        assert audit["standard_years"] == 5
        assert audit["extended_years_for_evasion_or_failure_to_register"] == 15
        assert audit["extra_years_for_audits_notified_before_expiry"] == 4
        refunds = tp["refunds_and_credit_balances"]
        assert isinstance(refunds, dict)
        assert refunds["claim_window_years"] == 5
        assert "31 December 2026" in refunds["transition"]

    def test_aml_cft_fdl_10_2025(self) -> None:
        data = self._data()
        aml = data["aml_cft"]
        assert isinstance(aml, dict)
        assert aml["law"] == "Federal Decree-Law 10 of 2025"
        assert aml["in_force_since"] == "2025-10-14"
        assert aml["executive_regulations"] == "Cabinet Resolution 134 of 2025"
        fines = aml["fines_legal_persons_aed"]
        assert isinstance(fines, dict)
        assert fines["min"] == 5000000
        assert fines["max"] == 100000000
        assert "20 of 2018" in aml["historical_note"]

    def test_vara_issuance_rulebook_2026(self) -> None:
        data = self._data()
        aml = data["aml_cft"]
        assert isinstance(aml, dict)
        vara = aml["vara"]
        assert isinstance(vara, dict)
        rulebook = vara["issuance_rulebook_2026"]
        assert isinstance(rulebook, dict)
        note = rulebook["note"]
        assert isinstance(note, str)
        assert "Issuance Rulebook" in note
        assert "derivatives" in note

    def test_sweetened_drinks_tiers(self) -> None:
        data = self._data()
        excise = data["excise"]
        assert isinstance(excise, dict)
        volumetric = excise["sweetened_drinks_volumetric"]
        assert isinstance(volumetric, dict)
        tiers = volumetric["tiers"]
        assert isinstance(tiers, list)
        assert [t["rate_aed_per_litre"] for t in tiers] == [0.79, 1.09]
        assert "5g" in volumetric["exempt"]
        assert "Emirates Conformity Certificate" in volumetric["certification"]
        assert "1.09" in volumetric["certification"]

    def test_tobacco_and_vaping_minimum_excise_prices(self) -> None:
        data = self._data()
        excise = data["excise"]
        assert isinstance(excise, dict)
        minimums = excise["tobacco_and_vaping_minimum_excise_prices"]
        assert isinstance(minimums, dict)
        assert minimums["law"] == "Cabinet Decision 137 of 2026"
        assert minimums["effective_from"] == "2026-09-01"
        prices = minimums["minimum_excise_prices"]
        assert isinstance(prices, list)
        assert [p["minimum_excise_price_aed"] for p in prices] == [0.4, 0.1, 1]

    def test_corporate_tax_2026_additions(self) -> None:
        data = self._data()
        ct = data["corporate_tax"]
        assert isinstance(ct, dict)
        dmtt = ct["pillar_two_dmtt"]
        assert isinstance(dmtt, dict)
        registration = dmtt["registration_status"]
        assert isinstance(registration, dict)
        assert registration["first_return_expected_due"] == "2027-06-30"
        assert "confirm" in str(registration["status"]).lower()
        sports = ct["sports_entities_exemption"]
        assert isinstance(sports, dict)
        assert sports["law"] == "Cabinet Decision 1 of 2026"
        assert sports["retroactive_from"] == "2023-06-01"
        fees = ct["fta_service_fees"]
        assert isinstance(fees, dict)
        assert fees["law"] == "Cabinet Decision 174 of 2025"
        guides = ct["guides_2026"]
        assert isinstance(guides, dict)
        assert "Family Foundations" in guides["note"]


class TestSeptemberCorrectness:
    @pytest.mark.asyncio
    async def test_qfzp_with_zero_qualifying_income_has_no_ordinary_band(self) -> None:
        result = await tools.corporate_tax_estimate(
            annual_taxable_income_aed=300000,
            is_free_zone=True,
            is_qfzp=True,
            qfzp_qualifying_pct=0,
        )
        data = result["data"]
        assert data["tax_free_band_applied_aed"] == 0
        assert data["total_corporate_tax_aed"] == 27000
        assert (
            data["pillar_two_dmtt"]["information_return"]["law"]
            == "Ministerial Decision 133 of 2026"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_free_zone,is_qfzp,qualifying", [(False, True, 0), (True, False, 50)]
    )
    async def test_inconsistent_qfzp_status_is_rejected(
        self, is_free_zone: bool, is_qfzp: bool, qualifying: int
    ) -> None:
        result = await tools.corporate_tax_estimate(
            300000, is_free_zone=is_free_zone, is_qfzp=is_qfzp, qfzp_qualifying_pct=qualifying
        )
        assert result["success"] is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "amount,expected",
        [
            (187500, "not_required"),
            (187501, "voluntary_eligible"),
            (375000, "voluntary_eligible"),
            (375001, "mandatory"),
        ],
    )
    async def test_vat_registration_requires_exceeding_the_threshold(
        self, amount: int, expected: str
    ) -> None:
        result = await tools.vat_filing_calendar(amount)
        assert result["data"]["registration"] == expected
        assert "next-30-days" in result["data"]["assessment_scope"]
        assert len(result["data"]["directives_2026"]["directives"]) == 5
