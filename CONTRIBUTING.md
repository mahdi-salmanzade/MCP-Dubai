# Contributing to MCP-Dubai

Thank you for considering a contribution. MCP-Dubai is a community project, and the best contributions come from people actually using the tools and noticing what is missing or stale.

This guide covers the dev setup, the conventions every feature follows, and the PR checklist.

---

## Where to start

The most useful contributions right now:

1. **Refresh stale curated knowledge.** Each `biz/*` feature reads a JSON file in `src/mcp_dubai/biz/_data/` with a `knowledge_date` and `verify_at` URL. UAE tax rules, visa thresholds, and free zone pricing change frequently. If you spot something stale, file a PR with the corrected data, the new `knowledge_date`, and a link to the official source.
2. **Improve Tier 1 data.dubai integrations and contract checks.** DLD and RTA wrappers already use the OAuth gateway, while RTA publishes GTFS independently. Add bounded pagination, schema validation, and opt-in live contract checks without changing established tool signatures.
3. **New Tier 1 Dubai Pulse wrappers.** `dld` and `rta` shells ship today with graceful credential-missing responses. The next orgs to wrap are DHA (health facilities), DEWA (utilities), DTCM (tourism stats), DET (business activities), Dubai Municipality (food safety, permits), Dubai Customs, and Dubai Airports (FIDS). See `src/mcp_dubai/_shared/auth.py` and `src/mcp_dubai/data/dld/tools.py` for the credential-missing contract.
4. **New curated business packs.** Sector-specific startup playbooks are high demand and have zero upstream dependency. Follow the `biz/founder_essentials` pattern: one JSON in `biz/_data/`, one `tools.py`, one `server.py`, and one test file.
5. **Improve `recommend_tools` BM25 quality** by tuning tags. Current quirk: in small sub-corpora, length normalization can favour shorter tools when queries collide on common tokens. Arabic and abbreviation aliases already expand at index and query time (see `_shared/aliases.py`); adding new equivalence sets there is often enough.
6. **Add features beyond Dubai.** Sharjah, Abu Dhabi, and federal UAE data could live in this same server.

---

## Dev setup

You need Python 3.11 or 3.12.

```bash
git clone https://github.com/mahdi-salmanzade/MCP-Dubai.git
cd MCP-Dubai

# Create a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install with dev + optional data extras
make dev
# Or directly:
pip install -e ".[dev,data]"
```

That installs `fastmcp`, `httpx`, `pydantic`, `tenacity`, `lxml`, `rank-bm25`, `pytest`, `pytest-asyncio`, `pytest-cov`, `respx`, `ruff`, `mypy`.

---

## Common commands

```bash
make test         # pytest with coverage report
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy strict
make check        # lint + format check + typecheck + test + freshness report
make run          # python -m mcp_dubai (runs the MCP server over stdio)
make clean        # drop caches
```

Smoke-test the server boots without errors:

```bash
.venv/bin/python -c "from mcp_dubai.server import mcp, list_features; print(mcp.name); print(len(list_features()), 'features')"
```

Run a single feature's tests:

```bash
pytest tests/test_data/test_al_adhan.py -v
pytest tests/test_biz/test_setup_advisor.py -v
```

---

## Project conventions

Read these before opening a PR. The patterns are not optional, they make the project shippable.

### 1. No em dashes

Hard project rule: do not use em dashes (`—`, U+2014) or en dashes (`–`, U+2013) anywhere in the project, including code, comments, docstrings, JSON files, README, tests. Use a regular hyphen, a colon, parentheses, or two sentences. Ranges are written as "X to Y" not "X-Y" and not "X–Y". The CI sweeps for both characters.

### 2. Feature folder layout

Every feature follows the same layout:

```
src/mcp_dubai/<data|biz>/<feature>/
├── __init__.py        # Exports FEATURE_META dict
├── constants.py       # Endpoint URLs, default parameters
├── schemas.py         # Pydantic v2 models (data features only)
├── client.py          # Async API client (data features only)
├── tools.py           # Pure async functions, NO FastMCP imports
└── server.py          # FastMCP wrappers + ToolDiscovery registration
```

