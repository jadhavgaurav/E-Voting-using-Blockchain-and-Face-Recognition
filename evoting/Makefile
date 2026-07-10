# Convenience targets for local (non-Docker) development.
# Prereqs on PATH: node 20+, pnpm 9+, python 3.12+, uv, a running PostgreSQL 16.
# Run each long-running target in its own terminal.

.PHONY: help install chain deploy-local migrate seed biometrics api web \
        test test-contracts test-api test-biometrics lint

help:
	@echo "Targets: install | chain | deploy-local | migrate | seed | biometrics | api | web | test | lint"

install:
	pnpm install
	cd apps/api && uv sync --extra dev
	cd apps/biometrics && uv sync --extra dev

# 1) Start a local Hardhat node (terminal A)
chain:
	pnpm --filter @evoting/contracts node

# 2) Deploy the contract to the local node; prints EVOTING_CONTRACT_ADDRESS to put in .env
deploy-local:
	pnpm --filter @evoting/contracts deploy:localhost

# 3) DB schema + seed (3 states + bootstrap admin). Needs DATABASE_URL_SYNC / DATABASE_URL.
migrate:
	cd apps/api && uv run alembic upgrade head

seed:
	cd apps/api && uv run python -m app.seed.seed

# 4) Services (each in its own terminal)
biometrics:
	cd apps/biometrics && uv run uvicorn app.main:app --port 8100 --reload

api:
	cd apps/api && uv run uvicorn app.main:app --port 8000 --reload

web:
	pnpm --filter @evoting/web dev

# ── Tests / quality ──
test: test-contracts test-api test-biometrics

test-contracts:
	pnpm --filter @evoting/contracts test

test-api:
	cd apps/api && uv run ruff check . && uv run mypy app && uv run pytest -q

test-biometrics:
	cd apps/biometrics && uv run ruff check . && uv run mypy app && uv run pytest -q

lint:
	pnpm --filter @evoting/web lint
