"""open-meteo.com endpoints, UAE city coordinates, and WMO code map.

Open-Meteo is a free, keyless weather API. This feature fills the human
weather gap that `aviation_weather` (METAR / TAF for pilots) does not cover:
plain temperature, feels-like, humidity, wind, and a multi-day forecast for
the cities people actually live in.
"""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import OPEN_METEO_BASE

FORECAST_ENDPOINT: Final[str] = f"{OPEN_METEO_BASE}/forecast"

# The Open-Meteo `timezone` query value. Keeping it as a plain string (rather
# than the shared ZoneInfo object) because it travels over the wire.
TIMEZONE_NAME: Final[str] = "Asia/Dubai"

# Maximum daily forecast horizon Open-Meteo supports on the free tier.
MAX_FORECAST_DAYS: Final[int] = 16

# Current-conditions variables requested from Open-Meteo.
CURRENT_VARIABLES: Final[tuple[str, ...]] = (
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "is_day",
    "precipitation",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
)

# Daily forecast variables requested from Open-Meteo.
DAILY_VARIABLES: Final[tuple[str, ...]] = (
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "sunrise",
    "sunset",
    "uv_index_max",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
)

# UAE cities with (latitude, longitude). Keys are lowercased slugs.
UAE_CITIES: Final[dict[str, dict[str, object]]] = {
    "dubai": {"name": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
    "abu_dhabi": {"name": "Abu Dhabi", "latitude": 24.4539, "longitude": 54.3773},
    "sharjah": {"name": "Sharjah", "latitude": 25.3463, "longitude": 55.4209},
    "ajman": {"name": "Ajman", "latitude": 25.4052, "longitude": 55.5136},
    "ras_al_khaimah": {"name": "Ras Al Khaimah", "latitude": 25.7895, "longitude": 55.9432},
    "fujairah": {"name": "Fujairah", "latitude": 25.1288, "longitude": 56.3265},
    "umm_al_quwain": {"name": "Umm Al Quwain", "latitude": 25.5647, "longitude": 55.5532},
    "al_ain": {"name": "Al Ain", "latitude": 24.2075, "longitude": 55.7447},
}

# Free-text city spellings mapped to a canonical slug. Lowercased keys.
CITY_ALIASES: Final[dict[str, str]] = {
    "abudhabi": "abu_dhabi",
    "abu-dhabi": "abu_dhabi",
    "auh": "abu_dhabi",
    "dxb": "dubai",
    "rak": "ras_al_khaimah",
    "ras-al-khaimah": "ras_al_khaimah",
    "rak city": "ras_al_khaimah",
    "uaq": "umm_al_quwain",
    "shj": "sharjah",
}

# WMO weather interpretation codes mapped to a human description.
# Reference: https://open-meteo.com/en/docs (WMO Weather interpretation codes).
WMO_WEATHER_CODES: Final[dict[int, str]] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def describe_weather_code(code: object) -> str | None:
    """Map a WMO weather code to a human description, tolerating floats/None."""
    if isinstance(code, bool):
        return None
    if isinstance(code, float) and not code.is_integer():
        return None
    if isinstance(code, (int, float)):
        return WMO_WEATHER_CODES.get(int(code), "Unknown")
    return None


__all__ = [
    "FORECAST_ENDPOINT",
    "TIMEZONE_NAME",
    "MAX_FORECAST_DAYS",
    "CURRENT_VARIABLES",
    "DAILY_VARIABLES",
    "UAE_CITIES",
    "CITY_ALIASES",
    "WMO_WEATHER_CODES",
    "describe_weather_code",
]
