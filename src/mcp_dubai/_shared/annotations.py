"""
Tool annotation middleware.

Every one of MCP-Dubai's tools is a read-only lookup: they query public APIs or
read curated JSON, and none of them writes, deletes, or transacts anything. The
MCP spec lets a server declare that with tool annotations, and clients use them
to decide whether a call needs a confirmation prompt. Without them a cautious
client has to assume the worst about all 120 tools.

Setting `annotations=` on each of the 120 `@mcp.tool` decorators would work but
means 120 near-identical edits that later contributors have to remember to
repeat. Applying them in one `on_list_tools` hook makes read-only the default
for the whole server, including tools mounted from sub-servers, so a new feature
inherits the correct annotations without doing anything.

The hints mean:

* `readOnlyHint=True`     -- the tool does not modify its environment.
* `destructiveHint=False` -- nothing is removed or overwritten.
* `idempotentHint=True`   -- calling twice with the same arguments is no
  different from calling once. Live upstreams may return fresher numbers, but
  the call itself has no cumulative effect.
* `openWorldHint`         -- whether the tool reaches a system outside this
  process. This is the one hint that genuinely differs per tool, so the
  network-calling tools are enumerated below.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastmcp.server.middleware import Middleware
from mcp.types import ToolAnnotations

# Tools that reach a live external upstream, so `openWorldHint=True`. Everything
# else answers from a bundled JSON pack, a curated snapshot, or pure arithmetic,
# and is therefore closed-world.
#
# This is an explicit list rather than something derived from the discovery
# registry, because that registry is a resettable singleton: anything reading it
# gets a different answer depending on when it is asked. A hardcoded set is
# reviewable in a diff, and `test_annotations.py` fails if a newly registered
# tool is missing from the classification entirely.
#
# Note the deliberate exclusions from `data/*`: `khda_*` reads a curated
# snapshot, `list_uae_weather_cities` and `osm_list_categories` return static
# vocabularies, `air_quality_dubai_stations` returns the curated station list,
# `rta_gtfs_static_url` returns a URL string without fetching it, and the
# holidays tools read a bundled calendar.
OPEN_WORLD_TOOLS: frozenset[str] = frozenset(
    {
        # air_quality (WAQI)
        "air_quality_by_coords",
        "air_quality_dubai",
        # al_adhan
        "gregorian_to_hijri",
        "hijri_to_gregorian",
        "prayer_times_calendar",
        "prayer_times_for",
        "qibla_direction",
        # aviation_weather (aviationweather.gov)
        "weather_uae_all",
        "weather_uae_icao",
        # cbuae (scraped)
        "cbuae_base_rate",
        "cbuae_exchange_rates",
        # currency
        "currency_convert",
        "currency_rates",
        # data_dubai
        "data_dubai_entities",
        "data_dubai_search",
        "data_dubai_themes",
        # dfm
        "dfm_index",
        "dfm_list_securities",
        "dfm_stock_quote",
        # dld (Dubai Pulse)
        "dld_lookup_broker",
        "dld_search_rent_contracts",
        "dld_search_transactions",
        # fcsc_ckan
        "fca_trade_stats",
        "fcsc_get_dataset",
        "fcsc_list_organizations",
        "fcsc_search_dataset",
        # gold_rate (scraped)
        "dubai_gold_rate",
        # makani
        "makani_details",
        "makani_reverse_geocode",
        "makani_validate",
        # open_meteo
        "uae_weather",
        "uae_weather_forecast",
        "weather_by_coords",
        # osm_overpass
        "osm_search_poi",
        # quran_cloud
        "quran_ayah",
        "quran_juz",
        "quran_search",
        "quran_surah",
        # rta (Dubai Pulse)
        "rta_salik_tariff",
        "rta_search_bus_routes",
        "rta_search_metro_stations",
    }
)


class ReadOnlyAnnotationMiddleware(Middleware):
    """
    Stamp read-only tool annotations onto every tool in `tools/list`.

    Only fills in annotations that a tool has not set for itself, so an
    individual tool can still override the defaults by passing
    `annotations=` to its decorator.
    """

    async def on_list_tools(self, context: Any, call_next: Any) -> Sequence[Any]:
        tools: Sequence[Any] = await call_next(context)
        for tool in tools:
            existing = getattr(tool, "annotations", None)
            if existing is not None and existing.readOnlyHint is not None:
                continue  # the tool declared its own annotations; leave them be
            tool.annotations = ToolAnnotations(
                title=getattr(existing, "title", None) if existing else None,
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=tool.name in OPEN_WORLD_TOOLS,
            )
        return tools
