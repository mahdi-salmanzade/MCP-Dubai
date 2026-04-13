# Pull Request

## Summary

<!-- One or two sentences. What does this PR change? -->

## Type of change

- [ ] Bug fix
- [ ] New `data/*` feature (Tier 0 or Tier 1)
- [ ] New `biz/*` feature (Tier 2 curated knowledge)
- [ ] New tool inside an existing feature
- [ ] Knowledge refresh (curated JSON file update)
- [ ] Documentation
- [ ] CI / tooling
- [ ] Refactor

## Why

<!-- The motivation. What problem does this solve? Link to the issue if relevant. -->

Closes #

## Test plan

<!-- How did you verify this works? -->

- [ ] `make check` passes locally (ruff, mypy, pytest)
- [ ] New tests added with `respx` mocks for any new HTTP path
- [ ] Smoke test: `python -m mcp_dubai` boots without errors
- [ ] Manual test in Claude Desktop or another MCP client (if relevant)

## Project conventions checklist

- [ ] No em dashes (`—` U+2014) or en dashes (`–` U+2013) anywhere in the diff
- [ ] If a new feature: follows the feature folder layout (constants, schemas, client, tools, server, tests)
- [ ] If `biz/*`: has a curated JSON in `_data/`, a per-domain `KNOWLEDGE` constant, and `register_domain_knowledge` call
- [ ] If Tier 1 with credentials: uses graceful credential degradation (`auth.availability()`)
- [ ] If knowledge update: bumped `knowledge_date` and added a `source_urls` entry
- [ ] Tools registered with `ToolDiscovery` via `_TOOLS: list[ToolMeta]`
- [ ] New feature mounted in `src/mcp_dubai/server.py`
- [ ] README updated if the catalogue changed materially
- [ ] CONTRIBUTING checklist followed

## Notes for reviewer

<!-- Anything that needs special attention. Tradeoffs you considered. Open questions. -->
