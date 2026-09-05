"""Tests for the makani feature (Dubai Municipality geo-addressing SOAP)."""

from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.constants import MAKANI_SOAP_ENDPOINT
from mcp_dubai.data.makani import tools


def _soap_envelope(operation: str, result: object) -> str:
    """Wrap a JSON result dict in a canned Makani SOAP 1.1 response envelope."""
    text = json.dumps(result, ensure_ascii=False)
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
        f'<{operation}Response xmlns="http://tempuri.org/">'
        f"<{operation}Result>{escaped}</{operation}Result>"
        f"</{operation}Response></s:Body></s:Envelope>"
    )


def _soap_response(operation: str, result: object) -> Response:
    return Response(
        200,
        text=_soap_envelope(operation, result),
        headers={"Content-Type": "text/xml; charset=utf-8"},
    )


# Fixtures based on live payloads captured from the service on 2026-07-02.
_REVERSE_GEOCODE_RESULT: dict[str, object] = {
    "COMMUNITY_E": "AL RIGGA - 119",
    "COMMUNITY_A": "الرقة - 119",
    "BLDG_NAME_E": "Dubai Municipality- Main Office",
    "BLDG_NAME_A": "بلدية دبي - المبنى الرئيسي",
    "EMIRATE_E": "DUBAI",
    "EMIRATE_A": "دبي",
    "MAKANI_INFO": [
        {
            "MAKANI": "30032 95320",
            "LATLNG": "25.26464,55.31217",
            "ENT_NAME_E": "",
            "ENT_NAME_A": "",
            "ENT_NO": " ",
            "MAKANI_CODE": "",
            "SHORT_URL": "https://www.makani.ae/q?l=E&m=30032 95320",
        },
        {
            "MAKANI": "30016 95350",
            "LATLNG": "25.26491,55.31201",
            "ENT_NAME_E": "",
            "ENT_NAME_A": "",
            "ENT_NO": " ",
            "MAKANI_CODE": "",
            "SHORT_URL": "https://www.makani.ae/q?l=E&m=30016 95350",
        },
    ],
}

_DETAILS_RESULT: dict[str, object] = {
    "MAKANI": "30032 95320",
    "MAKANI_INFO": [
        {
            "COMMUNITY_E": "AL RIGGA - 119",
            "COMMUNITY_A": "الرقة - 119",
            "ENT_NAME_E": "",
            "ENT_NAME_A": "",
            "ENT_NO": " ",
            "BLDG_NAME_E": "Dubai Municipality- Main Office",
            "BLDG_NAME_A": "بلدية دبي - المبنى الرئيسي",
            "EMIRATE_E": "DUBAI",
            "EMIRATE_A": "دبي",
            "MAKANI_CODE": "",
            "LATLNG": "25.26464,55.31217",
            "SHORT_URL": "https://www.makani.ae/q?l=E&m=30032 95320",
        }
    ],
}

_VALID_RESULT: dict[str, object] = {
    "MAKANI": "30032 95320",
    "IS_VALID": "true",
    "VALID": [{"EMIRATE_E": "DUBAI", "EMIRATE_A": "دبي"}],
}

_INVALID_RESULT: dict[str, object] = {
    "MAKANI": "11111 11111",
    "IS_VALID": "false",
    "VALID": [],
}


