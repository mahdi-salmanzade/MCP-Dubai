"""Gold rate tool functions (DJG retail gold rates from Dubai City of Gold)."""

from __future__ import annotations

import httpx

from mcp_dubai._shared.errors import now_iso, upstream_error_response
from mcp_dubai._shared.health import mark_failure as mark_upstream_failure
from mcp_dubai._shared.health import mark_success as mark_upstream_success
from mcp_dubai._shared.http_client import HttpClientError
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai.data.gold_rate import constants
from mcp_dubai.data.gold_rate.client import GoldRateClient

_SOURCE = "dubaicityofgold.com"
_UPSTREAM = "gold_rate"
_VERIFY_AT = constants.PAGE_URL
_ATTRIBUTION = (
    "Dubai Jewellery Group suggested retail rates via Dubai City of Gold (dubaicityofgold.com)"
)
_DISCLAIMER = (
    "These are Dubai Jewellery Group suggested jewellery retail reference "
    "rates in AED per gram, not spot bullion prices. Shops typically add a "
    "making charge on top."
)
_UPDATE_SCHEDULE = "published around 09:00, 13:30 and 18:00 UAE time"


def _fail(error: str | dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .fail(error=error, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _ok(data: dict[str, object]) -> dict[str, object]:
    return (
        ToolResponse[dict[str, object]]
        .ok(data, source=_SOURCE, retrieved_at=now_iso())
        .model_dump()
    )


def _parse_rates(page: str) -> dict[str, float]:
    """Extract karat -> AED/gram pairs from the page, keyed like "24k"."""
    rates: dict[str, float] = {}
    for karat, value in constants.KARAT_RATE_RE.findall(page):
        try:
            rates[f"{int(karat)}k"] = float(value.replace(",", ""))
        except ValueError:
            continue
    return rates


def _parse_rate_date(page: str) -> str | None:
    """Extract the current rate date (YYYY-MM-DD) from the date dropdown."""
    match = constants.RATE_DATE_RE.search(page)
    return match.group(1) if match else None


def _parse_updated_hint(page: str) -> str | None:
    """Extract the "Updated N minutes ago" hint, whitespace-normalised."""
    match = constants.UPDATED_HINT_RE.search(page)
    return " ".join(match.group(1).split()) if match else None


async def dubai_gold_rate() -> dict[str, object]:
    """
    Get today's Dubai retail gold rates in AED per gram by karat.

    Parses the Dubai Jewellery Group suggested retail rates (24K, 22K,
    21K, 18K, 14K) from the server-rendered Dubai City of Gold homepage.

    Returns:
        Dict with `rates_aed_per_gram` keyed by karat ("24k" ... "14k"),
        `rate_date` (YYYY-MM-DD), `updated_hint`, `update_schedule`,
        `attribution`, and `disclaimer`.
    """
    client = GoldRateClient()
    try:
        page = await client.fetch_page()
    except (HttpClientError, httpx.HTTPError) as exc:
        mark_upstream_failure(_UPSTREAM, str(exc))
        return upstream_error_response(exc, verify_at=_VERIFY_AT, source=_SOURCE)

    rates = _parse_rates(page)
    if len(rates) < constants.MIN_KARAT_RATES:
        mark_upstream_failure(_UPSTREAM, f"parse_error: only {len(rates)} karat rates found")
        return _fail(
            {
                "status": "parse_error",
                "reason": (
                    f"Only {len(rates)} karat rates found in the page HTML "
                    f"(expected at least {constants.MIN_KARAT_RATES}). The "
                    "dubaicityofgold.com markup may have changed."
                ),
                "verify_at": _VERIFY_AT,
            }
        )

    mark_upstream_success(_UPSTREAM)
    return _ok(
        {
            "rates_aed_per_gram": rates,
            "rate_date": _parse_rate_date(page),
            "updated_hint": _parse_updated_hint(page),
            "update_schedule": _UPDATE_SCHEDULE,
            "attribution": _ATTRIBUTION,
            "disclaimer": _DISCLAIMER,
        }
    )
