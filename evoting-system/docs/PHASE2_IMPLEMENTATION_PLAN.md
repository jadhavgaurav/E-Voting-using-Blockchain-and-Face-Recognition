# Phase 2 — AI Biometrics Core: Senior Implementation Plan

**Document owner**: CTO / Tech Lead  
**Status**: Approved for implementation  
**Prerequisite**: Phase 1 (Blockchain Core) — **VERIFIED COMPLETE**  
**Target**: P0 — Server-authoritative enrollment and verification; liveness baseline; face recognition; verification logs; rate limiting.

---

## 1. Phase 1 Verification Summary

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Hardhat project with Election + Candidate + Vote | ✅ | `contracts/contracts/EVoting.sol` — uint256 electionId, AccessControl, one-vote-per-address |
| Admin-only candidate registration | ✅ | `createElection` / `addCandidates` gated by `ADMIN_ROLE`; tests reject non-admin |
| One-vote-per-address | ✅ | `hasVoted[electionId][msg.sender]`; `AlreadyVoted` revert; tests cover double vote |
| Election lifecycle (start/end) | ✅ | `ElectionNotStarted` / `ElectionEnded`; time-bound tests |
| Events for receipt/indexing | ✅ | `ElectionCreated`, `CandidatesAdded`, `VoteCast` |
| Deployment script (address/ABI) | ✅ | `script/deploy.ts` → `deployments/default.json` |
| Hardhat tests on local chain | ✅ | 20 tests in `test/EVoting.test.ts`; CI in `.github/workflows/contracts.yml` |
| Backend consumption docs | ✅ | `docs/backend-consumption.md` — ABI path, env, read/write, events |

**Conclusion**: Phase 1 is complete. Proceed with Phase 2.

---

## 2. Phase 2 Goals and Non-Goals

### Goals

- **Enrollment**: Accept image(s) → produce embedding → store encrypted in DB; no raw images by default.
- **Verification**: Liveness-first (fail closed), then face match; all outcomes logged with request_id, scores, PAD result.
- **Server-authoritative**: No client-side trust; verification decision and session binding only on server.
- **Observability**: VerificationLog and audit fields; rate limiting on enrollment and verification.
- **Testability**: Unit tests (embedding, threshold, PAD pass/fail); integration tests (negative match, spoof, latency).

### Non-Goals (defer to Phase 3 / Phase 6)

- Voter registration API, JWT auth, or wallet creation (Phase 3).
- Full E2E vote cast flow (Phase 3).
- Constituency or election CRUD (Sprint 0 / Phase 3).
- Advanced PAD model (e.g. Silent-Face-Anti-Spoofing) — Phase 6; baseline liveness only in Phase 2.
- Raw image retention (optional policy later); default: embeddings + logs only.

---

## 3. Architecture and Placement

### Option A: Biometrics as part of `api/` (recommended)

- Single FastAPI app: `api/` with routers for health, enrollment, verification.
- Same process: no network hop for enrollment → DB write; verification → DB read + log.
- **Pro**: Simpler deployment, shared middleware (rate limit, request_id), single Docker service for Phase 3.
- **Con**: Heavier process (Python + ML deps); can split to separate service later if needed.

### Option B: Biometrics as separate service

- Second FastAPI app: `biometrics/` or `api-biometrics/`; API calls it over HTTP.
- **Pro**: Isolate ML deps; scale verification independently.
- **Con**: Two deployments, network latency, shared secrets for encryption key; overkill for Phase 2.

**Decision**: **Option A**. Implement enrollment and verification inside `api/` as dedicated routers and a `biometrics` domain module. If load or isolation becomes a requirement, extract to a separate service in a later phase.

### High-level layout

