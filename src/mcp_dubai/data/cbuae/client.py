"""
CBUAE client.

Parses HTML fragments from undocumented Umbraco endpoints. The structure
is a simple table with currency rows. We use lxml because it tolerates
malformed fragments better than html.parser.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from lxml import html

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.cbuae import constants


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

        The fragment structure is a simple HTML table with rows like:
            <tr><td>US Dollar</td><td>3.6725</td></tr>
            <tr><td>Euro</td><td>4.307918</td></tr>

        We tolerate column count variation by taking the first cell as the
        currency name and the last numeric cell as the rate.
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
            cells = tr.xpath(".//td")
            if len(cells) < 2:
                continue
            currency_name = (cells[0].text_content() or "").strip()
            if not currency_name:
                continue

            rate_value = None
            for cell in reversed(cells):
                text = (cell.text_content() or "").strip()
                match = re.search(r"-?\d+(?:\.\d+)?", text)
                if match:
                    try:
                        rate_value = float(match.group(0))
                        break
                    except ValueError:
                        continue

            if rate_value is None:
                continue

            rows.append(
                {
                    "currency": currency_name,
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
