"""Pure tool functions for the holidays feature."""

from __future__ import annotations

from datetime import date

from mcp_dubai._shared.constants import KNOWLEDGE_DATE
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.holidays.data import HOLIDAYS_BY_YEAR

_SOURCE = "curated (u.ae federal holidays + MoHRE circulars)"


def _parse_iso(value: str) -> date:
    return date.fromisoformat(value)


async def uae_holidays(year: int = 2026) -> dict[str, object]:
    """
    List all UAE federal public holidays for a given Gregorian year.

    Lunar holidays are flagged as `provisional` until officially announced
    by MoHRE roughly 10 days before the date.
    """
    holidays = HOLIDAYS_BY_YEAR.get(year)
    if holidays is None:
        return (
            ToolResponse[dict[str, object]]
            .ok(
                {
                    "year": year,
                    "holidays": [],
                    "warning": (
                        f"No curated holiday data for {year}. "
                        f"Currently only 2026 is shipped. "
                        f"Use Calendarific (https://calendarific.com) for other years."
                    ),
                },
                source=_SOURCE,
                retrieved_at=KNOWLEDGE_DATE,
            )
            .model_dump()
        )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "year": year,
                "holidays": list(holidays),
                "note": (
                    "Lunar holidays (provisional=true) need to be re-verified against "
                    "MoHRE circulars closer to the date."
                ),
            },
            source=_SOURCE,
            retrieved_at=KNOWLEDGE_DATE,
        )
        .model_dump()
    )


async def uae_next_holiday(from_date_str: str | None = None) -> dict[str, object]:
    """Return the next UAE public holiday on or after a reference date."""
    try:
        reference = _parse_iso(from_date_str) if from_date_str else date.today()
    except ValueError as exc:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"Invalid ISO date: {from_date_str!r} ({exc})", source=_SOURCE)
            .model_dump()
        )

    year_holidays = HOLIDAYS_BY_YEAR.get(reference.year, [])
    upcoming = [h for h in year_holidays if _parse_iso(h["date"]) >= reference]

    if not upcoming:
        next_year = HOLIDAYS_BY_YEAR.get(reference.year + 1, [])
        if next_year:
            upcoming = list(next_year)

    if not upcoming:
        return (
            ToolResponse[dict[str, object]]
            .ok(
                {
                    "from_date": reference.isoformat(),
                    "next_holiday": None,
                    "warning": "No upcoming holidays in the curated dataset.",
                },
                source=_SOURCE,
                retrieved_at=KNOWLEDGE_DATE,
            )
            .model_dump()
        )

    upcoming.sort(key=lambda h: h["date"])
    next_h = upcoming[0]
    days_away = (_parse_iso(next_h["date"]) - reference).days

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "from_date": reference.isoformat(),
                "next_holiday": next_h,
                "days_away": days_away,
            },
            source=_SOURCE,
            retrieved_at=KNOWLEDGE_DATE,
        )
        .model_dump()
    )


async def is_uae_holiday(date_str: str) -> dict[str, object]:
    """Check whether a specific Gregorian date is a UAE public holiday."""
    try:
        target = _parse_iso(date_str)
    except ValueError as exc:
        return (
            ToolResponse[dict[str, object]]
            .fail(error=f"Invalid ISO date: {date_str!r} ({exc})", source=_SOURCE)
            .model_dump()
        )

    year_holidays = HOLIDAYS_BY_YEAR.get(target.year, [])

    for holiday in year_holidays:
        if holiday["date"] == target.isoformat():
            return (
                ToolResponse[dict[str, object]]
                .ok(
                    {
                        "date": target.isoformat(),
                        "is_holiday": True,
                        "holiday": holiday,
                    },
                    source=_SOURCE,
                    retrieved_at=KNOWLEDGE_DATE,
                )
                .model_dump()
            )

    return (
        ToolResponse[dict[str, object]]
        .ok(
            {
                "date": target.isoformat(),
                "is_holiday": False,
                "holiday": None,
            },
            source=_SOURCE,
            retrieved_at=KNOWLEDGE_DATE,
        )
        .model_dump()
    )
