"""
MCP-Dubai biz/* features.

These are curated business knowledge tools that do not call external APIs.
Each feature reads from a JSON file in `_data/`, returns a `ToolResponse`
envelope with a `KnowledgeMetadata` block, and registers its per-domain
`KNOWLEDGE` constant with the shared knowledge registry on import.
"""
