.PHONY: install check test build-local serve

install:
	uv sync --extra dev

check:
	uv run ruff format --check .
	uv run ruff check .

test:
	uv run pytest

build-local:
	uv run claims-intelligence build-local

serve:
	uv run uvicorn claims_intelligence.serving.api:app --host 0.0.0.0 --port 8000