The split between `tools.py` and `server.py` is critical: `tools.py` has zero FastMCP imports, so unit tests can hit the real logic without going through any MCP layer. `server.py` is just thin docstring wrappers that pass kwargs through.

### 3. Pure tools, decorated wrappers

```python
# tools.py
async def my_tool(arg: str) -> dict[str, object]:
    """Real implementation."""
    ...
    return result

# server.py
from fastmcp import FastMCP
from mcp_dubai.<data|biz>.<feature> import tools

mcp: FastMCP = FastMCP("feature_name")

@mcp.tool
async def my_tool(arg: str) -> dict[str, object]:
    """Docstring the LLM sees. Mirror tools.py signature."""
    return await tools.my_tool(arg=arg)
```

### 4. ToolResponse envelope (biz/* features)

Every business knowledge tool returns a `ToolResponse` envelope. Carries `success`, `data`, `error`, and an optional `knowledge` block.

```python
from mcp_dubai._shared.schemas import ToolResponse
from mcp_dubai._shared.knowledge import register_domain_knowledge
from mcp_dubai.biz._data.loader import extract_knowledge, load_data_file

_DATA = load_data_file("my_domain.json")
KNOWLEDGE = extract_knowledge(_DATA)
register_domain_knowledge("my_domain", KNOWLEDGE)


async def my_tool(...) -> dict[str, object]:
    if invalid:
        return ToolResponse[dict[str, object]].fail(error="reason").model_dump()
    return ToolResponse[dict[str, object]].ok(result, knowledge=KNOWLEDGE).model_dump()
```

The per-domain `KNOWLEDGE` constant is registered with the shared registry at module import time, so `get_knowledge_status()` reflects the latest recorded update automatically. When an update is targeted, preserve the prior date and describe the exact scope; the shared response metadata exposes both fields to clients.

### 5. Graceful credential degradation (Tier 1 features)

Tools that need credentials (Dubai Pulse OAuth, WAQI free key) MUST NOT crash the server when env vars are missing. They call `availability()` and return a structured `ToolResponse.fail` with `{status, reason, docs}`. This way `python -m mcp_dubai` always boots cleanly on a fresh machine.

```python
from mcp_dubai._shared.auth import get_dubai_pulse_auth

async def dld_search(...) -> dict[str, object]:
    auth = get_dubai_pulse_auth()
    avail = auth.availability()
    if avail["status"] != "ready":
        return ToolResponse[dict[str, object]].fail(error=avail).model_dump()
    # ... real work
```

### 6. ToolDiscovery registration

Every feature registers its tools with the BM25 discovery at import time:

```python
from mcp_dubai._shared.discovery import TIER_OPEN, ToolMeta, get_tool_discovery

_TOOLS: list[ToolMeta] = [
    ToolMeta(
        name="my_tool",
        description="...",
        feature="my_feature",
        tier=TIER_OPEN,
        tags=["good", "search", "terms"],
    ),
]
get_tool_discovery().register_many(_TOOLS)
```

Tag generously. The BM25 layer ranks results based on token overlap, so synonyms and common related terms make the difference between the LLM finding the right tool and asking for it.

### 7. Tests

Use `respx` for any test that touches `httpx`. Real network calls in CI are a flake source.

```python
import pytest
import respx
from httpx import Response

@pytest.mark.asyncio
@respx.mock
async def test_happy_path():
    route = respx.get("https://example.com").mock(
        return_value=Response(200, json={"ok": True})
    )
    result = await tools.my_tool()
    assert route.called
    assert result["data"] == {"ok": True}
```

The `tests/conftest.py` autouse `reset_singletons` fixture clears `DubaiPulseAuth`, `ToolDiscovery`, and `KnowledgeRegistry` before AND after every test, so individual tests do not leak state.

---

## Curated JSON envelope (biz/_data/)

Every curated business knowledge file follows the same envelope. This is what makes the freshness model work.

