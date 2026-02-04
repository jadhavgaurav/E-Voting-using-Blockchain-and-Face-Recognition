---
name: E-Voting 2026 Rebuild Plan
overview: End-to-end implementation plan for rebuilding the E-Voting system with blockchain (on-chain vote storage, backend custodial wallets mapped to hashed Aadhar) and AI biometrics (face recognition + liveness/PAD), using Next.js, FastAPI, PostgreSQL, and Solidity on a free public testnet with local dev chain support.
todos: []
isProject: false
---

# E-Voting 2026 Rebuild — Implementation Plan

---

## 1. Executive Summary

- **Blockchain** and **AI biometrics** are the two P0 pillars; backend, admin/voter workflows, and audit UI are P1; polish and scalability are P2.
- **Source of truth**: Model A — on-chain votes are canonical; off-chain DB holds election metadata, candidate mirror, biometric logs, and indexing cache.
- **Voter identity**: Email + password for auth; Aadhar mandatory, encrypted in DB and hashed for uniqueness; **1:1 mapping** (hashed Aadhar ↔ unique custodial blockchain address) in backend.
- **Voting UX**: Backend relayer signs and submits transactions; voters do not manage wallets; Aadhar re-entered at vote time to fetch constituency and active elections.
- **Results**: Sealed until election close (commitment-reveal on-chain); tally computed from chain events/state.
- **Legacy findings**: PHP + Flask + Truffle; contract allows public candidate creation and has commented-out double-vote check; face API has no auth/liveness; client trusts verification result; dual DB+chain storage with no single policy — **full rewrite** with no reuse of legacy app code; contract logic and data flows inform redesign only.
- **Testnet**: Primary Sepolia (Ethereum); fallback Holesky; local Hardhat network for CI and fast dev.
- **AI verification**: Server-authoritative only; liveness/PAD first (baseline: blink/head-turn), then face recognition; all decisions logged (score, PAD result, request id).
- **Stack**: Next.js (TypeScript strict) + FastAPI (Python 3.12+) + PostgreSQL 16+ + Solidity (Hardhat) + ethers.js in backend relayer; biometrics as FastAPI module or separate service; **uv** for Python dependency management (10-100x faster than pip, cross-platform lockfile).
- **CI**: GitHub Actions — typecheck, lint, tests for web, API, contracts; contract tests run on local chain only.
- **Deployment**: Docker Compose for local dev; optional cloud deployment guide in Phase 6.
- **Security**: No client-side trust for verification or authorization; encrypted Aadhar and embeddings; no secrets in repo; rate limiting and audit logging throughout.
- **Constituency System**: 10 major Indian states with real ECI data; hierarchical selection (State → District → Assembly Constituency); supports Parliamentary, State Assembly, and Local elections; Assembly Constituency as base unit maps to Parliamentary; ~344 Lok Sabha + ~2,265 Vidhan Sabha constituencies.

---

## 1.1 Constituency System (ECI-Style)

### 10 States Coverage (Geographic Diversity)


| #   | State          | Region  | Lok Sabha (PC) | Vidhan Sabha (AC) | Districts |
| --- | -------------- | ------- | -------------- | ----------------- | --------- |
| 1   | Maharashtra    | West    | 48             | 288               | 36        |
| 2   | Tamil Nadu     | South   | 39             | 234               | 38        |
| 3   | Karnataka      | South   | 28             | 224               | 31        |
| 4   | Gujarat        | West    | 26             | 182               | 33        |
| 5   | Uttar Pradesh  | North   | 80             | 403               | 75        |
| 6   | West Bengal    | East    | 42             | 294               | 23        |
| 7   | Rajasthan      | North   | 25             | 200               | 33        |
| 8   | Madhya Pradesh | Central | 29             | 230               | 52        |
| 9   | Kerala         | South   | 20             | 140               | 14        |
| 10  | Delhi (NCT)    | North   | 7              | 70                | 11        |
|     | **Total**      |         | **~344**       | **~2,265**        | **~346**  |


### Electoral Hierarchy

```
Country (India)
└── State/UT (10 states)
    └── District (~346 districts)
        └── Assembly Constituency (Vidhan Sabha) - ~2,265 total
            └── Parliamentary Constituency (Lok Sabha) - ~344 total
                (Multiple Assembly constituencies → 1 Parliamentary constituency)
            └── Local Bodies (Ward/Panchayat) - sample wards per AC
```

### Election Types Supported

