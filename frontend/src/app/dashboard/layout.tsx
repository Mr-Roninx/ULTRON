"use client";

import React, { ReactNode, useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield, LayoutDashboard, Settings, Power, LogOut, ChevronRight, Sparkles,
  Bell, CheckCircle2, CheckCheck, Search, HelpCircle, Zap
} from "lucide-react";
import { useAuth, api } from "../../lib/auth";

interface NotificationItem {
  id: string;
  tenant_id: string;
  type: "LINK_CREATED" | "PAYMENT_RECOVERED" | "SWEEP_COMPLETED" | "INTEGRATION_ERROR" | "KILL_SWITCH_TRIGGERED";
  title: string;
  message: string;
  link_url?: string;
  read: boolean;
  created_at: string;
}

const NAV_ITEMS = [
  { href: "/dashboard", label: "Recovery Hub", icon: LayoutDashboard, exact: true, badge: "LIVE" },
  { href: "/dashboard/setup", label: "Integration Hub", icon: Sparkles, exact: false, highlight: true },
  { href: "/dashboard/settings", label: "Settings", icon: Settings, exact: false },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, tenant, token, loading, logout, switchEnvironment } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [switchingEnv, setSwitchingEnv] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const isLive = tenant?.environment === "live";

  useEffect(() => {
    setMounted(true);
  }, []);

  // Notification Center State
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const notifRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api<{ unread_count: number; notifications: NotificationItem[] }>("/v1/notifications");
      if (data) {
        setUnreadCount(data.unread_count || 0);
        setNotifications(data.notifications || []);
      }
    } catch {
      // ignore background notification errors
    }
  }, [token]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 5000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    if (showNotifications) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showNotifications]);

  const handleMarkAsRead = async (id: string, linkUrl?: string) => {
    try {
      await api(`/v1/notifications/${id}/read`, { method: "POST" });
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
      if (linkUrl) {
        setShowNotifications(false);
        router.push(linkUrl);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api("/v1/notifications/mark-all-read", { method: "POST" });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!loading && !token) {
      router.replace("/login");
    }
  }, [token, loading, router]);

  if (!mounted || loading || !token) {
    return (
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", background: "var(--bg-base)",
      }}>
        <div style={{
          width: 36, height: 36, border: "3px solid #1a73e8",
          borderTopColor: "transparent", borderRadius: "50%",
          animation: "spin 0.7s linear infinite"
        }} />
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
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-base)", color: "var(--text-primary)" }}>
      {/* ── Google Style White Sidebar ── */}
      <aside style={{
        width: 256, flexShrink: 0,
        background: "#ffffff",
        borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column",
        position: "fixed", top: 0, left: 0, bottom: 0,
        zIndex: 50,
      }}>
        {/* Google-Style Header Logo */}
        <div style={{
          padding: "18px 20px 14px",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex", alignItems: "center", justifyContent: "space-between"
        }}>
          <Link href="/dashboard" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "#1a73e8",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 1px 3px rgba(26,115,232,0.3)"
            }}>
              <Shield size={18} color="#ffffff" />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.3px", color: "var(--text-primary)" }}>
                ULTRON
              </div>
              <div style={{ fontSize: 10, color: "var(--text-secondary)", fontWeight: 500, letterSpacing: "0.2px" }}>
                Revenue Control Plane
              </div>
            </div>
          </Link>
        </div>

        {/* Tenant badge */}
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border-subtle)" }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "8px 12px", borderRadius: 8,
            background: "var(--bg-hover)", border: "1px solid var(--border-subtle)"
          }}>
            <div className="status-dot active" />
            <div style={{ overflow: "hidden", flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {tenant?.name || user?.email?.split("@")[0] || "Merchant Org"}
              </div>
              <div style={{ fontSize: 11, color: "var(--google-green)", fontWeight: 500 }}>
                {tenant?.environment === "test" ? "Razorpay Test Mode" : "Production"}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: "16px 12px", overflowY: "auto" }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, letterSpacing: "0.5px", padding: "4px 8px 10px", textTransform: "uppercase" }}>
            Workspace
          </div>
          {NAV_ITEMS.map(({ href, label, icon: Icon, exact, badge, highlight }) => {
            const active = isActive(href, exact);
            return (
              <Link key={href} href={href} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "10px 14px", borderRadius: 12, marginBottom: 6,
                  background: active
                    ? "var(--google-blue-light)"
                    : highlight
                    ? "var(--google-purple-light)"
                    : "transparent",
                  color: active
                    ? "var(--google-blue)"
                    : highlight
                    ? "var(--google-purple)"
                    : "var(--text-secondary)",
                  fontSize: 13, fontWeight: active ? 600 : 500,
                  transition: "all 0.15s ease",
                  cursor: "pointer",
                }}>
                  <Icon size={18} />
                  <span>{label}</span>
                  {badge && (
                    <span style={{
                      marginLeft: "auto", fontSize: 10, fontWeight: 700, padding: "2px 7px",
                      borderRadius: 10, background: "var(--google-green-light)", color: "var(--google-green)",
                    }}>
                      {badge}
                    </span>
                  )}
                  {active && !badge && <ChevronRight size={14} style={{ marginLeft: "auto" }} />}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Kill switch indicator */}
        {tenant?.kill_switch_active && (
          <div style={{
            margin: "0 12px 12px",
            padding: "10px 12px", borderRadius: 8,
            background: "var(--google-red-light)",
            border: "1px solid #fad2cf",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <Power size={15} color="var(--google-red)" />
            <span style={{ fontSize: 12, color: "var(--google-red)", fontWeight: 600 }}>Emergency Kill Switch Active</span>
          </div>
        )}

        {/* User profile footer */}
        <div style={{ padding: "12px 16px", borderTop: "1px solid var(--border-subtle)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%", flexShrink: 0,
              background: "#1a73e8",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 12, fontWeight: 700, color: "#ffffff",
            }}>
              {(user?.email || "U")[0].toUpperCase()}
            </div>
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {user?.email || "merchant@domain.com"}
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{user?.role || "Owner"}</div>
            </div>
            <button
              onClick={handleLogout}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-secondary)", padding: 6, borderRadius: "50%" }}
              title="Sign out"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main Content Area ── */}
      <main style={{ marginLeft: 256, flex: 1, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        {/* Google Style Top Header */}
        <header style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "10px 32px", borderBottom: "1px solid var(--border)",
          background: "#ffffff",
          position: "sticky", top: 0, zIndex: 40,
        }}>
          {/* Search bar */}
          <div style={{
            display: "flex", alignItems: "center", gap: 10,
            background: "var(--bg-hover)", border: "1px solid var(--border-subtle)",
            borderRadius: 24, padding: "8px 16px", width: 440, maxWidth: "100%"
          }}>
            <Search size={16} color="var(--text-secondary)" />
            <input
              type="text"
              placeholder="Search opportunities, phone, ID, bank..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                border: "none", background: "transparent", outline: "none",
                fontSize: 13, color: "var(--text-primary)", width: "100%", fontFamily: "var(--font-sans)"
              }}
            />
          </div>

          {/* Right Header Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            {/* Interactive Test vs Production Mode Switcher */}
            <div
              id="environment-switcher"
              style={{
                display: "flex",
                alignItems: "center",
                background: isLive ? "rgba(19, 115, 51, 0.08)" : "var(--bg-hover)",
                borderRadius: 24,
                padding: "3px 4px",
                border: isLive ? "1px solid #a8dab5" : "1px solid var(--border)",
                gap: 3,
                transition: "all 0.25s ease",
              }}
            >
              {/* Test Sandbox Button */}
              <button
                id="env-btn-test"
                type="button"
                onClick={async () => {
                  if (!isLive || switchingEnv) return;
                  setSwitchingEnv(true);
                  await switchEnvironment("test");
                  setSwitchingEnv(false);
                }}
                disabled={switchingEnv}
                title="Switch to Test Sandbox Mode (Simulated transactions & safe testing)"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "5px 12px",
                  borderRadius: 20,
                  border: "none",
                  cursor: isLive ? "pointer" : "default",
                  background: !isLive ? "#ffffff" : "transparent",
                  color: !isLive ? "#1a73e8" : "var(--text-secondary)",
                  fontSize: 12,
                  fontWeight: !isLive ? 700 : 500,
                  boxShadow: !isLive ? "0 1px 3px rgba(0,0,0,0.12)" : "none",
                  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
              >
                <span>🧪</span>
                <span>Test Sandbox</span>
                {!isLive && (
                  <span style={{
                    width: 6, height: 6, borderRadius: "50%", background: "#1a73e8", display: "inline-block"
                  }} />
                )}
              </button>

              {/* Production Button */}
              <button
                id="env-btn-prod"
                type="button"
                onClick={async () => {
                  if (isLive || switchingEnv) return;
                  const confirmSwitch = window.confirm(
                    "⚡ Switch to Production Mode (Real Money)?\n\n" +
                    "In Production Mode, all recovery payment links will be created via official Razorpay Live credentials and real money will be charged to customers.\n\n" +
                    "Ensure your live credentials (rzp_live_...) are connected in Settings → Integrations."
                  );
                  if (!confirmSwitch) return;
                  setSwitchingEnv(true);
                  await switchEnvironment("live");
                  setSwitchingEnv(false);
                }}
                disabled={switchingEnv}
                title="Switch to Production Mode (Real money recovery via live Razorpay account)"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "5px 13px",
                  borderRadius: 20,
                  border: "none",
                  cursor: !isLive ? "pointer" : "default",
                  background: isLive ? "#137333" : "transparent",
                  color: isLive ? "#ffffff" : "var(--text-secondary)",
                  fontSize: 12,
                  fontWeight: isLive ? 700 : 500,
                  boxShadow: isLive ? "0 1px 4px rgba(19, 115, 51, 0.35)" : "none",
                  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
              >
                <Zap size={13} color={isLive ? "#ffffff" : "var(--text-secondary)"} />
                <span>Production (Real Money)</span>
                {isLive && (
                  <span style={{
                    width: 7, height: 7, borderRadius: "50%", background: "#a8dab5",
                    boxShadow: "0 0 6px #ffffff", display: "inline-block"
                  }} />
                )}
              </button>
            </div>

            {/* Quick Docs Link */}
            <a
              href="https://razorpay.com/docs/payments/payment-links"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-ghost"
              style={{ padding: "6px 10px", fontSize: 12, gap: 5 }}
            >
              <HelpCircle size={15} />
              <span>Docs</span>
            </a>

            {/* Notification Bell */}
            <div ref={notifRef} style={{ position: "relative" }}>
              <button
                id="notification-bell-btn"
                onClick={() => setShowNotifications(!showNotifications)}
                style={{
                  background: showNotifications ? "var(--bg-hover)" : "transparent",
                  border: "1px solid var(--border)",
                  padding: "7px 12px",
                  borderRadius: 20,
                  cursor: "pointer",
                  color: "var(--text-primary)",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  position: "relative",
                  transition: "all 0.15s",
                }}
              >
                <Bell size={15} color={unreadCount > 0 ? "var(--google-blue)" : "var(--text-secondary)"} />
                <span style={{ fontSize: 12, fontWeight: 500 }}>Activity</span>
                {unreadCount > 0 && (
                  <span style={{
                    background: "var(--google-red)",
                    color: "white",
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "1px 6px",
                    borderRadius: 10,
                  }}>
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification Drawer */}
              {showNotifications && (
                <div
                  className="animate-fade-in card"
                  style={{
                    position: "absolute",
                    right: 0,
                    top: 42,
                    width: 380,
                    maxHeight: 460,
                    padding: 0,
                    background: "#ffffff",
                    border: "1px solid var(--border)",
                    borderRadius: 10,
                    boxShadow: "var(--shadow-dropdown)",
                    zIndex: 50,
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <div style={{
                    padding: "12px 16px",
                    borderBottom: "1px solid var(--border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    background: "#f8f9fa",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <Bell size={15} color="var(--google-blue)" />
                      <h4 style={{ fontSize: 13, fontWeight: 700, margin: 0 }}>Recovery Activity</h4>
                    </div>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllAsRead}
                        style={{
                          background: "none", border: "none", cursor: "pointer",
                          color: "var(--google-blue)", fontSize: 11, fontWeight: 600,
                          display: "flex", alignItems: "center", gap: 4,
                        }}
                      >
                        <CheckCheck size={13} /> Mark all read
                      </button>
                    )}
                  </div>

                  <div style={{ flex: 1, overflowY: "auto", maxHeight: 380 }}>
                    {notifications.length === 0 ? (
                      <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>
                        <CheckCircle2 size={24} style={{ margin: "0 auto 8px", color: "var(--google-green)" }} />
                        All caught up! No recent recovery notifications.
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => handleMarkAsRead(n.id, n.link_url)}
                          style={{
                            padding: "12px 16px",
                            borderBottom: "1px solid var(--border-subtle)",
                            background: n.read ? "transparent" : "var(--google-blue-light)",
                            cursor: "pointer",
                            transition: "background 0.15s",
                            display: "flex",
                            gap: 12,
                            alignItems: "flex-start",
                          }}
                        >
                          <div style={{ flex: 1, overflow: "hidden" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                              <div style={{ fontSize: 13, fontWeight: n.read ? 500 : 700, color: "var(--text-primary)" }}>
                                {n.title}
                              </div>
                              {!n.read && (
                                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--google-blue)" }} />
                              )}
                            </div>
                            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4, lineHeight: 1.4 }}>
                              {n.message}
                            </div>
                            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                              {new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Body content */}
        <div style={{ flex: 1, padding: "24px 32px" }}>
          {children}
        </div>
      </main>
    </div>
  );
}
