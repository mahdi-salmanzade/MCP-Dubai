"""
Curated data loader using importlib.resources.

Works in editable installs (`pip install -e .`) and inside built wheels
where the JSON files live alongside the package modules. Each call returns
a fresh dict so callers cannot mutate the cached payload.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any, cast

from mcp_dubai._shared.schemas import KnowledgeMetadata


class DataLoadError(Exception):
    """Raised when a curated data file cannot be loaded or is malformed."""


@lru_cache(maxsize=64)
def _load_raw(filename: str) -> str:
    """Cached file read. The cache is invalidated by clear_cache()."""
    try:
        resource = files("mcp_dubai.biz._data").joinpath(filename)
        return resource.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DataLoadError(f"Curated data file not found: {filename}") from exc
    except Exception as exc:
        raise DataLoadError(f"Failed to read {filename}: {exc}") from exc


def load_data_file(filename: str) -> dict[str, Any]:
    """
    Load a curated JSON file from biz/_data/.

    Args:
        filename: File name relative to biz/_data/, e.g. "free_zones.json".

    Returns:
        Parsed JSON as a dict. Returns a deep copy so callers cannot
        mutate the cached payload.
    """
    raw = _load_raw(filename)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DataLoadError(f"Invalid JSON in {filename}: {exc}") from exc
    if not isinstance(data, dict):
        raise DataLoadError(f"{filename} must be a JSON object at the top level")
    return cast(dict[str, Any], _deep_copy(data))


def extract_knowledge(data: dict[str, Any]) -> KnowledgeMetadata:
    """
    Build a KnowledgeMetadata from the standard envelope fields of a
    curated JSON file. Defaults are filled in from the project-wide
    constants if a file omits any field.
    """
    previous_date = data.get("previous_knowledge_date")
    refresh_scope = data.get("last_refresh_scope")
    full_review_date = data.get("full_review_date")
    return KnowledgeMetadata(
        knowledge_date=str(data.get("knowledge_date", "")),
        full_review_date=str(full_review_date) if full_review_date else None,
        previous_knowledge_date=str(previous_date) if previous_date else None,
        last_refresh_scope=str(refresh_scope) if refresh_scope else None,
        volatility=str(data.get("volatility", "medium")),
        verify_at=str(data.get("verify_at", "")),
        disclaimer=str(
            data.get(
                "disclaimer",
                "Verify current rules with the official source before acting.",
            )
        ),
    )


def clear_cache() -> None:
    """Drop the cached file reads. Used by tests after monkeypatching files."""
    _load_raw.cache_clear()


def _deep_copy(value: Any) -> Any:
    """Cheap deep copy for JSON-shaped data."""
    if isinstance(value, dict):
        return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy(v) for v in value]
    return value
