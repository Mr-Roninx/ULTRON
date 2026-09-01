"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { supabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
const TOKEN_KEY = "ultron_session_token";

export interface AuthUser {
  userId: string;
  tenantId: string;
  email: string;
  name?: string;
  role: string;
  mfaVerified?: boolean;
}

export interface AuthTenant {
  id: string;
  name: string;
  slug: string;
  environment: string;
  status: string;
  capacity_limit: number;
  kill_switch_active: boolean;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  tenant: AuthTenant | null;
  loading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (email: string, business_name: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    tenant: null,
    loading: true,
  });

  const fetchMe = useCallback(async (token: string) => {
    try {
      const res = await fetch(`${API_BASE}/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return null;
      const data = await res.json();
      return { user: data.user, tenant: data.tenant };
    } catch {
      return null;
    }
  }, []);

  // Restore session from Supabase or localStorage on mount
  useEffect(() => {
    let mounted = true;

    // 1. Check Supabase Auth session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!mounted) return;
      if (session?.access_token) {
        const token = session.access_token;
        localStorage.setItem(TOKEN_KEY, token);
        fetchMe(token).then((data) => {
          if (!mounted) return;
          const userMeta = session.user.user_metadata || {};
          setState({
            token,
            user: data?.user || {
              userId: session.user.id,
              email: session.user.email || "",
              name: userMeta.business_name || session.user.email?.split("@")[0] || "Merchant",
              role: userMeta.role || "Owner",
              tenantId: userMeta.tenant_id || `tnt_${session.user.id.slice(0, 8)}`,
            },
            tenant: data?.tenant || null,
            loading: false,
          });
        });
        return;
      }

      // 2. Fallback to local storage token
      const stored = localStorage.getItem(TOKEN_KEY);
      if (!stored) {
        setState((s) => ({ ...s, loading: false }));
        return;
      }

      fetchMe(stored).then((data) => {
        if (!mounted) return;
        if (data) {
          setState({ token: stored, user: data.user, tenant: data.tenant, loading: false });
        } else {
          localStorage.removeItem(TOKEN_KEY);
          setState({ token: null, user: null, tenant: null, loading: false });
        }
      });
    });

    // 3. Listen to Supabase Auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!mounted) return;
      if (session?.access_token) {
        const token = session.access_token;
        localStorage.setItem(TOKEN_KEY, token);
        fetchMe(token).then((data) => {
          if (!mounted) return;
          const userMeta = session.user.user_metadata || {};
          setState({
            token,
            user: data?.user || {
              userId: session.user.id,
              email: session.user.email || "",
              name: userMeta.business_name || session.user.email?.split("@")[0] || "Merchant",
              role: userMeta.role || "Owner",
              tenantId: userMeta.tenant_id || `tnt_${session.user.id.slice(0, 8)}`,
            },
            tenant: data?.tenant || null,
            loading: false,
          });
        });
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [fetchMe]);

  const login = async (email: string, password: string) => {
    try {
      // 1. Try Supabase Auth first
      const { data: sbData, error: sbError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (!sbError && sbData?.session?.access_token) {
        const token = sbData.session.access_token;
        localStorage.setItem(TOKEN_KEY, token);
        const me = await fetchMe(token);
        const userMeta = sbData.user.user_metadata || {};
        setState({
          token,
          user: me?.user || {
            userId: sbData.user.id,
            email: sbData.user.email || "",
            name: userMeta.business_name || email.split("@")[0],
            role: userMeta.role || "Owner",
            tenantId: userMeta.tenant_id || `tnt_${sbData.user.id.slice(0, 8)}`,
          },
          tenant: me?.tenant || null,
          loading: false,
        });
        return { success: true };
      }

      // 2. Fallback to ULTRON API auth
      const res = await fetch(`${API_BASE}/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) return { success: false, error: data.message || sbError?.message || "Login failed" };

      const token = data.session.token;
      localStorage.setItem(TOKEN_KEY, token);
      const me = await fetchMe(token);
      setState({ token, user: me?.user || data.merchant, tenant: me?.tenant || null, loading: false });
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || "Network error" };
    }
  };

  const signup = async (email: string, business_name: string, password: string) => {
    try {
      // 1. Attempt Supabase Auth signup (non-blocking)
      const { data: sbData } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            business_name,
            role: "Owner",
          },
        },
      }).catch(() => ({ data: null }));

      // 2. Register tenant with ULTRON backend
      const res = await fetch(`${API_BASE}/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, business_name, password }),
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        return { success: false, error: data.message || data.error || data.details || `Signup failed (${res.status})` };
      }

      const token = data?.session?.token || sbData?.session?.access_token;
      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
        const me = await fetchMe(token);
        setState({ token, user: me?.user || data?.merchant, tenant: me?.tenant || null, loading: false });
      }

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || "Network error connecting to backend API" };
    }
  };

  const logout = async () => {
    const token = state.token;
    localStorage.removeItem(TOKEN_KEY);
    setState({ token: null, user: null, tenant: null, loading: false });
    
    // Sign out from Supabase & backend
    supabase.auth.signOut().catch(() => {});
    if (token) {
      fetch(`${API_BASE}/v1/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});
    }
  };

  const refresh = async () => {
    if (!state.token) return;
    const me = await fetchMe(state.token);
    if (me) setState((s) => ({ ...s, user: me.user, tenant: me.tenant }));
  };

  return (
    <AuthContext.Provider value={{ ...state, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

// Typed API fetcher — auto-attaches Bearer token from storage
export async function api<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      localStorage.removeItem(TOKEN_KEY);
      window.location.href = '/login';
    }
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `API error ${res.status}`);
  }
  return res.json();
}
