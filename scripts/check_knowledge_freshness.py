#!/usr/bin/env python3
"""
Report which curated knowledge domains have an overdue full-review date.

Seven packs silently went 3.5 months stale before the July 2026 audit found
them, because staleness was only visible if a human opened the JSON. This
script makes pack age a machine-checkable signal.

Budgets are keyed by each domain's declared `volatility` and are applied to
`full_review_date`. A targeted update can advance `knowledge_date`, but it does
not reset the full-review clock. The three code-only domains are audited along
with the 16 JSON packs so all 19 advertised domains share one gate.

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

from mcp_dubai._shared.schemas import KnowledgeMetadata

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATA_DIR = _REPO_ROOT / "src" / "mcp_dubai" / "biz" / "_data"

# Maximum age of a domain's recorded full review. These are alerting windows.
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


def _code_only_knowledge() -> dict[str, KnowledgeMetadata]:
    """Load the three registered domains that do not have their own JSON pack."""
    from mcp_dubai.agents.arabic_writer.tools import KNOWLEDGE as ARABIC_WRITER_KNOWLEDGE
    from mcp_dubai.agents.data_analyst.tools import KNOWLEDGE as DATA_ANALYST_KNOWLEDGE
    from mcp_dubai.biz.setup_advisor.tools import KNOWLEDGE as SETUP_ADVISOR_KNOWLEDGE

    return {
        "arabic_writer": ARABIC_WRITER_KNOWLEDGE,
        "data_analyst": DATA_ANALYST_KNOWLEDGE,
        "setup_advisor": SETUP_ADVISOR_KNOWLEDGE,
    }


def _row(
    *,
    source: str,
    source_kind: str,
    domain: object,
    knowledge_date: object,
    full_review_date: object,
    previous_knowledge_date: object,
    last_refresh_scope: object,
    volatility: object,
    verify_at: object,
    today: date,
) -> dict[str, object]:
    """Build and validate one freshness row."""
    domain_name = str(domain)
    latest_stamp = date.fromisoformat(str(knowledge_date))
    full_stamp = date.fromisoformat(str(full_review_date))
    volatility_name = str(volatility)
    if volatility_name not in MAX_AGE_DAYS:
        raise ValueError(
            f"{source}: unknown volatility {volatility_name!r}; "
            f"expected one of {sorted(MAX_AGE_DAYS)}"
        )
    if latest_stamp > today:
        raise ValueError(f"{source}: knowledge_date {latest_stamp} is in the future")
    if full_stamp > today:
        raise ValueError(f"{source}: full_review_date {full_stamp} is in the future")
    if full_stamp > latest_stamp:
        raise ValueError(
            f"{source}: full_review_date {full_stamp} is after knowledge_date {latest_stamp}"
        )

    budget = MAX_AGE_DAYS[volatility_name]
    full_review_age = (today - full_stamp).days
    latest_update_age = (today - latest_stamp).days
    targeted = bool(last_refresh_scope)
    return {
        # `pack` is retained for consumers of the script's earlier JSON shape.
        "pack": source,
        "source": source,
        "source_kind": source_kind,
        "domain": domain_name,
        "knowledge_date": latest_stamp.isoformat(),
        "full_review_date": full_stamp.isoformat(),
        "previous_knowledge_date": previous_knowledge_date,
        "last_refresh_scope": last_refresh_scope,
        "targeted_refresh": targeted,
        "volatility": volatility_name,
        "latest_update_age_days": latest_update_age,
        # `age_days` now intentionally means full-review age.
        "age_days": full_review_age,
        "full_review_age_days": full_review_age,
        "budget_days": budget,
        "overdue": full_review_age > budget,
        "overdue_by_days": max(0, full_review_age - budget),
        "verify_at": verify_at,
    }


def audit() -> list[dict[str, object]]:
    """Return one row for each of the 19 freshness-tracked domains."""
    rows: list[dict[str, object]] = []
    today = _today()
    for path in sorted(_DATA_DIR.glob("*.json")):
        pack = json.loads(path.read_text())
        rows.append(
            _row(
                source=path.name,
                source_kind="json",
                domain=pack.get("domain"),
                knowledge_date=pack["knowledge_date"],
                full_review_date=pack["full_review_date"],
                previous_knowledge_date=pack.get("previous_knowledge_date"),
                last_refresh_scope=pack.get("last_refresh_scope"),
                volatility=pack.get("volatility", DEFAULT_VOLATILITY),
                verify_at=pack.get("verify_at"),
                today=today,
            )
        )

    for domain, meta in _code_only_knowledge().items():
        full_review_date = meta.full_review_date
        if not full_review_date:
            raise ValueError(f"{domain}: code-only domain is missing full_review_date")
        rows.append(
            _row(
                source=f"{domain} (code)",
                source_kind="code",
                domain=domain,
                knowledge_date=meta.knowledge_date,
                full_review_date=full_review_date,
                previous_knowledge_date=meta.previous_knowledge_date,
                last_refresh_scope=meta.last_refresh_scope,
                volatility=meta.volatility,
                verify_at=meta.verify_at,
                today=today,
            )
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
        header = (
            f"{'domain':22} {'latest':12} {'full review':12} "
            f"{'volatility':11} {'age':>5} {'budget':>7}  status"
        )
        print(header)
        print("-" * len(header))
        for r in rows:
            status = f"OVERDUE by {r['overdue_by_days']}d" if r["overdue"] else "ok"
            if r["targeted_refresh"]:
                status += " (targeted)"
            print(
                f"{r['domain']!s:22} {r['knowledge_date']!s:12} "
                f"{r['full_review_date']!s:12} "
                f"{r['volatility']!s:11} {int(r['age_days']):>5} "
                f"{int(r['budget_days']):>7}  {status}"
            )
        print()
        if overdue:
            print(f"{len(overdue)} domain(s) with an overdue full review:")
            for r in overdue:
                print(f"  - {r['domain']}: re-verify against {r['verify_at']}")
        else:
            print("All 19 full-review dates are within their alerting budgets.")
        print(
            "Targeted updates advance only knowledge_date. They do not reset "
            "the full_review_date used by this gate."
        )

    if args.strict and overdue:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
