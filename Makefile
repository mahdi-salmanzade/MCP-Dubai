.PHONY: install dev test lint format format-check typecheck check clean run registry-check freshness

install:
	pip install -e .

dev:
	pip install -e ".[dev,data]"

test:
	pytest

lint:
	ruff check src tests scripts

format:
	ruff format src tests scripts

format-check:
	ruff format --check src tests scripts

typecheck:
	mypy src

check: lint format-check typecheck test freshness

# Report which knowledge domains are overdue for a full review.
# Informational by default; add --strict to make it exit non-zero.
freshness:
	python scripts/check_knowledge_freshness.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m mcp_dubai

# Validate server.json against the MCP Registry schema without publishing.
# Install the CLI first: brew install mcp-publisher
registry-check:
	mcp-publisher validate server.json