1. **Parliamentary (Lok Sabha)**: ~344 constituencies across 10 states
2. **State Assembly (Vidhan Sabha)**: ~2,265 constituencies across 10 states
3. **Local (Municipal/Panchayat)**: Sample wards per Assembly Constituency

### Voter Registration Flow (ECI-Style)

1. **Basic Details**: Email, Password, Full Name, DOB, Gender, Aadhar
2. **Address Selection** (Cascading Dropdowns):
  - Select State → [Maharashtra ▼]
  - Select District → [Mumbai Suburban ▼] (filtered by state)
  - Select Assembly Constituency → [Andheri East ▼] (filtered by district)
3. **Auto-derived** (shown to user, not editable):
  - Parliamentary Constituency: derived from AC mapping
  - Local Body options: shown during local elections
4. **Face Enrollment**: Capture → Embedding → Store encrypted
5. **Wallet Creation**: Backend creates custodial wallet, maps aadhar_hash ↔ blockchain_address

### Voting Flow (ECI-Style)

1. Login + Re-enter Aadhar (identity confirmation)
2. System fetches voter's registered constituencies (Parliamentary, Assembly, Local Body)
3. Show active elections for voter's constituencies
4. Select election → Biometric verification (liveness + face)
5. Show candidates for selected election's constituency
6. Cast vote → Blockchain tx → Receipt (tx hash + explorer link)

### Data Sources for Seeding

- Election Commission of India (eci.gov.in): Official constituency names, codes, reservation status
- data.gov.in: District-to-constituency mappings
- Wikipedia/Census: District lists per state
- Seed via Alembic migration with JSON/CSV files

---

## 2. Legacy Code Assessment (Code-Only)

### Modules that exist

- **Web (Admin)**: `An_OnlineVotingQR_Admin/` — PHP (Bootstrap), election/candidate/voter management, contract interaction via Web3.
- **Web (Voter)**: `An_OnlineVotingQR_User/` — PHP (Bootstrap/jQuery), login, face verification call, voting UI, Web3 vote submission, `castVote.php` writes to DB after tx.
- **Face service**: `An_OnlineVotingQR_User/python/faceknn/face_recognition_knn_web.py` — Flask on 5001, `face_recognition` + scikit-learn KNN, `/register` and `POST /` verify; stores raw images under `Register/{email}/`, pickle model; no auth/CORS wide open.
- **Contract**: `Blockchain/contracts/Votingsol.sol` — Truffle, Solidity ^0.8.0, candidates by `electionName` string, `votedUser[address][electionName]`, `addCandidate`/`addVoter`/`vote`; duplicate-vote check commented out.
- **DB**: `db/evoting.sql` — MySQL/MariaDB: `admininfo`, `constituency`, `electioninfo`, `voterinfo` (vaadhar, baddress, etc.), `votes` (voter, candidate, txhash), `userinfo`.

### Top 10 correctness/security issues

1. **Contract: anyone can add candidates** — `addCandidate` is `external` with no role check.
2. **Contract: duplicate voting allowed** — `getVoter` check before `vote` is commented out; same address can vote multiple times per election.
3. **Contract: public `addVoter**` — any address can set `votedUser[_Id][_name]`, breaking integrity.
4. **Contract: free-text `electionName` on-chain** — gas cost and abuse surface; no bytes32/numeric ID.
5. **Face verification: client-side trust** — UI proceeds to voting if `obj[0].status` is true; no server-side session/token tying verification to vote submission.
6. **No liveness/PAD** — photo/video replay possible.
7. **Face API: no auth or rate limiting** — enrollment/verification open to abuse.
8. **SQL injection** — queries built with string concatenation (e.g. `castVote.php`, voter/login fetches).
9. **Plaintext passwords** — stored and compared in clear.
10. **Dual source of truth** — votes in both chain and DB with no reconciliation; DB allows duplicate (voter,election) and empty voter field; results can diverge.

### What can be reused

- **None of the application code** — PHP, Flask app, and frontend are not reused.
- **Conceptual reuse only**: DB schema ideas (voter, election, candidate, votes, constituency), contract flow (candidates per election, vote by id), and face pipeline (enroll → verify) inform the new design.

### What must be rewritten

- All backend (replace with FastAPI, Pydantic, SQLAlchemy 2, Alembic).
- All frontend (replace with Next.js, TypeScript, Tailwind, shadcn/ui).
- Smart contract (Hardhat, strict access control, bytes32/numeric election IDs, one-vote enforcement, no public candidate/voter manipulation).
- Biometrics (FastAPI, embeddings not raw images, liveness first, server-authoritative, audit logs).
- Deployment and CI (Docker Compose, Hardhat local + testnet, GitHub Actions).