```
evoting-system/
├── api/                          # NEW — FastAPI app (Phase 2)
│   ├── pyproject.toml            # uv, Python 3.12+
│   ├── uv.lock
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── enrollment.py     # POST /enrollment/face, GET /enrollment/status
│   │   │   └── verification.py  # POST /verification/start, POST /verification/face
│   │   ├── services/
│   │   │   ├── embedding.py      # InsightFace/ArcFace wrapper
│   │   │   ├── liveness.py       # Baseline: blink/head-turn or lightweight check
│   │   │   └── verification_svc.py
│   │   ├── db/                   # Optional for Phase 2: SQLAlchemy + Alembic when DB is needed
│   │   │   ├── models.py
│   │   │   ├── enrollment.py     # CRUD for templates
│   │   │   └── verification_log.py
│   │   └── middleware/
│   │       ├── rate_limit.py
│   │       └── request_id.py
│   └── tests/
│       ├── unit/
│       │   ├── test_embedding.py
│       │   ├── test_liveness.py
│       │   └── test_threshold.py
│       └── integration/
│           ├── test_enrollment_api.py
│           └── test_verification_api.py
├── contracts/                    # Existing (Phase 1)
├── docs/
│   ├── backend-consumption.md
│   └── PHASE2_IMPLEMENTATION_PLAN.md (this file)
└── .github/workflows/
    ├── contracts.yml
    └── api.yml                   # NEW — lint, typecheck, test for api/
```

Phase 2 can start with **in-memory or file-based storage** for templates and VerificationLog if PostgreSQL is not yet in place (Sprint 0 deferred); otherwise use PostgreSQL + Alembic from the start. Decision: **introduce DB in Phase 2** so that Phase 3 does not require a second migration; schema below assumes PostgreSQL.

### Local development environment

For local development, use the existing **evoting** database in pgAdmin/PostgreSQL. Set in `.env` (do not commit `.env`):

```bash
DATABASE_URL="postgresql://apple:1234@127.0.0.1:5432/evoting?schema=public"
```

- **Host**: 127.0.0.1 (local Postgres)
- **Port**: 5432
- **Database**: evoting
- **Schema**: public
- **User/password**: Use your local pgAdmin/Postgres credentials (example above; replace with your actual user and password if different).

The API reads `DATABASE_URL` from the environment (e.g. via pydantic-settings). Alembic migrations run against this URL and create/update tables in the `public` schema of the `evoting` database. No separate Docker Postgres is required if you already run Postgres locally with pgAdmin.

---

## 4. Data Model (Phase 2 relevant)

### Tables

- **enrollment_templates**
  - `id` (PK), `voter_id` (UUID or FK to future `voters.id`), `template_encrypted` (bytes or hex), `algorithm_version` (str), `created_at`.
  - Unique on `voter_id` (one template per voter for Phase 2).
- **verification_logs**
  - `id` (PK), `voter_id`, `election_id` (nullable for “verification only” calls), `request_id` (UUID), `passed` (bool), `face_score` (float), `pad_result` (str, e.g. "pass"|"fail"|"unknown"), `pad_score` (float, nullable), `created_at`.
  - Index on `(voter_id, created_at)` and `request_id` for lookup.

For Phase 2, `voter_id` can be a UUID provided by the client (or by a minimal “test voter” created in tests) until Phase 3 adds real voter registration. No Aadhar or PII in biometrics service; voter_id is an opaque reference.

### Encryption

- **Templates**: Encrypt at rest with a key from env (e.g. `TEMPLATE_ENCRYPTION_KEY`). Use Fernet (symmetric) or AES-256-GCM; document key rotation later.
- **Logs**: No encryption; do not store raw images or Aadhar; only scores, result, request_id, timestamps.

---

## 5. API Surface (OpenAPI)

All under a prefix if needed (e.g. `/api/v1`). Auth for enrollment/verification can be a simple API key or placeholder until Phase 3 JWT.

| Method | Path | Auth | Description | Request | Response |
|--------|------|------|-------------|---------|----------|
| GET | /health | none | Liveness/readiness | — | `{"status":"ok"}` |
| POST | /enrollment/face | API key or JWT placeholder | Submit image(s); compute embedding; store encrypted | multipart: `image` (file) or JSON: `image_base64` | 201 + `{"voter_id","algorithm_version"}` or 400/413/500 |
| GET | /enrollment/status | API key or JWT | Has template for voter? | query: `voter_id` | 200 + `{"has_template": true/false}` |
| POST | /verification/start | API key or JWT | Start verification session; return `request_id` and optional challenge type | body: `voter_id`, optional `election_id` | 200 + `{"request_id","challenge_type"}` or 429 |
| POST | /verification/face | API key or JWT | Submit frame; run liveness then face match; write VerificationLog | body: `request_id`, `image` (multipart or base64) | 200 + `{"passed","face_score","pad_result"}` or 400/429 |

