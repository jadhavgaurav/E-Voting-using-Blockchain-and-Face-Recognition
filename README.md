# E-Voting System using Blockchain and Face Recognition

Secure, transparent e-voting: votes recorded on **Ethereum** (immutable, one-vote-per-voter)
with **server-authoritative face + liveness** voter authentication.

> **This project was rebuilt to a production-grade stack in [`evoting/`](./evoting/).**
> The original PHP/XAMPP + Flask-KNN + Truffle implementation under [`Source code/`](./Source%20code/)
> is kept only as a reference ("before" state). See the full plan and rationale in
> [`UPGRADE_PLAN_2026.md`](./UPGRADE_PLAN_2026.md).

## The rebuild (`evoting/`)

| Layer | Now |
| --- | --- |
| Web | **Next.js 15** (App Router, TypeScript strict, Tailwind v4) |
| Backend | **FastAPI** (async SQLAlchemy 2, Pydantic v2, `uv`) + a separate **biometrics** service |
| Blockchain | **Solidity 0.8.24** on **Hardhat**, deployed to local + **Sepolia**, `web3.py` relayer |
| Face auth | **Embeddings + liveness/PAD**, server-authoritative (no client trust) |
| Data | **PostgreSQL 16**, Argon2 passwords, encrypted Aadhaar, chain-sourced results |
| Infra | **Turborepo** monorepo, **Docker Compose**, **GitHub Actions** CI |

**Getting started, architecture, demo script, and deploy notes:** see [`evoting/README.md`](./evoting/README.md)
and [`evoting/docs/DEMO.md`](./evoting/docs/DEMO.md).

## Why the rebuild

The original code had the votes running through a homemade `localhost:8080` "blockchain"
(with a client-supplied tx hash), an on-chain contract with double-voting enabled and public
`addCandidate`/`addVoter`, SQL-injectable PHP, plaintext passwords, and client-trusted face
verification. The rebuild puts votes on real Ethereum, enforces one-vote in the contract,
encrypts PII, and makes every trust decision on the server. Details in
[`UPGRADE_PLAN_2026.md`](./UPGRADE_PLAN_2026.md).

## Repository layout

```
evoting/                 ← the production-grade rebuild (start here)
UPGRADE_PLAN_2026.md     ← review of the old project + full upgrade plan
Source code/             ← legacy PHP/Flask/Truffle implementation (reference only)
Paper and report/        ← research paper, IEEE-style report, PPT, log book
data/ , refference templates/   ← academic artifacts
```
