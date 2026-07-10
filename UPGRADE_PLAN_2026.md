# E‑Voting Platform — Production‑Grade Upgrade Plan (2026)

> **Status:** Fresh greenfield plan. Supersedes and replaces all prior roadmaps
> (the old `.plan.md`, `IMPLEMENTATION_ROADMAP.html`, and the partial `evoting-system/`
> rebuild — all deleted; the partial rebuild remains recoverable in git history at commit `78aac81`).
>
> **Target:** Portfolio / demo‑grade production. It must look and behave like a real
> product running on a public Ethereum **testnet** (Sepolia) with a local dev chain —
> not a mainnet deployment, and not run for a real government election.
>
> **Author's stance:** This is a full rewrite. No legacy application code is reused.
> The legacy repo is kept only as a domain reference and as a "before" artifact.

---

## Part 0 — TL;DR

| Layer | Legacy (today) | Upgrade (target) |
| --- | --- | --- |
| Web | PHP + jQuery on XAMPP (125 `.php` files) | **Next.js 15** (App Router, TS strict, Tailwind v4, shadcn/ui) |
| Backend | Loose PHP scripts, raw SQL | **FastAPI** (Python 3.12, async SQLAlchemy 2, Pydantic v2, `uv`) |
| Blockchain | Homemade toy chain on `localhost:8080` + a broken Truffle contract | **Solidity 0.8.24** on **Hardhat**, deployed to local + **Sepolia**, `ethers v6` relayer |
| Face auth | Flask KNN, raw images on disk, **client‑trusted** result | **InsightFace/ArcFace embeddings** + **liveness/PAD**, server‑authoritative |
| Data | MySQL, plaintext passwords, SQL injection | **PostgreSQL 16**, Argon2 hashes, parameterized ORM, encrypted PII |
| Identity | Aadhaar as vote key, raw in DB | Email/password auth + **hashed+encrypted Aadhaar**, custodial wallet mapping |
| Infra | Manual XAMPP setup | **Docker Compose**, **Turborepo** monorepo, **GitHub Actions** CI |
| Tests | None | Hardhat/chai, pytest, Vitest, **Playwright** E2E |

**Two hard rules that define this project:**
1. **On‑chain is the source of truth for votes.** The database is a cache/index for UI and metadata — never the authority on who won.
2. **The client is never trusted.** Face match, liveness, authorization, and "already voted" are all decided server‑side and enforced by the contract.

---

## Part 1 — Review of the Existing Project

### 1.1 What exists

```
E-Voting-using-Blockchain-and-Face-Recognition/
├── Source code/                     # LEGACY — reference only, not reused
│   ├── An_OnlineVotingQR_Admin/     # PHP admin panel (elections, candidates, results)
│   ├── An_OnlineVotingQR_User/      # PHP voter panel + Flask face service (python/faceknn)
│   ├── Blockchain/                  # Truffle project, Votingsol.sol
│   └── db/evoting.sql               # MySQL schema
├── Paper and report/                # Research paper, IEEE-style report, PPT, log book
├── refference templates/            # Report/appendix templates (academic)
├── data/                            # Abstract, Gantt charts, diagrams
└── README.md                        # Describes the legacy PHP/XAMPP stack
```

Stack per the README: PHP + jQuery on Apache/XAMPP, MySQL, a Flask `face_recognition` KNN
service, and Ethereum/Truffle/Ganache with Solidity `^0.8.0`.

### 1.2 The research paper's thesis (what we must preserve)

The paper — *"A Framework to Make Voting System Transparent Using Blockchain Technology"* —
argues for **transparency and immutability of votes via blockchain** plus **biometric voter
authentication**. That thesis is sound and is exactly what the upgrade delivers properly.
The academic deliverables (report, log book, references, diagrams) are untouched by this plan
and can be updated to describe the new architecture once built.

### 1.3 Critical findings (grounded in the actual code)

These are confirmed by reading the source, not inherited from the old plan:

**Blockchain (`Blockchain/contracts/Votingsol.sol`)**
1. **Double voting is fully enabled.** In `vote()`, the `getVoter()` guard is commented out.
   The same address can vote unlimited times. `require(id >= 0 && …)` is a no‑op (`uint >= 0`).
