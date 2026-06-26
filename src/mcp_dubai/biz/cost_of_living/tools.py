"""cost_of_living tool functions."""

from __future__ import annotations

from typing import Any

from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai._shared.schemas import KnowledgeMetadata, ToolResponse
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("cost_of_living.json")
KNOWLEDGE: KnowledgeMetadata = extract_knowledge(_DATA)
register_domain_knowledge("cost_of_living", KNOWLEDGE)


def _block(name: str) -> dict[str, Any]:
    item = _DATA.get(name, {})
    return item if isinstance(item, dict) else {}


VALID_BEDROOMS = ("studio", "1BR", "2BR")
VALID_UNIT_SIZES = ("studio", "1BR", "2BR", "3BR")
VALID_SEASONS = ("summer", "winter")
VALID_HOUSEHOLDS = ("single", "couple", "family_of_four")
VALID_STAGES = ("foundation_primary", "primary", "secondary")


def _fail(error: str) -> dict[str, object]:
    return ToolResponse[dict[str, object]].fail(error=error).model_dump()


def _ok(data: dict[str, object]) -> dict[str, object]:
    return ToolResponse[dict[str, object]].ok(data, knowledge=KNOWLEDGE).model_dump()


def _resolve_area(area: str) -> str | None:
    """Resolve an area name case-insensitively to its canonical JSON key."""
    areas = _block("rents").get("areas", {})
    if not isinstance(areas, dict):
        return None
    target = area.strip().lower()
    for key in areas:
        if str(key).lower() == target:
            return str(key)
    return None


