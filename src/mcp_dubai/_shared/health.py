"""
Upstream health registry.

Every feature that talks to an external API registers its upstream here
at import time. The registry stores static metadata (endpoint host,
whether credentials are required, the known block reason if any) and
live counters (last_success, last_failure, failure_count) that features
can update on each HTTP call via `mark_success` / `mark_failure`.

The public surface:

    register_upstream(name, endpoint, requires_auth=False, initial_status=..., initial_reason=...)
    mark_success(name)
    mark_failure(name, reason)
    get_upstream_registry().snapshot()
    reset_upstream_registry()

The `get_upstream_status()` meta tool in `server.py` reads from this
registry and never probes endpoints proactively. Health comes from what
has actually happened during the session, plus any static state declared
at registration time (e.g. we know Cloudflare is blocking centralbank.ae
base-rate today, so that upstream is registered with initial_status
`blocked` until someone wires a live retry that succeeds).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Literal

Status = Literal[
    "unknown",
    "working",
    "blocked",
    "degraded",
    "credentials_missing",
    "static",
]

# Treat 3+ consecutive failures as "degraded" so a single transient blip
# does not flip the public status.
_DEGRADED_FAILURE_THRESHOLD = 3


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class UpstreamState:
    """One registered upstream and its live counters."""

    name: str
    endpoint: str
    requires_auth: bool = False
    status: Status = "unknown"
    reason: str | None = None
    last_success: str | None = None
    last_failure: str | None = None
    success_count: int = 0
    failure_count: int = 0
    features: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "endpoint": self.endpoint,
            "requires_auth": self.requires_auth,
            "status": self.status,
            "reason": self.reason,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "features": list(self.features),
        }


class UpstreamRegistry:
    """Thread-safe registry of upstream health state."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._states: dict[str, UpstreamState] = {}

    def register(
        self,
        name: str,
        endpoint: str,
        *,
        requires_auth: bool = False,
        initial_status: Status = "unknown",
        initial_reason: str | None = None,
        features: list[str] | None = None,
    ) -> None:
        """Register an upstream. Idempotent: second call updates metadata."""
        with self._lock:
            existing = self._states.get(name)
            if existing is None:
                self._states[name] = UpstreamState(
                    name=name,
                    endpoint=endpoint,
                    requires_auth=requires_auth,
                    status=initial_status,
                    reason=initial_reason,
                    features=list(features or []),
                )
                return
            existing.endpoint = endpoint
            existing.requires_auth = requires_auth
            if existing.status == "unknown":
                existing.status = initial_status
                existing.reason = initial_reason
            if features:
                for feat in features:
                    if feat not in existing.features:
                        existing.features.append(feat)

    def mark_success(self, name: str) -> None:
        """Record a successful call. Flips status to `working`."""
        with self._lock:
            state = self._states.get(name)
            if state is None:
                return
            state.success_count += 1
            state.last_success = _now_iso()
            state.status = "working"
            state.reason = None

    def mark_failure(self, name: str, reason: str) -> None:
        """Record a failed call. Flips status to `degraded` after 3 in a row."""
        with self._lock:
            state = self._states.get(name)
            if state is None:
                return
            state.failure_count += 1
            state.last_failure = _now_iso()
            state.reason = reason
            lower = reason.lower()
            if "cloudflare" in lower or "just a moment" in lower or "403" in lower:
                state.status = "blocked"
            elif state.failure_count >= _DEGRADED_FAILURE_THRESHOLD:
                state.status = "degraded"

    def snapshot(self) -> list[dict[str, object]]:
        """Return a stable, ordered copy of every registered upstream."""
        with self._lock:
            return [s.as_dict() for s in sorted(self._states.values(), key=lambda s: s.name)]

    def summary(self) -> dict[str, int]:
        """Count how many upstreams are in each status bucket."""
        with self._lock:
            buckets: dict[str, int] = {}
            for state in self._states.values():
                buckets[state.status] = buckets.get(state.status, 0) + 1
            buckets["total"] = len(self._states)
            return buckets

    def clear(self) -> None:
        with self._lock:
            self._states.clear()


_REGISTRY: UpstreamRegistry | None = None


def get_upstream_registry() -> UpstreamRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = UpstreamRegistry()
        _bootstrap_known_upstreams(_REGISTRY)
    return _REGISTRY


def reset_upstream_registry() -> None:
    """Clear and re-bootstrap. Used by tests and after env changes."""
    global _REGISTRY
    _REGISTRY = UpstreamRegistry()
    _bootstrap_known_upstreams(_REGISTRY)


def register_upstream(
    name: str,
    endpoint: str,
    *,
    requires_auth: bool = False,
    initial_status: Status = "unknown",
    initial_reason: str | None = None,
    features: list[str] | None = None,
) -> None:
    """Module-level shortcut used by feature packages."""
    get_upstream_registry().register(
        name,
        endpoint,
        requires_auth=requires_auth,
        initial_status=initial_status,
        initial_reason=initial_reason,
        features=features,
    )