2. **`addCandidate` is public** — anyone can add candidates.
3. **`addVoter` is public** — anyone can set `votedUser[addr][name]`, corrupting the "has voted" map.
4. **Free‑text `electionName` strings on‑chain** — `getCandidates` loops all candidates doing
   `keccak256` string compares. Gas‑heavy, unbounded, abuse‑prone.
5. **The real vote path doesn't even use Ethereum.** `castVote.php` POSTs to a homemade Python
   "blockchain" at `http://localhost:8080/transactions` then `/mine`. The `txhash` is supplied
   **by the client**. This is not a blockchain guarantee at all.

**Web / Backend (PHP)**
6. **SQL injection everywhere.** e.g. `castVote.php` concatenates `$_POST['aadhar']`,
   `$candidate`, etc. straight into `INSERT INTO votes …`. Same pattern in login/voter fetches.
7. **Plaintext passwords** stored and compared directly.
8. **Client‑trusted face verification.** The browser proceeds to voting when the face API
   returns `status:true`; nothing server‑side ties that verification to the vote write.
9. **Aadhaar is the vote identity and is stored raw** in `votes.voter` and `voterinfo.vaadhar`.

**Face service (`python/faceknn/face_recognition_knn_web.py`)**
10. **No auth, CORS wide open, raw images persisted** under `Register/{email}/`, KNN pickle model.
11. **No liveness / anti‑spoofing** — a printed photo or a video replay passes.

**Systemic**
12. **Two conflicting sources of truth** (toy chain + MySQL) with no reconciliation, no uniqueness
    on `(voter, election)`, no idempotency.

### 1.4 Verdict

- **Reuse:** none of the application code. **Concept reuse only** — the domain model
  (voters, elections, candidates, constituencies, votes) and the enroll→verify→vote flow.
- **Rewrite:** everything, greenfield, in the target stack below.

---

## Part 2 — Target Architecture

### 2.1 Monorepo layout (Turborepo + pnpm workspaces)

```
evoting/
├── apps/
│   ├── web/            # Next.js 15 (App Router, TS strict, Tailwind v4, shadcn/ui)
│   ├── api/            # FastAPI — core app (auth, admin, voting, relayer, results)
│   └── biometrics/     # FastAPI — face enrollment + liveness/PAD (separate service)
├── packages/
│   ├── contracts/      # Hardhat + Solidity 0.8.24 + tests + deploy scripts
│   ├── shared-types/   # OpenAPI-generated TS client + shared enums/DTOs
│   └── config/         # Shared ESLint/tsconfig/prettier presets
├── infra/
│   ├── docker-compose.yml     # postgres, redis, hardhat-node, api, biometrics, web
│   └── deploy/                # Sepolia + cloud deploy guides
├── .github/workflows/         # CI: contracts, api, biometrics, web, e2e
├── turbo.json
└── README.md
```

**Why two FastAPI services?** The biometrics service is CPU/GPU‑heavy (embedding models) and
has a different scaling and dependency profile (dlib/onnxruntime) than the transactional core
API. Splitting them is the honest "scalable" answer and keeps the core API image small. They
communicate over internal HTTP with a shared secret; the core API is the only public surface
for biometrics (it proxies, so the biometrics service is never exposed to the browser).

### 2.2 System diagram

```
                         ┌───────────────────────────────────────────┐
                         │  Browser (Next.js 15, React Server Comps)  │
                         │  Admin console · Voter flow · Receipt view │
                         └───────────────┬───────────────────────────┘
                                         │ HTTPS · typed OpenAPI client · JWT
                                         ▼
        ┌────────────────────────────────────────────────────────────────┐
        │  Core API (FastAPI, async)                                       │
        │  auth · admin CRUD · enrollment proxy · verification orchestr.   │
        │  vote relayer (ethers/web3.py) · results · receipts · audit      │
        └───┬───────────────┬──────────────────┬───────────────┬──────────┘
            │ SQLAlchemy 2  │ Redis            │ internal HTTP │ JSON-RPC (ethers v6)
            ▼               ▼                  ▼               ▼
     ┌────────────┐  ┌────────────┐   ┌──────────────────┐  ┌────────────────────┐
     │ PostgreSQL │  │  Redis     │   │ Biometrics svc   │  │ Ethereum            │
     │ metadata,  │  │ sessions,  │   │ (FastAPI)        │  │ · Local: Hardhat    │
     │ voters,    │  │ rate limit,│   │ enroll→embedding │  │ · Demo:  Sepolia    │
     │ receipts   │  │ verify TTL │   │ liveness/PAD     │  │ EVoting.sol         │
     │ cache,     │  │ job queue  │   │ face match       │  │ events + tally      │
     │ audit      │  └────────────┘   └──────────────────┘  └────────────────────┘
     └────────────┘
```