### Source-of-truth inconsistencies in legacy

- Votes written to MySQL after chain tx with no idempotency or uniqueness on (voter, election).
- Blockchain has `votedUser` but check disabled; DB has no unique constraint.
- Results can be read from either chain or DB with no defined rule.
- Face “verified” only in browser; backend does not enforce verification before allowing vote record.

---

## 3. Proposed 2026 Architecture

### Source of truth

**Model A (on-chain is source of truth).**  
Votes exist only on-chain as the canonical record. Off-chain DB stores: election metadata, candidates (mirrored for UI), constituency, voter profiles (email, encrypted Aadhar, hashed Aadhar, custodial address), biometric templates and verification logs, and optional event index for faster UI. Results are computed from chain state/events.

### Component diagram (text)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend (Next.js, TypeScript, Tailwind, shadcn/ui)                    │
│  - Admin: elections, candidates, voter enrollment, results/audit        │
│  - Voter: login, Aadhar lookup, face+liveness, cast vote, receipt       │
│  - Receipt verification: tx hash + explorer link                        │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTPS (REST, OpenAPI)
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend API (FastAPI, Python 3.12+, Pydantic v2)                         │
│  - Auth (email/password, JWT)                                           │
│  - Admin CRUD (elections, candidates, constituencies)                   │
│  - Voter enrollment (Aadhar encrypt+hash, wallet creation, biometrics) │
│  - Verification orchestration (liveness → face, server-authoritative)   │
│  - Vote relay: sign & submit tx with voter’s custodial key              │
│  - Receipts: return tx hash, event index (optional)                     │
│  - Results: read from chain or indexed events                           │
│  - Audit export (non-sensitive logs)                                   │
└─────┬─────────────────────────┬─────────────────────────┬───────────────┘
      │                         │                         │
      │ SQLAlchemy 2            │ HTTP (internal)         │ ethers.js
      ▼                         ▼                         ▼
