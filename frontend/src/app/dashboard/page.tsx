"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  TrendingUp, AlertTriangle, Zap, BarChart2, Shield, Activity,
  RefreshCw, Power, CheckCircle2, Clock, XCircle, ChevronRight,
} from "lucide-react";
import { useAuth, api } from "../../lib/auth";
import { supabase } from "../../lib/supabase";

interface Summary {
  total_opportunities: number;
  total_at_risk_display: string;
  total_recovered_display: string;
  real_recovered_count: number;
  synthetic_recovered_count: number;
  shadow_price_display: string;
  capacity_limit: number;
  capacity_used: number;
  capacity_available: number;
  kill_switch_active: boolean;
  status_counts: Record<string, number>;
  total_execution_records: number;
}

function KPICard({
  label, value, sub, icon: Icon, color, glow,
}: {
  label: string; value: string; sub?: string;
  icon: React.ElementType; color: string; glow?: boolean;
}) {
  return (
    <div className={`card ${glow ? "animate-pulse-glow" : ""}`} style={{
      display: "flex", flexDirection: "column", gap: 12,
      border: `1px solid rgba(${color}, 0.2)`,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: `rgba(${color}, 0.12)`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <Icon size={18} style={{ color: `rgb(${color})` }} />
        </div>
        <span style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
      </div>
      <div>
        <div style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-1px" }}>{value}</div>
        {sub && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{sub}</div>}
      </div>
    </div>
  );
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  pending:       { label: "Pending",       color: "var(--amber)",        icon: Clock },
  scored:        { label: "Scored",        color: "var(--electric-blue)", icon: BarChart2 },
  allocated:     { label: "Allocated",     color: "var(--violet)",       icon: ChevronRight },
  authorized:    { label: "Authorized",    color: "var(--cyan)",         icon: Shield },
  executing:     { label: "Executing",     color: "var(--violet)",       icon: Zap },
  recovered:     { label: "Recovered",     color: "var(--emerald)",      icon: CheckCircle2 },
  not_recovered: { label: "Not Recovered", color: "var(--rose)",         icon: XCircle },
  blocked:       { label: "Blocked",       color: "var(--rose)",         icon: XCircle },
  abstained:     { label: "Abstained",     color: "var(--text-muted)",   icon: Activity },
  deferred:      { label: "Deferred",      color: "var(--amber)",        icon: Clock },
};

export default function DashboardPage() {
  const { tenant } = useAuth();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const fetchSummary = useCallback(async () => {
    try {
      const data = await api<Summary>("/dashboard/summary");
      setSummary(data);
      setLastRefresh(new Date());
    } catch (err) {
      console.error("Dashboard fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 5000); // polling fallback

    // Supabase Realtime live sync
    const channel = supabase
      .channel("realtime-dashboard")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "recovery_opportunities" },
        () => {
          fetchSummary();
        }
      )
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "ledger_entries" },
        () => {
          fetchSummary();
        }
      )
      .subscribe();

    return () => {
      clearInterval(interval);
      supabase.removeChannel(channel);
    };
  }, [fetchSummary]);

  const toggleKillSwitch = async () => {
    if (!summary) return;
    try {
      await api("/authority/kill-switch", {
        method: "POST",
        body: JSON.stringify({ enabled: !summary.kill_switch_active }),
      });
      fetchSummary();
    } catch (err: any) {
      alert(`Kill switch error: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 400 }}>
        <div style={{ width: 32, height: 32, border: "2px solid var(--electric-blue)", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 28 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Recovery Overview</h1>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            {tenant?.name || "Your tenant"} · {tenant?.environment === "test" ? "Test Mode" : "Live"} ·{" "}
            Last updated {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" onClick={fetchSummary} style={{ gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button
            id="kill-switch-toggle"
            className={`btn ${summary?.kill_switch_active ? "btn-danger" : "btn-ghost"}`}
            onClick={toggleKillSwitch}
            style={{ gap: 6 }}
          >
            <Power size={14} />
            {summary?.kill_switch_active ? "Kill Switch: ON" : "Kill Switch: OFF"}
          </button>
        </div>
      </div>

      {/* Kill switch warning */}
      {summary?.kill_switch_active && (
        <div style={{
          padding: "14px 18px", borderRadius: 10,
          background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.3)",
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <Power size={18} color="var(--rose)" />
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--rose)" }}>Global Kill Switch Active</div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
              All recovery execution is halted. No new payment links will be created until you disable the kill switch.
            </div>
          </div>
        </div>
      )}

      {/* KPI Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        <KPICard
          label="Total Recovered (real, reconciled)"
          value={summary?.total_recovered_display || "₹0"}
          sub={`${summary?.real_recovered_count || 0} real payments`}
          icon={TrendingUp}
          color="16,185,129"
          glow={Number(summary?.real_recovered_count) > 0}
        />
        <KPICard
          label="Total at Risk"
          value={summary?.total_at_risk_display || "₹0"}
          sub={`${summary?.total_opportunities || 0} opportunities`}
          icon={AlertTriangle}
          color="245,158,11"
        />
        <KPICard
          label="Shadow Price (marginal value)"
          value={summary?.shadow_price_display || "₹0"}
          sub="Model-estimated"
          icon={BarChart2}
          color="139,92,246"
        />
        <KPICard
          label="Capacity Used"
          value={`${summary?.capacity_used || 0} / ${summary?.capacity_limit || 5}`}
          sub={`${summary?.capacity_available || 0} slots available`}
          icon={Zap}
          color="59,130,246"
        />
      </div>

      {/* Status Distribution */}
      <div className="card" style={{ padding: 24 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 20 }}>Opportunity Pipeline</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
          {Object.entries(summary?.status_counts || {})
            .filter(([, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([status, count]) => {
              const cfg = STATUS_CONFIG[status] || { label: status, color: "var(--text-muted)", icon: Activity };
              const Icon = cfg.icon;
              return (
                <div key={status} style={{
                  padding: "12px 14px", borderRadius: 10,
                  background: "var(--bg-surface)",
                  border: "1px solid var(--border)",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                    <Icon size={13} style={{ color: cfg.color }} />
                    <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "capitalize" }}>
                      {cfg.label}
                    </span>
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 700, color: cfg.color }}>{count}</div>
                </div>
              );
            })}
          {Object.entries(summary?.status_counts || {}).filter(([, count]) => count > 0).length === 0 && (
            <div style={{ color: "var(--text-muted)", fontSize: 13, gridColumn: "1 / -1", textAlign: "center", padding: "24px 0" }}>
              No active recovery opportunities yet. Connect your Razorpay webhook to stream failed payment events in real-time.
            </div>
          )}
        </div>
      </div>

      {/* Notice */}
      <div className="card" style={{ padding: 16, background: "rgba(59,130,246,0.05)", border: "1px solid rgba(59,130,246,0.15)" }}>
        <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
          <strong style={{ color: "var(--electric-blue)" }}>Model-Estimated Notice:</strong>{" "}
          All recovery probabilities (P_natural, P_intervention, incremental_prob) and IVEN values are{" "}
          <strong>model-estimated counterfactuals</strong>, not measured facts. Only{" "}
          <strong>reconciled, provider-confirmed</strong> payments count toward the "Total Recovered" KPI.
          Razorpay Test Mode is active — no real money is processed.
        </p>
      </div>
    </div>
  );
}