### 2.3 Definitive stack

| Concern | Choice | Notes |
| --- | --- | --- |
| Frontend | Next.js 15, React 19, TS strict, Tailwind v4, shadcn/ui, TanStack Query | Server Components for reads; client components for camera/vote flow |
| API | FastAPI, Python 3.12, `uv`, async SQLAlchemy 2, Pydantic v2, Alembic | mypy strict, ruff |
| Auth | JWT access+refresh, `argon2-cffi` password hashing, `python-jose` | httpOnly refresh cookie |
| DB | PostgreSQL 16 | async driver `asyncpg` |
| Cache/queue | Redis 7 | rate limiting, verification sessions, receipt‑indexer jobs |
| Contracts | Solidity 0.8.24, Hardhat, OpenZeppelin `AccessControl` | tests in TS (chai) |
| Chain client | `ethers v6` in a Node relayer **or** `web3.py` in FastAPI | see 4.4 for the relayer decision |
| Biometrics | InsightFace (ArcFace embeddings) + OpenCV; liveness challenge baseline; Silent‑Face‑Anti‑Spoofing optional | onnxruntime, no raw image retention |
| Secrets/crypto | Fernet/AES‑GCM for Aadhaar + wallet keys; env‑injected KEK | never in repo |
| Infra | Docker Compose (dev), Turborepo, GitHub Actions | |
| Testing | Hardhat/chai · pytest · Vitest · Playwright | |
| Observability | `structlog` JSON logs + request_id; Sentry; `/health` + `/ready` | OTel optional |

---

## Part 3 — Domain Model & Constituency System

Keep the ECI‑style hierarchy from the research (it's the project's identity) but **scale it for a
demo**: seed **3 states fully** (e.g. Maharashtra, Karnataka, Delhi) with real district/AC/PC
data, and make the seed pipeline data‑driven so more states drop in later.

```
Country → State/UT → District → Assembly Constituency (AC) → [maps to] Parliamentary Constituency (PC)
                                        └→ Local Body (ward/panchayat)
```

**Election types:** Parliamentary (Lok Sabha), State Assembly (Vidhan Sabha), Local.
A voter registers at **AC granularity** (the base unit); PC is derived; local bodies attach to AC.

### Core tables (PostgreSQL)

- **Geography:** `states`, `districts`, `parliamentary_constituencies`, `assembly_constituencies`
  (FK district + FK PC), `local_bodies` (FK AC).
- **`voters`**: id, email (unique), password_hash (argon2), full_name, dob, gender,
  aadhaar_encrypted, aadhaar_hash (unique — dedup), assembly_constituency_id,
  blockchain_address (unique), wallet_key_encrypted, status (`pending|accepted|rejected`),
  timestamps.
- **`admins`**: id, email, password_hash, role.
- **`elections`**: id, chain_election_id (uint256 mirror), name, type, scope (state/all‑India),
  start_at, end_at, status (`draft|active|closed`), result_published (bool).
- **`election_constituencies`**: election_id + (pc_id | ac_id | local_body_id).
- **`candidates`**: id, election_constituency_id, name, party, symbol_url, chain_candidate_index.
- **`enrollment_templates`**: voter_id (unique), template_encrypted (embedding bytes),
  algorithm_version, created/updated_at. **No raw images.**
- **`verification_logs`**: id, voter_id, election_id?, request_id (unique), passed,
  face_score, pad_result, pad_score, created_at.
- **`on_chain_receipts`**: voter_id, election_id, tx_hash, block_number, event_data(json) — UI cache.
- **`audit_events`**: actor_type, actor_id, action, resource, details(json), ip, request_id, ts.

All PII columns are encrypted at rest; Aadhaar is **never** sent to the biometrics service or on‑chain.

---

## Part 4 — Smart Contract Design (blockchain‑first)

### 4.1 Contract responsibilities & invariants

- **Election lifecycle:** admin creates an election with numeric `electionId` and `[start,end]`
  window. Votes accepted only within the window.