- **Validation**: Pydantic v2 for all inputs; max image size (e.g. 5MB); allowed MIME types (image/jpeg, image/png).
- **Idempotency**: `verification/start` is not idempotent (each call = new session); `verification/face` may accept multiple frames per `request_id` until pass/fail (define in implementation: e.g. max 5 attempts per request_id).

---

## 6. Liveness Baseline (Phase 2)

- **Requirement**: Fail closed; no reliance on client-side flags.
- **Options**:
  1. **Blink / head-turn challenge**: Server sends challenge type in `verification/start`; client sends short video or multiple frames; server runs simple motion/blink detection (OpenCV or lightweight model). More UX friction, stronger against static photo.
  2. **Single-frame heuristic**: Check for basic “liveness” cues on one image (e.g. face present, not a flat crop). Weak against good prints; document as “baseline” and replace with PAD in Phase 6.
  3. **Lightweight PAD model**: Integrate a small anti-spoof model (e.g. one from GitHub) that outputs score. Better robustness; slightly more dependency and latency.

**Decision**: Implement **(1) Blink/head-turn** as the baseline: `verification/start` returns `challenge_type: "blink"` or `"head_turn"`. Client sends 2–3 frames (or a short video); server runs:
- Face detection per frame (same detector as for recognition).
- Blink: simple eye aspect ratio or blink count between frames.
- Head turn: yaw/pose change between frames.
If liveness passes, then run face embedding and match to stored template. Log both `pad_result` and `face_score` in VerificationLog. If liveness fails, do not run face match; log `passed=false`, `pad_result=fail`.

**Fallback**: If integration of blink/head-turn is delayed, implement **(2) single-frame heuristic** (e.g. “face detected and size above threshold”) and clearly document it as temporary; replace with (1) or (3) before production.

---

## 7. Face Recognition Stack

- **Embedding model**: Prefer **InsightFace** (e.g. `insightface` Python package, or `buffalo_l` / `buffalo_s` for a balance of accuracy and speed). Alternative: **ArcFace** (e.g. via `face_recognition` or dedicated repo). Decision: **InsightFace** for Phase 2; document model name and version in `algorithm_version`.
- **Similarity**: Cosine similarity or L2 between current embedding and stored template; configurable threshold (e.g. 0.3–0.5); store threshold in config/env.
- **Storage**: Only store embedding (vector); no raw image. Optional: hash of face crop for dedup (Phase 2 can skip).

---

## 8. Rate Limiting and Security

- **Rate limits**: Per-IP and per-voter_id (or per-session) on:
  - `POST /enrollment/face`: e.g. 10/hour per voter_id, 100/hour per IP.
  - `POST /verification/start`: e.g. 20/hour per voter_id, 200/hour per IP.
  - `POST /verification/face`: e.g. 30/hour per request_id, 300/hour per IP.
- Use a simple in-memory store (e.g. `slowapi` or custom middleware with TTL dict) for Phase 2; Redis in Phase 5 if needed.
- **Secrets**: `TEMPLATE_ENCRYPTION_KEY`, optional `API_KEY` for internal calls; no secrets in repo; `.env.example` documents all.
- **Logging**: Structured logs (JSON); include `request_id`; never log raw images, embeddings, or PII.

---

## 9. Implementation Sprints (Senior-Level)

### Sprint 2.1 — API shell and health (2–3 days)

- **Tasks**:
  - Create `api/` with `uv init`; add FastAPI, uvicorn, pydantic, python-multipart to `pyproject.toml`; generate `uv.lock` and commit.
  - Add `app/main.py` (FastAPI app), `app/config.py` (pydantic-settings from env), `app/routers/health.py` → GET /health.
  - Add middleware: request_id (UUID per request, header `X-Request-ID`), CORS (configurable).
  - Docker: optional `Dockerfile` for `api/` and add to `docker-compose.yml` if Sprint 0 compose exists; otherwise document “run with `uv run uvicorn app.main:app`”.
  - CI: `.github/workflows/api.yml` — checkout, uv sync --frozen, ruff, mypy, pytest (placeholder test).
