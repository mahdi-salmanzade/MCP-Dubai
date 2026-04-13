"""Overpass API base and common amenity tags."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import OVERPASS_BASE

OVERPASS_ENDPOINT: Final[str] = OVERPASS_BASE

# Common POI categories mapped to OSM tag selectors. Each entry uses
# the canonical OSM key=value selector that the user is most likely to
# want when asking "find X near me".
COMMON_POI_TAGS: Final[dict[str, list[str]]] = {
    "restaurant": ["amenity=restaurant"],
    "cafe": ["amenity=cafe"],
    "fast_food": ["amenity=fast_food"],
    "pharmacy": ["amenity=pharmacy"],
    "hospital": ["amenity=hospital"],
    "clinic": ["amenity=clinic"],
    "atm": ["amenity=atm"],
    "bank": ["amenity=bank"],
    "fuel": ["amenity=fuel"],
    "school": ["amenity=school"],
    "kindergarten": ["amenity=kindergarten"],
    "mosque": ["amenity=place_of_worship", "religion=muslim"],
    "supermarket": ["shop=supermarket"],
    "mall": ["shop=mall"],
    "bus_stop": ["highway=bus_stop"],
    "metro_station": ["railway=station", "station=subway"],
    "parking": ["amenity=parking"],
    "park": ["leisure=park"],
    "gym": ["leisure=fitness_centre"],
    "hotel": ["tourism=hotel"],
    "embassy": ["amenity=embassy"],
    "post_office": ["amenity=post_office"],
}

DEFAULT_RADIUS_METERS: Final[int] = 1000
MAX_RADIUS_METERS: Final[int] = 10000
DEFAULT_LIMIT: Final[int] = 25