- **Candidates:** admin‑only, added before start, addressed by `(electionId, candidateIndex)`.
  **No free‑text names on‑chain** — names/symbols live off‑chain, keyed by index.
- **One vote per address per election:** `hasVoted[electionId][msg.sender]` set true on vote;
  second attempt reverts.
- **Tally on‑chain:** `candidateVoteCount[electionId][index]` incremented; `VoteCast` event emitted.
- **`msg.sender` is the voter.** The relayer submits a tx **signed by the voter's custodial key**,
  so identity is the voter's address — the contract never trusts a "on behalf of" parameter.

### 4.2 Access control & safety

- OpenZeppelin `AccessControl` with `ADMIN_ROLE` (create election, add candidates, pause).
- Custom errors (`AlreadyVoted`, `InvalidCandidate`, `ElectionNotStarted`, `ElectionEnded`,
  `ElectionDoesNotExist`, `InvalidElectionWindow`) — cheaper and clearer than string reverts.
- `Pausable` for emergency stop. No unbounded loops in state‑changing paths.
- Reentrancy is N/A (no external calls / value transfer), but keep checks‑effects‑interactions.

### 4.3 Sealed results (optional, Phase 5)

Baseline ships **open tally** (counts visible as votes come in). If "sealed until close" is
desired for realism, add a **commit‑reveal** variant: `commitVote(electionId, hash)` during the
window, `revealVote(electionId, candidateIndex, salt)` after close. Ship the simple version first;
gate commit‑reveal behind a config flag so the UI path is identical.

### 4.4 The relayer decision (custodial wallets)

Voters do **not** manage MetaMask/gas — this is the UX the paper implies. The backend:
1. On registration, generates an HD‑derived custodial wallet per voter; stores the key **encrypted**.
2. On vote, **checks `hasVoted` on‑chain**, then signs the `vote()` tx with the voter's key and
   submits it. Testnet gas is funded from a faucet‑topped deployer/funder account.

> **Documented trade‑off:** custodial keys mean the operator can technically vote as a user — this
> is called out explicitly as a demo limitation. A real system would use account abstraction /
> voter‑held keys. We keep custodial for demo UX but isolate keys, encrypt at rest, and log every
> relayer action to `audit_events`.

### 4.5 Contract test plan (Hardhat/chai, runs on local chain in CI)

create election · admin‑only candidate add · reject non‑admin · vote once · **reject double vote**
· reject invalid candidate/election · reject outside window · event emission · tally correctness ·
pause blocks voting · (commit‑reveal cases if enabled). Add a small fuzz pass on ids/bounds.

---

## Part 5 — AI Biometrics Design (server‑authoritative)

### 5.1 Enrollment
Capture 1–3 frames → detect face (reject none/multiple) → compute **ArcFace embedding** →
encrypt → store vector only in `enrollment_templates`. **No raw image retention** by default.

### 5.2 Verification (order matters — fail closed)
1. **Liveness / PAD first.** Baseline: active challenge (blink / head‑turn) with motion+blink
   detection; reject static images. Optional upgrade: Silent‑Face‑Anti‑Spoofing passive model.
2. **Face match second.** Embed submitted frame → cosine similarity vs stored template →
   threshold (configurable, ~0.35–0.5).
3. Persist a `verification_log` (pass/fail, scores, pad_result, request_id) **every** attempt.

### 5.3 The trust chain (this is the whole point)
- `POST /verification/start` issues a `request_id` + challenge, stored in Redis with a short TTL.
- The vote endpoint **requires a fresh, passed `verification_log` for that voter+election+request_id**
  before it will relay a tx. The browser cannot fabricate this — it's checked in the DB/Redis.
- Rate‑limited per voter and per IP; all failures logged.

### 5.4 Privacy
Aadhaar never reaches this service. Embeddings are encrypted. Logs hold scores and IDs, not images.

---

## Part 6 — Backend API (FastAPI)

### 6.1 Endpoint groups
- **Constituency (public):** `GET /geo/states`, `/geo/states/{id}/districts`,
  `/geo/districts/{id}/assemblies`, `/geo/assemblies/{id}` (returns derived PC) — cascading dropdowns.
- **Auth:** `POST /auth/register` (validates email/password/Aadhaar/AC; hashes+encrypts Aadhaar;
  creates custodial wallet), `POST /auth/login` → JWT, `POST /auth/refresh`, `POST /auth/logout`.
