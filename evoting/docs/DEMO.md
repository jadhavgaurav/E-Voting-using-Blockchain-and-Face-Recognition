# Demo Script

A ~10-minute walkthrough a reviewer can follow. Assumes the local (no-Docker) setup from
the root README is running: chain (8545), biometrics (8100), api (8000), web (3000), the
contract deployed and `EVOTING_CONTRACT_ADDRESS` set, and DB migrated + seeded.

For the smoothest no-ML demo set `FACE_MATCH_THRESHOLD=-1` in `.env` before starting the
API (liveness still enforced; face match is stubbed by the hash embedder).

## 1. Admin creates an election (2 min)

1. Go to http://localhost:3000/admin/login → `admin@evoting.com` / `admin12345`.
2. **Create election**: name "Andheri East Assembly 2026", type `assembly`, pick the
   assembly constituency **Andheri East** (MH → Mumbai Suburban → Andheri East), start = now,
   end = +2h, add 2–3 candidates. Submit.
   - Under the hood: the API calls `createElection` + `addCandidates` on-chain and mirrors
     candidate metadata to Postgres keyed by chain index.

## 2. Voter registers + enrolls (3 min)

1. http://localhost:3000/register → fill the form; use the **same** State→District→Assembly
   (Maharashtra → Mumbai Suburban → **Andheri East**) so the voter shares the election's
   constituency. Aadhaar = any 12 digits. Submit → a custodial wallet is created server-side.
2. Back in **admin → Voters**, approve the new voter (status → accepted).
3. Log in as the voter (http://localhost:3000/login), open **Enroll face**, allow the camera,
   capture a still. The embedding is stored encrypted; no raw image is kept.

## 3. Voter verifies + votes (3 min)

1. Voter **Dashboard** → the Andheri East election is listed → **Vote**.
2. **Verify identity**: the app shows a challenge (e.g. "blink"); the camera captures a few
   frames (liveness) + a probe still → server decides pass/fail. Only a server-recorded PASS
   unlocks the ballot.
3. Select a candidate → **Cast vote**. The API checks `hasVoted` on-chain, signs the tx with
   the voter's custodial key, and returns a receipt.
4. The receipt shows the **tx hash** with an explorer link (Sepolia) or the local tx hash.

## 4. Prove the guarantees (2 min)

- **No double voting**: try to vote again → `409 ALREADY_VOTED` (enforced by the contract and
  the API). Re-verifying doesn't help.
- **No client trust**: in devtools, try to POST `/voting/cast` with a random
  `verification_request_id` → `422 VERIFICATION_MISSING`.
- **Results from chain**: admin → election → **Results** shows the tally read straight from the
  contract (`source: chain`). Close the election to publish public results at
  `/results/elections/{id}`.
- **Audit**: admin → Audit shows register / approve / vote_cast events (no PII).

## Talking points

- The old project's votes ran through a homemade `localhost:8080` "blockchain" with a
  client-supplied tx hash, an on-chain contract with double-voting enabled, and SQL-injectable
  PHP. This rebuild puts votes on real Ethereum, enforces one-vote in the contract, and makes
  every trust decision server-side.
