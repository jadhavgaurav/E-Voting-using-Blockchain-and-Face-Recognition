# E-Voting System (Phase 1 — Blockchain Core)

On-chain voting contract for the E-Voting 2026 rebuild: election lifecycle, admin-only candidate registration, and one-vote-per-address with event-driven tally. Built with Hardhat, Solidity 0.8.24, and OpenZeppelin AccessControl.

## Prerequisites

- Node.js 20+
- pnpm 9+

## Install

From the repo root:

```bash
cd evoting-system/contracts
pnpm install
```

## Commands

- **Compile**: `pnpm run compile`
- **Test**: `pnpm run test` (runs on Hardhat in-process; no external RPC)
- **Local node**: `pnpm run node` (start a persistent local chain in another terminal)
- **Deploy (localhost)**: Start the node, then `pnpm run deploy:localhost` (or `pnpm run deploy --network localhost`)
- **Deploy (Sepolia)**: Set `RPC_URL` and `DEPLOYER_PRIVATE_KEY` in `.env`, then `pnpm run deploy:sepolia`

Deployment writes the contract address and ABI path to `contracts/deployments/default.json`. The backend can read this or use `EVOTING_CONTRACT_ADDRESS` from env. See [docs/backend-consumption.md](docs/backend-consumption.md) for ABI location, chain IDs, and relayer usage.

## Project layout

- `contracts/` — Hardhat project (Solidity, deploy script, tests)
- `docs/backend-consumption.md` — How the API/relayer consumes the contract
- `.env.example` — Env template (copy to `.env`; do not commit `.env` or private keys)

Keys and live Sepolia addresses are not committed; use `.env` or a vault for deployment.
