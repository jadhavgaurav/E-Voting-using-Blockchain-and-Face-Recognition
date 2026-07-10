# Deployment notes

## Contract (Hardhat → Sepolia)

```bash
cd packages/contracts
# .env at repo root must have SEPOLIA_RPC_URL and DEPLOYER_PRIVATE_KEY (funded via faucet)
pnpm deploy:sepolia
# copy the printed address into the root .env: EVOTING_CONTRACT_ADDRESS=0x...
```

The script writes `packages/contracts/deployments/<network>.json` (and `latest.json`) with
the address + ABI. The API loads the ABI from `apps/api/app/chain/evoting_abi.json` (kept in
sync with the contract) and the address from `EVOTING_CONTRACT_ADDRESS`.

## Services (suggested hosting)

- **web** (Next.js, `output: standalone`): Vercel, or the provided Dockerfile on any container host.
- **api** + **biometrics** (FastAPI): any container host (Railway / Fly / Render / AWS ECS).
  Provide Postgres + Redis; set env from `.env.example`. Run `alembic upgrade head` and the
  seed on first boot (the api Dockerfile does this).
- **Postgres 16** and **Redis 7**: managed instances in production.

## Production checklist (beyond demo scope)

- Replace custodial wallets with voter-held keys / account abstraction.
- Move `DATA_ENCRYPTION_KEY` and signing keys into a KMS/HSM or vault.
- Set `FACE_EMBEDDER=insightface` + a certified PAD model; tune `FACE_MATCH_THRESHOLD`.
- Real Redis-backed rate limits (already supported via `REDIS_URL`), WAF, TLS, backups.
- Independent security review of the contract and the vote path.
