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
  { href: "/presentation", label: "Visual Presentation", icon: Sparkles, exact: false, badge: "DECK" },
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
        minHeight: "100vh", background: "#02042B",
      }}>
        <div style={{
          width: 36, height: 36, border: "3px solid #0C83FF",
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
      {/* ── Razorpay Iconic Midnight Navy Sidebar ── */}
      <aside style={{
        width: 260, flexShrink: 0,
        background: "#02042B",
        borderRight: "1px solid #171E52",
        display: "flex", flexDirection: "column",
        position: "fixed", top: 0, left: 0, bottom: 0,
        zIndex: 50,
      }}>
        {/* Razorpay Brand Header with Stylized Chevron Emblem */}
        <div style={{
          padding: "20px 20px 16px",
          borderBottom: "1px solid #121742",
          display: "flex", alignItems: "center", justifyContent: "space-between"
        }}>
          <Link href="/dashboard" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 11 }}>
            {/* Razorpay Precision Emblem */}
            <div style={{
              width: 34, height: 34, borderRadius: 6,
              background: "linear-gradient(135deg, #0C83FF 0%, #0052CC 100%)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 2px 10px rgba(12, 131, 255, 0.4)",
              position: "relative", overflow: "hidden"
            }}>
              {/* Angular Razor Slash */}
              <div style={{
                position: "absolute", top: -4, right: -4, width: 14, height: 14,
                background: "#00D09C", transform: "rotate(45deg)", opacity: 0.9
              }} />
              <Shield size={19} color="#ffffff" style={{ position: "relative", zIndex: 2 }} />
            </div>
            <div>
              <div style={{
                fontSize: 17, fontWeight: 800, letterSpacing: "-0.4px",
                color: "#ffffff", display: "flex", alignItems: "center", gap: 6
              }}>
                <span>ULTRON</span>
                <span style={{
                  fontSize: 9, fontWeight: 700, padding: "1px 5px", borderRadius: 3,
                  background: "rgba(12, 131, 255, 0.25)", color: "#58A6FF", border: "1px solid rgba(12, 131, 255, 0.4)"
                }}>
                  RZP
                </span>
              </div>
              <div style={{ fontSize: 10, color: "#8492A6", fontWeight: 500, letterSpacing: "0.2px" }}>
                Autonomous Recovery Engine
              </div>
            </div>
          </Link>
        </div>

        {/* Merchant Org Badge with Live Dot */}
        <div style={{ padding: "12px 16px", borderBottom: "1px solid #121742" }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 9,
            padding: "9px 12px", borderRadius: 6,
            background: "#080C34", border: "1px solid #1E2659"
          }}>
            <div className="status-dot active" style={{ width: 7, height: 7 }} />
            <div style={{ overflow: "hidden", flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#ffffff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {tenant?.name || user?.email?.split("@")[0] || "Merchant Org"}
              </div>
              <div style={{ fontSize: 11, color: isLive ? "#00D09C" : "#58A6FF", fontWeight: 500 }}>
                {isLive ? "⚡ Live Gateway Active" : "🧪 Razorpay Test Mode"}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ flex: 1, padding: "16px 12px", overflowY: "auto" }}>
          <div style={{
            fontSize: 10, color: "#525D7E", fontWeight: 700, letterSpacing: "0.8px",
            padding: "4px 10px 10px", textTransform: "uppercase"
          }}>
            Merchant Control
          </div>
          {NAV_ITEMS.map(({ href, label, icon: Icon, exact, badge, highlight }) => {
            const active = isActive(href, exact);
            return (
              <Link key={href} href={href} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 11,
                  padding: "10px 14px", borderRadius: 6, marginBottom: 4,
                  background: active
                    ? "#0C83FF"
                    : highlight
                    ? "rgba(121, 82, 222, 0.12)"
                    : "transparent",
                  color: active
                    ? "#ffffff"
                    : highlight
                    ? "#B794F4"
                    : "#94A3B8",
                  fontSize: 13, fontWeight: active ? 600 : 500,
                  boxShadow: active ? "0 2px 8px rgba(12, 131, 255, 0.4)" : "none",
                  transition: "all 0.15s ease",
                  cursor: "pointer",
                }}>
                  <Icon size={17} color={active ? "#ffffff" : highlight ? "#B794F4" : "#8492A6"} />
                  <span>{label}</span>
                  {badge && (
                    <span style={{
                      marginLeft: "auto", fontSize: 9, fontWeight: 700, padding: "2px 6px",
                      borderRadius: 4,
                      background: badge === "LIVE" ? "rgba(0, 208, 156, 0.18)" : "rgba(255, 153, 0, 0.18)",
                      color: badge === "LIVE" ? "#00D09C" : "#FF9900",
                      border: badge === "LIVE" ? "1px solid rgba(0, 208, 156, 0.35)" : "1px solid rgba(255, 153, 0, 0.35)",
                    }}>
                      {badge}
                    </span>
                  )}
                  {active && !badge && <ChevronRight size={14} style={{ marginLeft: "auto", opacity: 0.8 }} />}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Kill Switch Indicator */}
        {tenant?.kill_switch_active && (
          <div style={{
            margin: "0 12px 12px",
            padding: "10px 12px", borderRadius: 6,
            background: "rgba(244, 63, 94, 0.15)",
            border: "1px solid rgba(244, 63, 94, 0.35)",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <Power size={15} color="#F43F5E" />
            <span style={{ fontSize: 11, color: "#FB7185", fontWeight: 700 }}>Emergency Kill Switch Active</span>
          </div>
        )}

        {/* User Profile Footer */}
        <div style={{ padding: "14px 16px", borderTop: "1px solid #121742", background: "#040730" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 6, flexShrink: 0,
              background: "linear-gradient(135deg, #0C83FF 0%, #0052CC 100%)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 12, fontWeight: 700, color: "#ffffff",
              boxShadow: "0 2px 6px rgba(12, 131, 255, 0.25)"
            }}>
              {(user?.email || "U")[0].toUpperCase()}
            </div>
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#ffffff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {user?.email || "merchant@domain.com"}
              </div>
              <div style={{ fontSize: 10, color: "#8492A6" }}>{user?.role || "Owner"} · Razorpay Org</div>
            </div>
            <button
              onClick={handleLogout}
              style={{ background: "none", border: "none", cursor: "pointer", color: "#8492A6", padding: 6, borderRadius: 4, transition: "color 0.15s" }}
              title="Sign out"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main Content Area ── */}
      <main style={{ marginLeft: 260, flex: 1, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        {/* Razorpay Fintech Top Header */}
        <header style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "10px 32px", borderBottom: "1px solid var(--border)",
          background: "#ffffff",
          position: "sticky", top: 0, zIndex: 40,
        }}>
          {/* Search Bar */}
          <div style={{
            display: "flex", alignItems: "center", gap: 10,
            background: "#F4F6FA", border: "1px solid var(--border)",
            borderRadius: 6, padding: "7px 14px", width: 440, maxWidth: "100%",
            transition: "all 0.15s ease",
          }}>
            <Search size={15} color="#525D7E" />
            <input
              type="text"
              placeholder="Search by opportunity ID, customer phone, bank, UTR..."
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
            {/* Interactive Razorpay Test vs Production Mode Switcher */}
            <div
              id="environment-switcher"
              style={{
                display: "flex",
                alignItems: "center",
                background: isLive ? "rgba(0, 208, 156, 0.08)" : "#F0F4F9",
                borderRadius: 6,
                padding: "3px 4px",
                border: isLive ? "1px solid #00D09C" : "1px solid #CBD5E1",
                gap: 2,
                transition: "all 0.2s ease",
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
                title="Switch to Razorpay Test Mode (Simulated transactions & safe sandbox)"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "5px 12px",
                  borderRadius: 4,
                  border: "none",
                  cursor: isLive ? "pointer" : "default",
                  background: !isLive ? "#ffffff" : "transparent",
                  color: !isLive ? "#0C83FF" : "#525D7E",
                  fontSize: 12,
                  fontWeight: !isLive ? 700 : 500,
                  boxShadow: !isLive ? "0 1px 3px rgba(0,0,0,0.12)" : "none",
                  transition: "all 0.15s ease",
                }}
              >
                <span>🧪</span>
                <span>Test Mode</span>
                {!isLive && (
                  <span style={{
                    width: 6, height: 6, borderRadius: "50%", background: "#0C83FF", display: "inline-block"
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
                  borderRadius: 4,
                  border: "none",
                  cursor: !isLive ? "pointer" : "default",
                  background: isLive ? "#00D09C" : "transparent",
                  color: isLive ? "#02042B" : "#525D7E",
                  fontSize: 12,
                  fontWeight: isLive ? 800 : 500,
                  boxShadow: isLive ? "0 1px 4px rgba(0, 208, 156, 0.4)" : "none",
                  transition: "all 0.15s ease",
                }}
              >
                <Zap size={13} color={isLive ? "#02042B" : "#525D7E"} />
                <span>Live Mode</span>
                {isLive && (
                  <span style={{
                    width: 7, height: 7, borderRadius: "50%", background: "#02042B",
                    display: "inline-block"
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
                  borderRadius: 6,
                  cursor: "pointer",
                  color: "var(--text-primary)",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  position: "relative",
                  transition: "all 0.15s",
                }}
              >
                <Bell size={15} color={unreadCount > 0 ? "var(--rzp-blue)" : "var(--text-secondary)"} />
                <span style={{ fontSize: 12, fontWeight: 600 }}>Activity</span>
                {unreadCount > 0 && (
                  <span style={{
                    background: "var(--rzp-crimson)",
                    color: "white",
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "1px 6px",
                    borderRadius: 4,
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
                    borderRadius: 6,
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
                    background: "#F8F9FD",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <Bell size={15} color="var(--rzp-blue)" />
                      <h4 style={{ fontSize: 13, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>Recovery Activity</h4>
                    </div>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllAsRead}
                        style={{
                          background: "none", border: "none", cursor: "pointer",
                          color: "var(--rzp-blue)", fontSize: 11, fontWeight: 600,
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
                        <CheckCircle2 size={24} style={{ margin: "0 auto 8px", color: "var(--rzp-emerald)" }} />
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
                            background: n.read ? "transparent" : "var(--rzp-blue-light)",
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
                                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--rzp-blue)" }} />
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

        {/* Body Content */}
        <div style={{ flex: 1, padding: "24px 32px" }}>
          {children}
        </div>
      </main>
    </div>
  );
}
