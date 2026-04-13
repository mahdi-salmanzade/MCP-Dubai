"""CBUAE Umbraco endpoints (undocumented but verified live)."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import CBUAE_UMBRACO_BASE

# ----------------------------------------------------------------------------
# Exchange rates
# ----------------------------------------------------------------------------
EXCHANGE_RATES_TODAY: Final[str] = f"{CBUAE_UMBRACO_BASE}/Exchange/GetExchangeRateAllCurrency"
EXCHANGE_RATES_HISTORICAL: Final[str] = (
    f"{CBUAE_UMBRACO_BASE}/Exchange/GetExchangeRateAllCurrencyDate"
)
EXCHANGE_RATES_HOMEPAGE_WIDGET: Final[str] = (
    f"{CBUAE_UMBRACO_BASE}/ExchangeHome/GetExchangeRateData"
)

# ----------------------------------------------------------------------------
# Interest rates
# ----------------------------------------------------------------------------
KEY_INTEREST_RATE: Final[str] = f"{CBUAE_UMBRACO_BASE}/InterestRate/GetKeyInterestRate"
