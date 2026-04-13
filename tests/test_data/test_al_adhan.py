"""
Tests for the al_adhan feature.

Real Al-Adhan response shapes captured from
https://api.aladhan.com/v1/timingsByCity?city=Dubai&country=United+Arab+Emirates&method=8
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from mcp_dubai._shared.http_client import RateLimitError
from mcp_dubai.data.al_adhan import constants, tools

# ----------------------------------------------------------------------------
# Fixture builders
# ----------------------------------------------------------------------------


def _timings_payload() -> dict[str, object]:
    """A representative /timingsByCity payload (UAE, method 8)."""
    return {
        "code": 200,
        "status": "OK",
        "data": {
            "timings": {
                "Fajr": "05:12",
                "Sunrise": "06:34",
                "Dhuhr": "12:23",
                "Asr": "15:44",
                "Sunset": "18:12",
                "Maghrib": "18:12",
                "Isha": "19:32",
                "Imsak": "05:02",
                "Midnight": "00:23",
                "Firstthird": "21:30",
                "Lastthird": "03:00",
            },
            "date": {
                "readable": "12 Apr 2026",
                "timestamp": "1776146400",
                "hijri": {
                    "date": "23-10-1447",
                    "day": "23",
                    "month": {"number": 10, "en": "Shawwāl", "ar": "شَوَّال"},
                    "year": "1447",
                    "designation": {"abbreviated": "AH", "expanded": "Anno Hegirae"},
                    "weekday": {"en": "Al Ahad", "ar": "الأحد"},
                    "holidays": [],
                },
                "gregorian": {
                    "date": "12-04-2026",
                    "day": "12",
                    "month": {"number": 4, "en": "April"},
                    "year": "2026",
                    "designation": {"abbreviated": "AD", "expanded": "Anno Domini"},
                    "weekday": {"en": "Sunday"},
                },
            },
            "meta": {
                "latitude": 25.2048,
                "longitude": 55.2708,
                "timezone": "Asia/Dubai",
                "method": {"id": 8, "name": "Gulf Region"},
                "school": "STANDARD",
            },
        },
    }


def _qibla_payload(lat: float, lon: float, direction: float) -> dict[str, object]:
    return {
        "code": 200,
        "status": "OK",
        "data": {"latitude": lat, "longitude": lon, "direction": direction},
    }


def _date_conversion_payload() -> dict[str, object]:
    return {
        "code": 200,
        "status": "OK",
        "data": {
            "hijri": {
                "date": "23-10-1447",
                "day": "23",
                "month": {"number": 10, "en": "Shawwāl", "ar": "شَوَّال"},
                "year": "1447",
                "designation": {"abbreviated": "AH", "expanded": "Anno Hegirae"},
            },
            "gregorian": {
                "date": "12-04-2026",
                "day": "12",
                "month": {"number": 4, "en": "April"},
                "year": "2026",
                "designation": {"abbreviated": "AD", "expanded": "Anno Domini"},
            },
        },
    }


# ----------------------------------------------------------------------------
# prayer_times_for
# ----------------------------------------------------------------------------


class TestPrayerTimesFor:
    @pytest.mark.asyncio
    @respx.mock
    async def test_by_city_returns_timings(self) -> None:
        route = respx.get(constants.TIMINGS_BY_CITY).mock(
            return_value=Response(200, json=_timings_payload())
        )

        result = await tools.prayer_times_for(city="Dubai", country="United Arab Emirates")

        assert route.called
        # The upstream gets snake_case after parsing through PrayerTimes aliases.
        assert result["timings"]["fajr"] == "05:12"
        assert result["timings"]["maghrib"] == "18:12"
        assert result["timings"]["isha"] == "19:32"
        # Date envelope is preserved.
        assert result["date"]["hijri"]["year"] == "1447"
        assert result["date"]["gregorian"]["year"] == "2026"
        # Meta is passed through as a plain dict.
        assert result["meta"]["timezone"] == "Asia/Dubai"

    @pytest.mark.asyncio
    @respx.mock
    async def test_by_city_sends_method_and_school_params(self) -> None:
        route = respx.get(constants.TIMINGS_BY_CITY).mock(
            return_value=Response(200, json=_timings_payload())
        )

        await tools.prayer_times_for(
            city="Dubai", country="United Arab Emirates", method=16, school=1
        )

        params = route.calls.last.request.url.params
        assert params["city"] == "Dubai"
        assert params["country"] == "United Arab Emirates"
        assert params["method"] == "16"
        assert params["school"] == "1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_by_coords_calls_timings_endpoint(self) -> None:
        route = respx.get(constants.TIMINGS).mock(
            return_value=Response(200, json=_timings_payload())
        )

        result = await tools.prayer_times_for(latitude=25.2048, longitude=55.2708)

        assert route.called
        params = route.calls.last.request.url.params
        assert params["latitude"] == "25.2048"
        assert params["longitude"] == "55.2708"
        assert result["timings"]["fajr"] == "05:12"

    @pytest.mark.asyncio
    @respx.mock
    async def test_with_explicit_date_formats_ddmmyyyy(self) -> None:
        route = respx.get(constants.TIMINGS_BY_CITY).mock(
            return_value=Response(200, json=_timings_payload())
        )

        await tools.prayer_times_for(city="Dubai", date_str="2026-04-12")

        params = route.calls.last.request.url.params
        assert params["date"] == "12-04-2026"

    @pytest.mark.asyncio
    async def test_no_city_no_coords_raises(self) -> None:
        with pytest.raises(ValueError, match=r"city.*latitude"):
            await tools.prayer_times_for()

    @pytest.mark.asyncio
    async def test_partial_coords_raises(self) -> None:
        with pytest.raises(ValueError, match="together"):
            await tools.prayer_times_for(latitude=25.2048)

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_propagates_as_rate_limit_error(self) -> None:
        respx.get(constants.TIMINGS_BY_CITY).mock(
            return_value=Response(429, text="Too Many Requests")
        )

        with pytest.raises(RateLimitError):
            await tools.prayer_times_for(city="Dubai")


# ----------------------------------------------------------------------------
# prayer_times_calendar
# ----------------------------------------------------------------------------


class TestPrayerTimesCalendar:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_list_of_days(self) -> None:
        # Calendar payload is the timings shape repeated, one entry per day.
        day_data = _timings_payload()["data"]
        calendar_payload = {
            "code": 200,
            "status": "OK",
            "data": [day_data, day_data, day_data],
        }
        route = respx.get(constants.CALENDAR_BY_CITY).mock(
            return_value=Response(200, json=calendar_payload)
        )

        result = await tools.prayer_times_calendar(city="Dubai", month=4, year=2026)

        assert route.called
        params = route.calls.last.request.url.params
        assert params["month"] == "4"
        assert params["year"] == "2026"
        assert len(result) == 3
        assert result[0]["timings"]["fajr"] == "05:12"

    @pytest.mark.asyncio
    async def test_invalid_month_raises(self) -> None:
        with pytest.raises(ValueError, match="month must be 1 to 12"):
            await tools.prayer_times_calendar(city="Dubai", month=13, year=2026)

    @pytest.mark.asyncio
    async def test_invalid_year_raises(self) -> None:
        with pytest.raises(ValueError, match="year must"):
            await tools.prayer_times_calendar(city="Dubai", month=4, year=10000)


# ----------------------------------------------------------------------------
# qibla_direction
# ----------------------------------------------------------------------------


class TestQiblaDirection:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_direction_for_dubai(self) -> None:
        # Mecca is roughly west-southwest from Dubai, around 258 degrees.
        route = respx.get(f"{constants.QIBLA}/25.2048/55.2708").mock(
            return_value=Response(200, json=_qibla_payload(25.2048, 55.2708, 258.42))
        )

        result = await tools.qibla_direction(latitude=25.2048, longitude=55.2708)

        assert route.called
        assert result["direction"] == pytest.approx(258.42)
        assert result["latitude"] == pytest.approx(25.2048)
        assert 250 < result["direction"] < 270  # roughly Mecca-ward from Dubai

    @pytest.mark.asyncio
    async def test_invalid_latitude_raises(self) -> None:
        with pytest.raises(ValueError, match="latitude must"):
            await tools.qibla_direction(latitude=91.0, longitude=55.0)

    @pytest.mark.asyncio
    async def test_invalid_longitude_raises(self) -> None:
        with pytest.raises(ValueError, match="longitude must"):
            await tools.qibla_direction(latitude=25.0, longitude=181.0)


# ----------------------------------------------------------------------------
# hijri_to_gregorian / gregorian_to_hijri
# ----------------------------------------------------------------------------


class TestDateConversion:
    @pytest.mark.asyncio
    @respx.mock
    async def test_hijri_to_gregorian(self) -> None:
        route = respx.get(f"{constants.HIJRI_TO_GREGORIAN}/23-10-1447").mock(
            return_value=Response(200, json=_date_conversion_payload())
        )

        result = await tools.hijri_to_gregorian(day=23, month=10, year=1447)

        assert route.called
        assert result["gregorian"]["year"] == "2026"
        assert result["gregorian"]["date"] == "12-04-2026"
        assert result["hijri"]["year"] == "1447"

    @pytest.mark.asyncio
    @respx.mock
    async def test_gregorian_to_hijri(self) -> None:
        route = respx.get(f"{constants.GREGORIAN_TO_HIJRI}/12-04-2026").mock(
            return_value=Response(200, json=_date_conversion_payload())
        )

        result = await tools.gregorian_to_hijri(day=12, month=4, year=2026)

        assert route.called
        assert result["hijri"]["year"] == "1447"
        assert result["hijri"]["date"] == "23-10-1447"

    @pytest.mark.asyncio
    async def test_hijri_invalid_day(self) -> None:
        with pytest.raises(ValueError, match="day must be 1 to 30"):
            await tools.hijri_to_gregorian(day=31, month=10, year=1447)

    @pytest.mark.asyncio
    async def test_gregorian_invalid_month(self) -> None:
        with pytest.raises(ValueError, match="month must be 1 to 12"):
            await tools.gregorian_to_hijri(day=12, month=13, year=2026)


# ----------------------------------------------------------------------------
# Discovery integration
# ----------------------------------------------------------------------------


class TestDiscoveryRegistration:
    """al_adhan should register all 5 tools with ToolDiscovery on import."""

    def test_all_tools_registered(self) -> None:
        # Re-import the server module to trigger registration. The
        # autouse `reset_singletons` fixture clears state between tests, so
        # we have to import here.
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.al_adhan import server as al_adhan_server

        importlib.reload(al_adhan_server)

        discovery = get_tool_discovery()
        names = {t.name for t in discovery.get_by_feature("al_adhan")}
        assert names == {
            "prayer_times_for",
            "prayer_times_calendar",
            "qibla_direction",
            "hijri_to_gregorian",
            "gregorian_to_hijri",
        }

    def test_recommend_surfaces_prayer_times(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.al_adhan import server as al_adhan_server

        importlib.reload(al_adhan_server)

        discovery = get_tool_discovery()
        results = discovery.recommend("when is fajr prayer in dubai marina", top_k=3)
        assert results, "expected at least one recommendation"
        assert results[0].name == "prayer_times_for"

    def test_recommend_surfaces_qibla(self) -> None:
        import importlib

        from mcp_dubai._shared.discovery import get_tool_discovery
        from mcp_dubai.data.al_adhan import server as al_adhan_server

        importlib.reload(al_adhan_server)

        discovery = get_tool_discovery()
        results = discovery.recommend("compass direction to mecca", top_k=3)
        assert results
        assert results[0].name == "qibla_direction"
