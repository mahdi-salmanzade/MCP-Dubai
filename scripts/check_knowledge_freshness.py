#!/usr/bin/env python3
"""
Report which curated knowledge packs are overdue for re-verification.

Seven packs silently went 3.5 months stale before the July 2026 audit found
them, because staleness was only visible if a human opened the JSON. This
script makes pack age a machine-checkable signal.

Budgets are keyed by each pack's declared `volatility`, since a pack of
accelerator cohort dates decays far faster than one describing a long-standing
attestation process.

Usage:
    python scripts/check_knowledge_freshness.py            # report, exit 0
    python scripts/check_knowledge_freshness.py --strict   # exit 1 if overdue
    python scripts/check_knowledge_freshness.py --json     # machine-readable
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATA_DIR = _REPO_ROOT / "src" / "mcp_dubai" / "biz" / "_data"

# Days a pack may go unverified before it is reported as overdue. The project
# aims at a quarterly refresh for fast-moving domains, so `high` sits near 90.
MAX_AGE_DAYS: dict[str, int] = {
    "high": 100,
    "medium": 190,
    "stable": 365,
}

DEFAULT_VOLATILITY = "high"


def _today() -> date:
    """Today in Asia/Dubai, matching the timezone every tool reports in."""
    from mcp_dubai._shared.constants import uae_today

    return uae_today()


def audit() -> list[dict[str, object]]:
    """Return one row per pack, newest-verified last."""
    rows: list[dict[str, object]] = []
    today = _today()
    for path in sorted(_DATA_DIR.glob("*.json")):
        pack = json.loads(path.read_text())
        volatility = str(pack.get("volatility", DEFAULT_VOLATILITY))
        budget = MAX_AGE_DAYS.get(volatility, MAX_AGE_DAYS[DEFAULT_VOLATILITY])
        stamp = date.fromisoformat(str(pack["knowledge_date"]))
        age = (today - stamp).days
        rows.append(
            {
                "pack": path.name,
                "domain": pack.get("domain"),
                "knowledge_date": stamp.isoformat(),
                "volatility": volatility,
                "age_days": age,
                "budget_days": budget,
                "overdue": age > budget,
                "overdue_by_days": max(0, age - budget),
                "verify_at": pack.get("verify_at"),
            }
        )
    rows.sort(key=lambda r: (not r["overdue"], -int(r["age_days"])))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 when any pack is overdue")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    rows = audit()
    overdue = [r for r in rows if r["overdue"]]

    if args.json:
        print(json.dumps({"today": _today().isoformat(), "packs": rows}, indent=2))
    else:
        print(f"Knowledge freshness as of {_today().isoformat()}\n")
        header = f"{'pack':26} {'verified':12} {'volatility':11} {'age':>5} {'budget':>7}  status"
        print(header)
        print("-" * len(header))
        for r in rows:
            status = f"OVERDUE by {r['overdue_by_days']}d" if r["overdue"] else "ok"
            print(
                f"{r['pack']!s:26} {r['knowledge_date']!s:12} "
                f"{r['volatility']!s:11} {int(r['age_days']):>5} "
                f"{int(r['budget_days']):>7}  {status}"
            )
        print()
        if overdue:
            print(f"{len(overdue)} pack(s) overdue for re-verification:")
            for r in overdue:
                print(f"  - {r['pack']}: re-verify against {r['verify_at']}")
        else:
            print("All packs within their freshness budget.")

    if args.strict and overdue:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