```json
{
  "domain": "my_domain",
  "knowledge_date": "YYYY-MM-DD",
  "volatility": "high",
  "verify_at": "https://official.source.ae",
  "source_brief_section": "6.x",
  "disclaimer": "Verify with the official source before quoting figures.",
  "currency": "AED",
  "items": [
    {
      "id": "stable_snake_case_id",
      "name": "Display Name",
      "as_of": "2025-Q4",
      "source_urls": [
        "https://official.source.ae"
      ]
    }
  ]
}
```

Rules:
- Stable `id` per row (lowercase snake_case, never reused).
- Put `as_of` at row level or in the narrowest shared block containing numeric values that can drift.
- Prefer `source_urls` for multiple references. Existing schemas may use `source_url` or a canonical `url` for a single official page.
- Prefer primary official sources. Add secondary reporting only where the official source does not publish the required dated fact.
- Use provenance tags only where a pack implements them consistently; they are not universal.
- All numeric values use the most natural unit. Currency in `_aed` or `_usd` suffix.

Files are loaded via `mcp_dubai.biz._data.loader.load_data_file(name)` which uses `importlib.resources` so they ship in the wheel automatically.

---

## PR Checklist

Before opening a PR, run `make check` and confirm:

- [ ] All gates pass: `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` (884 tests, 93.40% coverage).
- [ ] No em dashes (`—`) or en dashes (`–`) anywhere in the diff.
- [ ] If you added a new feature, it follows the feature folder layout (constants, schemas/client if needed, tools, server, tests).
- [ ] If you added a `biz/*` feature, it has a curated JSON file in `_data/` with the standard envelope, a per-domain `KNOWLEDGE` constant, and a call to `register_domain_knowledge`.
- [ ] If you added a Tier 1 feature, it uses the graceful credential degradation pattern.
- [ ] If you touched curated knowledge, you advanced `knowledge_date`, preserved `full_review_date` unless the whole domain was reviewed, recorded `previous_knowledge_date` and `last_refresh_scope` for a targeted refresh, and added or updated an authoritative `source_urls`, `source_url`, or canonical `url` reference in the affected record.
- [ ] You added tests with `respx` mocks for any new HTTP path. No real network calls in CI.
- [ ] You registered new tools with `ToolDiscovery` via a `_TOOLS: list[ToolMeta]` block in `server.py`.
- [ ] If you added a new tool, you mounted its parent feature in `src/mcp_dubai/server.py`.
- [ ] You updated `README.md` if the feature catalogue changed materially.

---

## Reporting bugs and broken APIs

Open an issue at <https://github.com/mahdi-salmanzade/MCP-Dubai/issues>.

When a tool returns wrong, empty, or error results, include:

1. The **tool name** (e.g., `dld_search_transactions`).
2. The **arguments** you passed.
3. The **error message** or unexpected output.
4. Optionally, the **upstream endpoint** if you know it.

We cannot fix upstream outages (if RTA's API is down, it is down). But we can update our integration when an endpoint moves, changes shape, or gets replaced.

---

## Knowledge update PRs

If you are filing a PR to refresh stale curated knowledge:

1. Find the relevant JSON file in `src/mcp_dubai/biz/_data/`.
2. Update the affected fields and add or update the authoritative `source_urls`, `source_url`, or canonical `url` reference used by that pack.
3. Advance the top-level `knowledge_date` to today's date only after materially re-verifying the affected fields. For a partial refresh, preserve `full_review_date`, record the old update date in `previous_knowledge_date`, describe the exact boundary in `last_refresh_scope`, and retain section-level `as_of` dates where applicable. Advance `full_review_date` only after reviewing the entire domain. Keep untouched packs and sections on their prior dates.
4. Run `make check` to confirm tests still pass (most knowledge updates require zero code changes).
5. Open the PR with the source URL in the description.

---

## License

By contributing, you agree your contributions are licensed under the MIT License (same as the rest of the project).

---

> هذا المشروع مبادرة مجتمعية مفتوحة المصدر، مرحبًا بمساهماتكم
