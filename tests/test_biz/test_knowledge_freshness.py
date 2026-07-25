"""
Structural invariants for the curated knowledge packs.

Seven packs silently went 3.5 months stale before the July 2026 audit found
them, because staleness was only visible if a human opened the JSON.

The split here is deliberate:

* Structure is a **test**. A pack with no `knowledge_date`, an unknown
  `volatility`, or a future-dated stamp makes every freshness check downstream
  meaningless, so those are hard failures that block the build.
* Staleness is a **scheduled alert**, not a test. Content going stale is normal
  and is the maintainer's cue to re-verify, not a reason to fail a PR that
  touched unrelated code. See `scripts/check_knowledge_freshness.py` and the
  `knowledge-freshness` workflow.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from mcp_dubai._shared.constants import uae_today

_DATA_DIR = Path(__file__).resolve().parents[2] / "src" / "mcp_dubai" / "biz" / "_data"

# Kept in lockstep with scripts/check_knowledge_freshness.py.
_VALID_VOLATILITY = {"high", "medium", "stable"}
_REQUIRED_KEYS = ("domain", "knowledge_date", "volatility", "verify_at")


def _packs() -> list[tuple[str, dict[str, object]]]:
    out = [(p.name, json.loads(p.read_text())) for p in sorted(_DATA_DIR.glob("*.json"))]
    assert out, f"no knowledge packs found under {_DATA_DIR}"
    return out


_PACKS = _packs()
_IDS = [name for name, _ in _PACKS]


@pytest.mark.parametrize("name,pack", _PACKS, ids=_IDS)
def test_pack_declares_required_metadata(name: str, pack: dict[str, object]) -> None:
    for key in _REQUIRED_KEYS:
        assert key in pack, f"{name} is missing the {key!r} key"


@pytest.mark.parametrize("name,pack", _PACKS, ids=_IDS)
def test_volatility_uses_the_known_vocabulary(name: str, pack: dict[str, object]) -> None:
    assert pack["volatility"] in _VALID_VOLATILITY, (
        f"{name} declares volatility {pack['volatility']!r}; expected one of "
        f"{sorted(_VALID_VOLATILITY)}. An unknown value silently falls back to "
        "the strictest freshness budget."
    )


@pytest.mark.parametrize("name,pack", _PACKS, ids=_IDS)
def test_knowledge_date_is_iso_and_not_in_the_future(name: str, pack: dict[str, object]) -> None:
    stamp = date.fromisoformat(str(pack["knowledge_date"]))
    assert stamp <= uae_today(), (
        f"{name} claims knowledge_date {stamp}, which is in the future. "
        "A forward-dated pack can never be reported as stale."
    )


@pytest.mark.parametrize("name,pack", _PACKS, ids=_IDS)
def test_verify_at_is_an_https_url(name: str, pack: dict[str, object]) -> None:
    verify_at = str(pack["verify_at"])
    assert verify_at.startswith("https://"), (
        f"{name} has verify_at={verify_at!r}. It is surfaced to users as the "
        "place to confirm the pack, so it must be a real https URL."
    )


def test_freshness_script_agrees_with_this_module() -> None:
    """The script owns the budgets; this guards against the two drifting apart."""
    from scripts.check_knowledge_freshness import MAX_AGE_DAYS

    assert set(MAX_AGE_DAYS) == _VALID_VOLATILITY
