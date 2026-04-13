"""
Curated JSON data files for biz/* features.

Loaded via `mcp_dubai.biz._data.loader.load_data_file(name)` which uses
importlib.resources so the files work both in editable installs and inside
a built wheel.

Each JSON file uses a top-level envelope with `domain`, `knowledge_date`,
`volatility`, `verify_at`, `source_brief_section`, plus a domain-specific
data block.
"""
