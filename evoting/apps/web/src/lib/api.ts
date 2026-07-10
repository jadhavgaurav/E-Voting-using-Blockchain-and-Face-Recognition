/**
 * Typed fetch client for the E-Voting core API.
 *
 * All calls are prefixed with the configured API base URL, automatically attach
 * the bearer token when present, and normalise the backend error envelope
 * `{ detail, code, request_id }` into a typed {@link ApiError}.
 */

import { API_BASE_URL } from "./config";
import { getAccessToken } from "./token-store";

/* ------------------------------------------------------------------ */
/* DTOs                                                                */
/* ------------------------------------------------------------------ */

export type Reservation = string;

export interface GeoState {
  id: string;
  name: string;
  code: string;
}

export interface GeoDistrict {
  id: string;
  name: string;
  code: string;
}

export interface GeoAssemblyBrief {
  id: string;
  name: string;
  code: string;
  reservation: Reservation;
}

export interface GeoAssemblyDetail {
  id: string;
  name: string;
  code: string;
  reservation: Reservation;
  district_name: string;
  parliamentary_constituency_name: string;
  parliamentary_constituency_id: string;
}

export type VoterStatus = "pending" | "accepted" | "rejected";
export type Gender = "male" | "female" | "other";

export interface VoterOut {
  id: string;
  email: string;
  full_name: string;
  status: VoterStatus;
  blockchain_address: string;
  assembly_constituency_id: string;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  dob: string; // YYYY-MM-DD
  gender: Gender;
  aadhaar: string; // 12 digits
  assembly_constituency_id: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface EnrollmentResult {
  enrolled: boolean;
  algorithm_version: string;
}

export interface EnrollmentStatus {
  enrolled: boolean;
  algorithm_version?: string;
}

export type LivenessChallenge = "blink" | "turn_left" | "turn_right" | "smile";

export interface VerificationStart {
  request_id: string;
  challenge_id: string;
  challenge: LivenessChallenge;
}

export interface VerificationFaceRequest {
  request_id: string;
  election_id: string;
  challenge: LivenessChallenge;
  frames_b64: string[];
  probe_image_b64: string;
}

export interface VerificationResult {
  request_id: string;
  passed: boolean;
  face_score: number;
  liveness_passed: boolean;
  reason: string;
}

export type ElectionType = string;
export type ElectionStatus = string;

export interface ElectionOut {
  id: string;
  chain_election_id: number;
  name: string;
  election_type: ElectionType;
  assembly_constituency_id: string;
  start_at: string;
  end_at: string;
  status: ElectionStatus;
  result_published: boolean;
}

export interface CandidateOut {
  id: string;
  name: string;
  party: string;
  symbol_url: string | null;
  chain_candidate_index: number;
}

export interface ElectionDetail extends ElectionOut {
  candidates: CandidateOut[];
}

export interface CastVoteRequest {
  election_id: string;
  candidate_id: string;
  verification_request_id: string;
}

export interface ReceiptOut {
  election_id: string;
  candidate_index: number;
  tx_hash: string;
  block_number: number;
  created_at: string;
}

export interface ResultRow {
  candidate_id: string;
  name: string;
  party: string;
  chain_candidate_index: number;
  votes: number;
}

export interface ElectionResults {
  election_id: string;
  name: string;
  status: ElectionStatus;
  total_votes: number;
  results: ResultRow[];
  source: string;
}

export interface CandidateInput {
  name: string;
  party: string;
  symbol_url?: string;
}

export interface CreateElectionRequest {
  name: string;
  election_type: ElectionType;
  assembly_constituency_id: string;
  start_at: string; // ISO
  end_at: string; // ISO
  candidates: CandidateInput[];
}

export interface AuditRow {
  id: string;
  actor: string;
  action: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

/* ------------------------------------------------------------------ */
/* Error type                                                          */
/* ------------------------------------------------------------------ */

export interface ErrorEnvelope {
  detail: string;
  code?: string;
  request_id?: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string | null;
  readonly requestId: string | null;
  readonly detail: string;

