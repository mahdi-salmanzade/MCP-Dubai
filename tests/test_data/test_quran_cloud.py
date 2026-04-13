"""Tests for the quran_cloud feature."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.quran_cloud import constants, tools


def _surah_payload() -> dict[str, object]:
    return {
        "code": 200,
        "status": "OK",
        "data": {
            "number": 1,
            "name": "سُورَةُ ٱلْفَاتِحَةِ",
            "englishName": "Al-Fatihah",
            "englishNameTranslation": "The Opening",
            "revelationType": "Meccan",
            "numberOfAyahs": 7,
            "ayahs": [
                {
                    "number": 1,
                    "text": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
                    "numberInSurah": 1,
                    "juz": 1,
                    "manzil": 1,
                    "page": 1,
                    "ruku": 1,
                    "hizbQuarter": 1,
                    "sajda": False,
                }
            ],
            "edition": {"identifier": "quran-uthmani", "language": "ar"},
        },
    }


def _ayah_payload() -> dict[str, object]:
    return {
        "code": 200,
        "status": "OK",
        "data": {
            "number": 262,
            "text": ("ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ"),
            "surah": {"number": 2, "name": "Al-Baqarah", "numberOfAyahs": 286},
            "numberInSurah": 255,
            "juz": 3,
            "page": 42,
            "edition": {"identifier": "quran-uthmani", "language": "ar"},
        },
    }


def _search_payload() -> dict[str, object]:
    return {
        "code": 200,
        "status": "OK",
        "data": {
            "count": 1,
            "matches": [
                {
                    "number": 262,
                    "text": "Allah, there is no deity except Him",
                    "surah": {"number": 2, "englishName": "Al-Baqarah"},
                    "numberInSurah": 255,
                }
            ],
        },
    }


class TestQuranSurah:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_surah(self) -> None:
        url = f"{constants.SURAH}/1/quran-uthmani"
        route = respx.get(url).mock(return_value=Response(200, json=_surah_payload()))

        result = await tools.quran_surah(number=1)

        assert route.called
        assert result["englishName"] == "Al-Fatihah"
        assert result["numberOfAyahs"] == 7

    @pytest.mark.asyncio
    async def test_invalid_surah_number_raises(self) -> None:
        with pytest.raises(ValueError, match=r"surah number"):
            await tools.quran_surah(number=200)

    @pytest.mark.asyncio
    async def test_zero_invalid(self) -> None:
        with pytest.raises(ValueError, match=r"surah number"):
            await tools.quran_surah(number=0)


class TestQuranAyah:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_ayah(self) -> None:
        url = f"{constants.AYAH}/2:255/quran-uthmani"
        route = respx.get(url).mock(return_value=Response(200, json=_ayah_payload()))

        result = await tools.quran_ayah(reference="2:255")

        assert route.called
        assert result["numberInSurah"] == 255
        surah = result["surah"]
        assert isinstance(surah, dict)
        assert surah["englishName" if "englishName" in surah else "name"]

    @pytest.mark.asyncio
    async def test_empty_reference_raises(self) -> None:
        with pytest.raises(ValueError, match=r"reference"):
            await tools.quran_ayah(reference="")


class TestQuranJuz:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_juz(self) -> None:
        url = f"{constants.JUZ}/1/quran-uthmani"
        route = respx.get(url).mock(
            return_value=Response(200, json={"code": 200, "status": "OK", "data": {"number": 1}})
        )

        result = await tools.quran_juz(number=1)
        assert route.called
        assert result["number"] == 1

    @pytest.mark.asyncio
    async def test_invalid_juz_raises(self) -> None:
        with pytest.raises(ValueError, match=r"juz number"):
            await tools.quran_juz(number=31)


class TestQuranSearch:
    @pytest.mark.asyncio
    @respx.mock
    async def test_search_returns_matches(self) -> None:
        url = f"{constants.SEARCH}/Allah/all/en"
        route = respx.get(url).mock(return_value=Response(200, json=_search_payload()))

        result = await tools.quran_search(query="Allah")

        assert route.called
        assert result["count"] == 1
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1

    @pytest.mark.asyncio
    async def test_empty_query_raises(self) -> None:
        with pytest.raises(ValueError, match=r"query"):
            await tools.quran_search(query="")


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.quran_cloud import server as quran_server

        importlib.reload(quran_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("quran_cloud")}
        assert names == {"quran_surah", "quran_ayah", "quran_juz", "quran_search"}

    def test_recommend_for_quran_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.quran_cloud import server as quran_server

        importlib.reload(quran_server)
        results = get_tool_discovery().recommend("ayatul kursi quran verse", top_k=3)
        assert results
        assert results[0].feature == "quran_cloud"
