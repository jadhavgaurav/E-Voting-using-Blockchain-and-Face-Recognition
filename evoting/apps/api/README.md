# E-Voting Core API

FastAPI service: voter auth, admin console, biometric-verification orchestration, the
on-chain **vote relayer**, receipts, and chain-sourced results.

## Ports & adapters (why it runs offline)

Two dependencies are swappable by config so the whole flow is testable/dev-runnable
without a node or the biometrics service:

| Port | Real adapter | Fake/dev adapter | Selector |
| --- | --- | --- | --- |
| Chain | `web3` (Hardhat/Sepolia) | in-memory simulation | `CHAIN_BACKEND=web3\|memory` |
| Biometrics | HTTP to the biometrics service | in-process stub | `BIOMETRICS_BACKEND=http\|fake` |

## Commands (from `apps/api/`)

```bash
uv sync --extra dev            # install
uv run ruff check .            # lint
uv run mypy app                # type-check (strict)
uv run pytest                  # tests (SQLite + memory chain + fake biometrics)

# Migrations (needs Postgres; set DATABASE_URL_SYNC)
uv run alembic upgrade head

# Seed geography (3 states) + bootstrap admin
uv run python -m app.seed.seed

# Run the API
uv run uvicorn app.main:app --port 8000 --reload
```

## Security model

- Server-authoritative verification: `/voting/cast` requires a fresh, passed,
  unconsumed `VerificationLog` for the voter + election — the browser cannot fake it.
- One vote per voter per election: DB idempotency **and** the contract's `hasVoted`.
- Aadhaar is encrypted at rest + salted-hashed for dedup; never on-chain, never logged.
- Custodial wallet keys are encrypted with `DATA_ENCRYPTION_KEY`; the relayer signs with
  the voter's key so `msg.sender` is the voter.

See the repository `UPGRADE_PLAN_2026.md` for the full architecture.
