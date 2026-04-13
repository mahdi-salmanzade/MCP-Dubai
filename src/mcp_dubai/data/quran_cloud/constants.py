"""Al-Quran Cloud endpoints and edition defaults."""

from __future__ import annotations

from typing import Final

from mcp_dubai._shared.constants import QURAN_CLOUD_BASE

SURAH: Final[str] = f"{QURAN_CLOUD_BASE}/surah"  # /{number}/{edition?}
AYAH: Final[str] = f"{QURAN_CLOUD_BASE}/ayah"  # /{reference}/{edition?}
SEARCH: Final[str] = f"{QURAN_CLOUD_BASE}/search"  # /{query}/{surah?}/{edition?}
JUZ: Final[str] = f"{QURAN_CLOUD_BASE}/juz"  # /{number}/{edition?}

# Edition slugs from alquran.cloud. Default to a sensible Arabic + English pair.
DEFAULT_ARABIC_EDITION: Final[str] = "quran-uthmani"
DEFAULT_ENGLISH_EDITION: Final[str] = "en.sahih"  # Sahih International

# Sanity bounds.
MIN_SURAH: Final[int] = 1
MAX_SURAH: Final[int] = 114
MIN_JUZ: Final[int] = 1
MAX_JUZ: Final[int] = 30
