"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { supabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
const TOKEN_KEY = "ultron_session_token";
const USER_KEY = "ultron_user_profile";
const TENANT_KEY = "ultron_tenant_profile";

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
  const [state, setState] = useState<AuthState>(() => {
    if (typeof window === "undefined") {
      return { token: null, user: null, tenant: null, loading: true };
    }
    const token = localStorage.getItem(TOKEN_KEY);
    let user: AuthUser | null = null;
    let tenant: AuthTenant | null = null;
    try {
      const storedUser = localStorage.getItem(USER_KEY);
      if (storedUser) user = JSON.parse(storedUser);
      const storedTenant = localStorage.getItem(TENANT_KEY);
      if (storedTenant) tenant = JSON.parse(storedTenant);
    } catch {}

    return { token, user, tenant, loading: !token };
  });

  const saveToStorage = useCallback((token: string | null, user: AuthUser | null, tenant: AuthTenant | null) => {
    if (typeof window === "undefined") return;
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
    if (tenant) {
      localStorage.setItem(TENANT_KEY, JSON.stringify(tenant));
    } else {
      localStorage.removeItem(TENANT_KEY);
    }
  }, []);

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

  // Restore session from localStorage or Supabase on mount
  useEffect(() => {
    let mounted = true;

    const restoreSession = async () => {
      // 1. Primary: Check stored backend session token
      const stored = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
      if (stored) {
        const data = await fetchMe(stored);
        if (!mounted) return;
        if (data?.user) {
          saveToStorage(stored, data.user, data.tenant);
          setState({ token: stored, user: data.user, tenant: data.tenant, loading: false });
          return;
        }
      }

      // 2. Fallback: Check Supabase Auth session
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!mounted) return;
        if (session?.access_token) {
          const token = session.access_token;
          const data = await fetchMe(token);
          if (!mounted) return;
          const userMeta = session.user.user_metadata || {};
          const tenantId = data?.user?.tenantId || data?.tenant?.id || userMeta.tenant_id || `tnt_${session.user.id.slice(0, 8)}`;
          const user: AuthUser = data?.user || {
            userId: session.user.id,
            email: session.user.email || "",
            name: userMeta.business_name || session.user.email?.split("@")[0] || "Merchant",
            role: userMeta.role || "Owner",
            tenantId,
          };
          const tenant = data?.tenant || (tenantId ? {
            id: tenantId,
            name: userMeta.business_name || user.name || "Merchant",
            slug: `merchant_${tenantId}`,
            environment: "test",
            status: "ACTIVE",
            capacity_limit: 5,
            kill_switch_active: false,
          } : null);
          saveToStorage(token, user, tenant);
          setState({ token, user, tenant, loading: false });
          return;
        }
      } catch {}

      if (mounted) {
        saveToStorage(null, null, null);
        setState({ token: null, user: null, tenant: null, loading: false });
      }
    };

    restoreSession();

    // 3. Listen to Supabase Auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (!mounted) return;
      if (session?.access_token) {
        const token = session.access_token;
        const data = await fetchMe(token);
        if (!mounted) return;
        const userMeta = session.user.user_metadata || {};
        const tenantId = data?.user?.tenantId || data?.tenant?.id || userMeta.tenant_id || `tnt_${session.user.id.slice(0, 8)}`;
        const user: AuthUser = data?.user || {
          userId: session.user.id,
          email: session.user.email || "",
          name: userMeta.business_name || session.user.email?.split("@")[0] || "Merchant",
          role: userMeta.role || "Owner",
          tenantId,
        };
        const tenant = data?.tenant || (tenantId ? {
          id: tenantId,
          name: userMeta.business_name || user.name || "Merchant",
          slug: `merchant_${tenantId}`,
          environment: "test",
          status: "ACTIVE",
          capacity_limit: 5,
          kill_switch_active: false,
        } : null);
        saveToStorage(token, user, tenant);
        setState({ token, user, tenant, loading: false });
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [fetchMe, saveToStorage]);

  const login = async (email: string, password: string) => {
    try {
      // 1. Primary: Authenticate with ULTRON backend API
      const res = await fetch(`${API_BASE}/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data?.session?.token) {
        const token = data.session.token;
        const me = await fetchMe(token);
        const merchantTenantId = data.merchant?.tenant_id || data.merchant?.id;

        const user: AuthUser = me?.user || (data.user ? {
          userId: data.user.id,
          email: data.user.email,
          name: data.user.name,
          role: data.user.role,
          tenantId: merchantTenantId || `tnt_${data.user.id.slice(0, 8)}`,
        } : (data.merchant ? {
          userId: data.merchant.user_id || data.merchant.id,
          email: data.merchant.email,
          name: data.merchant.name,
          role: data.merchant.role,
          tenantId: merchantTenantId,
        } : {
          userId: "usr_merchant",
          email,
          role: "Owner",
          tenantId: merchantTenantId || "tenant_default",
        }));

        const tenant: AuthTenant | null = me?.tenant || (merchantTenantId ? {
          id: merchantTenantId,
          name: data.merchant?.name || data.merchant?.business_name || "Merchant",
          slug: `merchant_${merchantTenantId}`,
          environment: data.merchant?.environment || "test",
          status: data.merchant?.status || "ACTIVE",
          capacity_limit: 5,
          kill_switch_active: false,
        } : null);

        saveToStorage(token, user, tenant);

        setState({
          token,
          user,
          tenant,
          loading: false,
        });

        // Non-blocking sync with Supabase
        supabase.auth.signInWithPassword({ email, password }).catch(() => {});

        return { success: true };
      }

      // 2. Fallback: Try Supabase Auth if backend credentials didn't match
      const { data: sbData, error: sbError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (!sbError && sbData?.session?.access_token) {
        const token = sbData.session.access_token;
        const me = await fetchMe(token);
        const userMeta = sbData.user.user_metadata || {};
        const tenantId = me?.user?.tenantId || me?.tenant?.id || userMeta.tenant_id || `tnt_${sbData.user.id.slice(0, 8)}`;

        const user: AuthUser = me?.user || {
          userId: sbData.user.id,
          email: sbData.user.email || "",
          name: userMeta.business_name || email.split("@")[0],
          role: userMeta.role || "Owner",
          tenantId,
        };

        const tenant = me?.tenant || {
          id: tenantId,
          name: userMeta.business_name || user.name || "Merchant",
          slug: `merchant_${tenantId}`,
          environment: "test",
          status: "ACTIVE",
          capacity_limit: 5,
          kill_switch_active: false,
        };
        saveToStorage(token, user, tenant);

        setState({
          token,
          user,
          tenant,
          loading: false,
        });
        return { success: true };
      }

      return {
        success: false,
        error: data.message || data.error || sbError?.message || "Invalid email or password",
      };
    } catch (err: any) {
      return { success: false, error: err.message || "Network error connecting to auth server" };
    }
  };

  const signup = async (email: string, business_name: string, password: string) => {
    try {
      // 1. Register tenant with ULTRON backend
      const res = await fetch(`${API_BASE}/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, business_name, password }),
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        return {
          success: false,
          error: data.message || data.error || data.details || `Signup failed (${res.status})`,
        };
      }

      const token = data?.session?.token;
      if (token) {
        const me = await fetchMe(token);
        const merchantTenantId = data.merchant?.tenant_id || data.merchant?.id;

        const user: AuthUser = me?.user || (data.user ? {
          userId: data.user.id,
          email: data.user.email,
          name: data.user.name,
          role: data.user.role,
          tenantId: merchantTenantId || `tnt_${data.user.id.slice(0, 8)}`,
        } : (data.merchant ? {
          userId: data.merchant.user_id || data.merchant.id,
          email: data.merchant.email,
          name: data.merchant.business_name || data.merchant.name,
          role: data.merchant.role,
          tenantId: merchantTenantId,
        } : {
          userId: "usr_merchant",
          email,
          role: "Owner",
          tenantId: merchantTenantId || "tenant_default",
        }));

        const tenant: AuthTenant | null = me?.tenant || (merchantTenantId ? {
          id: merchantTenantId,
          name: data.merchant?.business_name || data.merchant?.name || business_name,
          slug: `merchant_${merchantTenantId}`,
          environment: data.merchant?.environment || "test",
          status: data.merchant?.status || "ACTIVE",
          capacity_limit: 5,
          kill_switch_active: false,
        } : null);

        saveToStorage(token, user, tenant);

        setState({
          token,
          user,
          tenant,
          loading: false,
        });
      }

      // Non-blocking sync with Supabase Auth
      supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            business_name,
            role: "Owner",
            tenant_id: data?.merchant?.tenant_id || data?.merchant?.id,
          },
        },
      }).catch(() => {});

      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || "Network error connecting to backend API" };
    }
  };

  const logout = async () => {
    const token = state.token;
    saveToStorage(null, null, null);
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
    if (me) {
      saveToStorage(state.token, me.user, me.tenant);
      setState((s) => ({ ...s, user: me.user, tenant: me.tenant }));
    }
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
  let token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // If 401 Unauthorized, attempt a quick session recovery with Supabase before failing
  if (res.status === 401 && typeof window !== "undefined") {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token && session.access_token !== token) {
        token = session.access_token;
        localStorage.setItem(TOKEN_KEY, token);
        headers["Authorization"] = `Bearer ${token}`;
        res = await fetch(`${API_BASE}${path}`, { ...options, headers });
      }
    } catch {
      // Ignore recovery errors
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    const errorMessage = err.message || err.error || err.details || `API error ${res.status}`;

    // Only redirect on genuine 401 Unauthorized if not already on auth pages
    if (res.status === 401) {
      if (typeof window !== "undefined" && window.location.pathname !== "/login" && window.location.pathname !== "/signup") {
        console.warn("Session expired. Redirecting to login...");
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = "/login";
      }
    }

    throw new Error(errorMessage);
  }
  return res.json();
}
