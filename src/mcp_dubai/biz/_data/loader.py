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
from typing import Any

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
    copied = _deep_copy(data)
    assert isinstance(copied, dict)  # for mypy: _deep_copy preserves the dict shape
    return copied


def extract_knowledge(data: dict[str, Any]) -> KnowledgeMetadata:
    """
    Build a KnowledgeMetadata from the standard envelope fields of a
    curated JSON file. Defaults are filled in from the project-wide
    constants if a file omits any field.
    """
    return KnowledgeMetadata(
        knowledge_date=str(data.get("knowledge_date", "")),
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