  constructor(
    status: number,
    detail: string,
    code: string | null = null,
    requestId: string | null = null,
  ) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.detail = detail;
  }
}

/* ------------------------------------------------------------------ */
/* Core request helper                                                 */
/* ------------------------------------------------------------------ */

interface RequestOptions {
  method?: string;
  /** JSON body — serialised and sent with an application/json content type. */
  json?: unknown;
  /** Raw body (e.g. FormData). Takes precedence over `json`. */
  body?: BodyInit;
  /** Query parameters appended to the path. */
  query?: Record<string, string | number | undefined>;
  /** When true the endpoint returns no content (204). */
  expectNoContent?: boolean;
  signal?: AbortSignal;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const url = `${API_BASE_URL}${path}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function parseError(response: Response): Promise<ApiError> {
  let detail = response.statusText || "Request failed";
  let code: string | null = null;
  let requestId: string | null = null;
  try {
    const data = (await response.json()) as Partial<ErrorEnvelope> | null;
    if (data && typeof data === "object") {
      if (typeof data.detail === "string" && data.detail.length > 0) {
        detail = data.detail;
      }
      if (typeof data.code === "string") code = data.code;
      if (typeof data.request_id === "string") requestId = data.request_id;
    }
  } catch {
    // Non-JSON error body — keep the status-based default.
  }
  return new ApiError(response.status, detail, code, requestId);
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", json, body, query, expectNoContent, signal } = options;

  const headers = new Headers();
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let finalBody: BodyInit | undefined = body;
  if (finalBody === undefined && json !== undefined) {
    headers.set("Content-Type", "application/json");
    finalBody = JSON.stringify(json);
  }

  let response: Response;
  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: finalBody,
      signal,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      0,
      "Unable to reach the server. Check your connection and try again.",
      "NETWORK_ERROR",
    );
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  if (expectNoContent || response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/* ------------------------------------------------------------------ */
/* Geo (public)                                                        */
/* ------------------------------------------------------------------ */

export const geo = {
  states: (): Promise<GeoState[]> => request("/geo/states"),
  districts: (stateId: string): Promise<GeoDistrict[]> =>
    request(`/geo/states/${stateId}/districts`),
  assemblies: (districtId: string): Promise<GeoAssemblyBrief[]> =>
    request(`/geo/districts/${districtId}/assemblies`),
  assembly: (assemblyId: string): Promise<GeoAssemblyDetail> =>
    request(`/geo/assemblies/${assemblyId}`),
};

/* ------------------------------------------------------------------ */
/* Auth                                                                */
/* ------------------------------------------------------------------ */

export const auth = {
  register: (payload: RegisterRequest): Promise<VoterOut> =>
    request("/auth/register", { method: "POST", json: payload }),
  login: (payload: LoginRequest): Promise<TokenPair> =>
    request("/auth/login", { method: "POST", json: payload }),
  adminLogin: (payload: LoginRequest): Promise<TokenPair> =>
    request("/auth/admin/login", { method: "POST", json: payload }),
  refresh: (refreshToken: string): Promise<TokenPair> =>
    request("/auth/refresh", { method: "POST", json: { refresh_token: refreshToken } }),
  me: (): Promise<VoterOut> => request("/auth/me"),
};

/* ------------------------------------------------------------------ */
/* Enrollment                                                          */
/* ------------------------------------------------------------------ */

export const enrollment = {
  face: (file: Blob): Promise<EnrollmentResult> => {
    const form = new FormData();
    form.append("file", file, "face.jpg");
    return request("/enrollment/face", { method: "POST", body: form });
  },
  status: (): Promise<EnrollmentStatus> => request("/enrollment/status"),
};

/* ------------------------------------------------------------------ */
/* Verification                                                        */
/* ------------------------------------------------------------------ */

export const verification = {
  start: (electionId: string): Promise<VerificationStart> =>
    request("/verification/start", {
      method: "POST",
      query: { election_id: electionId },
    }),
  face: (payload: VerificationFaceRequest): Promise<VerificationResult> =>
    request("/verification/face", { method: "POST", json: payload }),
};

/* ------------------------------------------------------------------ */
/* Voting                                                              */
/* ------------------------------------------------------------------ */

export const voting = {
  elections: (): Promise<ElectionOut[]> => request("/voting/elections"),
  candidates: (electionId: string): Promise<CandidateOut[]> =>
    request(`/voting/elections/${electionId}/candidates`),
  cast: (payload: CastVoteRequest): Promise<ReceiptOut> =>
    request("/voting/cast", { method: "POST", json: payload }),
  receipts: (): Promise<ReceiptOut[]> => request("/voting/receipts"),
};

/* ------------------------------------------------------------------ */
/* Results (public)                                                    */
/* ------------------------------------------------------------------ */

export const results = {
  election: (electionId: string): Promise<ElectionResults> =>
    request(`/results/elections/${electionId}`),
};

/* ------------------------------------------------------------------ */
/* Admin                                                               */
/* ------------------------------------------------------------------ */

export const admin = {
  createElection: (payload: CreateElectionRequest): Promise<ElectionDetail> =>
    request("/admin/elections", { method: "POST", json: payload }),
  elections: (): Promise<ElectionOut[]> => request("/admin/elections"),
  election: (electionId: string): Promise<ElectionDetail> =>
    request(`/admin/elections/${electionId}`),
  closeElection: (electionId: string): Promise<ElectionOut> =>
    request(`/admin/elections/${electionId}/close`, { method: "POST" }),
  voters: (status?: VoterStatus): Promise<VoterOut[]> =>
    request("/admin/voters", { query: { status } }),
  setVoterStatus: (
    voterId: string,
    status: Exclude<VoterStatus, "pending">,
  ): Promise<VoterOut> =>
    request(`/admin/voters/${voterId}/status`, { method: "PATCH", json: { status } }),
  electionResults: (electionId: string): Promise<ElectionResults> =>
    request(`/admin/elections/${electionId}/results`),
  audit: (): Promise<AuditRow[]> => request("/admin/audit"),
};

export const api = {
  geo,
  auth,
  enrollment,
  verification,
  voting,
  results,
  admin,
};
