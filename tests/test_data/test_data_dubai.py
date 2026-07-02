"""Tests for data_dubai (credential-free catalog on data.dubai)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai.data.data_dubai import constants, tools

# Fixtures are trimmed-down copies of live payloads captured 2026-07-02
# from https://data.dubai/o/c/. The real items carry far more Liferay
# noise (actions maps, creator blocks, i18n duplicates); the fixtures keep
# just enough of it to prove the tools strip it out.


def _dataset_item() -> dict[str, object]:
    return {
        "actions": {"get": {"method": "GET", "href": "https://data.dubai/o/c/datasets/469745"}},
        "creator": {"contentType": "UserAccount", "id": 20123, "name": "Test Test"},
        "id": 469745,
        "externalReferenceCode": "03066e40-06e0-8259-a4b6-faf46814ffe9",
        "datasetName": "speed_and_radar_limits",
        "title": "Speed and Radar Limits",
        "title_i18n": {"ar_SA": "حدود السرعة والرادار", "en_US": "Speed and Radar Limits"},
        "description": "This dataset provides a guide to posted speed limits in Dubai.",
        "description_i18n": {
            "ar_SA": "تقدم هذه المجموعة بيانات إرشادية عن حدود السرعة المعلنة.",
            "en_US": "This dataset provides a guide to posted speed limits in Dubai.",
        },
        "themes": "Infrastructure",
        "themes_i18n": {"ar_SA": "البنية التحتية", "en_US": "Infrastructure"},
        "subthemes": "Transport and Mobility",
        "keywords": [],
        "format": "txt",
        "format_i18n": {"en_US": "txt"},
        "license": {"key": "NotSpecified", "name": "Not Specified"},
        "frequencyOfUpdateOnSource": "Upon transaction",
        "ingestionDate": "2025-10-07T13:45:00.000Z",
        "publishedDate": "2019-12-29T03:48:00.000Z",
        "dateModified": "2026-06-25T13:29:35Z",
        "viewCount": "58",
        "downloadCount": "14",
        "customViewCounts": 58,
        "customDownloadCount": 14,
        "datasetSource": "Traffic Dept",
        "r_issuingEntityOfDataset_c_issuingEntityERC": "d37c3329-f43e-794f-32a3-713234e197d8",
        "r_issuingEntityOfDataset_c_issuingEntityId": 268202,
        "dataAPIEndpoints": "https://apis.data.dubai/open/dp/dp_speed_and_radar_limits-open-api",
        "status": {"code": 0, "label": "approved", "label_i18n": "Approved"},
        "syncMetadataToLakehouse": True,
    }


def _search_payload() -> dict[str, object]:
    return {
        "actions": {"updateBatch": {"method": "PUT"}},
        "facets": [],
        "items": [_dataset_item()],
        "lastPage": 11,
        "page": 1,
        "pageSize": 2,
        "totalCount": 22,
    }


def _themes_payload() -> dict[str, object]:
    return {
        "facets": [],
        "items": [
            {
                "actions": {"get": {"method": "GET"}},
                "id": 3282906,
                "title": "Infrastructure",
                "title_i18n": {"ar_SA": "البنية التحتية", "en_US": "Infrastructure"},
                "description": "Data and insights on infrastructure.",
                "description_i18n": {
                    "ar_SA": "بيانات ورؤى حول البنية التحتية.",
                    "en_US": "Data and insights on infrastructure.",
                },
                "datasetCounts": "357",
                "dashboardURLWeb": "https://app.powerbi.com/view?r=abc",
            },
            {
                "id": 3282907,
                "title": "Population",
                "title_i18n": {"ar_SA": "السكان", "en_US": "Population"},
                "description": "",
                "description_i18n": {},
                "datasetCounts": "40",
            },
        ],
        "lastPage": 1,
        "page": 1,
        "pageSize": 100,
        "totalCount": 2,
    }


def _entities_payload() -> dict[str, object]:
    return {
        "facets": [],
        "items": [
            {
                "actions": {"get": {"method": "GET"}},
                "id": 267180,
                "key": "maf",
                "title": "Majid Al Futtaim",
                "title_i18n": {"ar_SA": " ماجد الفطيم", "en_US": "Majid Al Futtaim"},
                "description": "",
                "usages": "4",
                "externalReferenceCode": "d5158ad9-e63c-556b-84f5-33c99983cd3e",
            },
            {
                "id": 267181,
                "key": "rta",
                "title": "Roads and Transport Authority",
                "title_i18n": {"ar_SA": "هيئة الطرق والمواصلات"},
                "description": "",
                "usages": "120",
                "externalReferenceCode": "aaaa1111-2222-3333-4444-555566667777",
            },
        ],
        "lastPage": 1,
        "page": 1,
        "pageSize": 100,
        "totalCount": 2,
    }


class TestDataDubaiSearch:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_trimmed_datasets(self) -> None:
        route = respx.get(
            constants.DATASETS_ENDPOINT,
            params={"search": "traffic", "page": "1", "pageSize": "10"},
        ).mock(return_value=Response(200, json=_search_payload()))

        result = await tools.data_dubai_search(query="traffic", page=1, page_size=10)

        assert route.called
        assert result["success"] is True
        assert result["source"] == "data.dubai"
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 22
        assert data["last_page"] == 11
        datasets = data["datasets"]
        assert isinstance(datasets, list)
        dataset = datasets[0]
        assert dataset["id"] == 469745
        assert dataset["dataset_name"] == "speed_and_radar_limits"
        assert dataset["title"] == "Speed and Radar Limits"
        assert dataset["title_ar"] == "حدود السرعة والرادار"
        assert dataset["themes"] == "Infrastructure"
        assert dataset["license"] == "Not Specified"
        assert dataset["view_count"] == 58
        assert dataset["download_count"] == 14
        assert dataset["data_api_endpoint"] == (
            "https://apis.data.dubai/open/dp/dp_speed_and_radar_limits-open-api"
        )

    @pytest.mark.asyncio
    @respx.mock
    async def test_liferay_noise_stripped(self) -> None:
        respx.get(constants.DATASETS_ENDPOINT).mock(
            return_value=Response(200, json=_search_payload())
        )

        result = await tools.data_dubai_search(query="traffic")

        data = result["data"]
        assert isinstance(data, dict)
        datasets = data["datasets"]
        assert isinstance(datasets, list)
        dataset = datasets[0]
        assert isinstance(dataset, dict)
        for noise in ("actions", "creator", "status", "title_i18n", "syncMetadataToLakehouse"):
            assert noise not in dataset

    @pytest.mark.asyncio
    @respx.mock
    async def test_every_response_carries_metadata_only_note(self) -> None:
        respx.get(constants.DATASETS_ENDPOINT).mock(
            return_value=Response(200, json=_search_payload())
        )

        result = await tools.data_dubai_search()

        data = result["data"]
        assert isinstance(data, dict)
        note = str(data["note"])
        assert "METADATA ONLY" in note
        assert "401" in note
        assert "apis.data.dubai" in note

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_query_omits_search_param(self) -> None:
        route = respx.get(
            constants.DATASETS_ENDPOINT,
            params={"page": "1", "pageSize": "10"},
        ).mock(return_value=Response(200, json=_search_payload()))

        result = await tools.data_dubai_search(query="")

        assert route.called
        assert "search" not in str(route.calls[0].request.url)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_page_below_one_returns_fail(self) -> None:
        result = await tools.data_dubai_search(page=0)
        assert result["success"] is False
        assert "page" in str(result["error"])

    @pytest.mark.asyncio
    async def test_page_size_out_of_range_returns_fail(self) -> None:
        result = await tools.data_dubai_search(page_size=101)
        assert result["success"] is False
        assert "page_size" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDataDubaiThemes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_trimmed_themes(self) -> None:
        route = respx.get(constants.THEMES_ENDPOINT).mock(
            return_value=Response(200, json=_themes_payload())
        )

        result = await tools.data_dubai_themes()

        assert route.called
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 2
        themes = data["themes"]
        assert isinstance(themes, list)
        assert len(themes) == 2
        theme = themes[0]
        assert theme["title"] == "Infrastructure"
        assert theme["title_ar"] == "البنية التحتية"
        assert theme["dataset_count"] == 357
        assert "actions" not in theme
        assert "dashboardURLWeb" not in theme
        assert "METADATA ONLY" in str(data["note"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_arabic_title_is_none(self) -> None:
        respx.get(constants.THEMES_ENDPOINT).mock(
            return_value=Response(200, json=_themes_payload())
        )

        result = await tools.data_dubai_themes()

        data = result["data"]
        assert isinstance(data, dict)
        themes = data["themes"]
        assert isinstance(themes, list)
        assert themes[1]["description_ar"] is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_returns_failure(self) -> None:
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(500, text="boom"))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDataDubaiEntities:
    @pytest.mark.asyncio
    @respx.mock
    async def test_no_filter_returns_all(self) -> None:
        route = respx.get(
            constants.ISSUING_ENTITIES_ENDPOINT,
            params={"pageSize": "100"},
        ).mock(return_value=Response(200, json=_entities_payload()))

        result = await tools.data_dubai_entities()

        assert route.called
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 2
        assert data["matched_count"] == 2
        entities = data["entities"]
        assert isinstance(entities, list)
        entity = entities[0]
        assert entity["key"] == "maf"
        assert entity["title"] == "Majid Al Futtaim"
        assert entity["dataset_usages"] == 4
        assert "actions" not in entity
        assert "METADATA ONLY" in str(data["note"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_filter_matches_title_case_insensitive(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(
            return_value=Response(200, json=_entities_payload())
        )

        result = await tools.data_dubai_entities(search="ROADS AND transport")

        data = result["data"]
        assert isinstance(data, dict)
        assert data["matched_count"] == 1
        entities = data["entities"]
        assert isinstance(entities, list)
        assert entities[0]["key"] == "rta"

    @pytest.mark.asyncio
    @respx.mock
    async def test_filter_matches_short_key(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(
            return_value=Response(200, json=_entities_payload())
        )

        result = await tools.data_dubai_entities(search="maf")

        data = result["data"]
        assert isinstance(data, dict)
        assert data["matched_count"] == 1
        entities = data["entities"]
        assert isinstance(entities, list)
        assert entities[0]["title"] == "Majid Al Futtaim"

    @pytest.mark.asyncio
    @respx.mock
    async def test_filter_matches_arabic_title(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(
            return_value=Response(200, json=_entities_payload())
        )

        result = await tools.data_dubai_entities(search="هيئة الطرق")

        data = result["data"]
        assert isinstance(data, dict)
        assert data["matched_count"] == 1
        entities = data["entities"]
        assert isinstance(entities, list)
        assert entities[0]["key"] == "rta"

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_match_returns_empty_success(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(
            return_value=Response(200, json=_entities_payload())
        )

        result = await tools.data_dubai_entities(search="does-not-exist")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["matched_count"] == 0
        assert data["entities"] == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.data_dubai_entities()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.data_dubai import server as dd_server

        importlib.reload(dd_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("data_dubai")}
        assert names == {"data_dubai_search", "data_dubai_themes", "data_dubai_entities"}

    def test_recommend_for_open_data_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.data_dubai import server as dd_server

        importlib.reload(dd_server)
        results = get_tool_discovery().recommend("search dubai open data catalog datasets", top_k=5)
        assert results
        assert any(r.feature == "data_dubai" for r in results)
