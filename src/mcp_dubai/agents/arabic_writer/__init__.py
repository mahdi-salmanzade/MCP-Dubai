"""arabic_writer: bilingual content generation for formal Arabic business docs."""

from __future__ import annotations

FEATURE_META: dict[str, object] = {
    "name": "arabic_writer",
    "description": (
        "Bilingual content generation for formal Arabic business documents: "
        "letters, contracts, official correspondence, addressee blocks. "
        "Uses curated UAE government title and salutation conventions."
    ),
    "tier": 4,
    "requires_auth": False,
    "source_url": "https://u.ae",
}
