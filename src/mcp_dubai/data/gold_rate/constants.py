"""dubaicityofgold.com page constants and tolerant HTML regexes.

Dubai City of Gold is the Dubai Jewellery Group's consumer site. Its
homepage is server-rendered HTML that embeds the suggested retail gold
rates; the site's JSON API is WAF-blocked, so this feature parses that
HTML directly with tolerant regexes (no extra parser dependency).

User-Agent decision: requests go out with a desktop-browser User-Agent
and the project user-agent appended. The WAF that blocks the JSON API
tolerates plain clients on the HTML page today, but the browser UA keeps
us on the safe side while the appended project UA keeps our traffic
identifiable to the site operator.

Verified live markup on 2026-07-02:

    <div class="sortd-gold-price-item">
        <span class="sortd-gold-type">24K Gold</span>
        <span class="sortd-gold-value">AED 494.75</span>
    </div>

plus a `<select id="gold-price-date">` whose first option value is the
current rate date (YYYY-MM-DD) and a `<span class="update-dte">` hint
like "Updated 3 minutes ago".
"""

from __future__ import annotations

import re
from typing import Final

from mcp_dubai._shared.constants import GOLD_RATE_PAGE, HTTP_USER_AGENT

PAGE_URL: Final[str] = GOLD_RATE_PAGE

# Desktop-browser UA with the project UA appended (see module docstring).
BROWSER_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 {HTTP_USER_AGENT}"
)

# One karat row: anchors on the sortd-gold-type / sortd-gold-value class
# names, tolerating whitespace, attribute reshuffles, and thousands commas.
KARAT_RATE_RE: Final[re.Pattern[str]] = re.compile(
    r'sortd-gold-type"\s*>\s*(\d{1,2})\s*K\b[^<]*</span>\s*'
    r'<span[^>]*sortd-gold-value"\s*>\s*AED\s*([\d,]+(?:\.\d+)?)',
    re.IGNORECASE | re.DOTALL,
)

# The first <option> of the date dropdown carries the current rate date.
RATE_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r'id="gold-price-date".*?<option\s+value="(\d{4}-\d{2}-\d{2})"',
    re.IGNORECASE | re.DOTALL,
)

# The "Updated N minutes ago" freshness hint next to the price list.
UPDATED_HINT_RE: Final[re.Pattern[str]] = re.compile(
    r'class="update-dte"\s*>\s*([^<]+?)\s*</span>',
    re.IGNORECASE | re.DOTALL,
)

# Fewer parsed karats than this means the page layout changed: fail with
# parse_error instead of returning a half-empty rates map.
MIN_KARAT_RATES: Final[int] = 3
