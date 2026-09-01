"use client";

import React, { ReactNode, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield, LayoutDashboard, Zap, Activity, BarChart2,
  Settings, Key, Users, ScrollText, Power, LogOut, ChevronRight,
} from "lucide-react";
import { useAuth } from "../../lib/auth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/opportunities", label: "Opportunities", icon: Activity },
  { href: "/dashboard/market", label: "Recovery Market", icon: BarChart2 },
  { href: "/dashboard/execution", label: "Execution", icon: Zap },
  { href: "/dashboard/audit", label: "Audit Log", icon: ScrollText },
];

const SETTINGS_NAV = [
  { href: "/dashboard/settings", label: "General", icon: Settings, exact: true },
  { href: "/dashboard/settings/integrations", label: "Integrations", icon: Key },
  { href: "/dashboard/settings/api-keys", label: "API Keys", icon: Key },
  { href: "/dashboard/settings/team", label: "Team", icon: Users },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, tenant, token, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Redirect to login if unauthenticated
  useEffect(() => {
    if (!loading && !token) {
      router.replace("/login");
    }
  }, [token, loading, router]);

  if (loading || !token) {
    return (
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", background: "var(--bg-base)",
      }}>
        <div style={{ width: 32, height: 32, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    );
  }

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-base)" }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 240, flexShrink: 0,
        background: "var(--bg-surface)",
        borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column",
        position: "fixed", top: 0, left: 0, bottom: 0,
        zIndex: 50,
      }}>
        {/* Logo */}
        <div style={{
          padding: "20px 20px 16px",
          borderBottom: "1px solid var(--border)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 10,
              background: "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))",
              border: "1px solid rgba(59,130,246,0.3)",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}>
              <Shield size={16} color="var(--electric-blue)" />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: "-0.3px" }}>ULTRON</div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", letterSpacing: "0.5px" }}>CONTROL PLANE</div>
            </div>
          </div>
        </div>

        {/* Tenant badge */}
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", borderRadius: 8, background: "var(--bg-hover)" }}>
            <div className="status-dot active" />
            <div style={{ overflow: "hidden" }}>
              <div style={{ fontSize: 12, fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {tenant?.name || user?.email?.split("@")[0] || "Merchant"}
              </div>
              <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                {tenant?.environment === "test" ? "Test Mode" : "Live Mode"}
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "12px 8px", overflowY: "auto" }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 600, letterSpacing: "1px", padding: "0 8px 8px", textTransform: "uppercase" }}>
            Recovery Pipeline
          </div>
          {NAV_ITEMS.map(({ href, label, icon: Icon, exact }) => {
            const active = isActive(href, exact);
            return (
              <Link key={href} href={href} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "8px 10px", borderRadius: 8, marginBottom: 2,
                  background: active ? "rgba(59,130,246,0.12)" : "transparent",
                  color: active ? "var(--electric-blue)" : "var(--text-secondary)",
                  fontSize: 13, fontWeight: active ? 600 : 400,
                  transition: "all 0.15s",
                  cursor: "pointer",
                  borderLeft: active ? "2px solid var(--electric-blue)" : "2px solid transparent",
                }}>
                  <Icon size={16} />
                  {label}
                  {active && <ChevronRight size={12} style={{ marginLeft: "auto" }} />}
                </div>
              </Link>
            );
          })}

          <div style={{ height: 1, background: "var(--border)", margin: "12px 8px" }} />

          <div style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 600, letterSpacing: "1px", padding: "0 8px 8px", textTransform: "uppercase" }}>
            Settings
          </div>
          {SETTINGS_NAV.map(({ href, label, icon: Icon, exact }) => {
            const active = isActive(href, exact);
            return (
              <Link key={href} href={href} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "8px 10px", borderRadius: 8, marginBottom: 2,
                  background: active ? "rgba(59,130,246,0.12)" : "transparent",
                  color: active ? "var(--electric-blue)" : "var(--text-secondary)",
                  fontSize: 13, fontWeight: active ? 600 : 400,
                  transition: "all 0.15s",
                  cursor: "pointer",
                  borderLeft: active ? "2px solid var(--electric-blue)" : "2px solid transparent",
                }}>
                  <Icon size={16} />
                  {label}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Kill switch indicator */}
        {tenant?.kill_switch_active && (
          <div style={{
            margin: "0 8px 8px",
            padding: "10px 12px", borderRadius: 8,
            background: "rgba(244,63,94,0.15)",
            border: "1px solid rgba(244,63,94,0.3)",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <Power size={14} color="var(--rose)" />
            <span style={{ fontSize: 12, color: "var(--rose)", fontWeight: 600 }}>Kill Switch Active</span>
          </div>
        )}

        {/* User footer */}
        <div style={{ padding: "12px 8px", borderTop: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", borderRadius: 8 }}>
            <div style={{
              width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
              background: "var(--gradient-brand)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 11, fontWeight: 700, color: "white",
            }}>
              {(user?.email || "?")[0].toUpperCase()}
            </div>
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{ fontSize: 12, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {user?.email || "Unknown"}
              </div>
              <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{user?.role || "Owner"}</div>
            </div>
            <button
              onClick={handleLogout}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 4, borderRadius: 6 }}
              title="Sign out"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main style={{ marginLeft: 240, flex: 1, padding: "28px 32px", minHeight: "100vh" }}>
        {children}
      </main>
    </div>
  );
}
