"""Tests for the Arabic / abbreviation alias expansion layer."""

from __future__ import annotations

from mcp_dubai._shared.aliases import (
    EQUIVALENCE_SETS,
    expand_text,
    expand_tokens,
)
from mcp_dubai._shared.discovery import (
    TIER_BIZ,
    TIER_OPEN,
    ToolDiscovery,
    ToolMeta,
)


class TestExpandText:
    def test_arabic_query_picks_up_english_equivalents(self) -> None:
        result = expand_text("تأشيرة ذهبية")
        assert "golden visa" in result.lower()

    def test_english_query_picks_up_arabic_equivalents(self) -> None:
        result = expand_text("golden visa")
        assert "تأشيرة ذهبية" in result

    def test_abbreviation_expands_to_long_form(self) -> None:
        result = expand_text("DMCC license")
        lower = result.lower()
        assert "dubai multi commodities centre" in lower
        assert "licence" in lower

    def test_mixed_script_query(self) -> None:
        result = expand_text("جميرا schools")
        lower = result.lower()
        assert "jumeirah" in lower
        assert "مدرسة" in lower or "مدارس" in lower

    def test_unmatched_text_returns_unchanged(self) -> None:
        result = expand_text("completely unrelated banana salsa")
        assert result == "completely unrelated banana salsa"

    def test_each_set_expands_at_most_once(self) -> None:
        """A text that mentions the same equivalence set twice should only
        append the set's members once, not twice."""
        result = expand_text("visa visa تأشيرة")
        lower = result.lower()
        # Input has 2x `visa` + 1x `تأشيرة`. Expansion adds every member
        # of the matched set once, so we get +1 `visa` and +1 `تأشيرة`
        # for a total of 3 and 2 respectively.
        assert lower.count("visa") == 3
        assert lower.count("تأشيرة") == 2

    def test_empty_text_is_safe(self) -> None:
        assert expand_text("") == ""

    def test_ascii_word_boundary_prevents_false_match(self) -> None:
        """`rta` is an abbreviation; it must not match inside `start`."""
        result = expand_text("startup")
        assert "roads and transport" not in result.lower()

    def test_ded_matches_as_abbreviation_not_inside_words(self) -> None:
        result = expand_text("added pedding")
        assert "department of economy" not in result.lower()

    def test_all_equivalence_sets_are_non_empty(self) -> None:
        for members in EQUIVALENCE_SETS:
            assert len(members) >= 2, (
                f"Equivalence set {members!r} has fewer than 2 members, "
                "which makes it useless for expansion."
            )


class TestExpandTokens:
    def test_tokens_round_trip(self) -> None:
        expanded = expand_tokens(["golden", "visa"])
        assert "golden" in expanded
        assert "visa" in expanded
        # Arabic equivalent should be appended
        assert any("تأشيرة" in tok for tok in expanded)

    def test_empty_token_list(self) -> None:
        assert expand_tokens([]) == []


class TestDiscoveryIntegration:
    """
    End-to-end: build a tiny discovery index with English-tagged tools
    and confirm Arabic queries surface them. This guards the integration
    points in `discovery.py` (query expansion + index expansion).
    """

    def _sample_discovery(self) -> ToolDiscovery:
        disc = ToolDiscovery()
        disc.register_many(
            [
                ToolMeta(
                    name="golden_visa_check",
                    description="Check eligibility for a UAE golden visa.",
                    feature="visas",
                    tier=TIER_BIZ,
                    tags=["golden visa", "investor", "residency", "10 year"],
                ),
                ToolMeta(
                    name="prayer_times_for",
                    description="Get prayer times for a UAE city or coordinates.",
                    feature="al_adhan",
                    tier=TIER_OPEN,
                    tags=["prayer", "salah", "fajr", "dubai"],
                ),
                ToolMeta(
                    name="khda_search_school",
                    description="Search Dubai private schools by area, curriculum, rating.",
                    feature="khda",
                    tier=TIER_OPEN,
                    tags=["school", "education", "dubai", "area", "curriculum"],
                ),
                ToolMeta(
                    name="corporate_tax_estimate",
                    description="Estimate UAE corporate tax liability.",
                    feature="tax_compliance",
                    tier=TIER_BIZ,
                    tags=["corporate tax", "9%", "free zone", "375000"],
                ),
                ToolMeta(
                    name="list_free_zones",
                    description="List all Dubai free zones with cost, visa, and bank acceptance.",
                    feature="free_zones",
                    tier=TIER_BIZ,
                    tags=["free zone", "DMCC", "DIFC", "jafza", "ifza"],
                ),
                ToolMeta(
                    name="air_quality_dubai",
                    description="Real-time air quality for Dubai stations.",
                    feature="air_quality",
                    tier=TIER_OPEN,
                    tags=["air quality", "aqi", "pm2.5", "dubai"],
                ),
            ]
        )
        return disc

    def test_arabic_golden_visa_query_surfaces_english_tool(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("تأشيرة ذهبية", top_k=3)
        assert results
        assert results[0].name == "golden_visa_check"

    def test_arabic_school_query_surfaces_khda(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("جميرا مدارس", top_k=3)
        assert results
        assert results[0].name == "khda_search_school"

    def test_arabic_corporate_tax_query(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("ضريبة الشركات", top_k=3)
        assert results
        assert results[0].name == "corporate_tax_estimate"

    def test_abbreviation_query_surfaces_free_zones(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("DMCC license", top_k=3)
        assert results
        assert results[0].name == "list_free_zones"

    def test_arabic_air_quality_query(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("جودة الهواء", top_k=3)
        assert results
        assert results[0].name == "air_quality_dubai"

    def test_arabic_prayer_query(self) -> None:
        disc = self._sample_discovery()
        results = disc.recommend("صلاة الفجر", top_k=3)
        assert results
        assert results[0].name == "prayer_times_for"

    def test_english_query_still_works(self) -> None:
        """Alias expansion must not regress pure-English routing."""
        disc = self._sample_discovery()
        results = disc.recommend("prayer times dubai", top_k=3)
        assert results[0].name == "prayer_times_for"

    def test_unknown_arabic_term_returns_nothing(self) -> None:
        disc = self._sample_discovery()
        # A query with zero overlap even after expansion should return empty.
        results = disc.recommend("كلمة مجهولة تماما", top_k=3)
        assert results == []
