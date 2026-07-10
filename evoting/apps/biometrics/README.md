# E-Voting Biometrics Service

An internal FastAPI microservice that performs **face enrollment** and
**verification** (liveness + face match) for the e-voting platform.

> [!IMPORTANT]
> This is an **internal** service. It must **never** be exposed to browsers.
> The core API is the only client; it proxies requests here and owns all
> persistence. This service is **stateless** — it stores nothing to disk, keeps
> no raw images, and returns embeddings/scores only.

## Security model

- Every real endpoint requires the shared secret header `X-Internal-Token`,
  compared against `INTERNAL_SERVICE_TOKEN` with `secrets.compare_digest`.
  Missing/wrong token → `401`. With no token configured the service **fails
  closed** (rejects all authed traffic). `/health` is the only unauthenticated
  endpoint.
- **Server-authoritative.** The caller sends images; the service decides
  pass/fail. Client-provided scores are never trusted.

## Quickstart

```bash
cd apps/biometrics
cp .env.example .env          # set INTERNAL_SERVICE_TOKEN to a long random value
uv sync
uv run uvicorn app.main:app --port 8100
```

Run the checks:

```bash
uv run ruff check .
uv run mypy app
uv run pytest -q
```

## Endpoints

| Method | Path                       | Auth | Description                                   |
| ------ | -------------------------- | ---- | --------------------------------------------- |
| GET    | `/health`                  | no   | `{"status":"ok","embedder":<version>}`        |
| POST   | `/enrollment/embed`        | yes  | Multipart `file` **or** JSON `{image_b64}` → embedding |
| POST   | `/verification/challenge`  | yes  | `{}` → `{"challenge_id","challenge"}`          |
| POST   | `/verification/match`      | yes  | Liveness + cosine match → pass/fail + scores  |

`/verification/match` request body:

```json
{
  "probe_image_b64": "…|null",
  "frames_b64": ["…", "…"],
  "challenge": "blink",
  "stored_embedding": [0.1, 0.2, "…"],
  "threshold": 0.42
}
```

A normal non-match never errors: it returns `passed=false` with a `reason`
(`liveness_failed`, `face_mismatch`, `no_face_detected`, …).

## Embedders (pluggable)

Selected by `FACE_EMBEDDER`:

- **`hash`** (default) — `HashEmbedder`, a deterministic 128-dim vector derived
  from image bytes. No ML dependencies, so the whole system runs and is testable
  with zero model downloads.

  > [!WARNING]
  > The hash embedder is a **development stub, NOT real face recognition**. It
  > only reflects byte-level identity of images. Never use it in production.

- **`insightface`** — `InsightFaceEmbedder`, real ArcFace (r100) embeddings via
  `insightface` + `onnxruntime`. These are optional, heavy dependencies:

  ```bash
  uv sync --extra insightface
  FACE_EMBEDDER=insightface uv run uvicorn app.main:app --port 8100
  ```

## Liveness / PAD

`/verification/challenge` issues a random challenge from
`{blink, turn_left, turn_right, smile}`. `HeuristicLiveness` is a deterministic,
ML-free **stand-in** that only checks that multiple non-identical frames were
supplied (motion present). It does **not** validate the requested action or
defend against replay/deepfake attacks — replace it with a real PAD model before
production.

## Configuration

All settings come from the environment (see `.env.example`):
`INTERNAL_SERVICE_TOKEN`, `FACE_EMBEDDER`, `FACE_MATCH_THRESHOLD`,
`MIN_LIVENESS_FRAMES`, `HOST`, `PORT`, `LOG_LEVEL`.

## Docker

```bash
docker build -t evoting-biometrics apps/biometrics
docker run --rm -p 8100:8100 --env-file apps/biometrics/.env evoting-biometrics
```
