"""Tests for the quran_cloud feature."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.quran_cloud import constants, tools
from mcp_dubai.data.quran_cloud.client import QuranCloudClient


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
        data = result["data"]
        assert isinstance(data, dict)
        assert data["englishName"] == "Al-Fatihah"
        assert data["numberOfAyahs"] == 7
        assert result["source"] == "api.alquran.cloud"

    @pytest.mark.asyncio
    async def test_invalid_surah_number_returns_fail(self) -> None:
        result = await tools.quran_surah(number=200)
        assert result["success"] is False
        assert "surah number" in str(result["error"])

    @pytest.mark.asyncio
    async def test_zero_invalid(self) -> None:
        result = await tools.quran_surah(number=0)
        assert result["success"] is False
        assert "surah number" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_non_object_top_level_response_returns_fail(self) -> None:
        respx.get(f"{constants.SURAH}/1/quran-uthmani").mock(
            return_value=Response(200, json=[{"code": 200}])
        )

        result = await tools.quran_surah(number=1)

        assert result["success"] is False
        assert "top-level response is not an object" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("data", [None, [], "unexpected"])
    async def test_non_object_data_returns_fail(self, data: object) -> None:
        respx.get(f"{constants.SURAH}/1/quran-uthmani").mock(
            return_value=Response(200, json={"code": 200, "status": "OK", "data": data})
        )

        result = await tools.quran_surah(number=1)

        assert result["success"] is False
        assert "data is not an object" in str(result["error"])


class TestQuranAyah:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_ayah(self) -> None:
        url = f"{constants.AYAH}/2:255/quran-uthmani"
        route = respx.get(url).mock(return_value=Response(200, json=_ayah_payload()))

        result = await tools.quran_ayah(reference="2:255")

        assert route.called
        data = result["data"]
        assert isinstance(data, dict)
        assert data["numberInSurah"] == 255
        surah = data["surah"]
        assert isinstance(surah, dict)
        assert surah["englishName" if "englishName" in surah else "name"]

    @pytest.mark.asyncio
    async def test_empty_reference_returns_fail(self) -> None:
        result = await tools.quran_ayah(reference="")
        assert result["success"] is False
        assert "reference" in str(result["error"])


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
        data = result["data"]
        assert isinstance(data, dict)
        assert data["number"] == 1

    @pytest.mark.asyncio
    async def test_invalid_juz_returns_fail(self) -> None:
        result = await tools.quran_juz(number=31)
        assert result["success"] is False
        assert "juz number" in str(result["error"])


class TestQuranSearch:
    @pytest.mark.asyncio
    @respx.mock
    async def test_search_returns_matches(self) -> None:
        url = f"{constants.SEARCH}/Allah/all/en"
        route = respx.get(url).mock(return_value=Response(200, json=_search_payload()))

        result = await tools.quran_search(query="Allah")

        assert route.called
        data = result["data"]
        assert isinstance(data, dict)
        assert data["count"] == 1
        assert data["total"] == 1
        assert data["returned"] == 1
        assert data["offset"] == 0
        assert data["next_offset"] is None
        assert data["truncated"] is False
        matches = data["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1

    @pytest.mark.asyncio
    async def test_empty_query_returns_fail(self) -> None:
        result = await tools.quran_search(query="")
        assert result["success"] is False
        assert "query" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_high_cardinality_search_is_bounded_and_paginated(self) -> None:
        matches = [{"number": number, "text": f"match {number}"} for number in range(250)]
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": len(matches), "matches": matches},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah", limit=100, offset=100)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["total"] == 250
        assert data["returned"] == 100
        assert data["offset"] == 100
        assert data["next_offset"] == 200
        assert data["truncated"] is True
        page = data["matches"]
        assert isinstance(page, list)
        assert [match["number"] for match in page] == list(range(100, 200))

    @pytest.mark.asyncio
    @respx.mock
    async def test_default_search_limit_bounds_high_cardinality_results(self) -> None:
        matches = [{"number": number, "text": f"match {number}"} for number in range(250)]
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": len(matches), "matches": matches},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah")

        data = result["data"]
        assert isinstance(data, dict)
        assert data["returned"] == constants.DEFAULT_SEARCH_LIMIT
        assert data["next_offset"] == constants.DEFAULT_SEARCH_LIMIT
        page = data["matches"]
        assert isinstance(page, list)
        assert len(page) == constants.DEFAULT_SEARCH_LIMIT

    @pytest.mark.asyncio
    @respx.mock
    async def test_final_search_page_has_no_next_offset(self) -> None:
        matches = [{"number": number, "text": f"match {number}"} for number in range(250)]
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": len(matches), "matches": matches},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah", limit=100, offset=200)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["returned"] == 50
        assert data["next_offset"] is None
        assert data["truncated"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_offset_past_end_has_no_next_offset(self) -> None:
        matches = [{"number": number, "text": f"match {number}"} for number in range(10)]
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": len(matches), "matches": matches},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah", offset=20)

        data = result["data"]
        assert isinstance(data, dict)
        assert data["returned"] == 0
        assert data["matches"] == []
        assert data["next_offset"] is None
        assert data["truncated"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_mismatched_upstream_count_returns_fail(self) -> None:
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": 2, "matches": [{"number": 1}]},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah")

        assert result["success"] is False
        assert "count does not match" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_non_list_matches_returns_fail(self) -> None:
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": 1, "matches": {"number": 1}},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah")

        assert result["success"] is False
        assert "search matches is not a list" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("count", [True, -1, 1.5, "1"])
    async def test_invalid_upstream_count_returns_fail(self, count: object) -> None:
        payload = {
            "code": 200,
            "status": "OK",
            "data": {"count": count, "matches": [{"number": 1}]},
        }
        respx.get(f"{constants.SEARCH}/Allah/all/en").mock(return_value=Response(200, json=payload))

        result = await tools.quran_search(query="Allah")

        assert result["success"] is False
        assert "count is not a non-negative integer" in str(result["error"])

    @pytest.mark.asyncio
    @pytest.mark.parametrize("limit", [0, 101])
    async def test_invalid_limit_returns_fail(self, limit: int) -> None:
        result = await tools.quran_search(query="Allah", limit=limit)

        assert result["success"] is False
        assert "limit must be 1 to 100" in str(result["error"])

    @pytest.mark.asyncio
    async def test_negative_offset_returns_fail(self) -> None:
        result = await tools.quran_search(query="Allah", offset=-1)

        assert result["success"] is False
        assert "offset must be at least 0" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_user_values_are_encoded_as_path_segments(self) -> None:
        route = respx.get(f"{constants.SEARCH}/mercy%20%2F%20grace%3F/all/en%2Ftest").mock(
            return_value=Response(200, json=_search_payload())
        )

        result = await tools.quran_search(query="mercy / grace?", edition="en/test")

        assert result["success"] is True
        assert route.called


class TestQuranCloudClientValidation:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("limit", [0, constants.MAX_SEARCH_LIMIT + 1])
    async def test_rejects_invalid_limit_before_request(self, limit: int) -> None:
        with pytest.raises(ValueError, match="limit must be"):
            await QuranCloudClient().search("Allah", limit=limit)
        assert not respx.calls

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_negative_offset_before_request(self) -> None:
        with pytest.raises(ValueError, match="offset must be at least 0"):
            await QuranCloudClient().search("Allah", offset=-1)
        assert not respx.calls


class TestServerWrappers:
    @pytest.mark.asyncio
    async def test_quran_search_forwards_pagination(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from unittest.mock import AsyncMock

        from mcp_dubai.data.quran_cloud import server as quran_server

        expected: dict[str, object] = {"success": True, "data": {"matches": []}}
        search = AsyncMock(return_value=expected)
        monkeypatch.setattr(quran_server.tools, "quran_search", search)

        result = await quran_server.quran_search(
            query="mercy",
            surah="2",
            edition="en.sahih",
            limit=10,
            offset=20,
        )

        assert result == expected
        search.assert_awaited_once_with(
            query="mercy",
            surah="2",
            edition="en.sahih",
            limit=10,
            offset=20,
        )


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