- **Enrollment:** `POST /enrollment/face` (auth, multipart → proxies biometrics), `GET /enrollment/status`.
- **Verification:** `POST /verification/start`, `POST /verification/face` (liveness+match).
- **Voting:** `GET /voting/elections` (active for voter's constituency), `/elections/{id}/candidates`,
  `POST /voting/cast` (checks verification log + on‑chain `hasVoted`, relays tx, returns receipt).
- **Receipts:** `GET /voting/receipts`, `GET /voting/receipts/{tx_hash}`,
  public `GET /verify/{tx_hash}` (re‑reads chain).
- **Admin:** elections CRUD, candidate CRUD (mirrors to chain), voter approve/reject,
  `GET /admin/results/{id}`, `GET /admin/audit`.

### 6.2 Cross‑cutting
Pydantic v2 validation on all I/O · JWT + role guard on `/admin/*` · DB transactions for
multi‑step writes (voter+wallet+template rollback together) · idempotency key on `/voting/cast` ·
generic error envelopes (no stack traces) with `request_id` · OpenAPI spec drives the TS client.

---

## Part 7 — Frontend (Next.js 15)

- **Admin:** login · dashboard (elections) · create/edit election · manage candidates ·
  voter approvals · live results (from chain) · audit export.
- **Voter:** register (cascading geo dropdowns + face enrollment) · login · dashboard of active
  elections · **vote flow** (confirm Aadhaar → pick election → liveness challenge → face capture →
  cast → receipt with tx hash + Etherscan link).
- **Receipt verify:** paste tx hash → show status, `VoteCast` event, election/candidate index,
  explorer link.
- **Engineering:** Server Components for reads; client components for camera + tx pending states;
  global error boundary; typed OpenAPI client; Zod‑validated responses; skeleton/loading/disabled
  states; "already voted" → 409 handling; a11y (labels, focus, contrast).

---

## Part 8 — Security Model

Top threats and mitigations:
1. **Verification bypass** → server‑authoritative trust chain (§5.3); no client boolean is trusted.
2. **Double voting** → contract `hasVoted` + backend pre‑check + DB idempotency on `/voting/cast`.
3. **Aadhaar/PII leakage** → encrypted at rest, hashed for dedup, never on‑chain, never to biometrics,
   never logged.
4. **Injection / auth bypass** → ORM parameterization only, Pydantic validation, argon2, JWT+roles.
5. **Key compromise** → custodial keys encrypted with env/vault KEK; relayer actions audited;
   deployer/funder key separate from voter keys.
6. **DoS / abuse** → Redis rate limits on auth/enroll/verify/cast; image size/type caps; pause switch.
7. **Spoofing** → liveness before match; optional PAD model.

Non‑negotiables: no secrets in repo · `.env.example` only · no PII in logs · every sensitive action
writes an `audit_event` with `request_id`.

---

## Part 9 — DevOps, CI/CD, Testnet

- **Local dev:** `docker compose up` → postgres + redis + hardhat‑node + api + biometrics + web.
  Alembic migrations + geo seed run on boot. Contract auto‑deploys to the local node; address/ABI
  written to a shared artifact the API reads.
- **Testnet demo:** deploy `EVoting.sol` to **Sepolia** (fallback **Holesky**). Env: `RPC_URL`,
  `DEPLOYER_PRIVATE_KEY`, `CHAIN_ID`, `CONTRACT_ADDRESS`. Faucet‑funded funder account. UI shows
  real `sepolia.etherscan.io` receipt links. **Fallback demo mode** switches to the local chain
  with the identical UI if the testnet is congested.
- **CI (GitHub Actions):** matrix jobs — contracts (`hardhat test` on local chain, no external RPC),
  api (`uv sync --frozen`, ruff, mypy, pytest), biometrics (lint + unit), web (typecheck, lint,
  vitest, `next build`), and a Playwright E2E job against `docker compose`. Green required to merge.
- **CI security rule:** no job depends on Sepolia; no private keys or RPC secrets in the repo/CI logs.

---

## Part 10 — Phased Roadmap

Each phase ends with a **demoable** increment and green CI. Effort: S ≈ days, M ≈ 1–2 wks, L ≈ 2–3 wks.

### Phase 0 — Foundations · P0 · M
Turborepo + pnpm workspaces; `uv` API scaffold; Docker Compose (pg+redis+hardhat); ESLint/Prettier,
ruff/mypy; GitHub Actions skeleton; `.env.example`; geo schema + Alembic + **seed 3 states**;
cascading geo endpoints live.
**Done when:** `docker compose up` boots everything; CI green; geo dropdowns work end‑to‑end.

### Phase 1 — Blockchain Core · P0 · L
`EVoting.sol` (AccessControl, custom errors, one‑vote, lifecycle, events, pause); deploy scripts
(local + Sepolia); full Hardhat test suite; ABI/address artifact consumed by API.
**Done when:** all contract tests pass; deploys to local and Sepolia; double‑vote reverts.

### Phase 2 — Biometrics Core · P0 · L
Biometrics FastAPI: enrollment (embedding, encrypted store), verification (liveness → match),
`verification_logs`, rate limits; unit + spoof/negative integration tests.
**Done when:** verification is server‑authoritative; no raw images stored; spoof frames fail liveness.

### Phase 3 — End‑to‑End Vote · P0 · L
Core API: register (Aadhaar hash+encrypt, custodial wallet), JWT auth, verification orchestration,
**vote relayer** (pre‑check `hasVoted` → sign → submit), receipts. Next.js voter flow + admin CRUD.
Playwright E2E: one voter completes the flow once; duplicate rejected by contract **and** backend.
**Done when:** a voter votes once on Sepolia and sees a real Etherscan receipt; second attempt 409s.

### Phase 4 — Results & Audit · P1 · M
Results computed from chain (optional event indexer worker → `on_chain_receipts`); admin results
dashboard; audit export (CSV/JSON, non‑sensitive); "source: chain" disclaimer on any indexed view.
**Done when:** dashboard tally matches chain state exactly.

### Phase 5 — Hardening · P1 · M
Rate‑limit tuning; abuse tests (replay verification, double vote, invalid tokens, concurrency);
structured logging + request_id propagation; `/health`+`/ready`; Sentry; optional PAD model;
optional commit‑reveal sealed results.
**Done when:** abuse suite documents expected behavior; no PII in logs.

### Phase 6 — Demo Polish · P2 · M
UX copy + loading/pending states; a11y pass; Sepolia + cloud deploy guide (e.g. Vercel + a
container host); demo script; update the academic report/diagrams to the new architecture.
**Done when:** a reviewer can run the demo from the README on testnet in one sitting.

---

## Part 11 — Engineering Standards (repo constitution)

- **TypeScript:** strict, no `any`; Zod‑validate external/API data; explicit return types.
- **Python:** mypy strict; Pydantic v2 at every boundary; `uv.lock` committed; `uv sync --frozen` in CI.
- **Solidity:** custom errors; access control on every state mutator; no unbounded loops; tests
  for every branch; never comment out a `require`/role check.
- **No client‑side trust:** authorization, verification, and "already voted" enforced server‑side + on‑chain.
- **Migrations:** Alembic only; no ad‑hoc SQL; reviewed.
- **Errors:** generic messages to clients, detail only in structured logs; `request_id` everywhere.
- **Secrets:** env/vault only; `.env.example` documents keys; nothing sensitive committed.
- **PRs:** tests + types + lint green; no secrets; docs updated when behavior changes.

### AI‑agent guardrails (for any assistant working in this repo)
Small focused diffs · never weaken contract checks or verification flows · every change to
contract/auth/verify/vote paths ships tests · update OpenAPI + regenerated TS client when schemas
change · human review required for storage‑layout changes, identity mapping, thresholds, and key handling.

---

## Part 12 — Honest Limitations (state these in the demo)

1. **Testnet, not mainnet.** Sepolia has no economic finality guarantees of mainnet.
2. **Custodial wallets.** Operator can technically transact as a voter; mitigated by encryption +
   audit, but a real election needs voter‑held keys / account abstraction.
3. **Aadhaar is simulated.** No real UIDAI integration; treated as an opaque encrypted identifier.
4. **Liveness baseline is challenge‑response**, not a certified PAD; PAD model is an optional upgrade.
5. **Constituency data is a 3‑state sample**, extensible via the seed pipeline.

---

*Next step:* on approval, I scaffold **Phase 0** (monorepo + Docker Compose + geo seed + CI) as the
first working increment.