async def cost_of_living_overview() -> dict[str, object]:
    """Headline ranges across every block plus a sample monthly budget."""
    rents = _block("rents")
    utilities = _block("utilities")
    groceries = _block("groceries")
    transport = _block("transport")
    schooling = _block("schooling")

    bills = utilities.get("typical_monthly_bill_aed", {})
    grocery_monthly = groceries.get("monthly_aed", {})
    nol = transport.get("nol", {})
    monthly_pass = nol.get("monthly_pass_aed", {})

    # Rough monthly rent figures derived from the citywide / area ranges,
    # using the lower bound of representative units so the budget stays
    # conservative. These are deliberately ballpark.
    rent_single_monthly = [45000 // 12, 75000 // 12]  # studio in a mid area
    rent_couple_monthly = [75000 // 12, 115000 // 12]  # 1BR
    rent_family_monthly = [110000 // 12, 170000 // 12]  # 2BR

    def _budget(
        rent: list[int],
        unit_key: str,
        grocery_key: str,
        transport_cost: int,
    ) -> dict[str, object]:
        util = bills.get(unit_key, [0, 0])
        groc = grocery_monthly.get(grocery_key, [0, 0])
        low = rent[0] + int(util[0]) + int(groc[0]) + transport_cost
        high = rent[1] + int(util[1]) + int(groc[1]) + transport_cost
        return {
            "rent_aed": rent,
            "utilities_aed": util,
            "groceries_aed": groc,
            "transport_aed": transport_cost,
            "total_monthly_aed": [low, high],
        }

    sample_budget = {
        "single": _budget(
            rent_single_monthly, "studio", "single", int(monthly_pass.get("one_zone", 140))
        ),
        "couple": _budget(
            rent_couple_monthly, "1BR", "couple", int(monthly_pass.get("two_adjacent", 230))
        ),
        "family_of_four": _budget(
            rent_family_monthly,
            "2BR",
            "family_of_four",
            int(monthly_pass.get("all_zones", 350)),
        ),
    }

    return _ok(
        {
            "currency": _DATA.get("currency", "AED"),
            "rents": {
                "citywide_1br_average_aed": rents.get("citywide_1br_average_aed"),
                "yoy_growth_note": rents.get("yoy_growth_note"),
                "areas_covered": sorted(rents.get("areas", {}).keys()),
            },
            "utilities": {
                "typical_monthly_bill_aed": bills,
                "housing_fee": utilities.get("housing_fee"),
            },
            "groceries": {"monthly_aed": grocery_monthly},
            "transport": {
                "nol_monthly_pass_aed": monthly_pass,
                "salik_peak_toll_aed": transport.get("salik", {}).get("peak_toll_aed"),
                "salik_off_peak_toll_aed": transport.get("salik", {}).get("off_peak_toll_aed"),
            },
            "schooling": {
                "british_curriculum_annual_aed": schooling.get("british_curriculum_annual_aed"),
            },
            "sample_monthly_budget_aed": sample_budget,
            "budget_note": (
                "Sample budgets are ballpark: rough rent (lower-bound units) plus "
                "utilities, groceries, and a Nol monthly pass. They exclude school "
                "fees, healthcare, and discretionary spend."
            ),
        }
    )


async def rent_estimate(
    area: str = "Dubai Marina",
    bedrooms: str = "1BR",
) -> dict[str, object]:
    """Resolve area and bedroom key and return the matching annual rent range."""
    rents = _block("rents")
    areas = rents.get("areas", {})
    valid_areas = sorted(areas.keys()) if isinstance(areas, dict) else []

    canonical = _resolve_area(area)
    if canonical is None:
        return _fail(
            f"Unknown area {area!r}. Valid areas: {valid_areas}. "
            f"Valid bedrooms: {list(VALID_BEDROOMS)}."
        )
    if bedrooms not in VALID_BEDROOMS:
        return _fail(f"Unknown bedrooms {bedrooms!r}. Valid bedrooms: {list(VALID_BEDROOMS)}.")

    area_data = areas[canonical]
    if bedrooms not in area_data:
        available = [b for b in VALID_BEDROOMS if b in area_data]
        return _fail(
            f"No {bedrooms} data for {canonical!r}. Available bedrooms there: {available}."
        )

    return _ok(
        {
            "area": canonical,
            "bedrooms": bedrooms,
            "annual_rent_aed": area_data[bedrooms],
            "unit": "annual_aed",
            "citywide_1br_average_aed": rents.get("citywide_1br_average_aed"),
            "yoy_growth_note": rents.get("yoy_growth_note"),
            "source_urls": rents.get("source_urls", []),
        }
    )


async def dewa_bill_estimate(
    unit_size: str = "1BR",
    season: str = "summer",
) -> dict[str, object]:
    """Return the typical monthly DEWA bill for a unit size, plus housing fee and slabs."""
    if unit_size not in VALID_UNIT_SIZES:
        return _fail(f"Unknown unit_size {unit_size!r}. Valid: {list(VALID_UNIT_SIZES)}.")
    if season not in VALID_SEASONS:
        return _fail(f"Unknown season {season!r}. Valid: {list(VALID_SEASONS)}.")

    utilities = _block("utilities")
    bills = utilities.get("typical_monthly_bill_aed", {})
    bill_range = bills.get(unit_size)

    season_note = (
        bills.get("note")
        if season == "summer"
        else (
            "Winter bills are the lower end of typical ranges because AC load "
            "drops sharply outside summer."
        )
    )

    return _ok(
        {
            "unit_size": unit_size,
            "season": season,
            "typical_monthly_bill_aed": bill_range,
            "season_note": season_note,
            "housing_fee": utilities.get("housing_fee"),
            "electricity_slabs_fils_per_kwh": utilities.get("electricity_slabs_fils_per_kwh", []),
            "electricity_slab_note": utilities.get("electricity_slab_note"),
            "water_first_slab_aed_per_imperial_gallon": utilities.get(
                "water_first_slab_aed_per_imperial_gallon"
            ),
            "sewerage_rule": utilities.get("sewerage_rule"),
            "vat_pct": utilities.get("vat_pct"),
            "fuel_surcharge_note": utilities.get("fuel_surcharge_note"),
            "source_urls": utilities.get("source_urls", []),
        }
    )


def _parse_hhmm(value: str) -> int | None:
    """Parse HH:MM into minutes since midnight, or None if malformed."""
    parts = value.strip().split(":")
    if len(parts) != 2:
        return None
    hh, mm = parts
    if not (hh.isdigit() and mm.isdigit()):
        return None
    hours = int(hh)
    minutes = int(mm)
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        return None
    return hours * 60 + minutes


# Salik windows expressed as [start_minute, end_minute) ranges. Windows that
# cross midnight are split into two ranges.
_FREE_RANGES = [(60, 360)]  # 01:00-06:00
_PEAK_RANGES = [(360, 600), (960, 1200)]  # 06:00-10:00, 16:00-20:00
_OFF_PEAK_RANGES = [(600, 960), (1200, 1440), (0, 60)]  # 10:00-16:00, 20:00-01:00


def _in_ranges(minute: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= minute < end for start, end in ranges)


async def salik_toll_estimate(
    time_of_day: str = "08:00",
    day: str = "weekday",
) -> dict[str, object]:
    """Deterministic Salik toll for a HH:MM time using the official windows."""
    minute = _parse_hhmm(time_of_day)
    if minute is None:
        return _fail(f"Invalid time_of_day {time_of_day!r}. Use 24-hour HH:MM, e.g. '08:00'.")

    salik = _block("transport").get("salik", {})

    in_free = _in_ranges(minute, _FREE_RANGES)

    if in_free:
        toll = int(salik.get("free_toll_aed", 0))
        window = "free (01:00-06:00)"
    elif day == "sunday":
        toll = int(salik.get("sunday_flat_aed", 4))
        window = "sunday flat"
    elif _in_ranges(minute, _PEAK_RANGES):
        toll = int(salik.get("peak_toll_aed", 6))
        window = "peak"
    else:
        toll = int(salik.get("off_peak_toll_aed", 4))
        window = "off-peak"

    return _ok(
        {
            "time_of_day": time_of_day,
            "day": day,
            "toll_aed": toll,
            "window_applied": window,
            "peak_windows": salik.get("peak_windows", []),
            "off_peak_windows": salik.get("off_peak_windows", []),
            "free_window": salik.get("free_window"),
            "sunday_note": salik.get("sunday_note"),
            "ramadan_peak_window": salik.get("ramadan_peak_window"),
            "twin_gate_note": salik.get("twin_gate_note"),
            "source_urls": salik.get("source_urls", []),
        }
    )


async def grocery_estimate(household_size: str = "single") -> dict[str, object]:
    """Grocery monthly and weekly ranges for a household plus the staples basket."""
    if household_size not in VALID_HOUSEHOLDS:
        return _fail(f"Unknown household_size {household_size!r}. Valid: {list(VALID_HOUSEHOLDS)}.")

    groceries = _block("groceries")
    monthly = groceries.get("monthly_aed", {})
    weekly = groceries.get("weekly_aed", {})

    return _ok(
        {
            "household_size": household_size,
            "monthly_aed": monthly.get(household_size),
            "weekly_aed": weekly.get(household_size),
            "branded_imported_monthly_aed": (
                monthly.get("single_branded_imported") if household_size == "single" else None
            ),
            "staples_aed": groceries.get("staples_aed", {}),
            "chain_price_tiers": groceries.get("chain_price_tiers", []),
            "source_urls": groceries.get("source_urls", []),
        }
    )


async def school_fee_estimate(stage: str = "primary") -> dict[str, object]:
    """British-curriculum fee range for a stage plus the KHDA fee-cap rule."""
    if stage not in VALID_STAGES:
        return _fail(f"Unknown stage {stage!r}. Valid: {list(VALID_STAGES)}.")

    schooling = _block("schooling")
    fees = schooling.get("british_curriculum_annual_aed", {})

    # "primary" maps onto the foundation_primary band in the source data.
    fee_key = "foundation_primary" if stage in ("primary", "foundation_primary") else "secondary"
    fee_range = fees.get(fee_key)

    return _ok(
        {
            "stage": stage,
            "curriculum": schooling.get("curriculum", "british"),
            "annual_fee_aed": fee_range,
            "overall_range_aed": fees.get("overall_range"),
            "ultra_premium_up_to_aed": fees.get("ultra_premium_up_to_aed"),
            "fee_increase_cap_rule": schooling.get("fee_increase_cap_rule"),
            "other_curricula_note": schooling.get("other_curricula_note"),
            "source_urls": schooling.get("source_urls", []),
        }
    )
