# Backend consumption of EVoting contract

This document describes how the backend API/relayer should consume the EVoting contract: ABI location, contract address, chain configuration, and usage.

## ABI location

After compilation, the contract ABI is at:

- **Monorepo path**: `contracts/artifacts/contracts/EVoting.sol/EVoting.json`
- The JSON file contains the full artifact (ABI, bytecode, etc.). The backend may:
  - Read from this path when running inside the monorepo, or
  - Copy the `abi` field from this file into the API repo.

## Contract address

- **Environment**: Set `EVOTING_CONTRACT_ADDRESS` in the backend environment.
- **Deployment artifact**: Alternatively, read from `contracts/deployments/default.json` (keyed by `chainId`). The file contains:
  - `chainId`: number
  - `EVoting.address`: deployed contract address
  - `EVoting.abiPath`: path to the ABI file relative to `contracts/`

Do not commit private keys or live Sepolia addresses in the repo. Use `.env` or a vault for production.

## Chain ID and RPC

| Network   | Chain ID | RPC |
|----------|----------|-----|
| Hardhat local | 31337 | `http://127.0.0.1:8545` |
| Sepolia  | 11155111 | Set `RPC_URL` in env (e.g. Alchemy/Infura) |

Backend should use `RPC_URL` for the target network and the same `chainId` when verifying receipts or indexing events.

## Read calls

- `getElection(uint256 id)` → `(startTime, endTime, exists)`
- `getCandidateCount(uint256 electionId)` → `uint256`
- `getVoteCount(uint256 electionId, uint256 candidateIndex)` → `uint256`
- `hasVotedForElection(uint256 electionId, address voter)` → `bool`
- `hasVoted(uint256 electionId, address voter)` → `bool` (public mapping)
- `voteChoice(uint256 electionId, address voter)` → `uint256` (candidate index chosen)

Use these to check election status, tally, and whether a voter has already voted before allowing a new vote from the relayer.

## Write (relayer)

- **vote(uint256 electionId, uint256 candidateIndex)**  
  The transaction **must** be signed by the voter’s key so that `msg.sender` on-chain is the voter. The backend relayer holds custodial voter keys and submits the tx on behalf of the voter after server-side auth and verification. Do not expose admin functions (createElection, addCandidates) to the voter flow.

## Events

- **VoteCast(uint256 indexed electionId, address indexed voter, uint256 candidateIndex, uint256 timestamp)**  
  Emitted on every successful vote. Use for receipt verification and optional indexing: fetch tx receipt, parse event, show electionId/candidateIndex and link to block explorer.

## Security

- No private keys in the repo; backend uses env or vault for relayer keys.
- Admin functions (createElection, addCandidates) are restricted to `ADMIN_ROLE`; do not expose them to voter-facing APIs.
- Voter identity (e.g. Aadhar) is never on-chain; only the voter’s Ethereum address and vote data are on-chain.
