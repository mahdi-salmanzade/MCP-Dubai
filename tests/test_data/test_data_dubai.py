"""Tests for data_dubai (credential-free catalog on data.dubai)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.constants import DATA_DUBAI_CATALOG_BASE, DUBAI_DATA_PORTAL_BASE
from mcp_dubai.data.data_dubai import client as client_module
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
    items: list[dict[str, object]] = []
    for offset in range(10):
        item = _dataset_item()
        item["id"] = 469745 + offset
        items.append(item)
    return {
        "actions": {"updateBatch": {"method": "PUT"}},
        "facets": [],
        "items": items,
        "lastPage": 3,
        "page": 1,
        "pageSize": 10,
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


def _page_payload(
    items: list[dict[str, object]],
    *,
    total_count: int,
    page: int,
    page_size: int = 100,
) -> dict[str, object]:
    """Build one internally consistent Liferay page for pagination tests."""
    return {
        "items": items,
        "lastPage": max(1, (total_count + page_size - 1) // page_size),
        "page": page,
        "pageSize": page_size,
        "totalCount": total_count,
    }


def _theme_item(identifier: int) -> dict[str, object]:
    return {
        "id": identifier,
        "title": f"Theme {identifier}",
        "title_i18n": {},
        "description": "",
        "description_i18n": {},
        "datasetCounts": "1",
    }


def _entity_item(identifier: int) -> dict[str, object]:
    return {
        "id": identifier,
        "key": f"entity-{identifier}",
        "title": f"Entity {identifier}",
        "title_i18n": {},
        "description": "",
        "usages": "1",
        "externalReferenceCode": f"erc-{identifier}",
    }


class TestDataDubaiConstants:
    def test_catalog_base_is_derived_from_configurable_portal_base(self) -> None:
        expected_catalog_base = f"{DUBAI_DATA_PORTAL_BASE.rstrip('/')}/o/c"
        assert expected_catalog_base == DATA_DUBAI_CATALOG_BASE

    def test_current_catalog_verification_totals(self) -> None:
        assert constants.CATALOG_VERIFIED_DATE == "2026-09-05"
        assert constants.DATASET_COUNT == 610
        assert constants.THEME_COUNT == 11
        assert constants.ISSUING_ENTITY_COUNT == 75


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
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["last_page"] == 3
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

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_items_is_structured_failure(self) -> None:
        respx.get(constants.DATASETS_ENDPOINT).mock(
            return_value=Response(200, json={"totalCount": 0})
        )

        result = await tools.data_dubai_search()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "items is not a list" in error["reason"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("items", "total_count", "page", "page_size", "reason"),
        [
            ([42], 1, 1, 10, "items contains a non-object"),
            ([{"id": 1}, {"id": 2}], 1, 1, 10, "totalCount is smaller than items"),
            ([{"id": 1}, {"id": 2}], 2, 1, 1, "items exceeds pageSize"),
            ([{"id": 1}], 1, 2, 10, "page after lastPage has items"),
        ],
    )
    @respx.mock
    async def test_invalid_page_envelope_is_structured_failure(
        self,
        items: list[object],
        total_count: int,
        page: int,
        page_size: int,
        reason: str,
    ) -> None:
        payload: dict[str, object] = {
            "items": items,
            "lastPage": max(1, (total_count + page_size - 1) // page_size),
            "page": page,
            "pageSize": page_size,
            "totalCount": total_count,
        }
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(
            query="traffic",
            page=page,
            page_size=page_size,
        )

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert reason in error["reason"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("field", ["page", "pageSize", "lastPage"])
    @respx.mock
    async def test_missing_pagination_field_is_structured_failure(self, field: str) -> None:
        payload = _search_payload()
        payload.pop(field)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert field in error["reason"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("field", "value", "reason"),
        [
            ("page", 2, "requested page 1"),
            ("pageSize", 9, "requested pageSize 10"),
            ("lastPage", 11, "lastPage"),
            ("page", True, "page is not an integer"),
        ],
    )
    @respx.mock
    async def test_inconsistent_pagination_is_structured_failure(
        self,
        field: str,
        value: object,
        reason: str,
    ) -> None:
        payload = _search_payload()
        payload[field] = value
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert reason in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_overflowing_last_page_is_structured_failure(self) -> None:
        body = b'{"totalCount":1,"page":1,"pageSize":10,"lastPage":1e1000,"items":[]}'
        respx.get(constants.DATASETS_ENDPOINT).mock(
            return_value=Response(200, content=body, headers={"content-type": "application/json"})
        )

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "lastPage" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_unfiltered_empty_envelope_is_failure(self) -> None:
        payload = _page_payload([], total_count=0, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "empty unfiltered catalog" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_filtered_zero_result_envelope_is_success(self) -> None:
        payload = _page_payload([], total_count=0, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="does-not-exist")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 0
        assert data["datasets"] == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_filtered_incomplete_page_is_structured_failure(self) -> None:
        payload = _page_payload([], total_count=1, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "should contain 1 items" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_zero_custom_counters_do_not_fall_back_to_legacy_values(self) -> None:
        item = _dataset_item()
        item["customViewCounts"] = 0
        item["viewCount"] = "58"
        item["customDownloadCount"] = 0
        item["downloadCount"] = "14"
        payload = _page_payload([item], total_count=1, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        data = result["data"]
        assert isinstance(data, dict)
        datasets = data["datasets"]
        assert isinstance(datasets, list)
        assert datasets[0]["view_count"] == 0
        assert datasets[0]["download_count"] == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_value", [True, "not-a-number", 1.5, -1])
    @respx.mock
    async def test_invalid_custom_counter_is_structured_failure(
        self,
        invalid_value: object,
    ) -> None:
        item = _dataset_item()
        item["customViewCounts"] = invalid_value
        payload = _page_payload([item], total_count=1, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "customViewCounts" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_null_custom_counters_fall_back_to_legacy_values(self) -> None:
        item = _dataset_item()
        item["customViewCounts"] = None
        item["viewCount"] = "58"
        item["customDownloadCount"] = None
        item["downloadCount"] = "14"
        payload = _page_payload([item], total_count=1, page=1, page_size=10)
        respx.get(constants.DATASETS_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_search(query="traffic")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        datasets = data["datasets"]
        assert isinstance(datasets, list)
        assert datasets[0]["view_count"] == 58
        assert datasets[0]["download_count"] == 14


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

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response_is_structured_failure(self) -> None:
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(204))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "Empty response" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_envelope_is_structured_failure(self) -> None:
        payload = _page_payload([], total_count=0, page=1)
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "empty themes catalog" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_counter_overflow_is_structured_failure(self) -> None:
        body = (
            b'{"totalCount":1,"page":1,"pageSize":100,"lastPage":1,'
            b'"items":[{"id":1,"datasetCounts":1e1000}]}'
        )
        respx.get(constants.THEMES_ENDPOINT).mock(
            return_value=Response(200, content=body, headers={"content-type": "application/json"})
        )

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "datasetCounts" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetches_every_theme_page(self) -> None:
        first_items = [_theme_item(identifier) for identifier in range(100)]
        second_items = [_theme_item(100)]
        first = respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "1", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(first_items, total_count=101, page=1),
            )
        )
        second = respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "2", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(second_items, total_count=101, page=2),
            )
        )

        result = await tools.data_dubai_themes()

        assert first.called and second.called
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 101
        themes = data["themes"]
        assert isinstance(themes, list)
        assert len(themes) == 101

    @pytest.mark.asyncio
    @respx.mock
    async def test_page_safety_limit_is_structured_failure(self) -> None:
        first_items = [_theme_item(identifier) for identifier in range(100)]
        payload = _page_payload(
            first_items,
            total_count=(constants.MAX_LIST_PAGES * constants.LIST_ALL_PAGE_SIZE) + 1,
            page=1,
        )
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "safety limit" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_repeated_item_across_pages_is_structured_failure(self) -> None:
        first_items = [_theme_item(identifier) for identifier in range(100)]
        repeated_item = _theme_item(0)
        respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "1", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(first_items, total_count=101, page=1),
            )
        )
        respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "2", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload([repeated_item], total_count=101, page=2),
            )
        )

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "Repeated item id" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_total_change_between_pages_is_structured_failure(self) -> None:
        first_items = [_theme_item(identifier) for identifier in range(100)]
        second_items = [_theme_item(100), _theme_item(101)]
        respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "1", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(first_items, total_count=101, page=1),
            )
        )
        respx.get(
            constants.THEMES_ENDPOINT,
            params={"page": "2", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(second_items, total_count=102, page=2),
            )
        )

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "changed totalCount" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_last_page_change_after_decode_is_structured_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        first = _page_payload(
            [_theme_item(identifier) for identifier in range(100)],
            total_count=101,
            page=1,
        )
        second = _page_payload([_theme_item(100)], total_count=101, page=2)
        second["lastPage"] = 3
        decoded_pages = iter([first, second])

        def fake_decode_page_envelope(*args: object, **kwargs: object) -> dict[str, object]:
            return next(decoded_pages)

        monkeypatch.setattr(client_module, "_decode_page_envelope", fake_decode_page_envelope)
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(200, json={}))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "changed lastPage" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_incomplete_decoded_pagination_is_structured_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        decoded_page = _page_payload([], total_count=1, page=1)

        def fake_decode_page_envelope(*args: object, **kwargs: object) -> dict[str, object]:
            return decoded_page

        monkeypatch.setattr(client_module, "_decode_page_envelope", fake_decode_page_envelope)
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(200, json={}))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "Incomplete pagination" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_item_id_is_structured_failure(self) -> None:
        item = _theme_item(1)
        item.pop("id")
        payload = _page_payload([item], total_count=1, page=1)
        respx.get(constants.THEMES_ENDPOINT).mock(return_value=Response(200, json=payload))

        result = await tools.data_dubai_themes()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "item id is missing or invalid" in error["reason"]


class TestDataDubaiEntities:
    @pytest.mark.asyncio
    @respx.mock
    async def test_no_filter_returns_all(self) -> None:
        route = respx.get(
            constants.ISSUING_ENTITIES_ENDPOINT,
            params={"page": "1", "pageSize": "100"},
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

    @pytest.mark.asyncio
    @respx.mock
    async def test_non_object_response_is_structured_failure(self) -> None:
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(return_value=Response(200, json=[]))

        result = await tools.data_dubai_entities()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "expected an object" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_envelope_is_structured_failure(self) -> None:
        payload = _page_payload([], total_count=0, page=1)
        respx.get(constants.ISSUING_ENTITIES_ENDPOINT).mock(
            return_value=Response(200, json=payload)
        )

        result = await tools.data_dubai_entities()

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert "empty issuing-entities catalog" in error["reason"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetches_every_entity_page_before_filtering(self) -> None:
        first_items = [_entity_item(identifier) for identifier in range(100)]
        second_items = [_entity_item(100)]
        first = respx.get(
            constants.ISSUING_ENTITIES_ENDPOINT,
            params={"page": "1", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(first_items, total_count=101, page=1),
            )
        )
        second = respx.get(
            constants.ISSUING_ENTITIES_ENDPOINT,
            params={"page": "2", "pageSize": "100"},
        ).mock(
            return_value=Response(
                200,
                json=_page_payload(second_items, total_count=101, page=2),
            )
        )

        result = await tools.data_dubai_entities(search="Entity 100")

        assert first.called and second.called
        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["total_count"] == 101
        assert data["matched_count"] == 1
        entities = data["entities"]
        assert isinstance(entities, list)
        assert entities[0]["key"] == "entity-100"


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
