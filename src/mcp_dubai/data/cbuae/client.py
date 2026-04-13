"""
CBUAE client.

Parses HTML responses from undocumented Umbraco endpoints. The exchange
rate endpoint returns a full HTML page that embeds a single table where
each row has three cells: a decorative empty cell, an Arabic currency
name, and a rate cell marked `class="... value"`. The parser anchors on
the `value` class so it is resilient to column reordering. Arabic names
are translated to ISO 4217 codes via `currency_map.ARABIC_TO_ISO`.

Verified against the live response on 2026-04-13. We use lxml because it
tolerates malformed fragments better than html.parser.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from lxml import html

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.cbuae import constants
from mcp_dubai.data.cbuae.currency_map import lookup as lookup_currency

# Matches plain decimals like 3.6725 and scientific notation like 3E-06.
_RATE_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _parse_rate(text: str) -> float | None:
    """Extract a numeric rate from a cell's text, tolerating whitespace and units."""
    match = _RATE_RE.search(text)
    if match is None:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


class CbuaeClient:
    """Async client for CBUAE Umbraco endpoints."""

    async def get_exchange_rates_today(self) -> list[dict[str, Any]]:
        """Fetch today's exchange rates for all listed currencies."""
        async with HttpClient() as client:
            response = await client.get(constants.EXCHANGE_RATES_TODAY)
        return self._parse_currency_table(response.text)

    async def get_exchange_rates_for_date(self, target_date: date) -> list[dict[str, Any]]:
        """Fetch historical exchange rates for a specific date."""
        date_str = target_date.strftime("%Y-%m-%d")
        async with HttpClient() as client:
            response = await client.get(
                constants.EXCHANGE_RATES_HISTORICAL,
                params={"dateTime": date_str},
            )
        return self._parse_currency_table(response.text)

    async def get_key_interest_rate(self) -> dict[str, Any]:
        """Fetch the CBUAE base rate."""
        async with HttpClient() as client:
            response = await client.get(constants.KEY_INTEREST_RATE)
        return self._parse_base_rate(response.text)

    @staticmethod
    def _parse_currency_table(html_fragment: str) -> list[dict[str, Any]]:
        """
        Extract currency rows from a CBUAE HTML fragment.

        The live CBUAE Umbraco endpoint returns a three-cell row shape:

            <tr>
                <td class="font-r ...">              (empty decorative)
                <td class="font-r ...">دولار امريكي</td>
                <td class="font-r ... value">3.6725</td>
            </tr>

        We anchor on `td.value` for the rate cell, take the preceding
        sibling cell as the Arabic currency name, and translate that name
        to an ISO 4217 code and English label via `lookup_currency`.
        Rows without a `value` cell (header rows, layout rows) are
        skipped. Rows with an unrecognised Arabic name still pass through
        with `iso_code` and `currency` set to `None` so we never silently
        drop data.
        """
        if not html_fragment.strip():
            return []

        # Wrap in a root element so lxml can parse partial fragments cleanly.
        wrapped = f"<root>{html_fragment}</root>"
        try:
            tree = html.fromstring(wrapped)
        except Exception:
            return []

        rows: list[dict[str, Any]] = []
        for tr in tree.xpath(".//tr"):
            value_cells = tr.xpath(
                ".//td[contains(concat(' ', normalize-space(@class), ' '), ' value ')]"
            )
            if not value_cells:
                continue

            rate_text = (value_cells[0].text_content() or "").strip()
            rate_value = _parse_rate(rate_text)
            if rate_value is None:
                continue

            # Currency name: the td immediately before the value cell.
            cells = tr.xpath(".//td")
            name_cell = None
            for idx, cell in enumerate(cells):
                if cell is value_cells[0] and idx > 0:
                    name_cell = cells[idx - 1]
                    break
            if name_cell is None:
                continue

            arabic_name = (name_cell.text_content() or "").strip()
            if not arabic_name:
                continue

            iso_code, english_name = lookup_currency(arabic_name)
            rows.append(
                {
                    "currency": english_name,
                    "currency_ar": arabic_name,
                    "iso_code": iso_code,
                    "rate_aed": rate_value,
                }
            )

        return rows

    @staticmethod
    def _parse_base_rate(html_fragment: str) -> dict[str, Any]:
        """Extract the base rate as a single percentage value."""
        if not html_fragment.strip():
            return {"base_rate_percent": None, "raw": ""}

        text = re.sub(r"<[^>]+>", " ", html_fragment)
        text = re.sub(r"\s+", " ", text).strip()

        match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if match:
            return {
                "base_rate_percent": float(match.group(1)),
                "raw": text[:200],
            }

        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if match:
            return {
                "base_rate_percent": float(match.group(0)),
                "raw": text[:200],
            }

        return {"base_rate_percent": None, "raw": text[:200]}