def mark_success(name: str) -> None:
    """Module-level shortcut used by feature client code."""
    get_upstream_registry().mark_success(name)


def mark_failure(name: str, reason: str) -> None:
    """Module-level shortcut used by feature client code."""
    get_upstream_registry().mark_failure(name, reason)


# ----------------------------------------------------------------------------
# Bootstrap: the known upstreams for every feature that ships today.
#
# This is the source of truth for `get_upstream_status()` until features
# start opting in to live `mark_success` / `mark_failure` calls. Static
# entries capture what we know today: which upstreams are reachable, which
# are behind Cloudflare bot protection, and which require credentials that
# may or may not be configured in the current env.
# ----------------------------------------------------------------------------
def _bootstrap_known_upstreams(registry: UpstreamRegistry) -> None:
    pulse_creds_present = bool(
        os.getenv("MCP_DUBAI_PULSE_CLIENT_ID") and os.getenv("MCP_DUBAI_PULSE_CLIENT_SECRET")
    )
    waqi_token_present = bool(os.getenv("MCP_DUBAI_WAQI_TOKEN"))

    entries: list[dict[str, object]] = [
        {
            "name": "al_adhan",
            "endpoint": "api.aladhan.com",
            "requires_auth": False,
            "initial_status": "unknown",
            "features": ["al_adhan"],
        },
        {
            "name": "quran_cloud",
            "endpoint": "api.alquran.cloud",
            "requires_auth": False,
            "initial_status": "unknown",
            "features": ["quran_cloud"],
        },
        {
            "name": "cbuae_exchange",
            "endpoint": "www.centralbank.ae/umbraco/Surface/Exchange",
            "requires_auth": False,
            "initial_status": "working",
            "initial_reason": "Scraper updated in v0.1.2 for the new three-cell Arabic DOM.",
            "features": ["cbuae"],
        },
        {
            "name": "cbuae_base_rate",
            "endpoint": "www.centralbank.ae/umbraco/Surface/InterestRate",
            "requires_auth": False,
            "initial_status": "blocked",
            "initial_reason": "Cloudflare bot protection active as of 2026-04-13.",
            "features": ["cbuae"],
        },
        {
            "name": "fcsc_ckan",
            "endpoint": "opendata.fcsc.gov.ae",
            "requires_auth": False,
            "initial_status": "blocked",
            "initial_reason": "Cloudflare bot protection active as of 2026-04-13.",
            "features": ["fcsc_ckan"],
        },
        {
            "name": "aviation_weather",
            "endpoint": "aviationweather.gov",
            "requires_auth": False,
            "initial_status": "unknown",
            "features": ["aviation_weather"],
        },
        {
            "name": "osm_overpass",
            "endpoint": "overpass-api.de",
            "requires_auth": False,
            "initial_status": "unknown",
            "features": ["osm_overpass"],
        },
        {
            "name": "waqi",
            "endpoint": "api.waqi.info",
            "requires_auth": True,
            "initial_status": "working" if waqi_token_present else "credentials_missing",
            "initial_reason": (
                None
                if waqi_token_present
                else "Set MCP_DUBAI_WAQI_TOKEN. Free signup at https://aqicn.org/data-platform/token/"
            ),
            "features": ["air_quality"],
        },
        {
            "name": "dubai_pulse",
            "endpoint": "api.dubaipulse.gov.ae",
            "requires_auth": True,
            "initial_status": "working" if pulse_creds_present else "credentials_missing",
            "initial_reason": (
                None
                if pulse_creds_present
                else (
                    "Set MCP_DUBAI_PULSE_CLIENT_ID and MCP_DUBAI_PULSE_CLIENT_SECRET. "
                    "See CREDENTIALS.md for the approval walkthrough."
                )
            ),
            "features": ["dld", "rta"],
        },
        {
            "name": "khda_static",
            "endpoint": "curated snapshot (no network)",
            "requires_auth": False,
            "initial_status": "static",
            "initial_reason": "Curated snapshot, no upstream call.",
            "features": ["khda"],
        },
        {
            "name": "holidays_static",
            "endpoint": "curated calendar (no network)",
            "requires_auth": False,
            "initial_status": "static",
            "initial_reason": "Curated UAE federal calendar, no upstream call.",
            "features": ["holidays"],
        },
        {
            "name": "rta_gtfs",
            "endpoint": "gtfs-source-feeds.transit.land",
            "requires_auth": False,
            "initial_status": "unknown",
            "features": ["rta"],
        },
    ]

    for entry in entries:
        registry.register(
            name=str(entry["name"]),
            endpoint=str(entry["endpoint"]),
            requires_auth=bool(entry["requires_auth"]),
            initial_status=entry["initial_status"],  # type: ignore[arg-type]
            initial_reason=entry.get("initial_reason"),  # type: ignore[arg-type]
            features=entry.get("features"),  # type: ignore[arg-type]
        )
