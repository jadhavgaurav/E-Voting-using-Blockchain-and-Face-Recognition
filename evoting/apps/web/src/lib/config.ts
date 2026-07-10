/**
 * Runtime configuration derived from public environment variables.
 * These are inlined at build time by Next.js (NEXT_PUBLIC_* prefix).
 */

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export const API_BASE_URL: string = stripTrailingSlash(
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
);

export const CHAIN_EXPLORER_URL: string = stripTrailingSlash(
  process.env.NEXT_PUBLIC_CHAIN_EXPLORER_URL ?? "https://sepolia.etherscan.io",
);

/** Build a link to a transaction on the configured block explorer. */
export function explorerTxUrl(txHash: string): string {
  return `${CHAIN_EXPLORER_URL}/tx/${txHash}`;
}
