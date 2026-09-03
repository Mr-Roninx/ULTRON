"use client";

import React, { useState } from "react";
import {
  TrendingUp, BarChart2, ShieldCheck, Zap, Activity, Clock,
  Download, Sparkles, CheckCircle2, Landmark
} from "lucide-react";
import { api, useAuth } from "../../../lib/auth";

interface BankMetrics {
  bank_name: string;
  bank_code: string;
  failures_count: number;
  recovered_count: number;
  recovery_rate_pct: number;
  top_failure_reason: string;
  volume_paise: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  color: string;
}

interface AnalyticsResponse {
  success: boolean;
  bank_data: BankMetrics[];
  metrics: {
    gross_causal_lift_pct: number;
    intervention_rate_pct: number;
    holdout_rate_pct: number;
    recovery_velocity_display: string;
    capital_efficiency_ratio: number;
    compliance_veto_rate_pct: number;
    total_opportunities_evaluated: number;
  };
  bandit?: {
    arms: Array<{
      context_key: string;
      expected_p_interv: number;
      expected_p_nat: number;
      expected_incremental_lift: number;
      pull_count: number;
      confidence: "low" | "medium" | "high";
    }>;
    pacer?: {
      active_arm: string;
      time_window: string;
      lambda: number;
      daily_budget_paise: number;
      spent_today_paise: number;
    };
  };
}

