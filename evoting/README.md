# E-Voting Platform (Blockchain + Face Recognition)

A production-grade rebuild of the college e-voting project: on-chain votes, biometric
voter authentication, and a modern web stack. Votes are recorded on **Ethereum**
(local Hardhat for dev, **Sepolia** testnet for the demo) — the chain is the source of
truth. Face **enrollment + liveness/PAD** verification is **server-authoritative**: the
browser can never decide that a face matched.

> Demonstration system on a **testnet** — not a mainnet deployment and not intended to run
> a real election. See "Honest limitations" below.

## Architecture

```
Next.js 15 (apps/web)
   │  typed OpenAPI client · JWT
   ▼
Core API — FastAPI (apps/api)
   ├─ PostgreSQL 16   (metadata, voters, encrypted PII, receipts cache, audit)
   ├─ Redis           (rate limits, verification sessions)
   ├─ Biometrics svc  (apps/biometrics — enroll → embedding, liveness → face match)
   └─ Ethereum        (packages/contracts — EVoting.sol; Hardhat local / Sepolia)
```

Two ports are swappable by config so everything runs and is tested offline:

| Port       | Real                    | Dev/test fake        | Env                              |
| ---------- | ----------------------- | -------------------- | -------------------------------- |
| Chain      | web3 → Hardhat/Sepolia | in-memory simulation | `CHAIN_BACKEND=web3\|memory`    |
| Biometrics | HTTP → biometrics svc  | in-process stub      | `BIOMETRICS_BACKEND=http\|fake` |

## Repo layout

```
apps/web         Next.js 15 (App Router, TS strict, Tailwind v4)
apps/api         FastAPI core: auth, admin, verification orchestration, vote relayer, results
apps/biometrics  FastAPI: face embedding + liveness/PAD (internal, token-gated)
packages/contracts  Hardhat + Solidity 0.8.24 (EVoting.sol) + tests + deploy
infra            docker-compose + deploy notes
```

## Quick start (local, no Docker)

Prereqs: Node 20+, pnpm 9+, Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL 16 running.

```bash
cp .env.example .env            # then create the DB: createdb evoting (user/pass per .env)
make install                    # pnpm install + uv sync (api, biometrics)

# Terminal A — local chain
make chain
# Terminal B — deploy, copy the printed address into .env as EVOTING_CONTRACT_ADDRESS
make deploy-local
# then:
make migrate && make seed       # schema + 3 states + bootstrap admin (admin@evoting.com / admin12345)

# Terminals C/D/E — services
make biometrics                 # :8100
make api                        # :8000  (OpenAPI docs at /docs)
make web                        # :3000
```

Open http://localhost:3000. For a **no-ML end-to-end demo** (hash embedder can't match a
live camera), set `FACE_MATCH_THRESHOLD=-1` in `.env` — liveness is still enforced. For
**real face matching**, install the model (`cd apps/biometrics && uv sync --extra insightface`)
and set `FACE_EMBEDDER=insightface`, `FACE_MATCH_THRESHOLD=0.42`.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
# One-time: deploy the contract to the `chain` service and set EVOTING_CONTRACT_ADDRESS,
# then restart `api`  (see infra/docker-compose.yml header).
```

## Deploy to Sepolia (testnet demo)

1. Get a Sepolia RPC URL (Alchemy/Infura) and a funded test account (faucet).
2. In `.env`: set `SEPOLIA_RPC_URL`, `DEPLOYER_PRIVATE_KEY`, and for the API
   `CHAIN_RPC_URL=<sepolia rpc>`, `CHAIN_ID=11155111`, `FUNDER_PRIVATE_KEY=<funded key>`.
3. `pnpm --filter @evoting/contracts deploy:sepolia` → copy the address to
   `EVOTING_CONTRACT_ADDRESS`.
4. Receipts link to `https://sepolia.etherscan.io/tx/<hash>`.

If the testnet is congested, switch `CHAIN_BACKEND=memory` (or run the local Hardhat node)
for the same UI flow.

## Tests / quality gates

```bash
make test          # contracts (Hardhat) + api (ruff/mypy/pytest) + biometrics (ruff/mypy/pytest)
make lint          # web lint
```

- Contracts: 23 tests (one-vote enforcement, access control, lifecycle, pause).
- Core API: full end-to-end vote flow + double-vote / verification-required / unapproved /
  duplicate-Aadhaar rejections. ruff + mypy strict clean.
- Biometrics: enrollment, liveness, match, internal-token auth. ruff + mypy strict clean.

## Security model (highlights)

- **On-chain is source of truth**; DB is a cache/index. One vote per voter per election is
  enforced by the contract (`hasVoted`) **and** the API (idempotent receipt).
- **Server-authoritative verification**: `/voting/cast` requires a fresh, passed, unconsumed
  verification for the voter+election — unfakeable by the client.
- **PII**: Aadhaar is encrypted at rest and salted-hashed for dedup; never on-chain, never
  sent to biometrics, never logged. Passwords use Argon2.
- **Custodial wallets**: keys encrypted with `DATA_ENCRYPTION_KEY`; the relayer signs with the
  voter's key so `msg.sender` is the voter. Every sensitive action is audit-logged.

## Honest limitations

1. Testnet, not mainnet.
2. Custodial wallets — the operator could technically transact as a voter; mitigated by
   encryption + audit, but a real system needs voter-held keys / account abstraction.
3. Aadhaar is simulated (no UIDAI integration).
4. Liveness baseline is challenge-response, not a certified PAD (an InsightFace / anti-spoof
   upgrade is wired but optional).
5. Constituency data is a 3-state sample, extensible via `apps/api/app/seed/data/geo.json`.

See `../UPGRADE_PLAN_2026.md` for the full plan and rationale.