- **Acceptance**: `uv run uvicorn app.main:app` starts; GET /health returns 200; CI green for api/.

### Sprint 2.2 — DB schema and enrollment storage (2–3 days)

- **Tasks**:
  - Add SQLAlchemy 2, Alembic, async driver (e.g. asyncpg) or sync (psycopg2) per team preference; add `app/db/models.py` for `enrollment_templates` and `verification_logs`.
  - Alembic: init, first migration creating the two tables and indexes.
  - Encryption helper: `app/services/encryption.py` — encrypt/decrypt template bytes using key from config; use Fernet or AES-GCM.
  - Repository layer: `app/db/enrollment.py` — create template (encrypt before insert), get by voter_id, exists check; `app/db/verification_log.py` — insert log, get by request_id.
  - Wire config: `DATABASE_URL`, `TEMPLATE_ENCRYPTION_KEY` in config and `.env.example`.
- **Acceptance**: Migration runs; can insert/read encrypted template and insert/read verification log; unit test for encrypt/decrypt round-trip.

### Sprint 2.3 — Embedding service and enrollment API (3–4 days)

- **Tasks**:
  - Add InsightFace (or chosen lib) to `pyproject.toml`; optional separate `requirements-ml.txt` if needed for heavy deps.
  - `app/services/embedding.py`: load model once (startup or lazy); `extract_embedding(image_bytes) -> list[float]`; face detection + single face crop; reject zero or multiple faces; return 512-dim (or model dim) vector.
  - `app/routers/enrollment.py`: POST /enrollment/face (multipart or base64), validate size/type, call embedding service, encrypt, save via repository; return 201 with voter_id and algorithm_version. GET /enrollment/status?voter_id= — return has_template.
  - Use a placeholder `voter_id` from request body or query (Phase 3 will supply real voter_id from JWT).
  - Unit tests: embedding output shape; reject no face / multi face. Integration test: POST image → 201 → GET status true; POST invalid image → 400.
- **Acceptance**: Enrollment stores encrypted embedding; status reflects presence; tests pass; no raw image stored.

### Sprint 2.4 — Liveness baseline (3–4 days)

- **Tasks**:
  - `app/services/liveness.py`: Implement blink and/or head-turn check: input = list of frames (or video path); output = passed (bool), score, and optional details (e.g. blink_count). Use OpenCV + simple heuristics or a tiny model; document approach in code.
  - In-memory (or DB) session store: on `verification/start`, create session with request_id, voter_id, challenge_type, created_at; store expected frame count or time window.
  - POST /verification/face: receive frame(s); if session expects more frames for liveness, append and run liveness when enough frames; if liveness not yet passed, return `{"passed": false, "pad_result": "fail"}` or “pending”; if liveness passed, run face match (next sprint).
  - Log to verification_logs on final pass/fail (can log “liveness_only” in Phase 2 for intermediate steps if useful).
  - Integration test: send static image → liveness fails; send short video with blink → liveness passes (or mock frames in test).
- **Acceptance**: Liveness runs before face match; fail-closed; session state and PAD result logged.

### Sprint 2.5 — Verification flow and face match (2–3 days)

- **Tasks**:
  - After liveness passes: load template by voter_id, compute embedding for current frame, compare (cosine or L2), apply threshold from config; set `passed = pad_passed and (face_score >= threshold)`.
  - Write VerificationLog: request_id, voter_id, election_id (optional), passed, face_score, pad_result, pad_score, created_at.
  - POST /verification/face response: include `passed`, `face_score`, `pad_result`; optionally `request_id` for client to store and send to Phase 3 vote endpoint.
  - Rate limiting: add middleware or dependency for enrollment and verification endpoints; configurable limits; return 429 with Retry-After when exceeded.
  - Integration tests: same person → pass; different person → fail; no template → fail; rate limit → 429.
