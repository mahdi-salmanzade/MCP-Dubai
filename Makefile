.PHONY: install dev test lint format typecheck check clean run registry-check

install:
	pip install -e .

dev:
	pip install -e ".[dev,data]"

test:
	pytest

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src

check: lint typecheck test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m mcp_dubai

# Validate server.json against the MCP Registry schema without publishing.
# Install the CLI first: brew install mcp-publisher
registry-check:
	mcp-publisher publish --dry-run
