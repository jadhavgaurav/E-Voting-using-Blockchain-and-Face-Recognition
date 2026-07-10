# @evoting/web

Next.js 15 (App Router) web app for the E-Voting platform — blockchain ballots with
face-recognition identity checks. This is the voter- and admin-facing UI; it talks to the
core API over HTTP.

## What it does

- **Register → approve → enroll → verify → vote → receipt** end to end.
- Cascading State → District → Assembly constituency selection at registration.
- Live camera capture for face enrollment and per-vote liveness verification.
- On-chain receipts with links to the block explorer (Sepolia by default).
- Admin console: create elections, approve/reject voters, view live results, close
  elections.

## Requirements

Runs from the monorepo root with pnpm + Turborepo.

## Develop

```bash
# from the monorepo root (…/evoting)
pnpm install
pnpm --filter @evoting/web dev      # http://localhost:3000
```

Other scripts:

```bash
pnpm --filter @evoting/web lint
pnpm --filter @evoting/web typecheck
pnpm --filter @evoting/web build     # next build (standalone output)
pnpm --filter @evoting/web start     # serve the production build
```

## Environment

Copy `.env.example` to `.env.local` (or set these in the root `.env`). Both are inlined at
build time, so rebuild after changing them.

| Variable                         | Default                        | Purpose                                   |
| -------------------------------- | ------------------------------ | ----------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL`       | `http://localhost:8000`        | Base URL of the core API (no trailing /). |
| `NEXT_PUBLIC_CHAIN_EXPLORER_URL` | `https://sepolia.etherscan.io` | Block explorer for receipt tx links.      |

## Camera / HTTPS note

Browsers only expose `getUserMedia` on `localhost` or over HTTPS. On a deployed host you
must serve the app over TLS for enrollment and verification to work.

## Demo caveat — face-match threshold

Verification's face-match strength depends on the API's biometric embedder. With the dev
hash-embedder the face match only passes when the probe image equals the enrolled bytes,
so for a live-camera demo the operator sets `FACE_MATCH_THRESHOLD=-1` on the
biometrics/API service (liveness is still enforced). The web app makes no assumptions about
this — it always captures and sends real frames as specified.

## Docker

A multi-stage `Dockerfile` builds the Next.js standalone output on `node:20-alpine`. Build
it from the **monorepo root** so the workspace is in context:

```bash
docker build -f apps/web/Dockerfile -t evoting-web .
docker run -p 3000:3000 evoting-web
```
