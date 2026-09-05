"""Confirmed RTA dataset slugs on Dubai Pulse (now the data.dubai gateway)."""

from __future__ import annotations

from typing import Final

RTA_ORG: Final[str] = "rta"

DATASETS: Final[dict[str, str]] = {
    "metro_stations": "rta_metro_stations-open-api",
    "bus_routes": "rta_bus_routes-open-api",
    "tram_stations": "rta_tram_stations-open-api",
    "taxi": "rta_taxi-open-api",
    "marine_transport": "rta_marine_transport-open-api",
    "salik_tariff": "rta_salik_tariff-open-api",
    "gtfs_static": "rta_gtfs-open",
}

# DEAD as of 2026: Transitland now requires an API token (HTTP 401) and its
# archived Dubai feed versions date from 2021. Kept for reference only; use
# RTA_GTFS_DOWNLOAD_URL from mcp_dubai._shared.constants instead.
GTFS_TRANSITLAND_MIRROR_DEAD: Final[str] = "https://gtfs-source-feeds.transit.land/dubai-rta.zip"

# GTFS feed build inside the anonymous 7z download, rechecked 2026-09-05.
GTFS_FEED_VERSION: Final[str] = "GTFS_20250823"
GTFS_FEED_VERSION_CHECKED: Final[str] = "2026-09-05"

# Salik VAT: from 2026-06-01 a 5% VAT applies to toll crossings and tag
# activation fees (Salik PJSC announcement, 2026-05-22). The dataset rows
# may still carry pre-VAT base amounts, so tools surface this note.
SALIK_VAT_NOTE: Final[dict[str, object]] = {
    "vat_rate": 0.05,
    "effective_date": "2026-06-01",
    "standard_crossing_aed_incl_vat": 4.20,
    "peak_crossing_aed_incl_vat": 6.30,
    "note": (
        "From 2026-06-01 a 5% VAT applies to Salik toll crossings and toll "
        "tag activation fees. The standard AED 4 gate fee is AED 4.20 "
        "VAT-inclusive, and the dynamic-pricing peak AED 6 fee is AED 6.30 "
        "VAT-inclusive. Tariff dataset rows may still show pre-VAT base "
        "amounts."
    ),
    "ramadan_precedent": (
        "During Ramadan 2026 the toll-free window was extended to 2am-7am "
        "(normally 1am-6am) with peak pricing 9am-5pm; a similar shift is "
        "expected each Ramadan."
    ),
    "source_urls": [
        "https://www.salik.ae/en/news/Salik-to-Apply-VAT-on-Toll-Tariffs-Starting-1-June-2026",
        "https://www.khaleejtimes.com/uae/transport/salik-announces-5-vat-from-june-1-on-toll-tariff-tag-activation",
    ],
}

# Context notes for metro lines that are approved or under construction but
# NOT yet in the stations dataset. Do not treat these as served stations.
METRO_LINE_NOTES: Final[dict[str, str]] = {
    "blue_line": (
        "Under construction (about 20% complete as of May 2026, tunnelling "
        "started May 2026): 30 km, 14 stations, opening 2029-09-09. Not in "
        "the stations dataset yet."
    ),
    "gold_line": (
        "Approved April 2026: 42 km, 18 stations, fully underground, Al "
        "Ghubaiba to Jumeirah Golf Estates, opening 2032-09-09. Not in the "
        "stations dataset yet."
    ),
}
