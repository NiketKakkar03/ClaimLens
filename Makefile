.PHONY: install install-spark check test web-check build-local build-lakehouse docker-lakehouse drift-report demo app monitoring serve

install:
	uv sync --extra dev --extra training

install-spark:
	uv sync --extra dev --extra training --extra spark

check:
	uv run ruff format --check .
	uv run ruff check .

test:
	uv run pytest

web-check:
	cd frontend && npx --yes pnpm@10.20.0 lint && npx --yes pnpm@10.20.0 build

build-local:
	uv run claims-intelligence build-local

build-lakehouse:
	uv run claims-intelligence build-lakehouse

docker-lakehouse:
	docker compose --profile data run --rm lakehouse

drift-report:
	uv run claims-intelligence drift-report

demo:
	./scripts/demo_local.sh

app:
	docker compose up --detach --build keycloak postgres reviewer-api reviewer-web

monitoring:
	docker compose --profile monitoring up --detach inference-api prometheus grafana

serve:
	uv run uvicorn claims_intelligence.serving.api:app --host 0.0.0.0 --port 8000