┌─────────────┐    ┌─────────────────────────┐    ┌─────────────────────┐
│ PostgreSQL  │    │ Biometrics service      │    │ Ethereum            │
│ - voters    │    │ (FastAPI, same or       │    │ - Local: Hardhat    │
│ - elections │    │  separate process)       │    │ - Demo: Sepolia      │
│ - candidates│    │ - Enrollment: embedding  │    │ - Smart contract    │
│ - enrollments│   │ - Verify: liveness then │    │ - Events + state     │
│ - verif_logs│   │   face match            │    │ - Commitment-reveal  │
│ - audit_events│  │ - Rate limited, logged  │    │   for sealed results│
└─────────────┘    └─────────────────────────┘    └─────────────────────┘
```

### Data flows

- **Enrollment**: Admin creates election and candidates (DB + optionally mirror to chain). Voter registers (email, password, Aadhar, constituency). Backend hashes Aadhar (dedup), encrypts Aadhar, creates custodial wallet, stores mapping; biometric enrollment produces embedding stored in DB (encrypted). Face template linked to voter id.
- **Verification**: Voter logs in (email/password). To vote: enters Aadhar → backend decrypts and validates, returns constituency and active elections. Then liveness check (blink/head-turn or PAD model), then face match against stored template. Backend records VerificationLog (pass/fail, score, PAD result, request_id). Only on pass does backend allow vote-relay step.
- **Vote cast**: Backend checks on-chain that voter’s address has not voted for that election. Builds commitment (if sealed) or direct vote, signs with voter’s key, submits tx. Stores tx hash in DB as receipt cache; chain is source of truth.
- **Receipt verification**: Frontend shows tx hash and explorer link. Verification: frontend/backend can read tx and VoteCast (or Reveal) event from chain; backend may index events for faster “my receipt” lookup.
- **Tally/results**: After election end, reveal phase (if commitment-reveal) runs; results computed from contract state or events. Admin dashboard and audit export read from chain (or indexed data derived from chain).

---

## 4. Smart Contract Design (Blockchain First)

### Responsibilities and invariants

- **Election lifecycle**: Admin creates election with `electionId` (uint256 or bytes32), start/end timestamps. Only in [start, end] can votes be cast (or commitments submitted). After end, only reveal allowed (if sealed).
- **Candidate registration**: Restricted to admin (Ownable or role-based). Candidates per election identified by `electionId` + `candidateId`; no free-text election name on-chain.
- **One vote per voter per election**: Voter = Ethereum address. Mapping `hasVoted[electionId][voterAddress]`; `vote`/`commitVote` require `!hasVoted[electionId][msg.sender]` then set true.
- **Vote storage**: Prefer event-emitting + minimal state: e.g. `votes[electionId][voterAddress] = candidateId` and `candidateVoteCount[electionId][candidateId]` for tally; emit `VoteCast(electionId, voter, candidateId, timestamp)` (or commitment hash in sealed design).
- **Result computation**: From contract state (candidate counts) or from events; off-chain indexer optional for UI.

### Access control

- Use OpenZeppelin `AccessControl` or `Ownable` + admin role for: create election, add candidates, set election times, pause. No public `addCandidate` or `addVoter`.
- `vote`/`commitVote`/`revealVote`: only voter address (msg.sender); contract does not accept signed calls from relayer on behalf of others — relayer sends raw signed tx from voter’s key so `msg.sender` is voter.

### Attack considerations

- **Replay**: Same signed tx cannot be replayed (nonce); electionId and hasVoted prevent double use.
- **Double vote**: Enforced by `hasVoted[electionId][msg.sender]`; backend must not submit second tx for same voter+election.
- **Election name abuse**: Use bytes32 or uint256 electionId only; no string electionName in contract logic.
- **Front-running**: Not critical for voting; optional commit-reveal hides choice until reveal.
- **Gas grief**: Cap per-vote gas; avoid unbounded loops.

### Testing plan (contract)

- Hardhat + TypeScript (or Foundry, minimal). Tests run on local Hardhat network in CI.
- Cases: create election, add candidates (admin only), reject add candidate by non-admin, vote once per voter, reject second vote, reject vote for invalid candidate/election, reject vote outside window, reveal phase (if applicable), event emission and state consistency.
- Fuzz: electionId and candidateId bounds, hasVoted invariants.

---

## 5. AI Biometrics Design (Face + Liveness/PAD)

### Enrollment pipeline

- **Capture**: Single or few frames (configurable); server accepts image payload (base64 or multipart); optional client-side crop to face region.
- **Preprocessing**: OpenCV resize, normalize; face detection (MTCNN or InsightFace detector); reject if no face or multiple faces.
- **Embedding**: InsightFace or ArcFace (open-source) to produce fixed-size vector; store vector only (no raw image by default).
- **Storage**: Encrypted embedding in PostgreSQL (e.g. `enrollment_templates` table: voter_id, template_blob_encrypted, algorithm_version, created_at). Optional hash of face for dedup.

### Verification pipeline

- **Order**: Liveness/PAD first (fail closed). If pass, then face recognition.
- **Liveness/PAD**: Baseline: challenge (blink, head turn) with simple motion/blink detection (OpenCV or lightweight model). Advanced: open-source PAD model (e.g. Silent-Face-Anti-Spoofing) as optional upgrade. Store PAD result and score in VerificationLog.
- **Recognition**: Compute embedding of submitted frame; compare to stored template (cosine or L2); threshold (e.g. 0.3–0.5 configurable); store match score and decision.
- **Failure modes**: No face → fail. Multiple faces → fail. PAD fail → fail. Below threshold → fail. Timeout or rate limit → fail. All outcomes logged with request_id, timestamp, scores.

### Data retention and privacy

- Default: store only embeddings and verification logs (decision, score, PAD result, request_id, timestamp). No raw images unless required by policy (then short TTL and access control). Aadhar never in biometric service.

### Anti-spoofing

- Baseline: motion/blink and head-turn challenge; reject static images.
- Advanced (Phase 6): Integrate PAD model; same API, additional score in log.

### Testing

- Unit: embedding generation, threshold logic, PAD pass/fail.
- Integration: negative matches, spoof attempts (photo/video), replay same frame (should fail liveness or replay detection). Latency budget: e.g. &lt; 3s p95 for verify endpoint; load test for concurrent verifications.

---

## 6. Backend API and Data Model

### Entities and relationships

- **User/Voter**: id, email, password_hash, encrypted_aadhar, aadhar_hash (unique), constituency_id, blockchain_address, encrypted_private_key_or_mnemonic_ref, status (pending/accepted/rejected), created_at, updated_at.
- **Election**: id, external_id (bytes32/uint256 for chain), name, type (local/state/central), constituency_id or scope, start_time, end_time, status (draft/active/closed), created_at.
- **Candidate**: id, election_id, name, symbol_url, chain_candidate_id, created_at.
- **EnrollmentTemplate**: id, voter_id, template_encrypted, algorithm_version, created_at.
- **VerificationLog**: id, voter_id, election_id (nullable), request_id, passed (bool), face_score, pad_result, pad_score, created_at.
- **OnChainReceipt**: id, voter_id, election_id, tx_hash, block_number, event_data (json), created_at — cache for UI; chain is source of truth.
- **AuditEvent**: id, actor_type, actor_id, action, resource_type, resource_id, details (json), ip, request_id, created_at.

Relationships: Voter N–1 Constituency; Election N–1 Constituency (or many-to-many for multi-constituency); Candidate N–1 Election; EnrollmentTemplate N–1 Voter; VerificationLog N–1 Voter; OnChainReceipt N–1 Voter, N–1 Election.

### DB schema outline (key tables/columns)

#### Constituency Tables (ECI-Style Hierarchy)

- **states**: id, name, code (e.g. "MH"), is_active.
- **districts**: id, state_id (FK), name, code.
- **parliamentary_constituencies**: id, state_id (FK), name, code (e.g. "MH-PC-01"), reservation_type (General/SC/ST), is_active.
- **assembly_constituencies**: id, district_id (FK), parliamentary_constituency_id (FK), name, code (e.g. "MH-AC-123"), reservation_type, is_active.
- **local_bodies**: id, assembly_constituency_id (FK), name, body_type (Municipal_Corporation/Municipality/Panchayat), is_active.

#### Core Tables

- **voters**: id, email (unique), password_hash, full_name, dob, gender, encrypted_aadhar, aadhar_hash (unique), assembly_constituency_id (FK - base unit), blockchain_address (unique), key_encrypted, status (pending/accepted/rejected), created_at, updated_at.
- **elections**: id, chain_election_id (uint256), name, election_type (parliamentary/assembly/local), state_id (FK, nullable for all-India), start_at, end_at, status (draft/active/closed), created_at.
- **election_constituencies**: id, election_id (FK), parliamentary_constituency_id (FK, nullable), assembly_constituency_id (FK, nullable), local_body_id (FK, nullable) — maps which constituencies are part of each election.
- **candidates**: id, election_constituency_id (FK), name, party, symbol_url, chain_candidate_index, created_at.
- **enrollment_templates**: id, voter_id (unique per voter), template_encrypted, algorithm_version, created_at.
- **verification_logs**: id, voter_id, election_id, request_id, passed, face_score, pad_result, created_at.
- **on_chain_receipts**: id, voter_id, election_id, tx_hash, block_number, created_at.
- **audit_events**: id, actor_type, actor_id, action, resource_type, resource_id, details, request_id, created_at.
- **admins**: id, email, password_hash, created_at.

#### Key Relationships

- 1 State → many Districts → many Assembly Constituencies
- 1 Parliamentary Constituency spans multiple Assembly Constituencies (within same state)
- 1 Assembly Constituency → many Local Bodies
- Voter registers with Assembly Constituency as base unit; Parliamentary derived from mapping
- Election can target: all-India PCs, specific state ACs, or specific local bodies

### API endpoints (grouped, auth, validation)

- **Constituency (public, for registration dropdowns)**:
  - GET /constituencies/states → list of 10 states
  - GET /constituencies/states/:state_id/districts → districts in state
  - GET /constituencies/districts/:district_id/assemblies → assembly constituencies in district
  - GET /constituencies/assemblies/:ac_id → returns AC details + derived Parliamentary Constituency
- **Auth**: POST /auth/register (public, validate email, password, Aadhar, assembly_constituency_id) → create voter, wallet, hash/encrypt Aadhar; POST /auth/login (email, password) → JWT; POST /auth/refresh.
- **Admin — election**: POST /admin/elections (admin, Pydantic body), GET /admin/elections, PATCH /admin/elections/:id (status, times); POST /admin/elections/:id/candidates (admin); sync to chain as needed.
- **Admin — voters**: GET /admin/voters (list, filter), PATCH /admin/voters/:id/status (accept/reject), GET /admin/voters/:id (no raw Aadhar).
- **Enrollment**: POST /enrollment/face (auth, multipart/image) → call biometrics, store template; GET /enrollment/status (auth) → has_template.
- **Verification**: POST /verification/start (auth, election_id?) → request_id, challenge type; POST /verification/face (auth, request_id, image) → liveness + face, return pass/fail + next step; rate limited.
- **Voting**: GET /voting/elections (auth, body or query: Aadhar for constituency) → active elections for voter’s constituency; GET /voting/elections/:id/candidates (auth); POST /voting/cast (auth, election_id, candidate_id, verification_request_id) → backend checks verification log and chain, signs and submits tx, returns tx_hash and receipt.
- **Receipts**: GET /voting/receipts (auth) → list receipt records; GET /voting/receipts/:tx_hash (auth or public for verification) → tx + event details; optional GET /voting/verify/:tx_hash (public) → confirm tx and event on chain.
- **Results**: GET /results/elections/:id (after end, admin or public depending on policy) → tally from chain or index; GET /admin/results/export (admin).
- **Audit**: GET /admin/audit (admin, filters, date range) → paginated audit_events and verification_logs (non-sensitive).

All request bodies validated with Pydantic v2; Zod-equivalent for any runtime checks. Auth: JWT in Authorization header; admin role required for /admin/*.

---

## 7. Frontend Plan (Minimal but High Fidelity)

- **Admin screens**: Login; Dashboard (elections list); Create/Edit Election (name, type, constituency, dates, status); Manage Candidates (per election); Voter list (pending/accepted/rejected, approve/reject); Results (per election, from chain); Audit export (filters, download).
- **Voter screens**: Login (email/password); Dashboard (active elections); Vote flow: enter Aadhar → constituency + elections → select election → liveness challenge → face capture → submit → “Vote cast” with receipt (tx hash, explorer link).
- **Receipt verification**: Screen “Verify receipt”: input tx hash → show tx status, event (VoteCast/Reveal), election and candidate id; link to block explorer.
- **Error handling**: Global error boundary; API errors mapped to user messages (no stack traces); loading and disabled states for async actions; timeout and retry for tx submission.
- **State transitions**: Clear steps in vote flow (Aadhar → elections → verify → cast); success and failure paths; “Already voted” if backend returns 409.
- **Type-safe API client**: OpenAPI codegen (e.g. openapi-typescript + fetch or axios) or typed fetch wrapper with Zod-validated responses; shared types between frontend and backend from OpenAPI spec.

---

## 8. Security Model (Senior-Level)

- **Threat model (top threats)**: (1) Backend compromise (keys, DB); (2) Aadhar/identity leakage; (3) Verification bypass (client or server); (4) Double voting; (5) Injection and auth bypass; (6) DoS (rate limits, cost controls).
- **Server-side enforcement**: All auth and verification checks on backend; no reliance on client boolean for face match; vote submission allowed only after verified VerificationLog and chain check.
- **Rate limiting**: Per-IP and per-user on login, verification, enrollment; stricter on verification endpoints; configurable limits in env.
- **Input validation**: Pydantic for all inputs; SQL via SQLAlchemy (parameterized); no raw SQL concatenation; file type/size limits for images.
- **Secrets**: Keys and DB credentials in env (e.g. .env not committed); encryptors for Aadhar and wallet keys use keys from env/vault; no secrets in repo.
- **Logging and audit**: Structured logs; request_id in logs and VerificationLog; audit_events for admin and sensitive actions; no logging of raw Aadhar or passwords.
- **Wallet/address mapping**: Aadhar ↔ address only in backend DB (encrypted Aadhar, hashed for dedup); never expose mapping to frontend; relayer signs with voter key only after auth and verification.

---

## 9. Implementation Plan (Phases + Sprints)

### Sprint 0 — Foundations (P0)

- **Goal**: Repo structure, CI, local dev, type safety, lint/format, constituency data seeding.
- **Tasks**: 
  - Monorepo layout: `web/` (Next.js), `api/` (FastAPI + biometrics), `contracts/` (Hardhat/Solidity)
  - **Python setup with uv**: `uv init api`, configure `pyproject.toml` with FastAPI deps, create `uv.lock` (committed to git)
  - Docker Compose (Postgres, Hardhat local node)
  - ESLint/Prettier (web), Ruff/mypy (api)
  - GitHub Actions: `uv sync --frozen` for Python, pnpm for Node; typecheck, lint, test
  - Contract tests on Hardhat local
  - README and .env.example
  - **Constituency data seeding**: Prepare JSON/CSV files with real ECI data for 10 states (~346 districts, ~2,265 ACs, ~344 PCs); create Alembic migration to seed; implement cascading dropdown API endpoints
- **Priority**: P0.
- **Acceptance**: `docker-compose up` brings Postgres + chain; `uv sync` installs all Python deps; CI green on main; Constituency cascading dropdowns work (State → District → AC with derived PC).
- **Effort**: M.
- **Risks**: ECI data collection effort. Mitigation: Start with 2-3 states, add remaining states incrementally; use Wikipedia/data.gov.in as data sources.

### Phase 1 — Blockchain Core (P0)

- **Goal**: Contract v1 with admin-only candidate registration, one-vote-per-address, election lifecycle, events; deployment scripts; tests.
- **Tasks**: Hardhat project; Election + Candidate + Vote (commit/reveal if sealed); AccessControl or Ownable; bytes32/uint256 electionId; deployment script (save address/ABI); Hardhat tests (local chain); document ABI/address consumption by backend.
- **Priority**: P0.
- **Acceptance**: Tests pass; deploy to local and (optionally) Sepolia; backend can read ABI and address from env or artifact.
- **Effort**: L.
- **Risks**: Commitment-reveal complexity. Mitigation: implement simple vote first, add commit-reveal in same phase or Phase 4.

### Phase 2 — AI Biometrics Core (P0)

- **Goal**: Enrollment and verification services; liveness baseline; face recognition; verification logs; rate limiting.
- **Tasks**: FastAPI routes for enrollment (image → embedding, store encrypted) and verification (liveness then face); InsightFace or ArcFace integration; liveness (blink/head-turn or lightweight PAD); VerificationLog and audit fields; rate limiting; unit and integration tests (negative, spoof, latency).
- **Priority**: P0.
- **Acceptance**: Server-authoritative verification; all outcomes logged; no raw images stored by default.
- **Effort**: L.
- **Risks**: Liveness robustness. Mitigation: start with simple motion/blink; add PAD model in Phase 6.

### Phase 3 — Integrate End-to-End Vote Cast (P0)

- **Goal**: Voter flow from login → Aadhar → verification → cast → receipt; backend relayer; receipt verification UI.
- **Tasks**: Backend: voter registration (email, password, Aadhar encrypt/hash, wallet creation), JWT auth, verification orchestration, vote relay (sign + submit tx), receipt storage and endpoints; Frontend: login, Aadhar step, verification steps, cast vote, receipt page with tx hash and explorer link; E2E tests (e.g. Playwright or API E2E).
- **Priority**: P0.
- **Acceptance**: One voter can complete flow once per election; receipt verifiable on explorer; duplicate vote rejected by contract and backend.
- **Effort**: L.
- **Risks**: Key management. Mitigation: encrypt keys at rest, single deployer key for testnet separate from voter keys.

### Phase 4 — Results and Auditability (P1)

- **Goal**: Results from chain; sealed results (reveal phase if used); audit export; admin dashboards.
- **Tasks**: Backend: results endpoint (read from contract or index); reveal phase automation (if commitment-reveal); audit export (CSV/JSON); Frontend: admin results view, audit export UI.
- **Priority**: P1.
- **Acceptance**: Results match chain; audit export contains non-sensitive actions and verification summaries.
- **Effort**: M.
- **Risks**: Indexing lag. Mitigation: optional event indexer with “source: chain” disclaimer.

### Phase 5 — Hardening (P1)

- **Goal**: Rate limiting, abuse testing, concurrency/replay tests, observability.
- **Tasks**: Rate limits on all public and verification endpoints; abuse tests (double vote, replay verification, invalid tokens); concurrent vote simulation; structured logging and request_id propagation; health checks.
- **Priority**: P1.
- **Acceptance**: Rate limits enforced; no sensitive data in logs; tests document expected behavior under abuse.
- **Effort**: M.
- **Risks**: False positives on rate limit. Mitigation: configurable limits and whitelist for dev.

### Phase 6 — Demo Polish (P2)

- **Goal**: UX polish, accessibility, optional testnet and cloud deployment guide, optional PAD upgrade.
- **Tasks**: UI copy and loading states; a11y (focus, labels, contrast); docs: testnet deployment (Sepolia, faucet, env vars), optional cloud (e.g. Vercel + Railway/AWS); optional: replace baseline liveness with PAD model.
- **Priority**: P2.
- **Acceptance**: Demo script runs on testnet; docs sufficient for external reviewer.
- **Effort**: M.
- **Risks**: Testnet congestion. Mitigation: fallback “local chain demo” mode with same UI.

---

## 10. Senior Engineering Standards (Repo Constitution)

- **TypeScript**: Strict mode; no `any`; use `unknown` and narrow with Zod where needed; API responses validated with Zod.
- **Python**: mypy strict or near-strict; typed handlers and services; Pydantic v2 for all I/O.
- **Dependency Management**: 
  - Python: **uv** only; `uv.lock` committed to git; use `uv add` to add deps, `uv sync --frozen` in CI
  - Node: pnpm with `pnpm-lock.yaml` committed
  - No manual editing of lockfiles; no pip install in production
- **No client-side trust**: Verification and authorization only on server; client cannot bypass verification or vote without backend.
- **Transactions**: Use DB transactions for multi-step writes (e.g. voter creation + wallet + template); rollback on failure.
- **Error handling**: No stack traces or internal details to client; generic messages; detailed errors only in logs.
- **Logging**: Structured (JSON or key-value); request_id; no PII (no Aadhar, passwords, raw embeddings).
- **Migrations**: Alembic for all schema changes; no ad-hoc SQL in code; migrations reviewed.
- **PR/DoD**: PR checklist (tests, types, lint, no secrets); DoD: AC met, tests pass, docs updated if behavior changes.

---

## 11. AI Coding Agent Rules (Mandatory)

- Prefer small, focused diffs; avoid broad refactors without explicit approval.
- Do not weaken contract checks (no commenting out `require` or access controls).
- Do not bypass or relax verification flows (liveness, face, or auth).
- Every critical change (contract logic, verification, vote path, auth) must have or update tests.
- When API or contract schemas change, update OpenAPI spec and frontend types (and contract ABI/artifacts).
- Require human review for: contract storage layout changes, identity/mapping assumptions (Aadhar ↔ address, voter id), verification thresholds or PAD policy changes, and key/secrets handling.

---

## Addendum: Blockchain Testnet and Deployment

### Primary testnet: Sepolia

- **Why**: Ethereum L1 testnet; widely supported (wallets, explorers, faucets); good for demos and tutorials; Hardhat and ethers.js first-class support.
- **Fallback**: Holesky (Ethereum); same tooling; alternate faucets if Sepolia is down.

### Development modes

- **Mode 1 — Local**: Hardhat local network (default). Used for CI, fast tests, deterministic debugging. No external dependency.
- **Mode 2 — Public testnet**: Sepolia (or Holesky). Used for staging, real explorer links, demo. RPC and faucet required.

### Contract deployment workflow

- Build: `npx hardhat compile`. Deploy: `npx hardhat run scripts/deploy --network sepolia` (or localhost). Env: `RPC_URL`, `DEPLOYER_PRIVATE_KEY` (never committed), `CHAIN_ID`, `CONTRACT_ADDRESS` (output). Frontend/backend: read ABI from `artifacts/` and address from env or from a generated config (versioned with deploy).

### Funding and wallet management

- Create deployer wallet (one key for contract deployment and admin txs). Create voter wallets per user (backend HD or single-key storage). Faucets: Sepolia faucet (e.g. sepoliafaucet.com), Alchemy/Infura testnet faucets. Keys only in .env or vault; separate keys for deployer vs voter accounts. Reset between demos: redeploy contract and use new election IDs, or redeploy and re-enroll test voters.

### Explorer and receipt verification

- App shows: tx hash, block number, “View on Explorer” link (e.g. sepolia.etherscan.io). Verification: frontend or backend fetches tx receipt and parses VoteCast/VoteRevealed event; backend may cache in `on_chain_receipts` for fast “my votes” list; chain remains source of truth.

### Reliability and UX

- Pending state: “Transaction submitted…” with tx hash (link when available). Retry: exponential backoff for RPC errors; “Try again” button. Timeouts: configurable RPC timeout (e.g. 30s). Errors: “Transaction failed” / “Network error” with no sensitive detail. Demo fallback: if testnet unavailable, switch to local chain in same UI path and document in demo script.

### CI rules for blockchain

- All contract tests run on Hardhat local network in CI. No CI dependency on Sepolia or external RPC. ABI and deployment outputs versioned or generated from same codebase as tests.

### Security rules for testnet

- Never hardcode private keys or commit RPC API keys. Admin-only functions not callable by unauthenticated or non-admin users. Voter identity (Aadhar) never on-chain; only voter’s Ethereum address and vote data on-chain.