export default function EnterpriseAnalyticsStudioPage() {
  const { tenant } = useAuth();
  const [timeRange, setTimeRange] = useState<"24h" | "7d" | "30d" | "qtd">("7d");
  const [downloadingCert, setDownloadingCert] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = React.useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<AnalyticsResponse>("/dashboard/analytics");
      setAnalytics(data);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const bankData = analytics?.bank_data || [];

  const handleDownloadSignedCert = async () => {
    setDownloadingCert(true);
    try {
      const res = await api<any>("/v1/audit/export/json");
      const blob = new Blob([JSON.stringify(res, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ULTRON_Financial_Audit_Certificate_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (e: any) {
      alert("Failed to export certificate: " + e.message);
    } finally {
      setDownloadingCert(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1440, margin: "0 auto", width: "100%" }}>
      {/* Header */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: 20, flexWrap: "wrap", gap: 16
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px", margin: 0 }}>
              Bank Intelligence & Causal Recovery Lift
            </h1>
            <span className="badge badge-blue" style={{ fontWeight: 600 }}>
              CAUSAL INFERENCE ACTIVE
            </span>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: "4px 0 0" }}>
            Real-time causal recovery lift, issuer bank failure heatmaps, and empirical counterfactual holdout curves.
          </p>
        </div>

        {/* Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* Time Switcher */}
          <div style={{ display: "flex", background: "var(--bg-hover)", padding: 4, borderRadius: 20 }}>
            {(["24h", "7d", "30d", "qtd"] as const).map((r) => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                style={{
                  padding: "5px 12px", borderRadius: 16, fontSize: 12, fontWeight: 500, border: "none", cursor: "pointer",
                  background: timeRange === r ? "#ffffff" : "transparent",
                  color: timeRange === r ? "var(--google-blue)" : "var(--text-secondary)",
                  boxShadow: timeRange === r ? "0 1px 2px rgba(60,64,67,0.15)" : "none",
                  transition: "all 0.15s"
                }}
              >
                {r.toUpperCase()}
              </button>
            ))}
          </div>

          <button
            onClick={handleDownloadSignedCert}
            disabled={downloadingCert}
            className="btn btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
          >
            <Download size={14} />
            <span>{downloadingCert ? "Exporting..." : "Export Audit JSON"}</span>
          </button>
        </div>
      </div>

      {/* Top 4 Executive KPI Strip */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: 16, marginBottom: 20
      }}>
        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-green)" }}>
              Gross Causal Lift
            </span>
            <TrendingUp size={16} color="var(--google-green)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--google-green)", letterSpacing: "-0.5px" }}>
            +{analytics?.metrics ? analytics.metrics.gross_causal_lift_pct : 0}%
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Intervention ({analytics?.metrics?.intervention_rate_pct ?? 0}%) vs Natural Holdout ({analytics?.metrics?.holdout_rate_pct ?? 0}%)
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-blue)" }}>
              Recovery Velocity
            </span>
            <Clock size={16} color="var(--google-blue)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {analytics?.metrics?.recovery_velocity_display || "3.8 mins"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Median checkout failure to UPI payment settlement
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--google-purple)" }}>
              Capital Efficiency (ROI)
            </span>
            <Zap size={16} color="var(--google-purple)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {analytics?.metrics ? analytics.metrics.capital_efficiency_ratio : 1}x
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            ₹{analytics?.metrics ? analytics.metrics.capital_efficiency_ratio : 1} revenue returned per ₹1.00 operational cost
          </div>
        </div>

        <div className="card" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>
              Compliance Veto Rate
            </span>
            <ShieldCheck size={16} color="var(--google-green)" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
            {analytics?.metrics ? analytics.metrics.compliance_veto_rate_pct : 100}%
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
            Zero hard decline violations or retry cap breaches
          </div>
        </div>
      </div>

      {/* Issuer Bank Performance Heatmap */}
      <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 20 }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Landmark size={18} color="var(--google-blue)" />
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
                Issuer Bank Failure & Recovery Heatmap (India)
              </h2>
              <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "2px 0 0" }}>
                Autonomous routing effectiveness across major netbanking and UPI issuer gateways.
              </p>
            </div>
          </div>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Source: Razorpay Gateway Telemetry</span>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#f8f9fa", borderBottom: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 11, textTransform: "uppercase" }}>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Issuer Bank</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Failure Volume (₹)</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Top Failure Reason</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Recovery Success Rate</th>
                <th style={{ padding: "10px 16px", fontWeight: 600 }}>Recovered Count</th>
                <th style={{ padding: "10px 16px", fontWeight: 600, textAlign: "right" }}>Model Confidence</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} style={{ padding: "40px 16px", textAlign: "center", color: "var(--text-muted)" }}>
                    Loading live bank intelligence from database...
                  </td>
                </tr>
              ) : bankData.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: "40px 16px", textAlign: "center", color: "var(--text-muted)" }}>
                    No bank failure events recorded yet. Failures captured via the Client SDK or Webhook Gateway will populate here automatically.
                  </td>
                </tr>
              ) : (
                bankData.map((b) => (
                  <tr key={b.bank_code} style={{ borderBottom: "1px solid var(--border-subtle)", background: "#ffffff" }}>
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{
                          width: 28, height: 28, borderRadius: 6,
                          background: b.color + "15", color: b.color,
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontWeight: 700, fontSize: 10
                        }}>
                          {b.bank_code}
                        </div>
                        <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{b.bank_name}</div>
                      </div>
                    </td>

                    <td style={{ padding: "12px 16px", fontWeight: 700, color: "var(--text-primary)" }}>
                      ₹{(b.volume_paise / 100).toLocaleString("en-IN")}
                    </td>

                    <td style={{ padding: "12px 16px" }}>
                      <span style={{ padding: "4px 8px", borderRadius: 6, fontSize: 11, background: "var(--bg-hover)", border: "1px solid var(--border-subtle)" }}>
                        {b.top_failure_reason}
                      </span>
                    </td>

                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ width: 100, height: 6, borderRadius: 3, background: "#e8eaed", overflow: "hidden" }}>
                          <div style={{ width: `${Math.min(100, b.recovery_rate_pct)}%`, height: "100%", background: b.recovery_rate_pct >= 50 ? "var(--google-green)" : "var(--google-blue)" }} />
                        </div>
                        <span style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: 12 }}>{b.recovery_rate_pct}%</span>
                      </div>
                    </td>

                    <td style={{ padding: "12px 16px", color: "var(--google-green)", fontWeight: 600 }}>
                      {b.recovered_count.toLocaleString("en-IN")} / {b.failures_count.toLocaleString("en-IN")}
                    </td>

                    <td style={{ padding: "12px 16px", textAlign: "right" }}>
                      <span className="badge badge-green">
                        {b.confidence}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Causal Lift & Customer Fatigue Matrix */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {/* Causal Lift Visualizer */}
        <div className="card" style={{ padding: "20px 24px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <TrendingUp size={16} color="var(--google-green)" />
            <h3 style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>Causal Lift vs Natural Holdout</h3>
          </div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 16px 0" }}>
            Model-estimated counterfactual lift strictly verified against natural recovery holdout groups.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                <span style={{ color: "var(--google-green)", fontWeight: 600 }}>Intervention Group (ULTRON Active)</span>
                <span style={{ fontWeight: 700 }}>{analytics?.metrics?.intervention_rate_pct ?? 0}%</span>
              </div>
              <div style={{ width: "100%", height: 8, borderRadius: 4, background: "#e8eaed", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, analytics?.metrics?.intervention_rate_pct ?? 0)}%`, height: "100%", background: "var(--google-green)" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                <span style={{ color: "var(--text-secondary)" }}>Natural Holdout Baseline (Do-Nothing Control)</span>
                <span style={{ fontWeight: 700 }}>{analytics?.metrics?.holdout_rate_pct ?? 15}%</span>
              </div>
              <div style={{ width: "100%", height: 8, borderRadius: 4, background: "#e8eaed", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, analytics?.metrics?.holdout_rate_pct ?? 15)}%`, height: "100%", background: "#bdc1c6" }} />
              </div>
            </div>

            <div style={{ padding: "10px 14px", borderRadius: 6, background: "var(--google-green-light)", border: "1px solid #ceead6", marginTop: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--google-green-hover)" }}>
                Net Incremental Causal Lift: +{analytics?.metrics?.gross_causal_lift_pct ?? 0}%
              </div>
              <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                Evaluated across {analytics?.metrics?.total_opportunities_evaluated ?? 0} total recovery opportunities
              </div>
            </div>
          </div>
        </div>

        {/* Customer Fatigue Curve */}
        <div className="card" style={{ padding: "20px 24px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <Activity size={16} color="var(--google-yellow-dark)" />
            <h3 style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>Customer Fatigue Saturation Curve</h3>
          </div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 16px 0" }}>
            Marginal return decay per recovery attempt under Action Authority max-attempt guardrails.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", borderRadius: 6, background: "var(--bg-hover)" }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>Attempt 1 (Immediate Intercept)</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Fatigue Cost: ₹0.00 • High Receptivity</div>
              </div>
              <span style={{ fontSize: 13, fontWeight: 700, color: "var(--google-green)" }}>Baseline IVEN</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", borderRadius: 6, background: "var(--bg-hover)" }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>Attempt 2 (Follow-up +2 hrs)</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Fatigue Cost: ₹2.50 • Moderate Decay</div>
              </div>
              <span style={{ fontSize: 13, fontWeight: 700, color: "var(--google-blue)" }}>-₹2.50 Penalty</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", borderRadius: 6, background: "var(--google-red-light)", border: "1px solid #fad2cf" }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--google-red)" }}>Attempt 3+ (Deterministic Cutoff)</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Action Authority Veto Gate 2 Enforced</div>
              </div>
              <span className="badge badge-red">BLOCKED</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
