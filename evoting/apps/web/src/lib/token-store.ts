/**
 * Module-level holder for the current access token.
 *
 * The API client reads the token from here so it stays decoupled from React.
 * The auth context is the single writer and keeps this in sync with its state
 * and with localStorage.
 */

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}