class TestMakaniReverseGeocode:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("payload", [None, [], {}, {"MAKANI_INFO": ["invalid"]}])
    async def test_invalid_reverse_payload_returns_upstream_error(self, payload: object) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("GetMakaniInfoFromCoord", payload)
        )

        result = await tools.makani_reverse_geocode(25.2, 55.3)

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_building_and_makani_numbers(self) -> None:
        route = respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("GetMakaniInfoFromCoord", _REVERSE_GEOCODE_RESULT)
        )

        result = await tools.makani_reverse_geocode(latitude=25.26464, longitude=55.31217)

        assert result["success"] is True
        assert result["source"] == "www.makani.ae"
        data = result["data"]
        assert isinstance(data, dict)
        building = data["building"]
        assert isinstance(building, dict)
        assert building["en"] == "Dubai Municipality- Main Office"
        assert building["ar"] == "بلدية دبي - المبنى الرئيسي"
        community = data["community"]
        assert isinstance(community, dict)
        assert community["en"] == "AL RIGGA - 119"
        emirate = data["emirate"]
        assert isinstance(emirate, dict)
        assert emirate["en"] == "DUBAI"
        numbers = data["makani_numbers"]
        assert isinstance(numbers, list)
        assert len(numbers) == 2
        first = numbers[0]
        assert first["makani"] == "30032 95320"
        assert first["latitude"] == 25.26464
        assert first["longitude"] == 55.31217
        assert first["short_url"] == "https://www.makani.ae/q?l=E&m=30032 95320"
        assert "Dubai Municipality" in str(data["attribution"])

        request_body = route.calls.last.request.content.decode()
        assert "<latitude>25.26464</latitude>" in request_body
        assert "<longitude>55.31217</longitude>" in request_body
        assert "<remarks>mcp-dubai</remarks>" in request_body
        soap_action = route.calls.last.request.headers["SOAPAction"]
        assert soap_action == '"http://tempuri.org/IMakaniPublic/GetMakaniInfoFromCoord"'

    @pytest.mark.asyncio
    async def test_out_of_range_latitude_fails_locally(self) -> None:
        result = await tools.makani_reverse_geocode(latitude=999.0, longitude=55.31)

        assert result["success"] is False
        assert "latitude" in str(result["error"])

    @pytest.mark.asyncio
    async def test_out_of_range_longitude_fails_locally(self) -> None:
        result = await tools.makani_reverse_geocode(latitude=25.2, longitude=-999.0)

        assert result["success"] is False
        assert "longitude" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_service_error_payload_returns_fail(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("GetMakaniInfoFromCoord", {"DATA": "Exception Occurred!!!"})
        )

        result = await tools.makani_reverse_geocode(latitude=51.5074, longitude=-0.1278)

        assert result["success"] is False
        assert "Exception Occurred" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.makani_reverse_geocode(latitude=25.26464, longitude=55.31217)

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestMakaniDetails:
    @pytest.mark.asyncio
    @respx.mock
    async def test_normalizes_number_and_returns_details(self) -> None:
        route = respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("GetMakaniDetails", _DETAILS_RESULT)
        )

        result = await tools.makani_details(makani_number="3003295320")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["makani"] == "30032 95320"
        building = data["building"]
        assert isinstance(building, dict)
        assert building["en"] == "Dubai Municipality- Main Office"
        assert building["ar"] == "بلدية دبي - المبنى الرئيسي"
        assert data["latitude"] == 25.26464
        assert data["longitude"] == 55.31217
        assert data["short_url"] == "https://www.makani.ae/q?l=E&m=30032 95320"
        assert "Dubai Municipality" in str(data["attribution"])

        request_body = route.calls.last.request.content.decode()
        assert "<makanino>30032 95320</makanino>" in request_body
        assert "<remarks>mcp-dubai</remarks>" in request_body

    @pytest.mark.asyncio
    async def test_wrong_length_number_fails_locally(self) -> None:
        result = await tools.makani_details(makani_number="12345")

        assert result["success"] is False
        assert "10 digits" in str(result["error"])

    @pytest.mark.asyncio
    async def test_non_digit_number_fails_locally(self) -> None:
        result = await tools.makani_details(makani_number="ABCDE12345")

        assert result["success"] is False
        assert "10 digits" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_unknown_number_returns_fail(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response(
                "GetMakaniDetails", {"MAKANI": "11111 11111", "MAKANI_INFO": []}
            )
        )

        result = await tools.makani_details(makani_number="11111 11111")

        assert result["success"] is False
        assert "11111 11111" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.makani_details(makani_number="30032 95320")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestMakaniValidate:
    @pytest.mark.asyncio
    @respx.mock
    @pytest.mark.parametrize("payload", [None, [], {}, {"IS_VALID": "unknown"}])
    async def test_invalid_payload_does_not_claim_number_is_invalid(self, payload: object) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(return_value=_soap_response("IsValidMakani", payload))

        result = await tools.makani_validate("30032 95320")

        assert result["success"] is False
        assert result["error"]["status"] == "upstream_error"

    @pytest.mark.asyncio
    @respx.mock
    async def test_valid_number_returns_emirate(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("IsValidMakani", _VALID_RESULT)
        )

        result = await tools.makani_validate(makani_number="30032 95320")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["makani"] == "30032 95320"
        assert data["is_valid"] is True
        emirate = data["emirate"]
        assert isinstance(emirate, dict)
        assert emirate["en"] == "DUBAI"
        assert emirate["ar"] == "دبي"
        assert "Dubai Municipality" in str(data["attribution"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_nonexistent_number_returns_is_valid_false(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("IsValidMakani", _INVALID_RESULT)
        )

        result = await tools.makani_validate(makani_number="1111111111")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["is_valid"] is False
        assert data["emirate"] is None

    @pytest.mark.asyncio
    async def test_malformed_number_fails_locally(self) -> None:
        result = await tools.makani_validate(makani_number="not-a-makani")

        assert result["success"] is False
        assert "10 digits" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_arabic_indic_digits_are_normalized(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("IsValidMakani", _VALID_RESULT)
        )

        result = await tools.makani_validate(makani_number="٣٠٠٣٢٩٥٣٢٠")

        assert result["success"] is True
        data = result["data"]
        assert isinstance(data, dict)
        assert data["makani"] == "30032 95320"

    def test_normalize_rejects_non_ascii_non_digit_input(self) -> None:
        # Superscript three: str.isdigit() is True but it is not a Makani digit.
        assert tools._normalize_makani("³0032 95320") is None
        assert tools._normalize_makani("٣٠٠٣٢ ٩٥٣٢٠") == "30032 95320"

    @pytest.mark.asyncio
    @respx.mock
    async def test_service_error_payload_returns_fail(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=_soap_response("IsValidMakani", {"DATA": "Invalid makani value!"})
        )

        result = await tools.makani_validate(makani_number="0000000000")

        assert result["success"] is False
        assert "Invalid makani value" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_rejects_doctype_after_long_prefix(self) -> None:
        malicious_xml = (
            " " * 2049
            + """<!DOCTYPE x [
<!ENTITY injected '{&quot;IS_VALID&quot;:&quot;true&quot;}'>
]>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <IsValidMakaniResponse xmlns="http://tempuri.org/">
      <IsValidMakaniResult>&injected;</IsValidMakaniResult>
    </IsValidMakaniResponse>
  </s:Body>
</s:Envelope>"""
        )
        respx.post(MAKANI_SOAP_ENDPOINT).mock(return_value=Response(200, text=malicious_xml))

        result = await tools.makani_validate(makani_number="30032 95320")

        assert result["success"] is False
        assert "declares a DTD" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_malformed_soap_returns_structured_error(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(
            return_value=Response(200, text="<s:Envelope><unclosed>")
        )

        result = await tools.makani_validate(makani_number="30032 95320")

        assert result["success"] is False
        assert "Malformed SOAP response" in str(result["error"])

    @pytest.mark.asyncio
    @respx.mock
    async def test_503_returns_structured_upstream_error(self) -> None:
        respx.post(MAKANI_SOAP_ENDPOINT).mock(return_value=Response(503, text="busy"))

        result = await tools.makani_validate(makani_number="30032 95320")

        assert result["success"] is False
        error = result["error"]
        assert isinstance(error, dict)
        assert error["status"] in {"upstream_blocked", "upstream_error"}


class TestDiscovery:
    def test_tools_registered(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.makani import server as makani_server

        importlib.reload(makani_server)
        names = {t.name for t in get_tool_discovery().get_by_feature("makani")}
        assert names == {"makani_reverse_geocode", "makani_details", "makani_validate"}

    def test_recommend_for_makani_query(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.makani import server as makani_server

        importlib.reload(makani_server)
        results = get_tool_discovery().recommend(
            "find the makani number address for a building in dubai", top_k=5
        )
        assert results
        assert any(r.feature == "makani" for r in results)
