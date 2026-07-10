"use client";

/**
 * Client-side auth store.
 *
 * Holds the token pair and role, persists them to localStorage, and keeps the
 * module-level token holder (read by the API client) in sync.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { auth as authApi, type LoginRequest } from "./api";
import { setAccessToken } from "./token-store";

export type Role = "voter" | "admin";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  role: Role | null;
}

interface AuthContextValue extends AuthState {
  ready: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  adminLogin: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

const STORAGE_KEY = "evoting.auth";

const AuthContext = createContext<AuthContextValue | null>(null);

const EMPTY_STATE: AuthState = {
  accessToken: null,
  refreshToken: null,
  role: null,
};

function readPersisted(): AuthState {
  if (typeof window === "undefined") return EMPTY_STATE;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY_STATE;
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    const role = parsed.role === "voter" || parsed.role === "admin" ? parsed.role : null;
    return {
      accessToken: typeof parsed.accessToken === "string" ? parsed.accessToken : null,
      refreshToken: typeof parsed.refreshToken === "string" ? parsed.refreshToken : null,
      role,
    };
  } catch {
    return EMPTY_STATE;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(EMPTY_STATE);
  const [ready, setReady] = useState(false);

  // Hydrate from localStorage on mount (client only).
  useEffect(() => {
    const persisted = readPersisted();
    setAccessToken(persisted.accessToken);
    setState(persisted);
    setReady(true);
  }, []);

  const persist = useCallback((next: AuthState) => {
    setAccessToken(next.accessToken);
    setState(next);
    if (typeof window !== "undefined") {
      if (next.accessToken) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      const tokens = await authApi.login(credentials);
      persist({
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        role: "voter",
      });
    },
    [persist],
  );

  const adminLogin = useCallback(
    async (credentials: LoginRequest) => {
      const tokens = await authApi.adminLogin(credentials);
      persist({
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        role: "admin",
      });
    },
    [persist],
  );

  const logout = useCallback(() => {
    persist(EMPTY_STATE);
  }, [persist]);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      ready,
      isAuthenticated: Boolean(state.accessToken),
      login,
      adminLogin,
      logout,
    }),
    [state, ready, login, adminLogin, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
}
