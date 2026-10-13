"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { api, tokenStorage, UserProfile } from "./api";
import { Role, roleFromJwt, normalizeRole } from "./rbac";

interface AuthContextType {
  user: UserProfile | null;
  role: Role | null; // null = not signed in
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isSimulationMode: boolean;
  toggleSimulationMode: () => void;
  login: (email: string, password: string) => Promise<Role>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [role, setRole] = useState<Role | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSimulationMode, setIsSimulationMode] = useState<boolean>(false);

  const clearSession = useCallback(() => {
    tokenStorage.clear();
    setToken(null);
    setUser(null);
    setRole(null);
  }, []);

  // Restore a session on page load. The role is NEVER trusted from localStorage:
  // it is re-confirmed by the server (/auth/me), or, if the server is unreachable,
  // taken from the signed JWT claim.
  useEffect(() => {
    let cancelled = false;
    setIsSimulationMode(tokenStorage.isSimulationMode());

    (async () => {
      const storedToken = tokenStorage.getToken();
      if (!storedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await api.getMe(storedToken);
        if (cancelled) return;
        if (!me) {
          clearSession();
        } else {
          tokenStorage.setUser(me);
          setToken(storedToken);
          setUser(me);
          setRole(normalizeRole(me.role));
        }
      } catch {
        if (cancelled) return;
        const jwtRole = roleFromJwt(storedToken);
        const stored = tokenStorage.getUser();
        if (jwtRole && stored) {
          setToken(storedToken);
          setUser({ ...stored, role: jwtRole });
          setRole(jwtRole);
        } else {
          clearSession();
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [clearSession]);

  // End the session if the API ever says the token is no longer valid
  useEffect(() => {
    const onUnauthorized = () => clearSession();
    window.addEventListener("tv:unauthorized", onUnauthorized);
    return () => window.removeEventListener("tv:unauthorized", onUnauthorized);
  }, [clearSession]);

  // Keep multiple tabs in sync (logging out in one tab logs out the others)
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === "tv_access_token" && !e.newValue) clearSession();
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [clearSession]);

  const login = async (email: string, password: string): Promise<Role> => {
    const res = await api.login(email, password); // throws on bad credentials
    const newRole = normalizeRole(res.role);
    tokenStorage.setTokens(res.access_token, res.refresh_token);
    tokenStorage.setUser(res.user);
    setToken(res.access_token);
    setUser(res.user);
    setRole(newRole);
    return newRole;
  };

  const register = async (name: string, email: string, password: string) => {
    await api.register(name, email, password);
    await login(email, password);
  };

  const logout = () => {
    clearSession();
  };

  const toggleSimulationMode = () => {
    const next = !isSimulationMode;
    setIsSimulationMode(next);
    tokenStorage.setSimulationMode(next);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated: !!token && !!role,
        isLoading,
        isSimulationMode,
        toggleSimulationMode,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
