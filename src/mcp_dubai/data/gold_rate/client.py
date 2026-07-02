"""dubaicityofgold.com client. Fetches the DJG retail gold rates page."""

from __future__ import annotations

from mcp_dubai._shared.http_client import HttpClient
from mcp_dubai.data.gold_rate import constants


class GoldRateClient:
    """Async client for the Dubai City of Gold homepage."""

    async def fetch_page(self) -> str:
        """
        Fetch the server-rendered homepage HTML.

        The retail rates are embedded in the page markup (the site's JSON
        API is WAF-blocked), so the caller parses this HTML with the
        tolerant regexes in `constants`. The request carries a
        desktop-browser User-Agent with the project UA appended; see the
        constants module docstring for the rationale.
        """
        headers = {"User-Agent": constants.BROWSER_USER_AGENT}
        async with HttpClient(headers=headers) as client:
            response = await client.get(constants.PAGE_URL)
        return response.text