- **Acceptance**: Full verification (start → face) results in correct pass/fail and persisted VerificationLog; rate limits enforced.

### Sprint 2.6 — Observability and hardening (1–2 days)

- **Tasks**:
  - Structured logging: every request logs request_id, path, status, duration; no PII.
  - OpenAPI: tags, descriptions, example responses; export spec to `docs/openapi.yaml` or serve at /openapi.json.
  - Latency: add timing for embedding and liveness; log if p95 exceeds target (e.g. 3s for verify); optional metric endpoint for health dashboard.
  - Document: update README with api/ setup, env vars, and how Phase 3 will call verification (e.g. pass request_id to vote endpoint so backend can check VerificationLog).
- **Acceptance**: Logs are structured; API spec is accurate; README and .env.example are complete.

---

## 10. Testing Strategy

| Layer | Tools | Coverage |
|-------|--------|----------|
| Unit | pytest | embedding shape and rejection cases; liveness pass/fail for known frames; threshold logic; encrypt/decrypt |
| Integration | pytest + httpx TestClient | enrollment API (success, invalid image, size limit); verification start → face (success, wrong person, no template, rate limit) |
| Negative | pytest | spoof: static photo must fail liveness; replay same frame twice: second use of request_id behavior defined (e.g. reject or idempotent) |
| Latency | pytest + benchmark or manual | verify endpoint p95 &lt; 3s on a reference machine; document hardware |

No E2E with real browser in Phase 2; Phase 3 will add E2E for full vote flow.

---

## 11. Dependencies and Versions

- Python: 3.12+
- FastAPI: ^0.115+
- Pydantic: v2
- SQLAlchemy: 2.x
- Alembic: 1.x
- uv: latest; lockfile committed
- InsightFace: pin version (e.g. 0.7.x or as per package availability); document model file (e.g. buffalo_l) and license.
- OpenCV: opencv-python-headless (for liveness and optional preprocessing).

---

## 12. Risks and Mitigations

| Risk | Mitigation |
|------|-------------|
| Liveness too weak (photo replay) | Document as baseline; plan PAD model in Phase 6; optional: add “challenge” UX (blink/head-turn) to improve robustness. |
| Embedding model size/latency | Use a “small” variant (e.g. buffalo_s); lazy load; run benchmarks in CI or nightly. |
| DB not ready (Sprint 0 deferred) | Implement in-memory or SQLite for Phase 2 dev; add PostgreSQL migration when Sprint 0 lands; keep repository interface so swap is easy. |
| Rate limit store volatility | In-memory is acceptable for Phase 2; document that restarts clear limits; Phase 5 can add Redis. |

---

## 13. Definition of Done (Phase 2)

- [ ] `api/` runs with `uv run uvicorn app.main:app`; GET /health returns 200.
- [ ] POST /enrollment/face stores encrypted embedding; GET /enrollment/status returns has_template.
- [ ] POST /verification/start returns request_id (and challenge_type); POST /verification/face runs liveness then face match; all outcomes written to verification_logs.
- [ ] No raw images stored by default; only embeddings and log fields (scores, request_id, timestamps).
- [ ] Rate limiting applied to enrollment and verification; 429 returned when exceeded.
- [ ] Unit and integration tests pass; CI (api.yml) green.
- [ ] README and .env.example document API, env vars, and Phase 3 integration points (request_id → vote backend).
- [ ] OpenAPI spec accurate and available.

---

## 14. Handoff to Phase 3

Phase 3 (Integrate End-to-End Vote Cast) will:

- Implement voter registration (email, password, Aadhar encrypt/hash, wallet creation) and JWT auth.
- Call verification flow: after login and Aadhar step, frontend calls verification/start then verification/face; on pass, backend receives `verification_request_id` (request_id) and checks VerificationLog before allowing vote relay.
- Enforce: vote submission allowed only if there exists a VerificationLog row with that request_id, passed=true, and reasonable recency (e.g. within 5 minutes).

Phase 2 must expose `request_id` in the verification response and persist VerificationLog with request_id so Phase 3 can perform this check.

---

*End of Phase 2 Implementation Plan.*
